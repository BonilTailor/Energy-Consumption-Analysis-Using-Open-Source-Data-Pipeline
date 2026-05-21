import logging
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# CONFIG

INPUT_FILE = (
    Path("data/processed/household_metrics.csv")
)

OUTPUT_DIR = Path("data/processed/clusters")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CLUSTER_OUTPUT_FILE = (
    OUTPUT_DIR / "household_clusters.csv"
)

MODEL_FILE = (
    OUTPUT_DIR / "kmeans_model.pkl"
)

PLOT_FILE = (
    OUTPUT_DIR / "cluster_visualization.png"
)

# LOGGING

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# LOAD DATA

def load_household_metrics() -> pd.DataFrame:
    logger.info("Loading household metrics dataset...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    logger.info(f"Loaded {len(df):,} households.")

    return df

# PREPARE FEATURES

def prepare_features(df: pd.DataFrame):
    logger.info("Preparing clustering features...")

    feature_columns = [
        "avg_consumption",
        "max_consumption",
        "min_consumption",
        "total_consumption"
    ]

    missing_columns = [
        col for col in feature_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    X = df[feature_columns]

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    logger.info(
        f"Prepared {len(feature_columns)} clustering features."
    )

    return X_scaled, feature_columns

# TRAIN KMEANS MODEL

def train_kmeans(
    X_scaled,
    n_clusters=4
):

    logger.info(
        f"Training KMeans with {n_clusters} clusters..."
    )

    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10
    )

    model.fit(X_scaled)

    logger.info("KMeans training completed.")

    return model

# ASSIGN CLUSTERS

def assign_clusters(
    dataframe,
    model,
    X_scaled
):

    logger.info("Assigning household clusters...")

    dataframe["cluster"] = model.predict(X_scaled)

    cluster_labels = {
        0: "Low Usage",
        1: "Moderate Usage",
        2: "High Usage",
        3: "Peak Consumers"
    }

    dataframe["cluster_label"] = dataframe[
        "cluster"
    ].map(cluster_labels)

    logger.info("Cluster assignment completed.")

    return dataframe

# SAVE OUTPUTS

def save_outputs(
    dataframe,
    model
):

    logger.info("Saving clustering outputs...")

    dataframe.to_csv(
        CLUSTER_OUTPUT_FILE,
        index=False
    )

    joblib.dump(model, MODEL_FILE)

    logger.info(
        f"Cluster output saved: {CLUSTER_OUTPUT_FILE}"
    )

    logger.info(
        f"Model artifact saved: {MODEL_FILE}"
    )

# CLUSTER VISUALIZATION

def create_cluster_plot(dataframe):

    logger.info("Creating cluster visualization...")

    plt.figure(figsize=(12, 7))

    for cluster in dataframe["cluster"].unique():

        cluster_data = dataframe[
            dataframe["cluster"] == cluster
        ]

        plt.scatter(
            cluster_data["avg_consumption"],
            cluster_data["total_consumption"],
            alpha=0.7,
            label=f"Cluster {cluster}"
        )

    plt.xlabel("Average Consumption")
    plt.ylabel("Total Consumption")

    plt.title(
        "Household Energy Consumption Clusters"
    )

    plt.legend()

    plt.tight_layout()

    plt.savefig(PLOT_FILE)

    logger.info(
        f"Cluster visualization saved: {PLOT_FILE}"
    )

# GENERATE CLUSTER SUMMARY

def generate_cluster_summary(df):

    logger.info("Generating cluster summary...")

    summary = (
        df.groupby("cluster_label")
        .agg({
            "avg_consumption": "mean",
            "total_consumption": "mean",
            "max_consumption": "mean"
        })
        .round(2)
    )

    summary_file = (
        OUTPUT_DIR / "cluster_summary.csv"
    )

    summary.to_csv(summary_file)

    logger.info(
        f"Cluster summary saved: {summary_file}"
    )

# MAIN


def main():

    logger.info(
        "Starting household clustering pipeline..."
    )

    df = load_household_metrics()

    X_scaled, feature_columns = prepare_features(df)

    model = train_kmeans(
        X_scaled,
        n_clusters=4
    )

    clustered_df = assign_clusters(
        df,
        model,
        X_scaled
    )

    save_outputs(clustered_df, model)

    create_cluster_plot(clustered_df)

    generate_cluster_summary(clustered_df)

    logger.info(
        "Household clustering pipeline completed."
    )


if __name__ == "__main__":
    main()
