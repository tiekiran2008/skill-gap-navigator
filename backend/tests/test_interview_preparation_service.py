import sys
import os
import json
import shutil
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

TEST_DATA_DIR = None
SAMPLE_QUESTIONS = {
    "technical": {
        "Python": [
            {"id": "t1", "skill": "Python", "category": "Fundamentals", "difficulty": "Beginner",
             "question": "Explain list comprehensions.", "expected_concepts": ["iterable", "expression", "for loop"]},
            {"id": "t2", "skill": "Python", "category": "Data Structures", "difficulty": "Intermediate",
             "question": "What is a decorator?", "expected_concepts": ["function wrapper", "higher order", "@syntax"]},
        ],
        "JavaScript": [
            {"id": "t3", "skill": "JavaScript", "category": "Fundamentals", "difficulty": "Beginner",
             "question": "What is closure?", "expected_concepts": ["lexical scope", "outer function", "inner function"]},
        ],
    },
    "behavioral": [
        {"id": "b1", "area": "leadership", "question": "Tell me about a time you led a team.",
         "expected_concepts": ["leadership", "team", "outcome"]},
        {"id": "b2", "area": "teamwork", "question": "Describe a collaboration experience.",
         "expected_concepts": ["collaboration", "communication", "result"]},
        {"id": "b3", "area": "problem_solving", "question": "How did you solve a difficult problem?",
         "expected_concepts": ["problem", "approach", "solution"]},
    ],
    "project_based": [
        {"id": "p1", "question": "Walk me through your project using FastAPI.",
         "technologies": ["FastAPI", "Python"], "expected_concepts": ["API", "endpoint", "middleware"]},
        {"id": "p2", "question": "How did you deploy with Docker?",
         "technologies": ["Docker"], "expected_concepts": ["container", "image", "dockerfile"]},
    ],
}

MOCK_VERIFICATION_STATUS = {
    "skills": {
        "Python": {"status": "verified", "score": 85, "best_score": 85, "assessments_taken": 1},
        "JavaScript": {"status": "detected", "score": None, "best_score": 0, "assessments_taken": 0},
    },
    "summary": {"total_detected": 1, "total_verified": 1, "avg_score": 85, "verification_rate": 0.5},
}

MOCK_ROLE_SKILLS = [
    {"name": "Python", "demand": "high"},
    {"name": "Machine Learning", "demand": "high"},
    {"name": "Docker", "demand": "medium"},
]

MOCK_USER_SKILLS = [
    {"name": "Python", "proficiency": "advanced"},
    {"name": "JavaScript", "proficiency": "beginner"},
]

MOCK_PROJECTS = [
    {"name": "Churn Predictor", "technologies": ["Python", "Scikit-learn"]},
    {"name": "Chatbot", "technologies": ["Python", "Docker"]},
]


def _setup():
    global TEST_DATA_DIR
    TEST_DATA_DIR = tempfile.mkdtemp(prefix="interview_prep_test_")
    data_dir = os.path.join(TEST_DATA_DIR, "data")
    user_data_dir = os.path.join(data_dir, "user_data")
    os.makedirs(user_data_dir, exist_ok=True)

    questions_path = os.path.join(data_dir, "interview_questions.json")
    with open(questions_path, "w", encoding="utf-8") as f:
        json.dump(SAMPLE_QUESTIONS, f)

    import app.interview_preparation_service as svc
    svc.QUESTIONS_PATH = questions_path
    return svc


def _teardown():
    global TEST_DATA_DIR
    if TEST_DATA_DIR and os.path.exists(TEST_DATA_DIR):
        shutil.rmtree(TEST_DATA_DIR, ignore_errors=True)
        TEST_DATA_DIR = None


def test_generate_interview_plan_with_valid_role():
    svc = _setup()
    try:
        with patch.object(svc, "get_verification_status", return_value=MOCK_VERIFICATION_STATUS), \
             patch.object(svc, "get_all_projects", return_value=MOCK_PROJECTS), \
             patch.object(svc, "get_role_skills", return_value=MOCK_ROLE_SKILLS):
            plan = svc.generate_interview_plan(
                target_role="AI/ML Engineer",
                user_skills=MOCK_USER_SKILLS,
            )
        assert isinstance(plan, dict)
        assert plan["target_role"] == "AI/ML Engineer"
        assert plan["company"] is None
        assert "technical_topics" in plan
        assert "priority_topics" in plan
        assert "project_questions" in plan
        assert "behavioral_questions" in plan
        assert "recommended_practice_order" in plan
        assert "interview_readiness" in plan
        assert isinstance(plan["technical_topics"], list)
        assert isinstance(plan["priority_topics"], list)
        assert isinstance(plan["behavioral_questions"], list)
    finally:
        _teardown()


def test_generate_interview_plan_with_company():
    svc = _setup()
    try:
        with patch.object(svc, "get_verification_status", return_value=MOCK_VERIFICATION_STATUS), \
             patch.object(svc, "get_all_projects", return_value=MOCK_PROJECTS), \
             patch.object(svc, "get_role_skills", return_value=MOCK_ROLE_SKILLS):
            plan = svc.generate_interview_plan(
                target_role="AI/ML Engineer",
                company="Google",
                user_skills=MOCK_USER_SKILLS,
            )
        assert plan["company"] == "Google"
        assert plan["target_role"] == "AI/ML Engineer"
        assert "interview_readiness" in plan
        readiness = plan["interview_readiness"]
        assert "technical_readiness" in readiness
        assert "overall_readiness" in readiness
    finally:
        _teardown()


def test_generate_interview_plan_no_role():
    svc = _setup()
    try:
        with patch.object(svc, "get_verification_status", return_value=MOCK_VERIFICATION_STATUS), \
             patch.object(svc, "get_all_projects", return_value=MOCK_PROJECTS), \
             patch.object(svc, "get_role_skills", return_value=[]):
            plan = svc.generate_interview_plan(
                target_role="Nonexistent Role",
                user_skills=MOCK_USER_SKILLS,
            )
        assert isinstance(plan, dict)
        assert plan["target_role"] == "Nonexistent Role"
        readiness = plan["interview_readiness"]
        assert readiness["technical_readiness"] == 0.0
        assert readiness["overall_readiness"] == 0.0
    finally:
        _teardown()


def test_get_questions_for_skill_returns_questions():
    svc = _setup()
    try:
        questions = svc.get_questions_for_skill("Python")
        assert isinstance(questions, list)
        assert len(questions) == 2
        for q in questions:
            assert q["skill"] == "Python"
            assert "question" in q
            assert "expected_concepts" in q
    finally:
        _teardown()


def test_get_behavioral_questions_returns_questions():
    svc = _setup()
    try:
        questions = svc.get_behavioral_questions()
        assert isinstance(questions, list)
        assert len(questions) == 3
        for q in questions:
            assert "area" in q
            assert "question" in q
    finally:
        _teardown()


def test_get_behavioral_questions_filter_by_area():
    svc = _setup()
    try:
        questions = svc.get_behavioral_questions(areas=["leadership"])
        assert len(questions) == 1
        assert questions[0]["area"] == "leadership"
    finally:
        _teardown()


def test_get_project_based_questions_with_technologies():
    svc = _setup()
    try:
        questions = svc.get_project_based_questions(["FastAPI"])
        assert isinstance(questions, list)
        assert len(questions) == 1
        assert "FastAPI" in questions[0]["technologies"]

        questions = svc.get_project_based_questions(["Docker"])
        assert len(questions) == 1

        questions = svc.get_project_based_questions(["Nonexistent"])
        assert len(questions) == 0
    finally:
        _teardown()


def test_calculate_readiness_score_all_skills_match():
    svc = _setup()
    try:
        with patch.object(svc, "get_role_skills", return_value=MOCK_ROLE_SKILLS):
            result = svc.calculate_readiness_score(
                target_role="AI/ML Engineer",
                user_skills=["Python", "Machine Learning", "Docker"],
                verification_status={
                    "Python": {"score": 90},
                    "Machine Learning": {"score": 80},
                    "Docker": {"score": 75},
                },
                projects=[{"technologies": ["Python", "Machine Learning", "Docker"]}],
            )
        assert result["technical_readiness"] == 100.0
        assert result["verified_skill_confidence"] > 0
        assert result["project_readiness"] == 100.0
        assert result["overall_readiness"] > 0
    finally:
        _teardown()


def test_calculate_readiness_score_no_skills_match():
    svc = _setup()
    try:
        with patch.object(svc, "get_role_skills", return_value=MOCK_ROLE_SKILLS):
            result = svc.calculate_readiness_score(
                target_role="AI/ML Engineer",
                user_skills=["HTML", "CSS"],
                verification_status={},
                projects=[],
            )
        assert result["technical_readiness"] == 0.0
        assert result["verified_skill_confidence"] == 0.0
        assert result["project_readiness"] == 0.0
        assert result["overall_readiness"] == 0.0
    finally:
        _teardown()


def test_calculate_readiness_score_partial_match():
    svc = _setup()
    try:
        with patch.object(svc, "get_role_skills", return_value=MOCK_ROLE_SKILLS):
            result = svc.calculate_readiness_score(
                target_role="AI/ML Engineer",
                user_skills=["Python"],
                verification_status={"Python": {"score": 85}},
                projects=[{"technologies": ["Python"]}],
            )
        assert 0 < result["technical_readiness"] < 100
        assert result["verified_skill_confidence"] == 85.0
        assert result["project_readiness"] == 100.0
        assert result["overall_readiness"] > 0
    finally:
        _teardown()


def test_calculate_readiness_score_empty_role_skills():
    svc = _setup()
    try:
        with patch.object(svc, "get_role_skills", return_value=[]):
            result = svc.calculate_readiness_score(
                target_role="Unknown Role",
                user_skills=["Python"],
                verification_status={},
                projects=[],
            )
        assert result["technical_readiness"] == 0.0
        assert result["overall_readiness"] == 0.0
    finally:
        _teardown()


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
        print("All interview preparation service tests passed!")
    else:
        sys.exit(1)
