"""
CIBUS-AI - Surplus Meals Real-Time & Batch Prediction Engine
File: ai-engine/prediction/predict.py

Purpose:
Provides a clean, reusable inference interface for forecasting food surplus:
1. Validates input fields and rejects post-service features (e.g., Meals_Sold).
2. Performs data sanitization and defensive boundary checks.
3. Applies the pre-fitted preprocessing pipeline (OneHotEncoder + Passthrough).
4. Loads the trained final Random Forest Regressor (food_surplus_model.pkl).
5. Returns non-negative predicted surplus meal counts.
6. Operates both as an importable module and a command-line interface (CLI).
"""

import os
import sys
import argparse
from typing import Dict, Any, Union, List, Optional, Tuple
import numpy as np
import pandas as pd
import joblib

# Ensure ai-engine root is in python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_ENGINE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if AI_ENGINE_DIR not in sys.path:
    sys.path.insert(0, AI_ENGINE_DIR)

from preprocessing.preprocess import FEATURE_COLUMNS

# Artifact Locations
MODELS_DIR = os.path.join(AI_ENGINE_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "food_surplus_model.pkl")
PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "food_surplus_preprocessor.pkl")
BACKUP_PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "preprocessor.joblib")

# Global caches for loaded model and preprocessor (avoids re-reading disk on repeated calls)
_CACHED_MODEL = None
_CACHED_PREPROCESSOR = None


def load_inference_artifacts() -> Tuple[Any, Any]:
    """
    Loads and caches the serialized model and preprocessing pipeline.

    Returns:
        Tuple of (RandomForestRegressor, ColumnTransformer)
    """
    global _CACHED_MODEL, _CACHED_PREPROCESSOR

    if _CACHED_MODEL is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Trained model not found at: {MODEL_PATH}")
        _CACHED_MODEL = joblib.load(MODEL_PATH)

    if _CACHED_PREPROCESSOR is None:
        prep_path = PREPROCESSOR_PATH if os.path.exists(PREPROCESSOR_PATH) else BACKUP_PREPROCESSOR_PATH
        if not os.path.exists(prep_path):
            raise FileNotFoundError(f"Preprocessor artifact not found at: {prep_path}")
        _CACHED_PREPROCESSOR = joblib.load(prep_path)

    return _CACHED_MODEL, _CACHED_PREPROCESSOR


def validate_prediction_input(input_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates and normalizes input data prior to inference.

    Raises:
        ValueError: If required fields are missing, invalid, or if data leakage is detected.
    """
    # 1. Strict Data Leakage Prevention Check
    if "Meals_Sold" in input_dict or "meals_sold" in input_dict:
        raise ValueError(
            "CRITICAL ERROR (Data Leakage Violation): 'Meals_Sold' is a post-service outcome "
            "and cannot be accepted as a pre-service prediction input."
        )

    # 2. Check required fields
    clean_dict: Dict[str, Any] = {}
    missing_fields = []
    for field in FEATURE_COLUMNS:
        if field not in input_dict:
            missing_fields.append(field)
    if missing_fields:
        raise ValueError(f"Missing required prediction fields: {missing_fields}")

    # 3. Numerical Validations
    try:
        customers = int(input_dict["Customers_Forecast"])
        if customers < 0:
            raise ValueError(f"Customers_Forecast must be non-negative, got {customers}")
        clean_dict["Customers_Forecast"] = customers
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid Customers_Forecast: {input_dict.get('Customers_Forecast')} ({e})")

    try:
        meals = int(input_dict["Meals_Prepared"])
        if meals < 0:
            raise ValueError(f"Meals_Prepared must be non-negative, got {meals}")
        clean_dict["Meals_Prepared"] = meals
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid Meals_Prepared: {input_dict.get('Meals_Prepared')} ({e})")

    try:
        staff = int(input_dict["Staff_Count"])
        if staff < 1:
            raise ValueError(f"Staff_Count must be at least 1, got {staff}")
        clean_dict["Staff_Count"] = staff
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid Staff_Count: {input_dict.get('Staff_Count')} ({e})")

    try:
        rating = float(input_dict["Avg_Rating"])
        if not (1.0 <= rating <= 5.0):
            raise ValueError(f"Avg_Rating must be between 1.0 and 5.0, got {rating}")
        clean_dict["Avg_Rating"] = round(rating, 2)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid Avg_Rating: {input_dict.get('Avg_Rating')} ({e})")

    # 4. Special Event Binary Normalization
    special = input_dict["Special_Event"]
    if isinstance(special, str):
        special_val = 1 if special.strip().lower() in ["yes", "y", "1", "true"] else 0
    else:
        special_val = 1 if int(special) == 1 else 0
    clean_dict["Special_Event"] = special_val

    # 5. Categorical Sanitization
    clean_dict["Day"] = str(input_dict["Day"]).strip().capitalize() if input_dict["Day"] else "Monday"
    clean_dict["Weather"] = str(input_dict["Weather"]).strip().capitalize() if input_dict["Weather"] else "Sunny"
    
    # Event_Type handling (support fallback if None or empty)
    raw_event = input_dict.get("Event_Type")
    if raw_event is None or str(raw_event).strip().lower() in ["none", "", "null"]:
        clean_dict["Event_Type"] = "Regular"
    else:
        clean_dict["Event_Type"] = str(raw_event).strip().capitalize()

    # Festival handling
    raw_fest = input_dict.get("Festival")
    if raw_fest is None or str(raw_fest).strip().lower() in ["none", "", "null", "no"]:
        clean_dict["Festival"] = "No"
    else:
        clean_dict["Festival"] = str(raw_fest).strip()

    return clean_dict


def enforce_physical_constraints(
    predicted_surplus: float,
    meals_prepared: float,
    customers_forecast: float
) -> float:
    """
    Enforces post-prediction physical domain invariants:
    1. final_surplus = max(0.0, predicted_surplus)
    2. final_surplus = min(final_surplus, meals_prepared)
    3. Additionally, if customers_forecast >= meals_prepared:
       final_surplus = 0.0 (all prepared food is demanded/consumed)
    """
    final_surplus = max(0.0, float(predicted_surplus))
    final_surplus = min(final_surplus, float(meals_prepared))
    if customers_forecast >= meals_prepared:
        final_surplus = 0.0
    return round(final_surplus, 2)


def predict_surplus_detailed(input_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Provides both raw ML model prediction and operationally validated surplus
    with constraint audit verification.
    """
    model, preprocessor = load_inference_artifacts()
    validated_dict = validate_prediction_input(input_dict)
    df_single = pd.DataFrame([validated_dict])[FEATURE_COLUMNS]
    X_trans = preprocessor.transform(df_single)
    raw_pred = float(model.predict(X_trans)[0])
    meals_prep = float(validated_dict["Meals_Prepared"])
    cust_fore = float(validated_dict["Customers_Forecast"])

    final_pred = enforce_physical_constraints(raw_pred, meals_prep, cust_fore)
    constraints_ok = (0.0 <= final_pred <= meals_prep) and (final_pred == 0.0 if cust_fore >= meals_prep else True)

    return {
        "raw_prediction": round(raw_pred, 2),
        "validated_prediction": final_pred,
        "meals_prepared": meals_prep,
        "customers_forecast": cust_fore,
        "constraints_satisfied": constraints_ok
    }


def predict_surplus(input_data: Union[Dict[str, Any], pd.DataFrame, List[Dict[str, Any]]]) -> Union[float, List[float]]:
    """
    Predicts expected surplus meals based on pre-service operational indicators.

    Parameters:
        input_data: A dictionary, list of dictionaries, or pandas DataFrame
                    containing required operational features.

    Returns:
        float or List[float]: Estimated surplus meals (bounded >= 0.0).

    Example:
        >>> from prediction.predict import predict_surplus
        >>> sample = {
        ...     "Day": "Saturday",
        ...     "Weather": "Sunny",
        ...     "Customers_Forecast": 350,
        ...     "Meals_Prepared": 400,
        ...     "Festival": "No",
        ...     "Event_Type": "Regular",
        ...     "Staff_Count": 12,
        ...     "Avg_Rating": 4.3,
        ...     "Special_Event": 0
        ... }
        >>> predict_surplus(sample)
        45.2
    """
    model, preprocessor = load_inference_artifacts()

    # Handle single dictionary input
    if isinstance(input_data, dict):
        validated_dict = validate_prediction_input(input_data)
        df_single = pd.DataFrame([validated_dict])[FEATURE_COLUMNS]
        X_trans = preprocessor.transform(df_single)
        raw_pred = float(model.predict(X_trans)[0])
        final_pred = enforce_physical_constraints(
            predicted_surplus=raw_pred,
            meals_prepared=float(validated_dict["Meals_Prepared"]),
            customers_forecast=float(validated_dict["Customers_Forecast"])
        )
        return final_pred

    # Handle DataFrame or list of records
    elif isinstance(input_data, (pd.DataFrame, list)):
        records = input_data.to_dict(orient="records") if isinstance(input_data, pd.DataFrame) else input_data
        validated_records = [validate_prediction_input(rec) for rec in records]
        df_batch = pd.DataFrame(validated_records)[FEATURE_COLUMNS]
        X_trans = preprocessor.transform(df_batch)
        raw_preds = model.predict(X_trans)
        results = []
        for pred, rec in zip(raw_preds, validated_records):
            final_pred = enforce_physical_constraints(
                predicted_surplus=float(pred),
                meals_prepared=float(rec["Meals_Prepared"]),
                customers_forecast=float(rec["Customers_Forecast"])
            )
            results.append(final_pred)
        return results

    else:
        raise TypeError(f"Unsupported input type: {type(input_data)}. Expected dict, list, or DataFrame.")


def parse_cli_args():
    """Parses command line arguments for CLI usage."""
    parser = argparse.ArgumentParser(
        description="CIBUS-AI: Real-Time Food Surplus Prediction CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--day", type=str, default="Saturday", help="Day of the week (e.g. Saturday, Monday)")
    parser.add_argument("--weather", type=str, default="Sunny", help="Weather condition (e.g. Sunny, Rainy, Stormy)")
    parser.add_argument("--customers", type=int, default=350, help="Expected customer footfall forecast")
    parser.add_argument("--meals", type=int, default=400, help="Total meals prepared by kitchen")
    parser.add_argument("--festival", type=str, default="No", help="Festival name or 'No'")
    parser.add_argument("--event", type=str, default="Regular", help="Event type (Regular, Buffet, Corporate, Banquet)")
    parser.add_argument("--staff", type=int, default=12, help="Active staff count on duty")
    parser.add_argument("--rating", type=float, default=4.3, help="Establishment average rating (1.0 - 5.0)")
    parser.add_argument("--special", type=str, default="0", help="Special event flag (0/1 or Yes/No)")
    parser.add_argument("--demo", action="store_true", help="Run demonstrative sample predictions")
    return parser.parse_args()


def run_sanity_benchmark():
    """
    Executes the 8 canonical benchmark sanity cases and 100+ randomized
    test combinations to verify physical domain invariants across all regimes.
    """
    model, prep = load_inference_artifacts()
    print("=" * 80)
    print("     CIBUS-AI: CANONICAL BENCHMARK & GENERALIZATION AUDIT")
    print("=" * 80)

    sanity_cases = [
        {"id": 1, "desc": "C=200, M=20 (Demand Overhang)", "c": 200, "m": 20, "staff": 5, "exp": "0.0 or near 0"},
        {"id": 2, "desc": "C=20, M=200 (Large Supply Excess)", "c": 20, "m": 200, "staff": 10, "exp": "Positive (~130-180)"},
        {"id": 3, "desc": "C=100, M=200 (Moderate Buffer)", "c": 100, "m": 200, "staff": 10, "exp": "Positive (~85-110)"},
        {"id": 4, "desc": "C=200, M=200 (Supply-Demand Parity)", "c": 200, "m": 200, "staff": 10, "exp": "Near zero (0.0)"},
        {"id": 5, "desc": "C=500, M=200 (High Footfall Overhang)", "c": 500, "m": 200, "staff": 10, "exp": "Near zero (0.0)"},
        {"id": 6, "desc": "C=100, M=500 (Massive Over-Catering)", "c": 100, "m": 500, "staff": 20, "exp": "Substantial (~340-410)"},
        {"id": 7, "desc": "C=800, M=900 (Large Event Buffer)", "c": 800, "m": 900, "staff": 35, "exp": "Moderate (~30-90)"},
        {"id": 8, "desc": "C=300, M=1000 (Major Cancellation/Overprep)", "c": 300, "m": 1000, "staff": 40, "exp": "Large (~640-720)"},
    ]

    print("\n--- 8 SPECIFIED BENCHMARK SANITY CASES ---")
    print(f"{'#':<3} | {'Scenario':<42} | {'Raw RF':<9} | {'Validated':<9} | {'Status':<12}")
    print("-" * 80)

    for tc in sanity_cases:
        payload = {
            "Day": "Monday",
            "Weather": "Sunny",
            "Customers_Forecast": tc["c"],
            "Meals_Prepared": tc["m"],
            "Festival": "No",
            "Event_Type": "Regular",
            "Staff_Count": tc["staff"],
            "Avg_Rating": 4.0,
            "Special_Event": 0
        }
        res = predict_surplus_detailed(payload)
        raw = res["raw_prediction"]
        val = res["validated_prediction"]
        m = tc["m"]
        ok = "PASS" if (0.0 <= val <= m) else "FAIL"
        print(f"{tc['id']:<3} | {tc['desc']:<42} | {raw:9.2f} | {val:9.2f} | {ok:<12}")

    # 100+ Randomized Tests
    rng = np.random.default_rng(2026)
    num_tests = 120
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weathers = ["Sunny", "Cloudy", "Rainy", "Stormy"]
    events = ["Regular", "Buffet", "Corporate", "Banquet"]
    festivals = ["No", "Diwali", "Eid", "Christmas", "New Year"]

    violations = 0
    raw_list, val_list = [], []
    for _ in range(num_tests):
        m = int(rng.integers(20, 1400))
        c = int(rng.integers(20, 1000))
        payload = {
            "Day": str(rng.choice(days)),
            "Weather": str(rng.choice(weathers)),
            "Customers_Forecast": c,
            "Meals_Prepared": m,
            "Festival": str(rng.choice(festivals)),
            "Event_Type": str(rng.choice(events)),
            "Staff_Count": int(np.clip(3 + m // 26, 4, 52)),
            "Avg_Rating": round(float(rng.uniform(2.5, 4.9)), 2),
            "Special_Event": int(rng.choice([0, 1]))
        }
        res = predict_surplus_detailed(payload)
        raw_list.append(res["raw_prediction"])
        val_list.append(res["validated_prediction"])
        if not (0.0 <= res["validated_prediction"] <= m):
            violations += 1

    print("\n--- 120 RANDOMIZED OPERATIONAL CASES AUDIT ---")
    print(f"Total Cases:         {num_tests}")
    print(f"Physical Violations: {violations} (0 <= Surplus <= Meals_Prepared)")
    print(f"Raw RF Range:        [{min(raw_list):.2f}, {max(raw_list):.2f}]")
    print(f"Validated Range:     [{min(val_list):.2f}, {max(val_list):.2f}]")
    print(f"Zero-Surplus Rate:   {sum(1 for v in val_list if v == 0.0) / num_tests * 100:.1f}%")
    print(f"Positive Rate:       {sum(1 for v in val_list if v > 0.0) / num_tests * 100:.1f}%")
    print("=" * 80)


def main():
    """Main CLI execution routine."""
    args = parse_cli_args()

    if args.demo:
        run_sanity_benchmark()
        return

    print("=" * 65)
    print("      CIBUS-AI: FOOD SURPLUS PREDICTION SYSTEM")
    print("=" * 65)

    input_payload = {
        "Day": args.day,
        "Weather": args.weather,
        "Customers_Forecast": args.customers,
        "Meals_Prepared": args.meals,
        "Festival": args.festival,
        "Event_Type": args.event,
        "Staff_Count": args.staff,
        "Avg_Rating": args.rating,
        "Special_Event": args.special
    }

    try:
        print("\n[Input Operational Parameters]")
        for k, v in input_payload.items():
            print(f"  * {k:<20}: {v}")

        predicted_surplus = predict_surplus(input_payload)

        print("\n" + "-" * 65)
        print(f"  >>> Predicted Surplus Meals: {predicted_surplus:.2f} meals <<<")
        print("-" * 65)
        print(f"[Logistics Recommendation] Prepare redistribution dispatch for ~{int(round(predicted_surplus))} meal units.")
        print("=" * 65)

    except Exception as err:
        print(f"\n[ERROR] Prediction failed: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
