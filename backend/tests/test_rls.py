import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_db_service_save_and_load_skills():
    import app.db_service as db
    db.upsert_user_skills(skills=[
        {"skill_name": "Python", "confidence": 0.9, "source": "resume"},
        {"skill_name": "Docker", "confidence": 1.0, "source": "manual"},
    ])
    skills = db.list_user_skills()
    assert len(skills) == 2
    names = [s["skill_name"] for s in skills]
    assert "Python" in names
    assert "Docker" in names


def test_db_service_roadmap_progress():
    import app.db_service as db
    roadmap = db.create_roadmap(target_role="AI Engineer", roadmap_data={"skills": []})
    roadmap_id = roadmap["id"]
    db.upsert_roadmap_progress(roadmap_id=roadmap_id, skill_name="PyTorch", skill_status="Learning")
    progress = db.list_roadmap_progress(roadmap_id=roadmap_id)
    assert len(progress) == 1
    assert progress[0]["skill_name"] == "PyTorch"
    assert progress[0]["status"] == "Learning"


def test_db_service_chat_history():
    import app.db_service as db
    db.clear_chat_history()
    db.create_chat_message(role="user", content="Hello")
    db.create_chat_message(role="assistant", content="Hi there!")
    history = db.list_chat_history()
    assert len(history) == 2


def test_api_endpoints_no_auth_required():
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)

    endpoints = [
        ("GET", "/api/v1/user/profile", None),
        ("GET", "/api/v1/user/skills", None),
        ("POST", "/api/v1/user/skills", {"skills": []}),
        ("GET", "/api/v1/user/resumes", None),
        ("GET", "/api/v1/user/career-target", None),
        ("GET", "/api/v1/user/company-analyses", None),
        ("GET", "/api/v1/user/career-analyses", None),
        ("GET", "/api/v1/user/roadmaps", None),
        ("GET", "/api/v1/assistant/history", None),
    ]

    for method, endpoint, body in endpoints:
        if method == "GET":
            res = client.get(endpoint)
        else:
            res = client.post(endpoint, json=body or {})
        assert res.status_code != 401, f"{endpoint} should NOT require auth (got 401)"
        assert res.status_code != 403, f"{endpoint} should NOT require auth (got 403)"


def test_public_endpoints():
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)

    public = ["/health", "/careers", "/companies"]
    for endpoint in public:
        res = client.get(endpoint)
        assert res.status_code == 200, f"{endpoint} should be public, got {res.status_code}"


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
    if failed == 0:
        print("All tests passed!")
    else:
        sys.exit(1)
