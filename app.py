"""Streamlit Interactive Dashboard — Poll Results Visualizer.

Entry point: run with
    streamlit run app.py

Architecture:
- Loads and caches the cleaned survey dataset via src.data_loader + src.data_cleaning.
- Applies optional sidebar filters (department, study year) that cascade to all sections.
- Renders four tabbed sections: Overview, Visualizations, Insights, and Raw Data.
- All computations delegate to src.analysis, src.visualizations, and src.insights.
- No data is hard-coded; every metric recalculates whenever the DataFrame changes.
"""

from __future__ import annotations

import pathlib
import sys

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Path setup — allow running from the project root without installing the package
# ---------------------------------------------------------------------------
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.analysis import (
    get_dataset_overview,
    get_missing_value_summary,
    get_numeric_summary,
    get_categorical_frequency,
    get_department_language_crosstab,
    get_department_internship_crosstab,
    NUMERIC_SURVEY_COLUMNS,
    CATEGORICAL_SURVEY_COLUMNS,
)
from src.data_cleaning import clean_poll_data
from src.data_loader import load_poll_data
from src.insights import generate_all_insights
from src.visualizations import (
    plot_department_internship_interest,
    plot_department_language_comparison,
    plot_language_distribution,
    plot_learning_method_distribution,
    plot_recommendation_distribution,
    plot_satisfaction_distribution,
)

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Poll Results Visualizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — dark glassmorphism theme
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* ── Base & background ── */
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #0f172a 100%);
        color: #e2e8f0;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.85);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
        backdrop-filter: blur(12px);
    }
    [data-testid="stSidebar"] .css-1d391kg { padding-top: 1rem; }

    /* ── Main header ── */
    .hero-banner {
        background: linear-gradient(135deg, rgba(99,102,241,0.25) 0%, rgba(16,185,129,0.15) 100%);
        border: 1px solid rgba(99,102,241,0.35);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(8px);
        text-align: center;
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #818cf8, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 0.4rem;
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 1.05rem;
        margin: 0;
    }

    /* ── Metric cards ── */
    .metric-card {
        background: rgba(30, 41, 59, 0.75);
        border: 1px solid rgba(99,102,241,0.25);
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        backdrop-filter: blur(6px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(99,102,241,0.55);
    }
    .metric-label {
        font-size: 0.78rem;
        font-weight: 600;
        color: #94a3b8;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #e2e8f0;
        line-height: 1.1;
    }
    .metric-delta {
        font-size: 0.82rem;
        color: #34d399;
        margin-top: 0.25rem;
    }

    /* ── Insight cards ── */
    .insight-card {
        background: rgba(30, 41, 59, 0.7);
        border-left: 4px solid #6366f1;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.9rem;
        backdrop-filter: blur(6px);
    }
    .insight-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #818cf8;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.3rem;
    }
    .insight-metric {
        font-size: 1.55rem;
        font-weight: 800;
        color: #f1f5f9;
    }
    .insight-text {
        font-size: 0.88rem;
        color: #94a3b8;
        margin-top: 0.35rem;
        line-height: 1.55;
    }

    /* ── Section headers ── */
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #e2e8f0;
        border-bottom: 2px solid rgba(99,102,241,0.4);
        padding-bottom: 0.4rem;
        margin-bottom: 1rem;
    }

    /* ── Filter badge ── */
    .filter-badge {
        background: rgba(99,102,241,0.2);
        border: 1px solid rgba(99,102,241,0.4);
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.8rem;
        color: #818cf8;
        display: inline-block;
        margin: 0 0.25rem 0.4rem;
    }

    hr { border-color: rgba(99,102,241,0.2); }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Data loading — cached so filters don't reload from disk on every interaction
# ---------------------------------------------------------------------------

RAW_PATH = PROJECT_ROOT / "data" / "raw" / "sample_poll_data.csv"
CLEAN_PATH = PROJECT_ROOT / "data" / "processed" / "clean_poll_data.csv"


@st.cache_data(show_spinner="Loading and cleaning survey data…")
def load_data() -> pd.DataFrame:
    """Load and clean the survey dataset, preferring the pre-processed file."""
    if CLEAN_PATH.exists():
        df = load_poll_data(str(CLEAN_PATH))
    elif RAW_PATH.exists():
        raw_df = load_poll_data(str(RAW_PATH))
        df = clean_poll_data(raw_df)
    else:
        st.error(
            "No dataset found. "
            "Run `python generate_data.py` from the project root to create the sample dataset."
        )
        st.stop()
    return df


df_full = load_data()

# ---------------------------------------------------------------------------
# Sidebar — global filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style='text-align:center; padding: 0.5rem 0 1.2rem;'>
            <span style='font-size:2rem;'>📊</span>
            <div style='font-size:1.1rem; font-weight:700; color:#818cf8; margin-top:0.3rem;'>
                Poll Results Visualizer
            </div>
            <div style='font-size:0.75rem; color:#64748b; margin-top:0.2rem;'>
                Student Portfolio Project
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### Filters")

    all_departments = sorted(df_full["department"].dropna().unique().tolist())
    selected_departments = st.multiselect(
        "Department",
        options=all_departments,
        default=all_departments,
        help="Filter respondents by academic department.",
    )

    all_years = sorted(df_full["study_year"].dropna().unique().tolist())
    selected_years = st.multiselect(
        "Study Year",
        options=[int(y) for y in all_years],
        default=[int(y) for y in all_years],
        help="Filter respondents by study year (1 to 4).",
    )

    st.markdown("---")
    show_pct = st.toggle("Show percentages instead of counts", value=False)

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.75rem; color:#475569;'>"
        "Dataset: synthetic sample<br>500 respondents · 9 columns<br>"
        "Seed: 42 (reproducible)"
        "</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
df = df_full.copy()
if selected_departments:
    df = df[df["department"].isin(selected_departments)]
if selected_years:
    df = df[df["study_year"].isin(selected_years)]

n_filtered = len(df)
n_total = len(df_full)
is_filtered = n_filtered < n_total

# ---------------------------------------------------------------------------
# Hero Banner
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero-banner">
        <div class="hero-title">📊 Poll Results Visualizer</div>
        <p class="hero-sub">
            An interactive survey analytics dashboard — explore student preferences,
            satisfaction scores, and learning insights from {n_total} synthetic respondents.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if is_filtered:
    badges_html = "".join(
        f"<span class='filter-badge'>📁 {d}</span>" for d in selected_departments
    )
    badges_html += "".join(
        f"<span class='filter-badge'>📅 Year {y}</span>" for y in selected_years
    )
    st.markdown(
        f"<div style='margin-bottom:0.8rem;'>🔍 Active filters: {badges_html}"
        f"<span style='color:#94a3b8; font-size:0.82rem;'>"
        f" → {n_filtered} of {n_total} respondents</span></div>",
        unsafe_allow_html=True,
    )

if df.empty:
    st.warning("No respondents match the selected filters. Adjust the sidebar filters to continue.")
    st.stop()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_overview, tab_charts, tab_insights, tab_data = st.tabs(
    ["🏠 Overview", "📈 Visualizations", "💡 Insights", "🗃️ Raw Data"]
)

# ============================================================
# TAB 1 — OVERVIEW
# ============================================================
with tab_overview:

    numeric_summary = get_numeric_summary(df)

    sat_mean = float(
        numeric_summary.loc[numeric_summary["column"] == "training_satisfaction", "mean"].values[0]
    )
    rec_mean = float(
        numeric_summary.loc[numeric_summary["column"] == "recommendation_score", "mean"].values[0]
    )

    internship_yes = int((df["internship_interest"].str.strip().str.lower() == "yes").sum())
    internship_pct = round(internship_yes / n_filtered * 100, 1) if n_filtered else 0.0

    col1, col2, col3, col4 = st.columns(4)

    def kpi_html(label: str, value: str, delta: str = "") -> str:
        return (
            f"<div class='metric-card'>"
            f"<div class='metric-label'>{label}</div>"
            f"<div class='metric-value'>{value}</div>"
            f"<div class='metric-delta'>{delta}</div>"
            f"</div>"
        )

    with col1:
        st.markdown(kpi_html("Total Respondents", str(n_filtered), f"of {n_total} total"), unsafe_allow_html=True)
    with col2:
        st.markdown(kpi_html("Avg. Satisfaction", f"{sat_mean:.2f} / 5", "Training rating"), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi_html("Avg. Recommendation", f"{rec_mean:.2f} / 10", "NPS-style score"), unsafe_allow_html=True)
    with col4:
        st.markdown(kpi_html("Internship Interest", f"{internship_pct}%", f"{internship_yes} respondents"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown("<div class='section-header'>Numeric Summary</div>", unsafe_allow_html=True)
        display_numeric = numeric_summary[["column", "mean", "median", "std", "min", "max", "iqr"]].copy()
        display_numeric.columns = ["Column", "Mean", "Median", "Std Dev", "Min", "Max", "IQR"]
        st.dataframe(display_numeric, use_container_width=True, hide_index=True)

    with col_right:
        st.markdown("<div class='section-header'>Missing Value Audit</div>", unsafe_allow_html=True)
        mv_df = get_missing_value_summary(df)
        mv_df.columns = ["Column", "Missing Count", "Missing %"]
        st.dataframe(mv_df, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>Department Composition</div>", unsafe_allow_html=True)

    dept_freq = get_categorical_frequency(df, "department")
    dept_freq.columns = ["Department", "Count", "Percentage (%)"]

    col_d1, col_d2 = st.columns([1, 2])
    with col_d1:
        st.dataframe(dept_freq, use_container_width=True, hide_index=True)
    with col_d2:
        import plotly.graph_objects as go

        pie_fig = go.Figure(
            go.Pie(
                labels=dept_freq["Department"],
                values=dept_freq["Count"],
                hole=0.45,
                marker_colors=["#6366f1", "#10b981", "#f59e0b", "#ec4899", "#06b6d4"],
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
            )
        )
        pie_fig.update_layout(
            title="Department Composition",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(font=dict(color="#94a3b8")),
        )
        st.plotly_chart(pie_fig, use_container_width=True)


# ============================================================
# TAB 2 — VISUALIZATIONS
# ============================================================
with tab_charts:

    def apply_dark_theme(fig: "go.Figure") -> "go.Figure":
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            title_font_color="#c7d2fe",
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
            xaxis=dict(gridcolor="rgba(99,102,241,0.1)", color="#94a3b8"),
            yaxis=dict(gridcolor="rgba(99,102,241,0.1)", color="#94a3b8"),
        )
        return fig

    st.markdown("<div class='section-header'>Distribution Charts</div>", unsafe_allow_html=True)
    r1c1, r1c2 = st.columns(2, gap="medium")

    with r1c1:
        fig_sat = apply_dark_theme(plot_satisfaction_distribution(df, as_percentage=show_pct))
        st.plotly_chart(fig_sat, use_container_width=True, key="sat_dist")

    with r1c2:
        fig_lang = apply_dark_theme(plot_language_distribution(df, as_percentage=show_pct))
        st.plotly_chart(fig_lang, use_container_width=True, key="lang_dist")

    r2c1, r2c2 = st.columns(2, gap="medium")

    with r2c1:
        fig_learn = apply_dark_theme(plot_learning_method_distribution(df, as_percentage=show_pct))
        st.plotly_chart(fig_learn, use_container_width=True, key="learn_dist")

    with r2c2:
        fig_rec = apply_dark_theme(plot_recommendation_distribution(df, as_percentage=show_pct))
        st.plotly_chart(fig_rec, use_container_width=True, key="rec_dist")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>Department Cross-Tabulations</div>", unsafe_allow_html=True)

    barmode_choice = st.radio(
        "Bar mode",
        options=["group", "stack"],
        index=0,
        horizontal=True,
        key="barmode_radio",
    )

    r3c1, r3c2 = st.columns(2, gap="medium")

    with r3c1:
        fig_dept_lang = apply_dark_theme(
            plot_department_language_comparison(df, barmode=barmode_choice, as_percentage=show_pct)
        )
        st.plotly_chart(fig_dept_lang, use_container_width=True, key="dept_lang")

    with r3c2:
        fig_dept_intern = apply_dark_theme(
            plot_department_internship_interest(df, barmode=barmode_choice, as_percentage=show_pct)
        )
        st.plotly_chart(fig_dept_intern, use_container_width=True, key="dept_intern")


# ============================================================
# TAB 3 — INSIGHTS
# ============================================================
with tab_insights:

    st.markdown("<div class='section-header'>Automated Survey Insights</div>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#64748b; font-size:0.88rem;'>All metrics are computed dynamically from the "
        "filtered dataset. Figures update automatically when sidebar filters change.</p>",
        unsafe_allow_html=True,
    )

    insights = generate_all_insights(df)

    accent_colors = [
        "#6366f1", "#10b981", "#f59e0b", "#ec4899", "#06b6d4", "#8b5cf6", "#f97316",
    ]

    col_i1, col_i2 = st.columns(2, gap="large")

    for idx, insight in enumerate(insights):
        col = col_i1 if idx % 2 == 0 else col_i2
        accent = accent_colors[idx % len(accent_colors)]

        raw_metric = insight["metric_value"]
        metric_display = f"{raw_metric:.2f}" if isinstance(raw_metric, float) else str(raw_metric)

        pct = insight.get("percentage")
        pct_display = f" · {pct:.1f}%" if pct is not None else ""

        with col:
            st.markdown(
                f"""
                <div class="insight-card" style="border-left-color:{accent};">
                    <div class="insight-title" style="color:{accent};">{insight['title']}</div>
                    <div class="insight-metric">{metric_display}{pct_display}</div>
                    <div class="insight-text">{insight['summary_text']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with st.expander("View detailed insight data", expanded=False):
        for insight in insights:
            st.markdown(f"**{insight['title']}**")
            if isinstance(insight.get("details"), dict):
                detail_df = pd.DataFrame(
                    list(insight["details"].items()), columns=["Key", "Value"]
                )
                st.dataframe(detail_df, use_container_width=True, hide_index=True)
            st.markdown("---")


# ============================================================
# TAB 4 — RAW DATA
# ============================================================
with tab_data:

    st.markdown("<div class='section-header'>Survey Dataset Explorer</div>", unsafe_allow_html=True)

    col_search, col_colfilter = st.columns([2, 3])
    with col_search:
        search_term = st.text_input(
            "Search comments",
            placeholder="Type to filter rows with matching text…",
            key="data_search",
        )
    with col_colfilter:
        all_cols = list(df.columns)
        selected_cols = st.multiselect(
            "Columns to display",
            options=all_cols,
            default=all_cols,
            key="col_select",
        )

    display_df = df[selected_cols].copy() if selected_cols else df.copy()

    if search_term:
        mask = display_df.apply(
            lambda col: col.astype(str).str.contains(search_term, case=False, na=False)
        ).any(axis=1)
        display_df = display_df[mask]

    st.markdown(
        f"<p style='color:#64748b; font-size:0.85rem;'>"
        f"Showing <strong style='color:#818cf8;'>{len(display_df)}</strong> of "
        f"<strong style='color:#818cf8;'>{n_filtered}</strong> filtered rows.</p>",
        unsafe_allow_html=True,
    )

    st.dataframe(display_df, use_container_width=True, hide_index=False, height=420)

    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered data as CSV",
        data=csv_bytes,
        file_name="filtered_poll_data.csv",
        mime="text/csv",
        key="download_csv",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>Column Descriptions</div>", unsafe_allow_html=True)

    schema = {
        "response_id": "Unique respondent identifier (integer, sequential).",
        "department": "Academic department of the respondent (categorical).",
        "study_year": "Current year of study, 1 to 4 (integer).",
        "preferred_language": "Most preferred programming language (categorical).",
        "preferred_learning_method": "Preferred mode of learning (categorical).",
        "training_satisfaction": "Training satisfaction rating, 1 (lowest) to 5 (highest).",
        "internship_interest": "Internship placement interest — Yes or No.",
        "recommendation_score": "Likelihood to recommend score, 0 to 10.",
        "comments": "Optional open-ended written feedback (approx. 47% missing by design).",
    }

    schema_df = pd.DataFrame(
        [{"Column": k, "Description": v} for k, v in schema.items()]
    )
    st.dataframe(schema_df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    """
    <hr style='margin-top:2.5rem; margin-bottom:1rem;'>
    <div style='text-align:center; color:#475569; font-size:0.8rem; padding-bottom:1rem;'>
        Poll Results Visualizer · Student Portfolio Project ·
        Built with Python, Pandas, Plotly and Streamlit ·
        Synthetic dataset — seed 42 — 500 respondents
    </div>
    """,
    unsafe_allow_html=True,
)
