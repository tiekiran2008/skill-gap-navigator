import sys
import os
import json
import shutil
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app.assessment_service as svc


TEST_DATA_DIR = None
SAMPLE_QUESTIONS = [
    {"id": "q1", "skill": "Python", "category": "Fundamentals", "difficulty": "Beginner", "type": "mcq",
     "question": "What is 2+2?", "options": ["3", "4", "5", "6"], "correct_answer": "4", "explanation": "Math."},
    {"id": "q2", "skill": "Python", "category": "Fundamentals", "difficulty": "Beginner", "type": "mcq",
     "question": "Which keyword defines a function?", "options": ["func", "def", "function", "define"],
     "correct_answer": "def", "explanation": "Python uses def."},
    {"id": "q3", "skill": "Python", "category": "Data Structures", "difficulty": "Intermediate", "type": "mcq",
     "question": "What is a list?", "options": ["Mutable", "Immutable", "Fixed", "None"],
     "correct_answer": "Mutable", "explanation": "Lists are mutable."},
    {"id": "q4", "skill": "JavaScript", "category": "Fundamentals", "difficulty": "Beginner", "type": "mcq",
     "question": "What is typeof null?", "options": ["null", "object", "undefined", "boolean"],
     "correct_answer": "object", "explanation": "Historic JS bug."},
    {"id": "q5", "skill": "JavaScript", "category": "DOM", "difficulty": "Intermediate", "type": "mcq",
     "question": "Which method selects by ID?", "options": ["querySelector", "getElementById", "getElementsByClassName", "fetch"],
     "correct_answer": "getElementById", "explanation": "Standard DOM API."},
]


def _setup():
    global TEST_DATA_DIR
    TEST_DATA_DIR = tempfile.mkdtemp(prefix="assessment_test_")
    data_dir = os.path.join(TEST_DATA_DIR, "data")
    user_data_dir = os.path.join(data_dir, "user_data")
    os.makedirs(user_data_dir, exist_ok=True)

    questions_path = os.path.join(data_dir, "assessments.json")
    with open(questions_path, "w", encoding="utf-8") as f:
        json.dump(SAMPLE_QUESTIONS, f)

    svc.QUESTIONS_PATH = questions_path
    svc.USER_DATA_DIR = user_data_dir
    svc.USER_ASSESSMENTS_PATH = os.path.join(user_data_dir, "user_assessments.json")


def _teardown():
    global TEST_DATA_DIR
    if TEST_DATA_DIR and os.path.exists(TEST_DATA_DIR):
        shutil.rmtree(TEST_DATA_DIR, ignore_errors=True)
        TEST_DATA_DIR = None


def test_get_all_skills():
    _setup()
    try:
        skills = svc.get_all_skills()
        assert isinstance(skills, list)
        assert len(skills) == 2
        names = {s["skill"] for s in skills}
        assert "Python" in names
        assert "JavaScript" in names
        for s in skills:
            assert "skill" in s
            assert "question_count" in s
            assert "difficulties" in s
            assert "categories" in s
            assert isinstance(s["difficulties"], list)
            assert isinstance(s["categories"], list)
    finally:
        _teardown()


def test_get_questions_for_skill_valid():
    _setup()
    try:
        qs = svc.get_questions_for_skill("Python")
        assert isinstance(qs, list)
        assert len(qs) == 3
        for q in qs:
            assert q["skill"] == "Python"
    finally:
        _teardown()


def test_get_questions_for_skill_invalid():
    _setup()
    try:
        qs = svc.get_questions_for_skill("Rust")
        assert isinstance(qs, list)
        assert len(qs) == 0
    finally:
        _teardown()


def test_get_questions_for_skill_with_difficulty():
    _setup()
    try:
        qs = svc.get_questions_for_skill("Python", difficulty="Beginner")
        assert len(qs) == 2
        for q in qs:
            assert q["difficulty"] == "Beginner"
    finally:
        _teardown()


def test_get_questions_for_skill_limit():
    _setup()
    try:
        qs = svc.get_questions_for_skill("Python", limit=1)
        assert len(qs) == 1
    finally:
        _teardown()


def test_start_assessment_creates_correct_fields():
    _setup()
    try:
        a = svc.start_assessment(user_id="test-user", skill="Python", difficulty="Beginner", question_count=2)
        assert a["assessment_id"]
        assert a["user_id"] == "test-user"
        assert a["skill"] == "Python"
        assert a["difficulty"] == "Beginner"
        assert a["question_count"] == 2
        assert len(a["questions"]) == 2
        assert a["answers"] == {}
        assert a["status"] == "in_progress"
        assert a["score"] is None
        assert a["total_correct"] is None
        assert a["total_questions"] == 2
        assert a["completed_at"] is None
        assert a["created_at"]
    finally:
        _teardown()


def test_start_assessment_invalid_skill_raises():
    _setup()
    try:
        try:
            svc.start_assessment(user_id="u1", skill="Nonexistent")
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "No questions found" in str(e)
    finally:
        _teardown()


def test_start_assessment_persists():
    _setup()
    try:
        a = svc.start_assessment(user_id="u1", skill="Python", question_count=2)
        loaded = svc._load_user_assessments()
        assert len(loaded) == 1
        assert loaded[0]["assessment_id"] == a["assessment_id"]
    finally:
        _teardown()


def test_submit_answer_records():
    _setup()
    try:
        a = svc.start_assessment(user_id="u1", skill="Python", question_count=2)
        qid = a["questions"][0]["question_id"]
        result = svc.submit_answer(user_id="u1", assessment_id=a["assessment_id"], question_id=qid, answer="4")
        assert result["answers"][qid] == "4"
    finally:
        _teardown()


def test_submit_answer_invalid_assessment_raises():
    _setup()
    try:
        try:
            svc.submit_answer(user_id="u1", assessment_id="bad-id", question_id="q1", answer="4")
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "not found" in str(e)
    finally:
        _teardown()


def test_submit_answer_completed_assessment_raises():
    _setup()
    try:
        a = svc.start_assessment(user_id="u1", skill="Python", question_count=1)
        svc.complete_assessment(user_id="u1", assessment_id=a["assessment_id"])
        try:
            svc.submit_answer(user_id="u1", assessment_id=a["assessment_id"], question_id="q1", answer="4")
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "not in progress" in str(e)
    finally:
        _teardown()


def test_complete_assessment_scores_correctly():
    _setup()
    try:
        a = svc.start_assessment(user_id="u1", skill="Python", question_count=2)
        for q in a["questions"]:
            svc.submit_answer(user_id="u1", assessment_id=a["assessment_id"],
                              question_id=q["question_id"], answer=str(q["correct_answer"]))
        result = svc.complete_assessment(user_id="u1", assessment_id=a["assessment_id"])
        assert result["status"] == "completed"
        assert result["total_correct"] == 2
        assert result["score"] == 100.0
        assert result["completed_at"] is not None
    finally:
        _teardown()


def test_complete_assessment_partial_score():
    _setup()
    try:
        a = svc.start_assessment(user_id="u1", skill="Python", question_count=2)
        svc.submit_answer(user_id="u1", assessment_id=a["assessment_id"],
                          question_id=a["questions"][0]["question_id"],
                          answer=str(a["questions"][0]["correct_answer"]))
        svc.submit_answer(user_id="u1", assessment_id=a["assessment_id"],
                          question_id=a["questions"][1]["question_id"], answer="wrong")
        result = svc.complete_assessment(user_id="u1", assessment_id=a["assessment_id"])
        assert result["total_correct"] == 1
        assert result["score"] == 50.0
    finally:
        _teardown()


def test_complete_assessment_no_answers():
    _setup()
    try:
        a = svc.start_assessment(user_id="u1", skill="Python", question_count=2)
        result = svc.complete_assessment(user_id="u1", assessment_id=a["assessment_id"])
        assert result["total_correct"] == 0
        assert result["score"] == 0.0
    finally:
        _teardown()


def test_complete_assessment_invalid_raises():
    _setup()
    try:
        try:
            svc.complete_assessment(user_id="u1", assessment_id="bad-id")
            assert False, "Expected ValueError"
        except ValueError:
            pass
    finally:
        _teardown()


def test_list_user_assessments():
    _setup()
    try:
        svc.start_assessment(user_id="u1", skill="Python", question_count=1)
        svc.start_assessment(user_id="u1", skill="JavaScript", question_count=1)
        svc.start_assessment(user_id="u2", skill="Python", question_count=1)

        u1 = svc.list_user_assessments(user_id="u1")
        assert len(u1) == 2
        assert all(a["user_id"] == "u1" for a in u1)

        u2 = svc.list_user_assessments(user_id="u2")
        assert len(u2) == 1

        none = svc.list_user_assessments(user_id="u3")
        assert len(none) == 0
    finally:
        _teardown()


def test_list_user_assessments_includes_completed():
    _setup()
    try:
        a = svc.start_assessment(user_id="u1", skill="Python", question_count=1)
        svc.complete_assessment(user_id="u1", assessment_id=a["assessment_id"])
        assessments = svc.list_user_assessments(user_id="u1")
        assert len(assessments) == 1
        assert assessments[0]["status"] == "completed"
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
        print("All assessment service tests passed!")
    else:
        sys.exit(1)
