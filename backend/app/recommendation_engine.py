from app.skill_matcher import load_careers, match_role_batch, calculate_overall_match, calculate_category_scores, get_priority_gaps
from app.skill_taxonomy_service import get_category
from app.recommendation_config import get_weights, CATEGORY_THRESHOLDS, PROJECT_KEYWORDS, EDUCATION_KEYWORDS, EXPERIENCE_KEYWORDS


def calculate_skill_match(user_skills, career):
    matched, partial, missing = match_role_batch(user_skills, career)
    overall = calculate_overall_match(matched, partial, missing)
    return overall, matched, partial, missing


def calculate_project_relevance(user_projects, career):
    if not user_projects:
        return 30.0

    career_skills_lower = [s.lower() for s in career.get("required_skills", [])]
    career_categories = set()
    for skill in career.get("required_skills", []):
        cat = get_category(skill)
        if cat:
            career_categories.add(cat.lower())

    relevant_categories = set()
    for project in user_projects:
        text = (project.get("name", "") + " " + project.get("description", "") + " " + " ".join(project.get("technologies", []))).lower()

        for cat_key, keywords in PROJECT_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    relevant_categories.add(cat_key)

        for tech in project.get("technologies", []):
            if tech.lower() in career_skills_lower:
                relevant_categories.add("direct_match")

    if not relevant_categories:
        return 20.0

    score = 0.0
    if "direct_match" in relevant_categories:
        score += 50.0

    category_overlap = 0
    for cat in relevant_categories:
        if cat in career_categories:
            category_overlap += 1

    if relevant_categories:
        score += (category_overlap / len(relevant_categories)) * 40.0

    score += min(len(relevant_categories) * 5.0, 20.0)

    return min(round(score, 1), 100.0)


def calculate_experience_relevance(user_experience, user_internships, career):
    all_experience = (user_experience or []) + (user_internships or [])
    if not all_experience:
        return 25.0

    career_required = [s.lower() for s in career.get("required_skills", [])]

    score = 0.0
    total_entries = len(all_experience)

    for exp in all_experience:
        text = (exp.get("title", "") + " " + exp.get("company", "") + " " + exp.get("description", "")).lower()

        for skill in career_required:
            if skill in text:
                score += 15.0

        for exp_type, keywords in EXPERIENCE_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    score += 5.0
                    break

    years_score = min(total_entries * 10.0, 30.0)
    score += years_score

    return min(round(score, 1), 100.0)


def calculate_education_relevance(user_education, career):
    if not user_education:
        return 30.0

    career_name = career.get("name", "").lower()

    score = 0.0
    for edu in user_education:
        degree = edu.get("degree", "").lower()

        for field, keywords in EDUCATION_KEYWORDS.items():
            for kw in keywords:
                if kw in degree:
                    if field == "cs" and any(x in career_name for x in ["developer", "engineer", "backend", "full stack"]):
                        score += 40.0
                    elif field == "data" and any(x in career_name for x in ["data", "analyst", "scientist"]):
                        score += 40.0
                    elif field == "ai" and any(x in career_name for x in ["ai", "ml", "machine learning", "deep learning"]):
                        score += 45.0
                    elif field == "business" and any(x in career_name for x in ["product", "manager", "consultant"]):
                        score += 35.0
                    else:
                        score += 25.0
                    break

        if "bachelor" in degree or "b.s" in degree or "b.tech" in degree or "b.e" in degree:
            score += 15.0
        if "master" in degree or "m.s" in degree or "m.tech" in degree or "mca" in degree:
            score += 20.0
        if "phd" in degree or "ph.d" in degree:
            score += 10.0

    return min(round(score, 1), 100.0)


def calculate_career_preference(career_name, target_career):
    if not target_career:
        return 50.0

    if career_name.lower() == target_career.lower():
        return 100.0

    career_words = set(career_name.lower().split())
    target_words = set(target_career.lower().split())
    overlap = career_words & target_words

    if overlap:
        return round(50.0 + (len(overlap) / max(len(career_words), len(target_words))) * 50.0, 1)

    return 30.0


def generate_reason(skill_match, project_relevance, experience_relevance, education_relevance, matched_skills, career_name):
    reasons = []

    if skill_match >= 75:
        reasons.append(f"Strong skill alignment ({round(skill_match)}%)")
    elif skill_match >= 50:
        reasons.append(f"Good skill foundation ({round(skill_match)}%)")
    else:
        reasons.append(f"Building skill base ({round(skill_match)}%)")

    if matched_skills:
        top_skills = [s["skill"] for s in matched_skills[:3]]
        reasons.append(f"Your strengths: {', '.join(top_skills)}")

    if project_relevance >= 60:
        reasons.append("Your projects show relevant experience")

    if experience_relevance >= 50:
        reasons.append("Your work experience aligns well")

    if education_relevance >= 50:
        reasons.append("Your educational background is relevant")

    return reasons


def recommend_careers(user_skills, user_profile=None, target_career=None, top_n=10):
    careers = load_careers()
    weights = get_weights()

    user_projects = []
    user_education = []
    user_experience = []
    user_internships = []

    if user_profile:
        user_projects = user_profile.get("projects", [])
        user_education = user_profile.get("education", [])
        user_experience = user_profile.get("experience", [])
        user_internships = user_profile.get("internships", [])

    results = []

    for career in careers:
        skill_match, matched, partial, missing = calculate_skill_match(user_skills, career)
        project_relevance = calculate_project_relevance(user_projects, career)
        experience_relevance = calculate_experience_relevance(user_experience, user_internships, career)
        education_relevance = calculate_education_relevance(user_education, career)
        career_pref = calculate_career_preference(career["name"], target_career)

        overall_score = round(
            skill_match * weights["skill_match"]
            + project_relevance * weights["project_relevance"]
            + experience_relevance * weights["experience_relevance"]
            + education_relevance * weights["education_relevance"]
            + career_pref * weights["career_preference"],
            1,
        )

        category_scores = calculate_category_scores(matched, partial, missing)
        priority_gaps = get_priority_gaps(missing)

        strongest = sorted(matched, key=lambda x: x.get("score", 0), reverse=True)[:5]
        reasons = generate_reason(skill_match, project_relevance, experience_relevance, education_relevance, matched, career["name"])

        if overall_score >= CATEGORY_THRESHOLDS["best_fit"]:
            category = "Best Fit"
        elif overall_score >= CATEGORY_THRESHOLDS["close_match"]:
            category = "Close Match"
        else:
            category = "Long-Term Goal"

        results.append({
            "role": career["name"],
            "score": overall_score,
            "category": category,
            "skill_match": round(skill_match, 1),
            "project_match": round(project_relevance, 1),
            "experience_match": round(experience_relevance, 1),
            "education_match": round(education_relevance, 1),
            "career_preference": round(career_pref, 1),
            "strongest_skills": [{"skill": s["skill"], "score": s.get("score", 0), "match_type": s.get("match_type", "")} for s in strongest],
            "missing_skills": [m["skill"] for m in missing],
            "partial_matches": [{"skill": p["skill"], "score": p.get("score", 0)} for p in partial],
            "reason": reasons,
            "category_scores": category_scores,
            "total_required": len(career.get("required_skills", [])),
            "total_matched": len(matched) + len(partial),
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]
