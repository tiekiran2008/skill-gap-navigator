from app.skill_demand_analyzer import get_skill_demand_for_role, get_skill_demand_across_all_roles
from app.role_demand_analyzer import get_role_demand, get_roles_for_company, get_companies
from app.market_insight_service import analyze_user_vs_market, get_role_insight, get_company_insight


def get_market_overview():
    role_demand = get_role_demand()
    skill_demand = get_skill_demand_across_all_roles()
    companies = get_companies()
    return {
        "role_demand": role_demand,
        "skill_demand": skill_demand,
        "companies": companies,
    }


def get_role_skills(role):
    return get_skill_demand_for_role(role)


def analyze_user(user_skills, target_role=None):
    return analyze_user_vs_market(user_skills, target_role)


def get_company_view(company, user_skills=None):
    return get_company_insight(company, user_skills)


def get_trend(role, user_skills=None):
    return get_role_insight(role, user_skills)
