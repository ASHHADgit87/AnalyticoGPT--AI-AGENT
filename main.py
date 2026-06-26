import os
import sys
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from models.dataset_metadata import DatasetMetadata
from models.analysis_result import AnalysisResult
from models.report_model import ReportModel

from tools.csv_tools import read_and_validate_csv
from tools.cleaning_tools import standardize_column_names, fill_numeric_defaults
from tools.statistics_tools import (
    compute_descriptive_stats,
    generate_correlation_matrix,
    extract_top_performers,
)
from tools.visualization_tools import (
    generate_correlation_heatmap,
    generate_trend_line_chart,
)
from tools.forecasting_tools import compute_linear_extrapolation
from tools.pdf_tools import compile_structural_pdf
from tools.gemini_tools import fetch_gemini_structural_completion

from adk.agent_registry import AgentRegistry
from adk.agent_router import AgentRouter
from adk.workflows import ExecutionPipelineWorkflow


def run_headless_orchestration_pipeline(input_csv_path: str):
    print("Initializing AnalyticoGPT Core Subsystem Infrastructure Engine...")

    raw_df = read_and_validate_csv(input_csv_path)
    cleaned_df = standardize_column_names(raw_df)
    cleaned_df = fill_numeric_defaults(cleaned_df, default_val=0.0)

    clean_csv_path = "data/cleaned/headless_sync_dataset.csv"
    os.makedirs("data/cleaned", exist_ok=True)
    cleaned_df.to_csv(clean_csv_path, index=False)
    print(f"Dataset standardization executed successfully -> Saved: {clean_csv_path}")

    stats = compute_descriptive_stats(cleaned_df)
    corr_matrix = generate_correlation_matrix(cleaned_df)

    target_metric = (
        "Score"
        if "Score" in cleaned_df.columns
        else cleaned_df.select_dtypes(include=["number"]).columns
    )
    top_performers = extract_top_performers(
        cleaned_df, metric_col=target_metric, top_n=3
    )

    heatmap_path = generate_correlation_heatmap(corr_matrix)
    if heatmap_path:
        print(f"Analytics Visualization Core Synced. Exported: {heatmap_path}")
    else:
        print(
            "Heatmap skipped: insufficient meaningful numeric columns for correlation analysis."
        )

    feature_col = (
        "Hours_Studied"
        if "Hours_Studied" in cleaned_df.columns
        else cleaned_df.select_dtypes(include=["number"]).columns[-1]
    )
    forecast_results = compute_linear_extrapolation(
        cleaned_df, x_col=feature_col, y_col=target_metric, steps=5
    )

    statistical_context_dump = f"""
    Dataset Columns: {list(cleaned_df.columns)}
    Descriptive Summary: {stats}
    Correlation Matrices: {corr_matrix}
    Top Contextual Rows: {top_performers}
    Linear Projection Path: {forecast_results['predictions']}
    """

    system_instruction = "You are a lead enterprise AI analytics supervisor orchestrating a complex dataset pipeline run report structure."
    prompt = f"Synthesize structural execution data overview notes for the board of directors based on this running runtime metric block:\n{statistical_context_dump}"

    narrative_summary = fetch_gemini_structural_completion(prompt, system_instruction)
    print("\nExecutive AI Assessment Delivered:")
    print(narrative_summary)

    pdf_out = "outputs/reports/executive_pipeline_run_summary.pdf"
    compile_structural_pdf(
        target_path=pdf_out,
        title="AnalyticoGPT Framework Engine Operational Run Summary",
        summary=narrative_summary,
        records=top_performers,
    )
    print(f"Generated Hardcopy PDF Master Report Record Document -> {pdf_out}")
    print("Fully synchronized pipeline operations finished without exceptions.")


if __name__ == "__main__":
    sample_data_path = "Sample.csv"
    if not os.path.exists(sample_data_path):
        dummy_df = pd.DataFrame(
            {
                "Age": [20, 22, 21, 23, 22, 24, 21],
                "Score": [88, 95, 90, 85, 92, 87, 93],
                "Hours_Studied": [5, 10, 8, 6, 9, 7, 11],
                "Name": ["Hina", "Ahmed", "Zain", "Usman", "Hina", "Ali", "Ayesha"],
            }
        )
        os.makedirs(
            (
                os.path.dirname(sample_data_path)
                if os.path.dirname(sample_data_path)
                else "."
            ),
            exist_ok=True,
        )
        dummy_df.to_csv(sample_data_path, index=False)
        print(
            f" Initial workspace configuration placeholder generated at {sample_data_path}"
        )

    run_headless_orchestration_pipeline(sample_data_path)
