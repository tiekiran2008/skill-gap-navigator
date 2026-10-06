import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_projects_data_loads():
    import json
    path = os.path.join(os.path.dirname(__file__), "..", "data", "projects.json")
    assert os.path.exists(path)
    with open(path) as f:
        projects = json.load(f)
    assert len(projects) >= 25, f"Expected at least 25 projects, got {len(projects)}"


def test_projects_have_required_fields():
    import json
    path = os.path.join(os.path.dirname(__file__), "..", "data", "projects.json")
    with open(path) as f:
        projects = json.load(f)
    required = ["id", "title", "target_roles", "skills", "difficulty", "estimated_duration",
                 "description", "features", "tech_stack", "resume_value", "portfolio_value"]
    for proj in projects:
        for field in required:
            assert field in proj, f"Missing '{field}' in project: {proj.get('title', '?')}"


def test_project_recommendations_no_skills():
    from app.project_recommendation_service import recommend_projects
    result = recommend_projects()
    assert len(result) > 0
    assert all("score" in p for p in result)
    assert all("title" in p for p in result)


def test_project_recommendations_with_missing_skills():
    from app.project_recommendation_service import recommend_projects
    result = recommend_projects(
        missing_skills=["PyTorch", "Docker", "FastAPI"],
        target_role="AI/ML Engineer",
    )
    assert len(result) > 0
    top = result[0]
    assert top["score"] > 0
    assert len(top["missing_skills_covered"]) > 0 or top["score"] < 50


def test_project_recommendations_avoid_only_known_skills():
    from app.project_recommendation_service import recommend_projects
    result = recommend_projects(
        skills=["Python", "SQL"],
        missing_skills=["PyTorch", "Docker"],
        target_role="AI/ML Engineer",
    )
    top = result[0]
    assert len(top["skills_you_will_gain"]) > 0


def test_project_recommendations_sorted_by_score():
    from app.project_recommendation_service import recommend_projects
    result = recommend_projects(missing_skills=["Python", "Docker", "Kubernetes"])
    scores = [p["score"] for p in result]
    assert scores == sorted(scores, reverse=True)


def test_get_all_projects():
    from app.project_recommendation_service import get_all_projects
    projects = get_all_projects()
    assert len(projects) >= 25


def test_get_project_by_id():
    from app.project_recommendation_service import get_project_by_id
    proj = get_project_by_id("proj-001")
    assert proj is not None
    assert proj["title"] == "Customer Churn Prediction System"


def test_get_project_by_id_not_found():
    from app.project_recommendation_service import get_project_by_id
    proj = get_project_by_id("nonexistent")
    assert proj is None


def test_generate_resume_entry():
    from app.project_recommendation_service import generate_resume_entry
    result = generate_resume_entry("proj-006")
    assert result is not None
    assert "project_title" in result
    assert "resume_points" in result
    assert len(result["resume_points"]) >= 3


def test_generate_resume_entry_not_found():
    from app.project_recommendation_service import generate_resume_entry
    result = generate_resume_entry("nonexistent")
    assert result is None


def test_resume_improvement_empty_profile():
    from app.resume_improvement_service import analyze_resume
    result = analyze_resume({})
    assert result["resume_score"] == 0
    assert len(result["improvements"]) > 0


def test_resume_improvement_full_profile():
    from app.resume_improvement_service import analyze_resume
    profile = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "skills": ["Python", "Machine Learning", "SQL", "Docker", "FastAPI"],
        "projects": [
            {"name": "Churn Predictor", "description": "ML pipeline for customer churn", "technologies": ["Python", "Scikit-learn"]},
            {"name": "Chatbot", "description": "RAG-based chatbot", "technologies": ["Python", "LangChain"]},
        ],
        "experience": [{"title": "ML Engineer", "company": "TechCo"}],
        "education": [{"degree": "B.Tech CS"}],
        "certifications": [{"name": "AWS ML Specialty"}],
        "sections_detected": ["skills", "projects", "experience", "education", "certifications"],
    }
    result = analyze_resume(profile, target_role_skills=["Python", "PyTorch", "Docker"])
    assert result["resume_score"] > 0
    assert len(result["strengths"]) > 0
    assert len(result["missing_sections"]) == 0


def test_resume_improvement_no_projects():
    from app.resume_improvement_service import analyze_resume
    profile = {
        "name": "Jane",
        "email": "jane@test.com",
        "skills": ["Python"],
        "projects": [],
        "experience": [],
        "education": [{"degree": "BS"}],
        "sections_detected": ["skills", "education"],
    }
    result = analyze_resume(profile)
    assert result["score_breakdown"]["projects_relevance"]["score"] == 0


def test_resume_improvement_weak_project_description():
    from app.resume_improvement_service import analyze_resume
    profile = {
        "name": "Test",
        "skills": ["Python"],
        "projects": [{"name": "Project", "description": "short", "technologies": []}],
        "sections_detected": ["skills", "projects"],
    }
    result = analyze_resume(profile)
    assert any("Project" in s for s in result["project_improvements"])


def test_resume_improvement_missing_sections():
    from app.resume_improvement_service import analyze_resume
    profile = {
        "name": "Test",
        "skills": ["Python"],
        "sections_detected": ["skills"],
    }
    result = analyze_resume(profile)
    assert "experience" in result["missing_sections"]
    assert "projects" in result["missing_sections"]


def test_resume_improvement_target_keywords():
    from app.resume_improvement_service import analyze_resume
    profile = {
        "name": "Test",
        "skills": ["Python", "SQL"],
        "sections_detected": ["skills"],
    }
    result = analyze_resume(profile, target_role_skills=["Python", "PyTorch", "Docker"])
    assert "PyTorch" in result["target_role_keywords"]
    assert "Docker" in result["target_role_keywords"]
    assert "Python" not in result["target_role_keywords"]


def test_api_get_projects():
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    res = client.get("/api/v1/projects")
    assert res.status_code == 200
    data = res.json()
    assert len(data["projects"]) >= 25


def test_api_recommend_projects():
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    res = client.post("/api/v1/projects/recommend", json={
        "skills": ["Python"],
        "missing_skills": ["PyTorch", "Docker"],
        "target_role": "AI/ML Engineer",
    })
    assert res.status_code == 200
    data = res.json()
    assert len(data["recommended_projects"]) > 0


def test_api_resume_entry():
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    res = client.post("/api/v1/projects/resume-entry", json={"project_id": "proj-001"})
    assert res.status_code == 200
    data = res.json()
    assert "resume_points" in data


def test_api_resume_entry_not_found():
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    res = client.post("/api/v1/projects/resume-entry", json={"project_id": "nonexistent"})
    assert res.status_code == 404


def test_api_resume_improve():
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    res = client.post("/api/v1/resume/improve", json={
        "profile": {"name": "Test", "skills": ["Python"], "sections_detected": ["skills"]},
        "target_role_skills": ["Python", "PyTorch"],
    })
    assert res.status_code == 200
    data = res.json()
    assert "resume_score" in data
    assert "strengths" in data
    assert "improvements" in data


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS: {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {test.__name__} - {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
