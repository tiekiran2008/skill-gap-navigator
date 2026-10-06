import re

SECTION_PATTERNS = {
    "contact": [
        r"^\s*(contact|contact\s+info|personal\s+info|personal\s+details)\s*$",
    ],
    "summary": [
        r"^\s*(summary|profile|about\s+me|objective|career\s+objective|professional\s+summary|career\s+summary|professional\s+profile)\s*$",
    ],
    "education": [
        r"^\s*(education|academic|qualification|educational\s+background|academics)\s*$",
    ],
    "experience": [
        r"^\s*(experience|work\s+experience|employment|professional\s+experience|work\s+history|employment\s+history)\s*$",
    ],
    "internship": [
        r"^\s*(internship|internships|intern\s+experience|internship\s+experience)\s*$",
    ],
    "skills": [
        r"^\s*(skills|technical\s+skills|core\s+competencies|competencies|key\s+skills|technical\s+expertise|technologies)\s*$",
    ],
    "projects": [
        r"^\s*(projects|personal\s+projects|key\s+projects|project\s+experience|academic\s+projects)\s*$",
    ],
    "certifications": [
        r"^\s*(certifications|certificates|certification|licenses|credentials)\s*$",
    ],
    "achievements": [
        r"^\s*(achievements|accomplishments|awards|honors|recognitions)\s*$",
    ],
    "languages": [
        r"^\s*(languages|spoken\s+languages|foreign\s+languages)\s*$",
    ],
    "interests": [
        r"^\s*(interests|hobbies|extracurricular)\s*$",
    ],
}

SECTION_ORDER = [
    "contact", "summary", "skills", "education", "experience",
    "internship", "projects", "certifications", "achievements",
    "languages", "interests",
]


def detect_sections(lines):
    sections = {}
    current_section = None
    current_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_section:
                current_lines.append("")
            continue

        matched_section = _match_section_header(stripped)
        if matched_section:
            if current_section:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = matched_section
            current_lines = []
        else:
            if current_section:
                current_lines.append(stripped)

    if current_section:
        sections[current_section] = "\n".join(current_lines).strip()

    return sections


def _match_section_header(text):
    for section_name, patterns in SECTION_PATTERNS.items():
        for pattern in patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return section_name
    return None


def get_section_text(sections, section_name):
    return sections.get(section_name, "")


def extract_contact_info(sections):
    contact_text = get_section_text(sections, "contact")
    if not contact_text:
        return {}

    info = {}

    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", contact_text)
    if email_match:
        info["email"] = email_match.group(0)

    phone_match = re.search(r"[\+]?[\d\-\(\)\s]{7,15}", contact_text)
    if phone_match:
        phone = phone_match.group(0).strip()
        if len(re.sub(r"\D", "", phone)) >= 7:
            info["phone"] = phone

    linkedin_match = re.search(r"linkedin\.com/in/[a-zA-Z0-9_-]+", contact_text, re.IGNORECASE)
    if linkedin_match:
        info["linkedin"] = "https://" + linkedin_match.group(0)

    github_match = re.search(r"github\.com/[a-zA-Z0-9_-]+", contact_text, re.IGNORECASE)
    if github_match:
        info["github"] = "https://" + github_match.group(0)

    return info


def extract_name_from_text(full_text):
    lines = [l.strip() for l in full_text.split("\n") if l.strip()]
    if not lines:
        return ""

    first_line = lines[0]

    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", first_line)
    phone_match = re.search(r"[\+]?[\d\-\(\)\s]{7,15}", first_line)

    if email_match or phone_match:
        name_part = first_line
        if email_match:
            name_part = name_part[:email_match.start()]
        if phone_match:
            name_part = name_part[:phone_match.start()]
        name_part = name_part.strip().strip("|").strip("-").strip()
        if name_part and len(name_part.split()) <= 5:
            return name_part

    if len(first_line.split()) <= 5 and not any(kw in first_line.lower() for kw in SECTION_PATTERNS):
        has_upper = any(c.isupper() for c in first_line)
        has_alpha = any(c.isalpha() for c in first_line)
        if has_upper and has_alpha:
            return first_line

    return ""
