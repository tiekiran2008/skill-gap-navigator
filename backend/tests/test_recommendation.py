import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.recommendation_engine import (
    recommend_careers,
    calculate_skill_match,
    calculate_project_relevance,
    calculate_experience_relevance,
    calculate_education_relevance,
    calculate_career_preference,
)
from app.recommendation_config import get_weights, SCORE_WEIGHTS


def test_ranking_ai_ml_skills():
    skills = ["Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "NLP", "Neural Networks", "Statistics", "Scikit-learn", "Docker", "SQL", "Git"]
    recs = recommend_careers(skills)
    assert len(recs) > 0
    assert recs[0]["role"] == "AI/ML Engineer", f"Expected AI/ML Engineer first, got {recs[0]['role']}"
    print("PASS: test_ranking_ai_ml_skills")


def test_ranking_data_skills():
    skills = ["Python", "SQL", "Pandas", "NumPy", "Statistics", "Data Visualization", "Excel", "Tableau", "Power BI", "Data Cleaning", "Git", "Communication"]
    recs = recommend_careers(skills)
    assert len(recs) > 0
    top_roles = [r["role"] for r in recs[:3]]
    assert "Data Analyst" in top_roles or "Data Scientist" in top_roles, f"Expected data role in top 3, got {top_roles}"
    print("PASS: test_ranking_data_skills")


def test_ranking_web_skills():
    skills = ["JavaScript", "React", "Node.js", "TypeScript", "HTML", "CSS", "REST API", "Git", "SQL", "PostgreSQL", "Docker", "Next.js", "Express.js", "Tailwind CSS", "Authentication", "System Design"]
    recs = recommend_careers(skills)
    assert len(recs) > 0
    top_roles = [r["role"] for r in recs[:3]]
    assert "Full Stack Developer" in top_roles, f"Expected Full Stack Developer in top 3, got {top_roles}"
    print("PASS: test_ranking_web_skills")


def test_ranking_empty_skills():
    recs = recommend_careers([])
    assert len(recs) > 0
    for rec in recs:
        assert rec["score"] >= 0
        assert rec["category"] in ("Best Fit", "Close Match", "Long-Term Goal")
    print("PASS: test_ranking_empty_skills")


def test_scores_are_sorted():
    skills = ["Python", "Java", "SQL", "Docker"]
    recs = recommend_careers(skills)
    scores = [r["score"] for r in recs]
    assert scores == sorted(scores, reverse=True), "Recommendations should be sorted by score descending"
    print("PASS: test_scores_are_sorted")


def test_all_roles_present():
    skills = ["Python"]
    recs = recommend_careers(skills)
    roles = [r["role"] for r in recs]
    expected = ["AI/ML Engineer", "Data Scientist", "Data Analyst", "Backend Developer", "Full Stack Developer", "Computer Vision Engineer"]
    for role in expected:
        assert role in roles, f"Missing role: {role}"
    print("PASS: test_all_roles_present")


def test_category_assignments():
    skills = ["Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "NLP"]
    recs = recommend_careers(skills)
    for rec in recs:
        assert "category" in rec
        assert rec["category"] in ("Best Fit", "Close Match", "Long-Term Goal")
        if rec["score"] >= 75:
            assert rec["category"] == "Best Fit"
        elif rec["score"] >= 50:
            assert rec["category"] == "Close Match"
        else:
            assert rec["category"] == "Long-Term Goal"
    print("PASS: test_category_assignments")


def test_skill_match_range():
    skills = ["Python", "SQL"]
    recs = recommend_careers(skills)
    for rec in recs:
        assert 0 <= rec["skill_match"] <= 100, f"skill_match out of range: {rec['skill_match']}"
        assert 0 <= rec["project_match"] <= 100
        assert 0 <= rec["experience_match"] <= 100
        assert 0 <= rec["education_match"] <= 100
        assert 0 <= rec["score"] <= 100
    print("PASS: test_skill_match_range")


def test_strongest_skills_present():
    skills = ["Python", "Machine Learning", "React", "Docker"]
    recs = recommend_careers(skills)
    for rec in recs:
        assert "strongest_skills" in rec
        assert isinstance(rec["strongest_skills"], list)
        if rec["skill_match"] > 0:
            assert len(rec["strongest_skills"]) > 0
    print("PASS: test_strongest_skills_present")


def test_missing_skills_present():
    skills = ["Python"]
    recs = recommend_careers(skills)
    for rec in recs:
        assert "missing_skills" in rec
        assert isinstance(rec["missing_skills"], list)
    print("PASS: test_missing_skills_present")


def test_reason_present():
    skills = ["Python", "SQL", "Docker"]
    recs = recommend_careers(skills)
    for rec in recs:
        assert "reason" in rec
        assert isinstance(rec["reason"], list)
        assert len(rec["reason"]) > 0
    print("PASS: test_reason_present")


def test_target_career_boost():
    skills = ["Python", "SQL", "Machine Learning", "Statistics"]
    recs_no_target = recommend_careers(skills, target_career=None)
    recs_with_target = recommend_careers(skills, target_career="AI/ML Engineer")

    ai_no = next(r for r in recs_no_target if r["role"] == "AI/ML Engineer")
    ai_with = next(r for r in recs_with_target if r["role"] == "AI/ML Engineer")

    assert ai_with["score"] >= ai_no["score"], "Target career should boost matching role"
    print("PASS: test_target_career_boost")


def test_project_relevance():
    projects_empty = calculate_project_relevance([], {"required_skills": ["Python", "ML"]})
    projects_relevant = calculate_project_relevance(
        [{"name": "ML Pipeline", "description": "machine learning model deployment", "technologies": ["Python", "TensorFlow"]}],
        {"required_skills": ["Python", "Machine Learning", "Deep Learning"]}
    )
    assert projects_relevant > projects_empty, "Relevant projects should score higher"
    print("PASS: test_project_relevance")


def test_experience_relevance():
    exp_empty = calculate_experience_relevance([], [], {"required_skills": ["Python"]})
    exp_relevant = calculate_experience_relevance(
        [{"title": "ML Engineer", "company": "Tech Co", "description": "built machine learning models"}],
        [],
        {"required_skills": ["Python", "Machine Learning"]}
    )
    assert exp_relevant > exp_empty, "Relevant experience should score higher"
    print("PASS: test_experience_relevance")


def test_education_relevance():
    edu_empty = calculate_education_relevance([], {"name": "AI/ML Engineer"})
    edu_relevant = calculate_education_relevance(
        [{"degree": "M.S. Computer Science", "institution": "Stanford", "year": "2020-2022"}],
        {"name": "AI/ML Engineer"}
    )
    assert edu_relevant > edu_empty, "Relevant education should score higher"
    print("PASS: test_education_relevance")


def test_configurable_weights():
    weights = get_weights()
    assert "skill_match" in weights
    assert "project_relevance" in weights
    assert "experience_relevance" in weights
    assert "education_relevance" in weights
    assert "career_preference" in weights
    total = sum(weights.values())
    assert abs(total - 1.0) < 0.01, f"Weights should sum to 1.0, got {total}"
    print("PASS: test_configurable_weights")


if __name__ == "__main__":
    test_ranking_ai_ml_skills()
    test_ranking_data_skills()
    test_ranking_web_skills()
    test_ranking_empty_skills()
    test_scores_are_sorted()
    test_all_roles_present()
    test_category_assignments()
    test_skill_match_range()
    test_strongest_skills_present()
    test_missing_skills_present()
    test_reason_present()
    test_target_career_boost()
    test_project_relevance()
    test_experience_relevance()
    test_education_relevance()
    test_configurable_weights()
    print("\nAll ranking consistency tests passed!")
