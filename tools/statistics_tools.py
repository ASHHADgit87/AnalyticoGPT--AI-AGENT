import pandas as pd
import numpy as np
from typing import Dict, Any, List


def compute_descriptive_stats(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    numeric_df = df.select_dtypes(include=[np.number])
    stats_dict = {}
    for col in numeric_df.columns:
        stats_dict[col] = {
            "mean": float(numeric_df[col].mean()),
            "median": float(numeric_df[col].median()),
            "std_dev": float(numeric_df[col].std()) if len(numeric_df) > 1 else 0.0,
            "min_value": float(numeric_df[col].min()),
            "max_value": float(numeric_df[col].max()),
        }
    return stats_dict


def generate_correlation_matrix(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty:
        return {}
    corr_df = numeric_df.corr().fillna(0.0)
    return corr_df.to_dict()


def extract_top_performers(
    df: pd.DataFrame, metric_col: str, top_n: int = 3
) -> List[Dict[str, Any]]:
    if metric_col not in df.columns:
        return []
    sorted_df = df.sort_values(by=metric_col, ascending=False).head(top_n)
    return sorted_df.to_dict(orient="records")
