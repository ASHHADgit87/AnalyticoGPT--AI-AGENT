import os
from typing import Any, Dict, List, Optional

import pandas as pd

from services.dataset_service import DatasetService
from tools.cleaning_tools import fill_numeric_defaults, standardize_column_names
from tools.forecasting_tools import compute_linear_extrapolation
from tools.pdf_tools import compile_structural_pdf
from tools.statistics_tools import (
    build_chart_plan,
    compute_descriptive_stats,
    compute_data_quality_score,
    extract_top_performers,
    extract_performer_analysis,
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


def _run_forecasting(
    analysis_df: pd.DataFrame,
    trend_x: str,
    primary_metric: str,
    steps: int = 5,
) -> Dict[str, Any]:
    """
    Run all available forecasting methods and return a unified result dict.

    Methods attempted (in order of sophistication):
      1. Holt's double exponential smoothing  (trend-aware, no seasonal)
      2. Simple exponential smoothing          (baseline smoothing)
      3. Linear extrapolation                  (original fallback)

    Each method is tried independently; if it fails, the next is used.
    The final result includes forecasts from every method that succeeded,
    plus a 'best_method' label pointing to the most sophisticated successful one.
    """
    results: Dict[str, Any] = {"methods": {}, "best_method": None, "error": None}

    work = analysis_df[[trend_x, primary_metric]].copy()
    work[primary_metric] = pd.to_numeric(
        work[primary_metric]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace(r"[^0-9.\-]", "", regex=True),
        errors="coerce",
    )
    work = work.dropna().sort_values(trend_x).reset_index(drop=True)
    y = work[primary_metric].values

    if len(y) < 4:
        results["error"] = "Insufficient data points for forecasting (need ≥ 4)."
        return results

    last_x = work[trend_x].iloc[-1]
    try:
        from statsmodels.tsa.holtwinters import Holt

        holt_model = Holt(y, exponential=False, damped_trend=True).fit(
            optimized=True, remove_bias=True
        )
        holt_forecast = holt_model.forecast(steps).tolist()
        results["methods"]["holt"] = {
            "label": "Holt's Double Exponential Smoothing (damped)",
            "forecast": holt_forecast,
            "steps": steps,
        }
        results["best_method"] = "holt"
    except Exception:
        pass
    try:
        from statsmodels.tsa.holtwinters import SimpleExpSmoothing

        ses_model = SimpleExpSmoothing(y).fit(optimized=True, remove_bias=True)
        ses_forecast = ses_model.forecast(steps).tolist()
        results["methods"]["simple_exp"] = {
            "label": "Simple Exponential Smoothing",
            "forecast": ses_forecast,
            "steps": steps,
        }
        if results["best_method"] is None:
            results["best_method"] = "simple_exp"
    except Exception:
        pass

    try:
        lin_result = compute_linear_extrapolation(
            analysis_df, trend_x, primary_metric, steps=steps
        )
        results["methods"]["linear"] = {
            "label": "Linear Extrapolation (OLS)",
            "forecast": lin_result.get("forecast", []),
            "steps": steps,
            "r_squared": lin_result.get("r_squared"),
        }
        if results["best_method"] is None:
            results["best_method"] = "linear"
    except Exception:
        pass

    if not results["methods"]:
        results["error"] = "All forecasting methods failed."

    return results


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

        quality_report = compute_data_quality_score(cleaned_df)
        plan = build_chart_plan(cleaned_df)
        analysis_df = plan["analysis_df"]
        active_unit = plan["active_unit"]
        primary_metric = plan["primary_metric"]
        time_col = plan["time_col"]
        categorical_col = plan["categorical_col"]

        corr_method = plan.get("correlation_method", "pearson")
        corr_method_label = corr_method.capitalize()

        descriptive_stats = compute_descriptive_stats(analysis_df)
        correlation_matrix = generate_correlation_matrix(
            analysis_df, method=corr_method
        )

        performer_analysis: Dict[str, Any] = {}
        top_performers_df = pd.DataFrame()
        top_performers: List[Dict] = []

        if primary_metric:
            performer_analysis = extract_performer_analysis(
                analysis_df, primary_metric, top_n=5
            )
            top_performers = performer_analysis.get("top", [])
            top_performers_df = pd.DataFrame(top_performers)

        heatmap_path = ""
        trend_path = ""
        bar_path = ""
        forecast_results: Dict[str, Any] = {}

        if plan["generate_heatmap"] and correlation_matrix:
            heatmap_path = generate_correlation_heatmap(
                correlation_matrix,
                output_dir=self.chart_dir,
                method_label=corr_method_label,
            )

        if plan["generate_trend"] and primary_metric and plan["trend_x"]:
            trend_x = plan["trend_x"]
            if (
                trend_x in analysis_df.columns
                and primary_metric in analysis_df.columns
                and analysis_df[trend_x].nunique() >= 2
            ):
                trend_path = generate_trend_line_chart(
                    analysis_df,
                    trend_x,
                    primary_metric,
                    output_dir=self.chart_dir,
                    unit_label=active_unit,
                    show_confidence_interval=True,
                )
                forecast_results = _run_forecasting(
                    analysis_df, trend_x, primary_metric, steps=5
                )

        if plan["generate_bar"] and primary_metric and plan["bar_x"]:
            bar_x = plan["bar_x"]
            if bar_x in analysis_df.columns and primary_metric in analysis_df.columns:
                try:
                    skew_val = abs(float(analysis_df[primary_metric].dropna().skew()))
                    agg = "median" if skew_val > 1.0 else "mean"
                except Exception:
                    agg = "mean"

                bar_path = generate_bar_chart(
                    analysis_df,
                    bar_x,
                    primary_metric,
                    output_dir=self.chart_dir,
                    unit_label=active_unit,
                    aggregation=agg,
                )

        insight_text = self._build_insights_text(
            descriptive_stats=descriptive_stats,
            correlation_matrix=correlation_matrix,
            top_performers=top_performers,
            performer_analysis=performer_analysis,
            feature_column=time_col or plan.get("feature_col"),
            metric_column=primary_metric,
            active_unit=active_unit,
            plan=plan,
            corr_method_label=corr_method_label,
            quality_report=quality_report,
            forecast_results=forecast_results,
            heatmap_generated=bool(heatmap_path),
            trend_generated=bool(trend_path),
            bar_generated=bool(bar_path),
        )

        pdf_path = compile_structural_pdf(
            target_path=os.path.join(
                self.report_dir, f"report_{os.path.splitext(file_name)[0]}.pdf"
            ),
            title="AnalyticoGPT Pipeline Data Analysis Report",
            summary=insight_text,
            records=top_performers,
            quality_report=quality_report,
        )

        metadata.summary_statistics = descriptive_stats

        return {
            "metadata": metadata,
            "cleaned_path": cleaned_path,
            "descriptive_stats": descriptive_stats,
            "correlation_matrix": correlation_matrix,
            "top_performers": top_performers,
            "performer_analysis": performer_analysis,
            "heatmap_path": heatmap_path,
            "trend_path": trend_path,
            "bar_path": bar_path,
            "forecast_results": forecast_results,
            "insight_text": insight_text,
            "report_path": pdf_path,
            "quality_report": quality_report,
            "primary_metric": primary_metric,
            "time_col": time_col,
            "categorical_col": categorical_col,
            "active_unit": active_unit,
            "corr_method_label": corr_method_label,
            "mixed_units_detected": plan.get("mixed_units_detected", False),
            "metric_cols": plan.get("metric_cols", []),
        }

    def _build_insights_text(
        self,
        descriptive_stats: Dict[str, Any],
        correlation_matrix: Dict[str, Any],
        top_performers: List[Dict[str, Any]],
        performer_analysis: Dict[str, Any],
        feature_column: Optional[str],
        metric_column: Optional[str],
        active_unit: str = "",
        plan: Optional[Dict] = None,
        corr_method_label: str = "Pearson",
        quality_report: Optional[Dict[str, Any]] = None,
        forecast_results: Optional[Dict[str, Any]] = None,
        heatmap_generated: bool = False,
        trend_generated: bool = False,
        bar_generated: bool = False,
    ) -> str:
        summary = ["### Dataset Summary"]
        summary.append(
            f"* Processed numeric fields: {', '.join(descriptive_stats.keys()) or 'none'}"
        )
        summary.append(f'* Selected metric column: {metric_column or "not available"}')
        summary.append(
            f'* Selected feature column: {feature_column or "not available"}'
        )
        summary.append(f"* Correlation method used: **{corr_method_label}**")
        if active_unit:
            summary.append(f"* Analysis unit: **{active_unit}** (mixed units isolated)")
        if plan and plan.get("mixed_units_detected"):
            summary.append(
                "* Mixed units detected in value column — analysis restricted to dominant unit type"
            )
        if plan and plan.get("is_long_format"):
            summary.append(
                "* Dataset was in long format — pivoted to wide format for multi-metric analysis"
            )
        summary.append(f"* Top performers loaded: {len(top_performers)} rows")

        if quality_report:
            q = quality_report
            summary.append(
                f'\n### Data Quality Report  {q["star_str"]}  Score: {q["score"]}/100  [{q["badge"]}]'
            )
            summary.append(f'* Missing values: {q["missing_pct"]}%')
            summary.append(f'* Duplicate rows: {q["duplicate_pct"]}%')
            summary.append(f'* Outlier ratio: {q["outlier_pct"]}%')
            summary.append(f'* Average skewness: {q["avg_skewness"]}')
            bd = q["breakdown"]
            summary.append(
                f'* Dimension scores — Completeness: {bd["completeness"]}, '
                f'Uniqueness: {bd["uniqueness"]}, '
                f'Outlier: {bd["outlier"]}, '
                f'Consistency: {bd["consistency"]}, '
                f'Skewness: {bd["skewness"]}'
            )

        stats_lines = []
        for col, v in descriptive_stats.items():
            line = (
                f'- {col}: mean={v["mean"]:.2f}, median={v["median"]:.2f}, '
                f'min={v["min_value"]:.2f}, max={v["max_value"]:.2f}, std={v["std_dev"]:.2f}'
            )
            if "skewness" in v:
                line += f', skew={v["skewness"]:.2f}'
            if "kurtosis" in v:
                line += f', kurt={v["kurtosis"]:.2f}'
            stats_lines.append(line)
        stats_summary = "\n".join(stats_lines)

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

        bottom_performers = performer_analysis.get("bottom", [])
        growth_leaders = performer_analysis.get("growth", [])
        bottom_perf_summary = (
            "\n".join(
                [
                    ", ".join([f"{k}={val}" for k, val in row.items()])
                    for row in bottom_performers[:3]
                ]
            )
            if bottom_performers
            else "N/A"
        )
        growth_summary = (
            "\n".join(
                [
                    ", ".join([f"{k}={val}" for k, val in row.items()])
                    for row in growth_leaders[:3]
                ]
            )
            if growth_leaders
            else "N/A"
        )

        forecast_summary = "Not available."
        if forecast_results and forecast_results.get("best_method"):
            best = forecast_results["best_method"]
            method_data = forecast_results["methods"].get(best, {})
            label = method_data.get("label", best)
            fcast_vals = method_data.get("forecast", [])
            if fcast_vals:
                forecast_summary = (
                    f"Method: {label}\n"
                    f"Next {len(fcast_vals)} steps forecast: "
                    + ", ".join([f"{v:.2f}" for v in fcast_vals])
                )

        chart_context = []
        if heatmap_generated:
            chart_context.append("Correlation heatmap was generated.")
        if trend_generated:
            chart_context.append("Trend line chart was generated with OLS 95% CI.")
        if bar_generated:
            chart_context.append("Bar chart was generated.")
        chart_context_str = (
            " ".join(chart_context) if chart_context else "No charts generated."
        )

        quality_context = ""
        if quality_report:
            q = quality_report
            quality_context = (
                f'Dataset quality score: {q["score"]}/100 ({q["badge"]}). '
                f'Missing: {q["missing_pct"]}%, Duplicates: {q["duplicate_pct"]}%, '
                f'Outliers: {q["outlier_pct"]}%, Avg skewness: {q["avg_skewness"]}.'
            )

        unit_context = f" All values are in {active_unit}." if active_unit else ""
        prompt = (
            f"You are analyzing a real dataset.{unit_context} Here is the full data context:\n\n"
            f"**Metric column:** {metric_column}\n"
            f"**Feature column:** {feature_column}\n"
            f"**Correlation method:** {corr_method_label}\n\n"
            f"**Data Quality:** {quality_context}\n\n"
            f"**Descriptive Statistics (with skewness and kurtosis):**\n{stats_summary}\n\n"
            f"**Top Correlations:**\n{corr_summary}\n\n"
            f"**Top Performers:**\n{top_perf_summary}\n\n"
            f"**Bottom Performers:**\n{bottom_perf_summary}\n\n"
            f"**Top Growth Leaders:**\n{growth_summary}\n\n"
            f"**Forecast Summary:**\n{forecast_summary}\n\n"
            f"**Charts Generated:** {chart_context_str}\n\n"
            f"Write a professional, specific, data-driven analytical narrative (4–6 paragraphs) "
            f"using the actual variable names and numbers above. Do not use placeholder brackets. "
            f"Do not use any markdown symbols like **, *, ##, or # in your response. "
            f"Write in plain professional prose only. "
            f"Highlight key patterns, strongest correlations, outliers, data quality issues, "
            f"forecast direction, top and bottom performers, and actionable insights. "
            f"Reference skewness and kurtosis where relevant. "
            f"Comment on any data quality concerns that might affect interpretation."
        )

        if not ADKConfig.API_KEY:
            summary.append(
                "\nAI insights not available because GOOGLE_API_KEY is not configured."
            )
            return "\n".join(summary)

        try:
            ai_output = fetch_gemini_structural_completion(
                prompt,
                system_instruction="You are a professional data analyst. Never use markdown symbols like **, *, #, or ## in your response. Write in plain prose only.",
            )
            return "\n".join(summary + ["### AI Narrative Insights", ai_output])
        except Exception:
            summary.append("\nAI engine failed to produce a narrative summary.")
            return "\n".join(summary)
