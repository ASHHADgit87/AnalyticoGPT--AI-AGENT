from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ColumnSchema(BaseModel):
    name: str
    data_type: str
    is_nullable: bool
    unique_values_count: int
    missing_percentage: float


class DatasetMetadata(BaseModel):
    file_name: str
    file_path: str
    file_size_bytes: int
    row_count: int
    column_count: int
    columns: List[ColumnSchema] = Field(default_factory=list)
    detected_delimiters: str = ","
    encoding: str = "utf-8"
    summary_statistics: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
