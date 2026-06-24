from google import genai
from typing import Dict, Any, List
from adk.adk_config import ADKConfig


class GeminiService:
    def __init__(self):
        ADKConfig.validate_config()
        self.client = genai.Client(api_key=ADKConfig.API_KEY)
        self.model_name = ADKConfig.MODEL_NAME

    def generate_narrative_insights(
        self, statistical_summary: str, dataset_context: str
    ) -> str:
        system_instruction = "You are a professional principal data analyst who uncovers subtle hidden variances and produces precise summaries."
        prompt = f"""
        Context: {dataset_context}
        Data Analysis Summary:
        {statistical_summary}
        
        Synthesize detailed narrative insights, strategic trends, and actionable recommendations based strictly on the metrics provided.
        """
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={"system_instruction": system_instruction, "temperature": 0.2},
        )
        return response.text
