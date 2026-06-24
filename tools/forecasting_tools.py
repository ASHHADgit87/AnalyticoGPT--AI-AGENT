import numpy as np
import pandas as pd
from typing import Dict, Any


def compute_linear_extrapolation(
    df: pd.DataFrame, x_col: str, y_col: str, steps: int = 5
) -> Dict[str, Any]:
    x_raw = df[x_col].dropna().values
    y_raw = df[y_col].dropna().values

    if len(x_raw) < 2:
        return {"coefficient_slope": 0.0, "y_intercept": 0.0, "predictions": []}

    slope, intercept = np.polyfit(x_raw, y_raw, 1)
    max_x = x_raw.max()

    future_x = np.linspace(max_x, max_x + (max_x * 0.4), steps)
    future_y = (slope * future_x) + intercept

    predictions = []
    for fx, fy in zip(future_x, future_y):
        predictions.append({x_col: float(fx), f"predicted_{y_col}": float(fy)})

    return {
        "coefficient_slope": float(slope),
        "y_intercept": float(intercept),
        "predictions": predictions,
    }
