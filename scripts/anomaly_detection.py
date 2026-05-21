"""
anomaly_detection.py

Detect abnormal household energy usage patterns
using Isolation Forest.

Features:
- Detect unusual consumption spikes
- Identify potential energy waste
- Generate anomaly reports
- Dashboard-ready outputs

Author: Your Name
Project: Energy Consumption Optimization
"""

import logging
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------

INPUT_FILE = (
    Path("data/processed/cleaned_energy_data.csv")
)

OUTPUT_DIR = Path("data/processed/anomalies")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ANOMALY_OUTPUT_FILE = (
    OUTPUT_DIR / "detected_anomalies.csv"
)

MODEL_FILE = (
    OUTPUT_DIR / "isolation_forest_model.pkl"
)

PLOT_FILE = (
    OUTPUT_DIR / "anomaly_detection_plot.png"
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


def load_data() -> pd.DataFrame:
    """
    Load processed energy dataset.
    """

    logger.info("Loading processed dataset...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    logger.info(f"Loaded {len(df):,} rows.")

    return df


# -----------------------------------------------------------------------------
# IDENTIFY CONSUMPTION COLUMN
# -----------------------------------------------------------------------------


def get_consumption_column(df: pd.DataFrame):
    """
    Identify target energy consumption column.
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

    logger.info(
        f"Using consumption column: {candidate_columns[0]}"
    )

    return candidate_columns[0]


# -----------------------------------------------------------------------------
# FEATURE PREPARATION
# -----------------------------------------------------------------------------


def prepare_features(
    df: pd.DataFrame,
    target_column: str
):
    """
    Prepare numerical features for anomaly detection.
    """

    logger.info("Preparing anomaly detection features...")

    feature_columns = [target_column]

    optional_features = [
        "hour",
        "month",
        "is_peak_hour"
    ]

    for feature in optional_features:
        if feature in df.columns:
            feature_columns.append(feature)

    X = df[feature_columns].copy()

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    logger.info(
        f"Prepared {len(feature_columns)} features."
    )

    return X_scaled, feature_columns


# -----------------------------------------------------------------------------
# TRAIN ISOLATION FOREST
# -----------------------------------------------------------------------------


def train_isolation_forest(X_scaled):
    """
    Train anomaly detection model.
    """

    logger.info("Training Isolation Forest model...")

    model = IsolationForest(
        n_estimators=150,
        contamination=0.02,
        random_state=42
    )

    model.fit(X_scaled)

    logger.info("Model training completed.")

    return model


# -----------------------------------------------------------------------------
# GENERATE ANOMALY SCORES
# -----------------------------------------------------------------------------


def detect_anomalies(
    model,
    X_scaled,
    dataframe
):
    """
    Generate anomaly predictions.
    """

    logger.info("Generating anomaly predictions...")

    dataframe["anomaly_score"] = model.decision_function(
        X_scaled
    )

    dataframe["anomaly_flag"] = model.predict(
        X_scaled
    )

    dataframe["anomaly_label"] = dataframe[
        "anomaly_flag"
    ].map({
        1: "normal",
        -1: "anomaly"
    })

    anomaly_count = (
        dataframe["anomaly_label"] == "anomaly"
    ).sum()

    logger.info(
        f"Detected {anomaly_count:,} anomalies."
    )

    return dataframe


# -----------------------------------------------------------------------------
# SAVE OUTPUTS
# -----------------------------------------------------------------------------


def save_outputs(
    dataframe,
    model
):
    """
    Save anomaly results and model artifacts.
    """

    logger.info("Saving anomaly outputs...")

    dataframe.to_csv(
        ANOMALY_OUTPUT_FILE,
        index=False
    )

    joblib.dump(model, MODEL_FILE)

    logger.info(
        f"Anomaly report saved: {ANOMALY_OUTPUT_FILE}"
    )

    logger.info(
        f"Model artifact saved: {MODEL_FILE}"
    )


# -----------------------------------------------------------------------------
# CREATE VISUALIZATION
# -----------------------------------------------------------------------------


def create_anomaly_plot(
    dataframe,
    target_column
):
    """
    Create anomaly visualization.
    """

    logger.info("Creating anomaly plot...")

    plt.figure(figsize=(14, 7))

    normal_data = dataframe[
        dataframe["anomaly_label"] == "normal"
    ]

    anomaly_data = dataframe[
        dataframe["anomaly_label"] == "anomaly"
    ]

    plt.scatter(
        normal_data.index,
        normal_data[target_column],
        alpha=0.4,
        label="Normal"
    )

    plt.scatter(
        anomaly_data.index,
        anomaly_data[target_column],
        alpha=0.9,
        label="Anomaly"
    )

    plt.xlabel("Record Index")
    plt.ylabel("Energy Consumption")
    plt.title(
        "Household Energy Consumption Anomaly Detection"
    )

    plt.legend()

    plt.tight_layout()

    plt.savefig(PLOT_FILE)

    logger.info(
        f"Anomaly visualization saved: {PLOT_FILE}"
    )


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------


def main():

    logger.info(
        "Starting anomaly detection pipeline..."
    )

    df = load_data()

    target_column = get_consumption_column(df)

    X_scaled, feature_columns = prepare_features(
        df,
        target_column
    )

    model = train_isolation_forest(X_scaled)

    results_df = detect_anomalies(
        model,
        X_scaled,
        df
    )

    save_outputs(results_df, model)

    create_anomaly_plot(
        results_df,
        target_column
    )

    logger.info(
        "Anomaly detection pipeline completed."
    )


if __name__ == "__main__":
    main()