import json
import os
from app.company_matcher import match_company, analyze_company_role


def load_companies():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "companies.json")
    with open(data_path, "r") as f:
        return json.load(f)["companies"]


def get_company_by_name(name):
    for c in load_companies():
        if c["name"] == name:
            return c
    return None


def get_all_companies():
    companies = load_companies()
    return [
        {
            "name": c["name"],
            "industry": c.get("industry", ""),
            "description": c.get("description", ""),
            "roles": [
                {
                    "title": r["title"],
                    "description": r.get("description", ""),
                    "experience_level": r.get("experience_level", ""),
                }
                for r in c["roles"]
            ],
        }
        for c in companies
    ]


def recommend_companies(user_skills):
    companies = load_companies()
    results = []

    for company in companies:
        role, score, matched, partial, missing = match_company(user_skills, company)
        if role is None:
            continue

        results.append({
            "company": company["name"],
            "industry": company.get("industry", ""),
            "description": company.get("description", ""),
            "role": role["title"],
            "experience_level": role.get("experience_level", ""),
            "match_percentage": score,
            "matched_count": len(matched) + len(partial),
            "missing_count": len(missing),
            "matched_skills": matched,
            "partial_matches": partial,
            "missing_skills": [m["skill"] for m in missing],
        })

    results.sort(key=lambda x: x["match_percentage"], reverse=True)
    return results


def analyze_company(user_skills, company_name, role_title=None):
    company = get_company_by_name(company_name)
    if not company:
        return None

    if role_title:
        for role in company["roles"]:
            if role["title"] == role_title:
                return analyze_company_role(user_skills, company, role)
        return None

    role, score, matched, partial, missing = match_company(user_skills, company)
    if role is None:
        return None

    return analyze_company_role(user_skills, company, role)
