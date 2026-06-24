import pytest
import pandas as pd
import numpy as np
from tools.cleaning_tools import drop_nulls, fill_numeric_defaults, standardize_column_names

@pytest.fixture
def messy_dataframe():
    data = {
        "Age": [20.0, 21.0, float('nan'), 23.0, 20.0],
        "Score": [95.0, float('nan'), 90.0, 80.0, 95.0],
        "Hours Studied": [8.0, 7.0, 6.0, float('nan'), 8.0]
    }
    return pd.DataFrame(data)

def test_unit1_drop_nulls_removes_all_nan_rows(messy_dataframe):
    cleaned_df = drop_nulls(messy_dataframe)
    total_nulls = int(cleaned_df.isnull().sum().sum())
    assert total_nulls == 0
    assert len(cleaned_df) == 2

def test_unit2_drop_nulls_maintains_structural_columns(messy_dataframe):
    cleaned_df = drop_nulls(messy_dataframe)
    column_list = list(cleaned_df.columns)
    assert column_list == ["Age", "Score", "Hours Studied"]

def test_unit3_fill_numeric_defaults_replaces_nan_with_zero(messy_dataframe):
    filled_df = fill_numeric_defaults(messy_dataframe, default_val=0.0)
    total_nulls = int(filled_df.isnull().sum().sum())
    assert total_nulls == 0
    assert float(filled_df.loc[2, "Age"]) == 0.0
    assert float(filled_df.loc[1, "Score"]) == 0.0

def test_unit4_fill_numeric_defaults_leaves_valid_data_intact(messy_dataframe):
    filled_df = fill_numeric_defaults(messy_dataframe, default_val=99.0)
    assert float(filled_df.loc[0, "Age"]) == 20.0
    assert float(filled_df.loc[4, "Score"]) == 95.0

def test_unit5_standardize_column_names_replaces_spaces_with_underscores(messy_dataframe):
    standardized_df = standardize_column_names(messy_dataframe)
    column_list = list(standardized_df.columns)
    assert "Hours_Studied" in column_list
    assert "Hours Studied" not in column_list