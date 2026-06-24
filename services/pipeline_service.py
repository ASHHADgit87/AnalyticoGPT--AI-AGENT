import os
from typing import Any, Dict, List, Optional

import pandas as pd

from models.dataset_metadata import DatasetMetadata
from services.dataset_service import DatasetService
from tools.cleaning_tools import fill_numeric_defaults, standardize_column_names
from tools.forecasting_tools import compute_linear_extrapolation
from tools.pdf_tools import compile_structural_pdf
from tools.statistics_tools import (
    compute_descriptive_stats,
    extract_top_performers,
    generate_correlation_matrix,
)
from tools.visualization_tools import (
    generate_correlation_heatmap,
    generate_trend_line_chart,
)
from tools.gemini_tools import fetch_gemini_structural_completion
from adk.adk_config import ADKConfig


class PipelineService:
    def __init__(
        self,
        upload_dir: str = "data/uploads",
        clean_dir: str = "data/cleaned",
        chart_dir: str = "outputs/charts",
        report_dir: str = "outputs/reports",
    ):
        self.dataset_service = DatasetService(
            upload_dir=upload_dir, clean_dir=clean_dir
        )
        self.chart_dir = chart_dir
        self.report_dir = report_dir
        os.makedirs(self.chart_dir, exist_ok=True)
        os.makedirs(self.report_dir, exist_ok=True)

    def run_full_pipeline(self, file_name: str, file_bytes: bytes) -> Dict[str, Any]:
        metadata = self.dataset_service.process_and_profile_upload(
            file_name, file_bytes
        )
        df = pd.read_csv(metadata.file_path)

        cleaned_df = standardize_column_names(df)
        cleaned_df = fill_numeric_defaults(cleaned_df)
        cleaned_path = self.dataset_service.save_cleaned_dataset(cleaned_df, file_name)

        descriptive_stats = compute_descriptive_stats(cleaned_df)
        correlation_matrix = generate_correlation_matrix(cleaned_df)

        metric_column = self._choose_metric_column(cleaned_df)
        feature_column = self._choose_feature_column(cleaned_df, metric_column)

        top_performers_df = (
            extract_top_performers(cleaned_df, metric_column, top_n=5)
            if metric_column
            else pd.DataFrame()
        )
        top_performers = top_performers_df.to_dict(orient="records")

        heatmap_path = ""
        if correlation_matrix:
            heatmap_path = generate_correlation_heatmap(
                correlation_matrix, output_dir=self.chart_dir
            )

        trend_path = ""
        forecast_results: Dict[str, Any] = {}
        if feature_column and metric_column and feature_column != metric_column:
            try:
                trend_path = generate_trend_line_chart(
                    cleaned_df, feature_column, metric_column, output_dir=self.chart_dir
                )
                forecast_results = compute_linear_extrapolation(
                    cleaned_df, feature_column, metric_column, steps=5
                )
            except Exception:
                forecast_results = {
                    "error": "Unable to generate forecast for the selected columns."
                }

        insight_text = self._build_insights_text(
            descriptive_stats,
            correlation_matrix,
            top_performers,
            feature_column,
            metric_column,
        )
        pdf_path = compile_structural_pdf(
            target_path=os.path.join(
                self.report_dir, f"report_{os.path.splitext(file_name)[0]}.pdf"
            ),
            title="AnalyticoGPT Pipeline Data Analysis Report",
            summary=insight_text,
            records=top_performers,
        )

        metadata.summary_statistics = descriptive_stats

        return {
            "metadata": metadata,
            "cleaned_path": cleaned_path,
            "descriptive_stats": descriptive_stats,
            "correlation_matrix": correlation_matrix,
            "top_performers": top_performers,
            "heatmap_path": heatmap_path,
            "trend_path": trend_path,
            "forecast_results": forecast_results,
            "insight_text": insight_text,
            "report_path": pdf_path,
        }

    def _choose_metric_column(self, df: pd.DataFrame) -> Optional[str]:
        numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
        if not numeric_columns:
            return None
        return "Score" if "Score" in numeric_columns else numeric_columns[-1]

    def _choose_feature_column(
        self, df: pd.DataFrame, metric_column: Optional[str]
    ) -> Optional[str]:
        numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
        if not numeric_columns:
            return None
        if metric_column and metric_column in numeric_columns:
            other_columns = [col for col in numeric_columns if col != metric_column]
            if other_columns:
                return other_columns[0]
        return numeric_columns[0]

    def _build_insights_text(
        self,
        descriptive_stats: Dict[str, Any],
        correlation_matrix: Dict[str, Any],
        top_performers: List[Dict[str, Any]],
        feature_column: Optional[str],
        metric_column: Optional[str],
    ) -> str:
        summary = ["### Dataset Summary"]
        summary.append(
            f"* Processed numeric fields: {', '.join(descriptive_stats.keys()) or 'none'}"
        )
        summary.append(f"* Selected metric column: {metric_column or 'not available'}")
        summary.append(
            f"* Selected feature column: {feature_column or 'not available'}"
        )
        summary.append(f"* Top performers loaded: {len(top_performers)} rows")

        prompt = (
            "Based on the cleaned dataset, descriptive statistics, and correlation matrix, "
            "write a concise analytical summary and highlight the most important patterns."
        )
        if not ADKConfig.API_KEY:
            summary.append(
                "\nAI insights not available because GOOGLE_API_KEY is not configured."
            )
            return "\n".join(summary)

        try:
            ai_output = fetch_gemini_structural_completion(
                prompt, system_instruction="You are a professional analyst."
            )
            return "\n".join(summary + ["### AI Narrative Insights", ai_output])
        except Exception as exc:
            summary.append(
                "\nAI engine failed to produce a narrative summary. See error details in logs."
            )
            return "\n".join(summary)
