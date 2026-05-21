import logging
from pathlib import Path

import numpy as np
import pandas as pd

# CONFIG

RAW_DATA_PATH = Path("data/raw/extracted")
PROCESSED_DATA_PATH = Path("data/processed")

PROCESSED_DATA_PATH.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = PROCESSED_DATA_PATH / "cleaned_energy_data.csv"

# LOGGING

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# LOAD DATA

def load_raw_data() -> pd.DataFrame:

    logger.info("Loading raw CSV files...")

    csv_files = list(RAW_DATA_PATH.rglob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            "No CSV files found."
        )

    dataframes = []

    for file in csv_files:

        logger.info(f"Reading: {file.name}")

        try:

            # Read only smaller portion
            df = pd.read_csv(
                file,
                nrows=300000
            )

            # Random sample
            df = df.sample(
                n=min(len(df), 100000),
                random_state=42
            )

            dataframes.append(df)

        except Exception as e:

            logger.warning(
                f"Skipping {file.name}: {e}"
            )

    if not dataframes:
        raise ValueError(
            "No data loaded successfully."
        )

    combined_df = pd.concat(
        dataframes,
        ignore_index=True
    )

    logger.info(
        f"Total rows loaded: {len(combined_df):,}"
    )

    return combined_df

# CLEAN COLUMN NAMES

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df

# HANDLE MISSING VALUES

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:

    logger.info("Handling missing values...")

    numeric_cols = df.select_dtypes(include=np.number).columns

    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    categorical_cols = df.select_dtypes(
        exclude=np.number
    ).columns

    for col in categorical_cols:
        df[col] = df[col].fillna("unknown")

    return df

# STANDARDIZE DATETIME

def standardize_datetime(df: pd.DataFrame) -> pd.DataFrame:

    logger.info("Standardizing timestamps...")

    datetime_candidates = [
        "timestamp",
        "date",
        "datetime",
        "time"
    ]

    for col in datetime_candidates:
        if col in df.columns:

            df[col] = pd.to_datetime(
                df[col],
                errors="coerce"
            )

            df["year"] = df[col].dt.year
            df["month"] = df[col].dt.month
            df["day"] = df[col].dt.day
            df["hour"] = df[col].dt.hour
            df["day_of_week"] = df[col].dt.day_name()

            break

    return df

# REMOVE DUPLICATES

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:

    before = len(df)

    df = df.drop_duplicates()

    after = len(df)

    logger.info(
        f"Removed {before - after:,} duplicate rows."
    )

    return df

# REMOVE OUTLIERS

def remove_outliers(
    df: pd.DataFrame,
    column: str
) -> pd.DataFrame:
    
    if column not in df.columns:
        return df

    logger.info(f"Removing outliers from: {column}")

    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    filtered_df = df[
        (df[column] >= lower_bound)
        & (df[column] <= upper_bound)
    ]

    logger.info(
        f"Removed {len(df) - len(filtered_df):,} outliers."
    )

    return filtered_df

# FEATURE ENGINEERING

def create_energy_features(df: pd.DataFrame) -> pd.DataFrame:

    logger.info("Creating energy features...")

    consumption_columns = [
        col for col in df.columns
        if "energy" in col or "consumption" in col
    ]

    if consumption_columns:

        target_col = consumption_columns[0]

        df["is_peak_hour"] = df["hour"].apply(
            lambda x: 1 if 17 <= x <= 21 else 0
        )

        df["usage_category"] = pd.cut(
            df[target_col],
            bins=[0, 2, 5, 10, 20, 100],
            labels=[
                "very_low",
                "low",
                "moderate",
                "high",
                "excessive"
            ]
        )

    return df

# AGGREGATE HOUSEHOLD METRICS


def aggregate_household_metrics(
    df: pd.DataFrame
) -> pd.DataFrame:

    logger.info("Aggregating household metrics...")

    household_cols = [
        "household_id",
        "lclid",
        "household"
    ]

    household_col = None

    for col in household_cols:
        if col in df.columns:
            household_col = col
            break

    if not household_col:
        logger.warning("No household identifier found.")
        return df

    consumption_columns = [
        col for col in df.columns
        if "energy" in col or "consumption" in col
    ]

    if not consumption_columns:
        return df

    target_col = consumption_columns[0]

    agg_df = (
        df.groupby(household_col)
        .agg({
            target_col: [
                "mean",
                "max",
                "min",
                "sum"
            ]
        })
    )

    agg_df.columns = [
        "avg_consumption",
        "max_consumption",
        "min_consumption",
        "total_consumption"
    ]

    agg_df = agg_df.reset_index()

    return agg_df

# SAVE DATA

def save_processed_data(df: pd.DataFrame):

    logger.info(f"Saving processed data to: {OUTPUT_FILE}")

    df.to_csv(OUTPUT_FILE, index=False)

    logger.info("Processed dataset saved successfully.")


def convert_datetime_columns(df, datetime_columns):

    for column in datetime_columns:

        if column in df.columns:

            df[column] = pd.to_datetime(df[column])

    return df

def filter_invalid_consumption(df, consumption_column):

    df = df[df[consumption_column] >= 0]

    return df

# MAIN

def main():

    logger.info("Starting transformation pipeline...")

    df = load_raw_data()

    df = clean_column_names(df)

    df = handle_missing_values(df)

    df = standardize_datetime(df)

    df = remove_duplicates(df)

    consumption_columns = [
        col for col in df.columns
        if "energy" in col or "consumption" in col
    ]

    if consumption_columns:
        df = remove_outliers(
            df,
            consumption_columns[0]
        )

    df = create_energy_features(df)

    household_metrics = aggregate_household_metrics(df)

    save_processed_data(df)

    household_metrics.to_csv(
        PROCESSED_DATA_PATH / "household_metrics.csv",
        index=False
    )

    logger.info("Transformation pipeline completed.")


if __name__ == "__main__":
    main()
