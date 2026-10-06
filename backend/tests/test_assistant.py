import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.assistant_tools import TOOLS, execute_tool, get_user_profile, get_skill_gaps, get_career_matches, get_company_analysis, get_roadmap, get_progress
from app.career_assistant_service import _classify_intent, _fallback_response, chat


def test_tools_exist():
    expected = ["get_user_profile", "get_skill_gaps", "get_career_matches", "get_company_analysis", "get_roadmap", "get_progress"]
    for name in expected:
        assert name in TOOLS, f"Missing tool: {name}"


def test_tools_have_function():
    for name, tool in TOOLS.items():
        assert "function" in tool, f"Tool {name} missing function"
        assert callable(tool["function"]), f"Tool {name} function not callable"


def test_tools_have_description():
    for name, tool in TOOLS.items():
        assert "description" in tool, f"Tool {name} missing description"
        assert len(tool["description"]) > 10, f"Tool {name} description too short"


def test_execute_unknown_tool():
    result = execute_tool("unknown_tool", "user123")
    assert "error" in result


def test_classify_intent_readiness():
    tools = _classify_intent("How ready am I for AI Engineer?")
    assert "get_skill_gaps" in tools


def test_classify_intent_learn_next():
    tools = _classify_intent("What should I learn next?")
    assert "get_skill_gaps" in tools or "get_roadmap" in tools


def test_classify_intent_biggest_improvement():
    tools = _classify_intent("Which skill gives me the biggest improvement?")
    assert "get_skill_gaps" in tools


def test_classify_intent_company():
    tools = _classify_intent("How can I improve my match for Zoho?")
    assert "get_company_analysis" in tools


def test_classify_intent_career():
    tools = _classify_intent("What careers suit me?")
    assert "get_career_matches" in tools


def test_classify_intent_progress():
    tools = _classify_intent("Show my learning progress")
    assert "get_progress" in tools


def test_classify_intent_hello():
    tools = _classify_intent("Hello!")
    assert "get_user_profile" in tools


def test_fallback_readiness():
    tool_results = {
        "get_skill_gaps": {
            "overall_match": 65.0,
            "target_role": "AI Engineer",
            "matched_skills": [{"skill": "Python", "score": 1.0, "importance": "critical"}],
            "missing_skills": [{"skill": "Deep Learning", "importance": "critical"}, {"skill": "PyTorch", "importance": "high"}],
            "priority_gaps": [{"skill": "Deep Learning", "importance": "critical"}],
        }
    }
    response = _fallback_response("How ready am I for AI Engineer?", tool_results)
    assert "65" in response
    assert "AI Engineer" in response
    assert "Deep Learning" in response


def test_fallback_learn_next():
    tool_results = {
        "get_skill_gaps": {
            "priority_gaps": [{"skill": "Docker", "importance": "high"}, {"skill": "Kubernetes", "importance": "medium"}],
        }
    }
    response = _fallback_response("What should I learn next?", tool_results)
    assert "Docker" in response


def test_fallback_biggest_improvement():
    tool_results = {
        "get_skill_gaps": {
            "priority_gaps": [{"skill": "Deep Learning", "importance": "critical"}],
            "missing_skills": [{"skill": "Deep Learning", "importance": "critical"}],
            "target_role": "ML Engineer",
        }
    }
    response = _fallback_response("Which skill gives me the biggest improvement?", tool_results)
    assert "Deep Learning" in response


def test_fallback_docker_why():
    tool_results = {}
    response = _fallback_response("Why is Docker required?", tool_results)
    assert "Docker" in response
    assert "container" in response.lower()


def test_fallback_hello():
    tool_results = {
        "get_user_profile": {"full_name": "Test User", "skill_count": 5, "target_role": "ML Engineer"},
        "get_progress": {"total_completed": 3},
    }
    response = _fallback_response("Hello!", tool_results)
    assert "Test User" in response
    assert "5" in response


def test_fallback_projects():
    tool_results = {
        "get_skill_gaps": {
            "priority_gaps": [{"skill": "FastAPI", "importance": "high"}, {"skill": "Docker", "importance": "medium"}],
        }
    }
    response = _fallback_response("What projects should I build?", tool_results)
    assert "FastAPI" in response


def test_fallback_improve_match():
    tool_results = {
        "get_company_analysis": {
            "analyses": [{"company": "Zoho", "role": "Backend Developer", "match_percentage": 55, "missing_skills": ["FastAPI", "Docker"], "matched_skills": ["Python", "SQL"]}]
        }
    }
    response = _fallback_response("How can I improve my match for Zoho?", tool_results)
    assert "Zoho" in response
    assert "FastAPI" in response


def test_chat_returns_structured_response():
    result = chat("test-user-id", "Hello!")
    assert "response" in result
    assert "relevant_skills" in result
    assert "suggested_action" in result
    assert "source" in result
    assert result["source"] in ("ai", "fallback")


def test_assistant_endpoint_works_without_auth():
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)

    res = client.post("/api/v1/assistant/chat", json={"message": "hello"})
    assert res.status_code == 200


def test_assistant_history_works_without_auth():
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)

    res = client.get("/api/v1/assistant/history")
    assert res.status_code == 200


def test_assistant_clear_works_without_auth():
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)

    res = client.delete("/api/v1/assistant/history")
    assert res.status_code == 200


def test_migration_has_chat_history_table():
    migration_path = os.path.join(os.path.dirname(__file__), "..", "migrations", "001_initial_schema.sql")
    with open(migration_path, "r") as f:
        sql = f.read()

    assert "assistant_chat_history" in sql
    assert "role TEXT NOT NULL CHECK (role IN ('user', 'assistant'))" in sql
    assert "tools_used JSONB" in sql
    assert "relevant_skills JSONB" in sql
    assert "suggested_action TEXT" in sql
    assert "source TEXT" in sql


def test_chat_history_rls():
    migration_path = os.path.join(os.path.dirname(__file__), "..", "migrations", "001_initial_schema.sql")
    with open(migration_path, "r") as f:
        sql = f.read()

    assert "assistant_chat_history" in sql
    assert sql.count("assistant_chat_history") >= 5


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
        print("All assistant tests passed!")
    else:
        sys.exit(1)
