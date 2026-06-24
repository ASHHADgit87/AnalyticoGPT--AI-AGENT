import pytest
import pandas as pd
from tools.statistics_tools import compute_descriptive_stats, generate_correlation_matrix

@pytest.fixture
def clean_dataframe():
    return pd.DataFrame({
        "Age": [25, 30, 22, 28],
        "Score": [95.0, 82.0, 78.0, 91.0],
        "Hours_Studied": [5.0, 10.0, 8.0, 12.0]
    })

def test_compute_descriptive_stats(clean_dataframe):
    stats = compute_descriptive_stats(clean_dataframe)
    assert "Score" in stats
    assert stats["Score"]["max_value"] == 95.0
    assert stats["Hours_Studied"]["min_value"] == 5.0

def test_generate_correlation_matrix(clean_dataframe):
    matrix = generate_correlation_matrix(clean_dataframe)
    assert "Age" in matrix
    assert "Score" in matrix["Hours_Studied"]
    assert matrix["Score"]["Score"] == 1.0