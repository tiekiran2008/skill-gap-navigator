from app.skill_normalizer import normalize_skill_list
from app.skill_demand_analyzer import get_skill_demand_for_role, get_skill_demand_across_all_roles
from app.role_demand_analyzer import get_role_demand, get_roles_for_company, get_companies


def analyze_user_vs_market(user_skills, target_role=None):
    normalized_user = set(normalize_skill_list(user_skills))

    if target_role:
        role_data = get_skill_demand_for_role(target_role)
    else:
        role_data = get_skill_demand_across_all_roles()

    top_skills = role_data["top_skills"]
    if not top_skills:
        return {
            "market_readiness": 0,
            "high_demand_skills_user_has": [],
            "high_demand_skills_missing": [],
            "recommended_next_skills": [],
        }

    high_demand = [s["skill"] for s in top_skills if s["demand_percentage"] >= 30]

    user_has = [s for s in high_demand if s in normalized_user]
    user_missing = [s for s in high_demand if s not in normalized_user]

    readiness = round(len(user_has) / len(high_demand) * 100) if high_demand else 0

    recommended = []
    for skill in user_missing:
        for s in top_skills:
            if s["skill"] == skill:
                recommended.append({"skill": skill, "demand_percentage": s["demand_percentage"]})
                break
    recommended.sort(key=lambda x: x["demand_percentage"], reverse=True)

    return {
        "market_readiness": readiness,
        "high_demand_skills_user_has": user_has,
        "high_demand_skills_missing": user_missing,
        "recommended_next_skills": recommended,
    }


def get_role_insight(role, user_skills=None):
    role_data = get_skill_demand_for_role(role)
    jobs = _load_jobs_filtered(role)

    preferred_counter = {}
    experience_counter = {}
    companies = set()

    for job in jobs:
        for s in job.get("preferred_skills", []):
            ns = s
            preferred_counter[ns] = preferred_counter.get(ns, 0) + 1
        exp = job.get("experience_level", "Mid")
        experience_counter[exp] = experience_counter.get(exp, 0) + 1
        companies.add(job["company"])

    top_preferred = sorted(preferred_counter.items(), key=lambda x: x[1], reverse=True)[:5]
    top_experience = sorted(experience_counter.items(), key=lambda x: x[1], reverse=True)

    result = {
        "role": role,
        "total_jobs": role_data["total_jobs"],
        "top_skills": role_data["top_skills"],
        "preferred_skills": [{"skill": s, "frequency": f} for s, f in top_preferred],
        "experience_levels": [{"level": l, "count": c} for l, c in top_experience],
        "companies": sorted(companies),
    }

    if user_skills:
        normalized = set(normalize_skill_list(user_skills))
        role_skills = set(s["skill"] for s in role_data["top_skills"])
        result["user_readiness"] = round(len(normalized & role_skills) / len(role_skills) * 100) if role_skills else 0
        result["user_has"] = sorted(normalized & role_skills)
        result["user_missing"] = sorted(role_skills - normalized)

    return result


def get_company_insight(company, user_skills=None):
    data = get_roles_for_company(company)
    if data is None:
        return None

    if user_skills:
        normalized = set(normalize_skill_list(user_skills))
        all_company_skills = set(s["skill"] for s in data["required_skills"])
        matched = sorted(normalized & all_company_skills)
        missing = sorted(all_company_skills - normalized)
        data["user_match_count"] = len(matched)
        data["user_missing_count"] = len(missing)
        data["matched_skills"] = matched
        data["missing_skills"] = missing

    return data


def _load_jobs_filtered(role):
    import json, os
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "job_market.json")
    with open(path, "r") as f:
        jobs = json.load(f)
    return [j for j in jobs if j["role"] == role]
