from app.skill_matcher import load_careers, match_role_batch, calculate_overall_match, calculate_category_scores, get_priority_gaps
from app.company_service import analyze_company as analyze_company_v1
from app.recommendation_engine import recommend_careers
from app.roadmap_engine import build_roadmap
from app.skill_taxonomy_service import get_category, get_importance, get_prerequisites
from app.interview_preparation_service import generate_interview_plan
from app.mock_interview_service import list_user_interviews
import app.db_service as db


def get_user_profile(user_id: str) -> dict:
    profile = db.get_profile(user_id) or {}
    skills = db.list_user_skills(user_id)
    target = db.get_career_target(user_id)
    return {
        "full_name": profile.get("full_name", ""),
        "email": profile.get("email", ""),
        "skills": [s["skill_name"] for s in skills],
        "skill_count": len(skills),
        "target_role": target.get("target_role", "") if target else "",
    }


def get_skill_gaps(user_id: str, role: str = None) -> dict:
    skills = db.list_user_skills(user_id)
    user_skill_names = [s["skill_name"] for s in skills]

    if not user_skill_names:
        return {"error": "No skills found. Upload a resume or add skills first.", "skills": [], "target_role": role or ""}

    target = role
    if not target:
        target_obj = db.get_career_target(user_id)
        target = target_obj.get("target_role", "") if target_obj else ""

    if not target:
        return {"error": "No target role set. Set a career target first.", "skills": user_skill_names, "target_role": ""}

    careers = load_careers()
    career = None
    for c in careers:
        if c["name"].lower() == target.lower():
            career = c
            break

    if not career:
        return {"error": f"Role '{target}' not found.", "skills": user_skill_names, "target_role": target}

    matched, partial, missing = match_role_batch(user_skill_names, career)
    overall = calculate_overall_match(matched, partial, missing)
    category_scores = calculate_category_scores(matched, partial, missing)
    priority_gaps = get_priority_gaps(missing)

    return {
        "target_role": target,
        "overall_match": round(overall, 1),
        "matched_skills": [{"skill": m["skill"], "score": round(m.get("score", 0), 2), "importance": m.get("importance", "medium")} for m in matched],
        "partial_matches": [{"skill": p["skill"], "score": round(p.get("score", 0), 2)} for p in partial],
        "missing_skills": [{"skill": m["skill"], "importance": m.get("importance", "medium")} for m in missing],
        "category_scores": category_scores,
        "priority_gaps": [{"skill": g["skill"], "importance": g.get("importance", "medium")} for g in priority_gaps[:5]],
    }


def get_career_matches(user_id: str) -> dict:
    skills = db.list_user_skills(user_id)
    user_skill_names = [s["skill_name"] for s in skills]

    if not user_skill_names:
        return {"recommendations": [], "error": "No skills found."}

    target_obj = db.get_career_target(user_id)
    target_role = target_obj.get("target_role", "") if target_obj else ""

    recommendations = recommend_careers(user_skill_names, target_career=target_role, top_n=5)
    return {
        "recommendations": [
            {
                "role": r["role"],
                "score": r["score"],
                "category": r["category"],
                "skill_match": r["skill_match"],
                "missing_skills": r["missing_skills"][:5],
            }
            for r in recommendations
        ]
    }


def get_company_analysis(user_id: str, company: str = None) -> dict:
    analyses = db.list_company_analyses(user_id)
    if not analyses:
        return {"analyses": [], "error": "No company analyses found."}

    if company:
        analyses = [a for a in analyses if a.get("company", "").lower() == company.lower()]

    results = []
    for a in analyses[:3]:
        data = a.get("analysis_data", {})
        results.append({
            "company": a.get("company", ""),
            "role": a.get("role", ""),
            "match_percentage": data.get("match_percentage", 0),
            "missing_skills": data.get("missing_skills", [])[:5],
            "matched_skills": [m["skill"] for m in data.get("matched_skills", [])[:5]],
        })

    return {"analyses": results}


def get_roadmap(user_id: str) -> dict:
    roadmaps = db.list_roadmaps(user_id)
    if not roadmaps:
        return {"roadmaps": [], "error": "No roadmaps found."}

    results = []
    for r in roadmaps[:3]:
        data = r.get("roadmap_data", {})
        skills = data.get("skills", [])
        progress = db.list_roadmap_progress(user_id, r["id"])
        completed = sum(1 for p in progress if p.get("status") == "Completed")
        learning = sum(1 for p in progress if p.get("status") == "Learning")

        results.append({
            "id": r["id"],
            "target_role": r.get("target_role", ""),
            "total_skills": len(skills),
            "completed": completed,
            "learning": learning,
            "remaining": len(skills) - completed - learning,
        })

    return {"roadmaps": results}


def get_progress(user_id: str) -> dict:
    roadmaps = db.list_roadmaps(user_id)
    if not roadmaps:
        return {"total_completed": 0, "total_learning": 0, "total_remaining": 0, "roadmaps": []}

    total_completed = 0
    total_learning = 0
    total_remaining = 0
    roadmap_details = []

    for r in roadmaps[:5]:
        data = r.get("roadmap_data", {})
        skills = data.get("skills", [])
        progress = db.list_roadmap_progress(user_id, r["id"])
        completed = sum(1 for p in progress if p.get("status") == "Completed")
        learning = sum(1 for p in progress if p.get("status") == "Learning")
        remaining = len(skills) - completed - learning

        total_completed += completed
        total_learning += learning
        total_remaining += remaining

        roadmap_details.append({
            "target_role": r.get("target_role", ""),
            "completed": completed,
            "learning": learning,
            "remaining": remaining,
        })

    return {
        "total_completed": total_completed,
        "total_learning": total_learning,
        "total_remaining": total_remaining,
        "roadmaps": roadmap_details,
    }


TOOLS = {
    "get_user_profile": {
        "function": get_user_profile,
        "description": "Get the user's profile, skills, and target role.",
        "parameters": {},
    },
    "get_skill_gaps": {
        "function": get_skill_gaps,
        "description": "Analyze skill gaps for a target role. Shows matched, partial, and missing skills with importance levels.",
        "parameters": {"role": {"type": "string", "description": "Target career role. Uses user's saved target if not specified.", "required": False}},
    },
    "get_career_matches": {
        "function": get_career_matches,
        "description": "Get top career recommendations based on user's skills.",
        "parameters": {},
    },
    "get_company_analysis": {
        "function": get_company_analysis,
        "description": "Get company-specific analysis results. Shows match percentage and skill alignment.",
        "parameters": {"company": {"type": "string", "description": "Filter by company name. Returns all if not specified.", "required": False}},
    },
    "get_roadmap": {
        "function": get_roadmap,
        "description": "Get learning roadmaps and their progress.",
        "parameters": {},
    },
    "get_progress": {
        "function": get_progress,
        "description": "Get overall learning progress across all roadmaps.",
        "parameters": {},
    },
    "get_interview_plan": {
        "function": lambda user_id, **kwargs: _get_interview_plan(user_id, **kwargs),
        "description": "Get personalized interview preparation plan. Shows priority topics, readiness scores, and practice recommendations.",
        "parameters": {"company": {"type": "string", "description": "Optional company name for company-specific preparation.", "required": False}},
    },
    "get_interview_history": {
        "function": lambda user_id, **kwargs: _get_interview_history(user_id),
        "description": "Get history of mock interview attempts with scores and weak areas.",
        "parameters": {},
    },
}


def _get_interview_plan(user_id: str, company: str = None) -> dict:
    skills = db.list_user_skills(user_id)
    user_skill_names = [s["skill_name"] for s in skills]
    target = db.get_career_target(user_id)
    target_role = target.get("target_role", "") if target else ""
    if not target_role:
        return {"error": "No target role set. Set a career target first.", "target_role": ""}
    plan = generate_interview_plan(target_role, company, user_skill_names)
    return plan


def _get_interview_history(user_id: str) -> dict:
    interviews = list_user_interviews(user_id)
    return {"interviews": interviews[:5], "total": len(interviews)}


def execute_tool(tool_name: str, user_id: str, parameters: dict = None) -> dict:
    if tool_name not in TOOLS:
        return {"error": f"Unknown tool: {tool_name}"}

    tool = TOOLS[tool_name]
    fn = tool["function"]

    try:
        if tool_name == "get_user_profile":
            return fn(user_id)
        elif tool_name == "get_skill_gaps":
            return fn(user_id, role=parameters.get("role") if parameters else None)
        elif tool_name == "get_career_matches":
            return fn(user_id)
        elif tool_name == "get_company_analysis":
            return fn(user_id, company=parameters.get("company") if parameters else None)
        elif tool_name == "get_roadmap":
            return fn(user_id)
        elif tool_name == "get_progress":
            return fn(user_id)
        elif tool_name == "get_interview_plan":
            return fn(user_id, company=parameters.get("company") if parameters else None)
        elif tool_name == "get_interview_history":
            return fn(user_id)
        else:
            return {"error": f"Tool {tool_name} not implemented"}
    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}"}
