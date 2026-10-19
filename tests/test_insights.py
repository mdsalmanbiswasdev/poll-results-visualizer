"""Unit tests for src.insights."""

import pandas as pd
import pytest

from src.insights import (
    generate_all_insights,
    get_missing_comments_insight,
    get_overall_internship_insight,
    get_recommendation_score_insight,
    get_satisfaction_insight,
    get_top_internship_department_insight,
    get_top_language_insight,
    get_top_learning_method_insight,
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


def test_get_top_language_insight(deterministic_sample_df: pd.DataFrame) -> None:
    """Test top language identification, count, percentage, and tie flag."""
    insight = get_top_language_insight(deterministic_sample_df)

    assert insight["id"] == "top_language"
    assert insight["metric_value"] == "Python"
    assert insight["percentage"] == 50.0
    assert insight["denominator"] == 4
    assert insight["is_tie"] is False
    assert insight["details"]["Python"] == 2
    assert "Python with 2 responses (50.0% of N=4)" in insight["summary_text"]


def test_get_top_language_insight_tie_handling() -> None:
    """Test deterministic tie handling when two languages share top count."""
    tie_df = pd.DataFrame(
        {
            "preferred_language": ["Python", "Python", "Java", "Java"],
        }
    )
    insight = get_top_language_insight(tie_df)

    assert insight["is_tie"] is True
    assert insight["metric_value"] == "Java, Python"  # Sorted alphabetically
    assert insight["percentage"] == 50.0
    assert "Tied for most preferred language: Java, Python" in insight["summary_text"]


def test_get_top_learning_method_insight(deterministic_sample_df: pd.DataFrame) -> None:
    """Test top learning method identification."""
    insight = get_top_learning_method_insight(deterministic_sample_df)

    assert insight["id"] == "top_learning_method"
    assert insight["metric_value"] == "Hands-on Projects"
    assert insight["percentage"] == 50.0
    assert insight["is_tie"] is False
    assert insight["details"]["Hands-on Projects"] == 2


def test_get_satisfaction_insight(deterministic_sample_df: pd.DataFrame) -> None:
    """Test satisfaction mean and favorable proportion calculations."""
    insight = get_satisfaction_insight(deterministic_sample_df)

    # Ratings: [3, 4, 5, 2] -> Mean = 3.5, Favorable (4 & 5) = 2/4 = 50.0%
    assert insight["id"] == "training_satisfaction"
    assert insight["metric_value"] == 3.5
    assert insight["percentage"] == 50.0
    assert insight["details"]["median"] == 3.5
    assert insight["details"]["favorable_count"] == 2
    assert "Average training satisfaction is 3.50 / 5.0" in insight["summary_text"]


def test_get_top_internship_department_insight(deterministic_sample_df: pd.DataFrame) -> None:
    """Test department-level internship interest percentage calculation and tie detection."""
    insight = get_top_internship_department_insight(deterministic_sample_df)

    # IT has 2 Yes / 2 Total = 100.0%
    # Commerce has 1 Yes / 1 Total = 100.0%
    # Science has 0 Yes / 1 Total = 0.0%
    # IT and Commerce tie at 100.0%
    assert insight["id"] == "top_internship_department"
    assert insight["percentage"] == 100.0
    assert insight["is_tie"] is True
    assert insight["metric_value"] == "Commerce, IT"
    assert "Tied for highest internship placement interest" in insight["summary_text"]


def test_get_overall_internship_insight(deterministic_sample_df: pd.DataFrame) -> None:
    """Test overall cohort internship interest percentage."""
    insight = get_overall_internship_insight(deterministic_sample_df)

    # 3 Yes out of 4 responses -> 75.0%
    assert insight["id"] == "overall_internship"
    assert insight["metric_value"] == 75.0
    assert insight["percentage"] == 75.0
    assert insight["denominator"] == 4
    assert insight["details"]["yes_count"] == 3
    assert insight["details"]["no_count"] == 1
    assert "75.0%" in insight["summary_text"]


def test_get_recommendation_score_insight(deterministic_sample_df: pd.DataFrame) -> None:
    """Test average recommendation score and promoter calculation."""
    insight = get_recommendation_score_insight(deterministic_sample_df)

    # Scores: [6, 8, 10, 4] -> Mean = 7.0, Promoters (9-10) = 1 (10) -> 25.0%
    assert insight["id"] == "recommendation_score"
    assert insight["metric_value"] == 7.0
    assert insight["percentage"] == 25.0
    assert insight["details"]["median"] == 7.0
    assert insight["details"]["promoter_count"] == 1
    assert "Average recommendation score is 7.00 / 10.0" in insight["summary_text"]


def test_get_missing_comments_insight(deterministic_sample_df: pd.DataFrame) -> None:
    """Test missing comments audit counts and feedback rates."""
    insight = get_missing_comments_insight(deterministic_sample_df)

    # Comments: 2 provided, 2 missing out of 4 (50.0%)
    assert insight["id"] == "missing_comments"
    assert insight["metric_value"] == 2
    assert insight["percentage"] == 50.0
    assert insight["details"]["provided_count"] == 2
    assert insight["details"]["missing_count"] == 2
    assert "2 of 4 respondents (50.0%) provided optional written feedback" in insight["summary_text"]


def test_generate_all_insights_structure(deterministic_sample_df: pd.DataFrame) -> None:
    """Test master insight generator returns all 7 structured records."""
    all_insights = generate_all_insights(deterministic_sample_df)

    assert isinstance(all_insights, list)
    assert len(all_insights) == 7
    expected_ids = [
        "top_language",
        "top_learning_method",
        "training_satisfaction",
        "top_internship_department",
        "overall_internship",
        "recommendation_score",
        "missing_comments",
    ]
    actual_ids = [item["id"] for item in all_insights]
    assert actual_ids == expected_ids

    # Verify each insight dictionary has standard schema
    for item in all_insights:
        assert "id" in item
        assert "title" in item
        assert "metric_value" in item
        assert "percentage" in item
        assert "denominator" in item
        assert "summary_text" in item
        assert "details" in item


def test_insights_empty_dataframe_raises_error() -> None:
    """Test that insight functions reject empty DataFrames with ValueError."""
    empty_df = pd.DataFrame(columns=["preferred_language", "comments"])

    with pytest.raises(ValueError, match="Cannot perform statistical analysis on an empty DataFrame"):
        get_top_language_insight(empty_df)

    with pytest.raises(ValueError, match="Cannot perform statistical analysis on an empty DataFrame"):
        get_missing_comments_insight(empty_df)


def test_insights_missing_column_raises_error(deterministic_sample_df: pd.DataFrame) -> None:
    """Test that missing required columns raise descriptive ValueError."""
    dropped_df = deterministic_sample_df.drop(columns=["preferred_language"])
    with pytest.raises(ValueError, match="missing required analysis columns"):
        get_top_language_insight(dropped_df)


def test_insights_input_not_mutated(deterministic_sample_df: pd.DataFrame) -> None:
    """Test that insight functions do not mutate the input DataFrame."""
    df_copy = deterministic_sample_df.copy(deep=True)
    _ = generate_all_insights(deterministic_sample_df)
    pd.testing.assert_frame_equal(deterministic_sample_df, df_copy)


def test_insights_dynamic_sensitivity_on_data_change(deterministic_sample_df: pd.DataFrame) -> None:
    """Test that outputs dynamically adjust when underlying data changes."""
    init_insight = get_overall_internship_insight(deterministic_sample_df)
    assert init_insight["percentage"] == 75.0

    # Add 2 more respondents answering 'No'
    extended_df = pd.concat(
        [
            deterministic_sample_df,
            pd.DataFrame(
                [
                    {
                        "response_id": "R05",
                        "department": "Science",
                        "study_year": 3,
                        "preferred_language": "C++",
                        "training_satisfaction": 4,
                        "preferred_learning_method": "Online Courses",
                        "internship_interest": "No",
                        "recommendation_score": 5,
                        "comments": None,
                    },
                    {
                        "response_id": "R06",
                        "department": "Arts",
                        "study_year": 1,
                        "preferred_language": "JavaScript",
                        "training_satisfaction": 3,
                        "preferred_learning_method": "Classroom Lectures",
                        "internship_interest": "No",
                        "recommendation_score": 6,
                        "comments": "Okay",
                    },
                ]
            ),
        ],
        ignore_index=True,
    )

    updated_insight = get_overall_internship_insight(extended_df)
    # Total = 6, Yes = 3 -> 50.0%
    assert updated_insight["percentage"] == 50.0
    assert updated_insight["denominator"] == 6
    assert updated_insight["details"]["yes_count"] == 3
    assert updated_insight["details"]["no_count"] == 3
