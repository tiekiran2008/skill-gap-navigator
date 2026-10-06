import json
import uuid
import os
from datetime import datetime, timezone
from typing import Optional


DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
QUESTIONS_FILE = os.path.join(DATA_DIR, 'interview_questions.json')
INTERVIEWS_FILE = os.path.join(DATA_DIR, 'user_data', 'mock_interviews.json')

MODE_QUESTION_COUNTS = {
    "quick": 5,
    "technical": 10,
    "project": 8,
    "behavioral": 10,
    "full": (15, 20),
}

MODE_CATEGORIES = {
    "quick": None,
    "technical": ["technical"],
    "project": ["project"],
    "behavioral": ["behavioral"],
    "full": None,
}


def _load_questions() -> list:
    if not os.path.exists(QUESTIONS_FILE):
        return []
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_interviews() -> dict:
    os.makedirs(os.path.dirname(INTERVIEWS_FILE), exist_ok=True)
    if not os.path.exists(INTERVIEWS_FILE):
        return {}
    with open(INTERVIEWS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_interviews(data: dict):
    os.makedirs(os.path.dirname(INTERVIEWS_FILE), exist_ok=True)
    with open(INTERVIEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def evaluate_answer(answer: str, expected_concepts: list) -> dict:
    answer_lower = answer.lower()
    matched = []
    missing = []

    for concept in expected_concepts:
        concept_lower = concept.lower()
        keywords = [w for w in concept_lower.split() if len(w) > 3]
        if not keywords:
            keywords = [concept_lower]

        matched_keywords = sum(1 for kw in keywords if kw in answer_lower)
        if matched_keywords >= max(1, len(keywords) // 2):
            matched.append(concept)
        else:
            partial = any(
                kw[:max(4, len(kw) // 2)] in answer_lower for kw in keywords
            )
            if partial:
                matched.append(concept)
            else:
                missing.append(concept)

    total = len(expected_concepts) if expected_concepts else 1
    score = round((len(matched) / total) * 100, 1)

    if score >= 80:
        feedback = "Excellent answer. You covered most key concepts thoroughly."
    elif score >= 50:
        feedback = f"Good effort. You missed: {', '.join(missing[:3])}."
    elif score > 0:
        feedback = (
            f"Partial answer. Consider discussing: {', '.join(missing[:4])}."
        )
    else:
        feedback = (
            "Your answer did not cover the expected concepts. "
            "Review the topic and try to address the key points."
        )

    return {
        "score": score,
        "matched_concepts": matched,
        "missing_concepts": missing,
        "feedback": feedback,
    }


def _select_questions(
    all_questions: list,
    mode: str,
    target_role: Optional[str] = None,
    skills: Optional[list] = None,
) -> list:
    count_spec = MODE_QUESTION_COUNTS.get(mode, 5)
    if isinstance(count_spec, tuple):
        import random
        count = random.randint(count_spec[0], count_spec[1])
    else:
        count = count_spec

    categories = MODE_CATEGORIES.get(mode)
    candidates = all_questions[:]
    if categories:
        candidates = [q for q in candidates if q.get("category") in categories]

    if skills:
        skill_match = [
            q for q in candidates
            if any(s.lower() in q.get("skill", "").lower() for s in skills)
        ]
        if skill_match:
            candidates = skill_match

    import random
    random.shuffle(candidates)
    return candidates[:count]


def _format_question(q: dict) -> dict:
    return {
        "id": q["id"],
        "question": q["question"],
        "category": q.get("category", "technical"),
        "skill": q.get("skill", ""),
        "difficulty": q.get("difficulty", "Medium"),
        "expected_concepts": q.get("expected_concepts", []),
        "user_answer": None,
        "score": None,
        "matched_concepts": [],
        "missing_concepts": [],
        "feedback": "",
    }


def start_interview(
    user_id: str,
    mode: str,
    target_role: str = None,
    company: str = None,
    skills: list = None,
) -> dict:
    if mode not in MODE_QUESTION_COUNTS:
        raise ValueError(
            f"Invalid mode '{mode}'. Must be one of: {list(MODE_QUESTION_COUNTS)}"
        )

    all_questions = _load_questions()
    if not all_questions:
        raise FileNotFoundError(
            f"No questions found at {QUESTIONS_FILE}"
        )

    selected = _select_questions(all_questions, mode, target_role, skills)
    if not selected:
        raise ValueError("No questions available matching the given filters.")

    interview_id = str(uuid.uuid4())
    questions = [_format_question(q) for q in selected]

    interview = {
        "interview_id": interview_id,
        "user_id": user_id,
        "mode": mode,
        "target_role": target_role or "AI/ML Engineer",
        "company": company,
        "status": "in_progress",
        "questions": questions,
        "current_question_index": 0,
        "started_at": _now_iso(),
        "completed_at": None,
        "overall_score": None,
        "technical_score": None,
        "project_score": None,
        "behavioral_score": None,
        "strong_areas": [],
        "weak_areas": [],
    }

    interviews = _load_interviews()
    if user_id not in interviews:
        interviews[user_id] = []
    interviews[user_id].append(interview)
    _save_interviews(interviews)

    return interview


def _find_interview(interviews: dict, user_id: str, interview_id: str) -> Optional[dict]:
    for inv in interviews.get(user_id, []):
        if inv["interview_id"] == interview_id:
            return inv
    return None


def _save_interview(interviews: dict, user_id: str, interview_id: str, updated: dict):
    for i, inv in enumerate(interviews.get(user_id, [])):
        if inv["interview_id"] == interview_id:
            interviews[user_id][i] = updated
            break
    _save_interviews(interviews)


def submit_answer(user_id: str, interview_id: str, question_id: str, answer: str) -> dict:
    interviews = _load_interviews()
    interview = _find_interview(interviews, user_id, interview_id)

    if not interview:
        return {"success": False, "error": "Interview not found."}
    if interview["status"] != "in_progress":
        return {"success": False, "error": "Interview is not in progress."}

    q_index = None
    for i, q in enumerate(interview["questions"]):
        if q["id"] == question_id:
            q_index = i
            break

    if q_index is None:
        return {"success": False, "error": "Question not found in this interview."}

    question = interview["questions"][q_index]
    eval_result = evaluate_answer(answer, question["expected_concepts"])

    question["user_answer"] = answer
    question["score"] = eval_result["score"]
    question["matched_concepts"] = eval_result["matched_concepts"]
    question["missing_concepts"] = eval_result["missing_concepts"]
    question["feedback"] = eval_result["feedback"]

    if q_index == interview["current_question_index"]:
        interview["current_question_index"] = min(
            q_index + 1, len(interview["questions"]) - 1
        )

    _save_interview(interviews, user_id, interview_id, interview)

    return {
        "success": True,
        "question_id": question_id,
        "score": eval_result["score"],
        "feedback": eval_result["feedback"],
        "matched_concepts": eval_result["matched_concepts"],
        "missing_concepts": eval_result["missing_concepts"],
    }


def _compute_category_scores(questions: list) -> dict:
    category_scores = {}
    for q in questions:
        cat = q.get("category", "unknown")
        if q["score"] is not None:
            category_scores.setdefault(cat, []).append(q["score"])
    return {
        cat: round(sum(scores) / len(scores), 1)
        for cat, scores in category_scores.items()
    }


def _identify_areas(questions: list) -> tuple:
    skill_scores = {}
    for q in questions:
        skill = q.get("skill", "General")
        if q["score"] is not None:
            skill_scores.setdefault(skill, []).append(q["score"])

    avg_scores = {
        skill: sum(sc) / len(sc) for skill, sc in skill_scores.items()
    }

    strong = [s for s, sc in avg_scores.items() if sc >= 70]
    weak = [s for s, sc in avg_scores.items() if sc < 50]
    return strong, weak


def complete_interview(user_id: str, interview_id: str) -> dict:
    interviews = _load_interviews()
    interview = _find_interview(interviews, user_id, interview_id)

    if not interview:
        return {"success": False, "error": "Interview not found."}
    if interview["status"] != "in_progress":
        return {"success": False, "error": "Interview already completed."}

    all_scores = [
        q["score"] for q in interview["questions"] if q["score"] is not None
    ]
    overall = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0.0

    cat_scores = _compute_category_scores(interview["questions"])
    strong, weak = _identify_areas(interview["questions"])

    interview["status"] = "completed"
    interview["completed_at"] = _now_iso()
    interview["overall_score"] = overall
    interview["technical_score"] = cat_scores.get("technical")
    interview["project_score"] = cat_scores.get("project")
    interview["behavioral_score"] = cat_scores.get("behavioral")
    interview["strong_areas"] = strong
    interview["weak_areas"] = weak

    _save_interview(interviews, user_id, interview_id, interview)

    return {
        "success": True,
        "interview_id": interview_id,
        "overall_score": overall,
        "technical_score": interview["technical_score"],
        "project_score": interview["project_score"],
        "behavioral_score": interview["behavioral_score"],
        "strong_areas": strong,
        "weak_areas": weak,
        "total_questions": len(interview["questions"]),
        "answered_questions": len(all_scores),
    }


def get_interview_result(user_id: str, interview_id: str) -> dict:
    interviews = _load_interviews()
    interview = _find_interview(interviews, user_id, interview_id)

    if not interview:
        return {"error": "Interview not found."}
    if interview["status"] != "completed":
        return {"error": "Interview has not been completed yet."}

    return interview


def list_user_interviews(user_id: str) -> list:
    interviews = _load_interviews()
    user_interviews = interviews.get(user_id, [])
    summaries = []
    for inv in user_interviews:
        summaries.append({
            "interview_id": inv["interview_id"],
            "mode": inv["mode"],
            "target_role": inv["target_role"],
            "company": inv["company"],
            "status": inv["status"],
            "started_at": inv["started_at"],
            "completed_at": inv["completed_at"],
            "overall_score": inv["overall_score"],
            "total_questions": len(inv["questions"]),
            "answered_questions": sum(
                1 for q in inv["questions"] if q["user_answer"] is not None
            ),
        })
    return summaries
