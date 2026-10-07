"""
CIBUS-AI - Realistic Multi-Parameter Food Surplus Synthetic Dataset Generator
File: ai-engine/dataset/generate_dataset.py

Purpose:
Generates exactly 8,000 realistic records for food surplus prediction.
Adheres strictly to the data-leakage prevention rule by omitting Meals_Sold.
Models food surplus from a realistic operational food-service demand simulation:

Fundamental Relationship:
Customers_Forecast (baseline expectation)
        ↓
Operational & Contextual Factors (Weather, Festival, Event_Type, Special_Event, Day, Avg_Rating, Staff_Count)
        ↓
Realized Diner Demand / Service Throughput
        ↓
Meals Prepared (Production batch capacity across operational regimes)
        ↓
Surplus Meals (Unconsumed portions)

Key Principles:
1. Every operational parameter contributes meaningful domain information:
   - Customers_Forecast & Meals_Prepared: primary demand-supply determinants.
   - Weather: disruptions (storms/rain) dampen customer footfall and increase surplus.
   - Event_Type: buffet & banquet increase consumption/courses; corporate reduces portions.
   - Festival & Special_Event: festive occasions and themed events draw attendance surges.
   - Day: weekend dining peaks increase consumption; Mondays slow down.
   - Avg_Rating: reputation drives reservation conversion and walk-in footfall.
   - Staff_Count: service staffing ratio affects service throughput and table turnover.
2. Zero data leakage: Meals_Sold is strictly absent.
3. Physical Domain Laws:
   - 0 <= Surplus_Meals <= Meals_Prepared for every single row.
   - When realized demand >= Meals_Prepared, Surplus_Meals is strictly 0.0.
"""

import os
import numpy as np
import pandas as pd

# Define paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(CURRENT_DIR, "food_surplus.csv")


def generate_food_surplus_data(num_samples: int = 8000, random_seed: int = 42) -> pd.DataFrame:
    """
    Generates exactly `num_samples` realistic synthetic food surplus records respecting physical domain laws.

    Parameters:
        num_samples (int): Total number of records (exactly 8000).
        random_seed (int): Seed for deterministic reproducibility.

    Returns:
        pd.DataFrame: Clean DataFrame containing 10 columns without data leakage.
    """
    rng = np.random.default_rng(random_seed)

    # 1. Day of the Week
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_col = rng.choice(days, size=num_samples, p=[0.14, 0.14, 0.14, 0.15, 0.15, 0.14, 0.14])

    # 2. Weather Conditions
    weather_types = ["Sunny", "Cloudy", "Rainy", "Stormy"]
    weather_probs = [0.45, 0.28, 0.19, 0.08]
    weather_col = rng.choice(weather_types, size=num_samples, p=weather_probs)

    # 3. Event Type
    event_types = ["Regular", "Buffet", "Corporate", "Banquet"]
    event_probs = [0.45, 0.26, 0.17, 0.12]
    event_col = rng.choice(event_types, size=num_samples, p=event_probs)

    # 4. Festival Indicator / Occasions
    festivals = ["No", "Diwali", "Eid", "Christmas", "New Year"]
    festival_probs = [0.78, 0.07, 0.05, 0.05, 0.05]
    festival_col = rng.choice(festivals, size=num_samples, p=festival_probs)

    # 5. Special Event (Binary 0 or 1)
    special_event_col = rng.choice([0, 1], size=num_samples, p=[0.80, 0.20])

    # 6. Customers Forecast: wide realistic operational footfall range (20 to 950)
    scales = rng.choice(["small", "medium", "large"], size=num_samples, p=[0.25, 0.45, 0.30])
    customers_forecast_col = np.zeros(num_samples, dtype=int)

    s_idx = (scales == "small")
    customers_forecast_col[s_idx] = rng.integers(20, 151, size=s_idx.sum())

    m_idx = (scales == "medium")
    customers_forecast_col[m_idx] = rng.integers(151, 501, size=m_idx.sum())

    l_idx = (scales == "large")
    customers_forecast_col[l_idx] = rng.integers(501, 951, size=l_idx.sum())

    # 7. Operational Planning Regimes for Meals_Prepared:
    regimes = rng.choice(
        ["standard_buffer", "tight_balanced", "high_buffer", "underprep_surge", "large_overprep", "decoupled_extreme"],
        size=num_samples,
        p=[0.28, 0.18, 0.18, 0.14, 0.12, 0.10]
    )

    meals_prepared_col = np.zeros(num_samples, dtype=int)

    # Standard buffer (+10% to +35%)
    mask = (regimes == "standard_buffer")
    meals_prepared_col[mask] = np.round(
        customers_forecast_col[mask] * rng.uniform(1.10, 1.35, size=mask.sum())
        + rng.integers(5, 20, size=mask.sum())
    )

    # Tight balanced (-5% to +8%)
    mask = (regimes == "tight_balanced")
    meals_prepared_col[mask] = np.round(
        customers_forecast_col[mask] * rng.uniform(0.95, 1.08, size=mask.sum())
        + rng.integers(-4, 6, size=mask.sum())
    )

    # High buffer (+35% to +75%)
    mask = (regimes == "high_buffer")
    meals_prepared_col[mask] = np.round(
        customers_forecast_col[mask] * rng.uniform(1.35, 1.75, size=mask.sum())
        + rng.integers(15, 35, size=mask.sum())
    )

    # Underprep surge (Meals < Demand, supply exhausted -> surplus = 0)
    mask = (regimes == "underprep_surge")
    meals_prepared_col[mask] = np.round(
        customers_forecast_col[mask] * rng.uniform(0.25, 0.90, size=mask.sum())
        + rng.integers(-5, 5, size=mask.sum())
    )

    # Large overprep (+75% to +250%)
    mask = (regimes == "large_overprep")
    meals_prepared_col[mask] = np.round(
        customers_forecast_col[mask] * rng.uniform(1.75, 3.50, size=mask.sum())
        + rng.integers(25, 60, size=mask.sum())
    )

    # Decoupled extreme (ensures generalization across extreme corners)
    mask = (regimes == "decoupled_extreme")
    half = mask.sum() // 2
    idx_arr = np.where(mask)[0]
    # Extreme supply deficit: limited meals (20-80) with moderate/high crowd (200-800) -> surplus = 0
    meals_prepared_col[idx_arr[:half]] = rng.integers(20, 81, size=half)
    customers_forecast_col[idx_arr[:half]] = rng.integers(200, 801, size=half)
    # Extreme over-catering: large batch (700-1350) with lower attendance (50-350) -> huge surplus
    meals_prepared_col[idx_arr[half:]] = rng.integers(700, 1351, size=len(idx_arr) - half)
    customers_forecast_col[idx_arr[half:]] = rng.integers(50, 351, size=len(idx_arr) - half)

    # Physical kitchen batch production bounds
    meals_prepared_col = np.clip(meals_prepared_col, 20, 1400)

    # 8. Staff Count: Scheduled staff on duty (4 to 52)
    # Realistic operational scheduling: Planned staff roster is set by management based on
    # anticipated volume, service tier (buffet/banquet need more crew), with natural scheduling variation:
    optimal_staff_base = 4 + (customers_forecast_col // 28) + np.where(event_col == "Buffet", 3, np.where(event_col == "Banquet", 4, 0))
    staff_variation = rng.integers(-4, 5, size=num_samples)
    staff_count_col = np.clip(optimal_staff_base + staff_variation, 4, 52).astype(int)

    # 9. Average Rating (2.00 to 5.00)
    raw_ratings = rng.normal(loc=4.10, scale=0.45, size=num_samples)
    avg_rating_col = np.round(np.clip(raw_ratings, 2.0, 5.0), 2)

    # 10. Multi-feature Demand Simulation:
    # (a) Weather: Severe storms / rains reduce walk-in customers and outdoor attendance
    weather_mult = np.where(weather_col == "Stormy", rng.uniform(0.68, 0.76, size=num_samples),
                   np.where(weather_col == "Rainy",  rng.uniform(0.82, 0.90, size=num_samples),
                   np.where(weather_col == "Cloudy", rng.uniform(0.95, 0.98, size=num_samples),
                                                     rng.uniform(1.02, 1.06, size=num_samples))))

    # (b) Event Type per-capita dining behavior:
    # Buffets have higher per-capita intake; Banquets formal set courses; Corporate lighter/frugal
    event_mult = np.where(event_col == "Buffet",    rng.uniform(1.14, 1.22, size=num_samples),
                 np.where(event_col == "Banquet",   rng.uniform(1.06, 1.12, size=num_samples),
                 np.where(event_col == "Corporate", rng.uniform(0.84, 0.92, size=num_samples),
                                                    1.00)))

    # (c) Festival impact: Celebration surge increases attendance and group sizes
    fest_mult = np.where(festival_col != "No", rng.uniform(1.10, 1.20, size=num_samples), 1.00)

    # (d) Special Event impact: Themed events / VIP bookings bring higher turnout
    special_mult = np.where(special_event_col == 1, rng.uniform(1.18, 1.30, size=num_samples), 1.00)

    # (e) Day of week impact: Weekends have higher leisurely dining turnout; Mondays are slower
    weekend_mask = np.isin(day_col, ["Friday", "Saturday", "Sunday"])
    monday_mask = (day_col == "Monday")
    day_mult = np.where(weekend_mask, rng.uniform(1.06, 1.14, size=num_samples),
               np.where(monday_mask,  rng.uniform(0.88, 0.94, size=num_samples),
                                      rng.uniform(0.98, 1.02, size=num_samples)))

    # (f) Rating reputation impact: High rating boosts turnout; lower rating dampens conversion
    rating_mult = 1.0 + (avg_rating_col - 4.0) * 0.10
    rating_mult = np.clip(rating_mult, 0.82, 1.15)

    # (g) Staff Count: Service throughput and operational friction
    # Adequate staffing allows full table turns and uninterrupted service flow.
    # Understaffed service leads to bottlenecks, walkouts, or dining delays:
    staff_ratio = staff_count_col / np.maximum(1.0, optimal_staff_base.astype(float))
    staff_mult = np.where(
        staff_ratio < 0.85,
        1.0 - np.clip((0.85 - staff_ratio) * 0.20, 0.0, 0.14),
        1.0 + np.clip((staff_ratio - 1.0) * 0.06, 0.0, 0.05)
    )

    # Controlled stochastic operational noise (proportional to event size)
    noise = rng.normal(0.0, 0.02 * customers_forecast_col + 2.0, size=num_samples)

    # Total realized demand (actual meals diners attempt to consume)
    realized_demand = (
        customers_forecast_col.astype(float)
        * weather_mult
        * event_mult
        * fest_mult
        * special_mult
        * day_mult
        * rating_mult
        * staff_mult
        + noise
    )
    realized_demand = np.maximum(0.0, realized_demand)

    # 11. Physical Target Calculation (Surplus_Meals):
    raw_surplus = meals_prepared_col.astype(float) - realized_demand

    # Physical domain constraints:
    # 1. When realized demand >= meals prepared, surplus is strictly 0.0
    surplus_meals = np.where(realized_demand >= meals_prepared_col, 0.0, raw_surplus)

    # 2. When customers forecast is clearly greater than available meals, surplus is 0.0
    surplus_meals = np.where(customers_forecast_col >= 1.5 * meals_prepared_col, 0.0, surplus_meals)

    # 3. Strictly enforce physical bounds: 0.0 <= Surplus_Meals <= Meals_Prepared
    surplus_meals = np.clip(surplus_meals, 0.0, meals_prepared_col.astype(float))
    surplus_meals_col = np.round(surplus_meals, 1)

    # Assemble into DataFrame
    df = pd.DataFrame({
        "Day": day_col,
        "Weather": weather_col,
        "Customers_Forecast": customers_forecast_col,
        "Meals_Prepared": meals_prepared_col,
        "Festival": festival_col,
        "Event_Type": event_col,
        "Staff_Count": staff_count_col,
        "Avg_Rating": avg_rating_col,
        "Special_Event": special_event_col,
        "Surplus_Meals": surplus_meals_col
    })

    # Ensure exactly num_samples unique rows
    while df.duplicated().sum() > 0:
        dup_count = df.duplicated().sum()
        df = df.drop_duplicates()
        extra_df = generate_food_surplus_data(num_samples=dup_count + 50, random_seed=random_seed + len(df))
        df = pd.concat([df, extra_df], ignore_index=True).iloc[:num_samples]

    return df


def save_and_validate_dataset():
    """Generates and writes food_surplus.csv to disk."""
    print(f"[CIBUS-AI] Generating exactly 8,000 synthetic records with seed=42...")
    df = generate_food_surplus_data(num_samples=8000, random_seed=42)

    os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)
    df.to_csv(DATASET_PATH, index=False)
    print(f"[CIBUS-AI] Dataset successfully saved to: {DATASET_PATH}")
    print(f"[CIBUS-AI] Verification:")
    print(f"  - Total Rows: {len(df)}")
    print(f"  - Zero Surplus: {(df['Surplus_Meals'] == 0.0).sum()} ({(df['Surplus_Meals'] == 0.0).mean() * 100:.2f}%)")
    print(f"  - Positive Surplus: {(df['Surplus_Meals'] > 0.0).sum()} ({(df['Surplus_Meals'] > 0.0).mean() * 100:.2f}%)")
    print(f"  - Violations (Surplus < 0): {(df['Surplus_Meals'] < 0.0).sum()}")
    print(f"  - Violations (Surplus > Meals_Prepared): {(df['Surplus_Meals'] > df['Meals_Prepared']).sum()}")
    return df


if __name__ == "__main__":
    save_and_validate_dataset()
