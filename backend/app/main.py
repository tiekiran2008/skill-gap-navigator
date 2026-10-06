from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

from app.resume_parser import parse_resume, parse_resume_structured
from app.skill_matcher import (
    extract_skills_from_text, load_careers, load_companies,
    analyze_gap_new, analyze_company_gap,
)
from app.gap_analyzer import generate_gap_report
from app.company_service import (
    get_all_companies, recommend_companies as recommend_companies_v1,
    analyze_company as analyze_company_v1,
)
from app.recommendation_engine import recommend_careers
from app.roadmap_engine import build_roadmap
from app.career_assistant_service import chat as assistant_chat
from app.job_market_service import get_market_overview, get_role_skills, analyze_user, get_company_view, get_trend
from app.project_recommendation_service import recommend_projects, get_all_projects, get_project_by_id, generate_resume_entry
from app.resume_improvement_service import analyze_resume
from app.assessment_service import get_all_skills, start_assessment, submit_answer, complete_assessment, get_assessment_result, list_user_assessments
from app.skill_verification_service import get_verification_status, update_from_assessment, sync_detected_skills, get_verification_summary, get_skill_details
from app.interview_preparation_service import generate_interview_plan, get_questions_for_skill, get_behavioral_questions, get_project_based_questions
from app.mock_interview_service import start_interview, submit_answer as submit_interview_answer, complete_interview, get_interview_result, list_user_interviews
import app.db_service as db

app = FastAPI(title="Skill Gap Navigator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

USER_ID = "local-user"


@app.get("/health")
def health_check():
    return {"status": "running"}


@app.get("/careers")
def get_careers():
    careers = load_careers()
    return {"careers": [{"name": c["name"], "skills_count": len(c["required_skills"])} for c in careers]}


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        text = parse_resume(file_path)
        skills = extract_skills_from_text(text)
    finally:
        os.remove(file_path)

    return {
        "filename": file.filename,
        "extracted_text_length": len(text),
        "skills": skills,
        "skills_count": len(skills),
    }


@app.post("/api/v1/resume/analyze")
async def analyze_resume_v1(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        profile = parse_resume_structured(file_path)
    finally:
        os.remove(file_path)

    profile.pop("raw_text", None)
    return profile


@app.post("/analyze")
def analyze(data: dict):
    skills = data.get("skills", [])
    target_role = data.get("target_role", "")

    if not skills:
        raise HTTPException(status_code=400, detail="No skills provided")
    if not target_role:
        raise HTTPException(status_code=400, detail="No target role provided")

    result = analyze_gap_new(skills, target_role)

    if result is None:
        raise HTTPException(status_code=400, detail=f"Career role '{target_role}' not found")

    return result


@app.post("/api/v1/gap-analysis")
def gap_analysis(data: dict):
    skills = data.get("skills", [])
    target_role = data.get("target_role", "")

    if not skills:
        raise HTTPException(status_code=400, detail="No skills provided")
    if not target_role:
        raise HTTPException(status_code=400, detail="No target role provided")

    careers = load_careers()
    role = None
    for c in careers:
        if c["name"] == target_role:
            role = c
            break

    if not role:
        raise HTTPException(status_code=400, detail=f"Career role '{target_role}' not found")

    report = generate_gap_report(skills, role)
    return report


@app.post("/api/v1/careers/recommend")
def recommend_careers_endpoint(data: dict):
    skills = data.get("skills", [])
    if not skills:
        raise HTTPException(status_code=400, detail="No skills provided")

    user_profile = data.get("profile")
    target_career = data.get("target_career")
    top_n = data.get("top_n", 10)

    recommendations = recommend_careers(skills, user_profile, target_career, top_n)
    return {"recommendations": recommendations}


@app.get("/companies")
def get_companies():
    companies = load_companies()
    result = []
    for c in companies:
        result.append({
            "name": c["name"],
            "industry": c.get("industry", ""),
            "roles": [{"title": r["title"], "description": r.get("description", "")} for r in c["roles"]],
        })
    return {"companies": result}


@app.get("/api/v1/companies")
def get_companies_v1():
    return {"companies": get_all_companies()}


@app.post("/recommend-companies")
def recommend_companies_endpoint(data: dict):
    skills = data.get("skills", [])
    if not skills:
        raise HTTPException(status_code=400, detail="No skills provided")
    from app.skill_matcher import recommend_companies
    companies = recommend_companies(skills)
    return {"companies": companies}


@app.post("/api/v1/companies/recommend")
def recommend_companies_v1_endpoint(data: dict):
    skills = data.get("skills", [])
    if not skills:
        raise HTTPException(status_code=400, detail="No skills provided")
    companies = recommend_companies_v1(skills)
    return {"companies": companies}


@app.post("/company-analysis")
def company_analysis_endpoint(data: dict):
    skills = data.get("skills", [])
    company = data.get("company", "")
    role = data.get("role", "")
    if not skills:
        raise HTTPException(status_code=400, detail="No skills provided")
    if not company:
        raise HTTPException(status_code=400, detail="No company provided")
    if not role:
        raise HTTPException(status_code=400, detail="No role provided")
    result = analyze_company_gap(skills, company, role)
    if result is None:
        raise HTTPException(status_code=400, detail=f"Company '{company}' or role '{role}' not found")
    return result


@app.post("/api/v1/companies/analyze")
def analyze_company_v1_endpoint(data: dict):
    skills = data.get("skills", [])
    company = data.get("company", "")
    role = data.get("role")
    if not skills:
        raise HTTPException(status_code=400, detail="No skills provided")
    if not company:
        raise HTTPException(status_code=400, detail="No company provided")
    result = analyze_company_v1(skills, company, role)
    if result is None:
        raise HTTPException(status_code=400, detail=f"Company '{company}' or role '{role}' not found")
    return result


@app.post("/api/v1/roadmap/generate")
def generate_roadmap_endpoint(data: dict):
    missing_skills = data.get("missing_skills", [])
    if not missing_skills:
        raise HTTPException(status_code=400, detail="No missing skills provided")
    user_skills = data.get("user_skills", [])
    target_role = data.get("target_role")
    roadmap = build_roadmap(missing_skills, user_skills, target_role)
    return roadmap


# ── User Data Endpoints (local persistence) ──────────────────


@app.get("/api/v1/user/profile")
def get_user_profile():
    profile = db.get_profile()
    return {"profile": profile}


@app.put("/api/v1/user/profile")
def update_user_profile(data: dict):
    profile = db.upsert_profile(USER_ID, data)
    return {"profile": profile}


@app.get("/api/v1/user/skills")
def get_user_skills():
    skills = db.list_user_skills()
    return {"skills": skills}


@app.post("/api/v1/user/skills")
def save_user_skills(data: dict):
    skills = data.get("skills", [])
    db.upsert_user_skills(USER_ID, skills)
    return {"status": "saved"}


@app.get("/api/v1/user/resumes")
def get_user_resumes():
    resumes = db.list_resumes()
    return {"resumes": resumes}


@app.post("/api/v1/user/resumes")
def save_resume(data: dict):
    filename = data.get("filename", "")
    parsed_data = data.get("parsed_data", {})
    resume = db.create_resume(USER_ID, filename, parsed_data)
    return {"resume": resume}


@app.delete("/api/v1/user/resumes/{resume_id}")
def remove_resume(resume_id: str):
    db.delete_resume(USER_ID, resume_id)
    return {"status": "deleted"}


@app.get("/api/v1/user/career-target")
def get_career_target():
    target = db.get_career_target()
    return {"target": target}


@app.post("/api/v1/user/career-target")
def save_career_target(data: dict):
    target_role = data.get("target_role", "")
    target = db.upsert_career_target(USER_ID, target_role)
    return {"target": target}


@app.get("/api/v1/user/company-analyses")
def get_company_analyses():
    analyses = db.list_company_analyses()
    return {"analyses": analyses}


@app.post("/api/v1/user/company-analyses")
def save_company_analysis(data: dict):
    company = data.get("company", "")
    role = data.get("role", "")
    analysis_data = data.get("analysis_data", {})
    analysis = db.create_company_analysis(USER_ID, company, role, analysis_data)
    return {"analysis": analysis}


@app.delete("/api/v1/user/company-analyses/{analysis_id}")
def remove_company_analysis(analysis_id: str):
    db.delete_company_analysis(USER_ID, analysis_id)
    return {"status": "deleted"}


@app.get("/api/v1/user/career-analyses")
def get_career_analyses():
    analyses = db.list_career_analyses()
    return {"analyses": analyses}


@app.post("/api/v1/user/career-analyses")
def save_career_analysis(data: dict):
    recommendations = data.get("recommendations", [])
    target_role = data.get("target_role", "")
    analysis = db.create_career_analysis(USER_ID, recommendations, target_role)
    return {"analysis": analysis}


@app.delete("/api/v1/user/career-analyses/{analysis_id}")
def remove_career_analysis(analysis_id: str):
    db.delete_career_analysis(USER_ID, analysis_id)
    return {"status": "deleted"}


@app.get("/api/v1/user/roadmaps")
def get_roadmaps():
    roadmaps = db.list_roadmaps()
    return {"roadmaps": roadmaps}


@app.post("/api/v1/user/roadmaps")
def save_roadmap(data: dict):
    target_role = data.get("target_role", "")
    roadmap_data = data.get("roadmap_data", {})
    roadmap = db.create_roadmap(USER_ID, target_role, roadmap_data)
    return {"roadmap": roadmap}


@app.get("/api/v1/user/roadmaps/{roadmap_id}")
def get_single_roadmap(roadmap_id: str):
    roadmap = db.get_roadmap(USER_ID, roadmap_id)
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    return {"roadmap": roadmap}


@app.delete("/api/v1/user/roadmaps/{roadmap_id}")
def remove_roadmap(roadmap_id: str):
    db.delete_roadmap(USER_ID, roadmap_id)
    return {"status": "deleted"}


@app.get("/api/v1/user/roadmaps/{roadmap_id}/progress")
def get_progress(roadmap_id: str):
    progress = db.list_roadmap_progress(USER_ID, roadmap_id)
    return {"progress": progress}


@app.post("/api/v1/user/roadmaps/{roadmap_id}/progress")
def save_progress(roadmap_id: str, data: dict):
    skill_name = data.get("skill_name", "")
    status_val = data.get("status", "Not Started")
    result = db.upsert_roadmap_progress(USER_ID, roadmap_id, skill_name, status_val)
    return {"progress": result}


@app.post("/api/v1/user/roadmaps/{roadmap_id}/progress/bulk")
def save_bulk_progress(roadmap_id: str, data: dict):
    progress = data.get("progress", [])
    db.bulk_upsert_roadmap_progress(USER_ID, roadmap_id, progress)
    return {"status": "saved"}


@app.post("/api/v1/user/roadmaps/latest/progress")
def save_latest_progress(data: dict):
    roadmaps = db.list_roadmaps(USER_ID)
    if not roadmaps:
        raise HTTPException(status_code=404, detail="No roadmaps found")
    roadmap_id = roadmaps[0]["id"]
    skill_name = data.get("skill_name", "")
    status_val = data.get("status", "Not Started")
    result = db.upsert_roadmap_progress(USER_ID, roadmap_id, skill_name, status_val)
    return {"progress": result}


# ── Job Market Intelligence ──────────────────────────────────


@app.get("/api/v1/market/roles")
def market_roles():
    return get_market_overview()


@app.get("/api/v1/market/skills")
def market_skills_for_role(role: str = ""):
    result = get_role_skills(role)
    if not result["top_skills"]:
        raise HTTPException(status_code=404, detail=f"No data for role '{role}'")
    return result


@app.post("/api/v1/market/analyze-user")
def market_analyze_user(data: dict):
    user_skills = data.get("skills", [])
    target_role = data.get("target_role")
    return analyze_user(user_skills, target_role)


@app.get("/api/v1/market/company/{company}")
def market_company(company: str):
    result = get_company_view(company)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No data for company '{company}'")
    return result


@app.post("/api/v1/market/trend")
def market_trend(data: dict):
    role = data.get("role", "")
    user_skills = data.get("skills", [])
    if not role:
        raise HTTPException(status_code=400, detail="No role provided")
    return get_trend(role, user_skills if user_skills else None)


# ── Project Recommendations ─────────────────────────────────


@app.get("/api/v1/projects")
def list_projects():
    return {"projects": get_all_projects()}


@app.post("/api/v1/projects/recommend")
def recommend_projects_endpoint(data: dict):
    return {"recommended_projects": recommend_projects(
        skills=data.get("skills", []),
        missing_skills=data.get("missing_skills", []),
        target_role=data.get("target_role"),
        market_skills=data.get("market_skills", []),
        company=data.get("company"),
    )}


@app.post("/api/v1/projects/resume-entry")
def project_resume_entry(data: dict):
    project_id = data.get("project_id", "")
    if not project_id:
        raise HTTPException(status_code=400, detail="No project_id provided")
    result = generate_resume_entry(project_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return result


# ── Resume Improvement ──────────────────────────────────────


@app.post("/api/v1/resume/improve")
def resume_improve(data: dict):
    profile = data.get("profile", {})
    target_role_skills = data.get("target_role_skills", [])
    return analyze_resume(profile, target_role_skills)


# ── Assistant Endpoints ─────────────────────────────────────


@app.post("/api/v1/assistant/chat")
def assistant_chat_endpoint(data: dict):
    message = data.get("message", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="No message provided")

    history_rows = db.list_chat_history(limit=10)
    history = [{"role": h["role"], "content": h["content"]} for h in reversed(history_rows)]

    result = assistant_chat(USER_ID, message, history)

    db.create_chat_message(USER_ID, "user", message)
    db.create_chat_message(
        USER_ID,
        "assistant",
        result["response"],
        tools_used=result.get("tools_used", []),
        relevant_skills=result.get("relevant_skills", []),
        suggested_action=result.get("suggested_action", ""),
        source=result.get("source", "fallback"),
    )

    return {
        "response": result["response"],
        "relevant_skills": result.get("relevant_skills", []),
        "suggested_action": result.get("suggested_action"),
        "source": result.get("source", "fallback"),
    }


@app.get("/api/v1/assistant/history")
def get_chat_history():
    history = db.list_chat_history(limit=50)
    return {"history": list(reversed(history))}


@app.delete("/api/v1/assistant/history")
def clear_chat():
    db.clear_chat_history()
    return {"status": "cleared"}


# ── Skill Assessment & Verification ──────────────────────────


@app.get("/api/v1/assessments/skills")
def assessment_skills():
    return {"skills": get_all_skills()}


@app.post("/api/v1/assessments/start")
def start_assessment_endpoint(data: dict):
    skill = data.get("skill", "")
    if not skill:
        raise HTTPException(status_code=400, detail="No skill provided")
    difficulty = data.get("difficulty")
    question_count = data.get("question_count", 10)
    result = start_assessment(USER_ID, skill, difficulty, question_count)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No questions for skill '{skill}'")
    return result


@app.post("/api/v1/assessments/{assessment_id}/answer")
def submit_answer_endpoint(assessment_id: str, data: dict):
    question_id = data.get("question_id", "")
    answer = data.get("answer", "")
    if not question_id or not answer:
        raise HTTPException(status_code=400, detail="question_id and answer required")
    result = submit_answer(USER_ID, assessment_id, question_id, answer)
    if result is None:
        raise HTTPException(status_code=404, detail="Assessment not found or already completed")
    return result


@app.post("/api/v1/assessments/{assessment_id}/complete")
def complete_assessment_endpoint(assessment_id: str):
    result = complete_assessment(USER_ID, assessment_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    if result.get("status") == "completed":
        update_from_assessment(USER_ID, result["skill"], result["score"])
    return result


@app.get("/api/v1/assessments/history")
def assessment_history():
    return {"assessments": list_user_assessments(USER_ID)}


@app.get("/api/v1/assessments/{assessment_id}")
def get_assessment_endpoint(assessment_id: str):
    result = get_assessment_result(USER_ID, assessment_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return result


@app.get("/api/v1/skills/verification")
def skill_verification():
    return get_verification_status(USER_ID)


@app.get("/api/v1/skills/verification/summary")
def skill_verification_summary():
    return get_verification_summary(USER_ID)


@app.get("/api/v1/skills/verification/{skill}")
def skill_verification_detail(skill: str):
    result = get_skill_details(USER_ID, skill)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No data for skill '{skill}'")
    return result


@app.post("/api/v1/skills/verification/sync")
def sync_skills(data: dict):
    skills = data.get("skills", [])
    sync_detected_skills(USER_ID, skills)
    return {"status": "synced"}


# ── Interview Preparation & Mock Interviews ──────────────────


@app.post("/api/v1/interview/plan")
def interview_plan(data: dict):
    target_role = data.get("target_role", "")
    company = data.get("company")
    user_skills = data.get("skills")
    plan = generate_interview_plan(target_role, company, user_skills)
    return plan


@app.post("/api/v1/interview/start")
def interview_start(data: dict):
    mode = data.get("mode", "quick")
    target_role = data.get("target_role")
    company = data.get("company")
    skills = data.get("skills")
    result = start_interview(USER_ID, mode, target_role, company, skills)
    if result is None:
        raise HTTPException(status_code=400, detail="Failed to start interview")
    return result


@app.post("/api/v1/interview/{interview_id}/answer")
def interview_answer(interview_id: str, data: dict):
    question_id = data.get("question_id", "")
    answer = data.get("answer", "")
    if not question_id:
        raise HTTPException(status_code=400, detail="question_id required")
    result = submit_interview_answer(USER_ID, interview_id, question_id, answer)
    if result is None:
        raise HTTPException(status_code=404, detail="Interview not found or already completed")
    return result


@app.post("/api/v1/interview/{interview_id}/complete")
def interview_complete(interview_id: str):
    result = complete_interview(USER_ID, interview_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Interview not found")
    return result


@app.get("/api/v1/interview/history")
def interview_history():
    return {"interviews": list_user_interviews(USER_ID)}


@app.get("/api/v1/interview/questions")
def interview_questions(skill: str = "", category: str = "", difficulty: str = "", limit: int = 10):
    if skill:
        questions = get_questions_for_skill(skill, category or None, difficulty or None, limit)
    elif category == "behavioral":
        questions = get_behavioral_questions(limit=limit)
    else:
        questions = get_questions_for_skill(skill, category or None, difficulty or None, limit)
    return {"questions": questions}


@app.get("/api/v1/interview/{interview_id}")
def interview_result(interview_id: str):
    result = get_interview_result(USER_ID, interview_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Interview not found")
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
