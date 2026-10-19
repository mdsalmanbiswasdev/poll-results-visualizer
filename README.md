# Poll Results Visualizer

An interactive survey analytics and insights dashboard built with Python, Pandas, Plotly, and Streamlit.

---

## 📌 Project Overview

The **Poll Results Visualizer** is a student portfolio project providing clean, reproducible, and interactive exploration of survey and polling datasets. It emphasises modular software design, transparent statistical computation, and dynamic visual reporting.

> **Dataset Notice:** All data is 100% synthetic (seed 42, 500 respondents). No private or personally-identifiable information is included. Results are labelled as sample observations and must not be interpreted as statistically significant or causal findings about any real population.

---

## 🎯 Objectives

- **Data Ingestion & Hygiene**: Load raw polling data, enforce consistent cleaning pipelines, and preserve immutable raw inputs.
- **Statistical Summarisation**: Compute response distributions, descriptive statistics, and cross-tabulated breakdowns.
- **Interactive Visualisation**: Render six interactive Plotly charts covering distributions, cross-tabs, and demographic comparisons.
- **Automated Insights**: Synthesise seven key trends into concise, dynamically-computed narrative summaries.
- **Interactive Dashboard**: A multi-tab Streamlit web dashboard for non-technical exploration with real-time sidebar filters.
- **Production-Ready Quality**: Comprehensive test coverage (90 tests), thorough documentation, and clean modular code.

---

## ✅ Implemented Features

| Module | File | Status |
|---|---|---|
| Data Loading Pipeline | `src/data_loader.py` | ✅ Complete |
| Data Cleaning Suite | `src/data_cleaning.py` | ✅ Complete |
| Statistical Analysis Engine | `src/analysis.py` | ✅ Complete |
| Interactive Plotly Charts (6 charts) | `src/visualizations.py` | ✅ Complete |
| Automated Insights Generator (7 insights) | `src/insights.py` | ✅ Complete |
| Streamlit Dashboard (4 tabs) | `app.py` | ✅ Complete |
| CLI Pipeline Runner | `main.py` | ✅ Complete |
| Unit & Integration Tests | `tests/` | ✅ 90 tests passing |
| EDA Notebook | `notebooks/exploratory_data_analysis.ipynb` | ✅ Complete |
| Synthetic Data Generator | `generate_data.py` | ✅ Complete |

---

## 🗂️ Project Structure

```
Poll-Results-Visualizer/
├── app.py                                  # Streamlit interactive dashboard (main UI)
├── main.py                                 # CLI pipeline runner (load → clean → analyse → insights)
├── generate_data.py                        # Synthetic poll data generator (seed 42)
├── requirements.txt                        # Direct project dependencies
├── .gitignore                              # Git exclusion rules
├── README.md                               # Project documentation (this file)
├── data/
│   ├── raw/
│   │   └── sample_poll_data.csv            # Raw synthetic survey data (500 rows, 9 columns)
│   ├── processed/
│   │   └── clean_poll_data.csv             # Sanitised and validated dataset
│   └── README.md                           # Data governance and schema documentation
├── src/
│   ├── __init__.py
│   ├── data_loader.py                      # CSV ingestion with schema validation
│   ├── data_cleaning.py                    # Whitespace trim, domain checks, range validation
│   ├── analysis.py                         # Descriptive statistics and cross-tabulations
│   ├── visualizations.py                   # Six reusable Plotly interactive figures
│   └── insights.py                         # Seven dynamically-computed survey insights
├── tests/
│   ├── __init__.py
│   ├── test_data_loader.py                 # 7 unit tests for loading and schema checks
│   ├── test_data_cleaning.py               # 14 unit tests for cleaning and validation
│   ├── test_analysis.py                    # 13 unit tests for statistics and cross-tabs
│   ├── test_visualizations.py             # 12 unit tests for chart functions
│   ├── test_insights.py                    # 13 unit tests for insight generation
│   └── test_dashboard_logic.py             # 31 tests for filter, search, KPI, and export logic
├── notebooks/
│   └── exploratory_data_analysis.ipynb     # Reproducible EDA notebook
├── outputs/
│   └── README.md                           # Analytical outputs guide
├── images/
│   └── README.md                           # Chart exports and UI captures guide
└── docs/                                   # Technical documentation repository
    ├── README.md
    ├── architecture.md
    ├── data_flow.md
    ├── dataset.md
    ├── execution_log.md
    ├── model_details.md
    ├── modules.md
    └── validation_guide.md
```

---

## ⚙️ Setup & Execution

### 1. Prerequisites

Python 3.10 or higher required:
```powershell
python --version
```

### 2. Create and activate virtual environment

```powershell
# Create (if not already created)
python -m venv .venv

# Activate — Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Generate synthetic dataset

```powershell
python generate_data.py
```

This creates `data/raw/sample_poll_data.csv` (500 rows, 9 columns, seed 42).

### 5. Run the CLI pipeline (optional)

```powershell
.\.venv\Scripts\python.exe main.py
```

Runs: load → clean → analyse → insights → prints a formatted summary report.

### 6. Launch the interactive dashboard

```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

Then open **http://localhost:8501** in your browser.

### 7. Run the test suite

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Expected: **90 passed, 0 failed**.

### 8. Run the EDA notebook

```powershell
.\.venv\Scripts\python.exe -m nbconvert --to notebook --execute notebooks/exploratory_data_analysis.ipynb
```

---

## 📊 Dashboard Features

| Tab | Contents |
|---|---|
| **🏠 Overview** | 4 KPI cards, numeric summary table, missing-value audit, department donut chart |
| **📈 Visualizations** | 6 interactive Plotly charts; grouped/stacked toggle; count/percentage toggle |
| **💡 Insights** | 7 colour-coded automated insight cards (computed dynamically from filtered data) |
| **🗃️ Raw Data** | Scrollable grid, free-text search, column selector, CSV download, schema reference |

**Sidebar filters** (Department, Study Year) cascade to every tab in real time.

---

## 🗄️ Dataset Schema

| Column | Type | Description |
|---|---|---|
| `response_id` | string | Unique respondent identifier |
| `department` | string | Academic department (CS, IT, ME, …) |
| `study_year` | int | Year of study, 1–4 |
| `preferred_language` | string | Most preferred programming language |
| `preferred_learning_method` | string | Preferred learning mode |
| `training_satisfaction` | int | Rating 1 (lowest) to 5 (highest) |
| `internship_interest` | string | "Yes" or "No" |
| `recommendation_score` | int | NPS-style score, 0–10 |
| `comments` | string | Optional free-text feedback (~47% missing by design) |

---

## 🔒 Data & Privacy

- **Zero PII**: No private respondent information is contained or permitted.
- **100% Synthetic**: All records are computer-generated for educational and portfolio demonstration only.
- **Reproducible**: Generator uses `random_state=42`; SHA-256 of raw CSV: `47fe9337e57f2ea5dffc0cc793700a1988701f649cbd1658d08bafcde7b27baf`.
- **Immutable Raw Data**: `data/raw/` is never modified in-place; all cleaned outputs go to `data/processed/`.

---

## 📋 Current Project Status

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Project scaffolding | ✅ Complete |
| Phase 2 | Environment audit + dependencies + synthetic dataset | ✅ Complete |
| Phase 3 | Data loading and cleaning | ✅ Complete |
| Phase 4 | EDA and statistical analysis | ✅ Complete |
| Phase 5 | Interactive Plotly visualisations | ✅ Complete |
| Phase 6 | Automated insights module | ✅ Complete |
| Phase 7 | Streamlit interactive dashboard | ✅ Complete |
| Phase 8 | Final quality assurance | ✅ Complete |

---

## 🛠️ Technology Stack

| Tool | Purpose |
|---|---|
| Python 3.14.3 | Core language |
| Pandas | Data manipulation |
| NumPy | Numerical computation |
| Plotly | Interactive visualisations |
| Streamlit | Web dashboard |
| Pytest | Unit and integration testing |
| Jupyter | EDA notebook |
