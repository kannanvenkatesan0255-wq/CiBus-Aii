# Prediction Engine Documentation: CIBUS-AI

---

## 1. Prediction Objective
The CIBUS-AI Prediction Engine provides a production-ready, reusable inference interface for forecasting the expected quantity of surplus food portions at commercial dining facilities prior to service closure.

By delivering pre-service estimates, the module enables automated redistribution workflows—such as pairing available food surplus with nearby shelter homes and non-governmental organizations (NGOs)—well ahead of food spoilage windows.

---

## 2. Input Features & Target Definition

### Input Features ($X \in \mathbb{R}^{9}$):
1. **`Day`** *(str)*: Day of the week (`Monday` to `Sunday`).
2. **`Weather`** *(str)*: Expected meteorological conditions (`Sunny`, `Cloudy`, `Rainy`, `Stormy`).
3. **`Customers_Forecast`** *(int)*: Anticipated diner headcount based on reservations/forecast ($\ge 0$).
4. **`Meals_Prepared`** *(int)*: Total meal portions batch-cooked by the kitchen ($\ge 0$).
5. **`Festival`** *(str)*: Festive occasion indicator (`No`, `Diwali`, `Eid`, `Christmas`, `New Year`).
6. **`Event_Type`** *(str)*: Service format (`Regular`, `Buffet`, `Corporate`, `Banquet`).
7. **`Staff_Count`** *(int)*: Total service and kitchen workforce deployed ($\ge 1$).
8. **`Avg_Rating`** *(float)*: Historical customer satisfaction rating ($1.00 \le \text{Rating} \le 5.00$).
9. **`Special_Event`** *(int / str)*: Binary indicator for unscheduled or high-profile events (`0`/`1` or `No`/`Yes`).

### Target Variable ($y$):
- **`Predicted_Surplus_Meals`** *(float)*: Continuous numeric estimate of edible meal portions expected to remain unconsumed post-service.

> [!IMPORTANT]
> **Zero Data Leakage Guarantee:** `Meals_Sold` is strictly prohibited from entering the inference pipeline. Passing `Meals_Sold` raises a defensive `ValueError` and terminates execution.

---

## 3. Preprocessing & Model Loading Architecture

```
User Input Payload (Dict / DataFrame)
              │
              ▼
    [Input Validation & Sanitization]
    - Rejects Meals_Sold (raises ValueError)
    - Verifies all 9 schema keys
    - Enforces physical bounds (Meals >= 0, Rating in [1.0, 5.0])
              │
              ▼
    [ColumnTransformer (preprocessor.pkl)]
    - Categorical: OneHotEncoder (20 columns, handle_unknown='ignore')
    - Numerical: Passthrough (5 columns, original meal counts)
              │
              ▼
    [Transformed Feature Vector (1 x 25)]
              │
              ▼
    [RandomForestRegressor (food_surplus_model.pkl)]
    - 200 Ensemble Trees (max_depth=15, max_features=0.8)
              │
              ▼
    [Post-Processing & Bounding]
    - Bounded to [0.0, Meals_Prepared]
              │
              ▼
    Predicted Surplus Meals (e.g. 41.14 meals)
```

---

## 4. Python API Usage

### Single-Record Inference:
```python
import sys
import os
sys.path.insert(0, os.path.abspath("ai-engine"))

from prediction.predict import predict_surplus

# Define pre-service operational payload
sample_payload = {
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

# Generate prediction
predicted_surplus = predict_surplus(sample_payload)
print(f"Predicted Surplus: {predicted_surplus} meals")
# Output: Predicted Surplus: 41.14 meals
```

### Batch DataFrame Inference:
```python
import pandas as pd
from prediction.predict import predict_surplus

batch_df = pd.DataFrame([
    {
        "Day": "Wednesday", "Weather": "Sunny", "Customers_Forecast": 250,
        "Meals_Prepared": 290, "Festival": "No", "Event_Type": "Regular",
        "Staff_Count": 14, "Avg_Rating": 4.2, "Special_Event": 0
    },
    {
        "Day": "Sunday", "Weather": "Stormy", "Customers_Forecast": 320,
        "Meals_Prepared": 420, "Festival": "No", "Event_Type": "Buffet",
        "Staff_Count": 18, "Avg_Rating": 3.9, "Special_Event": 1
    }
])

results = predict_surplus(batch_df)
print(f"Batch Predictions: {results}")
# Output: [33.79, 226.32]
```

---

## 5. Command-Line Interface (CLI) Usage

The prediction script can be executed directly from the terminal with command-line arguments:

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

### Formatted CLI Output:
```
=================================================================
      CIBUS-AI: FOOD SURPLUS PREDICTION SYSTEM
=================================================================

[Input Operational Parameters]
  * Day                 : Saturday
  * Weather             : Sunny
  * Customers_Forecast  : 350
  * Meals_Prepared      : 400
  * Festival            : No
  * Event_Type          : Regular
  * Staff_Count         : 12
  * Avg_Rating          : 4.3
  * Special_Event       : 0

-----------------------------------------------------------------
  >>> Predicted Surplus Meals: 41.14 meals <<<
-----------------------------------------------------------------
[Logistics Recommendation] Prepare redistribution dispatch for ~41 meal units.
=================================================================
```

---

## 6. Defensive Boundary Checks & Error Handling

| Scenario | Input Given | Error Handling Response |
| :--- | :--- | :--- |
| **Data Leakage** | `Meals_Sold = 310` | `ValueError: CRITICAL ERROR (Data Leakage Violation)` |
| **Missing Field** | Omitted `Meals_Prepared` | `ValueError: Missing required prediction fields: ['Meals_Prepared']` |
| **Negative Meals** | `Meals_Prepared = -50` | `ValueError: Meals_Prepared must be non-negative, got -50` |
| **Rating Exceeded** | `Avg_Rating = 5.8` | `ValueError: Avg_Rating must be between 1.0 and 5.0, got 5.8` |
| **Unknown Category** | `Weather = 'Tornado'` | Encoded as all-zeros via `handle_unknown='ignore'`, proceeds gracefully without crashing |

---

## 7. Operational Limitations
1. **Batch Forecast Timing:** Predictions apply to planned batch preparation windows prior to shift commencement; intra-shift kitchen replenishment adjustments require refreshed parameter calls.
2. **Model Horizon:** Continuous numerical surplus output reflects unit meal portions, but does not disaggregate nutritional macros or perishable shelf-life hours (to be addressed in subsequent logistics modules).
