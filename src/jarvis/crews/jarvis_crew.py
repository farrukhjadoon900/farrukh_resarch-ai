"""
Jarvis crew — command router + research + skill learning + expert answer.
"""

from __future__ import annotations

import os
from crewai import Agent, Crew, Process, Task
from crewai_tools import DirectoryReadTool, FileReadTool, FileWriterTool

from jarvis.config import MAX_ITER, SKILLS_DIR, VERBOSE
from jarvis.llm import get_llm
from jarvis.tools import (
    append_skill_reference,
    list_skills,
    read_skill,
    write_skill,
)

try:
    from crewai_tools import SerperDevTool

    _search = SerperDevTool()
    SEARCH_TOOLS = [_search]
except Exception:
    SEARCH_TOOLS = []


def _get_skills_dir_path() -> str:
    """Safely return skills directory path as string, creating it if needed."""
    skills_path = str(SKILLS_DIR)
    if not os.path.exists(skills_path):
        os.makedirs(skills_path, exist_ok=True)
    return skills_path


def _common_tools():
    skills_path = _get_skills_dir_path()
    tools = [
        list_skills,
        read_skill,
        write_skill,
        append_skill_reference,
        DirectoryReadTool(directory=skills_path),
        FileReadTool(),
        FileWriterTool(),
    ]
    tools.extend(SEARCH_TOOLS)
    return tools


def build_agents():
    llm = get_llm()
    skills_path = _get_skills_dir_path()

    router = Agent(
        role="Jarvis Command Router",
        goal=(
            "Classify the user command: (1) learn/update a skill, "
            "(2) answer using existing skills, (3) general research/help. "
            "Produce a clear plan for the rest of the crew."
        ),
        backstory=(
            "You are the calm, precise interface of Jarvis. "
            "You never invent skills that do not exist; you check list_skills first. "
            "You write short, actionable plans."
        ),
        llm=llm,
        tools=[list_skills, read_skill],
        verbose=VERBOSE,
        max_iter=MAX_ITER,
        allow_delegation=False,
    )

    researcher = Agent(
        role="Deep Research Specialist",
        goal=(
            "Gather high-quality, current information from available tools and "
            "reason carefully. Prefer primary sources, official docs, and "
            "consensus best practices. Flag uncertainty."
        ),
        backstory=(
            "Senior research analyst with 20+ years of synthesizing technical "
            "and professional domains. You separate fact from hype and always "
            "note confidence level."
        ),
        llm=llm,
        tools=_common_tools(),
        verbose=VERBOSE,
        max_iter=MAX_ITER,
        allow_delegation=False,
    )

    skill_smith = Agent(
        role="Skill Architect",
        goal=(
            "Turn research into a professional SKILL.md that makes any agent "
            "behave like a 20-year practitioner in that domain. Write clear "
            "when-to-use, steps, anti-patterns, quality bars, and examples."
        ),
        backstory=(
            "You design agent skills for production systems. You know that "
            "skills must be concise, actionable, and versioned. You always "
            "use the write_skill tool to persist the skill package."
        ),
        llm=llm,
        tools=[list_skills, read_skill, write_skill, append_skill_reference, FileReadTool()],
        verbose=VERBOSE,
        max_iter=MAX_ITER,
        allow_delegation=False,
    )

    expert = Agent(
        role="Domain Expert Advisor",
        goal=(
            "Answer the user with professional depth. Load relevant skills via "
            "read_skill / list_skills when available. Structure answers clearly: "
            "executive summary, steps, risks, next actions."
        ),
        backstory=(
            "You are Jarvis's voice to the user — articulate, honest about limits, "
            "and practical. You sound like a trusted senior advisor, not a chatbot."
        ),
        llm=llm,
        tools=[list_skills, read_skill, DirectoryReadTool(directory=skills_path)],
        verbose=VERBOSE,
        max_iter=MAX_ITER,
        allow_delegation=False,
    )

    return router, researcher, skill_smith, expert


def build_tasks(command: str, mode: str, agents):
    router, researcher, skill_smith, expert = agents

    plan_task = Task(
        description=(
            f"User command:\n```\n{command}\n```\n\n"
            f"Requested mode hint: {mode}\n\n"
            "1. Call list_skills to see what is already learned.\n"
            "2. Decide intent: LEARN_SKILL | ANSWER | RESEARCH.\n"
            "3. Output a short plan with: intent, skill_name (if any), "
            "research questions, and whether write_skill must run."
        ),
        expected_output=(
            "YAML-like plan with keys: intent, skill_name, research_questions, "
            "must_write_skill (bool), notes"
        ),
        agent=router,
    )

    research_task = Task(
        description=(
            f"Execute research for the user command:\n```\n{command}\n```\n\n"
            "Use the router's plan. Search and/or reason deeply. "
            "If learning a skill, collect: core concepts, decision frameworks, "
            "common failures, quality checklist, and practical examples. "
            "Cite sources when tools provide them. Mark confidence."
        ),
        expected_output=(
            "Structured research brief: findings, sources, open questions, confidence"
        ),
        agent=researcher,
        context=[plan_task],
    )

    skill_task = Task(
        description=(
            "If the plan says must_write_skill=true (or mode is learn), "
            "author a complete SKILL.md and call write_skill.\n\n"
            "SKILL.md requirements:\n"
            "- YAML frontmatter: name, description, metadata.version, metadata.last_updated\n"
            "- Sections: When to Use, Core Principles, Step-by-step Workflow, "
            "Anti-patterns, Quality Bar / Definition of Done, Examples, Sources\n"
            "- Write for a senior practitioner (20+ years framing in guidance quality)\n"
            "- Keep body focused; put long notes via append_skill_reference if needed\n\n"
            "If must_write_skill=false, output SKIP and why."
        ),
        expected_output="Confirmation of skill path written, or SKIP with reason",
        agent=skill_smith,
        context=[plan_task, research_task],
    )

    answer_task = Task(
        description=(
            f"Final response to the user for:\n```\n{command}\n```\n\n"
            "Use learned skills (read_skill) when relevant. "
            "Be professional, structured, and actionable. "
            "If a skill was just learned, briefly say what was saved and where. "
            "Do not invent credentials or false certainty."
        ),
        expected_output="User-facing professional answer in clear Markdown",
        agent=expert,
        context=[plan_task, research_task, skill_task],
    )

    return [plan_task, research_task, skill_task, answer_task]


def build_crew(command: str, mode: str = "auto") -> Crew:
    agents = build_agents()
    tasks = build_tasks(command, mode, agents)
    return Crew(
        agents=list(agents),
        tasks=tasks,
        process=Process.sequential,
        verbose=VERBOSE,
        memory=False,
    )


def run_jarvis(command: str, mode: str = "auto") -> str:
    crew = build_crew(command, mode=mode)
    result = crew.kickoff()
    return str(result)
