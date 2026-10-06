import re

ALIAS_MAP = {
    # Programming Languages
    "ml": "Machine Learning",
    "dl": "Deep Learning",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "py": "Python",
    "python": "Python",
    "java": "Java",
    "rb": "Ruby",
    "ruby": "Ruby",
    "rs": "Rust",
    "rust": "Rust",
    "cs": "C#",
    "csharp": "C#",
    "c#": "C#",
    "cplusplus": "C++",
    "c++": "C++",
    "golang": "Go",
    "go": "Go",
    "r-lang": "R",
    "r-programming": "R",
    "scala": "Scala",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "php": "PHP",
    "perl": "Perl",
    "dart": "Dart",
    "elixir": "Elixir",
    "haskell": "Haskell",
    "julia": "Julia",
    "lua": "Lua",
    "sql": "SQL",
    "html": "HTML",
    "css": "CSS",
    "bash": "Bash",
    "shell": "Shell",
    "solidity": "Solidity",

    # Frameworks & Libraries
    "reactjs": "React",
    "react.js": "React",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",
    "angularjs": "Angular",
    "angular.js": "Angular",
    "sklearn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "tf": "TensorFlow",
    "tensorflow": "TensorFlow",
    "pyt": "PyTorch",
    "pytorch": "PyTorch",
    "keras": "Keras",
    "flask": "Flask",
    "django": "Django",
    "fastapi": "FastAPI",
    "fast-api": "FastAPI",
    "springboot": "Spring Boot",
    "spring-boot": "Spring Boot",
    "spring boot": "Spring Boot",
    "spring": "Spring",
    "laravel": "Laravel",
    "rails": "Ruby on Rails",
    "ruby on rails": "Ruby on Rails",

    # Databases
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "sqlite": "SQLite",
    "sqlite3": "SQLite",
    "mssql": "Microsoft SQL Server",
    "ms sql": "Microsoft SQL Server",
    "oracle db": "Oracle",
    "oracle": "Oracle",
    "cassandra": "Cassandra",
    "dynamodb": "DynamoDB",
    "dynamo": "DynamoDB",
    "elasticsearch": "Elasticsearch",
    "elastic": "Elasticsearch",
    "firebase": "Firebase",
    "supabase": "Supabase",
    "prisma": "Prisma",
    "typeorm": "TypeORM",
    "sequelize": "Sequelize",
    "mongoose": "Mongoose",
    "sqlalchemy": "SQLAlchemy",
    "sql-alchemy": "SQLAlchemy",

    # Cloud & DevOps
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "jenkins": "Jenkins",
    "github actions": "GitHub Actions",
    "gitlab ci": "GitLab CI",
    "travis": "Travis CI",
    "travis ci": "Travis CI",
    "circleci": "CircleCI",
    "circle ci": "CircleCI",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "nginx": "Nginx",
    "apache": "Apache",

    # AI/ML
    "nlp": "NLP",
    "natural language processing": "NLP",
    "cv": "Computer Vision",
    "computer vision": "Computer Vision",
    "cnn": "CNN",
    "convolutional neural network": "CNN",
    "convolutional neural networks": "CNN",
    "rnn": "RNN",
    "recurrent neural network": "RNN",
    "lstm": "LSTM",
    "gan": "GAN",
    "generative adversarial network": "GAN",
    "transformer": "Transformers",
    "transformers": "Transformers",
    "huggingface": "Hugging Face",
    "hugging face": "Hugging Face",
    "openai": "OpenAI",
    "llm": "LLM",
    "large language model": "LLM",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "reinforcement learning": "Reinforcement Learning",
    "mlops": "MLOps",
    "model deployment": "Model Deployment",

    # Data
    "pandas": "Pandas",
    "numpy": "NumPy",
    "matplotlib": "Matplotlib",
    "seaborn": "Seaborn",
    "plotly": "Plotly",
    "scipy": "SciPy",
    "jupyter": "Jupyter",
    "jupyter notebook": "Jupyter Notebook",
    "jupyterlab": "JupyterLab",
    "excel": "Excel",
    "google sheets": "Google Sheets",
    "tableau": "Tableau",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "looker": "Looker",
    "apache spark": "Apache Spark",
    "spark": "Apache Spark",
    "hadoop": "Hadoop",
    "kafka": "Kafka",
    "airflow": "Airflow",
    "dbt": "dbt",

    # Frontend
    "html": "HTML",
    "html5": "HTML",
    "css": "CSS",
    "css3": "CSS",
    "sass": "SASS",
    "scss": "SASS",
    "less": "LESS",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "jquery": "jQuery",
    "svelte": "Svelte",
    "graphql": "GraphQL",
    "graph-ql": "GraphQL",
    "rest": "REST API",
    "rest api": "REST API",
    "restful": "REST API",
    "grpc": "gRPC",

    # Tools
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "bitbucket": "Bitbucket",
    "vscode": "VS Code",
    "vs code": "VS Code",
    "intellij": "IntelliJ IDEA",
    "intellij idea": "IntelliJ IDEA",
    "pycharm": "PyCharm",
    "vim": "Vim",
    "emacs": "Emacs",
    "postman": "Postman",
    "swagger": "Swagger",
    "jira": "Jira",
    "confluence": "Confluence",
    "notion": "Notion",
    "figma": "Figma",
    "sketch": "Sketch",

    # Testing
    "pytest": "pytest",
    "unittest": "unittest",
    "junit": "JUnit",
    "selenium": "Selenium",
    "cypress": "Cypress",
    "jest": "Jest",
    "mocha": "Mocha",
    "playwright": "Playwright",

    # Soft Skills
    "problem solving": "Problem Solving",
    "communication": "Communication",
    "teamwork": "Teamwork",
    "leadership": "Leadership",
    "critical thinking": "Critical Thinking",
    "project management": "Project Management",
    "agile": "Agile",
    "scrum": "Scrum",
    "kanban": "Kanban",

    # Other
    "linux": "Linux",
    "unix": "Unix",
    "bash": "Bash",
    "shell": "Shell",
    "powershell": "PowerShell",
    "latex": "LaTeX",
    "matlab": "MATLAB",
    "solidity": "Solidity",
    "blockchain": "Blockchain",
    "web3": "Web3",
    "oauth": "OAuth",
    "jwt": "JWT",
    "oauth2": "OAuth 2.0",
    "cors": "CORS",
    "ssl": "SSL",
    "tls": "TLS",
    "microservices": "Microservices",
    "serverless": "Serverless",
    "lambda": "AWS Lambda",
    "etl": "ETL",
    "data pipeline": "Data Pipeline",
    "data engineering": "Data Engineering",
    "data science": "Data Science",
    "data analysis": "Data Analysis",
    "data visualization": "Data Visualization",
    "data cleaning": "Data Cleaning",
    "statistics": "Statistics",
    "linear algebra": "Linear Algebra",
    "probability": "Probability",
    "image processing": "Image Processing",
    "object detection": "Object Detection",
    "image segmentation": "Image Segmentation",
    "ocr": "OCR",
    "speech recognition": "Speech Recognition",
    "recommendation systems": "Recommendation Systems",
    "time series": "Time Series",
    "a/b testing": "A/B Testing",
    "ab testing": "A/B Testing",
    "neural networks": "Neural Networks",
    "neural network": "Neural Networks",
}


def normalize_skill(raw_skill):
    cleaned = raw_skill.strip().lower()
    cleaned = _remove_parentheses(cleaned)
    cleaned = _clean_whitespace(cleaned)

    if cleaned in ALIAS_MAP:
        return ALIAS_MAP[cleaned]

    for alias, canonical in ALIAS_MAP.items():
        if cleaned == alias.lower():
            return canonical

    return _title_case(raw_skill.strip())


def normalize_skill_list(raw_skills):
    normalized = []
    seen = set()

    for skill in raw_skills:
        result = normalize_skill(skill)
        key = result.lower().strip()
        if key not in seen:
            seen.add(key)
            normalized.append(result)

    return normalized


def _remove_parentheses(text):
    return text.replace("(", "").replace(")", "")


def _clean_whitespace(text):
    return " ".join(text.split())


def _title_case(text):
    if text.isupper() and len(text) <= 5:
        return text.capitalize()

    if " " in text:
        words = text.split()
        result = []
        small_words = {"and", "of", "the", "in", "on", "at", "to", "for", "with", "a", "an"}
        for i, word in enumerate(words):
            if i == 0 or word.lower() not in small_words:
                result.append(word.capitalize())
            else:
                result.append(word.lower())
        return " ".join(result)

    if re.match(r"^[A-Z]", text) and not text.isupper():
        return text

    return text[0].upper() + text[1:] if text else text
