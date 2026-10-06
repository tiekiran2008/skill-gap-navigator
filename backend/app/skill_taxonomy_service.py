import json
import os

_taxonomy = None
_name_to_canonical = None
_alias_to_canonical = None
_category_cache = None


def load_taxonomy():
    global _taxonomy
    if _taxonomy is None:
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", "skill_taxonomy.json")
        with open(data_path, "r") as f:
            _taxonomy = json.load(f)["categories"]
    return _taxonomy


def _build_lookup():
    global _name_to_canonical, _alias_to_canonical, _category_cache
    if _name_to_canonical is not None:
        return

    taxonomy = load_taxonomy()
    _name_to_canonical = {}
    _alias_to_canonical = {}
    _category_cache = {}

    for category, cat_data in taxonomy.items():
        for skill_name, skill_data in cat_data["skills"].items():
            canonical = skill_name.lower()
            _name_to_canonical[canonical] = skill_name
            _category_cache[canonical] = category
            for alias in skill_data.get("aliases", []):
                _alias_to_canonical[alias.lower()] = skill_name


def resolve_skill(raw):
    _build_lookup()
    cleaned = raw.strip().lower()

    if cleaned in _name_to_canonical:
        return _name_to_canonical[cleaned], True

    if cleaned in _alias_to_canonical:
        return _alias_to_canonical[cleaned], True

    return raw.strip(), False


def get_skill_info(canonical_name):
    _build_lookup()
    taxonomy = load_taxonomy()
    lower = canonical_name.lower()
    category = _category_cache.get(lower)
    if category and category in taxonomy:
        return taxonomy[category]["skills"].get(canonical_name)
    for cat_data in taxonomy.values():
        if canonical_name in cat_data["skills"]:
            return cat_data["skills"][canonical_name]
    return None


def get_category(canonical_name):
    _build_lookup()
    lower = canonical_name.lower()
    return _category_cache.get(lower)


def get_all_skills_in_category(category):
    taxonomy = load_taxonomy()
    if category in taxonomy:
        return list(taxonomy[category]["skills"].keys())
    return []


def get_all_categories():
    taxonomy = load_taxonomy()
    return list(taxonomy.keys())


def get_importance(canonical_name):
    info = get_skill_info(canonical_name)
    if info:
        return info.get("importance", 0.5)
    return 0.5


def get_prerequisites(canonical_name):
    info = get_skill_info(canonical_name)
    if info:
        return info.get("prerequisites", [])
    return []


def get_all_canonical_names():
    _build_lookup()
    return list(_name_to_canonical.keys())
