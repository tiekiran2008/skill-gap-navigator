import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import fitz
from app.resume_parser import parse_resume, parse_resume_structured


SAMPLE_RESUME = """Sarah Johnson
sarah.johnson@email.com
+1 555-987-6543
linkedin.com/in/sarahjohnson
github.com/sarahj

Summary
Experienced software engineer with 5+ years in full-stack development and machine learning.

Skills
Python, JavaScript, TypeScript
React, Node.js, Django
PostgreSQL, MongoDB, Redis
Docker, Kubernetes, AWS, Git
TensorFlow, PyTorch
Machine Learning, Deep Learning, NLP
CI/CD, REST API, GraphQL

Education
M.S. Computer Science - Stanford University 2018-2020
B.S. Computer Science - UC Berkeley 2014-2018

Experience
Senior Software Engineer - Google 2022-Present
Built scalable microservices serving millions of users
Led migration from monolith to microservices architecture
Implemented ML pipeline for recommendation system

Software Engineer - Meta 2020-2022
Developed React-based frontend for Instagram features
Built REST APIs using Python and Django
Deployed applications using Docker and Kubernetes on AWS

Internships
ML Intern - OpenAI 2019-Summer
Worked on NLP models for text classification
Fine-tuned transformers for domain-specific tasks

Projects
Real-time Chat Application
Technologies: React, Node.js, WebSocket, Redis, Docker
Built a real-time messaging platform supporting 10K concurrent users

Sentiment Analysis Pipeline
Technologies: Python, TensorFlow, Hugging Face, FastAPI, AWS
Developed an end-to-end sentiment analysis system for social media

Certifications
AWS Solutions Architect - Amazon 2023
TensorFlow Developer Certificate - Google 2021
"""


def create_test_pdf(text, path):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text, fontsize=7)
    doc.save(path)
    doc.close()


def test_parse_resume_raw():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        path = f.name
    try:
        create_test_pdf(SAMPLE_RESUME, path)
        text = parse_resume(path)
        assert len(text) > 0
        assert "Sarah Johnson" in text
        assert "Python" in text
    finally:
        os.remove(path)


def test_parse_resume_structured():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        path = f.name
    try:
        create_test_pdf(SAMPLE_RESUME, path)
        profile = parse_resume_structured(path)

        assert profile["name"] == "Sarah Johnson"
        assert profile["email"] == "sarah.johnson@email.com"
        assert profile["phone"] != ""

        assert len(profile["skills"]) > 0
        assert "Python" in profile["skills"]
        assert "React" in profile["skills"]
        assert "Docker" in profile["skills"]

        assert "Python" in profile["programming_languages"]
        assert "JavaScript" in profile["programming_languages"]
        assert "TypeScript" in profile["programming_languages"]

        assert "React" in profile["frameworks"]
        assert "Django" in profile["frameworks"]
        assert "TensorFlow" in profile["frameworks"]

        assert "PostgreSQL" in profile["databases"]
        assert "MongoDB" in profile["databases"]
        assert "Redis" in profile["databases"]

        assert "AWS" in profile["cloud_tools"]
        assert "Docker" in profile["cloud_tools"]
        assert "Kubernetes" in profile["cloud_tools"]

        assert "Machine Learning" in profile["ai_ml_skills"]
        assert "Deep Learning" in profile["ai_ml_skills"]
        assert "NLP" in profile["ai_ml_skills"]

        assert len(profile["education"]) >= 1
        assert len(profile["experience"]) >= 1
        assert len(profile["internships"]) >= 1
        assert len(profile["projects"]) >= 1
        assert len(profile["certifications"]) >= 1

        assert len(profile["skills_metadata"]) > 0
        for s in profile["skills_metadata"]:
            assert "skill" in s
            assert "category" in s
            assert "confidence" in s
            assert "source" in s
            assert 0 < s["confidence"] <= 1.0

    finally:
        os.remove(path)


def test_structured_profile_has_all_fields():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        path = f.name
    try:
        create_test_pdf(SAMPLE_RESUME, path)
        profile = parse_resume_structured(path)

        required_fields = [
            "name", "email", "phone", "education", "skills",
            "programming_languages", "frameworks", "databases",
            "cloud_tools", "ai_ml_skills", "projects", "certifications",
            "experience", "internships", "skills_metadata", "sections_detected",
        ]
        for field in required_fields:
            assert field in profile, f"Missing field: {field}"

    finally:
        os.remove(path)


if __name__ == "__main__":
    test_parse_resume_raw()
    print("PASS: test_parse_resume_raw")
    test_parse_resume_structured()
    print("PASS: test_parse_resume_structured")
    test_structured_profile_has_all_fields()
    print("PASS: test_structured_profile_has_all_fields")
    print("All integration tests passed!")
