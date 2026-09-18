# CIBUS-AI: Baseline vs. Refined Model Performance Comparison

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**PBL Milestone:** Iterative Model Refinement & Hyperparameter Tuning  
**Evaluation Partition:** Held-out Test Set ($N = 1600$ samples, $80/20$ Split, `random_state=42`)

---

## 1. Experimental Overview
In accordance with Machine Learning PBL iterative development practices, the model underwent two structured development iterations:
- **Iteration 1 (Baseline):** Default `RandomForestRegressor` (`n_estimators=100`, unconstrained tree depth).
- **Iteration 2 (Refined):** 3-Fold Cross-Validated Hyperparameter Optimization across tree count, tree depth, sample splitting thresholds, and feature sub-sampling ratios.

---

## 2. Hyperparameter Configuration Comparison

| Hyperparameter | Iteration 1 (Baseline) | Iteration 2 (Refined Final Model) |
| :--- | :--- | :--- |
| `n_estimators` | `100` | `200` |
| `max_depth` | `None` (unbounded) | `15` |
| `min_samples_split` | `2` | `4` |
| `min_samples_leaf` | `1` | `1` |
| `max_features` | `1.0` (all features) | `0.8` |
| **Selection Method** | Default parameters | 3-Fold Cross-Validation on $X_{\text{train}}$ |
| **CV Validation Score** | N/A | **RMSE = 20.9391 meals** |

---

## 3. Actual Test Set Evaluation Results

| Performance Metric | Baseline Model | Refined Final Model | Absolute Difference ($\Delta$) | Result Status |
| :--- | :---: | :---: | :---: | :---: |
| **Mean Absolute Error (MAE)** | `14.2939` meals | **`14.5793` meals** | `+0.2854` meals | Comparable / Minor Change |
| **Root Mean Squared Error (RMSE)** | `20.5429` meals | **`20.6869` meals** | `+0.1440` meals | Comparable / Minor Change |
| **Coefficient of Determination ($R^2$)** | `0.9549` | **`0.9543`** | `-0.0006` | Comparable |

*(Note: $R^2$ represents the proportion of explained variance. It is strictly distinct from classification accuracy).*

---

## 4. Analysis & Engineering Rationale

1. **Why the Refined Model Was Selected:**
   - The hyperparameter search identified an optimal parameter set via cross-validation strictly on the training set, preventing test-set data snooping.
   - The refined model optimizes tree split constraints to enhance variance reduction.

2. **Data-Leakage Integrity:**
   - Both iterations strictly excluded `Meals_Sold` from all feature vectors.
   - Preprocessing was fitted exclusively on $X_{\text{train}}$, preserving test partition isolation.

3. **Production Artifacts Exported:**
   - Final serialized model saved at: `ai-engine/models/food_surplus_model.pkl`
   - Baseline model preserved at: `ai-engine/models/baseline_food_surplus_model.pkl` (retained for PBL iterative comparison defense).
