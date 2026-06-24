import pytest
import pandas as pd
import numpy as np
from tools.cleaning_tools import drop_nulls, fill_numeric_defaults


@pytest.fixture
def messy_dataframe():
    return pd.DataFrame(
        {
            "Age": [20, 21, np.nan, 23, 20],
            "Score": [95, np.nan, 90, 80, 95],
            "Hours_Studied": [8, 7, 6, np.nan, 8],
        }
    )


def test_drop_nulls(messy_dataframe):
    cleaned_df = drop_nulls(messy_dataframe)
    assert cleaned_df.isnull().sum().sum() == 0
    assert len(cleaned_df) == 2


def test_fill_numeric_defaults(messy_dataframe):
    filled_df = fill_numeric_defaults(messy_dataframe, default_val=0.0)
    assert filled_df.isnull().sum().sum() == 0
    assert filled_df.loc[2, "Age"] == 0.0
    assert filled_df.loc[1, "Score"] == 0.0
