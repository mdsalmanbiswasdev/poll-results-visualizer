"""Main entry point for Poll Results Visualizer.

This script serves as the command-line entry point for the project.
It runs the complete pipeline (load → clean → analyse → insights)
and prints a quick summary report to stdout.

To launch the interactive Streamlit dashboard, run:
    streamlit run app.py
"""

from __future__ import annotations

import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.analysis import get_dataset_overview, get_numeric_summary
from src.data_cleaning import clean_poll_data, process_and_save_poll_data
from src.data_loader import load_poll_data
from src.insights import generate_all_insights


RAW_PATH = PROJECT_ROOT / "data" / "raw" / "sample_poll_data.csv"
CLEAN_PATH = PROJECT_ROOT / "data" / "processed" / "clean_poll_data.csv"


def main() -> None:
    print("=" * 65)
    print("  Poll Results Visualizer — Pipeline Summary")
    print("=" * 65)

    # 1. Load raw data
    if not RAW_PATH.exists():
        print(
            f"[ERROR] Raw dataset not found at: {RAW_PATH}\n"
            "        Run `python generate_data.py` first to generate the dataset."
        )
        sys.exit(1)

    raw_df = load_poll_data(str(RAW_PATH))
    print(f"[OK] Raw data loaded   : {len(raw_df)} rows, {len(raw_df.columns)} columns")

    # 2. Clean and save
    process_and_save_poll_data(str(RAW_PATH), str(CLEAN_PATH))
    clean_df = load_poll_data(str(CLEAN_PATH))
    print(f"[OK] Cleaned data saved: {len(clean_df)} rows, {len(clean_df.columns)} columns")

    # 3. Dataset overview
    overview = get_dataset_overview(clean_df)
    print(f"\n{'=' * 65}")
    print("  Dataset Overview")
    print(f"{'=' * 65}")
    print(f"  Rows    : {overview['row_count']}")
    print(f"  Columns : {overview['column_count']}")
    for col, dtype in overview["dtypes"].items():
        print(f"    {col:<30} {dtype}")

    # 4. Numeric summary
    numeric_df = get_numeric_summary(clean_df)
    print(f"\n{'=' * 65}")
    print("  Numeric Column Statistics")
    print(f"{'=' * 65}")
    print(
        f"  {'Column':<28} {'Mean':>6} {'Median':>8} {'Std':>6} {'Min':>5} {'Max':>5}"
    )
    for _, row in numeric_df.iterrows():
        print(
            f"  {row['column']:<28} {row['mean']:>6.2f} {row['median']:>8.2f} "
            f"{row['std']:>6.2f} {row['min']:>5.1f} {row['max']:>5.1f}"
        )

    # 5. Insights
    print(f"\n{'=' * 65}")
    print("  Automated Survey Insights")
    print(f"{'=' * 65}")
    insights = generate_all_insights(clean_df)
    for ins in insights:
        print(f"  [{ins['id']}]")
        print(f"    {ins['summary_text']}")

    print(f"\n{'=' * 65}")
    print("  To launch the interactive dashboard, run:")
    print("    streamlit run app.py")
    print("=" * 65)


if __name__ == "__main__":
    main()
