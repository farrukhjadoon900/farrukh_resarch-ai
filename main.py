from crewai import Agent, Task, Crew, Process

# Manager Agent (khud handle karega)
manager = Agent(
    role="Project Manager",
    goal="Manage research tasks and ensure quality output",
    backstory="You're an experienced manager who delegates and validates work.",
    allow_delegation=True,
)

# Researcher Agent
researcher = Agent(
    role="Senior Researcher",
    goal="Find accurate information on the given topic",
    backstory="You are a meticulous researcher who cites sources.",
    allow_delegation=False,
)

# Writer Agent  
writer = Agent(
    role="Technical Writer",
    goal="Create clear reports from research",
    backstory="You turn complex research into readable summaries.",
    allow_delegation=False,
)

# Tasks
research_task = Task(
    description="Research the topic provided by the user.",
    expected_output="Detailed findings with sources",
    agent=researcher,
)

write_task = Task(
    description="Write a report based on the research.",
    expected_output="A structured report",
    agent=writer,
)

# Crew with Manager
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.hierarchical,
    manager_llm="gpt-4o",  # Ya Gemini/Groq
    verbose=True,
)

result = crew.kickoff()
print(result)