from pydantic import BaseModel, Field
from typing import List, Dict, Any


class ReportSection(BaseModel):
    title: str
    content: str
    associated_chart_path: Optional[str] = None


class ReportModel(BaseModel):
    report_id: str
    title: str
    author: str = "AnalyticoGPT AI Agent"
    generated_at: str
    executive_summary: str
    sections: List[ReportSection] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    output_pdf_path: str
