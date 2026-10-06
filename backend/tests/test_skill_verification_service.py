import sys
import os
import json
import shutil
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app.skill_verification_service as svc

TEST_DATA_DIR = None


def _setup():
    global TEST_DATA_DIR
    TEST_DATA_DIR = tempfile.mkdtemp(prefix="skill_verification_test_")
    data_dir = os.path.join(TEST_DATA_DIR, "data")
    user_data_dir = os.path.join(data_dir, "user_data")
    os.makedirs(user_data_dir, exist_ok=True)

    svc.DATA_DIR = user_data_dir
    svc.DATA_FILE = os.path.join(user_data_dir, "skill_verification.json")


def _teardown():
    global TEST_DATA_DIR
    if TEST_DATA_DIR and os.path.exists(TEST_DATA_DIR):
        shutil.rmtree(TEST_DATA_DIR, ignore_errors=True)
        TEST_DATA_DIR = None


def test_get_verification_status_new_user():
    _setup()
    try:
        status = svc.get_verification_status(user_id="new-user")
        assert status["skills"] == {}
        assert status["summary"]["total_detected"] == 0
        assert status["summary"]["total_verified"] == 0
        assert status["summary"]["avg_score"] == 0
        assert status["summary"]["verification_rate"] == 0
    finally:
        _teardown()


def test_update_from_assessment_verified():
    _setup()
    try:
        entry = svc.update_from_assessment("u1", "Python", 85)
        assert entry["status"] == "verified"
        assert entry["score"] == 85
        assert entry["best_score"] == 85
        assert entry["assessments_taken"] == 1
        assert entry["last_assessed"] is not None
    finally:
        _teardown()


def test_update_from_assessment_verified_exact_threshold():
    _setup()
    try:
        entry = svc.update_from_assessment("u1", "Python", 70)
        assert entry["status"] == "verified"
    finally:
        _teardown()


def test_update_from_assessment_needs_review():
    _setup()
    try:
        entry = svc.update_from_assessment("u1", "Python", 69)
        assert entry["status"] == "needs_review"
        assert entry["score"] == 69
    finally:
        _teardown()


def test_update_from_assessment_needs_review_zero():
    _setup()
    try:
        entry = svc.update_from_assessment("u1", "Python", 0)
        assert entry["status"] == "needs_review"
    finally:
        _teardown()


def test_update_from_assessment_tracks_best_score():
    _setup()
    try:
        svc.update_from_assessment("u1", "Python", 50)
        entry = svc.update_from_assessment("u1", "Python", 80)
        assert entry["best_score"] == 80
        assert entry["assessments_taken"] == 2

        entry = svc.update_from_assessment("u1", "Python", 60)
        assert entry["best_score"] == 80
        assert entry["assessments_taken"] == 3
    finally:
        _teardown()


def test_sync_detected_skills_adds_new():
    _setup()
    try:
        result = svc.sync_detected_skills("u1", ["Python", "React", "Docker"])
        assert "Python" in result["skills"]
        assert "React" in result["skills"]
        assert "Docker" in result["skills"]
        for skill in ["Python", "React", "Docker"]:
            assert result["skills"][skill]["status"] == "detected"
            assert result["skills"][skill]["score"] is None
            assert result["skills"][skill]["assessments_taken"] == 0
    finally:
        _teardown()


def test_sync_detected_skills_preserves_existing():
    _setup()
    try:
        svc.update_from_assessment("u1", "Python", 85)
        result = svc.sync_detected_skills("u1", ["Python", "React"])
        assert result["skills"]["Python"]["status"] == "verified"
        assert result["skills"]["Python"]["score"] == 85
        assert result["skills"]["React"]["status"] == "detected"
        assert result["skills"]["React"]["score"] is None
    finally:
        _teardown()


def test_sync_detected_skills_empty_list():
    _setup()
    try:
        svc.update_from_assessment("u1", "Python", 85)
        result = svc.sync_detected_skills("u1", [])
        assert len(result["skills"]) == 1
        assert "Python" in result["skills"]
    finally:
        _teardown()


def test_get_verification_summary():
    _setup()
    try:
        svc.update_from_assessment("u1", "Python", 85)
        svc.update_from_assessment("u1", "React", 50)
        svc.sync_detected_skills("u1", ["Docker"])

        summary = svc.get_verification_summary("u1")
        assert summary["total_detected"] == 1
        assert summary["total_verified"] == 1
        assert summary["avg_score"] == 67.5
        assert summary["verification_rate"] == 0.5
    finally:
        _teardown()


def test_get_verification_summary_empty():
    _setup()
    try:
        summary = svc.get_verification_summary("u1")
        assert summary["total_detected"] == 0
        assert summary["total_verified"] == 0
        assert summary["avg_score"] == 0
        assert summary["verification_rate"] == 0
    finally:
        _teardown()


def test_get_skill_details_exists():
    _setup()
    try:
        svc.update_from_assessment("u1", "Python", 85)
        details = svc.get_skill_details("u1", "Python")
        assert details is not None
        assert details["status"] == "verified"
        assert details["score"] == 85
        assert details["best_score"] == 85
        assert details["assessments_taken"] == 1
    finally:
        _teardown()


def test_get_skill_details_not_found():
    _setup()
    try:
        details = svc.get_skill_details("u1", "Nonexistent")
        assert details is None
    finally:
        _teardown()


def test_get_skill_details_after_multiple_assessments():
    _setup()
    try:
        svc.update_from_assessment("u1", "Python", 40)
        svc.update_from_assessment("u1", "Python", 75)
        details = svc.get_skill_details("u1", "Python")
        assert details["status"] == "verified"
        assert details["score"] == 75
        assert details["best_score"] == 75
        assert details["assessments_taken"] == 2
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
        print("All skill verification service tests passed!")
    else:
        sys.exit(1)
