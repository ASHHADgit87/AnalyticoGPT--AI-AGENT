from google.adk import Agent
from adk.adk_config import ADKConfig
from adk.agent_registry import AgentRegistry
from tools.visualization_tools import (
    generate_correlation_heatmap,
    generate_trend_line_chart,
)


class VisualizationAgent:
    def __init__(self):
        self.agent = Agent(
            name="visualization_agent",
            model=ADKConfig.MODEL_NAME,
            instruction=(
                "You receive statistical data frames and output file references to construct presentation charts. "
                "If the dataset has fewer than two numeric columns, do not attempt to create a correlation heatmap. "
                "Choose a sensible x-axis and y-axis, and save figure assets directly to local storage."
            ),
            tools=[generate_correlation_heatmap, generate_trend_line_chart],
        )
        AgentRegistry.register("visualization_agent", self.agent)
