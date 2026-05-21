# Unit Tests - transform.py

import pytest
import pandas as pd
import numpy as np

from scripts.transform import (
    clean_column_names,
    remove_duplicates,
    handle_missing_values,
    convert_datetime_columns,
    filter_invalid_consumption,
)
# Test Data

@pytest.fixture
def sample_dataframe():

    data = {
        "House ID": [1, 1, 2, 3],
        "Energy Consumption": [10.5, 10.5, np.nan, -5],
        "Reading Date": [
            "2024-01-01",
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
        ]
    }

    return pd.DataFrame(data)

# Test clean_column_names

def test_clean_column_names(sample_dataframe):

    df = clean_column_names(sample_dataframe)

    expected_columns = [
        "house_id",
        "energy_consumption",
        "reading_date"
    ]

    assert list(df.columns) == expected_columns

# Test remove_duplicates

def test_remove_duplicates(sample_dataframe):

    df = clean_column_names(sample_dataframe)

    result = remove_duplicates(df)

    assert len(result) == 3

# Test handle_missing_values

def test_handle_missing_values(sample_dataframe):

    df = clean_column_names(sample_dataframe)

    result = handle_missing_values(df)

    assert result["energy_consumption"].isnull().sum() == 0

# Test convert_datetime_columns

def test_convert_datetime_columns(sample_dataframe):

    df = clean_column_names(sample_dataframe)

    result = convert_datetime_columns(
        df,
        ["reading_date"]
    )

    assert pd.api.types.is_datetime64_any_dtype(
        result["reading_date"]
    )

# Test filter_invalid_consumption

def test_filter_invalid_consumption(sample_dataframe):

    df = clean_column_names(sample_dataframe)

    result = filter_invalid_consumption(
        df,
        "energy_consumption"
    )

    assert (result["energy_consumption"] < 0).sum() == 0

# Edge Case Testing

def test_empty_dataframe():

    empty_df = pd.DataFrame()

    result = clean_column_names(empty_df)

    assert result.empty


def test_no_duplicates():

    df = pd.DataFrame({
        "id": [1, 2, 3]
    })

    result = remove_duplicates(df)

    assert len(result) == 3


def test_all_null_consumption():

    df = pd.DataFrame({
        "energy_consumption": [np.nan, np.nan]
    })

    result = handle_missing_values(df)

    assert result["energy_consumption"].isnull().sum() == 0
