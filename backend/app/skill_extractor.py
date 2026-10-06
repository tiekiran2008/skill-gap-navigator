import re
from app.skill_normalizer import normalize_skill

SKILL_DICTIONARY = {
    # Programming Languages
    "python": {"category": "Programming", "aliases": ["py", "python3", "python 3"]},
    "java": {"category": "Programming", "aliases": ["java8", "java 8", "java11", "java 11", "java17", "java 17"]},
    "javascript": {"category": "Programming", "aliases": ["js", "es6", "es2015", "ecmascript"]},
    "typescript": {"category": "Programming", "aliases": ["ts"]},
    "c++": {"category": "Programming", "aliases": ["cpp", "cplusplus", "c plus plus"]},
    "c": {"category": "Programming", "aliases": ["c lang", "ansi c"]},
    "c#": {"category": "Programming", "aliases": ["csharp", "c sharp", ".net"]},
    "go": {"category": "Programming", "aliases": ["golang"]},
    "rust": {"category": "Programming", "aliases": ["rs"]},
    "ruby": {"category": "Programming", "aliases": ["rb"]},
    "php": {"category": "Programming", "aliases": []},
    "swift": {"category": "Programming", "aliases": []},
    "kotlin": {"category": "Programming", "aliases": ["kt"]},
    "scala": {"category": "Programming", "aliases": []},
    "r": {"category": "Programming", "aliases": ["r-lang", "r programming", "r studio"]},
    "perl": {"category": "Programming", "aliases": []},
    "matlab": {"category": "Programming", "aliases": []},
    "lua": {"category": "Programming", "aliases": []},
    "dart": {"category": "Programming", "aliases": []},
    "elixir": {"category": "Programming", "aliases": []},
    "haskell": {"category": "Programming", "aliases": []},
    "julia": {"category": "Programming", "aliases": []},
    "sql": {"category": "Programming", "aliases": ["structured query language"]},
    "html": {"category": "Programming", "aliases": ["html5"]},
    "css": {"category": "Programming", "aliases": ["css3"]},
    "bash": {"category": "Programming", "aliases": ["shell", "shell scripting", "bash scripting"]},
    "solidity": {"category": "Programming", "aliases": []},

    # Frameworks & Libraries
    "react": {"category": "Framework", "aliases": ["reactjs", "react.js", "react js"]},
    "vue.js": {"category": "Framework", "aliases": ["vuejs", "vue", "vue 2", "vue 3"]},
    "angular": {"category": "Framework", "aliases": ["angularjs", "angular.js", "angular 2", "angular 4", "angular 6", "angular 8", "angular 12", "angular 14", "angular 16"]},
    "next.js": {"category": "Framework", "aliases": ["nextjs", "next", "next js"]},
    "svelte": {"category": "Framework", "aliases": ["sveltejs", "svelte.js"]},
    "node.js": {"category": "Framework", "aliases": ["nodejs", "node", "node js"]},
    "express.js": {"category": "Framework", "aliases": ["expressjs", "express", "express js"]},
    "django": {"category": "Framework", "aliases": []},
    "flask": {"category": "Framework", "aliases": []},
    "fastapi": {"category": "Framework", "aliases": ["fast api", "fast-api"]},
    "spring": {"category": "Framework", "aliases": ["spring framework"]},
    "spring boot": {"category": "Framework", "aliases": ["springboot", "spring-boot"]},
    "laravel": {"category": "Framework", "aliases": []},
    "rails": {"category": "Framework", "aliases": ["ruby on rails"]},
    "bootstrap": {"category": "Framework", "aliases": []},
    "tailwind css": {"category": "Framework", "aliases": ["tailwind", "tailwindcss", "tailwind css"]},
    "jquery": {"category": "Framework", "aliases": []},
    "tensorflow": {"category": "Framework", "aliases": ["tf"]},
    "pytorch": {"category": "Framework", "aliases": ["pyt"]},
    "keras": {"category": "Framework", "aliases": []},
    "scikit-learn": {"category": "Framework", "aliases": ["sklearn", "scikit learn", "scikit"]},
    "pandas": {"category": "Framework", "aliases": []},
    "numpy": {"category": "Framework", "aliases": []},
    "matplotlib": {"category": "Framework", "aliases": []},
    "seaborn": {"category": "Framework", "aliases": []},
    "plotly": {"category": "Framework", "aliases": []},
    "scipy": {"category": "Framework", "aliases": []},
    "opencv": {"category": "Framework", "aliases": ["opencv-python"]},
    "hugging face": {"category": "Framework", "aliases": ["huggingface", "hf"]},
    "langchain": {"category": "Framework", "aliases": []},
    "llamaindex": {"category": "Framework", "aliases": ["llama index"]},

    # Databases
    "postgresql": {"category": "Database", "aliases": ["postgres", "psql"]},
    "mysql": {"category": "Database", "aliases": []},
    "mongodb": {"category": "Database", "aliases": ["mongo"]},
    "redis": {"category": "Database", "aliases": []},
    "sqlite": {"category": "Database", "aliases": ["sqlite3"]},
    "elasticsearch": {"category": "Database", "aliases": ["elastic", "elastic search"]},
    "cassandra": {"category": "Database", "aliases": []},
    "dynamodb": {"category": "Database", "aliases": ["dynamo"]},
    "oracle": {"category": "Database", "aliases": ["oracle db"]},
    "microsoft sql server": {"category": "Database", "aliases": ["mssql", "ms sql", "sql server"]},
    "firebase": {"category": "Database", "aliases": []},
    "supabase": {"category": "Database", "aliases": []},
    "neo4j": {"category": "Database", "aliases": []},
    "couchdb": {"category": "Database", "aliases": ["couch db"]},
    "couchbase": {"category": "Database", "aliases": []},
    "prisma": {"category": "Database", "aliases": []},
    "typeorm": {"category": "Database", "aliases": []},
    "sequelize": {"category": "Database", "aliases": []},
    "mongoose": {"category": "Database", "aliases": []},
    "sqlalchemy": {"category": "Database", "aliases": ["sql-alchemy"]},
    "kafka": {"category": "Database", "aliases": []},

    # Cloud & DevOps
    "aws": {"category": "Cloud", "aliases": ["amazon web services", "amazon aws"]},
    "azure": {"category": "Cloud", "aliases": ["microsoft azure"]},
    "gcp": {"category": "Cloud", "aliases": ["google cloud", "google cloud platform", "google cloud platform"]},
    "docker": {"category": "DevOps", "aliases": []},
    "kubernetes": {"category": "DevOps", "aliases": ["k8s"]},
    "jenkins": {"category": "DevOps", "aliases": []},
    "github actions": {"category": "DevOps", "aliases": []},
    "gitlab ci": {"category": "DevOps", "aliases": ["gitlab ci/cd"]},
    "travis ci": {"category": "DevOps", "aliases": ["travis"]},
    "circleci": {"category": "DevOps", "aliases": ["circle ci"]},
    "terraform": {"category": "DevOps", "aliases": []},
    "ansible": {"category": "DevOps", "aliases": []},
    "nginx": {"category": "DevOps", "aliases": []},
    "apache": {"category": "DevOps", "aliases": []},
    "ci/cd": {"category": "DevOps", "aliases": ["cicd", "ci cd", "continuous integration", "continuous deployment"]},
    "devops": {"category": "DevOps", "aliases": []},
    "aws lambda": {"category": "Cloud", "aliases": ["lambda"]},
    "serverless": {"category": "Cloud", "aliases": ["serverless computing"]},
    "ec2": {"category": "Cloud", "aliases": []},
    "s3": {"category": "Cloud", "aliases": ["amazon s3"]},
    "cloudformation": {"category": "Cloud", "aliases": []},
    "cloud computing": {"category": "Cloud", "aliases": []},

    # AI/ML
    "machine learning": {"category": "AI/ML", "aliases": ["ml", "machine-learning"]},
    "deep learning": {"category": "AI/ML", "aliases": ["dl", "deep-learning"]},
    "nlp": {"category": "AI/ML", "aliases": ["natural language processing"]},
    "computer vision": {"category": "AI/ML", "aliases": ["cv"]},
    "neural networks": {"category": "AI/ML", "aliases": ["neural network", "nn"]},
    "cnn": {"category": "AI/ML", "aliases": ["convolutional neural network", "convolutional neural networks"]},
    "rnn": {"category": "AI/ML", "aliases": ["recurrent neural network"]},
    "lstm": {"category": "AI/ML", "aliases": []},
    "gan": {"category": "AI/ML", "aliases": ["generative adversarial network"]},
    "transformers": {"category": "AI/ML", "aliases": ["transformer"]},
    "reinforcement learning": {"category": "AI/ML", "aliases": ["rl"]},
    "mlops": {"category": "AI/ML", "aliases": []},
    "model deployment": {"category": "AI/ML", "aliases": []},
    "data science": {"category": "AI/ML", "aliases": []},
    "data analysis": {"category": "AI/ML", "aliases": ["data analytics"]},
    "data visualization": {"category": "AI/ML", "aliases": []},
    "data cleaning": {"category": "AI/ML", "aliases": []},
    "statistics": {"category": "AI/ML", "aliases": []},
    "linear algebra": {"category": "AI/ML", "aliases": []},
    "probability": {"category": "AI/ML", "aliases": []},
    "object detection": {"category": "AI/ML", "aliases": []},
    "image segmentation": {"category": "AI/ML", "aliases": []},
    "image processing": {"category": "AI/ML", "aliases": []},
    "recommendation systems": {"category": "AI/ML", "aliases": ["recommender systems"]},
    "time series": {"category": "AI/ML", "aliases": ["time series analysis"]},
    "a/b testing": {"category": "AI/ML", "aliases": ["ab testing"]},
    "llm": {"category": "AI/ML", "aliases": ["large language model", "large language models"]},
    "openai": {"category": "AI/ML", "aliases": []},
    "rag": {"category": "AI/ML", "aliases": ["retrieval augmented generation"]},
    "fine-tuning": {"category": "AI/ML", "aliases": ["fine tuning", "finetuning"]},

    # Tools
    "git": {"category": "Tool", "aliases": []},
    "github": {"category": "Tool", "aliases": []},
    "gitlab": {"category": "Tool", "aliases": []},
    "bitbucket": {"category": "Tool", "aliases": []},
    "jira": {"category": "Tool", "aliases": []},
    "confluence": {"category": "Tool", "aliases": []},
    "postman": {"category": "Tool", "aliases": []},
    "swagger": {"category": "Tool", "aliases": []},
    "figma": {"category": "Tool", "aliases": []},
    "jupyter notebook": {"category": "Tool", "aliases": ["jupyter", "jupyterlab"]},
    "vs code": {"category": "Tool", "aliases": ["vscode"]},
    "intellij idea": {"category": "Tool", "aliases": ["intellij"]},
    "pycharm": {"category": "Tool", "aliases": []},
    "visual studio": {"category": "Tool", "aliases": ["vs"]},
    "notion": {"category": "Tool", "aliases": []},
    "slack": {"category": "Tool", "aliases": []},
    "excel": {"category": "Tool", "aliases": ["microsoft excel", "ms excel"]},
    "google sheets": {"category": "Tool", "aliases": []},
    "tableau": {"category": "Tool", "aliases": []},
    "power bi": {"category": "Tool", "aliases": ["powerbi"]},
    "looker": {"category": "Tool", "aliases": []},
    "apache spark": {"category": "Tool", "aliases": ["spark"]},
    "hadoop": {"category": "Tool", "aliases": []},
    "airflow": {"category": "Tool", "aliases": ["apache airflow"]},
    "dbt": {"category": "Tool", "aliases": []},
    "latex": {"category": "Tool", "aliases": []},

    # Testing
    "pytest": {"category": "Testing", "aliases": []},
    "unittest": {"category": "Testing", "aliases": ["unit test"]},
    "junit": {"category": "Testing", "aliases": []},
    "selenium": {"category": "Testing", "aliases": []},
    "cypress": {"category": "Testing", "aliases": []},
    "jest": {"category": "Testing", "aliases": []},
    "mocha": {"category": "Testing", "aliases": []},
    "playwright": {"category": "Testing", "aliases": []},

    # Methodologies
    "agile": {"category": "Methodology", "aliases": []},
    "scrum": {"category": "Methodology", "aliases": []},
    "kanban": {"category": "Methodology", "aliases": []},
    "waterfall": {"category": "Methodology", "aliases": []},
    "microservices": {"category": "Architecture", "aliases": ["microservice"]},
    "rest api": {"category": "Architecture", "aliases": ["rest", "restful", "rest apis"]},
    "graphql": {"category": "Architecture", "aliases": ["graph-ql"]},
    "grpc": {"category": "Architecture", "aliases": ["g-rpc"]},

    # Soft Skills
    "communication": {"category": "Soft Skill", "aliases": []},
    "leadership": {"category": "Soft Skill", "aliases": []},
    "problem solving": {"category": "Soft Skill", "aliases": []},
    "critical thinking": {"category": "Soft Skill", "aliases": []},
    "teamwork": {"category": "Soft Skill", "aliases": []},
    "project management": {"category": "Soft Skill", "aliases": ["pm"]},

    # OS
    "linux": {"category": "OS", "aliases": []},
    "unix": {"category": "OS", "aliases": []},
    "windows": {"category": "OS", "aliases": []},
    "macos": {"category": "OS", "aliases": ["mac os", "mac"]},
}

CATEGORY_ORDER = [
    "Programming", "Framework", "Database", "Cloud", "DevOps",
    "AI/ML", "Architecture", "Tool", "Testing", "Methodology",
    "Soft Skill", "OS",
]


def extract_skills_with_metadata(text, section_name=None):
    text_lower = text.lower()
    found = {}

    for skill_name, meta in SKILL_DICTIONARY.items():
        patterns = [skill_name] + meta["aliases"]
        best_confidence = 0.0
        best_source = "text"

        for pattern in patterns:
            confidence = _calculate_confidence(pattern, text_lower, section_name)
            if confidence > best_confidence:
                best_confidence = confidence
                if section_name:
                    best_source = section_name
                else:
                    best_source = "text"

        if best_confidence > 0:
            normalized = normalize_skill(skill_name)
            if normalized.lower() not in found:
                found[normalized.lower()] = {
                    "skill": normalized,
                    "category": meta["category"],
                    "confidence": round(min(best_confidence, 1.0), 2),
                    "source": best_source,
                }

    return list(found.values())


def _calculate_confidence(pattern, text_lower, section_name=None):
    base_confidence = 0.0

    if len(pattern) <= 2:
        boundary = r"(?:^|[\s,;|/\-•·\*])(?:" + re.escape(pattern) + r")(?:$|[\s,;|/\-•·\*])"
    else:
        boundary = r"(?:^|[\s,;|/\-•·\*])(?:" + re.escape(pattern) + r")(?:$|[\s,;|/\-•·\*])"

    exact_match = re.search(boundary, text_lower)
    if exact_match:
        base_confidence = 0.95
    elif len(pattern) > 2 and pattern in text_lower:
        base_confidence = 0.80

    if base_confidence == 0:
        return 0

    section_bonus = 0.0
    if section_name:
        section_bonuses = {
            "skills": 0.05,
            "technical skills": 0.05,
            "projects": 0.02,
            "experience": 0.01,
            "internship": 0.01,
            "certifications": 0.03,
            "summary": -0.05,
            "education": -0.05,
        }
        section_bonus = section_bonuses.get(section_name.lower(), 0)

    return base_confidence + section_bonus


def categorize_skills(skills_with_metadata):
    categorized = {cat: [] for cat in CATEGORY_ORDER}

    for s in skills_with_metadata:
        cat = s.get("category", "Other")
        if cat in categorized:
            categorized[cat].append(s["skill"])
        else:
            categorized.setdefault(cat, []).append(s["skill"])

    return {k: v for k, v in categorized.items() if v}
