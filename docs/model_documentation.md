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
1. **Non-Linear Interactions:** Captures complex multi-feature interactions (e.g., Stormy weather $\times$ Banquet format) without manual feature engineering.
2. **Robustness Against Overfitting:** Ensemble averaging over randomized bootstrap subsamples reduces overall model variance.
3. **Handling High-Dimensional Encoded Features:** Natively splits across the 25 transformed one-hot encoded operational variables.
4. **Interpretability via Feature Importance:** Calculates Mean Decrease in Impurity (MDI) to identify key drivers of food surplus.

---

## 3. Preprocessing, Train / Test Partitioning & Leakage Prevention

### Validation & Train-Test Strategy
- **Partitioning Ratio:** 80% Training ($N = 6,400$), 20% Testing ($N = 1,600$)
- **Reproducibility:** Deterministic pseudo-random seed `random_state=42`.
- **Transformation Isolation:** 
  - The `ColumnTransformer` (OneHotEncoder for categorical features + passthrough for numerical features) is fitted **strictly on $X_{\text{train}}$**.
  - $X_{\text{test}}$ is transformed using the pre-fitted transformer without re-fitting.
  - The fitted preprocessor is serialized to `ai-engine/models/preprocessor.joblib`.

### Reusability in Production Inference
In real-world inference (`predict.py`), individual JSON/dictionary inputs are passed into `transform_single_input()`. Using the persisted preprocessor guarantees that categorical one-hot vectors always map to the identical 25-feature dimensional ordering expected by the trained model.

---

## 4. Planned Evaluation Metrics

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
> Stating that an $R^2$ score of $0.88$ represents "88% accuracy" is mathematically incorrect. $R^2$ is the Coefficient of Determination (explained variance). Classification accuracy applies only to discrete class labels.

---

## 6. Model Performance Results
*No models have been trained at this stage. Quantitative performance results, error metrics, and residual distribution charts will be populated upon completion of model training and validation execution.*
