import pytest
import pandas as pd
from tools.forecasting_tools import compute_linear_extrapolation

@pytest.fixture
def series_dataframe():
    return pd.DataFrame({
        "Hours_Studied":,
        "Score":
    })

def test_compute_linear_extrapolation(series_dataframe):
    results = compute_linear_extrapolation(series_dataframe, "Hours_Studied", "Score", steps=3)
    assert "coefficient_slope" in results
    assert "predictions" in results
    assert len(results["predictions"]) == 3