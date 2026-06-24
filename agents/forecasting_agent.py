from google.adk import Agent
from adk.adk_config import ADKConfig
from adk.agent_registry import AgentRegistry
from tools.forecasting_tools import compute_linear_extrapolation


class ForecastingAgent:
    def __init__(self):
        self.agent = Agent(
            name="forecasting_agent",
            model=ADKConfig.MODEL_NAME,
            instruction="You intercept trend records, execute projection algorithms, perform numerical regressions, and predict academic performance configurations over variables.",
            tools=[compute_linear_extrapolation],
        )
        AgentRegistry.register("forecasting_agent", self.agent)
