# ============================================================
# Airflow DAG
# Energy Consumption Optimization Pipeline
# ============================================================

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

# ============================================================
# DAG Default Arguments
# ============================================================

default_args = {
    "owner": "data-engineering-team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

# ============================================================
# DAG Definition
# ============================================================

with DAG(
    dag_id="energy_consumption_pipeline",
    default_args=default_args,
    description="London Smart Meter Energy Pipeline",
    schedule_interval="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=[
        "energy",
        "smart-meter",
        "bigquery",
        "ml",
        "analytics"
    ]
) as dag:

    # ========================================================
    # Extract Task
    # ========================================================

    extract_data = BashOperator(
        task_id="extract_data",
        bash_command=(
            "python /opt/airflow/src/extract.py"
        ),
    )

    # ========================================================
    # Transform Task
    # ========================================================

    transform_data = BashOperator(
        task_id="transform_data",
        bash_command=(
            "python /opt/airflow/src/transform.py"
        ),
    )

    # ========================================================
    # Feature Engineering Task
    # ========================================================

    feature_engineering = BashOperator(
        task_id="feature_engineering",
        bash_command=(
            "python "
            "/opt/airflow/src/feature_engineering.py"
        ),
    )

    # ========================================================
    # Clustering Task
    # ========================================================

    clustering_analysis = BashOperator(
        task_id="clustering_analysis",
        bash_command=(
            "python /opt/airflow/src/clustering.py"
        ),
    )

    # ========================================================
    # Anomaly Detection Task
    # ========================================================

    anomaly_detection = BashOperator(
        task_id="anomaly_detection",
        bash_command=(
            "python "
            "/opt/airflow/src/anomaly_detection.py"
        ),
    )

    # ========================================================
    # Load to BigQuery
    # ========================================================

    load_bigquery = BashOperator(
        task_id="load_bigquery",
        bash_command=(
            "python "
            "/opt/airflow/src/load_bigquery.py"
        ),
    )

    # ========================================================
    # Pipeline Dependencies
    # ========================================================

    (
        extract_data
        >> transform_data
        >> feature_engineering
        >> clustering_analysis
        >> anomaly_detection
        >> load_bigquery
    )