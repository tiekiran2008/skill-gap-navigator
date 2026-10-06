import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.skill_taxonomy_service import resolve_skill, get_skill_info, get_category, load_taxonomy
from app.skill_matcher import match_single_skill, match_role, calculate_overall_match, calculate_category_scores, get_priority_gaps, match_role


def test_ml_vs_machine_learning():
    score, match_type = match_single_skill("ML", "Machine Learning")
    assert score >= 0.95, f"Expected >= 0.95 for ML->Machine Learning, got {score}"
    assert match_type in ("exact", "alias"), f"Expected alias match, got {match_type}"
    print("PASS: test_ml_vs_machine_learning")


def test_postgres_vs_postgresql():
    score, match_type = match_single_skill("Postgres", "PostgreSQL")
    assert score >= 0.95, f"Expected >= 0.95 for Postgres->PostgreSQL, got {score}"
    assert match_type in ("exact", "alias"), f"Expected alias match, got {match_type}"
    print("PASS: test_postgres_vs_postgresql")


def test_fastapi_semantic():
    score, match_type = match_single_skill("FastAPI", "FastAPI")
    assert score == 1.0, f"Expected 1.0 for FastAPI exact, got {score}"
    assert match_type == "exact", f"Expected exact match, got {match_type}"
    print("PASS: test_fastapi_semantic")


def test_pytorch_exact():
    score, match_type = match_single_skill("PyTorch", "PyTorch")
    assert score == 1.0, f"Expected 1.0 for PyTorch exact, got {score}"
    assert match_type == "exact", f"Expected exact, got {match_type}"
    print("PASS: test_pytorch_exact")


def test_alias_resolution():
    name, is_exact = resolve_skill("torch")
    assert name == "PyTorch", f"Expected PyTorch, got {name}"

    name, is_exact = resolve_skill("k8s")
    assert name == "Kubernetes", f"Expected Kubernetes, got {name}"

    name, is_exact = resolve_skill("sklearn")
    assert name == "Scikit-learn", f"Expected Scikit-learn, got {name}"

    name, is_exact = resolve_skill("tf")
    assert name == "TensorFlow", f"Expected TensorFlow, got {name}"

    print("PASS: test_alias_resolution")


def test_taxonomy_loads():
    taxonomy = load_taxonomy()
    assert "Programming" in taxonomy
    assert "Deep Learning" in taxonomy
    assert "AI Agents" in taxonomy
    assert len(taxonomy) >= 15
    print("PASS: test_taxonomy_loads")


def test_skill_info():
    info = get_skill_info("Python")
    assert info is not None
    assert info["importance"] == 0.95
    assert "py" in info["aliases"]

    info = get_skill_info("PostgreSQL")
    assert info is not None
    assert "postgres" in info["aliases"]
    assert info["importance"] == 0.85

    print("PASS: test_skill_info")


def test_category_lookup():
    cat = get_category("Python")
    assert cat == "Programming"

    cat = get_category("PyTorch")
    assert cat == "Deep Learning"

    cat = get_category("React")
    assert cat == "Frontend"

    cat = get_category("Kubernetes")
    assert cat == "DevOps"

    print("PASS: test_category_lookup")


def test_importance_weight():
    from app.skill_matcher import match_role

    role = {
        "required_skills": ["Python"],
        "skill_importance": {"Python": "critical"},
    }
    matched, partial, missing = match_role(["Python"], role)
    assert len(matched) == 1
    assert matched[0]["weight"] == 1.0
    assert matched[0]["weighted_score"] == 1.0

    role2 = {
        "required_skills": ["Python"],
        "skill_importance": {"Python": "low"},
    }
    matched2, partial2, missing2 = match_role(["Python"], role2)
    assert len(matched2) == 1
    assert matched2[0]["weight"] == 0.4

    print("PASS: test_importance_weight")


def test_overall_match_calculation():
    role = {
        "required_skills": ["Python", "Django", "PostgreSQL"],
        "skill_importance": {
            "Python": "critical",
            "Django": "high",
            "PostgreSQL": "medium",
        },
    }
    matched, partial, missing = match_role(["Python", "Django"], role)
    overall = calculate_overall_match(matched, partial, missing)
    assert 50 < overall < 100, f"Expected 50-100, got {overall}"

    matched_all, partial_all, missing_all = match_role(["Python", "Django", "PostgreSQL"], role)
    overall_all = calculate_overall_match(matched_all, partial_all, missing_all)
    assert overall_all >= 95, f"Expected >= 95 for full match, got {overall_all}"

    print("PASS: test_overall_match_calculation")


def test_category_scores():
    role = {
        "required_skills": ["Python", "React", "PostgreSQL"],
        "skill_importance": {
            "Python": "critical",
            "React": "high",
            "PostgreSQL": "medium",
        },
    }
    matched, partial, missing = match_role(["Python"], role)
    scores = calculate_category_scores(matched, partial, missing)
    assert "Programming" in scores
    assert scores["Programming"] == 100.0

    print("PASS: test_category_scores")


def test_priority_gaps():
    missing = [
        {"skill": "Python", "importance": "critical", "weight": 1.0, "score": 0},
        {"skill": "Excel", "importance": "low", "weight": 0.4, "score": 0},
        {"skill": "Docker", "importance": "high", "weight": 0.8, "score": 0},
    ]
    gaps = get_priority_gaps(missing, top_n=2)
    assert len(gaps) == 2
    assert gaps[0]["skill"] == "Python"
    assert gaps[1]["skill"] == "Docker"

    print("PASS: test_priority_gaps")


def test_semantic_match():
    score, match_type = match_single_skill("deep learning", "Deep Learning")
    assert score >= 0.9, f"Expected >= 0.9 for semantic match, got {score}"
    assert match_type in ("exact", "alias", "semantic"), f"Unexpected type: {match_type}"
    print("PASS: test_semantic_match")


def test_no_match():
    score, match_type = match_single_skill("Cooking", "Python")
    assert score == 0.0, f"Expected 0.0 for unrelated skill, got {score}"
    assert match_type == "none"
    print("PASS: test_no_match")


if __name__ == "__main__":
    test_ml_vs_machine_learning()
    test_postgres_vs_postgresql()
    test_fastapi_semantic()
    test_pytorch_exact()
    test_alias_resolution()
    test_taxonomy_loads()
    test_skill_info()
    test_category_lookup()
    test_importance_weight()
    test_overall_match_calculation()
    test_category_scores()
    test_priority_gaps()
    test_semantic_match()
    test_no_match()
    print("\nAll skill intelligence tests passed!")
