from app.skill_taxonomy_service import get_category, get_importance, get_prerequisites
from app.skill_matcher import match_role, calculate_overall_match, calculate_category_scores, get_priority_gaps


def analyze_skill_gap(user_skills, role):
    matched, partial, missing = match_role(user_skills, role)
    overall = calculate_overall_match(matched, partial, missing)
    category_scores = calculate_category_scores(matched, partial, missing)
    priority_gaps = get_priority_gaps(missing)

    return {
        "overall_match": overall,
        "category_scores": category_scores,
        "matched_skills": matched,
        "partial_matches": partial,
        "missing_skills": [m["skill"] for m in missing],
        "priority_gaps": priority_gaps,
    }


def get_learning_path(priority_gaps, role):
    learning_order = role.get("learning_order", [])
    importance_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

    path = []
    for gap in priority_gaps:
        skill = gap["skill"]
        deps = get_prerequisites(skill)
        step = learning_order.index(skill) + 1 if skill in learning_order else 99
        path.append({
            "skill": skill,
            "importance": gap["importance"],
            "dependencies": deps,
            "step": step,
            "estimated_time": _estimate_time(gap["importance"]),
        })

    path.sort(key=lambda x: (x["step"], importance_order.get(x["importance"], 4)))
    return path


def get_readiness_assessment(overall_match):
    if overall_match >= 90:
        return {"level": "Job Ready", "description": "You are well-prepared for this role."}
    elif overall_match >= 75:
        return {"level": "Near Ready", "description": "You need to fill a few critical gaps."}
    elif overall_match >= 50:
        return {"level": "Developing", "description": "You have a solid foundation but need significant upskilling."}
    elif overall_match >= 25:
        return {"level": "Beginner", "description": "You need substantial learning to reach this role."}
    else:
        return {"level": "Exploring", "description": "This role requires extensive preparation from your current level."}


def generate_gap_report(user_skills, role):
    gap_analysis = analyze_skill_gap(user_skills, role)
    learning_path = get_learning_path(gap_analysis["priority_gaps"], role)
    readiness = get_readiness_assessment(gap_analysis["overall_match"])

    return {
        "overall_match": gap_analysis["overall_match"],
        "category_scores": gap_analysis["category_scores"],
        "readiness": readiness,
        "matched_skills": gap_analysis["matched_skills"],
        "partial_matches": gap_analysis["partial_matches"],
        "missing_skills": gap_analysis["missing_skills"],
        "priority_gaps": [
            {
                "skill": g["skill"],
                "importance": g["importance"],
                "weight": g["weight"],
                "category": get_category(g["skill"]),
            }
            for g in gap_analysis["priority_gaps"]
        ],
        "learning_path": learning_path,
        "total_missing": len(gap_analysis["missing_skills"]),
        "total_matched": len(gap_analysis["matched_skills"]),
        "total_partial": len(gap_analysis["partial_matches"]),
    }


def _estimate_time(importance):
    times = {"critical": "2-4 weeks", "high": "1-2 weeks", "medium": "3-5 days", "low": "1-2 days"}
    return times.get(importance, "1 week")
