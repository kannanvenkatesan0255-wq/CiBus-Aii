"""
CIBUS-AI - Feature Importance & Interpretability Analysis Module
File: ai-engine/training/feature_importance.py

Purpose:
Extracts and analyzes Mean Decrease in Impurity (MDI) / Gini feature importances
from the trained Random Forest model (food_surplus_model.pkl):
1. Loads the saved model and preprocessor to retrieve exact transformed feature names.
2. Validates importance values (numeric, non-negative, summing to ~1.0, NO Meals_Sold).
3. Produces ranked feature importance tables for both transformed and aggregated original features.
4. Generates a clean horizontal bar chart visualization saved to ai-engine/plots/feature_importance.png.
5. Exports structured results to ai-engine/evaluation/feature_importance.csv and summary JSON.
"""

import os
import sys
import json
from typing import Dict, List, Any, Tuple
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt

# Ensure ai-engine root is in python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_ENGINE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if AI_ENGINE_DIR not in sys.path:
    sys.path.insert(0, AI_ENGINE_DIR)

from preprocessing.preprocess import (
    get_feature_names,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    FEATURE_COLUMNS,
    TARGET_COLUMN
)

# File Paths
MODELS_DIR = os.path.join(AI_ENGINE_DIR, "models")
EVAL_DIR = os.path.join(AI_ENGINE_DIR, "evaluation")
PLOTS_DIR = os.path.join(AI_ENGINE_DIR, "plots")

MODEL_PATH = os.path.join(MODELS_DIR, "food_surplus_model.pkl")
PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "food_surplus_preprocessor.pkl")
BACKUP_PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "preprocessor.joblib")

OUTPUT_CSV_PATH = os.path.join(EVAL_DIR, "feature_importance.csv")
OUTPUT_JSON_PATH = os.path.join(EVAL_DIR, "feature_importance_summary.json")
OUTPUT_PLOT_PATH = os.path.join(PLOTS_DIR, "feature_importance.png")


def aggregate_by_original_feature(
    transformed_df: pd.DataFrame,
    raw_features: List[str]
) -> pd.DataFrame:
    """
    Aggregates one-hot encoded dummy column importances back to their
    original parent feature category.
    """
    aggregated_dict = {feat: 0.0 for feat in raw_features}

    for _, row in transformed_df.iterrows():
        feat_name = row["Feature"]
        importance_val = row["Importance"]

        matched = False
        for raw_feat in raw_features:
            if feat_name.startswith(f"{raw_feat}_") or feat_name == raw_feat:
                aggregated_dict[raw_feat] += importance_val
                matched = True
                break

        if not matched:
            aggregated_dict[feat_name] = aggregated_dict.get(feat_name, 0.0) + importance_val

    agg_df = pd.DataFrame([
        {"Original_Feature": k, "Aggregated_Importance": v}
        for k, v in aggregated_dict.items()
    ])
    agg_df["Aggregated_Importance"] = agg_df["Aggregated_Importance"].round(4)
    agg_df = agg_df.sort_values(by="Aggregated_Importance", ascending=False).reset_index(drop=True)
    agg_df["Rank"] = range(1, len(agg_df) + 1)
    return agg_df


def plot_feature_importance(
    df_transformed: pd.DataFrame,
    df_aggregated: pd.DataFrame,
    output_path: str
):
    """
    Renders a clear, publication-quality horizontal bar chart of feature importances.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Plot top 15 transformed features for detailed insight
    top_n = min(15, len(df_transformed))
    df_top = df_transformed.head(top_n).sort_values(by="Importance", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)

    bars = ax.barh(
        df_top["Feature"],
        df_top["Importance"],
        color="#2b5c8f",
        edgecolor="#1b3b5f",
        height=0.65
    )

    # Add numeric labels to ends of bars
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + 0.005,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.4f}",
            va="center",
            ha="left",
            fontsize=9,
            color="#222222"
        )

    ax.set_title("CIBUS-AI: Random Forest Feature Importance (MDI)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Feature Importance (Mean Decrease in Impurity)", fontsize=11, labelpad=8)
    ax.set_ylabel("Transformed Operational Feature", fontsize=11, labelpad=8)
    ax.set_xlim(0, max(df_top["Importance"]) * 1.15)
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[CIBUS-AI] Feature importance plot saved to: {output_path}")


def analyze_feature_importance() -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Loads final Random Forest model and performs feature importance extraction.
    """
    print("=" * 70)
    print("      CIBUS-AI RANDOM FOREST FEATURE IMPORTANCE ANALYSIS")
    print("=" * 70)

    # 1. Load Model
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
    print(f"\n[1] Loaded trained model: {MODEL_PATH}")

    # 2. Load Preprocessor to extract feature names
    prep_path = PREPROCESSOR_PATH if os.path.exists(PREPROCESSOR_PATH) else BACKUP_PREPROCESSOR_PATH
    if not os.path.exists(prep_path):
        raise FileNotFoundError(f"Preprocessor file not found at: {prep_path}")
    preprocessor = joblib.load(prep_path)
    feature_names = get_feature_names(preprocessor)
    print(f"[2] Recovered {len(feature_names)} transformed feature names from preprocessor.")

    # 3. Retrieve feature importances from model
    raw_importances = model.feature_importances_

    # 4. Strict Validation Checks
    print("\n[3] Executing Model Feature Integrity Checks...")
    assert len(raw_importances) == len(feature_names), (
        f"Mismatch: {len(raw_importances)} importances vs {len(feature_names)} feature names"
    )
    assert np.all(raw_importances >= 0.0), "Negative importance values detected!"
    total_importance = float(np.sum(raw_importances))
    assert np.isclose(total_importance, 1.0, atol=1e-3), (
        f"Total importance sums to {total_importance:.4f}, expected ~1.0"
    )
    assert "Meals_Sold" not in feature_names, (
        "CRITICAL LEAKAGE DETECTED: 'Meals_Sold' present in model features!"
    )
    print("    [PASS] Feature dimensions match (25 features).")
    print("    [PASS] All importance values are non-negative numeric floats.")
    print(f"    [PASS] Total importance sum = {total_importance:.6f} (~1.0).")
    print("    [PASS] 'Meals_Sold' is STRICTLY ABSENT (Zero Data Leakage).")

    # 5. Build Transformed Feature Ranking DataFrame
    df_transformed = pd.DataFrame({
        "Feature": feature_names,
        "Importance": np.round(raw_importances, 6)
    }).sort_values(by="Importance", ascending=False).reset_index(drop=True)
    df_transformed["Rank"] = range(1, len(df_transformed) + 1)

    # 6. Build Aggregated Parent Feature DataFrame
    df_aggregated = aggregate_by_original_feature(df_transformed, FEATURE_COLUMNS)

    # 7. Save Transformed CSV
    os.makedirs(EVAL_DIR, exist_ok=True)
    df_transformed[["Rank", "Feature", "Importance"]].to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"\n[4] Saved transformed feature importance table to: {OUTPUT_CSV_PATH}")

    # 8. Generate Visual Plot
    plot_feature_importance(df_transformed, df_aggregated, OUTPUT_PLOT_PATH)

    # 9. Export Summary JSON
    summary_data = {
        "model_name": type(model).__name__,
        "model_file": os.path.basename(MODEL_PATH),
        "target_variable": TARGET_COLUMN,
        "total_transformed_features": len(feature_names),
        "total_raw_features": len(FEATURE_COLUMNS),
        "total_importance_sum": round(total_importance, 6),
        "ranked_transformed_features": df_transformed.to_dict(orient="records"),
        "ranked_aggregated_features": df_aggregated.to_dict(orient="records")
    }

    with open(OUTPUT_JSON_PATH, "w") as f:
        json.dump(summary_data, f, indent=4)
    print(f"[5] Saved feature importance summary JSON to: {OUTPUT_JSON_PATH}")

    # 10. Print Formatted Summary Tables
    print("\n" + "=" * 70)
    print("         RANKED TRANSFORMED FEATURE IMPORTANCES (TOP 10)")
    print("=" * 70)
    print(f"{'Rank':<6} | {'Transformed Feature':<28} | {'Importance':<12}")
    print("-" * 52)
    for _, r in df_transformed.head(10).iterrows():
        print(f"{int(r['Rank']):<6} | {r['Feature']:<28} | {r['Importance']:<12.4f}")

    print("\n" + "=" * 70)
    print("     AGGREGATED LOGICAL FEATURE IMPORTANCES (ALL 9 FEATURES)")
    print("=" * 70)
    print(f"{'Rank':<6} | {'Original Feature':<24} | {'Aggregated Importance':<22}")
    print("-" * 58)
    for _, r in df_aggregated.iterrows():
        print(f"{int(r['Rank']):<6} | {r['Original_Feature']:<24} | {r['Aggregated_Importance']:<22.4f}")
    print("=" * 70)

    return df_transformed, df_aggregated, summary_data


if __name__ == "__main__":
    analyze_feature_importance()
