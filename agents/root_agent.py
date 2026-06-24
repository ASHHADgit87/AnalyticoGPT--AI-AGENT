from google.adk import Agent
from adk.adk_config import ADKConfig
from adk.workflows import AnalysisWorkflowBuilder
from adk.agent_registry import AgentRegistry


class RootOrchestrator:
    def __init__(self):
        ADKConfig.validate_config()
        self.agent = Agent(
            name="root_agent",
            model=ADKConfig.MODEL_NAME,
            instruction="You are the ultimate supervisor agent responsible for delegating exploratory data analysis tasks, validation tasks, and reporting to specialized pipeline sub-agents.",
        )
        AgentRegistry.register("root_agent", self.agent)

    def execute_full_pipeline(self, initial_input: str) -> str:
        pipeline = AnalysisWorkflowBuilder.build_sequential_pipeline()
        execution_context = pipeline.run(initial_input)
        return str(execution_context)
