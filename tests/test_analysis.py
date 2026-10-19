"""Unit tests for src.analysis."""

import pandas as pd
import pytest

from src.analysis import (
    get_categorical_frequency,
    get_cross_tabulation,
    get_dataset_overview,
    get_department_internship_crosstab,
    get_department_language_crosstab,
    get_internship_interest_summary,
    get_learning_method_distribution,
    get_missing_value_summary,
    get_numeric_summary,
    get_recommendation_distribution,
    get_satisfaction_distribution,
)


@pytest.fixture
def deterministic_sample_df() -> pd.DataFrame:
    """Provide a small, deterministic DataFrame with known metrics."""
    return pd.DataFrame(
        {
            "response_id": ["R01", "R02", "R03", "R04"],
            "department": ["IT", "IT", "Science", "Commerce"],
            "study_year": [1, 2, 2, 4],
            "preferred_language": ["Python", "Python", "Java", "C++"],
            "training_satisfaction": [3, 4, 5, 2],
            "preferred_learning_method": [
                "Hands-on Projects",
                "Hands-on Projects",
                "Video Tutorials",
                "Classroom Lectures",
            ],
            "internship_interest": ["Yes", "Yes", "No", "Yes"],
            "recommendation_score": [6, 8, 10, 4],
            "comments": ["Good", None, "Fine", None],
        }
    )


def test_get_dataset_overview(deterministic_sample_df: pd.DataFrame) -> None:
    """Test that overview returns exact row count, column count, and dtypes."""
    overview = get_dataset_overview(deterministic_sample_df)
    assert overview["row_count"] == 4
    assert overview["column_count"] == 9
    assert "response_id" in overview["columns"]
    assert "study_year" in overview["dtypes"]


def test_get_dataset_overview_type_error() -> None:
    """Test TypeError on non-DataFrame input."""
    with pytest.raises(TypeError, match="Expected pandas DataFrame"):
        get_dataset_overview([1, 2, 3])  # type: ignore


def test_get_missing_value_summary(deterministic_sample_df: pd.DataFrame) -> None:
    """Test missing value counts and percentage denominators."""
    missing_df = get_missing_value_summary(deterministic_sample_df)
    assert len(missing_df) == 9

    comments_row = missing_df[missing_df["column"] == "comments"].iloc[0]
    assert comments_row["missing_count"] == 2
    assert comments_row["missing_percentage"] == 50.0

    dept_row = missing_df[missing_df["column"] == "department"].iloc[0]
    assert dept_row["missing_count"] == 0
    assert dept_row["missing_percentage"] == 0.0


def test_get_missing_value_summary_empty_df() -> None:
    """Test missing value summary on empty DataFrame returns 0.0 percentages."""
    empty_df = pd.DataFrame(columns=["a", "b"])
    res = get_missing_value_summary(empty_df)
    assert (res["missing_percentage"] == 0.0).all()
    assert (res["missing_count"] == 0).all()


def test_get_numeric_summary(deterministic_sample_df: pd.DataFrame) -> None:
    """Test numeric summary against explicitly calculated hand metrics."""
    stats = get_numeric_summary(deterministic_sample_df)

    # study_year: [1, 2, 2, 4] -> mean=2.25, median=2.0, min=1, max=4
    sy = stats[stats["column"] == "study_year"].iloc[0]
    assert sy["count"] == 4
    assert sy["mean"] == 2.25
    assert sy["median"] == 2.0
    assert sy["min"] == 1.0
    assert sy["max"] == 4.0

    # training_satisfaction: [3, 4, 5, 2] -> mean=3.5, median=3.5, min=2, max=5
    ts = stats[stats["column"] == "training_satisfaction"].iloc[0]
    assert ts["mean"] == 3.5
    assert ts["median"] == 3.5
    assert ts["min"] == 2.0
    assert ts["max"] == 5.0

    # recommendation_score: [6, 8, 10, 4] -> mean=7.0, median=7.0, min=4, max=10
    rs = stats[stats["column"] == "recommendation_score"].iloc[0]
    assert rs["mean"] == 7.0
    assert rs["median"] == 7.0
    assert rs["min"] == 4.0
    assert rs["max"] == 10.0


def test_get_numeric_summary_missing_column(deterministic_sample_df: pd.DataFrame) -> None:
    """Test that missing required column raises ValueError."""
    with pytest.raises(ValueError, match="missing required analysis columns"):
        get_numeric_summary(deterministic_sample_df, columns=["non_existent_col"])


def test_get_categorical_frequency(deterministic_sample_df: pd.DataFrame) -> None:
    """Test categorical counts and percentage calculations."""
    freq = get_categorical_frequency(deterministic_sample_df, "department")

    # IT: 2 (50.0%), Science: 1 (25.0%), Commerce: 1 (25.0%)
    it_row = freq[freq["category"] == "IT"].iloc[0]
    assert it_row["count"] == 2
    assert it_row["percentage"] == 50.0

    sci_row = freq[freq["category"] == "Science"].iloc[0]
    assert sci_row["count"] == 1
    assert sci_row["percentage"] == 25.0


def test_get_cross_tabulation(deterministic_sample_df: pd.DataFrame) -> None:
    """Test cross-tabulation table counts."""
    ct = get_cross_tabulation(deterministic_sample_df, "department", "preferred_language")

    assert ct.loc["IT", "Python"] == 2
    assert ct.loc["Science", "Java"] == 1
    assert ct.loc["Commerce", "C++"] == 1
    assert ct.loc["IT", "Java"] == 0


def test_get_cross_tabulation_normalized(deterministic_sample_df: pd.DataFrame) -> None:
    """Test normalized cross-tabulation percentages."""
    ct_norm = get_cross_tabulation(
        deterministic_sample_df, "department", "preferred_language", normalize="all"
    )
    # Total responses = 4. IT+Python is 2 -> 50.0%
    assert ct_norm.loc["IT", "Python"] == 50.0
    assert ct_norm.loc["Science", "Java"] == 25.0


def test_domain_analysis_convenience_functions(deterministic_sample_df: pd.DataFrame) -> None:
    """Test specific domain convenience wrappers."""
    dept_lang = get_department_language_crosstab(deterministic_sample_df)
    assert dept_lang.loc["IT", "Python"] == 2

    dept_intern = get_department_internship_crosstab(deterministic_sample_df)
    assert dept_intern.loc["IT", "Yes"] == 2

    sat_dist = get_satisfaction_distribution(deterministic_sample_df)
    assert len(sat_dist) == 4  # ratings 2, 3, 4, 5 each appear once or twice

    learn_dist = get_learning_method_distribution(deterministic_sample_df)
    assert learn_dist[learn_dist["category"] == "Hands-on Projects"]["count"].iloc[0] == 2

    rec_dist = get_recommendation_distribution(deterministic_sample_df)
    assert len(rec_dist) == 4

    intern_summary = get_internship_interest_summary(deterministic_sample_df)
    yes_row = intern_summary[intern_summary["category"] == "Yes"].iloc[0]
    assert yes_row["count"] == 3
    assert yes_row["percentage"] == 75.0


def test_empty_dataframe_raises_error() -> None:
    """Test that analytical functions reject empty DataFrames with clear ValueError."""
    empty_df = pd.DataFrame(columns=["department", "study_year"])
    with pytest.raises(ValueError, match="Cannot perform statistical analysis on an empty DataFrame"):
        get_numeric_summary(empty_df, columns=["study_year"])

    with pytest.raises(ValueError, match="Cannot perform statistical analysis on an empty DataFrame"):
        get_categorical_frequency(empty_df, "department")


def test_input_dataframe_not_mutated(deterministic_sample_df: pd.DataFrame) -> None:
    """Test that analytical functions do not mutate the input DataFrame."""
    df_copy = deterministic_sample_df.copy(deep=True)
    _ = get_numeric_summary(deterministic_sample_df)
    _ = get_categorical_frequency(deterministic_sample_df, "department")
    _ = get_cross_tabulation(deterministic_sample_df, "department", "preferred_language")

    pd.testing.assert_frame_equal(deterministic_sample_df, df_copy)


def test_dynamic_recalculation_on_data_change(deterministic_sample_df: pd.DataFrame) -> None:
    """Test that outputs dynamically change and do not contain hard-coded results."""
    initial_intern = get_internship_interest_summary(deterministic_sample_df)
    assert initial_intern[initial_intern["category"] == "No"]["count"].iloc[0] == 1
    assert initial_intern[initial_intern["category"] == "No"]["percentage"].iloc[0] == 25.0

    # Add a 5th response with 'No'
    extended_df = pd.concat(
        [
            deterministic_sample_df,
            pd.DataFrame(
                [
                    {
                        "response_id": "R05",
                        "department": "Arts",
                        "study_year": 3,
                        "preferred_language": "JavaScript",
                        "training_satisfaction": 4,
                        "preferred_learning_method": "Online Courses",
                        "internship_interest": "No",
                        "recommendation_score": 8,
                        "comments": None,
                    }
                ]
            ),
        ],
        ignore_index=True,
    )

    updated_intern = get_internship_interest_summary(extended_df)
    # Total = 5, No = 2 -> 40.0%
    assert updated_intern[updated_intern["category"] == "No"]["count"].iloc[0] == 2
    assert updated_intern[updated_intern["category"] == "No"]["percentage"].iloc[0] == 40.0
