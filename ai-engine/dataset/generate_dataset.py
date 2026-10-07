"""
CIBUS-AI - Realistic Food Surplus Synthetic Dataset Generator
File: ai-engine/dataset/generate_dataset.py

Purpose:
Generates exactly 8,000 realistic records for food surplus prediction.
Adheres strictly to the data-leakage prevention rule by omitting Meals_Sold.
Models food surplus from a realistic operational food-service demand simulation:

Fundamental Relationship:
Customers_Forecast
        ↓
Expected Demand / Consumption
        ↓
Meals Prepared
        ↓
Potential Surplus
        ↓
Surplus_Meals

Key Principles:
1. Operational context: Day, Weather, Event_Type, Festival, Special_Event, Staff_Count, Avg_Rating.
2. Demand simulation: Realized diner demand modulated by weather disruptions, event per-capita dynamics,
   festival surges, day-of-week patterns, and establishment reputation.
3. Supply distribution: Meals_Prepared across diverse operational regimes:
   - Standard planned buffer (10% to 35% above forecast)
   - Tight / balanced production (-5% to +8% buffer)
   - High buffer / lavish service (35% to 75% buffer for buffets & banquets)
   - Demand surge / under-preparation (Meals < Demand, supply exhausted -> surplus = 0)
   - Large over-preparation / partial cancellation (Meals = 1.75x to 3.50x forecast)
   - Decoupled operational states (severe stockout or large contract with low turnout)
4. Physical Domain Laws:
   - Consumed meals cannot exceed Meals_Prepared (physical supply ceiling).
   - Surplus_Meals = max(0, Meals_Prepared - realized_demand)
   - Every single record satisfies: 0 <= Surplus_Meals <= Meals_Prepared.
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
    weather_probs = [0.46, 0.28, 0.18, 0.08]
    weather_col = rng.choice(weather_types, size=num_samples, p=weather_probs)

    # 3. Event Type
    event_types = ["Regular", "Buffet", "Corporate", "Banquet"]
    event_probs = [0.45, 0.27, 0.16, 0.12]
    event_col = rng.choice(event_types, size=num_samples, p=event_probs)

    # 4. Festival Indicator / Occasions
    festivals = ["No", "Diwali", "Eid", "Christmas", "New Year"]
    festival_probs = [0.78, 0.07, 0.05, 0.05, 0.05]
    festival_col = rng.choice(festivals, size=num_samples, p=festival_probs)

    # 5. Special Event (Binary 0 or 1)
    special_event_col = rng.choice([0, 1], size=num_samples, p=[0.82, 0.18])

    # 6. Customers Forecast: wide realistic operational footfall range (20 to 950)
    # Mixture of dining scales across the food-service industry:
    # - Small bistro / boutique event: 20 to 150 guests
    # - Medium restaurant / dining hall: 150 to 500 guests
    # - Large banquet / conference / convention: 500 to 950 guests
    scales = rng.choice(["small", "medium", "large"], size=num_samples, p=[0.25, 0.45, 0.30])
    customers_forecast_col = np.zeros(num_samples, dtype=int)

    s_idx = (scales == "small")
    customers_forecast_col[s_idx] = rng.integers(20, 151, size=s_idx.sum())

    m_idx = (scales == "medium")
    customers_forecast_col[m_idx] = rng.integers(151, 501, size=m_idx.sum())

    l_idx = (scales == "large")
    customers_forecast_col[l_idx] = rng.integers(501, 951, size=l_idx.sum())

    # 7. Operational Planning Regimes for Meals_Prepared:
    # Food-service kitchens plan batch production based on diverse operational conditions:
    # - standard_buffer   (~30%): Normal kitchen buffer (+10% to +35%)
    # - tight_balanced    (~18%): Conservative / just-in-time preparation (-5% to +8%)
    # - high_buffer       (~18%): Lavish buffet / banquet buffer (+35% to +75%)
    # - underprep_surge   (~14%): Supply constraint / walk-in rush (Meals = 0.25x to 0.90x forecast)
    # - large_overprep    (~12%): Cancellation / high minimum contract (+75% to +250%)
    # - decoupled_extreme (~8%):
    #     * Severe shortage: limited meals (20-80) despite moderate/high forecast (200-800) -> surplus = 0
    #     * Massive over-catering: large batch (600-1350) with low attendance (30-150) -> huge surplus
    regimes = rng.choice(
        ["standard_buffer", "tight_balanced", "high_buffer", "underprep_surge", "large_overprep", "decoupled_extreme"],
        size=num_samples,
        p=[0.30, 0.18, 0.18, 0.14, 0.12, 0.08]
    )

    meals_prepared_col = np.zeros(num_samples, dtype=int)

    # Standard buffer
    mask = (regimes == "standard_buffer")
    meals_prepared_col[mask] = np.round(
        customers_forecast_col[mask] * rng.uniform(1.10, 1.35, size=mask.sum())
        + rng.integers(5, 20, size=mask.sum())
    )

    # Tight balanced
    mask = (regimes == "tight_balanced")
    meals_prepared_col[mask] = np.round(
        customers_forecast_col[mask] * rng.uniform(0.95, 1.08, size=mask.sum())
        + rng.integers(-4, 6, size=mask.sum())
    )

    # High buffer
    mask = (regimes == "high_buffer")
    meals_prepared_col[mask] = np.round(
        customers_forecast_col[mask] * rng.uniform(1.35, 1.75, size=mask.sum())
        + rng.integers(15, 35, size=mask.sum())
    )

    # Underprep surge
    mask = (regimes == "underprep_surge")
    meals_prepared_col[mask] = np.round(
        customers_forecast_col[mask] * rng.uniform(0.25, 0.90, size=mask.sum())
        + rng.integers(-5, 5, size=mask.sum())
    )

    # Large overprep
    mask = (regimes == "large_overprep")
    meals_prepared_col[mask] = np.round(
        customers_forecast_col[mask] * rng.uniform(1.75, 3.50, size=mask.sum())
        + rng.integers(25, 60, size=mask.sum())
    )

    # Decoupled extreme (ensures generalization across the full (C, M) grid)
    mask = (regimes == "decoupled_extreme")
    half = mask.sum() // 2
    idx_arr = np.where(mask)[0]
    # Extreme supply deficit / small kitchen with large crowd:
    meals_prepared_col[idx_arr[:half]] = rng.integers(20, 81, size=half)
    # Extreme over-catering / large banquet with low attendance:
    meals_prepared_col[idx_arr[half:]] = rng.integers(600, 1351, size=len(idx_arr) - half)

    # Physical kitchen batch production bounds
    meals_prepared_col = np.clip(meals_prepared_col, 20, 1400)

    # 8. Staff Count: kitchen and front-of-house staff scales with production and volume
    base_staff = 3 + (meals_prepared_col // 28) + rng.integers(-2, 3, size=num_samples)
    staff_count_col = np.clip(base_staff, 4, 52).astype(int)

    # 9. Average Rating (2.00 to 5.00)
    raw_ratings = rng.normal(loc=4.12, scale=0.42, size=num_samples)
    avg_rating_col = np.round(np.clip(raw_ratings, 2.0, 5.0), 2)

    # 10. Multi-feature Demand Simulation:
    # Realized customer demand is a multi-factor operational function:
    # expected_consumption = f(Customers_Forecast, Weather, Event_Type, Festival, Special_Event, Day, Avg_Rating, noise)

    # Weather impact: Severe storms / rains reduce walk-in customers and outdoor attendance
    weather_mult = np.where(weather_col == "Stormy", rng.uniform(0.68, 0.78, size=num_samples),
                   np.where(weather_col == "Rainy",  rng.uniform(0.82, 0.92, size=num_samples),
                   np.where(weather_col == "Cloudy", rng.uniform(0.95, 0.99, size=num_samples),
                                                     rng.uniform(1.00, 1.04, size=num_samples))))

    # Event Type per-capita dining behavior:
    # Buffets have higher per-capita intake; Banquets formal set courses; Corporate lighter/frugal
    event_mult = np.where(event_col == "Buffet",    rng.uniform(1.10, 1.18, size=num_samples),
                 np.where(event_col == "Banquet",   rng.uniform(1.04, 1.10, size=num_samples),
                 np.where(event_col == "Corporate", rng.uniform(0.88, 0.95, size=num_samples),
                                                    1.00)))

    # Festival impact: Celebration surge increases attendance and group sizes
    fest_mult = np.where(festival_col != "No", rng.uniform(1.06, 1.15, size=num_samples), 1.00)

    # Special Event impact: Live entertainment / chef specials attract additional diners
    special_mult = np.where(special_event_col == 1, rng.uniform(1.04, 1.10, size=num_samples), 1.00)

    # Day of week impact: Weekends have higher leisurely dining turnout; Mondays are slower
    weekend_mask = np.isin(day_col, ["Friday", "Saturday", "Sunday"])
    monday_mask = (day_col == "Monday")
    day_mult = np.where(weekend_mask, rng.uniform(1.03, 1.09, size=num_samples),
               np.where(monday_mask,  rng.uniform(0.92, 0.97, size=num_samples),
                                      rng.uniform(0.98, 1.02, size=num_samples)))

    # Rating reputation impact: High rating boosts turnout; lower rating dampens conversion
    rating_mult = 1.0 + (avg_rating_col - 4.0) * 0.05
    rating_mult = np.clip(rating_mult, 0.88, 1.10)

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
        + noise
    )
    realized_demand = np.maximum(0.0, realized_demand)

    # 11. Physical Target Calculation (Surplus_Meals):
    # Physical law: Meals actually consumed cannot exceed meals prepared (supply ceiling)
    # consumed = min(meals_prepared, realized_demand)
    # unconsumed = meals_prepared - consumed = max(0, meals_prepared - realized_demand)
    raw_surplus = meals_prepared_col.astype(float) - realized_demand

    # Presentation / buffer display residue for Buffet and Banquet when surplus > 0
    display_residue = np.where(
        (np.isin(event_col, ["Buffet", "Banquet"])) & (raw_surplus > 0),
        meals_prepared_col * rng.uniform(0.01, 0.03, size=num_samples),
        0.0
    )

    # Physical domain constraints:
    # 1. When realized demand >= meals prepared, surplus is 0.0 (all prepared food is consumed)
    # 2. When realized demand < meals prepared, surplus is unconsumed meals + display residue
    surplus_meals = np.where(realized_demand >= meals_prepared_col, 0.0, raw_surplus + display_residue)

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
