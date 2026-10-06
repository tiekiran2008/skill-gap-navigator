import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.skill_extractor import extract_skills_with_metadata, categorize_skills


def test_extract_python():
    result = extract_skills_with_metadata("I know Python and Java")
    skills = [s["skill"] for s in result]
    assert "Python" in skills
    assert "Java" in skills


def test_extract_with_category():
    result = extract_skills_with_metadata("I use Python daily")
    py = [s for s in result if s["skill"] == "Python"]
    assert len(py) == 1
    assert py[0]["category"] == "Programming"
    assert py[0]["confidence"] > 0


def test_extract_frameworks():
    text = "Built with React, Node.js, and Django"
    result = extract_skills_with_metadata(text)
    skills = [s["skill"] for s in result]
    assert "React" in skills
    assert "Node.js" in skills
    assert "Django" in skills


def test_extract_databases():
    text = "Experience with PostgreSQL, MongoDB, and Redis"
    result = extract_skills_with_metadata(text)
    skills = [s["skill"] for s in result]
    assert "PostgreSQL" in skills
    assert "MongoDB" in skills
    assert "Redis" in skills


def test_extract_cloud():
    text = "Deployed on AWS and used Docker with Kubernetes"
    result = extract_skills_with_metadata(text)
    skills = [s["skill"] for s in result]
    assert "AWS" in skills
    assert "Docker" in skills
    assert "Kubernetes" in skills


def test_extract_aiml():
    text = "Built ML models using deep learning and NLP"
    result = extract_skills_with_metadata(text)
    skills = [s["skill"] for s in result]
    assert "Machine Learning" in skills
    assert "Deep Learning" in skills
    assert "NLP" in skills


def test_extract_aliases():
    text = "Used sklearn and tf for dl"
    result = extract_skills_with_metadata(text)
    skills = [s["skill"] for s in result]
    assert "Scikit-learn" in skills
    assert "TensorFlow" in skills
    assert "Deep Learning" in skills


def test_extract_confidence_score():
    result = extract_skills_with_metadata("Python is my primary language")
    py = [s for s in result if s["skill"] == "Python"]
    assert len(py) == 1
    assert 0 < py[0]["confidence"] <= 1.0


def test_extract_section_bonus():
    in_skills = extract_skills_with_metadata("Python", "skills")
    in_summary = extract_skills_with_metadata("Python", "summary")
    py_skills = [s for s in in_skills if s["skill"] == "Python"]
    py_summary = [s for s in in_summary if s["skill"] == "Python"]
    assert len(py_skills) == 1
    assert len(py_summary) == 1
    assert py_skills[0]["confidence"] >= py_summary[0]["confidence"]


def test_categorize_skills():
    skills = [
        {"skill": "Python", "category": "Programming", "confidence": 0.95, "source": "text"},
        {"skill": "React", "category": "Framework", "confidence": 0.90, "source": "text"},
        {"skill": "PostgreSQL", "category": "Database", "confidence": 0.85, "source": "text"},
        {"skill": "AWS", "category": "Cloud", "confidence": 0.80, "source": "text"},
        {"skill": "Machine Learning", "category": "AI/ML", "confidence": 0.90, "source": "text"},
    ]
    result = categorize_skills(skills)
    assert "Programming" in result
    assert "Framework" in result
    assert "Database" in result
    assert "Cloud" in result
    assert "AI/ML" in result
    assert "Python" in result["Programming"]
    assert "React" in result["Framework"]


def test_extract_no_matches():
    result = extract_skills_with_metadata("I like cooking and reading books")
    assert len(result) == 0


def test_extract_deduplication():
    text = "Python python PYTHON py"
    result = extract_skills_with_metadata(text)
    py_count = sum(1 for s in result if s["skill"] == "Python")
    assert py_count == 1


if __name__ == "__main__":
    test_extract_python()
    test_extract_with_category()
    test_extract_frameworks()
    test_extract_databases()
    test_extract_cloud()
    test_extract_aiml()
    test_extract_aliases()
    test_extract_confidence_score()
    test_extract_section_bonus()
    test_categorize_skills()
    test_extract_no_matches()
    test_extract_deduplication()
    print("All skill extractor tests passed!")
