from google.adk import Agent
from adk.adk_config import ADKConfig
from adk.agent_registry import AgentRegistry
from tools.csv_tools import inspect_csv_schema


class DatasetDetectorAgent:
    def __init__(self):
        self.agent = Agent(
            name="dataset_detector_agent",
            model=ADKConfig.MODEL_NAME,
            instruction="You analyze raw tabular inputs, discover structural properties, detect encoding anomalies, and inspect column datatypes using systemic schema tools.",
            tools=[inspect_csv_schema],
        )
        AgentRegistry.register("dataset_detector_agent", self.agent)
