"""
CIBUS-AI - Realistic Food Surplus Synthetic Dataset Generator
File: ai-engine/dataset/generate_dataset.py

Purpose:
Generates exactly 8,000 realistic records for food surplus prediction.
Adheres strictly to the data-leakage prevention rule by omitting Meals_Sold
and modeling surplus from operational context, environmental conditions,
non-linear feature interactions, and controlled stochastic noise.
"""

import os
import numpy as np
import pandas as pd

# Define paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(CURRENT_DIR, "food_surplus.csv")

def generate_food_surplus_data(num_samples: int = 8000, random_seed: int = 42) -> pd.DataFrame:
    """
    Generates a realistic synthetic food surplus dataset.

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
    weather_probs = [0.48, 0.27, 0.18, 0.07]
    weather_col = rng.choice(weather_types, size=num_samples, p=weather_probs)

    # 3. Event Type
    event_types = ["Regular", "Buffet", "Corporate", "Banquet"]
    event_probs = [0.46, 0.28, 0.16, 0.10]
    event_col = rng.choice(event_types, size=num_samples, p=event_probs)

    # 4. Festival Indicator / Occasions
    festivals = ["No", "Diwali", "Eid", "Christmas", "New Year"]
    festival_probs = [0.80, 0.06, 0.05, 0.05, 0.04]
    festival_col = rng.choice(festivals, size=num_samples, p=festival_probs)

    # 5. Special Event (Binary 0 or 1)
    special_event_col = rng.choice([0, 1], size=num_samples, p=[0.84, 0.16])

    # 6. Customers Forecast (Operational footfall estimation)
    # Varies based on Event Type and Day
    base_forecast = rng.integers(70, 680, size=num_samples)
    event_scale = np.where(event_col == "Banquet", 1.4,
                  np.where(event_col == "Buffet", 1.2,
                  np.where(event_col == "Corporate", 0.9, 1.0)))
    weekend_scale = np.where(np.isin(day_col, ["Friday", "Saturday", "Sunday"]), 1.15, 0.95)
    customers_forecast_col = np.round(base_forecast * event_scale * weekend_scale).astype(int)
    customers_forecast_col = np.clip(customers_forecast_col, 50, 950)

    # 7. Meals Prepared (Planned kitchen batch portions with operational buffer)
    # Buffets and Banquets maintain higher safety buffers than Regular service
    buffer_ratio = np.where(event_col == "Buffet", rng.uniform(1.15, 1.35, size=num_samples),
                   np.where(event_col == "Banquet", rng.uniform(1.18, 1.38, size=num_samples),
                   np.where(event_col == "Corporate", rng.uniform(1.06, 1.18, size=num_samples),
                            rng.uniform(1.08, 1.24, size=num_samples))))
    
    # Extra buffer if special event or festival
    festival_extra = np.where(festival_col != "No", rng.uniform(0.02, 0.08, size=num_samples), 0.0)
    total_buffer = buffer_ratio + festival_extra
    
    meals_prepared_col = np.round(customers_forecast_col * total_buffer + rng.integers(5, 25, size=num_samples)).astype(int)
    # Ensure meals prepared is strictly greater than forecast
    meals_prepared_col = np.maximum(meals_prepared_col, customers_forecast_col + rng.integers(6, 30, size=num_samples))

    # 8. Staff Count (Scales with kitchen production capacity)
    base_staff = 4 + (meals_prepared_col // 28) + rng.integers(-2, 4, size=num_samples)
    staff_count_col = np.clip(base_staff, 5, 48).astype(int)

    # 9. Average Rating (Historical satisfaction score)
    raw_ratings = rng.normal(loc=4.12, scale=0.42, size=num_samples)
    avg_rating_col = np.round(np.clip(raw_ratings, 2.30, 5.00), 2)

    # 10. Target Variable: Surplus_Meals
    # Modeled via realistic domain relationships + multi-variable non-linear interactions + controlled noise
    # (NO Meals_Sold is used)

    # Component A: Baseline buffer leftover
    buffer_diff = meals_prepared_col - customers_forecast_col
    surplus_base = buffer_diff * rng.uniform(0.55, 0.75, size=num_samples)

    # Component B: Weather disruption (Rain/Storms reduce walk-in attendance, increasing surplus)
    weather_impact = np.where(weather_col == "Stormy", customers_forecast_col * rng.uniform(0.20, 0.35, size=num_samples),
                     np.where(weather_col == "Rainy", customers_forecast_col * rng.uniform(0.08, 0.18, size=num_samples),
                     np.where(weather_col == "Cloudy", customers_forecast_col * rng.uniform(0.01, 0.04, size=num_samples),
                              0.0)))

    # Component C: Event Type structural leftover (Buffets & Banquets inherently leave larger display leftovers)
    event_impact = np.where(event_col == "Buffet", meals_prepared_col * rng.uniform(0.06, 0.12, size=num_samples),
                   np.where(event_col == "Banquet", meals_prepared_col * rng.uniform(0.07, 0.14, size=num_samples),
                   np.where(event_col == "Corporate", -meals_prepared_col * rng.uniform(0.01, 0.04, size=num_samples),
                            0.0)))

    # Component D: Festival & Special Event volatility
    fest_impact = np.where(festival_col != "No", customers_forecast_col * rng.uniform(0.03, 0.09, size=num_samples), 0.0)
    special_impact = np.where(special_event_col == 1, customers_forecast_col * rng.uniform(0.03, 0.08, size=num_samples), 0.0)

    # Component E: Rating dissatisfaction factor (Lower rating -> fewer repeat/walk-in diners)
    rating_impact = np.where(avg_rating_col < 3.8, (3.8 - avg_rating_col) * 14.0, 0.0)

    # Component F: Non-linear interaction terms
    # Interaction 1: Stormy weather during Buffet/Banquet (compounds surplus)
    stormy_buffet_interaction = np.where((weather_col == "Stormy") & (np.isin(event_col, ["Buffet", "Banquet"])),
                                         customers_forecast_col * 0.08, 0.0)
    
    # Interaction 2: Low rating during high-volume special events
    rating_special_interaction = np.where((special_event_col == 1) & (avg_rating_col < 3.5), 15.0, 0.0)

    # Component G: Controlled Stochastic Noise (representing unmodeled day-to-day human variance)
    stochastic_noise = rng.normal(loc=0.0, scale=6.5, size=num_samples)

    # Synthesize total surplus
    raw_surplus = (
        surplus_base
        + weather_impact
        + event_impact
        + fest_impact
        + special_impact
        + rating_impact
        + stormy_buffet_interaction
        + rating_special_interaction
        + stochastic_noise
    )

    # Physical domain constraints:
    # 1. Non-negative surplus
    # 2. Cannot exceed 85% of total meals prepared
    surplus_meals_col = np.round(np.clip(raw_surplus, 0.0, meals_prepared_col * 0.85), 1)

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

    # Ensure no duplicates
    while df.duplicated().sum() > 0:
        dup_count = df.duplicated().sum()
        df = df.drop_duplicates()
        # Regenerate required replacement rows
        extra_df = generate_food_surplus_data(num_samples=dup_count + 50, random_seed=random_seed + len(df))
        df = pd.concat([df, extra_df], ignore_index=True).iloc[:num_samples]

    return df

def save_and_validate_dataset():
    """Generates and writes food_surplus.csv to disk."""
    print(f"[CIBUS-AI] Generating 8,000 synthetic records with seed=42...")
    df = generate_food_surplus_data(num_samples=8000, random_seed=42)
    
    # Ensure destination directory exists
    os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)
    df.to_csv(DATASET_PATH, index=False)
    print(f"[CIBUS-AI] Dataset successfully saved to: {DATASET_PATH}")
    return df

if __name__ == "__main__":
    save_and_validate_dataset()
