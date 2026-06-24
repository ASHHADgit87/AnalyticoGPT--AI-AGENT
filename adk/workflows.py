from typing import Dict, Any
from google.adk import Workflow
from adk.agent_registry import AgentRegistry

class AnalysisWorkflowBuilder:
    @classmethod
    def build_sequential_pipeline(cls) -> Workflow:
        detector = AgentRegistry.get_agent("dataset_detector_agent")
        cleaner = AgentRegistry.get_agent("data_cleaner_agent")
        analyst = AgentRegistry.get_agent("analyst_agent")
        visualizer = AgentRegistry.get_agent("visualization_agent")
        forecaster = AgentRegistry.get_agent("forecasting_agent")
        insighter = AgentRegistry.get_agent("insight_agent")
        reporter = AgentRegistry.get_agent("report_agent")

        pipeline = Workflow(
            name="data_analysis_orchestration_flow",
            edges=[
                (detector, cleaner),
                (cleaner, analyst),
                (analyst, visualizer),
                (visualizer, forecaster),
                (forecaster, insighter),
                (insighter, reporter)
            ]
        )
        return pipeline