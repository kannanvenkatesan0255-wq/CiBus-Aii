"""
CIBUS-AI - Dataset Validation & Diagnostic Suite
File: ai-engine/dataset/validate_dataset.py

Purpose:
Verifies data integrity, schema conformance, missing values, duplicates,
absence of data leakage (Meals_Sold), and prints statistical summaries.
"""

import os
import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(CURRENT_DIR, "food_surplus.csv")

def validate_dataset():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found at: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)
    print("=" * 60)
    print("          CIBUS-AI DATASET VALIDATION REPORT")
    print("=" * 60)

    # 1. Shape check
    print(f"\n[1] Dataset Shape: {df.shape}")
    assert len(df) == 8000, f"Expected 8000 rows, found {len(df)}"
    assert df.shape[1] == 10, f"Expected 10 columns, found {df.shape[1]}"
    print("    [PASS] Exactly 8,000 rows and 10 columns.")

    # 2. Expected columns & Leakage check
    expected_cols = [
        "Day", "Weather", "Customers_Forecast", "Meals_Prepared",
        "Festival", "Event_Type", "Staff_Count", "Avg_Rating",
        "Special_Event", "Surplus_Meals"
    ]
    assert list(df.columns) == expected_cols, f"Column mismatch: {list(df.columns)}"
    assert "Meals_Sold" not in df.columns, "CRITICAL ERROR: Meals_Sold found in dataset columns!"
    print(f"\n[2] Columns: {list(df.columns)}")
    print("    [PASS] All 10 expected columns present.")
    print("    [PASS] Meals_Sold is STRICTLY ABSENT (Zero Data Leakage).")

    # 3. Missing values & Duplicates
    null_count = int(df.isnull().sum().sum())
    dup_count = int(df.duplicated().sum())
    print(f"\n[3] Missing Values: {null_count}")
    print(f"[4] Duplicate Rows: {dup_count}")
    assert null_count == 0, f"Found {null_count} missing values!"
    assert dup_count == 0, f"Found {dup_count} duplicate rows!"
    print("    [PASS] 0 missing values and 0 duplicate rows.")

    # 4. Target validity & Range checks
    min_surplus = df["Surplus_Meals"].min()
    max_surplus = df["Surplus_Meals"].max()
    mean_surplus = df["Surplus_Meals"].mean()
    std_surplus = df["Surplus_Meals"].std()
    assert min_surplus >= 0.0, f"Found negative surplus: {min_surplus}"
    assert (df["Surplus_Meals"] > df["Meals_Prepared"]).sum() == 0, "Surplus cannot exceed meals prepared!"
    print(f"\n[5] Target Variable (Surplus_Meals) Diagnostics:")
    print(f"    - Min: {min_surplus}")
    print(f"    - Max: {max_surplus}")
    print(f"    - Mean: {mean_surplus:.2f}")
    print(f"    - Std Dev: {std_surplus:.2f}")
    print("    [PASS] Surplus_Meals values are strictly valid, non-negative, and physically bounded.")

    # 5. Numerical Summary Statistics
    print("\n" + "=" * 60)
    print("          NUMERICAL FEATURES SUMMARY STATISTICS")
    print("=" * 60)
    print(df.describe().round(2).to_string())

    # 6. Categorical Feature Distributions
    print("\n" + "=" * 60)
    print("       CATEGORICAL & DISCRETE FEATURE DISTRIBUTIONS")
    print("=" * 60)
    for col in ["Day", "Weather", "Festival", "Event_Type", "Special_Event"]:
        print(f"\n--- Column: {col} ---")
        print(df[col].value_counts().to_string())

    print("\n" + "=" * 60)
    print("      ALL DATASET VALIDATION CHECKS PASSED SUCCESSFULLY")
    print("=" * 60)

if __name__ == "__main__":
    validate_dataset()
