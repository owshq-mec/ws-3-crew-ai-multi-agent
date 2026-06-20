from __future__ import annotations

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class SentinelCrew:
    """Shell for the Sentinel hierarchical crew.

    This scaffold wires a placeholder Manager agent and an empty specialist
    roster.  Detection/profiling agents are intentionally left for later tasks
    (A2/A3); the only logic verified here is that the crew builds with
    ``Process.hierarchical``.
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def manager(self) -> Agent:
        return Agent(config=self.agents_config["manager"], allow_delegation=True)

    @task
    def observe_task(self) -> Task:
        return Task(config=self.tasks_config["observe_task"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_llm="gpt-4o-mini",
            verbose=False,
        )
