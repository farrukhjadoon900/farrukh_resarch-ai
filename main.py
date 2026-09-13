import os
from crewai import Agent, Task, Crew, Process

# Topic GitHub Actions se aayega
topic = os.environ.get('TOPIC', 'default topic')
print(f"Researching: {topic}")

# Manager Agent
manager = Agent(
    role="Project Manager",
    goal="Manage research tasks and ensure quality output",
    backstory="You are an experienced manager who delegates and validates work.",
    allow_delegation=True,
)

# Researcher Agent
researcher = Agent(
    role="Senior Researcher",
    goal="Find accurate information on the given topic",
    backstory="You are a meticulous researcher who cites sources.",
    allow_delegation=False,
    llm="gemini/gemini-2.0-flash",
)

# Writer Agent
writer = Agent(
    role="Technical Writer",
    goal="Create clear reports from research",
    backstory="You turn complex research into readable summaries.",
    allow_delegation=False,
    llm="gemini/gemini-2.0-flash",
)

# Tasks
research_task = Task(
    description=f"Research this topic thoroughly: {topic}",
    expected_output="Detailed findings with sources",
    agent=researcher,
)

write_task = Task(
    description=f"Write a structured report on: {topic}",
    expected_output="A clean markdown report",
    agent=writer,
)

# Crew with Manager
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.hierarchical,
    manager_llm="gemini/gemini-2.0-flash",
    verbose=True,
)

result = crew.kickoff()

# Result save karein
with open('output.md', 'w', encoding='utf-8') as f:
    f.write(str(result))

print("Done! Result output.md mein save ho gaya.")
