import os
import pandas as pd
from typing import Dict, Any


def read_and_validate_csv(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Target CSV reference missing at path: {file_path}")
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            raise ValueError(
                "Target file parsing completed but DataFrame context is empty."
            )
        return df
    except Exception as e:
        raise RuntimeError(f"CSV Ingestion Subsystem failure: {str(e)}")


def export_dataframe_to_csv(df: pd.DataFrame, target_path: str) -> str:
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    df.to_csv(target_path, index=False)
    return target_path
