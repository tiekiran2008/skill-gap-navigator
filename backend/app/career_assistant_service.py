import os
import json
from dotenv import load_dotenv

load_dotenv()

from app.assistant_tools import TOOLS, execute_tool

SYSTEM_PROMPT = """You are a Career Development Assistant for the Skill Gap Navigator platform.

Your role is to help users understand their career readiness, skill gaps, and learning path.

You have access to tools that retrieve the user's real data. Always call the appropriate tools before answering questions about their profile, skills, or progress.

Rules:
- Always call tools to get real data before answering. Do not make up data.
- Be concise and actionable. Use bullet points.
- When explaining skill gaps, mention importance levels (critical/high/medium/low).
- When suggesting next steps, prioritize by impact.
- If a tool returns an error, explain what the user needs to do.
- Never reveal raw JSON to the user. Summarize clearly.

Available tools:
- get_user_profile: Get user's skills and target role
- get_skill_gaps: Analyze gaps for a specific role
- get_career_matches: Get top career recommendations
- get_company_analysis: Get company-specific analysis
- get_roadmap: Get learning roadmaps
- get_progress: Get overall learning progress
"""


def _get_llm_client():
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY")
    base_url = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
    if not api_key:
        return None, None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)
        model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
        return client, model
    except ImportError:
        return None, None


def _build_tools_schema():
    schema = []
    for name, tool in TOOLS.items():
        properties = {}
        required = []
        for param_name, param_info in tool.get("parameters", {}).items():
            properties[param_name] = {
                "type": param_info.get("type", "string"),
                "description": param_info.get("description", ""),
            }
            if param_info.get("required", False):
                required.append(param_name)

        schema.append({
            "type": "function",
            "function": {
                "name": name,
                "description": tool["description"],
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                } if properties else {"type": "object", "properties": {}},
            },
        })
    return schema


def _classify_intent(user_message: str) -> list:
    msg = user_message.lower()
    tools_to_call = []

    intent_keywords = {
        "get_user_profile": ["my skills", "what skills", "my profile", "what do i know", "my background", "what am i good at"],
        "get_skill_gaps": ["gap", "missing", "don't know", "need to learn", "not ready", "not qualified", "what am i missing", "readiness", "how ready", "am i ready", "skill gap", "biggest improvement", "which skill", "what should i learn next"],
        "get_career_matches": ["career", "recommend", "what job", "what role", "suit", "match me", "best role", "which role"],
        "get_company_analysis": ["company", "zoho", "tcs", "infosys", "amazon", "microsoft", "accenture", "cognizant", "freshworks", "improve my match", "how can i improve"],
        "get_roadmap": ["roadmap", "learning path", "learning plan", "study plan", "curriculum", "projects should i build"],
        "get_progress": ["progress", "how am i doing", "what have i completed", "learning status", "how much have i learned"],
        "get_interview_plan": ["interview", "mock interview", "prepare for interview", "interview prep", "interview preparation", "what should i prepare", "practice interview", "interview questions", "weakest topics", "project questions"],
        "get_interview_history": ["interview results", "interview history", "past interviews", "interview scores"],
    }

    for tool_name, keywords in intent_keywords.items():
        for kw in keywords:
            if kw in msg:
                tools_to_call.append(tool_name)
                break

    if not tools_to_call:
        if any(w in msg for w in ["hello", "hi", "hey", "help"]):
            tools_to_call = ["get_user_profile", "get_progress"]
        else:
            tools_to_call = ["get_user_profile"]

    return list(dict.fromkeys(tools_to_call))


def _fallback_response(user_message: str, tool_results: dict) -> str:
    msg = user_message.lower()

    if "how ready" in msg or "am i ready" in msg or "not ready" in msg:
        for tool_name, result in tool_results.items():
            if tool_name == "get_skill_gaps" and "overall_match" in result:
                pct = result["overall_match"]
                missing = result.get("missing_skills", [])
                matched = result.get("matched_skills", [])
                role = result.get("target_role", "your target role")
                lines = [f"**Your readiness for {role}: {pct}%**\n"]
                if matched:
                    lines.append(f"**Strengths ({len(matched)} matched):**")
                    for s in matched[:5]:
                        lines.append(f"- {s['skill']} ({s.get('importance', 'medium')})")
                if missing:
                    lines.append(f"\n**Gaps to close ({len(missing)} missing):**")
                    for s in missing[:5]:
                        lines.append(f"- {s['skill']} ({s.get('importance', 'medium')})")
                if pct < 50:
                    lines.append(f"\nFocus on critical skills first. Start with the missing skills marked as 'critical' or 'high' importance.")
                elif pct < 75:
                    lines.append(f"\nYou're making good progress! Focus on the remaining gaps to reach 75%+ readiness.")
                else:
                    lines.append(f"\nYou're nearly there! Fine-tune the remaining small gaps.")
                return "\n".join(lines)

    if "what should i learn" in msg or "learn next" in msg:
        for tool_name, result in tool_results.items():
            if tool_name == "get_skill_gaps":
                priority = result.get("priority_gaps", [])
                if priority:
                    lines = ["**Recommended learning order (by impact):**\n"]
                    for i, g in enumerate(priority, 1):
                        lines.append(f"{i}. **{g['skill']}** ({g['importance']})")
                    lines.append("\nStart with the highest-importance skill. Each builds on the previous.")
                    return "\n".join(lines)
            if tool_name == "get_roadmap":
                roadmaps = result.get("roadmaps", [])
                if roadmaps:
                    r = roadmaps[0]
                    lines = [f"**Your learning roadmap ({r['target_role']}):**\n"]
                    lines.append(f"- Completed: {r['completed']} skills")
                    lines.append(f"- In progress: {r['learning']} skills")
                    lines.append(f"- Remaining: {r['remaining']} skills")
                    lines.append("\nContinue with your current learning phase.")
                    return "\n".join(lines)

    if "biggest improvement" in msg or "which skill" in msg:
        for tool_name, result in tool_results.items():
            if tool_name == "get_skill_gaps":
                missing = result.get("missing_skills", [])
                priority = result.get("priority_gaps", [])
                if priority:
                    top = priority[0]
                    lines = [f"**{top['skill']}** gives you the biggest improvement.\n"]
                    lines.append(f"It's marked as **{top['importance']}** importance for {result.get('target_role', 'your target role')}.")
                    lines.append(f"Learning this single skill could boost your readiness significantly.")
                    return "\n".join(lines)
                elif missing:
                    lines = [f"**{missing[0]['skill']}** is your top priority.\n"]
                    lines.append(f"It's a {missing[0].get('importance', 'high')} importance gap.")
                    return "\n".join(lines)

    if "docker" in msg and ("why" in msg or "required" in msg):
        return """**Why Docker is required:**\n
- Docker containers ensure consistent environments across development and production
- Most modern backend/ML deployments use containerization
- Required for Kubernetes and cloud-native architectures
- Simplifies dependency management and scaling
- Widely used in DevOps and MLOps workflows\n
It's a foundational skill for deployment and infrastructure roles."""

    if "project" in msg and ("build" in msg or "what" in msg):
        for tool_name, result in tool_results.items():
            if tool_name == "get_skill_gaps":
                missing = result.get("missing_skills", [])
                priority = result.get("priority_gaps", [])
                if priority:
                    lines = ["**Projects to build (based on your gaps):**\n"]
                    for g in priority[:3]:
                        lines.append(f"- Build a project using **{g['skill']}** to demonstrate competency")
                    lines.append("\nEach project should be on GitHub with a clear README.")
                    return "\n".join(lines)

    if "improve" in msg and ("match" in msg or "zoho" in msg or "company" in msg):
        for tool_name, result in tool_results.items():
            if tool_name == "get_company_analysis":
                analyses = result.get("analyses", [])
                if analyses:
                    a = analyses[0]
                    lines = [f"**How to improve your match for {a['company']}:**\n"]
                    if a.get("missing_skills"):
                        lines.append("Learn these missing skills:")
                        for s in a["missing_skills"][:5]:
                            lines.append(f"- {s}")
                    if a.get("matched_skills"):
                        lines.append(f"\nLeverage your strengths: {', '.join(a['matched_skills'][:3])}")
                    lines.append(f"\nCurrent match: {a.get('match_percentage', 0)}%")
                    return "\n".join(lines)

    if "interview" in msg and ("prepare" in msg or "prep" in msg or "what should" in msg):
        for tool_name, result in tool_results.items():
            if tool_name == "get_interview_plan":
                if "error" in result:
                    return f"**Interview Preparation:**\n{result['error']}\n\nSet a target role first, then I can generate a personalized interview plan."
                readiness = result.get("interview_readiness", {})
                overall = readiness.get("overall_readiness", 0)
                priority = result.get("priority_topics", [])[:3]
                lines = [f"**Interview Readiness: {overall}%**\n"]
                if priority:
                    lines.append("**Priority topics to prepare:**")
                    for p in priority:
                        lines.append(f"- {p}")
                lines.append(f"\n**Technical Readiness:** {readiness.get('technical_readiness', 0)}%")
                lines.append(f"**Verified Skill Confidence:** {readiness.get('verified_skill_confidence', 0)}%")
                lines.append(f"**Project Readiness:** {readiness.get('project_readiness', 0)}%")
                lines.append("\nGo to **Interview Prep** to start a mock interview!")
                return "\n".join(lines)

    if "mock interview" in msg:
        for tool_name, result in tool_results.items():
            if tool_name == "get_interview_plan":
                if "error" in result:
                    return f"**Mock Interview:**\n{result['error']}\n\nSet a target role first, then I can start a mock interview."
                return "**Mock Interview Available!**\n\nGo to **Interview Prep** page and select an interview mode:\n- Quick (5 questions)\n- Technical (10 questions)\n- Project (8 questions)\n- Behavioral (10 questions)\n- Full Mock (15-20 questions)\n\nEach mode adapts to your target role and skill gaps."

    if "weakest" in msg and ("topic" in msg or "skill" in msg):
        for tool_name, result in tool_results.items():
            if tool_name == "get_interview_plan":
                if "error" in result:
                    return f"**Weak Areas:**\n{result['error']}"
                weak = result.get("weak_areas", [])
                if weak:
                    lines = ["**Your weak areas (prioritized):**\n"]
                    for i, w in enumerate(weak[:5], 1):
                        lines.append(f"{i}. **{w}**")
                    lines.append("\nThese topics need more practice. Start a mock interview to improve!")
                    return "\n".join(lines)
                else:
                    return "**Weak Areas:** No weak areas identified yet. Complete a mock interview to get personalized feedback!"

    if "project question" in msg:
        for tool_name, result in tool_results.items():
            if tool_name == "get_interview_plan":
                if "error" in result:
                    return f"**Project Questions:**\n{result['error']}"
                project_qs = result.get("project_questions", [])
                if project_qs:
                    lines = ["**Project-based interview questions:**\n"]
                    for i, q in enumerate(project_qs[:5], 1):
                        lines.append(f"{i}. {q.get('question', '')}")
                        techs = q.get("technologies", [])
                        if techs:
                            lines.append(f"   Technologies: {', '.join(techs)}")
                    return "\n".join(lines)
                else:
                    return "**Project Questions:** No project questions available. Add projects to your profile first!"

    if "hello" in msg or "hi" == msg.strip() or "hey" in msg:
        profile = tool_results.get("get_user_profile", {})
        progress = tool_results.get("get_progress", {})
        name = profile.get("full_name", "") or "there"
        skill_count = profile.get("skill_count", 0)
        target = profile.get("target_role", "")
        completed = progress.get("total_completed", 0)

        lines = [f"Hi {name}! I'm your Career Development Assistant.\n"]
        if skill_count:
            lines.append(f"You have **{skill_count} skills** on file.")
        if target:
            lines.append(f"Your target role: **{target}**.")
        if completed:
            lines.append(f"You've completed **{completed} learning items**.")
        lines.append("\nAsk me anything about your career path, skill gaps, or learning progress!")
        return "\n".join(lines)

    profile = tool_results.get("get_user_profile", {})
    skill_count = profile.get("skill_count", 0)
    target = profile.get("target_role", "")

    lines = ["I can help you with:\n"]
    lines.append("- **Skill gaps**: 'How ready am I for AI Engineer?'")
    lines.append("- **Learning path**: 'What should I learn next?'")
    lines.append("- **Biggest impact**: 'Which skill gives me the biggest improvement?'")
    lines.append("- **Career matches**: 'What careers suit me?'")
    lines.append("- **Company analysis**: 'How can I improve my match for Zoho?'")
    lines.append("- **Progress**: 'What have I learned so far?'")
    lines.append("- **Interview prep**: 'What should I prepare for my interview?'")
    lines.append("- **Mock interview**: 'Give me a mock interview for AI/ML Engineer'")
    lines.append("- **Weak topics**: 'Which topics am I weakest in?'")
    if skill_count:
        lines.append(f"\nYou currently have {skill_count} skills recorded.")
    if target:
        lines.append(f"Target role: {target}")
    return "\n".join(lines)


def chat(user_id: str, user_message: str, history: list = None) -> dict:
    tools_to_call = _classify_intent(user_message)

    tool_results = {}
    relevant_skills = []
    suggested_action = None

    for tool_name in tools_to_call:
        result = execute_tool(tool_name, user_id)
        tool_results[tool_name] = result

        if tool_name == "get_skill_gaps":
            for m in result.get("matched_skills", []):
                relevant_skills.append(m["skill"])
            for m in result.get("missing_skills", []):
                relevant_skills.append(m["skill"])
            if result.get("priority_gaps"):
                suggested_action = f"Learn {result['priority_gaps'][0]['skill']} next"

        if tool_name == "get_career_matches":
            for r in result.get("recommendations", []):
                relevant_skills.extend(r.get("missing_skills", []))

        if tool_name == "get_company_analysis":
            for a in result.get("analyses", []):
                relevant_skills.extend(a.get("matched_skills", []))
                relevant_skills.extend(a.get("missing_skills", []))

    relevant_skills = list(dict.fromkeys(relevant_skills))[:10]

    client, model = _get_llm_client()

    if client and model:
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            if history:
                for h in history[-6:]:
                    messages.append({"role": h["role"], "content": h["content"]})

            tool_context = json.dumps(tool_results, indent=2, default=str)
            messages.append({"role": "user", "content": f"User asked: {user_message}\n\nTool results:\n{tool_context}"})

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=500,
                temperature=0.3,
            )

            ai_response = response.choices[0].message.content

            return {
                "response": ai_response,
                "relevant_skills": relevant_skills,
                "suggested_action": suggested_action,
                "tools_used": tools_to_call,
                "source": "ai",
            }
        except Exception as e:
            pass

    fallback = _fallback_response(user_message, tool_results)
    return {
        "response": fallback,
        "relevant_skills": relevant_skills,
        "suggested_action": suggested_action,
        "tools_used": tools_to_call,
        "source": "fallback",
    }
