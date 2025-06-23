from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class TestGemini():
    """TestGemini crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    
    @agent
    def requirements_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['requirements_engineer'],
            verbose=True
        )

    @agent
    def test_case_designer(self) -> Agent:
        return Agent(
            config=self.agents_config['test_case_designer'],
            verbose=True
        )

    @agent
    def test_script_developer(self) -> Agent:
        return Agent(
            config=self.agents_config['test_script_developer'],
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    
    @task
    def requirements_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['requirements_analysis_task'],
        )

    @task
    def test_case_design_task(self) -> Task:
        return Task(
            config=self.tasks_config['test_case_design_task'],
        )

    @task
    def test_script_implementation_task(self) -> Task:
        return Task(
            config=self.tasks_config['test_script_implementation_task'],
            output_file='test_implementation.cpp'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the TestGemini crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )