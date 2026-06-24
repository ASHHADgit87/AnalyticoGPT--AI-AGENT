from google.adk import Agent
from adk.adk_config import ADKConfig
from adk.agent_registry import AgentRegistry
from tools.gemini_tools import synthesize_analytical_narrative


class InsightAgent:
    def __init__(self):
        self.agent = Agent(
            name="insight_agent",
            model=ADKConfig.MODEL_NAME,
            instruction="You interpret raw correlation matrices and numerical outputs to distill logical observations, highlight hidden variance factors, and produce high-level text explanations.",
            tools=[synthesize_analytical_narrative],
        )
        AgentRegistry.register("insight_agent", self.agent)
