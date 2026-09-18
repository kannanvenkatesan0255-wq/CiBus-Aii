# Model Documentation: CIBUS-AI Predictive Engine

---

## 1. Problem Formulation: Why Regression?

The CIBUS-AI forecasting task is mathematically formulated as **Supervised Regression**.

### Justification:
- The target variable `Surplus_Meals` is a continuous quantitative count ($\mathbb{R}_{\ge 0}$ or $\mathbb{Z}_{\ge 0}$) representing the exact or estimated volume of leftover meal portions.
- A classification approach (e.g., "Surplus" vs "No Surplus" or "Low" vs "High") is inadequate for logistics planning. NGO dispatchers and food collection vans require specific capacity information (e.g., whether to dispatch a 20-meal bike carrier or a 250-meal refrigerated van).
- Regression provides a direct quantitative estimation $\hat{y} \in [0, \infty)$ allowing granular distribution logistics.

---

## 2. Model Selection: Random Forest Regressor

### Algorithm Overview
Random Forest is an ensemble learning method based on **Bagging (Bootstrap Aggregating)** that constructs a multitude of uncorrelated Decision Trees during training and outputs the mean prediction ($\frac{1}{B}\sum_{b=1}^{B} T_b(x)$) of individual trees.

### Why Random Forest for Food Surplus Forecasting?
1. **Non-Linear Interactions:** Demand dynamics involve complex non-linear combinations (e.g., heavy rain during a buffet event on a Friday creates a drastically different surplus profile than heavy rain on a regular Monday lunch). Random Forest natively captures multi-way feature interactions without requiring explicit polynomial feature transformations.
2. **Robustness Against Overfitting:** By aggregating diverse trees trained on randomized bootstrap subsamples and randomized feature subsets (the random subspace method), Random Forest exhibits lower variance compared to individual deep decision trees.
3. **Handling Mixed Feature Types:** Seamlessly accommodates both continuous metrics (`Meals_Prepared`, `Customers_Forecast`, `Avg_Rating`) and encoded categorical features (`Day`, `Weather`, `Event_Type`).
4. **Interpretability via Feature Importance:** Calculates Gini impurity reduction or Mean Decrease in Impurity (MDI), showing domain stakeholders which operational factors most heavily drive food waste.
5. **No Strict Assumptions of Linearity/Normality:** Unlike linear models, it requires no assumptions regarding homoscedasticity or Gaussian distribution of errors.

---

## 3. Planned Train / Test Validation Strategy

### Data Partitioning
- **Split Ratio:** 80% Training Set, 20% Testing Set
- **Stratification / Random Seed:** Fixed `random_state=42` to ensure deterministic, reproducible splits for PBL defense.
- **Cross-Validation:** 5-Fold Cross-Validation planned during model training on the training partition to verify generalization performance across different data folds before evaluating on the held-out test partition.

### Baseline Comparison
- A **Multiple Linear Regression** baseline will be trained alongside Random Forest to establish a formal benchmark, demonstrating the empirical advantage of non-linear tree ensembles over simple linear hyperplanes.

---

## 4. Planned Evaluation Metrics

Regression models cannot be evaluated using classification metrics such as Accuracy, Precision, Recall, or F1-Score. The following standard regression metrics will be computed:

### 1. Mean Absolute Error (MAE)
$$\text{MAE} = \frac{1}{n} \sum_{i=1}^{n} |y_i - \hat{y}_i|$$
- **Interpretation:** The average magnitude of prediction errors in the original physical units (meals). If $\text{MAE} = 6.5$, predictions are off by an average of $\approx 6.5$ meals.
- **Advantage:** Highly intuitive for non-technical stakeholders and robust to outliers.

### 2. Root Mean Squared Error (RMSE)
$$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2}$$
- **Interpretation:** Penalizes larger prediction errors more severely due to squaring.
- **Advantage:** Useful when a large underestimation or overestimation of surplus carries high logistical penalties (e.g., van overflow or spoiled food).

### 3. Coefficient of Determination ($R^2$ Score)
$$R^2 = 1 - \frac{\sum_{i=1}^{n} (y_i - \hat{y}_i)^2}{\sum_{i=1}^{n} (y_i - \bar{y})^2} = 1 - \frac{\text{SS}_{\text{res}}}{\text{SS}_{\text{tot}}}$$
- **Interpretation:** The proportion of variance in `Surplus_Meals` explained by the input features relative to a naive mean baseline ($\bar{y}$).
- An $R^2 = 1.0$ represents a perfect fit; $R^2 = 0.0$ indicates performance identical to predicting the average surplus every time.

---

## 5. Critical Distinction: $R^2$ is NOT Classification Accuracy

> [!WARNING]
> **Common Student / PBL Pitfall:** Stating that an $R^2$ score of $0.88$ represents "88% accuracy" is mathematically incorrect.

- **Classification Accuracy** measures the percentage of discrete labels correctly assigned: $\frac{\text{Correct Predictions}}{\text{Total Samples}} \in [0\%, 100\%]$.
- In continuous regression, the probability of predicting the exact real-valued continuous number down to infinitesimal decimals is virtually zero ($P(\hat{y} = y) \approx 0$).
- **$R^2$** measures the **variance explained**, comparing the model's residual sum of squares against the total sum of squares. An $R^2$ can even be negative if the model performs worse than the simple horizontal line $\bar{y}$.
- In project presentations and reports, $R^2$ must be reported as the *Coefficient of Determination* or *Explained Variance*, while error magnitudes must be reported via MAE and RMSE.

---

## 6. Model Performance Results
*No models have been trained at this stage. Quantitative performance results, error metrics, and residual distribution charts will be populated upon completion of model training and validation execution.*
