from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from facebook_automation.tools.custom_tool import (
    FacebookPageListTool,
    FacebookPublishTool,
    FacebookPostEngagementTool,
    FacebookPageInsightsTool,
    FacebookUserContentTool,
    ImageGenerationTool,
    TrendSearchTool,
    WebScrapeTool
)


@CrewBase
class FacebookAutomation():
    """FacebookAutomation crew for autonomous Facebook Page management"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Agent definitions using YAML configuration
    @agent
    def content_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['content_strategist'], # type: ignore[index]
            verbose=True,
            allow_delegation=False  # Disable delegation to reduce token usage
        )

    @agent
    def creative_copywriter(self) -> Agent:
        return Agent(
            config=self.agents_config['creative_copywriter'], # type: ignore[index]
            verbose=True
        )

    @agent
    def visual_artist(self) -> Agent:
        return Agent(
            config=self.agents_config['visual_artist'], # type: ignore[index]
            verbose=True,
            tools=[ImageGenerationTool()]
        )

    @agent
    def social_media_publisher(self) -> Agent:
        return Agent(
            config=self.agents_config['social_media_publisher'], # type: ignore[index]
            verbose=True,
            tools=[FacebookPublishTool()]
        )

    @agent
    def community_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['community_analyst'], # type: ignore[index]
            verbose=True,
            tools=[FacebookPageInsightsTool()]
        )

    # Task definitions using YAML configuration
    @task
    def ideation_task(self) -> Task:
        return Task(
            config=self.tasks_config['ideation_task'], # type: ignore[index]
        )

    @task
    def drafting_task(self) -> Task:
        return Task(
            config=self.tasks_config['drafting_task'], # type: ignore[index]
        )

    @task
    def visualization_task(self) -> Task:
        return Task(
            config=self.tasks_config['visualization_task'], # type: ignore[index]
        )

    @task
    def review_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_task'], # type: ignore[index]
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
            output_file='facebook_analytics_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the FacebookAutomation crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
