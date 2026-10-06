import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "user_data")
DATA_FILE = os.path.join(DATA_DIR, "skill_verification.json")
DEFAULT_USER = "local-user"


def _load_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_data(data):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _ensure_user(data, user_id):
    if user_id not in data:
        data[user_id] = {"skills": {}, "summary": {}}
    return data[user_id]


def _recompute_summary(user_entry):
    skills = user_entry.get("skills", {})
    total_detected = sum(1 for s in skills.values() if s.get("status") == "detected")
    total_verified = sum(1 for s in skills.values() if s.get("status") == "verified")
    scored = [s["score"] for s in skills.values() if s.get("score") is not None]
    avg_score = round(sum(scored) / len(scored), 1) if scored else 0
    total_assessed = sum(1 for s in skills.values() if s.get("assessments_taken", 0) > 0)
    verification_rate = round(total_verified / total_assessed, 2) if total_assessed > 0 else 0
    user_entry["summary"] = {
        "total_detected": total_detected,
        "total_verified": total_verified,
        "avg_score": avg_score,
        "verification_rate": verification_rate,
    }
    return user_entry["summary"]


def get_verification_status(user_id=DEFAULT_USER):
    data = _load_data()
    user_entry = _ensure_user(data, user_id)
    _recompute_summary(user_entry)
    _save_data(data)
    return user_entry


def update_from_assessment(user_id, skill, score):
    data = _load_data()
    user_entry = _ensure_user(data, user_id)
    skills = user_entry.get("skills", {})
    now = datetime.now().isoformat()

    if skill not in skills:
        skills[skill] = {
            "status": "detected",
            "score": None,
            "assessments_taken": 0,
            "best_score": None,
            "last_assessed": None,
        }

    entry = skills[skill]
    entry["assessments_taken"] = entry.get("assessments_taken", 0) + 1
    entry["last_assessed"] = now
    entry["score"] = score

    if entry["best_score"] is None or score > entry["best_score"]:
        entry["best_score"] = score

    if score >= 70:
        entry["status"] = "verified"
    else:
        entry["status"] = "needs_review"

    _recompute_summary(user_entry)
    _save_data(data)
    return entry


def sync_detected_skills(user_id, detected_skills):
    data = _load_data()
    user_entry = _ensure_user(data, user_id)
    skills = user_entry.get("skills", {})

    for skill in detected_skills:
        if skill not in skills:
            skills[skill] = {
                "status": "detected",
                "score": None,
                "assessments_taken": 0,
                "best_score": None,
                "last_assessed": None,
            }

    _recompute_summary(user_entry)
    _save_data(data)
    return user_entry


def get_verification_summary(user_id=DEFAULT_USER):
    data = _load_data()
    user_entry = _ensure_user(data, user_id)
    return _recompute_summary(user_entry)


def get_skill_details(user_id, skill):
    data = _load_data()
    user_entry = _ensure_user(data, user_id)
    skills = user_entry.get("skills", {})
    if skill not in skills:
        return None
    return skills[skill]
