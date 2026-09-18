# CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network

> **Tagline:** *Predict. Connect. Nourish.*

---

## 1. Problem Statement
Every day, commercial food establishments (cafeterias, restaurants, banquet halls, and institutional caterers) face high variance in customer footfall, event attendance, and consumption patterns. As a result, massive quantities of freshly prepared, high-quality food are discarded as surplus at the end of service cycles. Concurrently, local shelter homes, community centers, and non-governmental organizations (NGOs) struggle to source nutritious meals reliably. 

A primary reason for food waste is the lack of advance visibility: food generators typically realize they have surplus only after service closes, leaving insufficient time to safely coordinate preservation, logistics, and distribution before the food spoils.

---

## 2. Project Objective
The objective of **CIBUS-AI** is to develop an intelligent Machine Learning system that predicts the quantity of surplus food meals available at a food-generating establishment *before* final consumption and sales are finalized. 

By forecasting surplus in advance based on operational parameters and external context, the system provides actionable foresight to enable proactive coordination with redistribution networks and NGOs.

---

## 3. Machine Learning Formulation
- **Learning Paradigm:** Supervised Learning
- **Task Type:** Regression (predicting continuous numerical quantities of surplus meals)
- **Target Variable ($y$):** `Surplus_Meals` (Count of surplus portions remaining post-service)

---

## 4. Planned Input Features ($X$)
To strictly prevent **data leakage**, only pre-service operational and environmental factors available prior to sales completion are used as model inputs:

| Feature Name | Type | Description |
| :--- | :--- | :--- |
| `Day` | Categorical | Day of the week (e.g., Monday, Friday, Sunday) |
| `Weather` | Categorical | Environmental conditions (e.g., Sunny, Rainy, Stormy) |
| `Customers_Forecast` | Integer | Anticipated footfall/expected visitor count |
| `Meals_Prepared` | Integer | Total meal units scheduled/cooked for the shift |
| `Festival` | Binary / Categorical | Indicator of public holidays or festive seasons |
| `Event_Type` | Categorical | Context of operation (e.g., Regular, Buffet, Corporate, Banquet) |
| `Staff_Count` | Integer | Active kitchen and service workforce on duty |
| `Avg_Rating` | Float | Historical customer satisfaction / service quality score |
| `Special_Event` | Binary (0 / 1) | Indicator of unpredicted or one-off catering events |

> **Critical Data Leakage Rule:** `Meals_Sold` is strictly excluded from input features ($X$). Because $\text{Surplus\_Meals} \approx \text{Meals\_Prepared} - \text{Meals\_Sold}$, incorporating `Meals_Sold` as an input would constitute target leakage and render real-time pre-service prediction invalid.

---

## 5. Planned Machine Learning Algorithm
- **Primary Model:** Random Forest Regressor (`scikit-learn`)
  - Handles non-linear feature interactions (e.g., weather $\times$ event type).
  - Robust against overfitting through ensemble bagging of decision trees.
  - Provides native feature importance interpretability for PBL study.
- **Baseline Model:** Linear Regression (for benchmark comparison).

---

## 6. Technology Stack
- **Programming Language:** Python 3.10+
- **Data Manipulation & Math:** Pandas, NumPy
- **Machine Learning Library:** Scikit-Learn
- **Model Serialization:** Joblib
- **Visualization & Diagnostics:** Matplotlib, Seaborn

---

## 7. Current Development Phase
- **Phase:** **Phase 7 – Final Model Evaluation Completed**
- **Status:** Conducted full test-set evaluation ($N=1,600$) on `food_surplus_model.pkl`. Generated `ai-engine/plots/actual_vs_predicted.png`, `ai-engine/plots/residual_analysis.png`, `ai-engine/evaluation/predictions.csv`, and `ai-engine/evaluation/final_results.json`.
- **Model Type:** Supervised Regression (`RandomForestRegressor`, `n_estimators=200`, `max_depth=15`, `max_features=0.8`).
- **Final Evaluation Metrics:**
  - $\text{MAE} = 14.5793$ meals
  - $\text{RMSE} = 20.6869$ meals
  - $R^2 = 0.9543$ (Explained Variance)
  - Mean Residual Bias: $-0.2729$ meals (Near-zero systematic error)
  - 82.81% of test predictions within $\pm 25$ meals.

---

## 8. Future Modules *(Planned Future Work)*
The following modules represent subsequent milestones:
- [x] **Data Pipeline Execution:** Synthetic dataset generation ($N=8000$) with domain-realistic variance and validation checks.
- [x] **Data Preprocessing & Encoding Pipeline:** Train-test splitting ($80/20$), leakage-safe ColumnTransformer fitting, and artifact serialization.
- [x] **Baseline Model Training:** Random Forest baseline training ($n=100$) and baseline benchmark logging.
- [x] **Final Model Training & Hyperparameter Tuning:** 3-Fold Cross-Validation parameter tuning, test evaluation, and baseline comparison.
- [x] **Feature Importance Analysis:** Mean Decrease in Impurity (MDI) extraction, ranking tables, and diagnostic plot.
- [x] **Evaluation & Diagnostic Plotting:** True vs. Predicted residual analysis, MAE, RMSE, and $R^2$ evaluation plots.
- [ ] **Standalone Prediction Interface:** Pre-service CLI and batch inference script.
- [ ] **NGO Matching Engine:** Distance- and capacity-aware matching algorithm (*Future Milestone*).
- [ ] **Dynamic Route Optimization:** Multi-stop pickup and drop route planning (*Future Milestone*).
- [ ] **Volunteer Allocation Engine:** Task dispatch system (*Future Milestone*).
- [ ] **Web Application & Dashboard:** Interactive frontend/backend interface with Google Maps integration (*Future Milestone*).

---

## 9. Project Directory Structure
```
CIBUS-AI/
│
├── ai-engine/
│   ├── dataset/
│   │   ├── generate_dataset.py
│   │   └── food_surplus.csv
│   │
│   ├── preprocessing/
│   │   └── preprocess.py
│   │
│   ├── training/
│   │   ├── train_baseline.py
│   │   ├── train_model.py
│   │   └── feature_importance.py
│   │
│   ├── models/
│   │   ├── food_surplus_model.pkl
│   │   └── label_encoders.pkl
│   │
│   ├── prediction/
│   │   └── predict.py
│   │
│   ├── evaluation/
│   │   └── evaluate_model.py
│   │
│   ├── plots/
│   │   ├── actual_vs_predicted.png
│   │   └── feature_importance.png
│   │
│   ├── requirements.txt
│   └── README.md
│
├── docs/
│   ├── project_overview.md
│   ├── dataset_description.md
│   ├── model_documentation.md
│   └── weekly_progress.md
│
├── .gitignore
└── README.md
```
