# ============================================================
# Unit Tests - feature_engineering.py
# ============================================================

import pytest
import pandas as pd
import numpy as np

from scripts.feature_engineering import (
    create_time_features,
    create_peak_hour_feature,
    create_weekend_feature,
    create_season_feature,
    create_consumption_intensity,
)

# ============================================================
# Sample Test Data
# ============================================================

@pytest.fixture
def sample_dataframe():

    data = {
        "timestamp": pd.to_datetime([
            "2024-01-01 08:00:00",
            "2024-06-15 19:00:00",
            "2024-10-20 14:00:00",
            "2024-12-25 22:00:00"
        ]),
        "energy_consumption": [
            0.5,
            2.5,
            4.0,
            7.5
        ]
    }

    return pd.DataFrame(data)


# ============================================================
# Test create_time_features
# ============================================================

def test_create_time_features(sample_dataframe):

    result = create_time_features(
        sample_dataframe,
        "timestamp"
    )

    expected_columns = [
        "hour",
        "day",
        "month",
        "day_of_week"
    ]

    for col in expected_columns:
        assert col in result.columns


# ============================================================
# Test create_peak_hour_feature
# ============================================================

def test_create_peak_hour_feature(sample_dataframe):

    result = create_peak_hour_feature(
        sample_dataframe,
        hour_column="hour"
    )

    assert "is_peak_hour" in result.columns

    assert set(result["is_peak_hour"].unique()).issubset({0, 1})


# ============================================================
# Test create_weekend_feature
# ============================================================

def test_create_weekend_feature(sample_dataframe):

    df = create_time_features(
        sample_dataframe,
        "timestamp"
    )

    result = create_weekend_feature(df)

    assert "is_weekend" in result.columns

    assert set(result["is_weekend"].unique()).issubset({0, 1})


# ============================================================
# Test create_season_feature
# ============================================================

def test_create_season_feature(sample_dataframe):

    df = create_time_features(
        sample_dataframe,
        "timestamp"
    )

    result = create_season_feature(df)

    assert "season" in result.columns

    valid_seasons = {
        "winter",
        "spring",
        "summer",
        "autumn"
    }

    assert set(result["season"].unique()).issubset(
        valid_seasons
    )


# ============================================================
# Test create_consumption_intensity
# ============================================================

def test_create_consumption_intensity(
    sample_dataframe
):

    result = create_consumption_intensity(
        sample_dataframe,
        consumption_column="energy_consumption"
    )

    assert "consumption_intensity" in result.columns

    valid_categories = {
        "low",
        "medium",
        "high",
        "very_high"
    }

    assert set(
        result["consumption_intensity"].unique()
    ).issubset(valid_categories)


# ============================================================
# Edge Case Tests
# ============================================================

def test_empty_dataframe():

    empty_df = pd.DataFrame({
        "timestamp": pd.to_datetime([])
    })

    result = create_time_features(
        empty_df,
        "timestamp"
    )

    assert result.empty


def test_single_record():

    df = pd.DataFrame({
        "timestamp": pd.to_datetime([
            "2024-01-01 12:00:00"
        ]),
        "energy_consumption": [1.5]
    })

    result = create_consumption_intensity(
        df,
        "energy_consumption"
    )

    assert len(result) == 1


def test_missing_consumption_column():

    df = pd.DataFrame({
        "timestamp": pd.to_datetime([
            "2024-01-01"
        ])
    })

    with pytest.raises(Exception):

        create_consumption_intensity(
            df,
            "energy_consumption"
        )