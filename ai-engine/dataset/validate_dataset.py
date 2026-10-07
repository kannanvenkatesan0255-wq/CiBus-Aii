"""
CIBUS-AI - Dataset Validation & Diagnostic Suite
File: ai-engine/dataset/validate_dataset.py

Purpose:
Performs rigorous data integrity verification, schema conformance, leakage checks,
statistical diagnostics, and generalization tests on the 8,000-row food surplus dataset:
1. Shape and schema check (exactly 8,000 rows, 10 columns, no Meals_Sold).
2. Missing values and duplicates audit.
3. Physical validity rules (Surplus_Meals >= 0, Surplus_Meals <= Meals_Prepared for EVERY row).
4. Categorical and numerical distribution ranges.
5. Statistical summaries: min, max, mean, median, zero-surplus %, positive-surplus %.
6. Correlation analysis across important operational variables.
7. Grid generalization analysis across diverse operational regimes.
"""

import os
import numpy as np
import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(CURRENT_DIR, "food_surplus.csv")

def validate_dataset():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found at: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)
    print("=" * 70)
    print("          CIBUS-AI DATASET QUALITY & VALIDATION REPORT")
    print("=" * 70)

    # 1. Shape Check
    print(f"\n[1] DATASET SHAPE & RECORD COUNT:")
    print(f"    - Dimensions: {df.shape[0]} rows x {df.shape[1]} columns")
    assert len(df) == 8000, f"Expected exactly 8,000 rows, found {len(df)}"
    assert df.shape[1] == 10, f"Expected 10 columns, found {df.shape[1]}"
    print("    [PASS] Exactly 8,000 rows and 10 columns.")

    # 2. Schema & Data Leakage Check
    expected_cols = [
        "Day", "Weather", "Customers_Forecast", "Meals_Prepared",
        "Festival", "Event_Type", "Staff_Count", "Avg_Rating",
        "Special_Event", "Surplus_Meals"
    ]
    assert list(df.columns) == expected_cols, f"Column mismatch: {list(df.columns)}"
    assert "Meals_Sold" not in df.columns, "CRITICAL ERROR: Meals_Sold found in dataset columns!"
    print(f"\n[2] COLUMN SCHEMA & DATA LEAKAGE AUDIT:")
    print(f"    - Columns: {list(df.columns)}")
    print("    [PASS] All 10 expected columns present in valid order.")
    print("    [PASS] Meals_Sold is STRICTLY ABSENT (Zero Data Leakage).")

    # 3. Missing Values & Duplicate Records Check
    null_count = int(df.isnull().sum().sum())
    dup_count = int(df.duplicated().sum())
    print(f"\n[3] COMPLETENESS & UNIQUENESS AUDIT:")
    print(f"    - Missing values (NaN / null): {null_count}")
    print(f"    - Duplicate rows:             {dup_count}")
    assert null_count == 0, f"Found {null_count} missing values!"
    assert dup_count == 0, f"Found {dup_count} duplicate rows!"
    print("    [PASS] 0 missing values and 0 duplicate rows.")

    # 4. Physical Validity Invariants
    neg_customers = (df["Customers_Forecast"] < 0).sum()
    neg_meals = (df["Meals_Prepared"] < 0).sum()
    neg_surplus = (df["Surplus_Meals"] < 0.0).sum()
    exceed_surplus = (df["Surplus_Meals"] > df["Meals_Prepared"]).sum()

    print(f"\n[4] PHYSICAL DOMAIN INVARIANTS AUDIT:")
    print(f"    - Negative Customers_Forecast: {neg_customers}")
    print(f"    - Negative Meals_Prepared:     {neg_meals}")
    print(f"    - Negative Surplus_Meals:      {neg_surplus}")
    print(f"    - Surplus > Meals_Prepared:    {exceed_surplus}")

    assert neg_customers == 0, f"Found {neg_customers} records with negative Customers_Forecast!"
    assert neg_meals == 0, f"Found {neg_meals} records with negative Meals_Prepared!"
    assert neg_surplus == 0, f"Found {neg_surplus} records with negative Surplus_Meals!"
    assert exceed_surplus == 0, f"Found {exceed_surplus} records where Surplus_Meals > Meals_Prepared!"
    print("    [PASS] Every single row satisfies: 0 <= Surplus_Meals <= Meals_Prepared.")

    # 5. Target Variable Distribution & Descriptive Metrics
    surplus_series = df["Surplus_Meals"]
    min_surplus = float(surplus_series.min())
    max_surplus = float(surplus_series.max())
    mean_surplus = float(surplus_series.mean())
    median_surplus = float(surplus_series.median())
    std_surplus = float(surplus_series.std())

    zero_count = int((surplus_series == 0.0).sum())
    zero_pct = float(zero_count / len(df) * 100.0)
    pos_count = int((surplus_series > 0.0).sum())
    pos_pct = float(pos_count / len(df) * 100.0)

    print(f"\n[5] TARGET VARIABLE (Surplus_Meals) METRICS:")
    print(f"    - Minimum Surplus:          {min_surplus:.1f} meals")
    print(f"    - Maximum Surplus:          {max_surplus:.1f} meals")
    print(f"    - Mean Surplus:             {mean_surplus:.2f} meals")
    print(f"    - Median Surplus:           {median_surplus:.2f} meals")
    print(f"    - Standard Deviation:       {std_surplus:.2f} meals")
    print(f"    - Zero-Surplus Records:     {zero_count} ({zero_pct:.2f}%)")
    print(f"    - Positive-Surplus Records: {pos_count} ({pos_pct:.2f}%)")

    # 6. Categorical Value Conformance
    print(f"\n[6] CATEGORICAL FEATURE CONFORMANCE:")
    valid_days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
    valid_weather = {"Sunny", "Cloudy", "Rainy", "Stormy"}
    valid_festivals = {"No", "Diwali", "Eid", "Christmas", "New Year"}
    valid_events = {"Regular", "Buffet", "Corporate", "Banquet"}

    assert set(df["Day"].unique()).issubset(valid_days), f"Unexpected days: {df['Day'].unique()}"
    assert set(df["Weather"].unique()).issubset(valid_weather), f"Unexpected weather: {df['Weather'].unique()}"
    assert set(df["Festival"].unique()).issubset(valid_festivals), f"Unexpected festivals: {df['Festival'].unique()}"
    assert set(df["Event_Type"].unique()).issubset(valid_events), f"Unexpected event types: {df['Event_Type'].unique()}"
    assert set(df["Special_Event"].unique()).issubset({0, 1}), f"Unexpected special events: {df['Special_Event'].unique()}"
    print("    [PASS] All categorical domains strictly valid.")

    # 7. Numerical Summary Table
    print("\n" + "=" * 70)
    print("             NUMERICAL FEATURES SUMMARY TABLE")
    print("=" * 70)
    print(df.describe().round(2).to_string())

    # 8. Correlation Analysis
    print("\n" + "=" * 70)
    print("            CORRELATION MATRIX WITH SURPLUS_MEALS")
    print("=" * 70)
    num_df = df.select_dtypes(include=[np.number])
    corr = num_df.corr()["Surplus_Meals"].sort_values(ascending=False)
    for feat, val in corr.items():
        print(f"    * {feat:<24}: {val:+.4f}")

    # 9. Generalization Grid Check on Dataset (Section 8)
    print("\n" + "=" * 70)
    print("      DATASET GENERALIZATION AUDIT ACROSS OPERATIONAL REGIMES")
    print("=" * 70)
    # Check that dataset covers:
    # 1. Low customers, low meals
    # 2. Low customers, high meals
    # 3. High customers, low meals
    # 4. High customers, high meals
    # 5. Customers ~ meals
    # 6. Customers >> meals
    # 7. Meals >> customers
    c_low = df["Customers_Forecast"] < 150
    c_high = df["Customers_Forecast"] > 500
    m_low = df["Meals_Prepared"] < 150
    m_high = df["Meals_Prepared"] > 600

    low_c_low_m = (c_low & m_low).sum()
    low_c_high_m = (c_low & m_high).sum()
    high_c_low_m = (c_high & m_low).sum()
    high_c_high_m = (c_high & m_high).sum()
    demand_surge = (df["Customers_Forecast"] >= df["Meals_Prepared"]).sum()
    supply_buffer = (df["Meals_Prepared"] > df["Customers_Forecast"]).sum()

    print(f"    * Low Customers (<150) & Low Meals (<150):   {low_c_low_m:4d} records")
    print(f"    * Low Customers (<150) & High Meals (>600):  {low_c_high_m:4d} records (Cancellations/Overprep)")
    print(f"    * High Customers (>500) & Low Meals (<150):  {high_c_low_m:4d} records (Severe Stockout/Surge)")
    print(f"    * High Customers (>500) & High Meals (>600): {high_c_high_m:4d} records")
    print(f"    * Demand Exceeds Supply (Customers >= Prep): {demand_surge:4d} records (Surplus is 0.0)")
    print(f"    * Supply Exceeds Demand (Prep > Customers):  {supply_buffer:4d} records")

    assert low_c_low_m > 50, "Insufficient low C / low M samples"
    assert low_c_high_m > 50, "Insufficient low C / high M samples"
    assert high_c_low_m > 50, "Insufficient high C / low M samples"
    assert high_c_high_m > 50, "Insufficient high C / high M samples"
    assert demand_surge > 500, "Insufficient demand surge samples"
    assert supply_buffer > 2000, "Insufficient supply buffer samples"

    # Verify that when demand is clearly greater than available meals, surplus is 0.0
    clear_surge = df[df["Customers_Forecast"] >= 1.5 * df["Meals_Prepared"]]
    clear_surge_zero_pct = float((clear_surge["Surplus_Meals"] == 0.0).mean() * 100.0)
    print(f"    * Records where Customers >= 1.5x Meals:     {len(clear_surge):4d} records")
    print(f"    * Zero-surplus rate when Customers >= 1.5x:  {clear_surge_zero_pct:.2f}% (Strictly 0.0 surplus)")
    assert clear_surge_zero_pct == 100.0, f"Expected 100% zero surplus when demand clearly exceeds meals, found {clear_surge_zero_pct}%"

    # Overall zero-surplus rate when Customers >= Meals (where realized demand >= meals)
    overall_surge_zero_pct = float((df.loc[df["Customers_Forecast"] >= df["Meals_Prepared"], "Surplus_Meals"] == 0.0).mean() * 100.0)
    print(f"    * Zero-surplus rate when Customers >= Meals: {overall_surge_zero_pct:.2f}%")
    assert overall_surge_zero_pct > 85.0, f"Expected >85% zero surplus when Customers >= Meals, found {overall_surge_zero_pct}%"

    print("\n" + "=" * 70)
    print("      ALL DATASET VALIDATION CHECKS PASSED SUCCESSFULLY")
    print("=" * 70)

if __name__ == "__main__":
    validate_dataset()
