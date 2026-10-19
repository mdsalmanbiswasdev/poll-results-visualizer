# Poll Results Visualizer

An Interactive Survey Analytics and Business Insights Dashboard.

---

## Executive Summary

The Poll Results Visualizer is an end-to-end data science and business analytics application designed to ingest, clean, analyze, and visualize structured survey data. Built with Python, Pandas, Plotly, and Streamlit, the platform transforms raw survey responses into interactive business intelligence dashboards and automated executive narrative summaries.

The architecture emphasizes modular engineering standards, strict data schema validation, reproducible analysis, and comprehensive test coverage (90 unit and integration tests passing). It is engineered for both technical developers seeking extensible data pipelines and business managers requiring immediate visibility into survey distributions, cohort satisfaction, and actionable metrics.

---

## Business Problem and Solution

### The Challenge
Organizations frequently collect survey and poll data across departments, academic years, or customer segments. However, raw survey data often suffers from:
- Inconsistent respondent inputs, trailing whitespace, and unstandardized categorical labels.
- Missing values in optional feedback fields that can compromise downstream processing.
- Static spreadsheets that fail to provide real-time filtering, cross-tabulation, or intuitive visual comparisons.
- Manual analytical workflows that delay reporting and obscure high-impact findings.

### The Solution
The Poll Results Visualizer addresses these challenges through an automated pipeline:
1. Automated Data Hygiene: Enforces deterministic data contracts and type validation during ingestion while preserving raw data immutability.
2. Statistical Engine: Calculates descriptive summaries, categorical frequency distributions, and multi-dimensional cross-tabulations on demand.
3. Interactive Visualization Layer: Provides responsive, publication-quality Plotly visualizations with grouped, stacked, count, and percentage views.
4. Dynamic Executive Insights: Synthesizes key metrics into clear narrative bullet points that automatically recalculate whenever dataset filters change.
5. Self-Service Explorer: Empowers non-technical stakeholders to slice, search, review, and export customized subsets of survey data as CSV files.

---

## System Architecture

The project follows a clean modular architecture separating data ingestion, business logic, visual rendering, and the user interface.

```
                    +-----------------------------+
                    |   Raw Survey Data Source    |
                    | (data/raw/sample_poll_data) |
                    +--------------+--------------+
                                   |
                                   v
                    +-----------------------------+
                    |      Data Loader Module     |
                    |    (src/data_loader.py)     |
                    +--------------+--------------+
                                   |
                                   v
                    +-----------------------------+
                    |    Data Cleaning Module     |
                    |    (src/data_cleaning.py)   |
                    +--------------+--------------+
                                   |
                                   v
                    +-----------------------------+
                    |   Clean Processed Dataset   |
                    |(data/processed/clean_data)  |
                    +--------------+--------------+
                                   |
                 +-----------------+-----------------+
                 |                                   |
                 v                                   v
   +---------------------------+       +---------------------------+
   | Statistical Engine Module |       |   Visualizations Module   |
   |     (src/analysis.py)     |       |   (src/visualizations.py) |
   +-------------+-------------+       +-------------+-------------+
                 |                                   |
                 v                                   |
   +---------------------------+                     |
   | Dynamic Insights Engine   |                     |
   |    (src/insights.py)      |                     |
   +-------------+-------------+                     |
                 |                                   |
                 +-----------------+-----------------+
                                   |
                                   v
                    +-----------------------------+
                    | Streamlit Interactive App   |
                    |          (app.py)           |
                    +-----------------------------+
```

---

## Dashboard Interface and Screenshots

The platform features a modern, dark-themed user interface organized into four primary functional tabs with persistent sidebar filtering.

### 1. Overview Tab
Provides immediate visibility into headline Key Performance Indicators (KPIs), summary metric cards, descriptive statistics, missing data audits, and cohort distributions.

![Dashboard Overview](images/dashboard_overview.png)
*Figure 1: Executive KPI metric cards, numeric distribution summary, and department breakdown.*

### 2. Visualizations Tab
Houses six interactive Plotly charts supporting real-time toggling between grouped and stacked layouts, as well as raw counts and normalized percentages.

![Interactive Visualizations](images/visualizations_tab.png)
*Figure 2: Interactive Plotly chart gallery with dynamic visual configuration controls.*

### 3. Dynamic Insights Tab
Renders dynamically calculated executive summaries categorized into thematic cards with color-coded sentiment accents.

![Automated Insights](images/automated_insights.png)
*Figure 3: Automated narrative insights generated directly from cohort-filtered responses.*

### 4. Raw Data Explorer Tab
Offers a responsive data grid with free-text search across all columns, dynamic column selection, filtered record counters, and instant CSV export capabilities.

![Raw Data Explorer](images/data_explorer.png)
*Figure 4: Self-service data table with column selector, search filter, and CSV download.*

*Note: Visual screenshot assets are maintained in the `images/` directory. If screenshots are pending upload, the application can be explored live via the local Streamlit server.*

---

## Core Modules and Capabilities

### Data Ingestion (src/data_loader.py)
- Ingests raw CSV data with boundary checks for missing files, zero-byte files, and unreadable directories.
- Validates the presence and integrity of all required columns against strict schema definitions.
- Returns immutable copies of the DataFrame to prevent unintended side effects.

### Data Cleaning and Normalization (src/data_cleaning.py)
- Strips leading and trailing whitespace from string and categorical columns.
- Validates integer ranges (Training Satisfaction between 1 and 5; Recommendation Score between 0 and 10).
- Verifies categorical values against allowable domain vocabularies.
- Identifies and handles duplicate response identifiers.
- Accurately tracks and preserves nulls in optional feedback columns (`comments`).
- Writes clean, sanitized outputs to `data/processed/clean_poll_data.csv`.

### Statistical Analysis (src/analysis.py)
- Computes comprehensive dataset overviews: row counts, column counts, and memory/data types.
- Audits missing-value distributions with count and percentage metrics per column.
- Calculates descriptive metrics: Mean, Median, Standard Deviation, Minimum, and Maximum.
- Generates single-variable frequency tables and two-variable cross-tabulations (raw counts and row/column percentages).

### Interactive Visualizations (src/visualizations.py)
Generates six publication-ready Plotly figures:
1. Training Satisfaction Distribution: Bar chart analyzing satisfaction scores (1 to 5).
2. Preferred Programming Language Distribution: Horizontal bar chart ranking language preferences.
3. Preferred Learning Method Distribution: Visual breakdown of project-based, video, or documentation learning modes.
4. Department versus Preferred Language: Cross-tabulation chart with grouped and stacked view toggles.
5. Recommendation Score Distribution: Net Promoter-style histogram (0 to 10 scale).
6. Department versus Internship Interest: Comparative cohort breakdown measuring career readiness.

### Automated Business Insights (src/insights.py)
Computes seven dynamic narrative insights directly from data:
1. Top Programming Language: Identifies the modal language, total counts, and cohort percentage.
2. Top Learning Method: Detects the most favored training modality.
3. Overall Satisfaction Index: Calculates average, median, and top-box satisfaction percentages (ratings of 4 or 5).
4. Departmental Career Interest Leader: Highlights the academic department with the highest internship interest.
5. Overall Internship Participation: Computes total population demand for internship placement programs.
6. Recommendation Score Index: Measures Net Promoter distribution and top-tier score percentages (ratings of 9 or 10).
7. Qualitative Feedback Engagement: Tracks response rates for optional free-text comments.

---

## Dataset Specifications

The platform is packaged with a reproducible synthetic survey dataset generated via NumPy and Pandas (`generate_data.py`).

| Field Name | Data Type | Permitted Values / Range | Description |
| :--- | :--- | :--- | :--- |
| `response_id` | String | Unique string identifier | Respondent identifier |
| `department` | Categorical | Computer Science, IT, Electronics, Mechanical | Academic department |
| `study_year` | Integer | 1, 2, 3, 4 | Current year of study |
| `preferred_language` | Categorical | Python, Java, C++, JavaScript | Primary programming language |
| `training_satisfaction` | Integer | 1 to 5 | Satisfaction rating with training curriculum |
| `preferred_learning_method` | Categorical | Hands-on Projects, Video Tutorials, Documentation | Preferred educational format |
| `internship_interest` | Categorical | Yes, No | Interest in internship opportunities |
| `recommendation_score` | Integer | 0 to 10 | Likelihood to recommend program |
| `comments` | String / Null | Text feedback or NaN | Optional open-ended qualitative comments |

*Notice on Data Privacy: All data in this repository is 100% synthetic, generated under seed 42 (500 records). No real-world individuals, protected attributes, or personally identifiable information (PII) are stored.*

---

## Technology Stack

- Language: Python 3.10+ (tested on Python 3.14.3)
- Data Processing: Pandas, NumPy
- Data Visualization: Plotly Graph Objects and Express
- Web Framework: Streamlit
- Testing Framework: Pytest
- Environment Management: Python venv
- Notebooks: Jupyter / IPython

---

## Installation and Setup

### 1. Prerequisites
Ensure Python 3.10 or higher and Git are installed on your system.

Verify your environment:
```powershell
python --version
git --version
```

### 2. Clone the Repository
```powershell
git clone https://github.com/<YOUR_USERNAME>/<YOUR_REPOSITORY_NAME>.git
cd <YOUR_REPOSITORY_NAME>
```

### 3. Set Up a Virtual Environment
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Optional Environment Configuration
If custom server settings or alternative file paths are required, copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
*Note: The `.env` file is excluded from Git tracking by `.gitignore` to ensure security.*

---

## Running the Application

### Option A: Run the End-to-End Pipeline (CLI)
Executes data loading, data cleaning, statistical evaluation, and automated insight generation directly in the terminal:
```powershell
python main.py
```

### Option B: Launch the Interactive Dashboard
Starts the Streamlit web server:
```powershell
streamlit run app.py
```
Once started, access the dashboard in your browser at:
`http://localhost:8501`

### Option C: Regenerate the Synthetic Dataset
To regenerate the benchmark dataset under a controlled seed:
```powershell
python generate_data.py
```

---

## Testing and Quality Assurance

The codebase includes an automated test suite verifying every component from raw data ingestion to dashboard filtering logic.

### Run All Tests
```powershell
pytest -v
```

### Test Suite Breakdown (90 Tests Total)
- `tests/test_data_loader.py` (10 tests): Verifies schema validation, missing file handling, and column consistency.
- `tests/test_data_cleaning.py` (11 tests): Verifies whitespace stripping, duplicate detection, range enforcement, and null preservation.
- `tests/test_analysis.py` (13 tests): Verifies descriptive calculations, frequency calculations, and cross-tabulation math.
- `tests/test_visualizations.py` (12 tests): Verifies Plotly figure structures, data integrity, and percentage conversions.
- `tests/test_insights.py` (13 tests): Verifies dynamic narrative generation, tie handling, and non-hardcoded logic.
- `tests/test_dashboard_logic.py` (31 tests): Verifies single and multi-department filtering, study-year slicing, KPI denominators, search filtering, and CSV export functionality.

---

## Project Directory Structure

```
Poll-Results-Visualizer/
├── .env.example                            # Configuration template for environment variables
├── .gitignore                              # Git exclusion rules for environments, caches, and logs
├── README.md                               # Project documentation and architectural guide
├── app.py                                  # Streamlit interactive dashboard application
├── main.py                                 # Pipeline runner script (load, clean, analyze, report)
├── generate_data.py                        # Reproducible synthetic dataset generator
├── requirements.txt                        # Direct project dependencies
├── data/
│   ├── raw/
│   │   ├── .gitkeep
│   │   └── sample_poll_data.csv            # Raw synthetic survey responses (500 records)
│   ├── processed/
│   │   ├── .gitkeep
│   │   └── clean_poll_data.csv             # Sanitized and validated dataset
│   └── README.md                           # Data governance and schema documentation
├── docs/                                   # In-depth technical documentation
│   ├── README.md                           # Documentation catalog
│   ├── architecture.md                     # Architectural specifications
│   ├── data_flow.md                        # Sequence and dataflow diagrams
│   ├── dataset.md                          # Data dictionary and variable attributes
│   ├── execution_log.md                    # Sequential development and audit trail
│   ├── model_details.md                    # Statistical definitions and logic
│   ├── modules.md                          # API reference and function signatures
│   └── validation_guide.md                 # Quality assurance criteria
├── images/
│   ├── .gitkeep                            # Retains directory in source control
│   └── README.md                           # Image assets guide and screenshot documentation
├── notebooks/
│   └── exploratory_data_analysis.ipynb     # Interactive Jupyter analysis notebook
├── outputs/
│   └── README.md                           # Destination guide for analytical exports
├── src/                                    # Reusable source code package
│   ├── __init__.py
│   ├── data_loader.py                      # Data ingestion and schema validation
│   ├── data_cleaning.py                    # Cleaning, validation, and serialization
│   ├── analysis.py                         # Statistical analysis and aggregation
│   ├── visualizations.py                   # Reusable Plotly chart builders
│   └── insights.py                         # Automated business insight generators
└── tests/                                  # Pytest automated test suite
    ├── __init__.py
    ├── test_data_loader.py
    ├── test_data_cleaning.py
    ├── test_analysis.py
    ├── test_visualizations.py
    ├── test_insights.py
    └── test_dashboard_logic.py
```

---

## Security, Privacy, and Compliance

- Zero Hardcoded Secrets: Scanned and audited. No API keys, passwords, database credentials, or tokens exist in source code.
- Credential Protection: Standardized `.env` exclusions configured in `.gitignore`.
- Data Anonymization: The project uses exclusively synthetic data; no actual student, employee, or customer data is stored or processed.
- Deterministic Execution: Controlled random seeds ensure reproducible testing across different environments.

---

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute this software for educational and commercial purposes.
