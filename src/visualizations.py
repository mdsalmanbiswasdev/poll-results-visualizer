"""Interactive Visualization Module for Poll Results Visualizer.

This module provides reusable Plotly figure generators for survey analysis,
supporting both exploratory work and direct embedding in Streamlit dashboards.

All visualizations:
- Dynamically leverage analytical aggregations from `src.analysis`.
- Never modify the input DataFrame.
- Guard against empty DataFrames and missing required columns.
- Provide descriptive titles, axis labels, legends, and hover templates.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd
import plotly.graph_objects as go

from src.analysis import (
    _validate_input_dataframe,
    get_categorical_frequency,
    get_department_internship_crosstab,
    get_department_language_crosstab,
    get_learning_method_distribution,
    get_recommendation_distribution,
    get_satisfaction_distribution,
)

# Standard accessible color palette
CHART_COLOR_PRIMARY = "#2563EB"       # Royal Blue
CHART_COLOR_ACCENT = "#10B981"        # Emerald Green
PALETTE_CATEGORICAL = [
    "#2563EB",  # Blue
    "#F59E0B",  # Amber
    "#10B981",  # Emerald
    "#8B5CF6",  # Purple
    "#EC4899",  # Pink
    "#06B6D4",  # Cyan
]


def plot_satisfaction_distribution(
    df: pd.DataFrame,
    as_percentage: bool = False,
) -> go.Figure:
    """Generate an interactive bar chart of training satisfaction ratings (1 to 5).

    Args:
        df: Input survey DataFrame.
        as_percentage: If True, plots percentage with denominator N; else counts.

    Returns:
        go.Figure: Interactive Plotly figure.

    Raises:
        ValueError: If df is empty or 'training_satisfaction' is missing.
    """
    _validate_input_dataframe(df, required_cols=["training_satisfaction"], allow_empty=False)

    dist_df = get_satisfaction_distribution(df)
    total_n = len(df)

    # Ensure ratings 1 through 5 are sorted numerically
    dist_df["category_int"] = dist_df["category"].astype(int)
    dist_df = dist_df.sort_values("category_int").reset_index(drop=True)

    y_vals = dist_df["percentage"] if as_percentage else dist_df["count"]
    y_title = f"Percentage of Responses (%) [Denominator N={total_n}]" if as_percentage else "Number of Responses"

    hover_text = [
        f"Rating: {row['category']} / 5<br>Count: {row['count']}<br>Share: {row['percentage']}% (N={total_n})"
        for _, row in dist_df.iterrows()
    ]

    fig = go.Figure(
        data=[
            go.Bar(
                x=[f"Rating {cat}" for cat in dist_df["category"]],
                y=y_vals,
                text=[f"{val:.1f}%" if as_percentage else str(int(val)) for val in y_vals],
                textposition="auto",
                hoverinfo="text",
                hovertext=hover_text,
                marker_color=CHART_COLOR_PRIMARY,
            )
        ]
    )

    fig.update_layout(
        title=f"Training Satisfaction Distribution (Total N={total_n})",
        xaxis_title="Satisfaction Rating (1: Lowest to 5: Highest)",
        yaxis_title=y_title,
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def plot_language_distribution(
    df: pd.DataFrame,
    as_percentage: bool = False,
) -> go.Figure:
    """Generate an interactive bar chart of preferred programming languages.

    Args:
        df: Input survey DataFrame.
        as_percentage: If True, plots percentages; else response counts.

    Returns:
        go.Figure: Interactive Plotly figure.

    Raises:
        ValueError: If df is empty or 'preferred_language' is missing.
    """
    _validate_input_dataframe(df, required_cols=["preferred_language"], allow_empty=False)

    dist_df = get_categorical_frequency(df, "preferred_language")
    total_n = len(df)

    y_vals = dist_df["percentage"] if as_percentage else dist_df["count"]
    y_title = f"Percentage of Responses (%) [N={total_n}]" if as_percentage else "Number of Responses"

    hover_text = [
        f"Language: {row['category']}<br>Count: {row['count']}<br>Share: {row['percentage']}% (N={total_n})"
        for _, row in dist_df.iterrows()
    ]

    fig = go.Figure(
        data=[
            go.Bar(
                x=dist_df["category"],
                y=y_vals,
                text=[f"{val:.1f}%" if as_percentage else str(int(val)) for val in y_vals],
                textposition="auto",
                hoverinfo="text",
                hovertext=hover_text,
                marker_color=PALETTE_CATEGORICAL[: len(dist_df)],
            )
        ]
    )

    fig.update_layout(
        title=f"Preferred Programming Language Distribution (Total N={total_n})",
        xaxis_title="Programming Language",
        yaxis_title=y_title,
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def plot_learning_method_distribution(
    df: pd.DataFrame,
    as_percentage: bool = False,
) -> go.Figure:
    """Generate an interactive bar chart of preferred learning methods.

    Args:
        df: Input survey DataFrame.
        as_percentage: If True, plots percentages; else counts.

    Returns:
        go.Figure: Interactive Plotly figure.

    Raises:
        ValueError: If df is empty or 'preferred_learning_method' is missing.
    """
    _validate_input_dataframe(df, required_cols=["preferred_learning_method"], allow_empty=False)

    dist_df = get_learning_method_distribution(df)
    total_n = len(df)

    y_vals = dist_df["percentage"] if as_percentage else dist_df["count"]
    y_title = f"Percentage of Responses (%) [N={total_n}]" if as_percentage else "Number of Responses"

    hover_text = [
        f"Method: {row['category']}<br>Count: {row['count']}<br>Share: {row['percentage']}% (N={total_n})"
        for _, row in dist_df.iterrows()
    ]

    fig = go.Figure(
        data=[
            go.Bar(
                x=dist_df["category"],
                y=y_vals,
                text=[f"{val:.1f}%" if as_percentage else str(int(val)) for val in y_vals],
                textposition="auto",
                hoverinfo="text",
                hovertext=hover_text,
                marker_color=CHART_COLOR_ACCENT,
            )
        ]
    )

    fig.update_layout(
        title=f"Preferred Learning Method Distribution (Total N={total_n})",
        xaxis_title="Learning Method",
        yaxis_title=y_title,
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def plot_department_language_comparison(
    df: pd.DataFrame,
    barmode: str = "group",
    as_percentage: bool = False,
) -> go.Figure:
    """Generate a grouped or stacked bar chart comparing language preferences by department.

    Args:
        df: Input survey DataFrame.
        barmode: 'group' for grouped bars or 'stack' for stacked bars.
        as_percentage: If True, normalizes percentages within each department (row %);
                       else plots counts.

    Returns:
        go.Figure: Interactive Plotly figure.

    Raises:
        ValueError: If df is empty or required columns are missing.
    """
    _validate_input_dataframe(df, required_cols=["department", "preferred_language"], allow_empty=False)

    normalize = "index" if as_percentage else None
    crosstab_df = get_department_language_crosstab(df, normalize=normalize)

    departments = list(crosstab_df.index)
    languages = list(crosstab_df.columns)

    traces: list[go.Bar] = []
    for idx, lang in enumerate(languages):
        y_vals = crosstab_df[lang].values
        color = PALETTE_CATEGORICAL[idx % len(PALETTE_CATEGORICAL)]
        hover_template = f"Dept: %{{x}}<br>Language: {lang}<br>" + (
            "Dept Share: %{y:.1f}%<extra></extra>" if as_percentage else "Count: %{y}<extra></extra>"
        )

        traces.append(
            go.Bar(
                name=str(lang),
                x=departments,
                y=y_vals,
                marker_color=color,
                hovertemplate=hover_template,
            )
        )

    fig = go.Figure(data=traces)
    y_title = "Percentage of Department (%)" if as_percentage else "Respondent Count"

    fig.update_layout(
        title="Preferred Programming Language by Academic Department",
        xaxis_title="Academic Department",
        yaxis_title=y_title,
        barmode=barmode,
        legend_title_text="Language",
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def plot_recommendation_distribution(
    df: pd.DataFrame,
    as_percentage: bool = False,
) -> go.Figure:
    """Generate an interactive bar chart of likelihood-to-recommend scores (0 to 10).

    Args:
        df: Input survey DataFrame.
        as_percentage: If True, plots percentage; else counts.

    Returns:
        go.Figure: Interactive Plotly figure.

    Raises:
        ValueError: If df is empty or 'recommendation_score' is missing.
    """
    _validate_input_dataframe(df, required_cols=["recommendation_score"], allow_empty=False)

    dist_df = get_recommendation_distribution(df)
    total_n = len(df)

    # Ensure all scores 0 through 10 are represented in sequential order
    score_map = {int(row["category"]): row for _, row in dist_df.iterrows()}
    all_scores = list(range(0, 11))

    ordered_counts: list[int] = []
    ordered_percentages: list[float] = []
    for s in all_scores:
        if s in score_map:
            ordered_counts.append(int(score_map[s]["count"]))
            ordered_percentages.append(float(score_map[s]["percentage"]))
        else:
            ordered_counts.append(0)
            ordered_percentages.append(0.0)

    y_vals = ordered_percentages if as_percentage else ordered_counts
    y_title = f"Percentage of Responses (%) [N={total_n}]" if as_percentage else "Number of Responses"

    hover_text = [
        f"Score: {s} / 10<br>Count: {cnt}<br>Share: {pct}% (N={total_n})"
        for s, cnt, pct in zip(all_scores, ordered_counts, ordered_percentages)
    ]

    fig = go.Figure(
        data=[
            go.Bar(
                x=[str(s) for s in all_scores],
                y=y_vals,
                text=[f"{val:.1f}%" if as_percentage else str(int(val)) for val in y_vals],
                textposition="auto",
                hoverinfo="text",
                hovertext=hover_text,
                marker_color="#3B82F6",
            )
        ]
    )

    fig.update_layout(
        title=f"Likelihood to Recommend Score Distribution (Total N={total_n})",
        xaxis_title="Recommendation Score (0: Not Likely to 10: Extremely Likely)",
        yaxis_title=y_title,
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def plot_department_internship_interest(
    df: pd.DataFrame,
    barmode: str = "group",
    as_percentage: bool = False,
) -> go.Figure:
    """Generate a grouped or stacked bar chart comparing internship interest across departments.

    Args:
        df: Input survey DataFrame.
        barmode: 'group' for grouped bars or 'stack' for stacked bars.
        as_percentage: If True, computes % within each department; else raw counts.

    Returns:
        go.Figure: Interactive Plotly figure.

    Raises:
        ValueError: If df is empty or required columns are missing.
    """
    _validate_input_dataframe(df, required_cols=["department", "internship_interest"], allow_empty=False)

    normalize = "index" if as_percentage else None
    crosstab_df = get_department_internship_crosstab(df, normalize=normalize)

    departments = list(crosstab_df.index)
    choices = list(crosstab_df.columns)

    # Distinct color mapping for Yes vs No
    color_map = {"Yes": "#10B981", "No": "#EF4444"}

    traces: list[go.Bar] = []
    for choice in choices:
        y_vals = crosstab_df[choice].values
        color = color_map.get(str(choice), "#6B7280")
        hover_template = f"Dept: %{{x}}<br>Interest: {choice}<br>" + (
            "Dept Share: %{y:.1f}%<extra></extra>" if as_percentage else "Count: %{y}<extra></extra>"
        )

        traces.append(
            go.Bar(
                name=str(choice),
                x=departments,
                y=y_vals,
                marker_color=color,
                hovertemplate=hover_template,
            )
        )

    fig = go.Figure(data=traces)
    y_title = "Percentage of Department (%)" if as_percentage else "Respondent Count"

    fig.update_layout(
        title="Internship Placement Interest by Academic Department",
        xaxis_title="Academic Department",
        yaxis_title=y_title,
        barmode=barmode,
        legend_title_text="Internship Interest",
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig
