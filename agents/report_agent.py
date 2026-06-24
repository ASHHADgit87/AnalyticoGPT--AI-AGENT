from google.adk import Agent
from adk.adk_config import ADKConfig
from adk.agent_registry import AgentRegistry
from tools.pdf_tools import export_pdf_document


class ReportAgent:
    def __init__(self):
        self.agent = Agent(
            name="report_agent",
            model=ADKConfig.MODEL_NAME,
            instruction="You consolidate visualization paths, metrics summary dicts, and textual insights into an exportable, corporate-grade PDF file asset configuration.",
            tools=[export_pdf_document],
        )
        AgentRegistry.register("report_agent", self.agent)
