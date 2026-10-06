import json
import os
from collections import Counter

_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "job_market.json")


def _load_jobs():
    with open(_DATA_PATH, "r") as f:
        return json.load(f)


def get_role_demand():
    jobs = _load_jobs()
    role_counter = Counter(j["role"] for j in jobs)
    total = len(jobs)

    roles = []
    for role, count in role_counter.most_common():
        roles.append({
            "role": role,
            "openings": count,
            "demand_score": round(count / total * 100),
        })

    return {"total_jobs": total, "roles": roles}


def get_roles_for_company(company):
    jobs = _load_jobs()
    company_jobs = [j for j in jobs if j["company"].lower() == company.lower()]

    if not company_jobs:
        return None

    role_counter = Counter(j["role"] for j in company_jobs)
    skill_counter = Counter()
    for job in company_jobs:
        for s in job["required_skills"]:
            skill_counter[s] += 1

    roles = []
    for role, count in role_counter.most_common():
        roles.append({"role": role, "openings": count})

    top_skills = []
    for skill, freq in skill_counter.most_common(10):
        top_skills.append({"skill": skill, "frequency": freq})

    return {
        "company": company,
        "total_openings": len(company_jobs),
        "roles": roles,
        "required_skills": top_skills,
    }


def get_companies():
    jobs = _load_jobs()
    companies = sorted(set(j["company"] for j in jobs))
    return companies
