import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.skill_normalizer import normalize_skill, normalize_skill_list


def test_normalize_alias_ml():
    assert normalize_skill("ml") == "Machine Learning"


def test_normalize_alias_dl():
    assert normalize_skill("dl") == "Deep Learning"


def test_normalize_alias_js():
    assert normalize_skill("js") == "JavaScript"


def test_normalize_alias_ts():
    assert normalize_skill("ts") == "TypeScript"


def test_normalize_alias_reactjs():
    assert normalize_skill("reactjs") == "React"
    assert normalize_skill("ReactJS") == "React"
    assert normalize_skill("react.js") == "React"


def test_normalize_alias_postgres():
    assert normalize_skill("postgres") == "PostgreSQL"
    assert normalize_skill("Postgres") == "PostgreSQL"


def test_normalize_alias_sklearn():
    assert normalize_skill("sklearn") == "Scikit-learn"
    assert normalize_skill("Sklearn") == "Scikit-learn"


def test_normalize_alias_nodejs():
    assert normalize_skill("nodejs") == "Node.js"
    assert normalize_skill("NodeJS") == "Node.js"
    assert normalize_skill("node.js") == "Node.js"


def test_normalize_alias_vuejs():
    assert normalize_skill("vuejs") == "Vue.js"
    assert normalize_skill("VueJS") == "Vue.js"
    assert normalize_skill("vue.js") == "Vue.js"


def test_normalize_exact_match():
    assert normalize_skill("Python") == "Python"
    assert normalize_skill("python") == "Python"
    assert normalize_skill("JAVA") == "Java"


def test_normalize_unknown_passthrough():
    result = normalize_skill("SomeUnknownSkill")
    assert result == "SomeUnknownSkill"


def test_normalize_list_deduplicates():
    raw = ["python", "Python", "PYTHON", "py"]
    result = normalize_skill_list(raw)
    assert result.count("Python") == 1


def test_normalize_list_multiple():
    raw = ["js", "react", "nodejs", "postgres", "ml"]
    result = normalize_skill_list(raw)
    expected = ["JavaScript", "React", "Node.js", "PostgreSQL", "Machine Learning"]
    assert result == expected


if __name__ == "__main__":
    test_normalize_alias_ml()
    test_normalize_alias_dl()
    test_normalize_alias_js()
    test_normalize_alias_ts()
    test_normalize_alias_reactjs()
    test_normalize_alias_postgres()
    test_normalize_alias_sklearn()
    test_normalize_alias_nodejs()
    test_normalize_alias_vuejs()
    test_normalize_exact_match()
    test_normalize_unknown_passthrough()
    test_normalize_list_deduplicates()
    test_normalize_list_multiple()
    print("All skill normalizer tests passed!")
