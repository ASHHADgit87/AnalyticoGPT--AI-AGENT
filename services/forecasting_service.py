import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from models.analysis_result import AnalysisResult


class ForecastingService:
    def __init__(self, output_dir: str = "outputs/forecasts"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_linear_projection(
        self, df: pd.DataFrame, feature_col: str, target_col: str, steps: int = 5
    ) -> Tuple[str, Dict[str, Any]]:
        if feature_col not in df.columns or target_col not in df.columns:
            raise KeyError("Specified feature or target columns missing from DataFrame")

        x = df[feature_col].dropna().values
        y = df[target_col].dropna().values

        slope, intercept = np.polyfit(x, y, 1)
        last_val = x.max()
        future_x = np.linspace(last_val, last_val + (last_val * 0.3), steps)
        future_y = (slope * future_x) + intercept

        forecast_df = pd.DataFrame(
            {feature_col: future_x, f"predicted_{target_col}": future_y}
        )

        output_file_path = os.path.join(self.output_dir, f"forecast_{target_col}.csv")
        forecast_df.to_csv(output_file_path, index=False)

        metrics = {
            "coefficient_slope": float(slope),
            "y_intercept": float(intercept),
            "forecast_path": output_file_path,
            "predictions": forecast_df.to_dict(orient="records"),
        }
        return output_file_path, metrics
