import pytest
import pandas as pd
from tools.statistics_tools import (
    compute_descriptive_stats,
    generate_correlation_matrix,
    extract_top_performers,
)


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
    assert float(top_three["Score"]) == 95.0
