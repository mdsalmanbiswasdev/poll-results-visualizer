"""Unit tests for src.data_cleaning."""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.data_cleaning import (
    DataValidationError,
    clean_poll_data,
    process_and_save_poll_data,
)
from src.data_loader import REQUIRED_COLUMNS


@pytest.fixture
def sample_valid_df() -> pd.DataFrame:
    """Provide a minimal valid in-memory DataFrame."""
    return pd.DataFrame(
        {
            "response_id": ["RESP_0001", "RESP_0002", "RESP_0003"],
            "department": ["IT", "Commerce", "Science"],
            "study_year": [1, 2, 3],
            "preferred_language": ["Python", "Java", "C++"],
            "training_satisfaction": [4, 5, 3],
            "preferred_learning_method": [
                "Hands-on Projects",
                "Video Tutorials",
                "Classroom Lectures",
            ],
            "internship_interest": ["Yes", "No", "Yes"],
            "recommendation_score": [8, 9, 7],
            "comments": ["Great session", np.nan, "Very helpful"],
        }
    )


def test_clean_poll_data_valid(sample_valid_df: pd.DataFrame) -> None:
    """Test cleaning on a valid dataset succeeds with expected shape and columns."""
    cleaned = clean_poll_data(sample_valid_df)
    assert len(cleaned) == 3
    assert list(cleaned.columns) == REQUIRED_COLUMNS
    assert cleaned["comments"].isnull().sum() == 1


def test_clean_poll_data_preserves_input(sample_valid_df: pd.DataFrame) -> None:
    """Test that input DataFrame is not mutated in-place."""
    input_copy = sample_valid_df.copy(deep=True)
    _ = clean_poll_data(sample_valid_df)
    pd.testing.assert_frame_equal(sample_valid_df, input_copy)


def test_clean_poll_data_whitespace_trimming(sample_valid_df: pd.DataFrame) -> None:
    """Test that leading/trailing whitespaces in string fields are safely trimmed."""
    df_with_spaces = sample_valid_df.copy()
    df_with_spaces.loc[0, "response_id"] = "  RESP_0001  "
    df_with_spaces.loc[0, "department"] = " IT "
    df_with_spaces.loc[0, "preferred_language"] = " Python "
    df_with_spaces.loc[0, "comments"] = "  Great session  "

    cleaned = clean_poll_data(df_with_spaces)
    assert cleaned.loc[0, "response_id"] == "RESP_0001"
    assert cleaned.loc[0, "department"] == "IT"
    assert cleaned.loc[0, "preferred_language"] == "Python"
    assert cleaned.loc[0, "comments"] == "Great session"


def test_clean_poll_data_missing_required_value(sample_valid_df: pd.DataFrame) -> None:
    """Test that missing values in required fields raise DataValidationError."""
    df_missing = sample_valid_df.copy()
    df_missing.loc[1, "study_year"] = np.nan

    with pytest.raises(DataValidationError, match="null values in 'study_year'"):
        clean_poll_data(df_missing)


def test_clean_poll_data_duplicate_response_id(sample_valid_df: pd.DataFrame) -> None:
    """Test that duplicate response_id values raise DataValidationError."""
    df_dups = sample_valid_df.copy()
    df_dups.loc[1, "response_id"] = "RESP_0001"  # duplicate of row 0

    with pytest.raises(DataValidationError, match="duplicate response_id"):
        clean_poll_data(df_dups)


def test_clean_poll_data_invalid_numeric_values(sample_valid_df: pd.DataFrame) -> None:
    """Test that non-numeric entries in numeric fields raise DataValidationError."""
    df_invalid = sample_valid_df.copy()
    df_invalid["study_year"] = df_invalid["study_year"].astype(object)
    df_invalid.loc[0, "study_year"] = "First Year"  # string instead of integer

    with pytest.raises(DataValidationError, match="non-numeric values"):
        clean_poll_data(df_invalid)


def test_clean_poll_data_non_integer_floats(sample_valid_df: pd.DataFrame) -> None:
    """Test that floating point values in integer fields raise DataValidationError."""
    df_float = sample_valid_df.copy()
    df_float["study_year"] = df_float["study_year"].astype(float)
    df_float.loc[0, "study_year"] = 2.5

    with pytest.raises(DataValidationError, match="non-integer floating point values"):
        clean_poll_data(df_float)




def test_clean_poll_data_out_of_range_satisfaction(sample_valid_df: pd.DataFrame) -> None:
    """Test that satisfaction scores outside 1-5 raise DataValidationError."""
    df_bad_sat = sample_valid_df.copy()
    df_bad_sat.loc[0, "training_satisfaction"] = 6

    with pytest.raises(DataValidationError, match="Invalid training_satisfaction ratings"):
        clean_poll_data(df_bad_sat)


def test_clean_poll_data_out_of_range_recommendation(sample_valid_df: pd.DataFrame) -> None:
    """Test that recommendation scores outside 0-10 raise DataValidationError."""
    df_bad_rec = sample_valid_df.copy()
    df_bad_rec.loc[0, "recommendation_score"] = 15

    with pytest.raises(DataValidationError, match="Invalid recommendation_score values"):
        clean_poll_data(df_bad_rec)


def test_clean_poll_data_unknown_category_label(sample_valid_df: pd.DataFrame) -> None:
    """Test that unrecognized department categories raise DataValidationError."""
    df_bad_cat = sample_valid_df.copy()
    df_bad_cat.loc[0, "department"] = "Biotechnology"

    with pytest.raises(DataValidationError, match="Invalid department categories found"):
        clean_poll_data(df_bad_cat)


def test_clean_poll_data_preserves_optional_comments(sample_valid_df: pd.DataFrame) -> None:
    """Test that missing optional comments remain NaN and are not dropped or replaced."""
    cleaned = clean_poll_data(sample_valid_df)
    assert pd.isna(cleaned.loc[1, "comments"])
    assert len(cleaned) == 3


def test_clean_poll_data_empty_dataframe() -> None:
    """Test that an empty DataFrame with valid columns returns an empty cleaned DataFrame."""
    empty_df = pd.DataFrame(columns=REQUIRED_COLUMNS)
    cleaned = clean_poll_data(empty_df)
    assert cleaned.empty
    assert list(cleaned.columns) == REQUIRED_COLUMNS


def test_clean_poll_data_stable_schema(sample_valid_df: pd.DataFrame) -> None:
    """Test that output DataFrame preserves exact column order and integer dtypes."""
    cleaned = clean_poll_data(sample_valid_df)
    assert list(cleaned.columns) == REQUIRED_COLUMNS
    assert cleaned["study_year"].dtype == np.int64 or cleaned["study_year"].dtype == int
    assert cleaned["training_satisfaction"].dtype == np.int64 or cleaned["training_satisfaction"].dtype == int
    assert cleaned["recommendation_score"].dtype == np.int64 or cleaned["recommendation_score"].dtype == int


def test_process_and_save_poll_data_pipeline(tmp_path: Path, sample_valid_df: pd.DataFrame) -> None:
    """Test end-to-end saving pipeline with isolated temp directory."""
    raw_path = tmp_path / "raw.csv"
    processed_path = tmp_path / "processed" / "clean.csv"

    sample_valid_df.to_csv(raw_path, index=False)
    initial_raw_hash = raw_path.read_bytes()

    clean_df = process_and_save_poll_data(
        raw_path=raw_path,
        processed_path=processed_path,
        overwrite=True,
    )

    assert processed_path.exists()
    assert len(clean_df) == 3
    # Verify raw file was not modified
    assert raw_path.read_bytes() == initial_raw_hash
