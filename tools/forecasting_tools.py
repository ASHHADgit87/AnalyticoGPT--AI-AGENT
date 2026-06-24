import numpy as np
import pandas as pd
from typing import Dict, Any


def compute_linear_extrapolation(
    df: pd.DataFrame, x_col: str, y_col: str, steps: int = 5
) -> Dict[str, Any]:
    x_raw = df[x_col].dropna().values
    y_raw = df[y_col].dropna().values

    if len(x_raw) < 2:
        return {
            "coefficient_slope": 0.0,
            "y_intercept": 0.0,
            "predictions": pd.DataFrame(columns=[x_col, y_col]),
        }

    slope, intercept = np.polyfit(x_raw, y_raw, 1)
    max_x = x_raw.max()
    step_size = (x_raw.max() - x_raw.min()) / (len(x_raw) - 1)

    future_x = [max_x + step_size * (i + 1) for i in range(steps)]
    future_y = [slope * xi + intercept for xi in future_x]

    return {
        "coefficient_slope": float(slope),
        "y_intercept": float(intercept),
        "predictions": pd.DataFrame({x_col: future_x, y_col: future_y}),
    }
