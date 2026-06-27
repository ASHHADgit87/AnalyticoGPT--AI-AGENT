import pandas as pd
import numpy as np
from typing import Dict, Any, List


def _coerce_numeric_series(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")

    if pd.api.types.is_datetime64_any_dtype(series):
        return pd.Series(pd.NaT, index=series.index)

    cleaned = series.astype(str).str.replace(r"[^0-9.\-]", "", regex=True)
    return pd.to_numeric(cleaned, errors="coerce")


def _is_metadata_like_column(col_name: str) -> bool:
    lower_name = col_name.lower()
    ignored_tokens = [
        "year",
        "date",
        "time",
        "index",
        "id",
        "code",
        "footnote",
        "sample",
        "error",
        "status",
        "unit",
        "category",
        "breakdown",
        "variable",
    ]
    return any(token in lower_name for token in ignored_tokens)


def _is_meaningful_numeric_column(series: pd.Series, col_name: str) -> bool:
    if pd.api.types.is_datetime64_any_dtype(series):
        return False
    if _is_metadata_like_column(col_name):
        return False

    coerced = _coerce_numeric_series(series).dropna()
    return not coerced.empty and coerced.nunique() >= 2


def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    numeric_columns = []
    for col in df.columns:
        series = df[col]
        if pd.api.types.is_numeric_dtype(series) and _is_meaningful_numeric_column(
            series, col
        ):
            numeric_columns.append(col)
            continue

        if pd.api.types.is_datetime64_any_dtype(series):
            continue

        if _is_metadata_like_column(col):
            continue

        coerced = _coerce_numeric_series(series)
        if coerced.notna().sum() >= 2 and _is_meaningful_numeric_column(series, col):
            numeric_columns.append(col)
    return numeric_columns


def get_meaningful_numeric_columns(df: pd.DataFrame) -> List[str]:
    return get_numeric_columns(df)


def compute_descriptive_stats(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    numeric_columns = get_numeric_columns(df)
    stats_dict = {}
    for col in numeric_columns:
        numeric_series = _coerce_numeric_series(df[col]).dropna()
        if numeric_series.empty:
            continue
        stats_dict[col] = {
            "mean": float(numeric_series.mean()),
            "median": float(numeric_series.median()),
            "std_dev": float(numeric_series.std()) if len(numeric_series) > 1 else 0.0,
            "min_value": float(numeric_series.min()),
            "max_value": float(numeric_series.max()),
        }
    return stats_dict


def generate_correlation_matrix(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    numeric_columns = get_meaningful_numeric_columns(df)
    if len(numeric_columns) < 2:
        return {}

    numeric_df = pd.DataFrame(
        {col: _coerce_numeric_series(df[col]).astype(float) for col in numeric_columns}
    )
    if numeric_df.empty or len(numeric_df.columns) < 2:
        return {}
    corr_df = numeric_df.corr().fillna(0.0)
    return corr_df.to_dict()


def extract_top_performers(
    df: pd.DataFrame, metric_col: str, top_n: int = 3
) -> pd.DataFrame:
    if metric_col not in df.columns:
        return pd.DataFrame()
    return (
        df.sort_values(by=metric_col, ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
