import json
import os
from app.skill_normalizer import normalize_skill_list

_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "projects.json")

WEIGHTS = {
    "missing_skill_match": 0.40,
    "target_role_match": 0.25,
    "market_demand_match": 0.20,
    "difficulty_fit": 0.15,
}

DIFFICULTY_LEVELS = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}


def _load_projects():
    with open(_DATA_PATH, "r") as f:
        return json.load(f)


def _estimate_level(user_skills):
    count = len(user_skills) if user_skills else 0
    if count >= 8:
        return 3
    if count >= 4:
        return 2
    return 1


def _difficulty_fit_score(project_difficulty, user_level):
    proj_level = DIFFICULTY_LEVELS.get(project_difficulty, 2)
    diff = abs(proj_level - user_level)
    if diff == 0:
        return 1.0
    if diff == 1:
        return 0.6
    return 0.2


def recommend_projects(skills=None, missing_skills=None, target_role=None,
                       market_skills=None, company=None, top_n=10):
    projects = _load_projects()
    user_skills = set(normalize_skill_list(skills or []))
    missing = set(normalize_skill_list(missing_skills or []))
    market = set(normalize_skill_list(market_skills or []))
    user_level = _estimate_level(skills)

    scored = []
    for proj in projects:
        proj_skills = set(normalize_skill_list(proj["skills"]))

        # Missing skill overlap
        if missing:
            missing_covered = proj_skills & missing
            missing_score = len(missing_covered) / len(missing) if missing else 0
        else:
            missing_covered = set()
            missing_score = 0

        # Target role match
        if target_role:
            role_match = 1.0 if target_role in proj["target_roles"] else 0.0
        else:
            role_match = 0.5

        # Market demand match
        if market:
            market_overlap = proj_skills & market
            market_score = len(market_overlap) / len(market) if market else 0
        else:
            market_score = 0.5

        # Difficulty fit
        diff_score = _difficulty_fit_score(proj["difficulty"], user_level)

        # Penalize projects that only use skills user already has
        new_skills = proj_skills - user_skills
        novelty_penalty = 1.0 if new_skills else 0.3

        total_score = (
            WEIGHTS["missing_skill_match"] * missing_score +
            WEIGHTS["target_role_match"] * role_match +
            WEIGHTS["market_demand_match"] * market_score +
            WEIGHTS["difficulty_fit"] * diff_score
        ) * novelty_penalty

        score = round(total_score * 100)

        skills_you_gain = sorted(new_skills)
        why = []
        if missing_covered:
            why.append(f"Covers {len(missing_covered)} missing skill(s): {', '.join(sorted(missing_covered))}")
        if role_match == 1.0:
            why.append(f"Directly targets {target_role}")
        elif role_match > 0:
            why.append(f"Related to {target_role}")
        if market_overlap if market else False:
            why.append(f"Uses {len(market_overlap)} market-demand skill(s)")
        if not why:
            why.append("Broadens your skill set")

        scored.append({
            "id": proj["id"],
            "title": proj["title"],
            "score": score,
            "skills_you_will_gain": skills_you_gain,
            "missing_skills_covered": sorted(missing_covered),
            "why_recommended": why,
            "difficulty": proj["difficulty"],
            "estimated_duration": proj["estimated_duration"],
            "tech_stack": proj["tech_stack"],
            "description": proj["description"],
            "features": proj["features"],
            "resume_value": proj["resume_value"],
            "portfolio_value": proj["portfolio_value"],
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]


def get_all_projects():
    return _load_projects()


def get_project_by_id(project_id):
    for proj in _load_projects():
        if proj["id"] == project_id:
            return proj
    return None


def generate_resume_entry(project_id):
    proj = get_project_by_id(project_id)
    if not proj:
        return None

    points = []
    tech = ", ".join(proj["tech_stack"][:4])

    points.append(
        f"Designed and developed {proj['title'].lower()} using {tech}"
    )

    for feature in proj["features"][:3]:
        points.append(f"Implemented {feature.lower()}")

    points.append(
        f"Managed end-to-end development lifecycle including architecture, implementation, and deployment"
    )

    return {
        "project_title": proj["title"],
        "resume_points": points,
        "skills_demonstrated": proj["skills"],
        "tech_stack": proj["tech_stack"],
    }
