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
- **Test Performance:**
  - **MAE:** `14.2939 meals`
  - **RMSE:** `20.5429 meals`
  - **$R^2$ Score:** `0.9549`

### Iteration 2: Hyperparameter Optimization & Refined Model
- **Refinement Motivation:** Investigate whether constraining tree depth, tuning split minimums, and sub-sampling features optimizes variance control on unseen data.
- **Hyperparameter Search Space Considered:**
  - `n_estimators`: `[100, 150, 200]`
  - `max_depth`: `[None, 15, 25]`
  - `min_samples_split`: `[2, 4, 8]`
  - `min_samples_leaf`: `[1, 2, 4]`
  - `max_features`: `['sqrt', 0.8, 1.0]`
- **Cross-Validation Strategy:** 3-Fold Cross-Validation strictly on the training partition ($X_{\text{train}}$) using `neg_root_mean_squared_error` scoring. The test partition ($X_{\text{test}}$) was never touched during parameter selection.
- **Best Selected Hyperparameters:**
  - `n_estimators`: `200`
  - `max_depth`: `15`
  - `min_samples_split`: `4`
  - `min_samples_leaf`: `1`
  - `max_features`: `0.8`
  - *Best 3-Fold CV RMSE:* `20.9391 meals`
- **Test Performance (Evaluated on held-out test set $N = 1,600$):**
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

### Engineering Takeaway:
- Both the baseline and refined models perform with high consistency ($R^2 > 0.954$), indicating that the operational feature space possesses strong predictive power.
- The refined model with `max_depth=15` and `max_features=0.8` provides a more regularized, memory-efficient tree ensemble (40.4 MB vs 57.9 MB) while maintaining virtually identical predictive fidelity.
- All baseline and final artifacts are preserved in `ai-engine/models/` and logged in `ai-engine/evaluation/model_comparison.json`.
