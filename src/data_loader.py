"""Data Loader Module for Poll Results Visualizer.

This module is responsible for loading raw poll data from CSV files
and ensuring required columns are present without altering or cleaning
the data during the loading stage.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd


# Canonical list of nine expected columns in the poll dataset
REQUIRED_COLUMNS: list[str] = [
    "response_id",
    "department",
    "study_year",
    "preferred_language",
    "training_satisfaction",
    "preferred_learning_method",
    "internship_interest",
    "recommendation_score",
    "comments",
]


def load_poll_data(file_path: Union[str, Path]) -> pd.DataFrame:
    """Load raw poll survey responses from a CSV file into a pandas DataFrame.

    This function strictly handles file retrieval and column presence verification.
    It does NOT mutate, clean, or type-cast data, keeping raw loading strictly
    decoupled from downstream data cleaning.

    Args:
        file_path: Filesystem path to the raw CSV file.

    Returns:
        pd.DataFrame containing the raw, uncleaned survey records.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the path is a directory, if the CSV file is empty,
                    or if any required columns are missing.
    """
    path = Path(file_path)

    # 1. Existence and path type validation
    if not path.exists():
        raise FileNotFoundError(f"Poll data file not found at: '{path}'")

    if path.is_dir():
        raise ValueError(f"Provided path is a directory, not a CSV file: '{path}'")

    # 2. Check file size to catch empty files early
    if path.stat().st_size == 0:
        raise ValueError(f"The CSV file at '{path}' is completely empty (0 bytes).")

    # 3. Ingest CSV via pandas
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError as err:
        raise ValueError(f"The CSV file at '{path}' contains no data or columns.") from err
    except Exception as err:
        raise ValueError(f"Failed to parse CSV file at '{path}': {err}") from err

    # 4. Verify DataFrame is not empty of columns
    if df.empty and len(df.columns) == 0:
        raise ValueError(f"The CSV file at '{path}' contains no columns.")

    # 5. Schema validation: all required columns must be present
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"CSV file at '{path}' is missing required columns: {missing_columns}. "
            f"Expected all of: {REQUIRED_COLUMNS}"
        )

    return df
