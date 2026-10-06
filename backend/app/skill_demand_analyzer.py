import json
import os
from collections import Counter
from app.skill_normalizer import normalize_skill_list

_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "job_market.json")


def _load_jobs():
    with open(_DATA_PATH, "r") as f:
        return json.load(f)


def get_skill_demand_for_role(role):
    jobs = [j for j in _load_jobs() if j["role"] == role]
    if not jobs:
        return {"role": role, "total_jobs": 0, "top_skills": []}

    total = len(jobs)
    skill_counter = Counter()

    for job in jobs:
        all_skills = normalize_skill_list(job["required_skills"] + job.get("preferred_skills", []))
        skill_counter.update(all_skills)

    top_skills = []
    for skill, freq in skill_counter.most_common(15):
        top_skills.append({
            "skill": skill,
            "frequency": freq,
            "demand_percentage": round(freq / total * 100),
        })

    return {"role": role, "total_jobs": total, "top_skills": top_skills}


def get_skill_demand_across_all_roles():
    jobs = _load_jobs()
    skill_counter = Counter()

    for job in jobs:
        all_skills = normalize_skill_list(job["required_skills"] + job.get("preferred_skills", []))
        skill_counter.update(all_skills)

    total_roles = len(jobs)
    top_skills = []
    for skill, freq in skill_counter.most_common(20):
        top_skills.append({
            "skill": skill,
            "frequency": freq,
            "demand_percentage": round(freq / total_roles * 100),
        })

    return {"total_jobs": total_roles, "top_skills": top_skills}
