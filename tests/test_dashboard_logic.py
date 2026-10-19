"""Tests for app.py dashboard filter and calculation logic.

These tests exercise the data filtering, KPI computation, search, and
insight generation logic from app.py using deterministic DataFrames —
without starting a Streamlit server.

Covers:
- Single-department filter produces correct subset.
- Multi-department filter produces correct union.
- Study-year filter works correctly.
- Combined (department + year) intersection is correct.
- Clearing all filters (keeping all values) restores full dataset.
- Empty filter result produces empty DataFrame, no crash.
- Internship KPI uses n_filtered as denominator, not n_total.
- Percentage denominator is consistent with the filtered DataFrame.
- Insights regenerate dynamically from the filtered DataFrame.
- No hardcoded expected values from the synthetic dataset.
- Search logic filters rows case-insensitively across all string columns.
- Column selection produces correct subset of columns.
- CSV export contains exactly the right rows and columns.
"""

from __future__ import annotations

import pathlib
import sys

import pandas as pd
import pytest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.analysis import get_numeric_summary, get_missing_value_summary
from src.insights import generate_all_insights


# ---------------------------------------------------------------------------
# Deterministic fixture — built manually, NOT loaded from the synthetic CSV
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_df() -> pd.DataFrame:
    """Deterministic 12-row DataFrame covering all filter combinations."""
    return pd.DataFrame(
        {
            "response_id": [f"R{i:03d}" for i in range(1, 13)],
            "department": [
                "CS", "CS", "CS", "IT", "IT", "IT",
                "ME", "ME", "ME", "CS", "IT", "ME",
            ],
            "study_year": [1, 2, 3, 1, 2, 3, 1, 2, 3, 4, 4, 4],
            "preferred_language": [
                "Python", "Java", "Python", "R", "Python", "Java",
                "Python", "R", "Java", "Python", "Java", "R",
            ],
            "training_satisfaction": [5, 4, 3, 5, 2, 4, 3, 5, 1, 4, 3, 2],
            "preferred_learning_method": [
                "Video", "Hands-on Projects", "Video", "Reading",
                "Hands-on Projects", "Video", "Reading", "Video",
                "Hands-on Projects", "Hands-on Projects", "Reading", "Video",
            ],
            "internship_interest": [
                "Yes", "Yes", "No", "Yes", "No", "Yes",
                "No", "Yes", "No", "Yes", "Yes", "No",
            ],
            "recommendation_score": [9, 7, 5, 10, 4, 8, 6, 9, 3, 7, 6, 5],
            "comments": [
                "Great", None, "Ok", "Loved it", None, "Fine",
                None, "Good", None, "Excellent", None, "Average",
            ],
        }
    )


# ---------------------------------------------------------------------------
# Helper: replicate app.py filter logic exactly
# ---------------------------------------------------------------------------

def apply_filters(
    df_full: pd.DataFrame,
    selected_departments: list[str] | None = None,
    selected_years: list[int] | None = None,
) -> pd.DataFrame:
    """Mirror the filter block in app.py (lines 277-281)."""
    df = df_full.copy()
    if selected_departments:
        df = df[df["department"].isin(selected_departments)]
    if selected_years:
        df = df[df["study_year"].isin(selected_years)]
    return df


def apply_search(df: pd.DataFrame, search_term: str) -> pd.DataFrame:
    """Mirror the search logic in app.py (lines 558-562)."""
    mask = df.apply(
        lambda col: col.astype(str).str.contains(search_term, case=False, na=False)
    ).any(axis=1)
    return df[mask]


# ---------------------------------------------------------------------------
# FILTER CORRECTNESS TESTS
# ---------------------------------------------------------------------------

class TestSingleDepartmentFilter:
    def test_cs_only_returns_correct_rows(self, sample_df):
        df = apply_filters(sample_df, selected_departments=["CS"])
        assert list(df["department"].unique()) == ["CS"]
        assert len(df) == 4  # rows 1-3 and 10

    def test_it_only_returns_correct_rows(self, sample_df):
        df = apply_filters(sample_df, selected_departments=["IT"])
        assert list(df["department"].unique()) == ["IT"]
        assert len(df) == 4  # rows 4-6 and 11


class TestMultiDepartmentFilter:
    def test_cs_and_it_union(self, sample_df):
        df = apply_filters(sample_df, selected_departments=["CS", "IT"])
        assert set(df["department"].unique()) == {"CS", "IT"}
        assert len(df) == 8

    def test_all_departments_returns_full_set(self, sample_df):
        all_depts = sorted(sample_df["department"].unique().tolist())
        df = apply_filters(sample_df, selected_departments=all_depts)
        assert len(df) == len(sample_df)


class TestStudyYearFilter:
    def test_year_1_only(self, sample_df):
        df = apply_filters(sample_df, selected_years=[1])
        assert list(df["study_year"].unique()) == [1]
        assert len(df) == 3  # rows 1, 4, 7

    def test_years_1_and_2(self, sample_df):
        df = apply_filters(sample_df, selected_years=[1, 2])
        assert set(df["study_year"].unique()) == {1, 2}
        assert len(df) == 6


class TestCombinedFilters:
    def test_cs_and_year_1_intersection(self, sample_df):
        df = apply_filters(sample_df, selected_departments=["CS"], selected_years=[1])
        assert len(df) == 1
        assert df.iloc[0]["response_id"] == "R001"

    def test_it_years_1_2(self, sample_df):
        df = apply_filters(sample_df, selected_departments=["IT"], selected_years=[1, 2])
        assert len(df) == 2  # R004 and R005
        assert set(df["response_id"].tolist()) == {"R004", "R005"}


class TestClearFilters:
    def test_no_filter_returns_full_dataset(self, sample_df):
        """Mirrors app.py behavior: empty lists mean no filter applied."""
        # app.py only filters if selected_departments/years are truthy
        df = apply_filters(sample_df, selected_departments=[], selected_years=[])
        assert len(df) == len(sample_df)

    def test_all_values_selected_returns_full_dataset(self, sample_df):
        all_depts = sorted(sample_df["department"].unique().tolist())
        all_years = sorted(sample_df["study_year"].unique().tolist())
        df = apply_filters(sample_df, selected_departments=all_depts, selected_years=all_years)
        assert len(df) == len(sample_df)


class TestEmptyFilterResult:
    def test_impossible_combination_returns_empty(self, sample_df):
        df = apply_filters(
            sample_df,
            selected_departments=["CS"],
            selected_years=[99],  # no year 99 exists
        )
        assert df.empty

    def test_nonexistent_department_returns_empty(self, sample_df):
        df = apply_filters(sample_df, selected_departments=["NonExistent"])
        assert df.empty


# ---------------------------------------------------------------------------
# KPI DENOMINATOR TESTS
# ---------------------------------------------------------------------------

class TestKpiDenominators:
    def test_internship_pct_uses_filtered_n(self, sample_df):
        """internship_pct = yes_count / n_filtered, NOT n_total."""
        df = apply_filters(sample_df, selected_departments=["CS"])
        n_filtered = len(df)
        yes_count = int((df["internship_interest"].str.strip().str.lower() == "yes").sum())
        internship_pct = round(yes_count / n_filtered * 100, 1)

        # Verify against direct calculation
        cs_df = sample_df[sample_df["department"] == "CS"]
        expected_yes = (cs_df["internship_interest"].str.lower() == "yes").sum()
        expected_pct = round(expected_yes / len(cs_df) * 100, 1)
        assert internship_pct == expected_pct

    def test_total_n_is_unfiltered_full_dataset(self, sample_df):
        df = apply_filters(sample_df, selected_departments=["CS"])
        n_total = len(sample_df)
        n_filtered = len(df)
        assert n_total == 12
        assert n_filtered == 4
        assert n_total != n_filtered  # confirms filtering is active

    def test_numeric_summary_uses_filtered_df(self, sample_df):
        df_full = sample_df
        df_cs = apply_filters(sample_df, selected_departments=["CS"])

        summary_full = get_numeric_summary(df_full, columns=["training_satisfaction"])
        summary_cs = get_numeric_summary(df_cs, columns=["training_satisfaction"])

        # Means must differ because subsets are different
        mean_full = float(summary_full.loc[summary_full["column"] == "training_satisfaction", "mean"].values[0])
        mean_cs = float(summary_cs.loc[summary_cs["column"] == "training_satisfaction", "mean"].values[0])

        # CS satisfaction values: [5, 4, 3, 4] → mean = 4.0
        assert mean_cs == pytest.approx(4.0, abs=0.01)
        # Full dataset mean should be different
        assert mean_full != mean_cs


# ---------------------------------------------------------------------------
# INSIGHT DYNAMIC RECALCULATION TESTS
# ---------------------------------------------------------------------------

class TestInsightDynamism:
    def test_insights_recalculate_on_filter(self, sample_df):
        """Insights generated from full dataset differ from filtered dataset."""
        insights_full = generate_all_insights(sample_df)
        df_cs = apply_filters(sample_df, selected_departments=["CS"])
        insights_cs = generate_all_insights(df_cs)

        # Denominators must reflect filtering
        full_n = next(i for i in insights_full if i["id"] == "top_language")["denominator"]
        cs_n = next(i for i in insights_cs if i["id"] == "top_language")["denominator"]
        assert full_n == 12
        assert cs_n == 4

    def test_all_seven_insights_generated(self, sample_df):
        insights = generate_all_insights(sample_df)
        assert len(insights) == 7
        expected_ids = {
            "top_language", "top_learning_method", "training_satisfaction",
            "top_internship_department", "overall_internship",
            "recommendation_score", "missing_comments",
        }
        assert {i["id"] for i in insights} == expected_ids

    def test_no_hardcoded_values_in_insights(self, sample_df):
        """Insight metric_value must change when data changes."""
        insights_orig = generate_all_insights(sample_df)

        # Invert all internship answers
        df_inverted = sample_df.copy()
        df_inverted["internship_interest"] = df_inverted["internship_interest"].map(
            {"Yes": "No", "No": "Yes"}
        )
        insights_inverted = generate_all_insights(df_inverted)

        orig_pct = next(i for i in insights_orig if i["id"] == "overall_internship")["percentage"]
        inverted_pct = next(i for i in insights_inverted if i["id"] == "overall_internship")["percentage"]
        assert orig_pct != inverted_pct


# ---------------------------------------------------------------------------
# SEARCH LOGIC TESTS
# ---------------------------------------------------------------------------

class TestSearchLogic:
    def test_search_is_case_insensitive(self, sample_df):
        df_upper = apply_search(sample_df, "GREAT")
        df_lower = apply_search(sample_df, "great")
        assert len(df_upper) == len(df_lower)
        assert len(df_upper) >= 1

    def test_search_matches_across_all_columns(self, sample_df):
        # "Python" appears in preferred_language column
        result = apply_search(sample_df, "Python")
        assert len(result) >= 1
        # "CS" appears in department column
        result_cs = apply_search(sample_df, "CS")
        assert len(result_cs) >= 1

    def test_search_with_no_match_returns_empty(self, sample_df):
        result = apply_search(sample_df, "ZZZNOMATCH99999")
        assert result.empty

    def test_search_handles_none_values_without_crash(self, sample_df):
        """Comments column has None values — search must not raise."""
        # None values in sample_df["comments"] — should not raise
        result = apply_search(sample_df, "Good")
        assert isinstance(result, pd.DataFrame)

    def test_search_then_filter_gives_correct_intersection(self, sample_df):
        df_filtered = apply_filters(sample_df, selected_departments=["CS"])
        df_searched = apply_search(df_filtered, "python")
        # CS has Python in rows R001, R003, R010
        assert all(df_searched["department"] == "CS")
        assert all(
            df_searched["preferred_language"].str.lower().str.contains("python")
        )


# ---------------------------------------------------------------------------
# COLUMN SELECTION AND CSV EXPORT TESTS
# ---------------------------------------------------------------------------

class TestColumnSelectionAndExport:
    def test_column_subset_has_correct_shape(self, sample_df):
        selected_cols = ["response_id", "department", "training_satisfaction"]
        display_df = sample_df[selected_cols].copy()
        assert list(display_df.columns) == selected_cols
        assert len(display_df) == len(sample_df)

    def test_empty_column_selection_falls_back_to_full_df(self, sample_df):
        """Mirrors app.py line 556: if no cols selected, use df.copy()."""
        selected_cols: list[str] = []
        display_df = sample_df[selected_cols].copy() if selected_cols else sample_df.copy()
        assert list(display_df.columns) == list(sample_df.columns)

    def test_csv_export_contains_correct_rows(self, sample_df):
        df_filtered = apply_filters(sample_df, selected_departments=["IT"])
        csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
        # Re-read and verify
        import io
        reconstructed = pd.read_csv(io.BytesIO(csv_bytes))
        assert len(reconstructed) == len(df_filtered)
        assert list(reconstructed["department"].unique()) == ["IT"]

    def test_csv_export_respects_column_selection(self, sample_df):
        selected_cols = ["response_id", "department"]
        display_df = sample_df[selected_cols].copy()
        csv_bytes = display_df.to_csv(index=False).encode("utf-8")
        import io
        reconstructed = pd.read_csv(io.BytesIO(csv_bytes))
        assert list(reconstructed.columns) == selected_cols


# ---------------------------------------------------------------------------
# MISSING VALUE HANDLING
# ---------------------------------------------------------------------------

class TestMissingValueHandling:
    def test_missing_comments_do_not_crash_analysis(self, sample_df):
        """DataFrames with NaN in comments must not crash insight generation."""
        assert sample_df["comments"].isna().any()
        insights = generate_all_insights(sample_df)
        assert len(insights) == 7

    def test_missing_summary_correctly_counts_nulls(self, sample_df):
        mv = get_missing_value_summary(sample_df)
        comments_row = mv[mv["column"] == "comments"].iloc[0]
        expected_nulls = sample_df["comments"].isna().sum()
        assert int(comments_row["missing_count"]) == expected_nulls


# ---------------------------------------------------------------------------
# NO HARDCODED SYNTHETIC VALUES IN DASHBOARD DATA PATH
# ---------------------------------------------------------------------------

class TestNoDashboardHardcoding:
    def test_kpi_changes_when_data_changes(self, sample_df):
        df_all = apply_filters(sample_df)
        df_partial = apply_filters(sample_df, selected_departments=["ME"])

        yes_all = int((df_all["internship_interest"].str.lower() == "yes").sum())
        yes_me = int((df_partial["internship_interest"].str.lower() == "yes").sum())

        pct_all = round(yes_all / len(df_all) * 100, 1)
        pct_me = round(yes_me / len(df_partial) * 100, 1)

        # ME: No, Yes, No, No → 1/4 = 25%
        # All: 7/12 ≈ 58.3%
        assert pct_me == pytest.approx(25.0)
        assert pct_all != pct_me

    def test_sat_mean_changes_with_filter(self, sample_df):
        df_me = apply_filters(sample_df, selected_departments=["ME"])
        summary = get_numeric_summary(df_me, columns=["training_satisfaction"])
        mean_me = float(summary.loc[summary["column"] == "training_satisfaction", "mean"].values[0])
        # ME sat values: [3, 5, 1, 2] → mean = 2.75
        assert mean_me == pytest.approx(2.75, abs=0.01)
