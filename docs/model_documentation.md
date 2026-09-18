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

### Reusability in Production Inference
In real-world inference (`predict.py`), individual JSON/dictionary inputs are passed into `transform_single_input()`. Using the persisted preprocessor guarantees that categorical one-hot vectors always map to the identical 25-feature dimensional ordering expected by the trained model.

---

## 4. Evaluation Metrics Definition

Regression models are evaluated using the following formal metrics:

### 1. Mean Absolute Error (MAE)
$$\text{MAE} = \frac{1}{n} \sum_{i=1}^{n} |y_i - \hat{y}_i|$$
- Measures average prediction error magnitude in real physical meal units.

### 2. Root Mean Squared Error (RMSE)
$$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2}$$
- Penalizes large prediction errors quadratically.

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

| Metric | Baseline Model (Iter. 1) | Refined Model (Iter. 2) | Difference ($\Delta$) | Analysis |
| :--- | :---: | :---: | :---: | :--- |
| **MAE** | 14.2939 meals | **14.5793 meals** | $+0.2854$ meals | Highly comparable ($\approx 14.4$ meals average error). |
| **RMSE** | 20.5429 meals | **20.6869 meals** | $+0.1440$ meals | Highly comparable residual variance. |
| **$R^2$** | 0.9549 | **0.9543** | $-0.0006$ | Both models consistently explain $>95.4\%$ variance. |

---

## 8. Feature Importance Analysis *(MDI Extraction)*

### 1. Purpose of Feature Importance Analysis
In a Machine Learning PBL project, model interpretability is vital for validating that the predictive engine relies on logical operational relationships rather than spurious artifacts, and for providing actionable operational insights to kitchen managers and food recovery coordinators.

### 2. Method Used
- **Algorithm Metric:** Mean Decrease in Impurity (MDI), computed across all 200 trees in the trained Random Forest ensemble.
- **Model Evaluated:** `ai-engine/models/food_surplus_model.pkl`.
- **Target:** `Surplus_Meals` (Leakage-free, `Meals_Sold` strictly omitted).

### 3. Actual Ranked Feature Importance Results

#### Transformed Feature Importances (Top 12):
| Rank | Transformed Feature | Importance (MDI) | Category |
| :-: | :--- | :---: | :--- |
| 1 | `Meals_Prepared` | **0.4896** (48.96%) | Numerical (Batch production volume) |
| 2 | `Staff_Count` | **0.1166** (11.66%) | Numerical (Kitchen scale & capacity) |
| 3 | `Weather_Stormy` | **0.1093** (10.93%) | Categorical One-Hot (Disruption factor) |
| 4 | `Event_Type_Regular` | **0.0647** (6.47%) | Categorical One-Hot (Service format) |
| 5 | `Event_Type_Buffet` | **0.0564** (5.64%) | Categorical One-Hot (Service format) |
| 6 | `Weather_Rainy` | **0.0387** (3.87%) | Categorical One-Hot (Disruption factor) |
| 7 | `Event_Type_Banquet` | **0.0343** (3.43%) | Categorical One-Hot (Service format) |
| 8 | `Customers_Forecast` | **0.0246** (2.46%) | Numerical (Planned attendance) |
| 9 | `Festival_No` | **0.0216** (2.16%) | Categorical One-Hot (Calendar baseline) |
| 10 | `Event_Type_Corporate` | **0.0097** (0.97%) | Categorical One-Hot (Service format) |
| 11 | `Special_Event` | **0.0079** (0.79%) | Binary Indicator |
| 12 | `Weather_Sunny` | **0.0077** (0.77%) | Categorical One-Hot (Baseline weather) |

#### Aggregated Logical Feature Importances (All 9 Features):
| Rank | Original Feature | Aggregated Importance | Cumulative Share |
| :-: | :--- | :---: | :---: |
| 1 | **`Meals_Prepared`** | **0.4896** (48.96%) | 48.96% |
| 2 | **`Event_Type`** | **0.1651** (16.51%) | 65.47% |
| 3 | **`Weather`** | **0.1603** (16.03%) | 81.50% |
| 4 | **`Staff_Count`** | **0.1166** (11.66%) | 93.16% |
| 5 | **`Customers_Forecast`** | **0.0246** (2.46%) | 95.62% |
| 6 | **`Festival`** | **0.0238** (2.38%) | 98.00% |
| 7 | **`Special_Event`** | **0.0079** (0.79%) | 98.79% |
| 8 | **`Avg_Rating`** | **0.0072** (0.72%) | 99.51% |
| 9 | **`Day`** | **0.0048** (0.48%) | 100.00% |

### 4. Domain Interpretation of Key Features
1. **`Meals_Prepared` (48.96%):** As the primary physical scale driver, the total volume of food batch-cooked dictates the absolute upper bound and scale of potential leftover variance.
2. **`Event_Type` (16.51%):** Service format heavily governs leftover probability: buffets and banquets require high continuous safety buffer presentation, whereas regular dining allows portion control.
3. **`Weather` (16.03%, specifically `Weather_Stormy` 10.93%):** Severe weather acts as a major external demand shock that sharply reduces walk-in footfall below forecasts, creating large unexpected surpluses.
4. **`Staff_Count` (11.66%):** Serves as an operational proxy for kitchen throughput and commercial scale.

### 5. Methodological Limitations of Feature Importance

> [!IMPORTANT]
> **Causation vs. Correlation:** Feature importance indicates how useful a feature was to the trained model's predictive decisions; it does **not** establish a causal relationship.

- **Impurity Bias:** MDI feature importance can favor continuous numerical variables (`Meals_Prepared`, `Staff_Count`) over one-hot binary flags because continuous features offer more candidate split points.
- **Correlated Splitting:** When features are correlated (e.g., `Customers_Forecast` and `Meals_Prepared`), the ensemble splits importance across them, which can lower individual MDI scores for collinear features.
- **Visual Evidence:** Diagnostic plot exported at `ai-engine/plots/feature_importance.png` and full ranking table logged in `ai-engine/evaluation/feature_importance.csv`.
