from google.adk import Agent
from adk.adk_config import ADKConfig
from adk.agent_registry import AgentRegistry
from tools.statistics_tools import (
    compute_descriptive_stats,
    generate_correlation_matrix,
)


class AnalystAgent:
    def __init__(self):
        self.agent = Agent(
            name="analyst_agent",
            model=ADKConfig.MODEL_NAME,
            instruction="You perform extensive standard quantitative data evaluation, extract linear dependency configurations, compute variances, and process statistical matrices.",
            tools=[compute_descriptive_stats, generate_correlation_matrix],
        )
        AgentRegistry.register("analyst_agent", self.agent)
