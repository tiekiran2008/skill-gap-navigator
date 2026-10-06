import json
import os
import uuid
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "user_data")
os.makedirs(DATA_DIR, exist_ok=True)

DEFAULT_USER = "local-user"


def _db_path(name):
    return os.path.join(DATA_DIR, f"{name}.json")


def _load(name):
    path = _db_path(name)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def _save(name, data):
    path = _db_path(name)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


# Profiles
def get_profile(user_id=DEFAULT_USER):
    db = _load("profiles")
    return db.get(user_id)


def upsert_profile(user_id=DEFAULT_USER, data=None):
    if data is None:
        data = {}
    db = _load("profiles")
    db[user_id] = data
    _save("profiles", db)
    return data


# Resumes
def list_resumes(user_id=DEFAULT_USER):
    db = _load("resumes")
    return db.get(user_id, [])


def create_resume(user_id=DEFAULT_USER, filename="", parsed_data=None):
    if parsed_data is None:
        parsed_data = {}
    db = _load("resumes")
    if user_id not in db:
        db[user_id] = []
    row = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "filename": filename,
        "parsed_data": parsed_data,
        "created_at": datetime.now().isoformat(),
    }
    db[user_id].insert(0, row)
    _save("resumes", db)
    return row


def delete_resume(user_id=DEFAULT_USER, resume_id=""):
    db = _load("resumes")
    if user_id in db:
        db[user_id] = [r for r in db[user_id] if r["id"] != resume_id]
        _save("resumes", db)


# User Skills
def list_user_skills(user_id=DEFAULT_USER):
    db = _load("user_skills")
    return db.get(user_id, [])


def upsert_user_skills(user_id=DEFAULT_USER, skills=None):
    if skills is None:
        skills = []
    db = _load("user_skills")
    processed = []
    for s in skills:
        if isinstance(s, str):
            s = {"skill": s, "user_id": user_id, "created_at": datetime.now().isoformat()}
        elif isinstance(s, dict):
            s["user_id"] = user_id
            if "created_at" not in s:
                s["created_at"] = datetime.now().isoformat()
        processed.append(s)
    db[user_id] = processed
    _save("user_skills", db)


# Career Targets
def get_career_target(user_id=DEFAULT_USER):
    db = _load("career_targets")
    targets = db.get(user_id, [])
    return targets[0] if targets else None


def upsert_career_target(user_id=DEFAULT_USER, target_role=""):
    db = _load("career_targets")
    row = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "target_role": target_role,
        "created_at": datetime.now().isoformat(),
    }
    existing = db.get(user_id, [])
    if existing:
        existing[0]["target_role"] = target_role
        row = existing[0]
    else:
        db[user_id] = [row]
    _save("career_targets", db)
    return row


# Company Analyses
def list_company_analyses(user_id=DEFAULT_USER):
    db = _load("company_analyses")
    return db.get(user_id, [])


def create_company_analysis(user_id=DEFAULT_USER, company="", role="", analysis_data=None):
    if analysis_data is None:
        analysis_data = {}
    db = _load("company_analyses")
    if user_id not in db:
        db[user_id] = []
    row = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "company": company,
        "role": role,
        "analysis_data": analysis_data,
        "created_at": datetime.now().isoformat(),
    }
    db[user_id].insert(0, row)
    _save("company_analyses", db)
    return row


def delete_company_analysis(user_id=DEFAULT_USER, analysis_id=""):
    db = _load("company_analyses")
    if user_id in db:
        db[user_id] = [a for a in db[user_id] if a["id"] != analysis_id]
        _save("company_analyses", db)


# Career Analyses
def list_career_analyses(user_id=DEFAULT_USER):
    db = _load("career_analyses")
    return db.get(user_id, [])


def create_career_analysis(user_id=DEFAULT_USER, recommendations=None, target_role=""):
    if recommendations is None:
        recommendations = []
    db = _load("career_analyses")
    if user_id not in db:
        db[user_id] = []
    row = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "recommendations": recommendations,
        "target_role": target_role,
        "created_at": datetime.now().isoformat(),
    }
    db[user_id].insert(0, row)
    _save("career_analyses", db)
    return row


def delete_career_analysis(user_id=DEFAULT_USER, analysis_id=""):
    db = _load("career_analyses")
    if user_id in db:
        db[user_id] = [a for a in db[user_id] if a["id"] != analysis_id]
        _save("career_analyses", db)


# Roadmaps
def list_roadmaps(user_id=DEFAULT_USER):
    db = _load("roadmaps")
    return db.get(user_id, [])


def create_roadmap(user_id=DEFAULT_USER, target_role="", roadmap_data=None):
    if roadmap_data is None:
        roadmap_data = {}
    db = _load("roadmaps")
    if user_id not in db:
        db[user_id] = []
    row = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "target_role": target_role,
        "roadmap_data": roadmap_data,
        "created_at": datetime.now().isoformat(),
    }
    db[user_id].insert(0, row)
    _save("roadmaps", db)
    return row


def get_roadmap(user_id=DEFAULT_USER, roadmap_id=""):
    db = _load("roadmaps")
    items = db.get(user_id, [])
    for r in items:
        if r["id"] == roadmap_id:
            return r
    return None


def delete_roadmap(user_id=DEFAULT_USER, roadmap_id=""):
    db_progress = _load("roadmap_progress")
    if user_id in db_progress:
        db_progress[user_id] = {k: v for k, v in db_progress[user_id].items() if k != roadmap_id}
        _save("roadmap_progress", db_progress)
    db = _load("roadmaps")
    if user_id in db:
        db[user_id] = [r for r in db[user_id] if r["id"] != roadmap_id]
        _save("roadmaps", db)


# Roadmap Progress
def list_roadmap_progress(user_id=DEFAULT_USER, roadmap_id=""):
    db = _load("roadmap_progress")
    user_data = db.get(user_id, {})
    roadmap_data = user_data.get(roadmap_id, {})
    return [{"skill_name": k, "status": v} for k, v in roadmap_data.items()]


def upsert_roadmap_progress(user_id=DEFAULT_USER, roadmap_id="", skill_name="", skill_status="Not Started"):
    db = _load("roadmap_progress")
    if user_id not in db:
        db[user_id] = {}
    if roadmap_id not in db[user_id]:
        db[user_id][roadmap_id] = {}
    db[user_id][roadmap_id][skill_name] = skill_status
    _save("roadmap_progress", db)
    return {"skill_name": skill_name, "status": skill_status}


def bulk_upsert_roadmap_progress(user_id=DEFAULT_USER, roadmap_id="", progress=None):
    if progress is None:
        progress = []
    db = _load("roadmap_progress")
    if user_id not in db:
        db[user_id] = {}
    if roadmap_id not in db[user_id]:
        db[user_id][roadmap_id] = {}
    for p in progress:
        db[user_id][roadmap_id][p["skill_name"]] = p["status"]
    _save("roadmap_progress", db)


# Assistant Chat History
def list_chat_history(user_id=DEFAULT_USER, limit=20):
    db = _load("chat_history")
    messages = db.get(user_id, [])
    return messages[:limit]


def create_chat_message(user_id=DEFAULT_USER, role="", content="", tools_used=None, relevant_skills=None, suggested_action="", source="fallback"):
    db = _load("chat_history")
    if user_id not in db:
        db[user_id] = []
    row = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "role": role,
        "content": content,
        "tools_used": tools_used or [],
        "relevant_skills": relevant_skills or [],
        "suggested_action": suggested_action,
        "source": source,
        "created_at": datetime.now().isoformat(),
    }
    db[user_id].insert(0, row)
    _save("chat_history", db)
    return row


def clear_chat_history(user_id=DEFAULT_USER):
    db = _load("chat_history")
    db[user_id] = []
    _save("chat_history", db)
