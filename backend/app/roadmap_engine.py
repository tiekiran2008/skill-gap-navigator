import json
import os
from collections import defaultdict, deque
from app.skill_taxonomy_service import get_prerequisites, get_importance, get_category, resolve_skill


_resources = None


def load_resources():
    global _resources
    if _resources is None:
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", "learning_resources.json")
        with open(data_path, "r") as f:
            _resources = json.load(f)["skills"]
    return _resources


def get_resource(skill_name):
    resources = load_resources()
    canonical, _ = resolve_skill(skill_name)
    return resources.get(canonical, resources.get(skill_name, None))


DIFFICULTY_ORDER = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}


def estimate_difficulty(skill_name, user_skills_set):
    preres = get_prerequisites(skill_name)
    missing_prereqs = [p for p in preres if p.lower() not in {s.lower() for s in user_skills_set}]

    if not preres:
        return "Beginner"
    if len(missing_prereqs) <= 1:
        return "Intermediate"
    return "Advanced"


def topological_sort(skills, user_skills_set):
    skill_set = {s.lower() for s in skills}
    resolved = {}
    for s in skills:
        canonical, _ = resolve_skill(s)
        resolved[s] = canonical

    in_degree = defaultdict(int)
    graph = defaultdict(list)

    all_nodes = set(skills)
    for s in skills:
        preres = get_prerequisites(s)
        for p in preres:
            if p.lower() in skill_set:
                graph[p].append(s)
                in_degree[s] += 1

    queue = deque([s for s in skills if in_degree[s] == 0])
    sorted_skills = []

    while queue:
        current = queue.popleft()
        sorted_skills.append(current)
        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(sorted_skills) < len(skills):
        for s in skills:
            if s not in sorted_skills:
                sorted_skills.append(s)

    return sorted_skills


def group_by_category(skills):
    groups = defaultdict(list)
    for s in skills:
        cat = get_category(s) or "Other"
        groups[cat].append(s)
    return dict(groups)


def estimate_duration(skill_name, user_skills_set):
    resource = get_resource(skill_name)
    if resource and "duration" in resource:
        return resource["duration"]

    importance = get_importance(skill_name)
    if importance >= 0.9:
        return "2-3 weeks"
    if importance >= 0.7:
        return "1-2 weeks"
    return "1 week"


def build_roadmap(missing_skills, user_skills=None, target_role=None):
    if not missing_skills:
        return {"skills": [], "phases": [], "summary": {}, "target_role": target_role}

    user_skills_set = set(user_skills) if user_skills else set()
    sorted_skills = topological_sort(missing_skills, user_skills_set)

    roadmap_items = []
    for i, skill in enumerate(sorted_skills):
        canonical, _ = resolve_skill(skill)
        resource = get_resource(canonical) or get_resource(skill)

        importance = get_importance(canonical)
        difficulty = estimate_difficulty(canonical, user_skills_set)
        duration = estimate_duration(canonical, user_skills_set)
        preres = get_prerequisites(canonical)

        item = {
            "id": i + 1,
            "skill": canonical or skill,
            "importance": "critical" if importance >= 0.9 else "high" if importance >= 0.75 else "medium" if importance >= 0.6 else "low",
            "difficulty": difficulty,
            "estimated_time": duration,
            "prerequisites": [p for p in preres if p.lower() not in {s.lower() for s in user_skills_set}],
            "topics": resource.get("topics", []) if resource else [],
            "project": resource.get("project", "") if resource else "",
            "category": get_category(canonical) or "Other",
            "status": "Not Started",
        }
        roadmap_items.append(item)

    phases = _build_phases(roadmap_items)

    total_critical = sum(1 for r in roadmap_items if r["importance"] == "critical")
    total_high = sum(1 for r in roadmap_items if r["importance"] == "high")
    total_medium = sum(1 for r in roadmap_items if r["importance"] == "medium")
    total_low = sum(1 for r in roadmap_items if r["importance"] == "low")

    total_weeks = 0
    for item in roadmap_items:
        d = item["estimated_time"]
        if "week" in d:
            parts = d.replace("weeks", "week").replace("Ongoing", "1 week").split("-")
            try:
                total_weeks += int(parts[-1].strip().replace("week", "").strip())
            except (ValueError, IndexError):
                total_weeks += 2

    return {
        "skills": roadmap_items,
        "phases": phases,
        "summary": {
            "total_skills": len(roadmap_items),
            "critical": total_critical,
            "high": total_high,
            "medium": total_medium,
            "low": total_low,
            "estimated_weeks": total_weeks,
        },
        "target_role": target_role,
    }


def _build_phases(roadmap_items):
    foundation = []
    core = []
    advanced = []
    specialization = []

    for item in roadmap_items:
        if item["difficulty"] == "Beginner":
            foundation.append(item)
        elif item["difficulty"] == "Advanced":
            advanced.append(item)
        elif item["importance"] in ("critical", "high"):
            core.append(item)
        else:
            specialization.append(item)

    phases = []
    if foundation:
        phases.append({
            "phase": 1,
            "name": "Foundation",
            "description": "Build core fundamentals",
            "skills": foundation,
            "estimated_weeks": sum(_parse_weeks(s["estimated_time"]) for s in foundation),
        })
    if core:
        phases.append({
            "phase": len(phases) + 1,
            "name": "Core Skills",
            "description": "Develop essential technical skills",
            "skills": core,
            "estimated_weeks": sum(_parse_weeks(s["estimated_time"]) for s in core),
        })
    if advanced:
        phases.append({
            "phase": len(phases) + 1,
            "name": "Advanced Topics",
            "description": "Master advanced concepts and frameworks",
            "skills": advanced,
            "estimated_weeks": sum(_parse_weeks(s["estimated_time"]) for s in advanced),
        })
    if specialization:
        phases.append({
            "phase": len(phases) + 1,
            "name": "Specialization",
            "description": "Deepen expertise in specific areas",
            "skills": specialization,
            "estimated_weeks": sum(_parse_weeks(s["estimated_time"]) for s in specialization),
        })

    return phases


def _parse_weeks(duration_str):
    if "week" in duration_str:
        parts = duration_str.replace("weeks", "week").split("-")
        try:
            return int(parts[-1].strip().replace("week", "").strip())
        except (ValueError, IndexError):
            pass
    return 2
