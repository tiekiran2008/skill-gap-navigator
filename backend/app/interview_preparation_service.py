import json
import os
from typing import Optional

from app.skill_verification_service import get_verification_status, get_verification_summary
from app.db_service import get_career_target, list_user_skills, list_roadmaps
from app.project_recommendation_service import get_all_projects
from app.job_market_service import get_role_skills

DEFAULT_USER = "local-user"

QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "interview_questions.json")


def _load_interview_questions() -> dict:
    try:
        with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"technical": {}, "behavioral": []}


def _get_all_skills_from_questions() -> dict:
    questions = _load_interview_questions()
    return questions.get("technical", {})


def get_questions_for_skill(skill: str, category: str = None, difficulty: str = None, limit: int = 10) -> list:
    questions = _load_interview_questions()
    skill_questions = questions.get("technical", {}).get(skill, [])

    if category:
        skill_questions = [q for q in skill_questions if q.get("category") == category]
    if difficulty:
        skill_questions = [q for q in skill_questions if q.get("difficulty") == difficulty]

    return skill_questions[:limit]


def get_behavioral_questions(areas: list = None, limit: int = 10) -> list:
    questions = _load_interview_questions()
    behavioral = questions.get("behavioral", [])

    if areas:
        behavioral = [q for q in behavioral if q.get("area") in areas]

    return behavioral[:limit]


def get_project_based_questions(technologies: list) -> list:
    questions = _load_interview_questions()
    project_qs = questions.get("project_based", [])
    result = []

    for pq in project_qs:
        pq_techs = pq.get("technologies", [])
        if any(t in pq_techs for t in technologies):
            result.append(pq)

    return result


def calculate_readiness_score(target_role: str, user_skills: list, verification_status: dict, projects: list) -> dict:
    role_skills = get_role_skills(target_role)

    if not role_skills:
        return {
            "technical_readiness": 0.0,
            "verified_skill_confidence": 0.0,
            "project_readiness": 0.0,
            "overall_readiness": 0.0,
        }

    skill_names = [s.get("name") if isinstance(s, dict) else s for s in user_skills]
    role_skill_names = [s.get("name") if isinstance(s, dict) else s for s in role_skills]
    matched = [s for s in role_skill_names if s in skill_names]
    technical_readiness = (len(matched) / len(role_skill_names) * 100) if role_skill_names else 0.0

    verification_confidence = 0.0
    if matched and verification_status:
        verified_scores = []
        for skill_name in matched:
            status = verification_status.get(skill_name, {})
            score = status.get("score", 0)
            verified_scores.append(score)
        verification_confidence = sum(verified_scores) / len(verified_scores) if verified_scores else 0.0

    project_readiness = 0.0
    if projects:
        all_project_techs = set()
        for proj in projects:
            techs = proj.get("technologies", [])
            if isinstance(techs, str):
                techs = [t.strip() for t in techs.split(",")]
            all_project_techs.update(techs)

        matched_in_projects = [s for s in matched if s in all_project_techs]
        project_readiness = (len(matched_in_projects) / len(matched) * 100) if matched else 0.0

    overall = (technical_readiness * 0.4) + (verification_confidence * 0.35) + (project_readiness * 0.25)

    return {
        "technical_readiness": round(technical_readiness, 1),
        "verified_skill_confidence": round(verification_confidence, 1),
        "project_readiness": round(project_readiness, 1),
        "overall_readiness": round(overall, 1),
    }


def generate_interview_plan(target_role: str, company: str = None, user_skills: list = None) -> dict:
    if user_skills is None:
        user_skills = list_user_skills(DEFAULT_USER)

    skill_names = [s.get("name") if isinstance(s, dict) else s for s in user_skills]

    role_skills = get_role_skills(target_role)
    role_skill_names = [s.get("name") if isinstance(s, dict) else s for s in role_skills]

    verification_status = get_verification_status(DEFAULT_USER)
    skills_dict = verification_status.get("skills", {})
    projects = get_all_projects()

    all_questions = _load_interview_questions()
    technical_bank = all_questions.get("technical", {})

    missing_skills = [s for s in role_skill_names if s not in skill_names]

    low_verification = []
    for s in skill_names:
        status = skills_dict.get(s, {})
        score = status.get("score") or 100
        if score < 70:
            low_verification.append(s)

    project_techs = []
    for proj in projects:
        techs = proj.get("technologies", [])
        if isinstance(techs, str):
            techs = [t.strip() for t in techs.split(",")]
        project_techs.extend(techs)
    project_techs = list(set(project_techs))

    technical_topics = []
    prioritized_skills = []

    for skill in missing_skills:
        questions = technical_bank.get(skill, [])
        if questions:
            technical_topics.append({
                "skill": skill,
                "questions": questions,
                "priority": "high",
            })
            prioritized_skills.append(skill)

    for skill in low_verification:
        if skill not in prioritized_skills:
            questions = technical_bank.get(skill, [])
            if questions:
                technical_topics.append({
                    "skill": skill,
                    "questions": questions,
                    "priority": "medium",
                })
                prioritized_skills.append(skill)

    for skill in skill_names:
        if skill not in prioritized_skills and skill in technical_bank:
            questions = technical_bank.get(skill, [])
            if questions:
                technical_topics.append({
                    "skill": skill,
                    "questions": questions,
                    "priority": "low",
                })

    market_skills = []
    for s in role_skills:
        skill_name = s.get("name") if isinstance(s, dict) else s
        demand = s.get("demand", "medium") if isinstance(s, dict) else "medium"
        if skill_name not in prioritized_skills and skill_name in technical_bank:
            market_skills.append((skill_name, demand))

    market_skills.sort(key=lambda x: 0 if x[1] == "high" else 1)
    for skill_name, _ in market_skills[:5]:
        questions = technical_bank.get(skill_name, [])
        if questions:
            technical_topics.append({
                "skill": skill_name,
                "questions": questions,
                "priority": "low",
            })

    project_questions = get_project_based_questions(project_techs)

    behavioral_questions = get_behavioral_questions(areas=["leadership", "teamwork", "problem_solving"], limit=10)

    practice_order = []
    for skill in prioritized_skills:
        reason = "Missing for target role" if skill in missing_skills else "Low verification score"
        practice_order.append({"skill": skill, "reason": reason})

    for skill, _ in market_skills[:3]:
        practice_order.append({"skill": skill, "reason": "High market demand"})

    readiness = calculate_readiness_score(target_role, user_skills, skills_dict, projects)

    return {
        "target_role": target_role,
        "company": company,
        "technical_topics": technical_topics,
        "priority_topics": prioritized_skills,
        "project_questions": project_questions,
        "behavioral_questions": behavioral_questions,
        "recommended_practice_order": practice_order,
        "interview_readiness": readiness,
    }
