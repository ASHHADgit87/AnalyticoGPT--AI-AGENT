from google.adk import Agent
from adk.adk_config import ADKConfig
from adk.agent_registry import AgentRegistry
from tools.visualization_tools import render_bar_chart, render_scatter_matrix


class VisualizationAgent:
    def __init__(self):
        self.agent = Agent(
            name="visualization_agent",
            model=ADKConfig.MODEL_NAME,
            instruction="You receive statistical data frames and output file references to construct presentation charts, saving visual figure assets directly to local storage.",
            tools=[render_bar_chart, render_scatter_matrix],
        )
        AgentRegistry.register("visualization_agent", self.agent)
