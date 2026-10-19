"""Unit tests for src.data_loader."""

from pathlib import Path
import pytest
import pandas as pd

from src.data_loader import REQUIRED_COLUMNS, load_poll_data


@pytest.fixture
def valid_poll_csv(tmp_path: Path) -> Path:
    """Create a temporary valid CSV file containing all required columns."""
    csv_file = tmp_path / "valid_poll.csv"
    df = pd.DataFrame(
        {
            "response_id": ["RESP_001", "RESP_002"],
            "department": ["IT", "Commerce"],
            "study_year": [1, 2],
            "preferred_language": ["Python", "Java"],
            "training_satisfaction": [4, 5],
            "preferred_learning_method": ["Hands-on Projects", "Video Tutorials"],
            "internship_interest": ["Yes", "No"],
            "recommendation_score": [8, 9],
            "comments": ["Good", None],
        }
    )
    df.to_csv(csv_file, index=False)
    return csv_file


def test_load_poll_data_success(valid_poll_csv: Path) -> None:
    """Test successful loading of a valid CSV file."""
    df = load_poll_data(valid_poll_csv)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == REQUIRED_COLUMNS


def test_load_poll_data_missing_file(tmp_path: Path) -> None:
    """Test that loading a non-existent file raises FileNotFoundError."""
    non_existent = tmp_path / "does_not_exist.csv"
    with pytest.raises(FileNotFoundError, match="Poll data file not found at"):
        load_poll_data(non_existent)


def test_load_poll_data_directory_path(tmp_path: Path) -> None:
    """Test that passing a directory path raises ValueError."""
    with pytest.raises(ValueError, match="Provided path is a directory"):
        load_poll_data(tmp_path)


def test_load_poll_data_empty_zero_byte_file(tmp_path: Path) -> None:
    """Test that loading a 0-byte file raises ValueError."""
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="is completely empty"):
        load_poll_data(empty_file)


def test_load_poll_data_empty_content(tmp_path: Path) -> None:
    """Test that loading a file with only whitespace raises ValueError."""
    whitespace_file = tmp_path / "whitespace.csv"
    whitespace_file.write_text("   \n   \n", encoding="utf-8")
    with pytest.raises(ValueError, match="contains no data or columns"):
        load_poll_data(whitespace_file)


def test_load_poll_data_missing_required_columns(tmp_path: Path) -> None:
    """Test that missing required columns raises ValueError identifying missing fields."""
    incomplete_file = tmp_path / "incomplete.csv"
    df = pd.DataFrame(
        {
            "response_id": ["RESP_001"],
            "department": ["IT"],
            # Missing remaining 7 columns
        }
    )
    df.to_csv(incomplete_file, index=False)

    with pytest.raises(ValueError, match="missing required columns"):
        load_poll_data(incomplete_file)


def test_load_poll_data_preserves_column_order(valid_poll_csv: Path) -> None:
    """Test that loader does not alter or reorder the raw columns."""
    df = load_poll_data(valid_poll_csv)
    assert list(df.columns) == REQUIRED_COLUMNS
