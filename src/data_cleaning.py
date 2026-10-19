"""Data Cleaning and Transformation Module for Poll Results Visualizer.

This module enforces data quality standards, trims whitespace, standardizes
categorical fields, verifies value ranges, and produces a sanitized dataset
without modifying raw inputs or silently deleting records.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd

from src.data_loader import REQUIRED_COLUMNS, load_poll_data


# Controlled domain standards
ALLOWED_DEPARTMENTS: set[str] = {"IT", "Commerce", "Science", "Arts"}
ALLOWED_STUDY_YEARS: set[int] = {1, 2, 3, 4}
ALLOWED_LANGUAGES: set[str] = {"Python", "Java", "C++", "JavaScript"}
ALLOWED_SATISFACTION_SCORES: set[int] = {1, 2, 3, 4, 5}
ALLOWED_LEARNING_METHODS: set[str] = {
    "Hands-on Projects",
    "Video Tutorials",
    "Classroom Lectures",
    "Online Courses",
}
ALLOWED_INTERNSHIP_CHOICES: set[str] = {"Yes", "No"}
ALLOWED_RECOMMENDATION_SCORES: set[int] = set(range(0, 11))  # 0 to 10 inclusive


class DataValidationError(ValueError):
    """Exception raised when poll data violates quality or schema standards."""
    pass


def clean_poll_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean, standardize, and validate poll survey responses.

    Validation & Cleaning Policy:
    1. Pure function: Does NOT modify caller's input DataFrame in place.
    2. Whitespace trimming: Leading/trailing whitespace is trimmed from all string columns.
    3. Category enforcement: Checks against controlled allowed domain sets.
    4. Numeric range validation: Validates integer ranges for ratings and study year.
    5. Completeness: All columns except 'comments' must be complete (0 nulls/blanks).
    6. Optional comments: Null/missing values in 'comments' are explicitly preserved.
    7. No silent drops: If quality problems exist, a DataValidationError is raised detailing
       all violations rather than silently dropping rows.

    Args:
        df: Input pandas DataFrame containing survey responses.

    Returns:
        pd.DataFrame: Cleaned, validated DataFrame with preserved column order.

    Raises:
        DataValidationError: If any required column is missing, null, duplicate,
                            out of range, or contains unknown category values.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, received {type(df).__name__}")

    # Check for missing required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise DataValidationError(f"DataFrame is missing required columns: {missing_cols}")

    # Work on an isolated copy to preserve caller's data
    cleaned_df = df.copy()

    # Handle edge case: empty DataFrame with correct columns
    if cleaned_df.empty:
        return cleaned_df[REQUIRED_COLUMNS].copy()

    error_messages: list[str] = []

    # 1. Clean string columns: trim whitespace
    string_cols = [
        "response_id",
        "department",
        "preferred_language",
        "preferred_learning_method",
        "internship_interest",
    ]
    for col in string_cols:
        cleaned_df[col] = cleaned_df[col].astype(str).str.strip()

    # 2. Validate response_id (non-null, non-blank, unique)
    blank_ids = cleaned_df["response_id"].isin(["", "nan", "None", "NaN"])
    if blank_ids.any():
        error_messages.append(f"Found {blank_ids.sum()} blank or null response_id values.")

    duplicate_ids = cleaned_df["response_id"].duplicated()
    if duplicate_ids.any():
        dups_list = cleaned_df.loc[duplicate_ids, "response_id"].unique().tolist()
        error_messages.append(
            f"Found {duplicate_ids.sum()} duplicate response_id values: {dups_list[:5]}"
        )

    # 3. Validate department
    invalid_depts = ~cleaned_df["department"].isin(ALLOWED_DEPARTMENTS)
    if invalid_depts.any():
        bad_values = cleaned_df.loc[invalid_depts, "department"].unique().tolist()
        error_messages.append(
            f"Invalid department categories found: {bad_values}. Allowed: {sorted(ALLOWED_DEPARTMENTS)}"
        )

    # 4. Validate study_year (integers 1 to 4)
    if cleaned_df["study_year"].isnull().any():
        error_messages.append(f"Found {cleaned_df['study_year'].isnull().sum()} null values in 'study_year'.")
    else:
        numeric_year = pd.to_numeric(cleaned_df["study_year"], errors="coerce")
        if numeric_year.isnull().any():
            error_messages.append("Column 'study_year' contains non-numeric values.")
        elif not (numeric_year % 1 == 0).all():
            error_messages.append("Column 'study_year' contains non-integer floating point values.")
        else:
            cleaned_df["study_year"] = numeric_year.astype(int)
            invalid_years = ~cleaned_df["study_year"].isin(ALLOWED_STUDY_YEARS)
            if invalid_years.any():
                bad_years = cleaned_df.loc[invalid_years, "study_year"].unique().tolist()
                error_messages.append(
                    f"Invalid study_year values found: {bad_years}. Allowed: {sorted(ALLOWED_STUDY_YEARS)}"
                )

    # 5. Validate preferred_language
    invalid_langs = ~cleaned_df["preferred_language"].isin(ALLOWED_LANGUAGES)
    if invalid_langs.any():
        bad_langs = cleaned_df.loc[invalid_langs, "preferred_language"].unique().tolist()
        error_messages.append(
            f"Invalid preferred_language categories found: {bad_langs}. Allowed: {sorted(ALLOWED_LANGUAGES)}"
        )

    # 6. Validate training_satisfaction (integers 1 to 5)
    if cleaned_df["training_satisfaction"].isnull().any():
        error_messages.append(
            f"Found {cleaned_df['training_satisfaction'].isnull().sum()} null values in 'training_satisfaction'."
        )
    else:
        numeric_sat = pd.to_numeric(cleaned_df["training_satisfaction"], errors="coerce")
        if numeric_sat.isnull().any():
            error_messages.append("Column 'training_satisfaction' contains non-numeric values.")
        elif not (numeric_sat % 1 == 0).all():
            error_messages.append("Column 'training_satisfaction' contains non-integer floating point values.")
        else:
            cleaned_df["training_satisfaction"] = numeric_sat.astype(int)
            invalid_sat = ~cleaned_df["training_satisfaction"].isin(ALLOWED_SATISFACTION_SCORES)
            if invalid_sat.any():
                bad_sat = cleaned_df.loc[invalid_sat, "training_satisfaction"].unique().tolist()
                error_messages.append(
                    f"Invalid training_satisfaction ratings found: {bad_sat}. Allowed: {sorted(ALLOWED_SATISFACTION_SCORES)}"
                )

    # 7. Validate preferred_learning_method
    invalid_methods = ~cleaned_df["preferred_learning_method"].isin(ALLOWED_LEARNING_METHODS)
    if invalid_methods.any():
        bad_methods = cleaned_df.loc[invalid_methods, "preferred_learning_method"].unique().tolist()
        error_messages.append(
            f"Invalid preferred_learning_method categories found: {bad_methods}. Allowed: {sorted(ALLOWED_LEARNING_METHODS)}"
        )

    # 8. Validate internship_interest
    invalid_intern = ~cleaned_df["internship_interest"].isin(ALLOWED_INTERNSHIP_CHOICES)
    if invalid_intern.any():
        bad_intern = cleaned_df.loc[invalid_intern, "internship_interest"].unique().tolist()
        error_messages.append(
            f"Invalid internship_interest values found: {bad_intern}. Allowed: {sorted(ALLOWED_INTERNSHIP_CHOICES)}"
        )

    # 9. Validate recommendation_score (integers 0 to 10)
    if cleaned_df["recommendation_score"].isnull().any():
        error_messages.append(
            f"Found {cleaned_df['recommendation_score'].isnull().sum()} null values in 'recommendation_score'."
        )
    else:
        numeric_rec = pd.to_numeric(cleaned_df["recommendation_score"], errors="coerce")
        if numeric_rec.isnull().any():
            error_messages.append("Column 'recommendation_score' contains non-numeric values.")
        elif not (numeric_rec % 1 == 0).all():
            error_messages.append("Column 'recommendation_score' contains non-integer floating point values.")
        else:
            cleaned_df["recommendation_score"] = numeric_rec.astype(int)
            invalid_rec = ~cleaned_df["recommendation_score"].isin(ALLOWED_RECOMMENDATION_SCORES)
            if invalid_rec.any():
                bad_rec = cleaned_df.loc[invalid_rec, "recommendation_score"].unique().tolist()
                error_messages.append(
                    f"Invalid recommendation_score values found: {bad_rec}. Allowed: [0..10]"
                )

    # 10. Handle comments (optional text, preserve NaN/null, strip whitespace if present)
    def clean_comment(val: object) -> object:
        if pd.isna(val) or val is None:
            return np.nan
        s = str(val).strip()
        return s if s else np.nan

    cleaned_df["comments"] = cleaned_df["comments"].apply(clean_comment)

    # If any validation errors occurred, fail with complete diagnostic message
    if error_messages:
        combined_error = "\n- ".join(error_messages)
        raise DataValidationError(f"Poll data cleaning validation failed:\n- {combined_error}")

    # Ensure stable column order
    return cleaned_df[REQUIRED_COLUMNS].copy()


def process_and_save_poll_data(
    raw_path: Union[str, Path] = "data/raw/sample_poll_data.csv",
    processed_path: Union[str, Path] = "data/processed/clean_poll_data.csv",
    overwrite: bool = True,
) -> pd.DataFrame:
    """Load raw poll data, apply cleaning validation, and save to the processed directory.

    Safety Rules:
    - Never modifies or overwrites the raw input file.
    - Creates target output directory if it does not exist.
    - Inspects destination file before writing; overwrites only if overwrite=True.
    - Reports row counts, missing values, and execution status.

    Args:
        raw_path: Path to the raw CSV file.
        processed_path: Path where the cleaned CSV should be written.
        overwrite: Whether to overwrite existing processed file (default: True).

    Returns:
        pd.DataFrame: Cleaned and saved DataFrame.
    """
    raw_file = Path(raw_path)
    processed_file = Path(processed_path)

    print(f"[Pipeline] Loading raw poll data from: '{raw_file}'")
    raw_df = load_poll_data(raw_file)
    input_count = len(raw_df)

    print(f"[Pipeline] Cleaning and validating {input_count} records...")
    clean_df = clean_poll_data(raw_df)
    output_count = len(clean_df)

    # Check output file safety policy
    if processed_file.exists():
        if overwrite:
            print(f"[Notice] Processed file '{processed_file}' already exists. Overwriting as requested.")
        else:
            print(f"[Notice] Processed file '{processed_file}' exists and overwrite=False. Skipping write.")
            return clean_df

    # Ensure output directory exists
    processed_file.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(processed_file, index=False)

    print(f"[Success] Cleaned dataset saved to: '{processed_file}'")
    print(f"[Report] Input rows: {input_count} | Output rows: {output_count}")
    print(f"[Report] Missing comments count: {clean_df['comments'].isnull().sum()} / {output_count}")

    return clean_df
