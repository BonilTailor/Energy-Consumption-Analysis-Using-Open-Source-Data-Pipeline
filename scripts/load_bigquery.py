import logging
from pathlib import Path

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# CONFIG

PROJECT_ID = "your-gcp-project-id"
DATASET_ID = "your-dataset-id"
TABLE_ID = "your-bigquery-table-id"

SERVICE_ACCOUNT_FILE = "credentials/gcp_service_account.json"

PROCESSED_DATA_FILE = (
    Path("data/processed/cleaned_energy_data.csv")
)

# LOGGING

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# BIGQUERY CLIENT


def create_bigquery_client():

    logger.info("Creating BigQuery client...")

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE
    )

    client = bigquery.Client(
        credentials=credentials,
        project=PROJECT_ID
    )

    logger.info("BigQuery client created successfully.")

    return client

# LOAD DATAFRAME

def load_processed_data() -> pd.DataFrame:

    logger.info("Loading processed dataset...")

    if not PROCESSED_DATA_FILE.exists():
        raise FileNotFoundError(
            f"Processed dataset not found: {PROCESSED_DATA_FILE}"
        )

    df = pd.read_csv(PROCESSED_DATA_FILE)

    logger.info(f"Loaded {len(df):,} rows.")

    return df

# CREATE DATASET

def create_dataset_if_not_exists(client):

    dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"

    try:
        client.get_dataset(dataset_ref)

        logger.info(
            f"Dataset already exists: {dataset_ref}"
        )

    except Exception:

        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "EU"

        client.create_dataset(dataset)

        logger.info(
            f"Created dataset: {dataset_ref}"
        )

# LOAD TO BIGQUERY

def upload_dataframe_to_bigquery(
    client,
    dataframe: pd.DataFrame
):

    table_ref = (
        f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    )

    logger.info(
        f"Uploading data to BigQuery table: {table_ref}"
    )

    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        write_disposition="WRITE_TRUNCATE",
        source_format=bigquery.SourceFormat.CSV
    )

    load_job = client.load_table_from_dataframe(
        dataframe,
        table_ref,
        job_config=job_config
    )

    load_job.result()

    logger.info(
        f"Successfully uploaded {len(dataframe):,} rows."
    )

# VALIDATE LOAD

def validate_table_row_count(client):

    query = f"""
    SELECT COUNT(*) AS total_rows
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    """

    query_job = client.query(query)

    result = query_job.result()

    for row in result:
        logger.info(
            f"BigQuery row count: {row.total_rows:,}"
        )

# MAIN

def main():

    logger.info("Starting BigQuery load pipeline...")

    client = create_bigquery_client()

    create_dataset_if_not_exists(client)

    df = load_processed_data()

    upload_dataframe_to_bigquery(client, df)

    validate_table_row_count(client)

    logger.info("BigQuery load completed successfully.")


if __name__ == "__main__":
    main()
