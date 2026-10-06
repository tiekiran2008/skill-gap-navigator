import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_job_market_data_loads():
    import json
    path = os.path.join(os.path.dirname(__file__), "..", "data", "job_market.json")
    assert os.path.exists(path)
    with open(path) as f:
        jobs = json.load(f)
    assert len(jobs) >= 40, f"Expected at least 40 jobs, got {len(jobs)}"


def test_job_market_records_have_required_fields():
    import json
    path = os.path.join(os.path.dirname(__file__), "..", "data", "job_market.json")
    with open(path) as f:
        jobs = json.load(f)
    required = ["company", "role", "location", "experience_level", "required_skills", "preferred_skills", "source_type"]
    for job in jobs:
        for field in required:
            assert field in job, f"Missing '{field}' in job: {job.get('role', '?')}"


def test_skill_demand_for_role():
    from app.skill_demand_analyzer import get_skill_demand_for_role
    result = get_skill_demand_for_role("AI/ML Engineer")
    assert result["role"] == "AI/ML Engineer"
    assert result["total_jobs"] > 0
    assert len(result["top_skills"]) > 0
    for s in result["top_skills"]:
        assert "skill" in s
        assert "frequency" in s
        assert "demand_percentage" in s
        assert 0 <= s["demand_percentage"] <= 100


def test_skill_demand_top_skill_is_python():
    from app.skill_demand_analyzer import get_skill_demand_for_role
    result = get_skill_demand_for_role("AI/ML Engineer")
    top = result["top_skills"][0]
    assert top["skill"] == "Python", f"Expected Python as top skill, got {top['skill']}"


def test_skill_demand_nonexistent_role():
    from app.skill_demand_analyzer import get_skill_demand_for_role
    result = get_skill_demand_for_role("Nonexistent Role")
    assert result["total_jobs"] == 0
    assert result["top_skills"] == []


def test_role_demand():
    from app.role_demand_analyzer import get_role_demand
    result = get_role_demand()
    assert result["total_jobs"] >= 40
    assert len(result["roles"]) >= 5
    for r in result["roles"]:
        assert "role" in r
        assert "openings" in r
        assert "demand_score" in r
        assert r["openings"] > 0


def test_role_demand_top_role():
    from app.role_demand_analyzer import get_role_demand
    result = get_role_demand()
    top = result["roles"][0]
    assert top["openings"] >= result["roles"][-1]["openings"]


def test_companies_list():
    from app.role_demand_analyzer import get_companies
    companies = get_companies()
    assert len(companies) >= 5
    assert "Amazon" in companies
    assert "Microsoft" in companies


def test_company_view():
    from app.role_demand_analyzer import get_roles_for_company
    result = get_roles_for_company("Amazon")
    assert result is not None
    assert result["company"] == "Amazon"
    assert result["total_openings"] > 0
    assert len(result["roles"]) > 0
    assert len(result["required_skills"]) > 0


def test_company_view_nonexistent():
    from app.role_demand_analyzer import get_roles_for_company
    result = get_roles_for_company("Nonexistent")
    assert result is None


def test_analyze_user_vs_market():
    from app.market_insight_service import analyze_user_vs_market
    result = analyze_user_vs_market(["Python", "Machine Learning", "SQL", "Docker"], "AI/ML Engineer")
    assert "market_readiness" in result
    assert "high_demand_skills_user_has" in result
    assert "high_demand_skills_missing" in result
    assert "recommended_next_skills" in result
    assert 0 <= result["market_readiness"] <= 100
    assert "Python" in result["high_demand_skills_user_has"]


def test_analyze_user_empty_skills():
    from app.market_insight_service import analyze_user_vs_market
    result = analyze_user_vs_market([], "AI/ML Engineer")
    assert result["market_readiness"] == 0
    assert len(result["high_demand_skills_user_has"]) == 0
    assert len(result["high_demand_skills_missing"]) > 0


def test_role_insight():
    from app.market_insight_service import get_role_insight
    result = get_role_insight("AI/ML Engineer", ["Python", "ML", "SQL"])
    assert result["role"] == "AI/ML Engineer"
    assert result["total_jobs"] > 0
    assert len(result["top_skills"]) > 0
    assert "user_readiness" in result
    assert "user_has" in result
    assert "user_missing" in result


def test_company_insight():
    from app.market_insight_service import get_company_insight
    result = get_company_insight("Amazon", ["Python", "ML", "SQL"])
    assert result is not None
    assert result["company"] == "Amazon"
    assert "matched_skills" in result
    assert "missing_skills" in result


def test_market_service_overview():
    from app.job_market_service import get_market_overview
    result = get_market_overview()
    assert "role_demand" in result
    assert "skill_demand" in result
    assert "companies" in result


def test_api_market_roles():
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    res = client.get("/api/v1/market/roles")
    assert res.status_code == 200
    data = res.json()
    assert "role_demand" in data
    assert "skill_demand" in data
    assert "companies" in data


def test_api_market_skills():
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    res = client.get("/api/v1/market/skills", params={"role": "AI/ML Engineer"})
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "AI/ML Engineer"
    assert len(data["top_skills"]) > 0


def test_api_market_skills_nonexistent():
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    res = client.get("/api/v1/market/skills", params={"role": "Nonexistent"})
    assert res.status_code == 404


def test_api_market_analyze_user():
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    res = client.post("/api/v1/market/analyze-user", json={"skills": ["Python", "SQL", "Docker"], "target_role": "AI/ML Engineer"})
    assert res.status_code == 200
    data = res.json()
    assert "market_readiness" in data
    assert "high_demand_skills_user_has" in data


def test_api_market_company():
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    res = client.get("/api/v1/market/company/Amazon")
    assert res.status_code == 200
    data = res.json()
    assert data["company"] == "Amazon"
    assert len(data["roles"]) > 0


def test_api_market_company_nonexistent():
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    res = client.get("/api/v1/market/company/Nonexistent")
    assert res.status_code == 404


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
