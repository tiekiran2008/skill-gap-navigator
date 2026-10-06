import re
import fitz
from app.resume_section_detector import (
    detect_sections, extract_contact_info, extract_name_from_text, get_section_text,
)
from app.skill_extractor import extract_skills_with_metadata, categorize_skills
from app.skill_normalizer import normalize_skill_list


def parse_resume(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def parse_resume_structured(file_path):
    raw_text = parse_resume(file_path)
    cleaned_text = _clean_text(raw_text)
    lines = cleaned_text.split("\n")

    sections = detect_sections(lines)
    contact_info = extract_contact_info(sections)
    name = extract_name_from_text(raw_text)
    if not name:
        name = contact_info.pop("name", "")

    if not contact_info:
        contact_info = _extract_contact_from_full_text(cleaned_text)

    skills_text = get_section_text(sections, "skills")
    all_text_for_skills = cleaned_text
    skills_metadata = extract_skills_with_metadata(all_text_for_skills, "skills")

    if skills_text:
        section_skills = extract_skills_with_metadata(skills_text, "skills")
        seen = {s["skill"].lower() for s in skills_metadata}
        for s in section_skills:
            if s["skill"].lower() not in seen:
                skills_metadata.append(s)
                seen.add(s["skill"].lower())

    skill_names = [s["skill"] for s in skills_metadata]
    categorized = categorize_skills(skills_metadata)

    programming = categorized.get("Programming", [])
    frameworks = categorized.get("Framework", [])
    databases = categorized.get("Database", [])
    cloud_tools = categorized.get("Cloud", []) + categorized.get("DevOps", [])
    ai_ml = categorized.get("AI/ML", [])

    education = _extract_education(get_section_text(sections, "education"))
    experience = _extract_experience(get_section_text(sections, "experience"))
    internships = _extract_experience(get_section_text(sections, "internship"))
    projects = _extract_projects(get_section_text(sections, "projects"))
    certifications = _extract_certifications(get_section_text(sections, "certifications"))

    return {
        "name": name,
        "email": contact_info.get("email", ""),
        "phone": contact_info.get("phone", ""),
        "linkedin": contact_info.get("linkedin", ""),
        "github": contact_info.get("github", ""),
        "education": education,
        "skills": skill_names,
        "skills_metadata": skills_metadata,
        "programming_languages": programming,
        "frameworks": frameworks,
        "databases": databases,
        "cloud_tools": cloud_tools,
        "ai_ml_skills": ai_ml,
        "projects": projects,
        "certifications": certifications,
        "experience": experience,
        "internships": internships,
        "raw_text": cleaned_text,
        "sections_detected": list(sections.keys()),
    }


def _clean_text(text):
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\r", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            cleaned.append(stripped)
        elif cleaned and cleaned[-1] != "":
            cleaned.append("")
    return "\n".join(cleaned)


def _extract_contact_from_full_text(text):
    info = {}

    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    if email_match:
        info["email"] = email_match.group(0)

    phone_match = re.search(r"[\+]?[\d\-\(\)\s]{7,15}", text)
    if phone_match:
        phone = phone_match.group(0).strip()
        if len(re.sub(r"\D", "", phone)) >= 7:
            info["phone"] = phone

    linkedin_match = re.search(r"linkedin\.com/in/[a-zA-Z0-9_-]+", text, re.IGNORECASE)
    if linkedin_match:
        info["linkedin"] = "https://" + linkedin_match.group(0)

    github_match = re.search(r"github\.com/[a-zA-Z0-9_-]+", text, re.IGNORECASE)
    if github_match:
        info["github"] = "https://" + github_match.group(0)

    return info


def _extract_education(text):
    if not text:
        return []

    entries = []
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    degree_pattern = re.compile(
        r"(b\.?s\.?|bachelor|btech|b\.?tech|m\.?s\.?|master|mtech|m\.?tech|phd|ph\.?d|"
        r"b\.?e\.?|m\.?b\.?a|b\.?b\.?a|b\.?ca|m\.?ca|diploma|associate)",
        re.IGNORECASE,
    )
    year_pattern = re.compile(r"(20\d{2}|19\d{2})\s*[-–]\s*(20\d{2}|19\d{2}|present|current|now)", re.IGNORECASE)
    gpa_pattern = re.compile(r"(?:cgpa|gpa|percentage|marks)[\s:]*(\d+\.?\d*)", re.IGNORECASE)

    current_entry = {}
    for line in lines:
        if degree_pattern.search(line):
            if current_entry.get("degree"):
                entries.append(current_entry)
            current_entry = {"degree": line, "institution": "", "year": "", "gpa": ""}

            year_match = year_pattern.search(line)
            if year_match:
                current_entry["year"] = year_match.group(0)

            gpa_match = gpa_pattern.search(line)
            if gpa_match:
                current_entry["gpa"] = gpa_match.group(1)
        elif current_entry:
            if not current_entry.get("institution") and not degree_pattern.search(line):
                current_entry["institution"] = line
            if not current_entry.get("year"):
                year_match = year_pattern.search(line)
                if year_match:
                    current_entry["year"] = year_match.group(0)
            if not current_entry.get("gpa"):
                gpa_match = gpa_pattern.search(line)
                if gpa_match:
                    current_entry["gpa"] = gpa_match.group(1)

    if current_entry.get("degree"):
        entries.append(current_entry)

    return entries


def _extract_experience(text):
    if not text:
        return []

    entries = []
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    title_pattern = re.compile(
        r"(intern|developer|engineer|analyst|manager|lead|senior|junior|associate|"
        r"architect|consultant|researcher|scientist|coordinator|director|"
        r"full.?stack|backend|frontend|front.?end|data|ml|ai|software|"
        r"quality|devops|cloud|security|product)",
        re.IGNORECASE,
    )
    company_pattern = re.compile(
        r"(at|@|for)\s+([A-Z][A-Za-z\s&]+)",
    )
    date_pattern = re.compile(
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{4}\s*"
        r"[-–to]*\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{4}|"
        r"(20\d{2}|19\d{2})\s*[-–]\s*(20\d{2}|19\d{2}|present|current|now|summer|winter|spring|fall)",
        re.IGNORECASE,
    )

    current_entry = {}
    for line in lines:
        is_header = title_pattern.search(line) and (
            date_pattern.search(line) or company_pattern.search(line)
        )

        if is_header:
            if current_entry.get("title"):
                entries.append(current_entry)

            date_match = date_pattern.search(line)
            company_match = company_pattern.search(line)

            title = line
            if date_match:
                title = line[:date_match.start()].strip()
            if company_match:
                title = title[:company_match.start()].strip()

            current_entry = {
                "title": title.strip("•-*| ").strip(),
                "company": company_match.group(2).strip() if company_match else "",
                "date": date_match.group(0).strip() if date_match else "",
                "description": [],
            }
        elif current_entry and not current_entry.get("title"):
            current_entry["title"] = line.strip("•-*| ").strip()
        elif current_entry.get("title"):
            desc = line.strip("•-*|").strip()
            if desc:
                current_entry["description"].append(desc)

    if current_entry.get("title"):
        entries.append(current_entry)

    for entry in entries:
        entry["description"] = " ".join(entry["description"])

    return entries


def _extract_projects(text):
    if not text:
        return []

    projects = []
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    link_pattern = re.compile(r"https?://[^\s]+|github\.com/[^\s]+")
    tech_pattern = re.compile(r"(?:technologies|tech stack|built with|using)[\s:]+(.+)", re.IGNORECASE)

    current_project = {}
    for line in lines:
        if not line.startswith(("•", "-", "*", "├", "└", "|")) and not line.startswith("  "):
            if current_project.get("name"):
                projects.append(current_project)
            current_project = {"name": line.strip("•-*| ").strip(), "description": "", "technologies": [], "links": []}
        elif current_project.get("name"):
            link_match = link_pattern.search(line)
            tech_match = tech_pattern.search(line)

            if link_match:
                current_project["links"].append(link_match.group(0))
            elif tech_match:
                current_project["technologies"] = normalize_skill_list(
                    [t.strip() for t in tech_match.group(1).split(",")]
                )
            else:
                desc = line.strip("•-*|").strip()
                if desc:
                    if current_project["description"]:
                        current_project["description"] += " " + desc
                    else:
                        current_project["description"] = desc

    if current_project.get("name"):
        projects.append(current_project)

    return projects


def _extract_certifications(text):
    if not text:
        return []

    certs = []
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    issuer_pattern = re.compile(r"(?:from|by|issued by|provider)[\s:]+(.+)", re.IGNORECASE)
    date_pattern = re.compile(r"(20\d{2}|19\d{2})")

    for line in lines:
        clean = line.strip("•-*|").strip()
        if not clean:
            continue

        cert = {"name": clean, "issuer": "", "year": ""}

        issuer_match = issuer_pattern.search(clean)
        if issuer_match:
            cert["issuer"] = issuer_match.group(1).strip()
            cert["name"] = clean[:issuer_match.start()].strip()

        date_match = date_pattern.search(clean)
        if date_match:
            cert["year"] = date_match.group(1)

        if cert["name"]:
            certs.append(cert)

    return certs
