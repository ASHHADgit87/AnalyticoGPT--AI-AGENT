import os
import sys

import pytest
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.pipeline_service import PipelineService
from tools.statistics_tools import (
    compute_descriptive_stats,
    generate_correlation_matrix,
    extract_top_performers,
)
from tools.visualization_tools import generate_trend_line_chart


@pytest.fixture
def clean_dataframe():
    data = {
        "Age": [25.0, 30.0, 22.0, 28.0],
        "Score": [95.0, 82.0, 78.0, 91.0],
        "Hours_Studied": [5.0, 10.0, 8.0, 12.0],
    }
    return pd.DataFrame(data)


def test_unit6_compute_descriptive_stats_contains_all_metrics(clean_dataframe):
    stats = compute_descriptive_stats(clean_dataframe)
    assert "Score" in stats
    assert "mean" in stats["Score"]
    assert "median" in stats["Score"]


def test_unit7_compute_descriptive_stats_calculates_correct_bounds(clean_dataframe):
    stats = compute_descriptive_stats(clean_dataframe)
    assert float(stats["Score"]["max_value"]) == 95.0
    assert float(stats["Hours_Studied"]["min_value"]) == 5.0


def test_unit8_generate_correlation_matrix_identity_property(clean_dataframe):
    matrix = generate_correlation_matrix(clean_dataframe)
    assert float(matrix["Score"]["Score"]) == 1.0
    assert float(matrix["Age"]["Age"]) == 1.0


def test_unit9_generate_correlation_matrix_symmetry(clean_dataframe):
    matrix = generate_correlation_matrix(clean_dataframe)
    assert float(matrix["Hours_Studied"]["Score"]) == float(
        matrix["Score"]["Hours_Studied"]
    )


def test_unit10_extract_top_performers_limits_output_size(clean_dataframe):
    top_three = extract_top_performers(clean_dataframe, metric_col="Score", top_n=3)
    assert len(top_three) == 3
    assert float(top_three["Score"].iloc[0]) == 95.0


def test_unit11_single_numeric_column_returns_no_correlation_matrix():
    df = pd.DataFrame({"Year": [2020, 2021, 2022]})
    matrix = generate_correlation_matrix(df)
    assert matrix == {}


def test_unit12_pipeline_prefers_date_feature_and_high_variance_metric():
    df = pd.DataFrame(
        {
            "Year": [2020, 2021, 2022, 2023],
            "Sales": [100.0, 120.0, 90.0, 130.0],
            "Profit": [10.0, 15.0, 12.0, 20.0],
        }
    )
    service = PipelineService(
        upload_dir="data/uploads",
        clean_dir="data/cleaned",
        chart_dir="outputs/charts",
        report_dir="outputs/reports",
    )

    metric_column = service._choose_metric_column(df)
    feature_column = service._choose_feature_column(df, metric_column)

    assert metric_column == "Sales"
    assert feature_column == "Year"


def test_unit13_numeric_strings_are_coerced_for_correlation_matrix():
    df = pd.DataFrame(
        {
            "Year": [2020, 2021, 2022],
            "Sales": ["100", "120", "90"],
            "Profit": ["10", "15", "12"],
            "Margin": ["2", "3", "4"],
        }
    )
    matrix = generate_correlation_matrix(df)
    assert "Sales" in matrix and "Profit" in matrix
    assert matrix["Sales"]["Sales"] == 1.0


def test_unit14_single_meaningful_numeric_column_skips_heatmap():
    df = pd.DataFrame(
        {
            "Year": [2016, 2017, 2018],
            "RD_Value": ["10", "12", "14"],
            "Relative_Sampling_Error": ["0.1", "0.2", "0.3"],
        }
    )
    matrix = generate_correlation_matrix(df)
    assert matrix == {}


def test_unit15_pipeline_prefers_datetime_column_for_feature_selection():
    df = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
            "Customer_Name": ["A", "B", "C"],
            "Sales": [10, 20, 30],
        }
    )
    service = PipelineService(
        upload_dir="data/uploads",
        clean_dir="data/cleaned",
        chart_dir="outputs/charts",
        report_dir="outputs/reports",
    )

    metric_column = service._choose_metric_column(df)
    feature_column = service._choose_feature_column(df, metric_column)

    assert metric_column == "Sales"
    assert feature_column == "Date"


def test_unit15_pipeline_skips_heatmap_when_numeric_columns_are_too_few():
    df = pd.DataFrame(
        {
            "Year": [2020, 2021, 2022],
            "Sales": [100, 120, 90],
            "Profit": [10, 15, 12],
        }
    )
    service = PipelineService(
        upload_dir="data/uploads",
        clean_dir="data/cleaned",
        chart_dir="outputs/charts",
        report_dir="outputs/reports",
    )

    plan = service._select_chart_plan(df, "Sales", "Year")

    assert plan["chart_type"] == "line"
    assert plan["generate_heatmap"] is False


def test_unit16_trend_chart_aggregates_repeated_years(tmp_path):
    df = pd.DataFrame(
        {
            "Year": [2016, 2016, 2017, 2017, 2018],
            "RD_Value": [10, 12, 14, 16, 18],
        }
    )

    output_path = generate_trend_line_chart(
        df, "Year", "RD_Value", output_dir=str(tmp_path)
    )

    assert os.path.exists(output_path)
