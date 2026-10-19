"""Automated Insights Module for Poll Results Visualizer.

This module dynamically synthesizes key analytical takeaways, rankings,
and descriptive summaries from survey data without hard-coded numbers.

Key Design Principles:
- Dynamic computation: All metrics are derived from `src.analysis` or the supplied DataFrame.
- Deterministic tie-handling: Explicitly flags ties and lists tied categories alphabetically.
- Pure functions: Input DataFrames are never mutated in place.
- Structured output: Each insight returns a standardized dictionary separating numeric
  evidence from presentation text, facilitating seamless Streamlit dashboard integration.
- Strictly descriptive: Labels findings as synthetic sample observations; does not assert
  causality or extrapolate statistical significance to real populations.
"""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd

from src.analysis import (
    _validate_input_dataframe,
    get_categorical_frequency,
    get_department_internship_crosstab,
    get_internship_interest_summary,
    get_learning_method_distribution,
    get_missing_value_summary,
    get_numeric_summary,
    get_recommendation_distribution,
    get_satisfaction_distribution,
)


def get_top_language_insight(df: pd.DataFrame) -> dict[str, Any]:
    """Identify the most preferred programming language(s) in the survey cohort.

    Args:
        df: Input survey DataFrame.

    Returns:
        dict with keys: 'id', 'title', 'metric_value', 'percentage', 'denominator',
                        'is_tie', 'details', 'summary_text'.

    Raises:
        ValueError: If df is empty or 'preferred_language' is missing.
    """
    _validate_input_dataframe(df, required_cols=["preferred_language"], allow_empty=False)

    freq_df = get_categorical_frequency(df, "preferred_language")
    total_n = len(df)

    max_count = int(freq_df["count"].max())
    top_rows = freq_df[freq_df["count"] == max_count].sort_values("category")

    top_languages = top_rows["category"].tolist()
    is_tie = len(top_languages) > 1
    top_pct = float(top_rows["percentage"].iloc[0])

    if is_tie:
        metric_str = ", ".join(top_languages)
        summary = (
            f"Tied for most preferred language: {metric_str} with {max_count} responses each "
            f"({top_pct:.1f}% of N={total_n})."
        )
    else:
        metric_str = top_languages[0]
        summary = (
            f"Most preferred programming language is {metric_str} with {max_count} responses "
            f"({top_pct:.1f}% of N={total_n})."
        )

    return {
        "id": "top_language",
        "title": "Most Preferred Programming Language",
        "metric_value": metric_str,
        "percentage": top_pct,
        "denominator": total_n,
        "is_tie": is_tie,
        "details": dict(zip(freq_df["category"], freq_df["count"].astype(int))),
        "summary_text": summary,
    }


def get_top_learning_method_insight(df: pd.DataFrame) -> dict[str, Any]:
    """Identify the most preferred learning method(s).

    Args:
        df: Input survey DataFrame.

    Returns:
        dict containing structured insight metadata and summary narrative.

    Raises:
        ValueError: If df is empty or 'preferred_learning_method' is missing.
    """
    _validate_input_dataframe(df, required_cols=["preferred_learning_method"], allow_empty=False)

    freq_df = get_learning_method_distribution(df)
    total_n = len(df)

    max_count = int(freq_df["count"].max())
    top_rows = freq_df[freq_df["count"] == max_count].sort_values("category")

    top_methods = top_rows["category"].tolist()
    is_tie = len(top_methods) > 1
    top_pct = float(top_rows["percentage"].iloc[0])

    if is_tie:
        metric_str = ", ".join(top_methods)
        summary = (
            f"Tied for most preferred learning method: {metric_str} with {max_count} responses each "
            f"({top_pct:.1f}% of N={total_n})."
        )
    else:
        metric_str = top_methods[0]
        summary = (
            f"Most preferred learning method is {metric_str} with {max_count} responses "
            f"({top_pct:.1f}% of N={total_n})."
        )

    return {
        "id": "top_learning_method",
        "title": "Most Preferred Learning Method",
        "metric_value": metric_str,
        "percentage": top_pct,
        "denominator": total_n,
        "is_tie": is_tie,
        "details": dict(zip(freq_df["category"], freq_df["count"].astype(int))),
        "summary_text": summary,
    }


def get_satisfaction_insight(df: pd.DataFrame) -> dict[str, Any]:
    """Analyze training satisfaction ratings, computing mean and favorable proportions.

    Favorable satisfaction is defined as ratings 4 or 5 out of 5.

    Args:
        df: Input survey DataFrame.

    Returns:
        dict containing mean rating, favorable percentage, and summary text.

    Raises:
        ValueError: If df is empty or 'training_satisfaction' is missing.
    """
    _validate_input_dataframe(df, required_cols=["training_satisfaction"], allow_empty=False)

    total_n = len(df)
    stats_df = get_numeric_summary(df, columns=["training_satisfaction"])
    mean_sat = float(stats_df["mean"].iloc[0])
    median_sat = float(stats_df["median"].iloc[0])

    dist_df = get_satisfaction_distribution(df)
    favorable_rows = dist_df[dist_df["category"].astype(int).isin([4, 5])]
    favorable_count = int(favorable_rows["count"].sum())
    favorable_pct = round((favorable_count / total_n) * 100.0, 2)

    summary = (
        f"Average training satisfaction is {mean_sat:.2f} / 5.0 (median: {median_sat:.1f}), "
        f"with {favorable_pct:.1f}% of respondents rating satisfaction at 4 or 5 (N={total_n})."
    )

    return {
        "id": "training_satisfaction",
        "title": "Training Satisfaction Overview",
        "metric_value": mean_sat,
        "percentage": favorable_pct,
        "denominator": total_n,
        "is_tie": False,
        "details": {
            "mean": mean_sat,
            "median": median_sat,
            "favorable_count": favorable_count,
            "favorable_percentage": favorable_pct,
            "distribution": dict(zip(dist_df["category"], dist_df["count"].astype(int))),
        },
        "summary_text": summary,
    }


def get_top_internship_department_insight(df: pd.DataFrame) -> dict[str, Any]:
    """Identify which department exhibits the highest percentage of internship interest.

    Args:
        df: Input survey DataFrame.

    Returns:
        dict containing the leading department name, percentage, and cross-tab details.

    Raises:
        ValueError: If df is empty or required columns are missing.
    """
    _validate_input_dataframe(df, required_cols=["department", "internship_interest"], allow_empty=False)

    pct_crosstab = get_department_internship_crosstab(df, normalize="index")
    raw_crosstab = get_department_internship_crosstab(df, normalize=None)

    if "Yes" not in pct_crosstab.columns:
        return {
            "id": "top_internship_department",
            "title": "Top Internship Interest by Department",
            "metric_value": "None",
            "percentage": 0.0,
            "denominator": len(df),
            "is_tie": False,
            "details": {},
            "summary_text": "No respondents indicated interest in internships ('Yes').",
        }

    yes_pcts = pct_crosstab["Yes"]
    max_pct = float(yes_pcts.max())
    top_depts = yes_pcts[yes_pcts == max_pct].index.sort_values().tolist()
    is_tie = len(top_depts) > 1

    if is_tie:
        dept_str = ", ".join(top_depts)
        summary = (
            f"Tied for highest internship placement interest: {dept_str} "
            f"with {max_pct:.1f}% of cohort respondents indicating interest."
        )
    else:
        dept_str = top_depts[0]
        yes_count = int(raw_crosstab.loc[dept_str, "Yes"])
        dept_total = int(raw_crosstab.loc[dept_str].sum())
        summary = (
            f"Highest internship placement interest is in {dept_str} at {max_pct:.1f}% "
            f"({yes_count} of {dept_total} cohort respondents)."
        )

    return {
        "id": "top_internship_department",
        "title": "Top Internship Interest by Department",
        "metric_value": dept_str,
        "percentage": max_pct,
        "denominator": len(df),
        "is_tie": is_tie,
        "details": {dept: float(pct) for dept, pct in yes_pcts.items()},
        "summary_text": summary,
    }


def get_overall_internship_insight(df: pd.DataFrame) -> dict[str, Any]:
    """Calculate overall internship interest percentage across all survey respondents.

    Args:
        df: Input survey DataFrame.

    Returns:
        dict containing overall 'Yes' percentage, count, and summary.

    Raises:
        ValueError: If df is empty or 'internship_interest' is missing.
    """
    _validate_input_dataframe(df, required_cols=["internship_interest"], allow_empty=False)

    summary_df = get_internship_interest_summary(df)
    total_n = len(df)

    yes_row = summary_df[summary_df["category"] == "Yes"]
    yes_count = int(yes_row["count"].iloc[0]) if not yes_row.empty else 0
    yes_pct = float(yes_row["percentage"].iloc[0]) if not yes_row.empty else 0.0

    summary = (
        f"Overall internship placement interest is {yes_pct:.1f}%, representing "
        f"{yes_count} out of {total_n} respondents indicating 'Yes'."
    )

    return {
        "id": "overall_internship",
        "title": "Overall Internship Placement Interest",
        "metric_value": yes_pct,
        "percentage": yes_pct,
        "denominator": total_n,
        "is_tie": False,
        "details": {
            "yes_count": yes_count,
            "no_count": total_n - yes_count,
            "yes_percentage": yes_pct,
            "no_percentage": round(100.0 - yes_pct, 2),
        },
        "summary_text": summary,
    }


def get_recommendation_score_insight(df: pd.DataFrame) -> dict[str, Any]:
    """Compute average likelihood to recommend rating and promoter percentage (scores 9-10).

    Args:
        df: Input survey DataFrame.

    Returns:
        dict containing average recommendation score and promoter proportion.

    Raises:
        ValueError: If df is empty or 'recommendation_score' is missing.
    """
    _validate_input_dataframe(df, required_cols=["recommendation_score"], allow_empty=False)

    total_n = len(df)
    stats_df = get_numeric_summary(df, columns=["recommendation_score"])
    mean_rec = float(stats_df["mean"].iloc[0])
    median_rec = float(stats_df["median"].iloc[0])

    dist_df = get_recommendation_distribution(df)
    promoters_df = dist_df[dist_df["category"].astype(int).isin([9, 10])]
    promoter_count = int(promoters_df["count"].sum())
    promoter_pct = round((promoter_count / total_n) * 100.0, 2)

    summary = (
        f"Average recommendation score is {mean_rec:.2f} / 10.0 (median: {median_rec:.1f}), "
        f"with {promoter_pct:.1f}% of respondents rating 9 or 10 (N={total_n})."
    )

    return {
        "id": "recommendation_score",
        "title": "Likelihood to Recommend Score",
        "metric_value": mean_rec,
        "percentage": promoter_pct,
        "denominator": total_n,
        "is_tie": False,
        "details": {
            "mean": mean_rec,
            "median": median_rec,
            "promoter_count": promoter_count,
            "promoter_percentage": promoter_pct,
        },
        "summary_text": summary,
    }


def get_missing_comments_insight(df: pd.DataFrame) -> dict[str, Any]:
    """Audit optional survey feedback completeness in the comments column.

    Args:
        df: Input survey DataFrame.

    Returns:
        dict containing missing comments count and percentage.

    Raises:
        ValueError: If df is empty or 'comments' is missing.
    """
    _validate_input_dataframe(df, required_cols=["comments"], allow_empty=False)

    total_n = len(df)
    missing_df = get_missing_value_summary(df)
    comm_row = missing_df[missing_df["column"] == "comments"].iloc[0]

    missing_cnt = int(comm_row["missing_count"])
    missing_pct = float(comm_row["missing_percentage"])
    provided_cnt = total_n - missing_cnt

    summary = (
        f"{provided_cnt} of {total_n} respondents ({100.0 - missing_pct:.1f}%) provided optional "
        f"written feedback, while {missing_cnt} ({missing_pct:.1f}%) left the comments field blank."
    )

    return {
        "id": "missing_comments",
        "title": "Optional Qualitative Feedback Rate",
        "metric_value": missing_cnt,
        "percentage": missing_pct,
        "denominator": total_n,
        "is_tie": False,
        "details": {
            "missing_count": missing_cnt,
            "missing_percentage": missing_pct,
            "provided_count": provided_cnt,
            "provided_percentage": round(100.0 - missing_pct, 2),
        },
        "summary_text": summary,
    }


def generate_all_insights(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Synthesize all 7 primary survey takeaways into a structured list of insight records.

    This master generator provides a unified data structure ready for rendering
    in reports or Streamlit card components.

    Args:
        df: Validated survey DataFrame.

    Returns:
        list of 7 insight dictionaries.

    Raises:
        ValueError: If df is empty or any required columns are missing.
    """
    return [
        get_top_language_insight(df),
        get_top_learning_method_insight(df),
        get_satisfaction_insight(df),
        get_top_internship_department_insight(df),
        get_overall_internship_insight(df),
        get_recommendation_score_insight(df),
        get_missing_comments_insight(df),
    ]
