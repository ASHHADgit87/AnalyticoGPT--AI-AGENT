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
    get_meaningful_numeric_columns,
    get_numeric_columns,
)
from tools.visualization_tools import (
    generate_bar_chart,
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
        chart_plan = self._select_chart_plan(cleaned_df, metric_column, feature_column)

        top_performers_df = (
            extract_top_performers(cleaned_df, metric_column, top_n=5)
            if metric_column
            else pd.DataFrame()
        )
        top_performers = top_performers_df.to_dict(orient="records")

        heatmap_path = ""
        if chart_plan.get("generate_heatmap") and correlation_matrix:
            heatmap_path = generate_correlation_heatmap(
                correlation_matrix, output_dir=self.chart_dir
            )

        trend_path = ""
        forecast_results: Dict[str, Any] = {}
        if (
            feature_column
            and metric_column
            and feature_column != metric_column
            and cleaned_df[feature_column].notna().any()
            and cleaned_df[metric_column].notna().any()
            and cleaned_df[feature_column].nunique() > 1
            and cleaned_df[metric_column].nunique() > 1
        ):
            try:
                if chart_plan.get("chart_type") == "bar":
                    trend_path = generate_bar_chart(
                        cleaned_df,
                        feature_column,
                        metric_column,
                        output_dir=self.chart_dir,
                    )
                else:
                    trend_path = generate_trend_line_chart(
                        cleaned_df,
                        feature_column,
                        metric_column,
                        output_dir=self.chart_dir,
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
        if "RD_Value" in df.columns:
            return "RD_Value"

        numeric_columns = get_numeric_columns(df)
        if not numeric_columns:
            for col in df.columns:
                if col.lower() == "rd_value":
                    return col
            return None

        preferred_names = ["score", "sales", "profit", "value", "amount", "revenue"]
        for preferred in preferred_names:
            for col in numeric_columns:
                if col.lower() == preferred or preferred in col.lower():
                    return col

        if "Score" in numeric_columns:
            return "Score"

        candidate_columns = []
        for col in numeric_columns:
            numeric_series = pd.to_numeric(df[col], errors="coerce").dropna()
            if numeric_series.empty:
                continue
            if numeric_series.nunique() > 1 and numeric_series.std(ddof=0) > 0:
                candidate_columns.append(col)

        if not candidate_columns:
            return numeric_columns[0]

        return max(
            candidate_columns,
            key=lambda col: (
                pd.to_numeric(df[col], errors="coerce").nunique(),
                abs(pd.to_numeric(df[col], errors="coerce").std(ddof=0)),
                abs(pd.to_numeric(df[col], errors="coerce").mean()),
            ),
        )

    def _choose_feature_column(
        self, df: pd.DataFrame, metric_column: Optional[str]
    ) -> Optional[str]:
        for col in df.columns:
            if col.lower() == "year" and col != metric_column:
                return col

        date_like_patterns = [
            "date",
            "datetime",
            "timestamp",
            "year",
            "month",
            "quarter",
            "day",
            "week",
            "time",
        ]

        for col in df.columns:
            if col == metric_column:
                continue

            lower_name = col.lower()
            if any(pattern in lower_name for pattern in date_like_patterns):
                parsed = pd.to_datetime(df[col], errors="coerce")
                if parsed.notna().sum() >= 2:
                    return col

            if pd.api.types.is_datetime64_any_dtype(df[col]):
                return col

        numeric_columns = get_numeric_columns(df)
        if not numeric_columns:
            return "index"

        useful_columns = [
            col
            for col in numeric_columns
            if col != metric_column and df[col].nunique() > 1
        ]
        if useful_columns:
            preferred_order = ["year", "month", "day", "date", "time", "index"]
            for preferred in preferred_order:
                for col in useful_columns:
                    if col.lower() == preferred:
                        return col

            return useful_columns[0]

        other_columns = [col for col in numeric_columns if col != metric_column]
        return other_columns[0] if other_columns else "index"

    def _is_time_like_column(self, df: pd.DataFrame, col: str) -> bool:
        if col in {"index", "Index"}:
            return True
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return True

        lower_name = col.lower()
        if any(
            token in lower_name
            for token in ["date", "time", "year", "month", "day", "week", "quarter"]
        ):
            return True

        parsed = pd.to_datetime(df[col], errors="coerce")
        return parsed.notna().sum() >= 2

    def _select_chart_plan(
        self,
        df: pd.DataFrame,
        metric_column: Optional[str],
        feature_column: Optional[str],
    ) -> Dict[str, Any]:
        meaningful_numeric_columns = get_meaningful_numeric_columns(df)
        generate_heatmap = len(meaningful_numeric_columns) >= 3

        chart_type = "line"
        if feature_column and metric_column and feature_column != metric_column:
            if self._is_time_like_column(df, feature_column):
                chart_type = "line"
            elif df[feature_column].nunique() <= 20:
                chart_type = "bar"
            else:
                chart_type = "bar"

        return {
            "chart_type": chart_type,
            "generate_heatmap": generate_heatmap,
            "metric_column": metric_column,
            "feature_column": feature_column,
        }

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

        stats_summary = "\n".join(
            [
                f"- {col}: mean={v['mean']:.2f}, min={v['min_value']:.2f}, max={v['max_value']:.2f}, std={v['std_dev']:.2f}"
                for col, v in descriptive_stats.items()
            ]
        )

        top_corr_pairs = []
        seen = set()
        for col_a, row in correlation_matrix.items():
            for col_b, val in row.items():
                if col_a != col_b and (col_b, col_a) not in seen:
                    top_corr_pairs.append((col_a, col_b, val))
                    seen.add((col_a, col_b))
        top_corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
        corr_summary = "\n".join(
            [f"- {a} vs {b}: r={v:.3f}" for a, b, v in top_corr_pairs[:6]]
        )

        top_perf_summary = "\n".join(
            [
                ", ".join([f"{k}={val}" for k, val in row.items()])
                for row in top_performers[:3]
            ]
        )

        prompt = (
            f"You are analyzing a real dataset. Here is the actual data:\n\n"
            f"**Metric column:** {metric_column}\n"
            f"**Feature column:** {feature_column}\n\n"
            f"**Descriptive Statistics:**\n{stats_summary}\n\n"
            f"**Top Correlations:**\n{corr_summary}\n\n"
            f"**Top Performers (sample rows):**\n{top_perf_summary}\n\n"
            f"Write a professional, specific, data-driven analytical narrative (3-5 paragraphs) "
            f"using the actual variable names and numbers above. Do not use placeholder brackets. "
            f"Highlight key patterns, strongest correlations, outliers, and actionable insights."
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
