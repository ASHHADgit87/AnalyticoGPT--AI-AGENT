import os
import pandas as pd
from typing import Optional, Dict, Any
from models.dataset_metadata import DatasetMetadata, ColumnSchema


class DatasetService:
    def __init__(
        self, upload_dir: str = "data/uploads", clean_dir: str = "data/cleaned"
    ):
        self.upload_dir = upload_dir
        self.clean_dir = clean_dir
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.clean_dir, exist_ok=True)

    def process_and_profile_upload(
        self, file_name: str, file_content: bytes
    ) -> DatasetMetadata:
        target_path = os.path.join(self.upload_dir, file_name)
        with open(target_path, "wb") as f:
            f.write(file_content)
        df = pd.read_csv(target_path)
        file_size = os.path.getsize(target_path)

        column_schemas = []
        for col in df.columns:
            column_schemas.append(
                ColumnSchema(
                    name=str(col),
                    data_type=str(df[col].dtype),
                    is_nullable=bool(df[col].isnull().any()),
                    unique_values_count=int(df[col].nunique()),
                    missing_percentage=float((df[col].isnull().sum() / len(df)) * 100),
                )
            )

        return DatasetMetadata(
            file_name=file_name,
            file_path=target_path,
            file_size_bytes=file_size,
            row_count=len(df),
            column_count=len(df.columns),
            columns=column_schemas,
        )

    def save_cleaned_dataset(self, df: pd.DataFrame, file_name: str) -> str:
        clean_path = os.path.join(self.clean_dir, f"cleaned_{file_name}")
        df.to_csv(clean_path, index=False)
        return clean_path
