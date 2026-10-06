import json
import os
import uuid
import random
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

DEFAULT_USER = "local-user"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
USER_DATA_DIR = os.path.join(DATA_DIR, "user_data")
QUESTIONS_PATH = os.path.join(DATA_DIR, "assessments.json")
USER_ASSESSMENTS_PATH = os.path.join(USER_DATA_DIR, "user_assessments.json")


def _load_questions() -> List[Dict[str, Any]]:
    if not os.path.exists(QUESTIONS_PATH):
        return []
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_user_assessments() -> List[Dict[str, Any]]:
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    if not os.path.exists(USER_ASSESSMENTS_PATH):
        return []
    with open(USER_ASSESSMENTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_user_assessments(data: List[Dict[str, Any]]) -> None:
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    with open(USER_ASSESSMENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _find_assessment_index(assessments: List[Dict[str, Any]], user_id: str, assessment_id: str) -> int:
    for i, a in enumerate(assessments):
        if a["user_id"] == user_id and a["assessment_id"] == assessment_id:
            return i
    return -1


def get_all_skills() -> List[Dict[str, Any]]:
    questions = _load_questions()
    skills: Dict[str, Dict[str, Any]] = {}

    for q in questions:
        skill = q.get("skill", "unknown")
        if skill not in skills:
            skills[skill] = {
                "skill": skill,
                "question_count": 0,
                "difficulties": [],
                "categories": [],
            }
        skills[skill]["question_count"] += 1
        difficulty = q.get("difficulty", "unknown")
        if difficulty not in skills[skill]["difficulties"]:
            skills[skill]["difficulties"].append(difficulty)
        category = q.get("category", "unknown")
        if category not in skills[skill]["categories"]:
            skills[skill]["categories"].append(category)

    return list(skills.values())


def get_questions_for_skill(skill: str, difficulty: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    questions = _load_questions()
    filtered = [q for q in questions if q.get("skill", "").lower() == skill.lower()]
    if difficulty:
        filtered = [q for q in filtered if q.get("difficulty", "").lower() == difficulty.lower()]
    random.shuffle(filtered)
    return filtered[:limit]


def start_assessment(user_id: Optional[str] = None, skill: str = "", difficulty: Optional[str] = None, question_count: int = 10) -> Dict[str, Any]:
    if user_id is None:
        user_id = DEFAULT_USER

    questions = get_questions_for_skill(skill, difficulty=difficulty, limit=question_count)
    if not questions:
        raise ValueError(f"No questions found for skill '{skill}' with difficulty '{difficulty}'")

    assessment_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    assessment = {
        "assessment_id": assessment_id,
        "user_id": user_id,
        "skill": skill,
        "difficulty": difficulty,
        "question_count": len(questions),
        "questions": [
            {
                "question_id": q["id"],
                "skill": q.get("skill"),
                "category": q.get("category"),
                "difficulty": q.get("difficulty"),
                "type": q.get("type"),
                "question": q.get("question"),
                "options": q.get("options"),
                "correct_answer": q.get("correct_answer"),
                "explanation": q.get("explanation"),
            }
            for q in questions
        ],
        "answers": {},
        "status": "in_progress",
        "score": None,
        "total_correct": None,
        "total_questions": len(questions),
        "completed_at": None,
        "created_at": now,
    }

    assessments = _load_user_assessments()
    assessments.append(assessment)
    _save_user_assessments(assessments)

    return assessment


def submit_answer(user_id: Optional[str] = None, assessment_id: str = "", question_id: str = "", answer: str = "") -> Dict[str, Any]:
    if user_id is None:
        user_id = DEFAULT_USER

    assessments = _load_user_assessments()
    idx = _find_assessment_index(assessments, user_id, assessment_id)
    if idx == -1:
        raise ValueError(f"Assessment '{assessment_id}' not found for user '{user_id}'")

    assessment = assessments[idx]
    if assessment["status"] != "in_progress":
        raise ValueError(f"Assessment '{assessment_id}' is not in progress (status: {assessment['status']})")

    assessment["answers"][question_id] = answer
    _save_user_assessments(assessments)
    return assessment


def complete_assessment(user_id: Optional[str] = None, assessment_id: str = "") -> Dict[str, Any]:
    if user_id is None:
        user_id = DEFAULT_USER

    assessments = _load_user_assessments()
    idx = _find_assessment_index(assessments, user_id, assessment_id)
    if idx == -1:
        raise ValueError(f"Assessment '{assessment_id}' not found for user '{user_id}'")

    assessment = assessments[idx]
    if assessment["status"] != "in_progress":
        raise ValueError(f"Assessment '{assessment_id}' is not in progress (status: {assessment['status']})")

    total_correct = 0
    questions = assessment["questions"]
    answers = assessment["answers"]

    for q in questions:
        qid = q["question_id"]
        correct = q.get("correct_answer")
        user_answer = answers.get(qid)
        if user_answer is not None and user_answer.strip().lower() == str(correct).strip().lower():
            total_correct += 1

    total_questions = assessment["total_questions"]
    score = round((total_correct / total_questions) * 100, 2) if total_questions > 0 else 0.0

    now = datetime.now(timezone.utc).isoformat()
    assessment["status"] = "completed"
    assessment["score"] = score
    assessment["total_correct"] = total_correct
    assessment["completed_at"] = now

    _save_user_assessments(assessments)
    return assessment


def get_assessment_result(user_id: Optional[str] = None, assessment_id: str = "") -> Optional[Dict[str, Any]]:
    if user_id is None:
        user_id = DEFAULT_USER

    assessments = _load_user_assessments()
    for a in assessments:
        if a["user_id"] == user_id and a["assessment_id"] == assessment_id:
            return a
    return None


def list_user_assessments(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    if user_id is None:
        user_id = DEFAULT_USER

    assessments = _load_user_assessments()
    return [a for a in assessments if a["user_id"] == user_id]
