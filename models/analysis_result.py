from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class SummaryMetric(BaseModel):
    mean: Optional[float] = None
    median: Optional[float] = None
    std_dev: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class AnalysisResult(BaseModel):
    dataset_id: str
    descriptive_stats: Dict[str, SummaryMetric] = Field(default_factory=dict)
    correlation_matrix: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    top_performers: List[Dict[str, Any]] = Field(default_factory=list)
    detected_anomalies: List[Dict[str, Any]] = Field(default_factory=list)
    execution_time_seconds: float
