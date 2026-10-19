"""Unit tests for src.visualizations."""

import pandas as pd
import plotly.graph_objects as go
import pytest

from src.visualizations import (
    plot_department_internship_interest,
    plot_department_language_comparison,
    plot_language_distribution,
    plot_learning_method_distribution,
    plot_recommendation_distribution,
    plot_satisfaction_distribution,
)


@pytest.fixture
def deterministic_sample_df() -> pd.DataFrame:
    """Provide a small, deterministic DataFrame with known values."""
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


def test_plot_satisfaction_distribution(deterministic_sample_df: pd.DataFrame) -> None:
    """Test satisfaction distribution figure properties and data values."""
    fig = plot_satisfaction_distribution(deterministic_sample_df)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == "bar"

    # In deterministic_sample_df: ratings 2, 3, 4, 5 each appear once (count=1)
    y_values = list(fig.data[0].y)
    assert y_values == [1, 1, 1, 1]
    assert "Satisfaction" in fig.layout.title.text
    assert "Rating" in fig.layout.xaxis.title.text


def test_plot_satisfaction_distribution_percentage(deterministic_sample_df: pd.DataFrame) -> None:
    """Test percentage mode for satisfaction distribution."""
    fig = plot_satisfaction_distribution(deterministic_sample_df, as_percentage=True)
    # 4 ratings out of 4 -> 25.0% each
    assert list(fig.data[0].y) == [25.0, 25.0, 25.0, 25.0]
    assert "%" in fig.layout.yaxis.title.text


def test_plot_language_distribution(deterministic_sample_df: pd.DataFrame) -> None:
    """Test preferred language distribution trace and categories."""
    fig = plot_language_distribution(deterministic_sample_df)
    assert isinstance(fig, go.Figure)
    assert fig.data[0].type == "bar"

    x_categories = list(fig.data[0].x)
    y_counts = list(fig.data[0].y)
    assert "Python" in x_categories
    # Python count is 2 in deterministic sample
    py_idx = x_categories.index("Python")
    assert y_counts[py_idx] == 2
    assert "Preferred Programming Language" in fig.layout.title.text


def test_plot_learning_method_distribution(deterministic_sample_df: pd.DataFrame) -> None:
    """Test preferred learning method distribution."""
    fig = plot_learning_method_distribution(deterministic_sample_df)
    assert isinstance(fig, go.Figure)
    assert fig.data[0].type == "bar"

    x_categories = list(fig.data[0].x)
    y_counts = list(fig.data[0].y)
    assert "Hands-on Projects" in x_categories
    ho_idx = x_categories.index("Hands-on Projects")
    assert y_counts[ho_idx] == 2  # 2 respondents preferred Hands-on Projects


def test_plot_department_language_comparison(deterministic_sample_df: pd.DataFrame) -> None:
    """Test grouped/stacked department vs language comparison."""
    fig = plot_department_language_comparison(deterministic_sample_df, barmode="group")
    assert isinstance(fig, go.Figure)
    assert fig.layout.barmode == "group"

    # Traces correspond to unique languages
    trace_names = [trace.name for trace in fig.data]
    assert "Python" in trace_names
    assert "Java" in trace_names
    assert "C++" in trace_names

    # Check that x-axis categories contain departments
    for trace in fig.data:
        assert set(trace.x).issubset({"IT", "Commerce", "Science", "Arts"})


def test_plot_department_language_comparison_percentage(deterministic_sample_df: pd.DataFrame) -> None:
    """Test normalized percentage mode for department language comparison."""
    fig = plot_department_language_comparison(deterministic_sample_df, as_percentage=True)
    assert "%" in fig.layout.yaxis.title.text
    # IT cohort: 2 out of 2 are Python -> 100.0%
    py_trace = [t for t in fig.data if t.name == "Python"][0]
    it_idx = list(py_trace.x).index("IT")
    assert py_trace.y[it_idx] == 100.0


def test_plot_recommendation_distribution(deterministic_sample_df: pd.DataFrame) -> None:
    """Test recommendation score distribution covers 0-10 scale."""
    fig = plot_recommendation_distribution(deterministic_sample_df)
    assert isinstance(fig, go.Figure)

    # X-axis should contain all scores '0' through '10'
    x_scores = list(fig.data[0].x)
    expected_scores = [str(i) for i in range(11)]
    assert x_scores == expected_scores

    # Score 10 count is 1, Score 6 count is 1, Score 8 count is 1, Score 4 count is 1, rest 0
    y_counts = list(fig.data[0].y)
    assert y_counts[10] == 1
    assert y_counts[0] == 0


def test_plot_department_internship_interest(deterministic_sample_df: pd.DataFrame) -> None:
    """Test department vs internship interest chart."""
    fig = plot_department_internship_interest(deterministic_sample_df)
    assert isinstance(fig, go.Figure)

    trace_names = [trace.name for trace in fig.data]
    assert "Yes" in trace_names
    assert "No" in trace_names

    # In IT, both respondents answered Yes
    yes_trace = [t for t in fig.data if t.name == "Yes"][0]
    it_idx = list(yes_trace.x).index("IT")
    assert yes_trace.y[it_idx] == 2


def test_visualizations_empty_dataframe_raises_error() -> None:
    """Test that all visualization functions raise ValueError on empty DataFrame."""
    empty_df = pd.DataFrame(
        columns=[
            "training_satisfaction",
            "preferred_language",
            "preferred_learning_method",
            "department",
            "recommendation_score",
            "internship_interest",
        ]
    )

    with pytest.raises(ValueError, match="Cannot perform statistical analysis on an empty DataFrame"):
        plot_satisfaction_distribution(empty_df)

    with pytest.raises(ValueError, match="Cannot perform statistical analysis on an empty DataFrame"):
        plot_language_distribution(empty_df)

    with pytest.raises(ValueError, match="Cannot perform statistical analysis on an empty DataFrame"):
        plot_learning_method_distribution(empty_df)

    with pytest.raises(ValueError, match="Cannot perform statistical analysis on an empty DataFrame"):
        plot_department_language_comparison(empty_df)

    with pytest.raises(ValueError, match="Cannot perform statistical analysis on an empty DataFrame"):
        plot_recommendation_distribution(empty_df)

    with pytest.raises(ValueError, match="Cannot perform statistical analysis on an empty DataFrame"):
        plot_department_internship_interest(empty_df)


def test_visualizations_missing_columns_raise_error(deterministic_sample_df: pd.DataFrame) -> None:
    """Test that missing required columns raise descriptive ValueError."""
    dropped_df = deterministic_sample_df.drop(columns=["department"])
    with pytest.raises(ValueError, match="missing required analysis columns"):
        plot_department_language_comparison(dropped_df)


def test_visualizations_input_not_mutated(deterministic_sample_df: pd.DataFrame) -> None:
    """Test that visualization calls do not mutate the input DataFrame."""
    df_copy = deterministic_sample_df.copy(deep=True)
    _ = plot_satisfaction_distribution(deterministic_sample_df)
    _ = plot_language_distribution(deterministic_sample_df)
    _ = plot_department_language_comparison(deterministic_sample_df)

    pd.testing.assert_frame_equal(deterministic_sample_df, df_copy)


def test_visualizations_dynamic_update_on_data_change(deterministic_sample_df: pd.DataFrame) -> None:
    """Test that changing input data dynamically alters plotted figure values."""
    fig_initial = plot_satisfaction_distribution(deterministic_sample_df)
    initial_y = list(fig_initial.data[0].y)

    # Append an additional rating of 5
    modified_df = pd.concat(
        [
            deterministic_sample_df,
            pd.DataFrame(
                [
                    {
                        "response_id": "R05",
                        "department": "IT",
                        "study_year": 3,
                        "preferred_language": "Python",
                        "training_satisfaction": 5,
                        "preferred_learning_method": "Online Courses",
                        "internship_interest": "Yes",
                        "recommendation_score": 9,
                        "comments": None,
                    }
                ]
            ),
        ],
        ignore_index=True,
    )

    fig_updated = plot_satisfaction_distribution(modified_df)
    updated_y = list(fig_updated.data[0].y)

    assert initial_y != updated_y
    # Rating 5 count increased from 1 to 2
    assert updated_y[-1] == 2
