"""
extract.py

Extract smart meter energy consumption data from:
https://data.london.gov.uk/dataset/smartmeter-energy-use-data-in-london-households

Author: Your Name
Project: Energy Consumption Optimization
"""

import os
import logging
import zipfile
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------

DATA_URL = (
    "https://data.london.gov.uk/download/smartmeter-energy-use-data-in-"
    "london-households/10d04d57-5d4c-4b69-b6f2-4f8c9c6e8d5b/"
    "smartmeter.zip"
)

RAW_DATA_DIR = Path("data/raw")
EXTRACT_DIR = Path("data/raw/extracted")

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

ZIP_FILE_PATH = RAW_DATA_DIR / "smartmeter.zip"

# -----------------------------------------------------------------------------
# LOGGING
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# DOWNLOAD DATASET
# -----------------------------------------------------------------------------


def download_file(url: str, output_path: Path):
    """
    Download dataset with progress bar.
    """

    logger.info("Starting dataset download...")

    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024

    with open(output_path, "wb") as file:
        with tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            desc="Downloading"
        ) as progress_bar:

            for chunk in response.iter_content(block_size):
                file.write(chunk)
                progress_bar.update(len(chunk))

    logger.info(f"Dataset downloaded to: {output_path}")


# -----------------------------------------------------------------------------
# EXTRACT ZIP
# -----------------------------------------------------------------------------


def extract_zip(zip_path: Path, extract_to: Path):
    """
    Extract zip dataset.
    """

    logger.info("Extracting dataset...")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

    logger.info(f"Files extracted to: {extract_to}")


# -----------------------------------------------------------------------------
# VALIDATE FILES
# -----------------------------------------------------------------------------


def validate_extraction(directory: Path):
    """
    Validate extracted files exist.
    """

    csv_files = list(directory.rglob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            "No CSV files found after extraction."
        )

    logger.info(f"Found {len(csv_files)} CSV files.")


# -----------------------------------------------------------------------------
# SAMPLE PREVIEW
# -----------------------------------------------------------------------------


def preview_data(directory: Path):
    """
    Load sample rows from first CSV file.
    """

    csv_files = list(directory.rglob("*.csv"))

    sample_file = csv_files[0]

    logger.info(f"Previewing file: {sample_file.name}")

    df = pd.read_csv(sample_file, nrows=5)

    logger.info("\n%s", df.head())


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------


def main():

    if not ZIP_FILE_PATH.exists():
        download_file(DATA_URL, ZIP_FILE_PATH)
    else:
        logger.info("Dataset already exists. Skipping download.")

    extract_zip(ZIP_FILE_PATH, EXTRACT_DIR)

    validate_extraction(EXTRACT_DIR)

    preview_data(EXTRACT_DIR)

    logger.info("Extraction pipeline completed successfully.")


if __name__ == "__main__":
    main()