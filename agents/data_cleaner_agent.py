from google.adk import Agent
from adk.adk_config import ADKConfig
from adk.agent_registry import AgentRegistry
from tools.cleaning_tools import drop_nulls, fill_numeric_defaults


class DataCleanerAgent:
    def __init__(self):
        self.agent = Agent(
            name="data_cleaner_agent",
            model=ADKConfig.MODEL_NAME,
            instruction="You normalize raw structured data frames, handle extreme outliers, repair missing rows, and eliminate target duplicates using processing scripts.",
            tools=[drop_nulls, fill_numeric_defaults],
        )
        AgentRegistry.register("data_cleaner_agent", self.agent)
