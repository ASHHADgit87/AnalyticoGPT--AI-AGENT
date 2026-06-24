import pandas as pd
import numpy as np


def drop_nulls(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna().reset_index(drop=True)


def fill_numeric_defaults(df: pd.DataFrame, default_val: float = 0.0) -> pd.DataFrame:
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df_filled = df.copy()
    df_filled[numeric_cols] = df_filled[numeric_cols].fillna(default_val)
    return df_filled


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df_copied = df.copy()
    df_copied.columns = (
        df_copied.columns.str.strip()
        .str.replace(" ", "_")
        .str.replace(r"[^\w]", "", regex=True)
    )
    return df_copied
