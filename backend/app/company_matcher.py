from app.skill_matcher import (
    match_single_skill,
    calculate_overall_match,
    calculate_category_scores,
    get_priority_gaps,
)

IMPORTANCE_WEIGHTS = {"critical": 1.0, "high": 0.8, "medium": 0.6, "low": 0.4}


def match_company_role(user_skills, role):
    required = role.get("required_skills", [])
    preferred = role.get("preferred_skills", [])
    weights = role.get("skill_weights", {})

    matched = []
    partial = []
    missing = []

    for skill in required:
        best_score = 0.0
        best_match = None
        best_type = "none"

        for user_skill in user_skills:
            score, match_type = match_single_skill(user_skill, skill)
            if score > best_score:
                best_score = score
                best_match = user_skill
                best_type = match_type

        imp = weights.get(skill, "medium")
        weight = IMPORTANCE_WEIGHTS.get(imp, 0.6)
        weighted_score = best_score * weight if best_score > 0 else 0

        entry = {
            "skill": skill,
            "user_skill": best_match,
            "score": round(best_score, 4),
            "match_type": best_type,
            "importance": imp,
            "weight": weight,
            "weighted_score": round(weighted_score, 4),
        }

        if best_score >= 0.95:
            matched.append(entry)
        elif best_score >= 0.65:
            partial.append(entry)
        else:
            missing.append(entry)

    for skill in preferred:
        best_score = 0.0
        best_match = None
        best_type = "none"

        for user_skill in user_skills:
            score, match_type = match_single_skill(user_skill, skill)
            if score > best_score:
                best_score = score
                best_match = user_skill
                best_type = match_type

        imp = weights.get(skill, "low")
        weight = IMPORTANCE_WEIGHTS.get(imp, 0.4)
        weighted_score = best_score * weight if best_score > 0 else 0

        entry = {
            "skill": skill,
            "user_skill": best_match,
            "score": round(best_score, 4),
            "match_type": best_type,
            "importance": imp,
            "weight": weight,
            "weighted_score": round(weighted_score, 4),
        }

        if best_score >= 0.95:
            matched.append(entry)
        elif best_score >= 0.65:
            partial.append(entry)
        else:
            missing.append(entry)

    return matched, partial, missing


def calculate_role_score(matched, partial, missing):
    total_weight = 0
    earned_weight = 0

    for e in matched:
        total_weight += e["weight"]
        earned_weight += e["weight"]

    for e in partial:
        total_weight += e["weight"]
        earned_weight += e["weight"] * e["score"]

    for e in missing:
        total_weight += e["weight"]

    if total_weight == 0:
        return 0.0
    return round((earned_weight / total_weight) * 100, 1)


def match_company(user_skills, company):
    best_role = None
    best_score = -1
    best_matched = []
    best_partial = []
    best_missing = []

    for role in company["roles"]:
        matched, partial, missing = match_company_role(user_skills, role)
        score = calculate_role_score(matched, partial, missing)
        if score > best_score:
            best_score = score
            best_role = role
            best_matched = matched
            best_partial = partial
            best_missing = missing

    return best_role, best_score, best_matched, best_partial, best_missing


def analyze_company_role(user_skills, company, role):
    matched, partial, missing = match_company_role(user_skills, role)
    score = calculate_role_score(matched, partial, missing)
    cat_scores = calculate_category_scores(matched, partial, missing)
    priority = get_priority_gaps(missing)

    return {
        "company": company["name"],
        "industry": company.get("industry", ""),
        "role": role["title"],
        "experience_level": role.get("experience_level", ""),
        "description": role.get("description", ""),
        "match_percentage": score,
        "category_scores": cat_scores,
        "matched_skills": matched,
        "partial_matches": partial,
        "missing_skills": [m["skill"] for m in missing],
        "required_skills": role.get("required_skills", []),
        "preferred_skills": role.get("preferred_skills", []),
        "priority_gaps": [
            {"skill": g["skill"], "importance": g["importance"], "weight": g["weight"]}
            for g in priority
        ],
    }
