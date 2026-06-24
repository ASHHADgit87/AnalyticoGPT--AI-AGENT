import pytest
import pandas as pd
from tools.forecasting_tools import compute_linear_extrapolation


@pytest.fixture
def series_dataframe():
    data = {"Hours_Studied": [5.0, 8.0, 10.0, 12.0], "Score": [70.0, 80.0, 85.0, 90.0]}
    return pd.DataFrame(data)


def test_unit11_compute_linear_extrapolation_generates_exact_steps(series_dataframe):
    results = compute_linear_extrapolation(
        series_dataframe, "Hours_Studied", "Score", steps=3
    )
    assert len(results["predictions"]) == 3


def test_unit12_compute_linear_extrapolation_includes_model_coefficients(
    series_dataframe,
):
    results = compute_linear_extrapolation(
        series_dataframe, "Hours_Studied", "Score", steps=3
    )
    assert "coefficient_slope" in results
    assert "y_intercept" in results


def test_unit13_compute_linear_extrapolation_calculates_positive_trend(
    series_dataframe,
):
    results = compute_linear_extrapolation(
        series_dataframe, "Hours_Studied", "Score", steps=3
    )
    assert float(results["coefficient_slope"]) > 0.0


def test_unit14_compute_linear_extrapolation_projects_beyond_max_x(series_dataframe):
    results = compute_linear_extrapolation(
        series_dataframe, "Hours_Studied", "Score", steps=3
    )
    first_prediction_x = float(results["predictions"]["Hours_Studied"].iloc[0])
    max_historical_x = float(series_dataframe["Hours_Studied"].max())
    assert first_prediction_x >= max_historical_x


def test_unit15_compute_linear_extrapolation_handles_empty_or_insufficient_data_gracefully():
    data = {"Hours_Studied": [5.0], "Score": [70.0]}
    empty_df = pd.DataFrame(data)
    results = compute_linear_extrapolation(empty_df, "Hours_Studied", "Score", steps=3)
    assert float(results["coefficient_slope"]) == 0.0
    assert len(results["predictions"]) == 0
