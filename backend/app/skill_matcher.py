import json
import os
import re
from app.skill_normalizer import normalize_skill, normalize_skill_list
from app.skill_taxonomy_service import (
    load_taxonomy, resolve_skill, get_skill_info, get_category,
    get_importance, get_all_skills_in_category, get_all_categories,
)
from sentence_transformers import SentenceTransformer, util
import numpy as np

_model = None
_emb_cache = {}

SIMILARITY_THRESHOLD = 0.65
EXACT_MATCH_SCORE = 1.0
ALIAS_MATCH_SCORE = 0.98


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _get_embedding(text):
    if text not in _emb_cache:
        model = get_model()
        _emb_cache[text] = model.encode(text, convert_to_tensor=True)
    return _emb_cache[text]


def load_careers():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "careers.json")
    with open(data_path, "r") as f:
        return json.load(f)["careers"]


def load_companies():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "companies.json")
    with open(data_path, "r") as f:
        return json.load(f)["companies"]


def extract_skills_from_text(text):
    text_lower = text.lower()
    found = []

    for category, cat_data in load_taxonomy().items():
        for skill_name, skill_data in cat_data["skills"].items():
            patterns = [skill_name.lower()] + [a.lower() for a in skill_data.get("aliases", [])]
            for pattern in patterns:
                escaped = pattern.replace(".", r"\.?").replace("+", r"\+")
                if re.search(r"(?:^|[\s,;|/\-•·\*])(?:" + escaped + r")(?:$|[\s,;|/\-•·\*])", text_lower):
                    normalized = resolve_skill(skill_name)[0]
                    if normalized.lower() not in [s.lower() for s in found]:
                        found.append(normalized)
                    break

    return list(set(found))


def match_single_skill(user_skill, role_skill):
    user_resolved, user_is_exact = resolve_skill(user_skill)
    role_resolved, role_is_exact = resolve_skill(role_skill)

    user_lower = user_resolved.lower()
    role_lower = role_resolved.lower()

    if user_lower == role_lower:
        return EXACT_MATCH_SCORE, "exact"

    role_info = get_skill_info(role_resolved)
    if role_info:
        for alias in role_info.get("aliases", []):
            if user_lower == alias.lower():
                return ALIAS_MATCH_SCORE, "alias"

    user_info = get_skill_info(user_resolved)
    if user_info:
        for alias in user_info.get("aliases", []):
            if alias.lower() == role_lower:
                return ALIAS_MATCH_SCORE, "alias"

    user_emb = _get_embedding(user_resolved)
    role_emb = _get_embedding(role_resolved)
    sim = float(util.cos_sim(user_emb, role_emb)[0])

    if sim >= SIMILARITY_THRESHOLD:
        return round(sim, 4), "semantic"

    return 0.0, "none"


def match_role(user_skills, role):
    importance_map = role.get("skill_importance", role.get("skill_weights", {}))
    importance_weights = {"critical": 1.0, "high": 0.8, "medium": 0.6, "low": 0.4}

    matched = []
    missing = []
    partial = []

    all_skills = role.get("required_skills", []) + role.get("preferred_skills", [])
    is_required = {s: True for s in role.get("required_skills", [])}

    for skill in all_skills:
        best_score = 0.0
        best_match = None
        best_type = "none"

        for user_skill in user_skills:
            score, match_type = match_single_skill(user_skill, skill)
            if score > best_score:
                best_score = score
                best_match = user_skill
                best_type = match_type

        imp_str = importance_map.get(skill, "medium" if is_required.get(skill, True) else "low")
        weight = importance_weights.get(imp_str, 0.6)
        weighted_score = best_score * weight if best_score > 0 else 0

        entry = {
            "skill": skill,
            "user_skill": best_match,
            "score": round(best_score, 4),
            "match_type": best_type,
            "importance": imp_str,
            "weight": weight,
            "weighted_score": round(weighted_score, 4),
            "required": is_required.get(skill, True),
        }

        if best_score >= 0.95:
            matched.append(entry)
        elif best_score >= SIMILARITY_THRESHOLD:
            partial.append(entry)
        else:
            missing.append(entry)

    return matched, partial, missing


def match_role_batch(user_skills, role):
    required = role.get("required_skills", [])
    preferred = role.get("preferred_skills", [])
    importance_map = role.get("skill_importance", role.get("skill_weights", {}))

    importance_weights = {"critical": 1.0, "high": 0.8, "medium": 0.6, "low": 0.4}

    resolved_user = []
    for s in user_skills:
        r, _ = resolve_skill(s)
        resolved_user.append((s, r.lower()))

    resolved_required = []
    for s in required:
        r, _ = resolve_skill(s)
        resolved_required.append((s, r.lower()))

    resolved_preferred = []
    for s in preferred:
        r, _ = resolve_skill(s)
        resolved_preferred.append((s, r.lower()))

    alias_map = {}
    for skill_name in set([s for _, s in resolved_user] + [s for _, s in resolved_required] + [s for _, s in resolved_preferred]):
        info = get_skill_info(skill_name)
        if info:
            for alias in info.get("aliases", []):
                alias_map[(skill_name, alias.lower())] = True

    exact_matches = set()
    alias_matches = {}
    for u_orig, u_lower in resolved_user:
        for r_orig, r_lower in resolved_required + resolved_preferred:
            if u_lower == r_lower:
                exact_matches.add((u_orig, r_orig))
            elif (r_lower, u_lower) in alias_map or (u_lower, r_lower) in alias_map:
                alias_matches[(u_orig, r_orig)] = ALIAS_MATCH_SCORE

    needs_semantic = []
    for r_orig, r_lower in resolved_required + resolved_preferred:
        found = False
        for u_orig, u_lower in resolved_user:
            if (u_orig, r_orig) in exact_matches or (u_orig, r_orig) in alias_matches:
                found = True
                break
        if not found:
            needs_semantic.append((r_orig, r_lower))

    semantic_scores = {}
    if needs_semantic:
        user_lower_list = [u for _, u in resolved_user]
        role_lower_list = [r for _, r in needs_semantic]

        if user_lower_list and role_lower_list:
            user_embs = [_get_embedding(u) for u in user_lower_list]
            role_embs = [_get_embedding(r) for r in role_lower_list]
            import torch
            user_embs = torch.stack(user_embs)
            role_embs = torch.stack(role_embs)
            sim_matrix = util.cos_sim(role_embs, user_embs)

            for i, (r_orig, _) in enumerate(needs_semantic):
                best_sim = 0.0
                best_user = None
                for j, (u_orig, _) in enumerate(resolved_user):
                    sim_val = float(sim_matrix[i][j])
                    if sim_val > best_sim:
                        best_sim = sim_val
                        best_user = u_orig
                if best_sim >= SIMILARITY_THRESHOLD:
                    semantic_scores[(best_user, r_orig)] = round(best_sim, 4)

    matched = []
    missing = []
    partial = []

    for req_skill in required:
        best_score = 0.0
        best_match = None
        best_type = "none"

        for u_orig, u_lower in resolved_user:
            if (u_orig, req_skill) in exact_matches:
                if EXACT_MATCH_SCORE > best_score:
                    best_score = EXACT_MATCH_SCORE
                    best_match = u_orig
                    best_type = "exact"
            elif (u_orig, req_skill) in alias_matches:
                if ALIAS_MATCH_SCORE > best_score:
                    best_score = ALIAS_MATCH_SCORE
                    best_match = u_orig
                    best_type = "alias"
            elif (u_orig, req_skill) in semantic_scores:
                score = semantic_scores[(u_orig, req_skill)]
                if score > best_score:
                    best_score = score
                    best_match = u_orig
                    best_type = "semantic"

        imp_str = importance_map.get(req_skill, "medium")
        weight = importance_weights.get(imp_str, 0.6)
        weighted_score = best_score * weight if best_score > 0 else 0

        entry = {
            "skill": req_skill,
            "user_skill": best_match,
            "score": round(best_score, 4),
            "match_type": best_type,
            "importance": imp_str,
            "weight": weight,
            "weighted_score": round(weighted_score, 4),
            "required": True,
        }

        if best_score >= 0.95:
            matched.append(entry)
        elif best_score >= SIMILARITY_THRESHOLD:
            partial.append(entry)
        else:
            missing.append(entry)

    for pref_skill in preferred:
        best_score = 0.0
        best_match = None
        best_type = "none"

        for u_orig, u_lower in resolved_user:
            if (u_orig, pref_skill) in exact_matches:
                if EXACT_MATCH_SCORE > best_score:
                    best_score = EXACT_MATCH_SCORE
                    best_match = u_orig
                    best_type = "exact"
            elif (u_orig, pref_skill) in alias_matches:
                if ALIAS_MATCH_SCORE > best_score:
                    best_score = ALIAS_MATCH_SCORE
                    best_match = u_orig
                    best_type = "alias"
            elif (u_orig, pref_skill) in semantic_scores:
                score = semantic_scores[(u_orig, pref_skill)]
                if score > best_score:
                    best_score = score
                    best_match = u_orig
                    best_type = "semantic"

        imp_str = importance_map.get(pref_skill, "low")
        weight = importance_weights.get(imp_str, 0.4)
        weighted_score = best_score * weight if best_score > 0 else 0

        entry = {
            "skill": pref_skill,
            "user_skill": best_match,
            "score": round(best_score, 4),
            "match_type": best_type,
            "importance": imp_str,
            "weight": weight,
            "weighted_score": round(weighted_score, 4),
            "required": False,
        }

        if best_score >= 0.95:
            matched.append(entry)
        elif best_score >= SIMILARITY_THRESHOLD:
            partial.append(entry)
        else:
            missing.append(entry)

    return matched, partial, missing
    required = role.get("required_skills", [])
    preferred = role.get("preferred_skills", [])
    importance_map = role.get("skill_importance", {})

    importance_weights = {"critical": 1.0, "high": 0.8, "medium": 0.6, "low": 0.4}

    matched = []
    missing = []
    partial = []

    for req_skill in required:
        best_score = 0.0
        best_match = None
        best_type = "none"

        for user_skill in user_skills:
            score, match_type = match_single_skill(user_skill, req_skill)
            if score > best_score:
                best_score = score
                best_match = user_skill
                best_type = match_type

        imp_str = importance_map.get(req_skill, "medium")
        weight = importance_weights.get(imp_str, 0.6)
        weighted_score = best_score * weight if best_score > 0 else 0

        entry = {
            "skill": req_skill,
            "user_skill": best_match,
            "score": round(best_score, 4),
            "match_type": best_type,
            "importance": imp_str,
            "weight": weight,
            "weighted_score": round(weighted_score, 4),
            "required": True,
        }

        if best_score >= 0.95:
            matched.append(entry)
        elif best_score >= SIMILARITY_THRESHOLD:
            partial.append(entry)
        else:
            missing.append(entry)

    for pref_skill in preferred:
        best_score = 0.0
        best_match = None
        best_type = "none"

        for user_skill in user_skills:
            score, match_type = match_single_skill(user_skill, pref_skill)
            if score > best_score:
                best_score = score
                best_match = user_skill
                best_type = match_type

        imp_str = importance_map.get(pref_skill, "low")
        weight = importance_weights.get(imp_str, 0.4)
        weighted_score = best_score * weight if best_score > 0 else 0

        entry = {
            "skill": pref_skill,
            "user_skill": best_match,
            "score": round(best_score, 4),
            "match_type": best_type,
            "importance": imp_str,
            "weight": weight,
            "weighted_score": round(weighted_score, 4),
            "required": False,
        }

        if best_score >= 0.95:
            matched.append(entry)
        elif best_score >= SIMILARITY_THRESHOLD:
            partial.append(entry)
        else:
            missing.append(entry)

    return matched, partial, missing


def calculate_category_scores(matched, partial, missing):
    category_data = {}

    for entry in matched + partial + missing:
        cat = get_category(entry["skill"]) or "Other"
        if cat not in category_data:
            category_data[cat] = {"total_weight": 0, "earned_weight": 0}
        category_data[cat]["total_weight"] += entry["weight"]

        if entry["score"] >= 0.95:
            category_data[cat]["earned_weight"] += entry["weight"]
        elif entry["score"] >= SIMILARITY_THRESHOLD:
            category_data[cat]["earned_weight"] += entry["weight"] * entry["score"]

    scores = {}
    for cat, data in category_data.items():
        if data["total_weight"] > 0:
            scores[cat] = round((data["earned_weight"] / data["total_weight"]) * 100, 1)
        else:
            scores[cat] = 0.0

    return scores


def calculate_overall_match(matched, partial, missing):
    total_weight = 0
    earned_weight = 0

    for entry in matched:
        total_weight += entry["weight"]
        earned_weight += entry["weight"]

    for entry in partial:
        total_weight += entry["weight"]
        earned_weight += entry["weight"] * entry["score"]

    for entry in missing:
        total_weight += entry["weight"]

    if total_weight == 0:
        return 0.0

    return round((earned_weight / total_weight) * 100, 1)


def get_priority_gaps(missing, top_n=10):
    importance_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_missing = sorted(missing, key=lambda x: (importance_order.get(x["importance"], 4), -x["weight"]))
    return sorted_missing[:top_n]


def analyze_gap_new(user_skills, target_role):
    careers = load_careers()
    career = None
    for c in careers:
        if c["name"] == target_role:
            career = c
            break

    if not career:
        return None

    matched, partial, missing = match_role(user_skills, career)

    overall = calculate_overall_match(matched, partial, missing)
    category_scores = calculate_category_scores(matched, partial, missing)
    priority_gaps = get_priority_gaps(missing)

    importance_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    roadmap = []
    for gap in priority_gaps:
        skill_name = gap["skill"]
        learning_order = career.get("learning_order", [])
        step = learning_order.index(skill_name) + 1 if skill_name in learning_order else 99
        roadmap.append({
            "skill": skill_name,
            "importance": gap["importance"],
            "order": step,
            "estimated_time": _estimate_time(gap["importance"]),
        })
    roadmap.sort(key=lambda x: x["order"])

    return {
        "target_role": target_role,
        "overall_match": overall,
        "category_scores": category_scores,
        "matched_skills": matched,
        "partial_matches": partial,
        "missing_skills": [m["skill"] for m in missing],
        "priority_gaps": [
            {"skill": g["skill"], "importance": g["importance"], "weight": g["weight"]}
            for g in priority_gaps
        ],
        "roadmap": [
            {"skill": r["skill"], "importance": r["importance"], "estimated_time": r["estimated_time"]}
            for r in roadmap
        ],
    }


def _estimate_time(importance):
    times = {"critical": "2-4 weeks", "high": "1-2 weeks", "medium": "3-5 days", "low": "1-2 days"}
    return times.get(importance, "1 week")


def recommend_companies(user_skills):
    companies = load_companies()
    results = []

    for company in companies:
        best_role = None
        best_score = -1
        best_matched = []
        best_partial = []
        best_missing = []

        for role in company["roles"]:
            matched, partial, missing = match_role(user_skills, role)
            overall = calculate_overall_match(matched, partial, missing)
            if overall > best_score:
                best_score = overall
                best_role = role["title"]
                best_matched = matched
                best_partial = partial
                best_missing = missing

        results.append({
            "company": company["name"],
            "industry": company.get("industry", ""),
            "role": best_role,
            "match_percentage": best_score,
            "matched_skills": best_matched,
            "partial_matches": best_partial,
            "missing_skills": [m["skill"] for m in best_missing],
        })

    results.sort(key=lambda x: x["match_percentage"], reverse=True)
    return results


def analyze_company_gap(user_skills, company_name, role_title):
    companies = load_companies()
    company = None
    for c in companies:
        if c["name"] == company_name:
            company = c
            break
    if not company:
        return None

    role = None
    for r in company["roles"]:
        if r["title"] == role_title:
            role = r
            break
    if not role:
        return None

    matched, partial, missing = match_role(user_skills, role)
    overall = calculate_overall_match(matched, partial, missing)
    priority_gaps = get_priority_gaps(missing)

    importance_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    roadmap = []
    for gap in priority_gaps:
        roadmap.append({
            "skill": gap["skill"],
            "importance": gap["importance"],
            "estimated_time": _estimate_time(gap["importance"]),
        })

    return {
        "company": company_name,
        "role": role_title,
        "match_percentage": overall,
        "required_skills": role.get("required_skills", []),
        "preferred_skills": role.get("preferred_skills", []),
        "matched_skills": matched,
        "partial_matches": partial,
        "missing_skills": [m["skill"] for m in missing],
        "priority_skills": [g["skill"] for g in priority_gaps[:5]],
        "roadmap": roadmap,
    }
