"""
CIBUS-AI - Baseline Random Forest Regression Model
File: ai-engine/training/train_baseline.py

Purpose:
Trains the baseline Random Forest Regressor on the preprocessed 8,000-row food surplus dataset:
1. Loads and preprocesses data via the leakage-safe preprocessing pipeline (80/20 train-test split, random_state=42).
2. Fits RandomForestRegressor with n_estimators=100, random_state=42 (default hyperparameters).
3. Generates predictions on the unseen test set (1,600 samples).
4. Evaluates real baseline regression metrics: MAE, RMSE, and R² (Coefficient of Determination).
5. Persists baseline model and preprocessor artifacts to ai-engine/models/.
6. Exports machine-readable metrics to ai-engine/evaluation/baseline_results.json.
"""

import os
import sys
import json
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Ensure ai-engine root is in python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_ENGINE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if AI_ENGINE_DIR not in sys.path:
    sys.path.insert(0, AI_ENGINE_DIR)

from preprocessing.preprocess import preprocess_pipeline, DATASET_PATH

# Output Paths
MODELS_DIR = os.path.join(AI_ENGINE_DIR, "models")
EVAL_DIR = os.path.join(AI_ENGINE_DIR, "evaluation")
BASELINE_MODEL_PATH = os.path.join(MODELS_DIR, "baseline_food_surplus_model.pkl")
BASELINE_PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "baseline_preprocessor.pkl")
BASELINE_RESULTS_PATH = os.path.join(EVAL_DIR, "baseline_results.json")


def train_and_evaluate_baseline(
    dataset_path: str = DATASET_PATH,
    n_estimators: int = 100,
    random_state: int = 42
) -> Tuple[RandomForestRegressor, Dict[str, Any]]:
    """
    Executes baseline training and test set evaluation.

    Returns:
        Tuple of (trained_model, results_dict)
    """
    print("=" * 65)
    print("       CIBUS-AI BASELINE MODEL TRAINING & EVALUATION")
    print("=" * 65)

    # Step 1: Preprocess dataset with train/test isolation
    print("\n[1] Loading data & executing leakage-safe preprocessing pipeline...")
    X_train, X_test, y_train, y_test, preprocessor, feature_names = preprocess_pipeline(
        dataset_path=dataset_path,
        test_size=0.2,
        random_state=random_state,
        save_artifacts=True
    )
    print(f"    - Training samples: {X_train.shape[0]}")
    print(f"    - Testing samples:  {X_test.shape[0]}")
    print(f"    - Feature count:    {X_train.shape[1]}")

    # Step 2: Initialize baseline Random Forest Regressor
    print(f"\n[2] Initializing Baseline RandomForestRegressor(n_estimators={n_estimators}, random_state={random_state})...")
    baseline_rf = RandomForestRegressor(
        n_estimators=n_estimators,
        random_state=random_state,
        n_jobs=-1
    )

    # Step 3: Train model strictly on training data
    print("    - Fitting baseline model on training partition (X_train, y_train)...")
    baseline_rf.fit(X_train, y_train)
    print("    - Training complete.")

    # Step 4: Generate predictions on held-out test set
    print("\n[3] Generating predictions on held-out test set (X_test)...")
    y_pred = baseline_rf.predict(X_test)

    # Step 5: Compute actual regression evaluation metrics
    mae = float(mean_absolute_error(y_test, y_pred))
    # Calculate RMSE compatible across sklearn versions
    mse = float(mean_squared_error(y_test, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_test, y_pred))

    # Step 6: Serialize model and preprocessor artifacts
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(EVAL_DIR, exist_ok=True)

    joblib.dump(baseline_rf, BASELINE_MODEL_PATH)
    joblib.dump(preprocessor, BASELINE_PREPROCESSOR_PATH)

    results = {
        "model_name": "RandomForestRegressor (Baseline)",
        "algorithm": "Random Forest Regression",
        "hyperparameters": {
            "n_estimators": n_estimators,
            "random_state": random_state,
            "criterion": "squared_error",
            "max_depth": None,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
            "max_features": 1.0,
            "bootstrap": True
        },
        "dataset": {
            "path": os.path.relpath(dataset_path, AI_ENGINE_DIR),
            "total_samples": len(y_train) + len(y_test),
            "train_size": len(y_train),
            "test_size": len(y_test),
            "feature_count": X_train.shape[1]
        },
        "metrics": {
            "mae": round(mae, 4),
            "rmse": round(rmse, 4),
            "r2": round(r2, 4)
        },
        "target_variable": "Surplus_Meals",
        "random_state": random_state
    }

    # Step 7: Save results JSON
    with open(BASELINE_RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=4)

    # Step 8: Print formatted report
    print("\n" + "=" * 65)
    print("                 BASELINE EVALUATION METRICS")
    print("=" * 65)
    print(f"  * Mean Absolute Error (MAE):           {mae:.4f} meals")
    print(f"  * Root Mean Squared Error (RMSE):      {rmse:.4f} meals")
    print(f"  * Coefficient of Determination (R²):   {r2:.4f}")
    print("=" * 65)
    print(f"[Note] R² = {r2:.4f} represents the proportion of variance explained.")
    print("       (R² is NOT a percentage accuracy score).")
    print(f"[Artifacts Saved]")
    print(f"  - Model:        {BASELINE_MODEL_PATH}")
    print(f"  - Preprocessor: {BASELINE_PREPROCESSOR_PATH}")
    print(f"  - Results JSON: {BASELINE_RESULTS_PATH}")
    print("=" * 65)

    return baseline_rf, results


if __name__ == "__main__":
    train_and_evaluate_baseline()
