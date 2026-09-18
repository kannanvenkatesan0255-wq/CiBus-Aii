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
- **Phase:** **Phase 8 – Reusable Prediction System Completed**
- **Status:** Implemented and validated real-time/batch prediction module in `ai-engine/prediction/predict.py` and automated test suite in `ai-engine/prediction/test_predict.py` (9 unit tests passing).
- **Inference Interfaces:** Python API (`predict_surplus()`) and Terminal CLI.
- **Data Leakage Guarantee:** `Meals_Sold` is strictly rejected during inference.

---

## 8. Making Predictions (Inference Interface)

### A. Python API
```python
from prediction.predict import predict_surplus

sample_event = {
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

surplus_estimate = predict_surplus(sample_event)
print(f"Predicted Surplus: {surplus_estimate} meals")
# Output: Predicted Surplus: 41.14 meals
```

### B. Command-Line Interface (CLI)
```bash
python ai-engine/prediction/predict.py \
  --day Saturday \
  --weather Sunny \
  --customers 350 \
  --meals 400 \
  --festival No \
  --event Regular \
  --staff 12 \
  --rating 4.3 \
  --special 0
```

---

## 9. Future Modules *(Planned Future Work)*
The following modules represent subsequent milestones:
- [x] **Data Pipeline Execution:** Synthetic dataset generation ($N=8000$) with domain-realistic variance and validation checks.
- [x] **Data Preprocessing & Encoding Pipeline:** Train-test splitting ($80/20$), leakage-safe ColumnTransformer fitting, and artifact serialization.
- [x] **Baseline Model Training:** Random Forest baseline training ($n=100$) and baseline benchmark logging.
- [x] **Final Model Training & Hyperparameter Tuning:** 3-Fold Cross-Validation parameter tuning, test evaluation, and baseline comparison.
- [x] **Feature Importance Analysis:** Mean Decrease in Impurity (MDI) extraction, ranking tables, and diagnostic plot.
- [x] **Evaluation & Diagnostic Plotting:** True vs. Predicted residual analysis, MAE, RMSE, and $R^2$ evaluation plots.
- [x] **Standalone Prediction Interface:** Pre-service CLI and batch inference script with defensive input validation.
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
