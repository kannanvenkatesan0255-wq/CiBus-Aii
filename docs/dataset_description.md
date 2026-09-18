# Dataset Description: CIBUS-AI Food Surplus Dataset

---

## 1. Dataset Overview & Purpose
The `food_surplus.csv` dataset provides structured supervised training records representing daily meal shifts across dining establishments, institutional canteens, and catering services. It models the non-linear dynamics governing operational demand variance and post-service food surplus.

- **File Location:** `ai-engine/dataset/food_surplus.csv`
- **Total Records ($N$):** Exactly **8,000** rows
- **Total Columns ($D$):** **10** columns (9 prediction-time input features + 1 continuous target variable)
- **Data Completeness:** 0 missing values, 0 duplicate records
- **Random Seed:** `42` (ensuring 100% deterministic reproducibility)

---

## 2. Column Schema & Data Types

| # | Column Name | Data Type | Feature Role | Valid Range / Categories | Description |
| :-: | :--- | :--- | :--- | :--- | :--- |
| 1 | `Day` | Categorical (string) | Input Feature ($X$) | `Monday` to `Sunday` | Day of the operational week |
| 2 | `Weather` | Categorical (string) | Input Feature ($X$) | `Sunny`, `Cloudy`, `Rainy`, `Stormy` | Environmental weather forecast for the service period |
| 3 | `Customers_Forecast` | Numeric (integer) | Input Feature ($X$) | $60 - 950$ | Anticipated diner attendance based on bookings/forecast |
| 4 | `Meals_Prepared` | Numeric (integer) | Input Feature ($X$) | $84 - 1,360$ | Total meal portions cooked/portioned in advance |
| 5 | `Festival` | Categorical (string) | Input Feature ($X$) | `No`, `Diwali`, `Eid`, `Christmas`, `New Year` | Major festive or holiday period indicator |
| 6 | `Event_Type` | Categorical (string) | Input Feature ($X$) | `Regular`, `Buffet`, `Corporate`, `Banquet` | Service format and operational context |
| 7 | `Staff_Count` | Numeric (integer) | Input Feature ($X$) | $5 - 48$ | Kitchen and service staff deployed on duty |
| 8 | `Avg_Rating` | Numeric (float) | Input Feature ($X$) | $2.51 - 5.00$ | Historical customer satisfaction/quality rating |
| 9 | `Special_Event` | Binary (integer) | Input Feature ($X$) | `0`, `1` | Indicator for unscheduled or high-profile events |
| 10 | `Surplus_Meals` | Numeric (float) | **Target Variable ($y$)** | $0.0 - 686.0$ | Number of edible meal portions left over after service |

---

## 3. Summary Statistics (Generated Dataset)

### Numerical Attributes ($N = 8,000$)
| Attribute | Mean | Std Dev | Min | 25% | 50% (Median) | 75% | Max |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `Customers_Forecast` | 418.29 | 210.49 | 60.00 | 241.00 | 410.00 | 576.00 | 950.00 |
| `Meals_Prepared` | 519.66 | 263.95 | 84.00 | 302.00 | 502.00 | 702.00 | 1360.00 |
| `Staff_Count` | 22.59 | 9.56 | 5.00 | 15.00 | 22.00 | 29.00 | 48.00 |
| `Avg_Rating` | 4.11 | 0.42 | 2.51 | 3.82 | 4.11 | 4.40 | 5.00 |
| `Special_Event` | 0.16 | 0.37 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| **`Surplus_Meals` (Target)** | **118.59** | **97.27** | **0.00** | **47.88** | **86.70** | **162.22** | **686.00** |

### Categorical Distributions
- **`Day`**: Thursday (1,225), Friday (1,189), Tuesday (1,168), Monday (1,127), Saturday (1,100), Wednesday (1,099), Sunday (1,092)
- **`Weather`**: Sunny (3,784), Cloudy (2,233), Rainy (1,421), Stormy (562)
- **`Festival`**: No (6,411), Diwali (485), Eid (398), Christmas (374), New Year (332)
- **`Event_Type`**: Regular (3,612), Buffet (2,244), Corporate (1,331), Banquet (813)

---

## 4. Preprocessing & Feature Transformation Pipeline

The data preprocessing engine is implemented in `ai-engine/preprocessing/preprocess.py`:

```
Raw CSV (8000 x 10)
        │
        ├── Step 1: Data Integrity & Leakage Validation (Verify 0 nulls, 0 dups, NO Meals_Sold)
        ├── Step 2: Feature / Target Isolation (X: 9 features, y: Surplus_Meals)
        ├── Step 3: Train-Test Partitioning (80% Train [6400], 20% Test [1600], seed=42)
        ├── Step 4: Fit ColumnTransformer ONLY on X_train
        │       ├── Categorical: OneHotEncoder (20 binary columns, handle_unknown='ignore')
        │       └── Numerical: Passthrough (5 columns, preserves physical meal counts)
        ├── Step 5: Transform X_train -> (6400 x 25), Transform X_test -> (1600 x 25)
        └── Step 6: Serialize Preprocessor -> ai-engine/models/preprocessor.joblib
```

### Transformed Feature Schema (25 Features):
1. `Day_Friday`, `Day_Monday`, `Day_Saturday`, `Day_Sunday`, `Day_Thursday`, `Day_Tuesday`, `Day_Wednesday` (7 columns)
2. `Weather_Cloudy`, `Weather_Rainy`, `Weather_Stormy`, `Weather_Sunny` (4 columns)
3. `Festival_Christmas`, `Festival_Diwali`, `Festival_Eid`, `Festival_New Year`, `Festival_No` (5 columns)
4. `Event_Type_Banquet`, `Event_Type_Buffet`, `Event_Type_Corporate`, `Event_Type_Regular` (4 columns)
5. `Customers_Forecast`, `Meals_Prepared`, `Staff_Count`, `Avg_Rating`, `Special_Event` (5 numeric columns)

---

## 5. Critical Data-Leakage Prevention Rules

1. **`Meals_Sold` Exclusion:** `Meals_Sold` is strictly omitted from the dataset and preprocessing pipeline.
2. **Train-First Preprocessing Fit:** Preprocessing encodings are fitted **exclusively on the training partition ($X_{\text{train}}$)**. The test set ($X_{\text{test}}$) and subsequent real-time inference inputs are only transformed using the pre-fitted transformer, ensuring zero data snooping from test samples into the training pipeline.
3. **Reusability in Prediction:** The exact fitted `ColumnTransformer` is persisted as `preprocessor.joblib` to guarantee identical feature dimension, category ordering, and handling of unseen values during live inference.
