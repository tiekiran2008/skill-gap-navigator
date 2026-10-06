SCORE_WEIGHTS = {
    "skill_match": 0.50,
    "project_relevance": 0.15,
    "experience_relevance": 0.15,
    "education_relevance": 0.10,
    "career_preference": 0.10,
}

CATEGORY_THRESHOLDS = {
    "best_fit": 75,
    "close_match": 50,
    "long_term_goal": 0,
}

SKILL_MATCH_SIGNALS = {
    "exact_weight": 1.0,
    "alias_weight": 0.98,
    "semantic_weight": 0.7,
    "critical_bonus": 0.1,
}

PROJECT_KEYWORDS = {
    "ai_ml": ["machine learning", "deep learning", "nlp", "neural", "model", "tensorflow", "pytorch", "ai", "ml"],
    "data": ["data", "analytics", "visualization", "dashboard", "etl", "pipeline", "sql", "pandas"],
    "web": ["web", "frontend", "backend", "api", "react", "node", "django", "fastapi", "flask"],
    "mobile": ["mobile", "android", "ios", "flutter", "react native"],
    "cloud": ["cloud", "aws", "azure", "gcp", "docker", "kubernetes", "devops"],
    "database": ["database", "sql", "nosql", "mongodb", "postgresql", "redis"],
}

EDUCATION_KEYWORDS = {
    "cs": ["computer science", "computer engineering", "software engineering", "information technology"],
    "data": ["data science", "analytics", "statistics", "applied mathematics"],
    "ai": ["artificial intelligence", "machine learning", "deep learning"],
    "business": ["mba", "business administration", "management"],
}

EXPERIENCE_KEYWORDS = {
    "ai_ml": ["machine learning", "deep learning", "nlp", "ai", "ml engineer", "data scientist"],
    "backend": ["backend", "server", "api", "microservice", "distributed"],
    "frontend": ["frontend", "front-end", "ui", "ux", "react", "vue", "angular"],
    "data": ["data engineer", "data analyst", "etl", "pipeline", "analytics"],
    "fullstack": ["full stack", "full-stack", "fullstack"],
}


def get_weights():
    return SCORE_WEIGHTS.copy()


def set_weights(**kwargs):
    for key, value in kwargs.items():
        if key in SCORE_WEIGHTS:
            SCORE_WEIGHTS[key] = value


def normalize_weights():
    total = sum(SCORE_WEIGHTS.values())
    if total > 0:
        for key in SCORE_WEIGHTS:
            SCORE_WEIGHTS[key] = round(SCORE_WEIGHTS[key] / total, 4)
