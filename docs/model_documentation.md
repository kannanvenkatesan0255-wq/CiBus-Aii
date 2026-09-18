# Model Documentation: CIBUS-AI Predictive Engine

---

## 1. Problem Formulation: Why Regression?

The CIBUS-AI forecasting task is mathematically formulated as **Supervised Regression**.

### Justification:
- The target variable `Surplus_Meals` is a continuous quantitative count ($\mathbb{R}_{\ge 0}$) representing the exact estimated volume of leftover meal portions.
- A classification approach (e.g., "Surplus" vs "No Surplus") is inadequate for logistics planning. NGO dispatchers require specific capacity figures (e.g., whether to dispatch a 20-meal bike carrier or a 250-meal refrigerated van).
- Regression provides a direct quantitative estimation $\hat{y} \in [0, \infty)$ allowing granular distribution logistics.

---

## 2. Model Selection: Random Forest Regressor

### Algorithm Overview
Random Forest is an ensemble learning method based on **Bagging (Bootstrap Aggregating)** that constructs a multitude of uncorrelated Decision Trees during training and outputs the mean prediction ($\frac{1}{B}\sum_{b=1}^{B} T_b(x)$) of individual trees.

### Why Random Forest for Food Surplus Forecasting?
1. **Non-Linear Interactions:** Captures complex multi-feature interactions (e.g., Stormy weather $\times$ Banquet format) without manual polynomial feature expansion.
2. **Robustness Against Overfitting:** Ensemble averaging over randomized bootstrap subsamples reduces overall model variance.
3. **Handling High-Dimensional Encoded Features:** Natively splits across the 25 transformed one-hot encoded operational variables.
4. **Interpretability via Feature Importance:** Calculates Mean Decrease in Impurity (MDI) to identify key drivers of food surplus.

---

## 3. Preprocessing, Partitioning & Leakage-Free Pipeline

### Validation & Train-Test Strategy
- **Partitioning Ratio:** 80% Training ($N = 6,400$), 20% Testing ($N = 1,600$)
- **Reproducibility:** Deterministic pseudo-random seed `random_state=42`.
- **Transformation Isolation:** 
  - The `ColumnTransformer` (OneHotEncoder for categorical features + passthrough for numerical features) is fitted **strictly on $X_{\text{train}}$**.
  - $X_{\text{test}}$ is transformed using the pre-fitted transformer without re-fitting.
  - The fitted preprocessor is serialized to `ai-engine/models/food_surplus_preprocessor.pkl`.

---

## 4. Evaluation Metrics Definition

Regression models are evaluated using the following formal metrics:

### 1. Mean Absolute Error (MAE)
$$\text{MAE} = \frac{1}{n} \sum_{i=1}^{n} |y_i - \hat{y}_i|$$
- Measures average absolute prediction error magnitude in real physical meal units.

### 2. Root Mean Squared Error (RMSE)
$$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2}$$
- Measures standard deviation of residuals, penalizing larger deviations quadratically.

### 3. Coefficient of Determination ($R^2$ Score)
$$R^2 = 1 - \frac{\sum_{i=1}^{n} (y_i - \hat{y}_i)^2}{\sum_{i=1}^{n} (y_i - \bar{y})^2}$$
- Quantifies the proportion of target variance explained by input features relative to a naive mean predictor.

---

## 5. Critical Distinction: $R^2$ is NOT Classification Accuracy

> [!WARNING]
> Stating that an $R^2$ score of $0.9543$ represents "95.43% accuracy" is mathematically incorrect. $R^2$ is the Coefficient of Determination (explained variance). Classification accuracy applies only to discrete class labels.

---

## 6. Iterative PBL Development & Model Refinement *(Experimental Results)*

### Iteration 1: Baseline Random Forest Model
- **Configuration:** `n_estimators=100`, `max_depth=None`, `min_samples_split=2`, `min_samples_leaf=1`, `max_features=1.0`, `random_state=42`.
- **Test Performance ($N=1,600$):**
  - **MAE:** `14.2939 meals`
  - **RMSE:** `20.5429 meals`
  - **$R^2$ Score:** `0.9549`

### Iteration 2: Hyperparameter Optimization & Refined Model
- **Refinement Motivation:** Investigate whether constraining tree depth, tuning split minimums, and sub-sampling features optimizes variance control on unseen data.
- **Cross-Validation Strategy:** 3-Fold Cross-Validation strictly on the training partition ($X_{\text{train}}$) using `neg_root_mean_squared_error` scoring.
- **Best Selected Hyperparameters:**
  - `n_estimators`: `200`
  - `max_depth`: `15`
  - `min_samples_split`: `4`
  - `min_samples_leaf`: `1`
  - `max_features`: `0.8`
  - *Best 3-Fold CV RMSE:* `20.9391 meals`
- **Test Performance ($N=1,600$):**
  - **MAE:** `14.5793 meals`
  - **RMSE:** `20.6869 meals`
  - **$R^2$ Score:** `0.9543`

---

## 7. Baseline vs. Refined Comparison Summary

| Metric | Baseline Model (Iter. 1) | Refined Final Model (Iter. 2) | Difference ($\Delta$) | Analysis |
| :--- | :---: | :---: | :---: | :--- |
| **MAE** | 14.2939 meals | **14.5793 meals** | $+0.2854$ meals | Highly comparable ($\approx 14.4$ meals average error). |
| **RMSE** | 20.5429 meals | **20.6869 meals** | $+0.1440$ meals | Highly comparable residual variance. |
| **$R^2$** | 0.9549 | **0.9543** | $-0.0006$ | Both models consistently explain $>95.4\%$ variance. |

---

## 8. Feature Importance Analysis *(MDI Extraction)*

- **`Meals_Prepared` (48.96%):** Primary scale driver setting the absolute surplus ceiling.
- **`Event_Type` (16.51%):** Buffet/Banquet display formats vs. portion-controlled regular dining.
- **`Weather` (16.03%, `Weather_Stormy`: 10.93%):** Footfall disruption shocks.
- **`Staff_Count` (11.66%):** Kitchen throughput and operational capacity proxy.

> **Methodological Note:** Feature importance indicates predictive utility within the trained ensemble; it does not establish causal proof. Diagnostic plot saved in `ai-engine/plots/feature_importance.png`.

---

## 9. Final Model Evaluation & Diagnostic Analysis

Evaluated on the held-out test partition ($N = 1,600$ samples, $20\%$ of total records) via `ai-engine/evaluation/evaluate_model.py`:

- **Mean Absolute Error (MAE):** `14.5793 meals`
- **Root Mean Squared Error (RMSE):** `20.6869 meals`
- **Coefficient of Determination ($R^2$):** `0.9543`
- **Mean Residual Bias ($\bar{e}$):** `-0.2729 meals` (Near-zero systematic error)
- **Residual Standard Deviation ($s_e$):** `20.6851 meals`
- **Tolerance Interval ($\pm 15$ meals):** `65.38%` of test samples
- **Tolerance Interval ($\pm 25$ meals):** `82.81%` of test samples
- **Diagnostic Plots:** [actual_vs_predicted.png](file:///k:/CiBus-Ai%20R/ai-engine/plots/actual_vs_predicted.png), [residual_analysis.png](file:///k:/CiBus-Ai%20R/ai-engine/plots/residual_analysis.png).

---

## 10. Standalone Prediction Pipeline & Inference Workflow

The prediction system is implemented in `ai-engine/prediction/predict.py`:

```
Input Operational Dictionary
            │
            ├── 1. Validation: Verifies 9 keys, bounds, and REJECTS Meals_Sold
            ├── 2. Transformation: Converts via persisted ColumnTransformer
            ├── 3. Inference: Computes prediction via food_surplus_model.pkl
            └── 4. Physical Bounding: Clips to [0.0, Meals_Prepared]
```

### Example Prediction:
```python
from prediction.predict import predict_surplus

input_data = {
    "Day": "Saturday",
    "Weather": "Sunny",
    "Customers_Forecast": 350,
    "Meals_Prepared": 400,
    "Festival": "No",
    "Event_Type": "Regular",
    "Staff_Count": 12,
    "Avg_Rating": 4.3,
    "Special_Event": 0
}

predicted_meals = predict_surplus(input_data)
# Returns: 41.14 meals
```

---

## 11. Backend REST API Integration & Serving

To enable web and mobile client applications to consume the trained model, CIBUS-AI encapsulates the inference engine inside an asynchronous **FastAPI** service (`backend/app/`):

1. **Zero Retraining Architecture:** The backend imports `predict_surplus()` and `load_inference_artifacts()` directly from `ai-engine/prediction/predict.py`. No training, tuning, or modification of model weights occurs during API execution.
2. **Schema & Leakage Defense:** Incoming JSON requests are validated using Pydantic schemas (`backend/app/schemas.py`). Any attempt to submit post-service features (such as `Meals_Sold`) triggers an immediate HTTP 422 validation error.
3. **Operational Contextualization:** In addition to the raw quantitative prediction $\hat{y}$, the service layer attaches logistics recommendations (e.g. shelter alert thresholds) based on forecasted surplus volume.
4. **Endpoint Exposure:**
   - `POST /api/predict`: Real-time surplus forecasting endpoint.
   - `GET /api/model-info`: Returns active model metadata, feature schemas, and test evaluation metrics.
   - `GET /health`: Validates server health and confirms both ML model and preprocessor artifacts are loaded.
