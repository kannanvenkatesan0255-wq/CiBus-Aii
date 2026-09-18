# Dataset Description: CIBUS-AI Food Surplus Dataset

---

## 1. Planned Dataset Purpose
The `food_surplus.csv` dataset is designed to provide supervised training instances representing daily service shifts across commercial cafeterias, institutional food providers, and catering services. Each record captures the operational context, environmental conditions, and scheduling decisions known *prior to or during meal preparation*, mapped to the observed resulting meal surplus.

The primary objective is to allow the model to learn the underlying non-linear relationship between pre-service operational indicators and the volume of edible meals left unconsumed.

---

## 2. Expected Columns and Data Types

| Column Name | Data Type | Role | Example Values |
| :--- | :--- | :--- | :--- |
| `Day` | Categorical (string) | Input Feature | `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`, `Sunday` |
| `Weather` | Categorical (string) | Input Feature | `Sunny`, `Rainy`, `Cloudy`, `Stormy` |
| `Customers_Forecast` | Numeric (integer) | Input Feature | `120`, `250`, `480` |
| `Meals_Prepared` | Numeric (integer) | Input Feature | `150`, `300`, `500` |
| `Festival` | Categorical / Binary | Input Feature | `Yes`, `No` (or `None`, `Diwali`, `Eid`, `Christmas`) |
| `Event_Type` | Categorical (string) | Input Feature | `Regular`, `Buffet`, `Corporate`, `Banquet` |
| `Staff_Count` | Numeric (integer) | Input Feature | `8`, `15`, `25` |
| `Avg_Rating` | Numeric (float) | Input Feature | `3.8`, `4.2`, `4.9` |
| `Special_Event` | Binary (integer) | Input Feature | `0`, `1` |
| `Surplus_Meals` | Numeric (integer/float) | **Target Variable ($y$)** | `15`, `42`, `85` |

*(Note: In raw logs, `Meals_Sold` or `Actual_Customers` may exist for ground-truth calculation, but they are strictly sequestered from model training features).*

---

## 3. Feature Descriptions

### Input Features ($X$)
1. **`Day`**: Day of the week. Captures recurring cyclical demand patterns (e.g., lower cafeteria attendance on Fridays/weekends, higher regular attendance mid-week).
2. **`Weather`**: Environmental weather forecast. Severe rain or storms often drastically reduce outdoor footfall, leaving excess prepared food.
3. **`Customers_Forecast`**: Expected footfall based on table reservations, ticket sales, or historical attendance estimations made prior to meal cooking.
4. **`Meals_Prepared`**: Total number of meal portions batch-cooked or pre-portioned by the kitchen staff for the service window.
5. **`Festival`**: Indicator denoting if the day falls on or near a major holiday/festival, which often alters dining habits and attendance.
6. **`Event_Type`**: Format of food service. Buffets and banquets typically produce higher variance in food preparation buffers compared to fixed-portion à la carte or regular cafeteria services.
7. **`Staff_Count`**: Kitchen and floor staff deployed. Acts as a proxy for operational scale and kitchen capacity.
8. **`Avg_Rating`**: Historical establishment rating (1.0 to 5.0). Lower satisfaction can lead to customer churn or lower than projected consumption.
9. **`Special_Event`**: Binary flag indicating unscheduled or special occasions (e.g., campus workshops, corporate parties, unexpected guest speaker events).

### Target Variable ($y$)
- **`Surplus_Meals`**: The actual physical count of wholesome, edible meal portions remaining at the conclusion of service that were not consumed or sold.

---

## 4. Prediction-Time Feature Rule & Data Leakage Prevention

### The Fundamental Rule
> **Any feature used during model training and inference must be strictly available at the moment the prediction is requested (i.e., *before* or *during* meal preparation, well before service concludes).**

### Why `Meals_Sold` Must NOT Be Used as an Input Feature

In food service operations, the actual surplus is mathematically defined post-service as:
$$\text{Surplus\_Meals} = \text{Meals\_Prepared} - \text{Meals\_Sold}$$

If `Meals_Sold` is included as a feature in the training matrix $X$:
1. **Direct Target Leakage:** The learning algorithm would trivially learn the arithmetic formula ($\text{Surplus} = \text{Meals\_Prepared} - \text{Meals\_Sold}$) rather than learning the real-world demand patterns, variance, and behavioral drivers.
2. **Inference Impossibility:** In a real deployment, `Meals_Sold` is only known **after** all customer transactions have concluded and service has shut down. If the ML model required `Meals_Sold` to make a prediction, it could only run at the end of the day—completely defeating the objective of generating advance alerts for proactive NGO redistribution logistics.
3. **PBL Examination Flaw:** Utilizing post-facto features is one of the most critical conceptual errors in machine learning system design. CIBUS-AI explicitly enforces the exclusion of `Meals_Sold` from all feature vectors.
