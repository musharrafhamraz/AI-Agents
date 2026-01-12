from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from linkedin_automation.tools.custom_tool import (
    LinkedInPublishTool,
    LinkedInAnalyticsTool,
    LinkedInEngagementTool,
    ImageGenerationTool
)


@CrewBase
class LinkedinAutomation():
    """LinkedinAutomation crew for autonomous LinkedIn profile/page management"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Agent definitions using YAML configuration
    @agent
    def content_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['content_strategist'], # type: ignore[index]
            verbose=True,
            allow_delegation=False
        )

    @agent
    def professional_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['professional_writer'], # type: ignore[index]
            verbose=True,
            allow_delegation=False
        )

    @agent
    def visual_designer(self) -> Agent:
        return Agent(
            config=self.agents_config['visual_designer'], # type: ignore[index]
            verbose=True,
            tools=[ImageGenerationTool()],
            allow_delegation=False
        )

    @agent
    def linkedin_publisher(self) -> Agent:
        return Agent(
            config=self.agents_config['linkedin_publisher'], # type: ignore[index]
            verbose=True,
            tools=[LinkedInPublishTool()],
            allow_delegation=False
        )

    @agent
    def engagement_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['engagement_analyst'], # type: ignore[index]
            verbose=True,
            tools=[LinkedInAnalyticsTool()],
            allow_delegation=False
        )

    # Task definitions using YAML configuration
    @task
    def industry_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['industry_research_task'], # type: ignore[index]
        )

    @task
    def content_creation_task(self) -> Task:
        return Task(
            config=self.tasks_config['content_creation_task'], # type: ignore[index]
        )

    @task
    def visual_design_task(self) -> Task:
        return Task(
            config=self.tasks_config['visual_design_task'], # type: ignore[index]
        )

    @task
    def content_review_task(self) -> Task:
        return Task(
            config=self.tasks_config['content_review_task'], # type: ignore[index]
        )

    @task
    def publishing_task(self) -> Task:
        return Task(
            config=self.tasks_config['publishing_task'], # type: ignore[index]
        )

    @task
    def analytics_task(self) -> Task:
        return Task(
            config=self.tasks_config['analytics_task'], # type: ignore[index]
            output_file='linkedin_analytics_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the LinkedinAutomation crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
