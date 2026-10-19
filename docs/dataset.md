# Dataset Specifications: Poll Results Visualizer

## 1. Overview
This document tracks dataset sources, schema definitions, category domains, and reproducibility behavior for the Poll Results Visualizer project.

## 2. Dataset Metadata
- **Dataset File**: `data/raw/sample_poll_data.csv`
- **Type**: 100% Synthetic / Mock Survey Responses
- **Generator**: `generate_data.py`
- **Total Records**: 500 rows
- **Total Columns**: 9 columns
- **Random Seed**: `42` (fully reproducible)
- **PII Status**: Zero personally identifiable information

## 3. Schema Definition
| Column Name | Data Type | Permitted Values / Range | Null Count | Description |
| :--- | :--- | :--- | :--- | :--- |
| `response_id` | String | `RESP_0001` - `RESP_0500` | 0 | Unique non-null respondent identifier. |
| `department` | String | `IT`, `Commerce`, `Science`, `Arts` | 0 | Fictional student academic department. |
| `study_year` | Integer | `1`, `2`, `3`, `4` | 0 | Student's current study year. |
| `preferred_language` | String | `Python`, `Java`, `C++`, `JavaScript` | 0 | Preferred primary programming language. |
| `training_satisfaction` | Integer | `1` to `5` | 0 | Likert rating (1=Lowest, 5=Highest). |
| `preferred_learning_method` | String | `Hands-on Projects`, `Video Tutorials`, `Classroom Lectures`, `Online Courses` | 0 | Preferred learning modality. |
| `internship_interest` | String | `Yes`, `No` | 0 | Interest in industry internships. |
| `recommendation_score` | Integer | `0` to `10` | 0 | Likelihood to recommend rating (0 to 10). |
| `comments` | String / NaN | Text or NaN | 235 (47.0%) | Optional qualitative survey feedback. |

## 4. Regeneration Command
```bash
.\.venv\Scripts\python.exe generate_data.py --samples 500 --seed 42 --output data/raw/sample_poll_data.csv
```
