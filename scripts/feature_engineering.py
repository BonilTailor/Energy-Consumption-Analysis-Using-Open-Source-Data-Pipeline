"""
feature_engineering.py

Generate advanced analytical features for
energy consumption optimization.

Features:
- Time-based features
- Peak/off-peak indicators
- Rolling consumption statistics
- Consumption intensity scoring
- Seasonal categorization

Author: Your Name
Project: Energy Consumption Optimization
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------

INPUT_FILE = (
    Path("data/processed/cleaned_energy_data.csv")
)

OUTPUT_FILE = (
    Path("data/processed/feature_engineered_data.csv")
)

# -----------------------------------------------------------------------------
# LOGGING
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# LOAD DATA
# -----------------------------------------------------------------------------


def load_dataset() -> pd.DataFrame:
    """
    Load processed energy dataset.
    """

    logger.info("Loading processed dataset...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    logger.info(f"Loaded {len(df):,} records.")

    return df


# -----------------------------------------------------------------------------
# IDENTIFY TARGET COLUMN
# -----------------------------------------------------------------------------


def identify_consumption_column(df):
    """
    Identify energy consumption column.
    """

    candidate_columns = [
        col for col in df.columns
        if (
            "energy" in col.lower()
            or "consumption" in col.lower()
            or "kwh" in col.lower()
        )
    ]

    if not candidate_columns:
        raise ValueError(
            "No energy consumption column found."
        )

    return candidate_columns[0]


# -----------------------------------------------------------------------------
# TIME FEATURES
# -----------------------------------------------------------------------------


def generate_time_features(df):
    """
    Create time-based analytical features.
    """

    logger.info("Generating time features...")

    if "timestamp" in df.columns:

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

        df["hour"] = df["timestamp"].dt.hour
        df["day"] = df["timestamp"].dt.day
        df["month"] = df["timestamp"].dt.month
        df["weekday"] = (
            df["timestamp"].dt.day_name()
        )

        df["is_weekend"] = df["timestamp"].dt.weekday >= 5

    return df


# -----------------------------------------------------------------------------
# PEAK PERIOD FEATURES
# -----------------------------------------------------------------------------


def generate_peak_features(df):
    """
    Identify peak usage periods.
    """

    logger.info("Generating peak usage features...")

    df["is_peak_hour"] = df["hour"].apply(
        lambda x: 1 if 17 <= x <= 21 else 0
    )

    df["time_period"] = pd.cut(
        df["hour"],
        bins=[0, 6, 12, 18, 24],
        labels=[
            "night",
            "morning",
            "afternoon",
            "evening"
        ],
        include_lowest=True
    )

    return df


# -----------------------------------------------------------------------------
# SEASONAL FEATURES
# -----------------------------------------------------------------------------


def generate_seasonal_features(df):
    """
    Generate seasonal categorization.
    """

    logger.info("Generating seasonal features...")

    season_map = {
        12: "winter",
        1: "winter",
        2: "winter",
        3: "spring",
        4: "spring",
        5: "spring",
        6: "summer",
        7: "summer",
        8: "summer",
        9: "autumn",
        10: "autumn",
        11: "autumn"
    }

    df["season"] = df["month"].map(season_map)

    return df


# -----------------------------------------------------------------------------
# CONSUMPTION INTENSITY
# -----------------------------------------------------------------------------


def generate_consumption_intensity(
    df,
    target_column
):
    """
    Categorize households based on energy usage.
    """

    logger.info(
        "Generating consumption intensity features..."
    )

    quantiles = df[target_column].quantile(
        [0.25, 0.50, 0.75]
    )

    q1 = quantiles[0.25]
    q2 = quantiles[0.50]
    q3 = quantiles[0.75]

    def classify_usage(value):

        if value <= q1:
            return "low"

        elif value <= q2:
            return "moderate"

        elif value <= q3:
            return "high"

        return "very_high"

    df["consumption_intensity"] = df[
        target_column
    ].apply(classify_usage)

    return df


# -----------------------------------------------------------------------------
# ROLLING FEATURES
# -----------------------------------------------------------------------------


def generate_rolling_statistics(
    df,
    target_column
):
    """
    Generate rolling energy consumption statistics.
    """

    logger.info(
        "Generating rolling statistics..."
    )

    if "household_id" not in df.columns:
        return df

    df = df.sort_values(
        by=["household_id", "timestamp"]
    )

    df["rolling_avg_24h"] = (
        df.groupby("household_id")[target_column]
        .transform(
            lambda x: x.rolling(
                window=24,
                min_periods=1
            ).mean()
        )
    )

    df["rolling_std_24h"] = (
        df.groupby("household_id")[target_column]
        .transform(
            lambda x: x.rolling(
                window=24,
                min_periods=1
            ).std()
        )
    )

    return df


# -----------------------------------------------------------------------------
# SAVE DATASET
# -----------------------------------------------------------------------------


def save_dataset(df):
    """
    Save engineered dataset.
    """

    logger.info(
        f"Saving feature-engineered dataset: {OUTPUT_FILE}"
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    logger.info("Dataset saved successfully.")


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------


def main():

    logger.info(
        "Starting feature engineering pipeline..."
    )

    df = load_dataset()

    target_column = identify_consumption_column(df)

    df = generate_time_features(df)

    df = generate_peak_features(df)

    df = generate_seasonal_features(df)

    df = generate_consumption_intensity(
        df,
        target_column
    )

    df = generate_rolling_statistics(
        df,
        target_column
    )

    save_dataset(df)

    logger.info(
        "Feature engineering pipeline completed."
    )


if __name__ == "__main__":
    main()