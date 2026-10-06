from app.skill_normalizer import normalize_skill_list


REQUIRED_SECTIONS = ["skills", "experience", "education", "projects"]
IMPORTANT_SECTIONS = ["certifications", "internships"]

WEIGHTS = {
    "structure": 20,
    "skills_relevance": 25,
    "projects_relevance": 25,
    "experience_relevance": 15,
    "education_certs": 15,
}


def analyze_resume(profile, target_role_skills=None):
    if not profile:
        return _empty_result()

    structure_score = _score_structure(profile)
    skills_score = _score_skills(profile, target_role_skills)
    projects_score = _score_projects(profile, target_role_skills)
    experience_score = _score_experience(profile)
    education_score = _score_education(profile)

    total = structure_score + skills_score + projects_score + experience_score + education_score

    strengths = _get_strengths(profile, structure_score, skills_score, projects_score)
    improvements = _get_improvements(profile, structure_score, skills_score, projects_score, experience_score)
    missing_sections = _get_missing_sections(profile)
    target_keywords = _get_target_keywords(target_role_skills, profile)
    project_improvements = _get_project_improvements(profile)
    skill_improvements = _get_skill_improvements(profile, target_role_skills)

    return {
        "resume_score": total,
        "score_breakdown": {
            "structure": {"score": structure_score, "max": WEIGHTS["structure"]},
            "skills_relevance": {"score": skills_score, "max": WEIGHTS["skills_relevance"]},
            "projects_relevance": {"score": projects_score, "max": WEIGHTS["projects_relevance"]},
            "experience_relevance": {"score": experience_score, "max": WEIGHTS["experience_relevance"]},
            "education_certifications": {"score": education_score, "max": WEIGHTS["education_certs"]},
        },
        "strengths": strengths,
        "improvements": improvements,
        "missing_sections": missing_sections,
        "target_role_keywords": target_keywords,
        "project_improvements": project_improvements,
        "skill_improvements": skill_improvements,
    }


def _empty_result():
    return {
        "resume_score": 0,
        "score_breakdown": {},
        "strengths": [],
        "improvements": ["No resume data found. Upload a PDF to get started."],
        "missing_sections": REQUIRED_SECTIONS[:],
        "target_role_keywords": [],
        "project_improvements": [],
        "skill_improvements": [],
    }


def _score_structure(profile):
    score = 0
    sections = profile.get("sections_detected", [])

    for section in REQUIRED_SECTIONS:
        if section in sections:
            score += WEIGHTS["structure"] / len(REQUIRED_SECTIONS)

    if profile.get("name"):
        score += 2
    if profile.get("email"):
        score += 2
    if profile.get("phone") or profile.get("linkedin") or profile.get("github"):
        score += 1

    return round(min(score, WEIGHTS["structure"]))


def _score_skills(profile, target_role_skills):
    if not target_role_skills:
        return round(WEIGHTS["skills_relevance"] * 0.5)

    user_skills = set(normalize_skill_list(profile.get("skills", [])))
    target = set(normalize_skill_list(target_role_skills))

    if not target:
        return round(WEIGHTS["skills_relevance"] * 0.5)

    overlap = user_skills & target
    return round(len(overlap) / len(target) * WEIGHTS["skills_relevance"])


def _score_projects(profile, target_role_skills):
    projects = profile.get("projects", [])
    if not projects:
        return 0

    base = min(len(projects) * 5, 15)

    if target_role_skills:
        target = set(normalize_skill_list(target_role_skills))
        project_text = " ".join(
            " ".join(p.get("technologies", []) if isinstance(p, dict) else [])
            if isinstance(p, dict) else str(p)
            for p in projects
        ).lower()
        project_skills = set(normalize_skill_list(
            [t for p in projects if isinstance(p, dict) for t in p.get("technologies", [])]
        ))
        relevance = len(project_skills & target) / len(target) if target else 0
        base += round(relevance * 10)

    return min(base, WEIGHTS["projects_relevance"])


def _score_experience(profile):
    experience = profile.get("experience", [])
    internships = profile.get("internships", [])

    if experience:
        return min(12 + len(experience) * 2, WEIGHTS["experience_relevance"])
    if internships:
        return min(8 + len(internships) * 2, WEIGHTS["experience_relevance"])
    return 3


def _score_education(profile):
    education = profile.get("education", [])
    certifications = profile.get("certifications", [])

    score = 0
    if education:
        score += 8
    if certifications:
        score += min(len(certifications) * 3, 7)

    return min(score, WEIGHTS["education_certs"])


def _get_strengths(profile, structure_score, skills_score, projects_score):
    strengths = []
    if structure_score >= 16:
        strengths.append("Well-structured resume with all key sections present")
    if profile.get("skills") and len(profile["skills"]) >= 5:
        strengths.append(f"Strong skill set with {len(profile['skills'])} skills listed")
    if profile.get("projects") and len(profile["projects"]) >= 2:
        strengths.append(f"Good project portfolio with {len(profile['projects'])} projects")
    if profile.get("experience"):
        strengths.append(f"Work experience included ({len(profile['experience'])} roles)")
    if profile.get("name") and profile.get("email"):
        strengths.append("Complete contact information")
    return strengths


def _get_improvements(profile, structure_score, skills_score, projects_score, experience_score):
    improvements = []
    if structure_score < 14:
        improvements.append("Add missing sections (skills, experience, education, projects)")
    if skills_score < 15:
        improvements.append("Add more relevant technical skills for your target role")
    if projects_score < 12:
        improvements.append("Include more projects with relevant technologies")
    if experience_score < 8:
        improvements.append("Add work experience or internship details if available")

    for proj in profile.get("projects", []):
        if isinstance(proj, dict):
            desc = proj.get("description", "")
            if len(desc) < 30:
                improvements.append(
                    f"Expand description for project '{proj.get('name', 'Unknown')}' — add specific contributions"
                )
    return improvements


def _get_missing_sections(profile):
    sections = profile.get("sections_detected", [])
    return [s for s in REQUIRED_SECTIONS if s not in sections]


def _get_target_keywords(target_role_skills, profile):
    if not target_role_skills:
        return []
    user_skills = set(normalize_skill_list(profile.get("skills", [])))
    target = set(normalize_skill_list(target_role_skills))
    missing = target - user_skills
    return sorted(missing)


def _get_project_improvements(profile):
    suggestions = []
    for proj in profile.get("projects", []):
        if isinstance(proj, dict):
            name = proj.get("name", "Unknown project")
            desc = proj.get("description", "")
            techs = proj.get("technologies", [])
            if len(desc) < 30:
                suggestions.append(f"Project '{name}': Add a more detailed description of your role and contributions")
            if not techs:
                suggestions.append(f"Project '{name}': List the technologies and tools used")
    return suggestions


def _get_skill_improvements(profile, target_role_skills):
    if not target_role_skills:
        return []
    user_skills = set(normalize_skill_list(profile.get("skills", [])))
    target = set(normalize_skill_list(target_role_skills))
    missing = sorted(target - user_skills)
    if not missing:
        return []
    return [f"Consider adding '{s}' to your skills section if you have experience with it" for s in missing[:5]]
