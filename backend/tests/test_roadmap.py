import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.roadmap_engine import (
    topological_sort, estimate_difficulty, group_by_category,
    build_roadmap, _parse_weeks,
)
from app.skill_taxonomy_service import get_prerequisites


def test_topological_sort_prerequisites_before_dependents():
    skills = ["Deep Learning", "Machine Learning", "Python"]
    result = topological_sort(skills, set())

    idx_python = result.index("Python")
    idx_ml = result.index("Machine Learning")
    idx_dl = result.index("Deep Learning")

    assert idx_python < idx_ml, "Python must come before Machine Learning"
    assert idx_ml < idx_dl, "Machine Learning must come before Deep Learning"


def test_topological_sort_no_duplicates():
    skills = ["PyTorch", "TensorFlow", "Deep Learning", "Python"]
    result = topological_sort(skills, set())
    assert len(result) == len(set(result)), "No duplicates in sorted output"


def test_topological_sort_all_present():
    skills = ["React", "Node.js", "FastAPI"]
    result = topological_sort(skills, set())
    assert len(result) == len(skills), "All skills must be present"


def test_topological_sort_with_user_skills():
    skills = ["PyTorch", "TensorFlow"]
    user_skills = {"Python", "Deep Learning"}
    result = topological_sort(skills, user_skills)
    assert len(result) == 2


def test_topological_sort_deep_chain():
    skills = ["LSTM", "RNN", "CNN", "Neural Networks", "Deep Learning", "Machine Learning", "Python"]
    result = topological_sort(skills, set())

    assert result.index("Python") < result.index("Machine Learning")
    assert result.index("Machine Learning") < result.index("Deep Learning")
    assert result.index("Deep Learning") < result.index("Neural Networks")
    assert result.index("Neural Networks") < result.index("RNN")
    assert result.index("RNN") < result.index("LSTM")


def test_estimate_difficulty_beginner():
    assert estimate_difficulty("Python", set()) == "Beginner"
    assert estimate_difficulty("JavaScript", set()) == "Beginner"
    assert estimate_difficulty("SQL", set()) == "Beginner"


def test_estimate_difficulty_intermediate():
    assert estimate_difficulty("TypeScript", {"JavaScript"}) == "Intermediate"
    assert estimate_difficulty("React", {"JavaScript"}) == "Intermediate"


def test_estimate_difficulty_advanced():
    diff = estimate_difficulty("Deep Learning", set())
    assert diff in ("Intermediate", "Advanced"), f"Deep Learning without prereqs should be Intermediate or Advanced, got {diff}"


def test_group_by_category():
    skills = ["Python", "React", "Docker"]
    groups = group_by_category(skills)
    assert len(groups) >= 1


def test_build_roadmap_empty():
    result = build_roadmap([])
    assert result["skills"] == []
    assert result["phases"] == []
    assert result["summary"] == {}


def test_build_roadmap_with_skills():
    missing = ["Deep Learning", "PyTorch", "Python"]
    result = build_roadmap(missing, user_skills=[], target_role="ML Engineer")

    assert len(result["skills"]) == 3
    assert result["target_role"] == "ML Engineer"
    assert result["summary"]["total_skills"] == 3


def test_build_roadmap_prerequisites_ordered():
    missing = ["PyTorch", "TensorFlow", "Python", "Deep Learning", "Machine Learning"]
    result = build_roadmap(missing, user_skills=[], target_role="ML Engineer")

    skill_names = [s["skill"] for s in result["skills"]]
    idx_python = skill_names.index("Python")
    idx_ml = skill_names.index("Machine Learning")
    idx_dl = skill_names.index("Deep Learning")

    assert idx_python < idx_ml, "Python before ML"
    assert idx_ml < idx_dl, "ML before DL"


def test_build_roadmap_phases():
    missing = ["Python", "React", "Docker", "Kubernetes"]
    result = build_roadmap(missing, user_skills=[], target_role="Full Stack")

    assert len(result["phases"]) >= 1
    phase_names = [p["name"] for p in result["phases"]]
    assert "Foundation" in phase_names or "Core Skills" in phase_names


def test_build_roadmap_has_resources():
    missing = ["Python", "React"]
    result = build_roadmap(missing, user_skills=[], target_role="Frontend Dev")

    for skill in result["skills"]:
        assert "topics" in skill
        assert "project" in skill


def test_build_roadmap_summary_counts():
    missing = ["Python", "Machine Learning", "Deep Learning", "PyTorch", "NLP"]
    result = build_roadmap(missing, user_skills=[], target_role="AI Engineer")

    summary = result["summary"]
    assert summary["total_skills"] == 5
    assert summary["critical"] + summary["high"] + summary["medium"] + summary["low"] == 5


def test_parse_weeks():
    assert _parse_weeks("2-3 weeks") == 3
    assert _parse_weeks("1 week") == 1
    assert _parse_weeks("1-2 weeks") == 2
    assert _parse_weeks("3-4 weeks") == 4


def test_build_roadmap_no_duplicate_skills():
    missing = ["Python", "Machine Learning", "Deep Learning"]
    result = build_roadmap(missing, user_skills=[], target_role="ML Engineer")
    skill_names = [s["skill"] for s in result["skills"]]
    assert len(skill_names) == len(set(skill_names)), "No duplicate skills in roadmap"


def test_build_roadmap_with_user_skills():
    missing = ["PyTorch", "TensorFlow"]
    user_skills = ["Python", "Deep Learning", "Machine Learning"]
    result = build_roadmap(missing, user_skills=user_skills, target_role="Deep Learning Engineer")
    assert len(result["skills"]) == 2


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
