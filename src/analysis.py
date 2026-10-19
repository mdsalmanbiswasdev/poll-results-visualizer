"""Statistical Analysis Module for Poll Results Visualizer.

This module provides dynamic, reusable functions for computing descriptive statistics,
frequency distributions, and demographic cross-tabulations on survey data.

Important Guidelines:
- All calculations are computed dynamically from the supplied DataFrame (no hard-coded values).
- Input DataFrames are treated as immutable and never mutated in place.
- All distributions and cross-tabulations explicitly define percentage denominators
  and guard against division-by-zero.
- Functions are purely descriptive; no causal assertions, machine learning,
  or extrapolations beyond the synthetic sample are performed.
"""

from __future__ import annotations

from typing import Any, Optional

import numpy as np
import pandas as pd

from src.data_loader import REQUIRED_COLUMNS

# Canonical numeric and categorical columns
NUMERIC_SURVEY_COLUMNS: list[str] = [
    "study_year",
    "training_satisfaction",
    "recommendation_score",
]

CATEGORICAL_SURVEY_COLUMNS: list[str] = [
    "department",
    "preferred_language",
    "preferred_learning_method",
    "internship_interest",
]


def _validate_input_dataframe(
    df: pd.DataFrame,
    required_cols: Optional[list[str]] = None,
    allow_empty: bool = False,
) -> None:
    """Validate DataFrame instance, non-emptiness, and presence of required columns."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, received {type(df).__name__}")

    if not allow_empty and df.empty:
        raise ValueError("Cannot perform statistical analysis on an empty DataFrame.")

    if required_cols is not None:
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"DataFrame is missing required analysis columns: {missing}")


def get_dataset_overview(df: pd.DataFrame) -> dict[str, Any]:
    """Return high-level structural dimensions and data types of the dataset.

    Args:
        df: Input pandas DataFrame.

    Returns:
        dict containing 'row_count', 'column_count', 'columns', and 'dtypes'.

    Raises:
        TypeError: If df is not a DataFrame.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, received {type(df).__name__}")

    return {
        "row_count": int(df.shape[0]),
        "column_count": int(df.shape[1]),
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }


def get_missing_value_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate missing value counts and percentages for each column.

    Percentage denominator is strictly defined as the total number of rows.
    If the DataFrame has 0 rows, percentage is set to 0.0.

    Args:
        df: Input pandas DataFrame.

    Returns:
        pd.DataFrame with columns: ['column', 'missing_count', 'missing_percentage'].
    """
    _validate_input_dataframe(df, allow_empty=True)

    total_rows = len(df)
    missing_counts = df.isnull().sum()

    if total_rows > 0:
        missing_percentages = (missing_counts / total_rows * 100.0).round(2)
    else:
        missing_percentages = pd.Series(0.0, index=df.columns)

    summary_df = pd.DataFrame(
        {
            "column": df.columns,
            "missing_count": missing_counts.values.astype(int),
            "missing_percentage": missing_percentages.values.astype(float),
        }
    )
    return summary_df.reset_index(drop=True)


def get_numeric_summary(
    df: pd.DataFrame,
    columns: Optional[list[str]] = None,
) -> pd.DataFrame:
    """Compute descriptive statistics for specified numeric columns.

    Calculates count, mean, std, median, min, max, and IQR (Interquartile Range).

    Args:
        df: Input pandas DataFrame.
        columns: List of numeric column names. Defaults to
                 ['study_year', 'training_satisfaction', 'recommendation_score'].

    Returns:
        pd.DataFrame indexed by column name with computed statistical metrics.

    Raises:
        ValueError: If df is empty or columns are missing.
    """
    target_columns = columns if columns is not None else NUMERIC_SURVEY_COLUMNS
    _validate_input_dataframe(df, required_cols=target_columns, allow_empty=False)

    summary_rows: list[dict[str, Any]] = []

    for col in target_columns:
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if series.empty:
            summary_rows.append(
                {
                    "column": col,
                    "count": 0,
                    "mean": np.nan,
                    "std": np.nan,
                    "median": np.nan,
                    "min": np.nan,
                    "max": np.nan,
                    "iqr": np.nan,
                }
            )
            continue

        q25 = float(series.quantile(0.25))
        q75 = float(series.quantile(0.75))
        iqr = round(q75 - q25, 2)

        summary_rows.append(
            {
                "column": col,
                "count": int(series.count()),
                "mean": round(float(series.mean()), 2),
                "std": round(float(series.std()), 2) if len(series) > 1 else 0.0,
                "median": round(float(series.median()), 2),
                "min": round(float(series.min()), 2),
                "max": round(float(series.max()), 2),
                "iqr": iqr,
            }
        )

    return pd.DataFrame(summary_rows).reset_index(drop=True)


def get_categorical_frequency(
    df: pd.DataFrame,
    column: str,
    dropna: bool = True,
) -> pd.DataFrame:
    """Compute frequency counts and percentages for a single categorical column.

    Denominator is the total number of considered responses (excluding NaN if dropna=True).

    Args:
        df: Input pandas DataFrame.
        column: Categorical column name to aggregate.
        dropna: Whether to exclude missing values from the denominator.

    Returns:
        pd.DataFrame with columns ['category', 'count', 'percentage'], sorted by count descending.

    Raises:
        ValueError: If df is empty or column is not in df.
    """
    _validate_input_dataframe(df, required_cols=[column], allow_empty=False)

    series = df[column]
    if dropna:
        series = series.dropna()

    total_valid = len(series)
    if total_valid == 0:
        return pd.DataFrame(columns=["category", "count", "percentage"])

    counts = series.value_counts(dropna=dropna)
    percentages = ((counts / total_valid) * 100.0).round(2)

    freq_df = pd.DataFrame(
        {
            "category": counts.index.astype(str),
            "count": counts.values.astype(int),
            "percentage": percentages.values.astype(float),
        }
    )
    return freq_df.reset_index(drop=True)


def get_cross_tabulation(
    df: pd.DataFrame,
    row_col: str,
    col_col: str,
    normalize: Optional[str] = None,
) -> pd.DataFrame:
    """Compute a contingency table / cross-tabulation across two categorical variables.

    Args:
        df: Input pandas DataFrame.
        row_col: Column name for rows.
        col_col: Column name for columns.
        normalize: 'index' (row percentages), 'columns' (column percentages),
                   'all' (total percentage), or None (raw integer counts).

    Returns:
        pd.DataFrame representing the cross-tabulation matrix.

    Raises:
        ValueError: If df is empty or specified columns are missing.
    """
    _validate_input_dataframe(df, required_cols=[row_col, col_col], allow_empty=False)

    if normalize is not None:
        ct = pd.crosstab(
            df[row_col],
            df[col_col],
            normalize=normalize,
        )
        ct = (ct * 100.0).round(2)
    else:
        ct = pd.crosstab(
            df[row_col],
            df[col_col],
        )

    return ct


# Convenience domain analysis functions


def get_department_language_crosstab(
    df: pd.DataFrame,
    normalize: Optional[str] = None,
) -> pd.DataFrame:
    """Generate department versus preferred programming language cross-tabulation."""
    return get_cross_tabulation(df, "department", "preferred_language", normalize=normalize)


def get_department_internship_crosstab(
    df: pd.DataFrame,
    normalize: Optional[str] = None,
) -> pd.DataFrame:
    """Generate department versus internship interest cross-tabulation."""
    return get_cross_tabulation(df, "department", "internship_interest", normalize=normalize)


def get_satisfaction_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Generate frequency and percentage distribution for training_satisfaction."""
    return get_categorical_frequency(df, "training_satisfaction")


def get_learning_method_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Generate frequency and percentage distribution for preferred_learning_method."""
    return get_categorical_frequency(df, "preferred_learning_method")


def get_recommendation_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Generate frequency and percentage distribution for recommendation_score."""
    return get_categorical_frequency(df, "recommendation_score")


def get_internship_interest_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generate frequency and percentage distribution for internship_interest."""
    return get_categorical_frequency(df, "internship_interest")
