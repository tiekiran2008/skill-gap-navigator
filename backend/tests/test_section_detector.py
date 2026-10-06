import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.resume_section_detector import (
    detect_sections,
    extract_contact_info,
    extract_name_from_text,
    _match_section_header,
)


def test_match_section_header():
    assert _match_section_header("Skills") == "skills"
    assert _match_section_header("TECHNICAL SKILLS") == "skills"
    assert _match_section_header("Education") == "education"
    assert _match_section_header("Work Experience") == "experience"
    assert _match_section_header("Projects") == "projects"
    assert _match_section_header("Certifications") == "certifications"
    assert _match_section_header("Summary") == "summary"
    assert _match_section_header("Contact Info") == "contact"
    assert _match_section_header("Internships") == "internship"
    assert _match_section_header("Random text here") is None


def test_detect_sections():
    text_lines = [
        "John Doe",
        "Skills",
        "Python, JavaScript, React",
        "Education",
        "B.S. Computer Science, MIT 2020",
        "Experience",
        "Software Engineer at Google",
    ]
    sections = detect_sections(text_lines)
    assert "skills" in sections
    assert "Python, JavaScript, React" in sections["skills"]
    assert "education" in sections
    assert "B.S. Computer Science, MIT 2020" in sections["education"]
    assert "experience" in sections
    assert "Software Engineer at Google" in sections["experience"]


def test_extract_contact_info_email():
    sections = {"contact": "john.doe@email.com"}
    info = extract_contact_info(sections)
    assert info.get("email") == "john.doe@email.com"


def test_extract_contact_info_phone():
    sections = {"contact": "+1 555-123-4567"}
    info = extract_contact_info(sections)
    assert "phone" in info
    assert "555" in info["phone"]


def test_extract_contact_info_linkedin():
    sections = {"contact": "linkedin.com/in/johndoe"}
    info = extract_contact_info(sections)
    assert "linkedin" in info
    assert "johndoe" in info["linkedin"]


def test_extract_contact_info_github():
    sections = {"contact": "github.com/johndoe"}
    info = extract_contact_info(sections)
    assert "github" in info
    assert "johndoe" in info["github"]


def test_extract_name_from_text():
    text = "John Doe\njohn@email.com\n+1 555-123-4567"
    name = extract_name_from_text(text)
    assert name == "John Doe"


def test_extract_name_simple():
    text = "Jane Smith\nSkills: Python, Java"
    name = extract_name_from_text(text)
    assert name == "Jane Smith"


def test_detect_sections_empty():
    sections = detect_sections([])
    assert sections == {}


def test_detect_sections_no_sections():
    lines = ["Just some random text", "More text here"]
    sections = detect_sections(lines)
    assert len(sections) == 0


if __name__ == "__main__":
    test_match_section_header()
    test_detect_sections()
    test_extract_contact_info_email()
    test_extract_contact_info_phone()
    test_extract_contact_info_linkedin()
    test_extract_contact_info_github()
    test_extract_name_from_text()
    test_extract_name_simple()
    test_detect_sections_empty()
    test_detect_sections_no_sections()
    print("All section detector tests passed!")
