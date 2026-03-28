import os
from pathlib import Path

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

@CrewBase
class Demo():
    """Demo crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    def _agent_skill_source(self, agent_name: str) -> TextFileKnowledgeSource:
        skills_root = Path(__file__).resolve().parents[1] / "skills"
        return TextFileKnowledgeSource(
            file_paths=[
                skills_root / agent_name / "skills.md",
            ]
        )

    def _llm(self) -> LLM:
        model = os.getenv("MODEL")
        base_url = os.getenv("OPENAI_BASE_URL")
        api_key = os.getenv("OPENAI_API_KEY")

        if not model:
            raise ValueError("MODEL is missing from environment.")
        if not base_url:
            raise ValueError("OPENAI_BASE_URL is missing from environment.")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing from environment.")

        return LLM(
            model=model,
            base_url=base_url,
            api_key=api_key,
        )

    @agent
    def business_analytics(self) -> Agent:
        return Agent(
            config=self.agents_config['business_analytics'], # type: ignore[index]
            llm=self._llm(),
            knowledge_sources=[self._agent_skill_source("business_analytics")],
            verbose=True
        )

    @agent
    def frontend_developer(self) -> Agent:
        return Agent(
            config=self.agents_config['frontend_developer'], # type: ignore[index]
            llm=self._llm(),
            knowledge_sources=[self._agent_skill_source("frontend_developer")],
            verbose=True
        )

    @agent
    def manual_tester(self) -> Agent:
        return Agent(
            config=self.agents_config['manual_tester'], # type: ignore[index]
            llm=self._llm(),
            knowledge_sources=[self._agent_skill_source("manual_tester")],
            verbose=True
        )

    @task
    def business_analytics_task(self) -> Task:
        return Task(
            config=self.tasks_config['business_analytics_task'], # type: ignore[index]
        )

    @task
    def frontend_developer_task(self) -> Task:
        return Task(
            config=self.tasks_config['frontend_developer_task'], # type: ignore[index]
        )

    @task
    def manual_tester_task(self) -> Task:
        return Task(
            config=self.tasks_config['manual_tester_task'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Demo crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

    def business_analytics_crew(self) -> Crew:
        return Crew(
            agents=[self.business_analytics()],
            tasks=[self.business_analytics_task()],
            process=Process.sequential,
            verbose=True,
        )

    def frontend_developer_crew(self) -> Crew:
        return Crew(
            agents=[self.frontend_developer()],
            tasks=[self.frontend_developer_task()],
            process=Process.sequential,
            verbose=True,
        )

    def manual_tester_crew(self) -> Crew:
        return Crew(
            agents=[self.manual_tester()],
            tasks=[self.manual_tester_task()],
            process=Process.sequential,
            verbose=True,
        )
