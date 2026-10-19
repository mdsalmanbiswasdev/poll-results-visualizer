# Data Management & Dataset Documentation

This directory houses all raw and processed dataset artifacts for the **Poll Results Visualizer** project.

---

## 📂 Directory Layout

```
data/
├── raw/
│   ├── .gitkeep
│   └── sample_poll_data.csv    # Raw synthetic survey data (500 rows)
├── processed/
│   ├── .gitkeep
│   └── clean_poll_data.csv     # Cleaned, standardized, and validated dataset (500 rows)
└── README.md                   # Data policies, schema definitions, and cleaning guide
```

---

## ⚠️ Synthetic Data Notice & Privacy Precautions
- **100% Synthetic:** All data stored in `data/raw/sample_poll_data.csv` is completely synthetic and generated for demonstration and portfolio development purposes. It does not represent actual students, individuals, or institutions.
- **Zero PII Policy:** No personally identifiable information (PII)—including names, email addresses, phone numbers, or IP addresses—is contained or permitted in this repository.
- **Git Tracking Rules:** As defined in `.gitignore`, general data files are excluded by default, with an explicit whitelist exception (`!data/raw/sample_*`, `!data/raw/synthetic_*`, `!data/processed/sample_*`, `!data/processed/clean_*`) permitting reproducible sample files for public portfolio evaluation.

---

## 📊 Dataset Schema (`sample_poll_data.csv` & `clean_poll_data.csv`)

| Column Name | Data Type | Permitted Values / Range | Description |
| :--- | :--- | :--- | :--- |
| `response_id` | String | `RESP_0001` to `RESP_0500` | Unique respondent identifier (non-null, whitespace trimmed). |
| `department` | String | `IT`, `Commerce`, `Science`, `Arts` | Student's primary academic department. |
| `study_year` | Integer | `1`, `2`, `3`, `4` | Current year of academic study. |
| `preferred_language` | String | `Python`, `Java`, `C++`, `JavaScript` | Primary programming language preference. |
| `training_satisfaction`| Integer | `1` to `5` | Likert rating of training satisfaction (1=Lowest, 5=Highest). |
| `preferred_learning_method` | String | `Hands-on Projects`, `Video Tutorials`, `Classroom Lectures`, `Online Courses` | Preferred pedagogical method. |
| `internship_interest` | String | `Yes`, `No` | Expressed interest in industry internship placement. |
| `recommendation_score`| Integer | `0` to `10` | Likelihood to recommend score (0 to 10 inclusive). |
| `comments` | String / NaN | Text or `NaN` | Optional qualitative feedback (235 missing values preserved). |

---

## 🧹 Cleaning & Validation Policy (`src.data_cleaning`)
- **Raw Data Immutability**: `data/raw/` is treated as strictly read-only. Cleaned outputs write exclusively to `data/processed/`.
- **Whitespace Sanitation**: Leading and trailing whitespaces are trimmed from all string columns.
- **Zero Silent Deletion**: Records with data quality issues (duplicates, unknown categories, out-of-range ratings) raise a `DataValidationError` with exact error diagnostics rather than being silently dropped.
- **Preservation of Optional Nulls**: The `comments` field is optional survey feedback; valid responses with missing comments are preserved without imputation of fake text.
- **Type Stability**: Integer fields (`study_year`, `training_satisfaction`, `recommendation_score`) are explicitly validated and typed as standard integers.

---

## 🔄 Regeneration & Processing

### 1. Regenerate Raw Synthetic Dataset
```bash
python generate_data.py --samples 500 --seed 42 --output data/raw/sample_poll_data.csv
```

### 2. Generate Cleaned Dataset
```python
from src.data_cleaning import process_and_save_poll_data

process_and_save_poll_data(
    raw_path="data/raw/sample_poll_data.csv",
    processed_path="data/processed/clean_poll_data.csv",
    overwrite=True,
)
```
