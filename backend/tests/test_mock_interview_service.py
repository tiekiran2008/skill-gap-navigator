import sys
import os
import json
import shutil
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

TEST_DATA_DIR = None
SAMPLE_QUESTIONS = [
    {"id": "q1", "skill": "Python", "category": "technical", "difficulty": "Medium",
     "question": "What is a closure?", "expected_concepts": ["lexical scope", "outer function", "inner function", "variable"]},
    {"id": "q2", "skill": "Python", "category": "technical", "difficulty": "Hard",
     "question": "Explain GIL in Python.", "expected_concepts": ["global interpreter lock", "thread safety", "concurrency"]},
    {"id": "q3", "skill": "JavaScript", "category": "technical", "difficulty": "Medium",
     "question": "What is event loop?", "expected_concepts": ["callback queue", "call stack", "async", "non-blocking"]},
    {"id": "q4", "skill": "General", "category": "behavioral", "difficulty": "Medium",
     "question": "Tell me about a time you led a team.", "expected_concepts": ["leadership", "team", "outcome", "decision"]},
    {"id": "q5", "skill": "General", "category": "behavioral", "difficulty": "Medium",
     "question": "Describe a conflict you resolved.", "expected_concepts": ["conflict", "communication", "resolution", "empathy"]},
    {"id": "q6", "skill": "General", "category": "project", "difficulty": "Medium",
     "question": "Walk me through a project you built.", "expected_concepts": ["architecture", "design", "testing", "deployment"]},
    {"id": "q7", "skill": "Python", "category": "technical", "difficulty": "Beginner",
     "question": "What are decorators?", "expected_concepts": ["function wrapper", "higher order", "@syntax", "decorator pattern"]},
    {"id": "q8", "skill": "JavaScript", "category": "technical", "difficulty": "Beginner",
     "question": "What is hoisting?", "expected_concepts": ["variable declaration", "function declaration", "scope", "undefined"]},
    {"id": "q9", "skill": "Python", "category": "technical", "difficulty": "Hard",
     "question": "Explain async/await in Python.", "expected_concepts": ["coroutine", "event loop", "awaitable", "concurrency"]},
    {"id": "q10", "skill": "Python", "category": "technical", "difficulty": "Medium",
     "question": "What is a metaclass?", "expected_concepts": ["type", "class creation", "__new__", "inheritance"]},
    {"id": "q11", "skill": "JavaScript", "category": "technical", "difficulty": "Hard",
     "question": "Explain prototypal inheritance.", "expected_concepts": ["prototype chain", "object delegation", "__proto__", "inheritance"]},
    {"id": "q12", "skill": "Python", "category": "technical", "difficulty": "Beginner",
     "question": "What is a generator?", "expected_concepts": ["yield", "iterator", "lazy evaluation", "sequence"]},
    {"id": "q13", "skill": "JavaScript", "category": "technical", "difficulty": "Medium",
     "question": "What is promise chaining?", "expected_concepts": ["then", "catch", "resolve", "reject"]},
    {"id": "q14", "skill": "Python", "category": "technical", "difficulty": "Hard",
     "question": "Explain memory management in Python.", "expected_concepts": ["reference counting", "garbage collector", "memory pool", "optimization"]},
    {"id": "q15", "skill": "General", "category": "behavioral", "difficulty": "Medium",
     "question": "Tell me about a time you failed.", "expected_concepts": ["failure", "learning", "growth", "reflection"]},
    {"id": "q16", "skill": "General", "category": "behavioral", "difficulty": "Medium",
     "question": "How do you handle tight deadlines?", "expected_concepts": ["prioritization", "time management", "communication", "stress"]},
    {"id": "q17", "skill": "General", "category": "behavioral", "difficulty": "Medium",
     "question": "Describe your ideal work environment.", "expected_concepts": ["culture", "collaboration", "autonomy", "growth"]},
    {"id": "q18", "skill": "General", "category": "project", "difficulty": "Medium",
     "question": "Describe a challenging bug you fixed.", "expected_concepts": ["debugging", "root cause", "testing", "prevention"]},
    {"id": "q19", "skill": "General", "category": "project", "difficulty": "Medium",
     "question": "How do you approach code reviews?", "expected_concepts": ["review", "feedback", "quality", "best practices"]},
    {"id": "q20", "skill": "General", "category": "behavioral", "difficulty": "Medium",
     "question": "How do you stay updated with technology?", "expected_concepts": ["learning", "community", "practice", "adaptation"]},
]


def _setup():
    global TEST_DATA_DIR
    TEST_DATA_DIR = tempfile.mkdtemp(prefix="mock_interview_test_")
    data_dir = os.path.join(TEST_DATA_DIR, "data")
    user_data_dir = os.path.join(data_dir, "user_data")
    os.makedirs(user_data_dir, exist_ok=True)

    questions_path = os.path.join(data_dir, "interview_questions.json")
    with open(questions_path, "w", encoding="utf-8") as f:
        json.dump(SAMPLE_QUESTIONS, f)

    import app.mock_interview_service as svc
    svc.QUESTIONS_FILE = questions_path
    svc.INTERVIEWS_FILE = os.path.join(user_data_dir, "mock_interviews.json")
    return svc


def _teardown():
    global TEST_DATA_DIR
    if TEST_DATA_DIR and os.path.exists(TEST_DATA_DIR):
        shutil.rmtree(TEST_DATA_DIR, ignore_errors=True)
        TEST_DATA_DIR = None


def test_start_interview_creates_correct_mode():
    svc = _setup()
    try:
        interview = svc.start_interview(user_id="u1", mode="quick")
        assert interview["interview_id"]
        assert interview["user_id"] == "u1"
        assert interview["mode"] == "quick"
        assert interview["status"] == "in_progress"
        assert interview["current_question_index"] == 0
        assert interview["overall_score"] is None
        assert interview["completed_at"] is None
        assert len(interview["questions"]) == 5
    finally:
        _teardown()


def test_start_interview_technical_mode():
    svc = _setup()
    try:
        interview = svc.start_interview(user_id="u1", mode="technical")
        assert interview["mode"] == "technical"
        assert len(interview["questions"]) == 10
        for q in interview["questions"]:
            assert q["category"] == "technical"
    finally:
        _teardown()


def test_start_interview_with_target_role():
    svc = _setup()
    try:
        interview = svc.start_interview(
            user_id="u1", mode="quick", target_role="Backend Developer", company="Meta"
        )
        assert interview["target_role"] == "Backend Developer"
        assert interview["company"] == "Meta"
    finally:
        _teardown()


def test_start_interview_invalid_mode():
    svc = _setup()
    try:
        try:
            svc.start_interview(user_id="u1", mode="invalid")
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "Invalid mode" in str(e)
    finally:
        _teardown()


def test_submit_answer_records():
    svc = _setup()
    try:
        interview = svc.start_interview(user_id="u1", mode="quick")
        q_id = interview["questions"][0]["id"]
        result = svc.submit_answer(
            user_id="u1",
            interview_id=interview["interview_id"],
            question_id=q_id,
            answer="A closure is a function that retains access to its lexical scope.",
        )
        assert result["success"] is True
        assert result["question_id"] == q_id
        assert result["score"] >= 0
        assert "feedback" in result
    finally:
        _teardown()


def test_submit_answer_not_found():
    svc = _setup()
    try:
        result = svc.submit_answer(
            user_id="u1", interview_id="nonexistent", question_id="q1", answer="test"
        )
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    finally:
        _teardown()


def test_submit_answer_wrong_question():
    svc = _setup()
    try:
        interview = svc.start_interview(user_id="u1", mode="quick")
        result = svc.submit_answer(
            user_id="u1",
            interview_id=interview["interview_id"],
            question_id="nonexistent_q",
            answer="test answer",
        )
        assert result["success"] is False
    finally:
        _teardown()


def test_complete_interview_calculates_scores():
    svc = _setup()
    try:
        interview = svc.start_interview(user_id="u1", mode="quick")
        for q in interview["questions"]:
            svc.submit_answer(
                user_id="u1",
                interview_id=interview["interview_id"],
                question_id=q["id"],
                answer="A closure retains access to lexical scope and outer function variables.",
            )
        result = svc.complete_interview(user_id="u1", interview_id=interview["interview_id"])
        assert result["success"] is True
        assert result["overall_score"] >= 0
        assert result["total_questions"] == 5
        assert result["answered_questions"] == 5
        assert isinstance(result["strong_areas"], list)
        assert isinstance(result["weak_areas"], list)
    finally:
        _teardown()


def test_complete_interview_already_completed():
    svc = _setup()
    try:
        interview = svc.start_interview(user_id="u1", mode="quick")
        svc.complete_interview(user_id="u1", interview_id=interview["interview_id"])
        result = svc.complete_interview(user_id="u1", interview_id=interview["interview_id"])
        assert result["success"] is False
        assert "already completed" in result["error"].lower()
    finally:
        _teardown()


def test_get_interview_result_returns_results():
    svc = _setup()
    try:
        interview = svc.start_interview(user_id="u1", mode="quick")
        svc.submit_answer(
            user_id="u1", interview_id=interview["interview_id"],
            question_id=interview["questions"][0]["id"], answer="test answer",
        )
        svc.complete_interview(user_id="u1", interview_id=interview["interview_id"])
        result = svc.get_interview_result(user_id="u1", interview_id=interview["interview_id"])
        assert result["interview_id"] == interview["interview_id"]
        assert result["status"] == "completed"
        assert result["overall_score"] is not None
    finally:
        _teardown()


def test_get_interview_result_not_completed():
    svc = _setup()
    try:
        interview = svc.start_interview(user_id="u1", mode="quick")
        result = svc.get_interview_result(user_id="u1", interview_id=interview["interview_id"])
        assert "error" in result
        assert "not been completed" in result["error"].lower()
    finally:
        _teardown()


def test_get_interview_result_not_found():
    svc = _setup()
    try:
        result = svc.get_interview_result(user_id="u1", interview_id="nonexistent")
        assert "error" in result
        assert "not found" in result["error"].lower()
    finally:
        _teardown()


def test_list_user_interviews_returns_list():
    svc = _setup()
    try:
        svc.start_interview(user_id="u1", mode="quick")
        svc.start_interview(user_id="u1", mode="technical")
        svc.start_interview(user_id="u2", mode="quick")

        u1_interviews = svc.list_user_interviews(user_id="u1")
        assert isinstance(u1_interviews, list)
        assert len(u1_interviews) == 2
        for inv in u1_interviews:
            assert "interview_id" in inv
            assert "mode" in inv
            assert "status" in inv

        u2_interviews = svc.list_user_interviews(user_id="u2")
        assert len(u2_interviews) == 1

        empty = svc.list_user_interviews(user_id="u3")
        assert len(empty) == 0
    finally:
        _teardown()


def test_list_user_interviews_includes_completed():
    svc = _setup()
    try:
        interview = svc.start_interview(user_id="u1", mode="quick")
        svc.complete_interview(user_id="u1", interview_id=interview["interview_id"])
        interviews = svc.list_user_interviews(user_id="u1")
        assert len(interviews) == 1
        assert interviews[0]["status"] == "completed"
        assert interviews[0]["overall_score"] is not None
    finally:
        _teardown()


def test_evaluate_answer_correct():
    svc = _setup()
    try:
        result = svc.evaluate_answer(
            answer="A closure is a function that remembers the variables from its lexical scope even after the outer function has returned.",
            expected_concepts=["lexical scope", "outer function", "inner function", "variable"],
        )
        assert result["score"] >= 80
        assert len(result["matched_concepts"]) >= 3
        assert "Excellent" in result["feedback"]
    finally:
        _teardown()


def test_evaluate_answer_partial():
    svc = _setup()
    try:
        result = svc.evaluate_answer(
            answer="A closure is related to scope.",
            expected_concepts=["lexical scope", "outer function", "inner function", "variable"],
        )
        assert 0 < result["score"] < 80
        assert len(result["missing_concepts"]) > 0
    finally:
        _teardown()


def test_evaluate_answer_empty():
    svc = _setup()
    try:
        result = svc.evaluate_answer(
            answer="",
            expected_concepts=["lexical scope", "outer function", "inner function"],
        )
        assert result["score"] == 0.0
        assert len(result["matched_concepts"]) == 0
        assert len(result["missing_concepts"]) == 3
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
        print("All mock interview service tests passed!")
    else:
        sys.exit(1)
