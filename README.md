# Poll Results Visualizer

An Interactive Survey Analytics and Business Insights Dashboard.

---

## 1. Project Overview

The Poll Results Visualizer is an end-to-end survey analytics platform designed to convert raw polling data into interactive visual intelligence and automated executive narrative reports. Built with Python, Pandas, Plotly, and Streamlit, the application automates data ingestion, sanitization, exploratory statistical evaluation, dynamic charting, and narrative insight synthesis.

The project demonstrates modular software engineering principles, automated test-driven development (90 unit and integration tests passing), and clean data governance. It serves both technical practitioners seeking an extensible data science pipeline and management stakeholders requiring clear, real-time visibility into survey distributions and satisfaction metrics.

All data in this repository is 100% synthetic (generated deterministically under seed 42 with N=500 respondents) to ensure complete data privacy while providing fully reproducible benchmarks.

---

## 2. Business Problem

Organizations frequently collect survey and polling feedback across academic cohorts, employee teams, or customer segments. Despite the value of this feedback, traditional analysis workflows suffer from critical bottlenecks:

- Inconsistent Data Hygiene: Raw survey responses often include trailing whitespace, irregular text casing, and non-standard categorical entries that break automated downstream processes.
- Fragile Missing Value Handling: Real surveys contain optional free-text comments or blank feedback fields. Traditional pipelines either drop incomplete records entirely (distorting sample representativeness) or crash on unhandled nulls.
- Static and Inflexible Reporting: Standard spreadsheets and slide decks provide static snapshots that cannot be filtered interactively by department, study year, or cohort attributes.
- Manual and Delayed Reporting: Analysts spend hours writing repetitive narrative summaries for each demographic segment rather than leveraging automated, deterministic insight engines.

---

## 3. Solution Architecture

The Poll Results Visualizer solves these challenges through a modular, decoupled architecture where each stage of the lifecycle is handled by a specialized component:

```
+-----------------------------------------------------------------------------------+
|                                 SYSTEM ARCHITECTURE                               |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
                         +----------------------------------+
                         |     Raw Survey Data Ingestion    |
                         |   (data/raw/sample_poll_data)    |
                         +----------------+-----------------+
                                          |
                                          v
                         +----------------------------------+
                         |        Data Loader Module        |
                         |       (src/data_loader.py)       |
                         +----------------+-----------------+
                                          |
                                          v
                         +----------------------------------+
                         |       Data Cleaning Suite        |
                         |      (src/data_cleaning.py)      |
                         +----------------+-----------------+
                                          |
                                          v
                         +----------------------------------+
                         |      Clean Processed Dataset     |
                         | (data/processed/clean_poll_data) |
                         +----------------+-----------------+
                                          |
                 +------------------------+------------------------+
                 |                                                 |
                 v                                                 v
   +----------------------------+                    +----------------------------+
   | Statistical Analysis Engine|                    | Interactive Visualizations |
   |      (src/analysis.py)     |                    |   (src/visualizations.py)  |
   +-------------+--------------+                    +--------------+-------------+
                 |                                                  |
                 v                                                  |
   +----------------------------+                                   |
   | Dynamic Business Insights  |                                   |
   |      (src/insights.py)     |                                   |
   +-------------+--------------+                                   |
                 |                                                  |
                 +------------------------+-------------------------+
                                          |
                                          v
                         +----------------------------------+
                         |    Streamlit Interactive App     |
                         |             (app.py)             |
                         +----------------------------------+
```

1. Ingestion and Verification: The Data Loader enforces strict data contracts, column typing, and boundary protections.
2. Cleaning and Standardization: The Cleaning module trims string whitespace, enforces numeric domain bounds, validates categorical vocabularies, and safely tracks optional comments without data loss.
3. Analytical Computation: The Analysis module computes summary statistics, frequency tables, and multi-variable cross-tabulations.
4. Dynamic Insight Generation: The Insights module evaluates aggregated metrics against business rules to generate automated, narrative findings.
5. Interactive Web Interface: Streamlit combines all components into a four-tab dashboard with cascading sidebar filters.

---

## 4. Key Features and Capabilities

### Data Hygiene and Integrity
- Automatic whitespace trimming across all categorical and text fields.
- Value range enforcement: Training Satisfaction (1 to 5) and Recommendation Score (0 to 10).
- Categorical vocabulary validation across departments, programming languages, and learning methods.
- Accurate handling of optional text feedback, retaining 235 null comment records without corruption.
- Deterministic synthetic dataset generator (`generate_data.py`) configured with fixed random seed 42.

### Statistical Analysis Engine
- Dataset structural overview: record count, column count, and data types.
- Missingness audits: exact null counts and percentages per column.
- Numeric summary metrics: Mean, Median, Standard Deviation, Minimum, and Maximum.
- Single-variable frequency counts and percentages.
- Two-variable cross-tabulations with optional row/column normalization.

### Six Interactive Plotly Visualizations
1. Training Satisfaction Distribution: Bar chart analyzing satisfaction scores (1 to 5).
2. Preferred Programming Language Distribution: Horizontal bar chart ranking language preferences.
3. Preferred Learning Method Distribution: Categorical breakdown of hands-on, video, and documentation modalities.
4. Department vs. Preferred Language: Cross-tabulation bar chart with grouped and stacked toggle views.
5. Recommendation Score Distribution: Net Promoter style histogram (0 to 10 scale).
6. Department vs. Internship Interest: Comparative cohort breakdown measuring career readiness.

### Automated Executive Narrative Insights
- Top Programming Language: Detects modal choice, response volume, and population share.
- Top Learning Method: Detects most preferred training methodology.
- Training Satisfaction Index: Average rating, median, and percentage of positive respondents (ratings 4 and 5).
- Departmental Career Leader: Identifies the academic department with highest internship interest percentage.
- Overall Internship Demand: Measures total population placement participation interest.
- Recommendation Score Index: Calculates average, median, and top-tier promoter percentage (ratings 9 and 10).
- Qualitative Feedback Engagement: Tracks response and completion rates for open-ended comments.

### Self-Service Dashboard Interface
- Persistent sidebar filters: Department multiselect, Study Year multiselect, and Count vs. Percentage toggles.
- Real-time KPI metric cards: Total Respondents, Average Satisfaction, Average Recommendation, and Internship Interest Rate.
- Raw Data Explorer: Full-text search across all columns, column subset selector, and instant CSV export.

---

## 5. Technology Stack

- Core Programming Language: Python 3.10+ (tested and verified on Python 3.14.3)
- Data Manipulation and Analysis: Pandas, NumPy
- Interactive Charting Engine: Plotly Graph Objects and Plotly Express
- Web Dashboard Framework: Streamlit
- Testing and Quality Assurance: Pytest
- Development and Exploration: Jupyter / IPython Notebooks
- Version Control: Git, GitHub

---

## 6. How to Run and Execute

### Prerequisites
Ensure Python 3.10 or higher and Git are installed:
```powershell
python --version
git --version
```

### Installation Steps

1. Clone the repository:
```powershell
git clone https://github.com/mdsalmanbiswasdev/poll-results-visualizer.git
cd poll-results-visualizer
```

2. Set up and activate a virtual environment:
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

3. Install required dependencies:
```powershell
pip install -r requirements.txt
```

4. Optional configuration:
If custom port or path settings are desired, copy the provided environment template:
```powershell
Copy-Item .env.example .env
```
Note: The `.env` file is excluded from version control by `.gitignore` to maintain security.

---

### Execution Modes

#### Mode 1: Run the End-to-End CLI Pipeline
Executes data ingestion, sanitization, statistical summarization, and automated insight generation directly in your terminal:
```powershell
python main.py
```

#### Mode 2: Launch the Interactive Web Dashboard
Starts the local Streamlit application server:
```powershell
streamlit run app.py
```
Open your browser and navigate to:
`http://localhost:8501`

#### Mode 3: Execute the Automated Test Suite
Runs the comprehensive 90-test automated verification suite:
```powershell
pytest -v
```

#### Mode 4: Regenerate the Benchmark Synthetic Dataset
Regenerates the raw survey dataset under controlled random seed 42:
```powershell
python generate_data.py
```

---

## 7. Results and Key Findings

### Baseline Survey Results (N=500 Respondents)

The full pipeline was executed against the benchmark survey dataset. The key findings are summarized below:

| Metric / Survey Dimension | Value / Finding | Context and Population Share |
| :--- | :--- | :--- |
| Total Survey Sample Size | 500 records | 100% valid records after cleaning |
| Most Preferred Language | Python | 206 responses (41.2% share) |
| Second Preferred Language | Java | 129 responses (25.8% share) |
| Top Learning Method | Hands-on Projects | 232 responses (46.4% share) |
| Mean Training Satisfaction | 3.55 / 5.00 | Median: 4.00, Std Dev: 1.06 |
| Positive Satisfaction Rate | 55.2% | Rated satisfaction at 4 or 5 |
| Overall Internship Interest | 74.4% | 372 of 500 respondents answered "Yes" |
| Highest Internship Interest Dept | IT Department | 78.0% interest rate (138 of 177 respondents) |
| Mean Recommendation Score | 6.47 / 10.00 | Median: 7.00, Std Dev: 2.43 |
| Top-Tier Recommendation Rate | 19.0% | Rated recommendation score at 9 or 10 |
| Written Comments Engagement | 53.0% | 265 provided feedback, 235 left blank |

### Automated Testing and Quality Assurance Results

The test suite validates data ingestion, cleaning logic, mathematical consistency, visualization structure, insight dynamism, and dashboard filter mechanics:

| Test Module | Tests | Execution Status | Coverage Focus |
| :--- | :--- | :--- | :--- |
| `tests/test_data_loader.py` | 10 | PASSED | Missing files, zero-byte checks, schema validation |
| `tests/test_data_cleaning.py` | 11 | PASSED | Whitespace stripping, range checks, null preservation |
| `tests/test_analysis.py` | 13 | PASSED | Descriptive stats, cross-tabulations, shape integrity |
| `tests/test_visualizations.py` | 12 | PASSED | Plotly figure generation, data types, percentage views |
| `tests/test_insights.py` | 13 | PASSED | Dynamic narrative calculations, tie-break handling |
| `tests/test_dashboard_logic.py` | 31 | PASSED | Cascading filters, KPI denominators, search, CSV export |
| **Total Test Suite** | **90** | **100% PASS** | **Zero test failures, zero regressions** |

---

## 8. Dashboard Screenshots and Visual Previews

The platform features four functional tabs with persistent sidebar controls. Visual screenshot previews are linked below directly from the `images/` directory:

### Tab 1: Executive Overview
Displays high-level KPI cards, summary numeric statistics, missing data audit tables, and cohort distribution donut charts.

![Dashboard Overview](images/dashboard_overview.png)
*Figure 1: Executive KPI metric cards, numeric distribution summary, and department breakdown.*

### Tab 2: Interactive Visualizations
Interactive Plotly charts supporting real-time toggling between grouped and stacked layouts, as well as raw counts and normalized percentages.

![Interactive Visualizations](images/visualizations_tab.png)
*Figure 2: Interactive Plotly chart gallery with dynamic visual configuration controls.*

### Tab 3: Automated Executive Insights
Dynamically rendered narrative cards with color-coded thematic accents and expandable breakdown tables.

![Automated Insights](images/automated_insights.png)
*Figure 3: Automated narrative insights generated directly from cohort-filtered responses.*

### Tab 4: Raw Data Explorer
Searchable data grid with free-text search across all columns, dynamic column selection, filtered record count, and instant CSV export.

![Raw Data Explorer](images/data_explorer.png)
*Figure 4: Self-service data table with column selector, search filter, and CSV download.*

*Note on Image Assets: Screenshot files are maintained in the `images/` folder. When running the project locally, explore all features interactively via `streamlit run app.py`.*

---

## 9. Security, Privacy, and Repository Structure

### Data Privacy and Security Statement
- Zero Real-World PII: All survey records, respondent identifiers, and responses are 100% synthetic.
- Zero Hardcoded Secrets: Audited and verified. No private API keys, credentials, or tokens are present in the repository.
- Environment Protection: Standardized `.gitignore` rules prevent `.env`, `.env.*`, `.venv/`, `.streamlit/`, and log files from entering version control.

### Project Directory Layout

```
poll-results-visualizer/
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

## 11. Future Improvements and Roadmap

The Poll Results Visualizer architecture is designed for modular extensibility. The following strategic and technical improvements represent the planned roadmap:

### 1. Live Polling Integration
- Deploy synchronous audience voting via mobile-friendly web interfaces and QR codes.
- Implement bidirectional WebSocket communication using FastAPI WebSockets to ingest incoming responses during live presentations, town halls, or lectures with zero compilation lag.
- Incorporate IP-based and token-based rate limiting via Redis to prevent duplicate submissions.

### 2. Streamlit Dashboard Enhancements
- Role-Based Access Control (RBAC): Introduce user authentication (via Streamlit Authenticator or OAuth2) separating Administrator, Analyst, and Executive access tiers.
- Automated Executive Export: Add single-click generation of branded PDF summary briefs and PowerPoint presentation decks directly from dashboard state.
- WCAG 2.1 Accessibility: Implement high-contrast color modes and screen-reader compliant data visualizations.

### 3. Sentiment Analysis on Open-Ended Responses
- Transformer NLP Pipeline: Integrate Hugging Face pretrained models (such as DistilRoBERTa or CardiffNLP sentiment models) to score polarity and subjectivity on the qualitative feedback column.
- Thematic Topic Modeling: Deploy KeyBERT or BERTopic to cluster qualitative comments automatically into recurring feedback themes (e.g., pace of instruction, laboratory support, documentation clarity).
- Sentiment-stratified word frequency visualizations embedded directly into the Insights tab.

### 4. Demographic Deep-Dive Analysis
- Hypothesis Testing: Implement Chi-Square tests of independence and ANOVA to determine whether satisfaction differentials across cohorts and departments meet statistical significance thresholds (p < 0.05).
- Multivariate Regression: Calculate odds ratios and regression coefficients to measure the relative impact of learning methodology and study year on final recommendation scores.
- Predictive Persona Clustering: Apply unsupervised k-means clustering to identify distinct respondent profiles.

### 5. Real-Time Result Updates
- Event-Driven Streaming: Integrate an Apache Kafka or Redis Pub-Sub pipeline to stream responses continuously into an analytical data store.
- Asynchronous Dashboard Refresh: Connect Streamlit background listeners to refresh KPI metric cards and Plotly distributions dynamically as votes arrive without manual browser reloads.

### 6. REST API Integration
- Decoupled Microservice Architecture: Expose data loading, cleaning, aggregation, and dynamic insight generation through an asynchronous FastAPI service.
- RESTful Endpoints:
  - `POST /api/v1/surveys/ingest`: Ingests and validates survey payloads against strict Pydantic schemas.
  - `GET /api/v1/surveys/summary`: Returns descriptive metrics and distribution tables as JSON.
  - `GET /api/v1/surveys/insights`: Delivers dynamically calculated narrative insights.
  - `GET /api/v1/surveys/export`: Generates on-demand filtered CSV and Parquet extracts.
- Interactive OpenAPI Swagger documentation available at `/docs`.

### 7. Power BI Dashboard Integration
- Enterprise Semantic Modeling: Publish processed survey tables to Microsoft Power BI via DirectQuery or scheduled automated refresh pipelines.
- DAX Measure Library: Implement standardized Data Analysis Expressions for executive Net Promoter metrics, top-box satisfaction shares, and department benchmarks.
- Embedded Executive Reports: Embed Power BI analytical views within corporate portals and Microsoft Teams channels.

---

## 12. License

This project is licensed under the MIT License. You are free to use, modify, and distribute this software for educational and commercial purposes.

