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

## 4. How the Synthetic Data Was Generated

The dataset generation script (`ai-engine/dataset/generate_dataset.py`) utilizes a parameterized behavioral synthesis model:
1. **Operational Scaling:** `Customers_Forecast` is drawn based on day-of-week and event type distributions.
2. **Buffer Modeling:** `Meals_Prepared` is calculated from forecast with domain-realistic safety buffers (Buffets/Banquets maintain +15% to +38% safety buffer, Corporate maintains tighter +6% to +18% margins).
3. **Compound Surplus Formation:** `Surplus_Meals` is computed without using post-facto sales, incorporating:
   - *Baseline buffer surplus:* Expected excess between preparation and planned demand.
   - *Weather disruptions:* Severe storms (+20% to +35%) and heavy rain (+8% to +18%) that diminish footfall.
   - *Event format structural waste:* Continuous full display requirements in buffets and banquets.
   - *Rating penalty:* Dissatisfaction factors when historical rating falls below 3.8.
   - *Multi-variable interaction terms:* Compound effects (e.g., Stormy weather $\times$ Banquet format).
   - *Controlled stochastic Gaussian noise:* $\epsilon \sim \mathcal{N}(0, 6.5^2)$ to model natural real-world unobserved behavioral entropy.
4. **Physical Bounds:** Strictly bounded such that $\text{Surplus\_Meals} \ge 0.0$ and $\text{Surplus\_Meals} \le 0.85 \times \text{Meals\_Prepared}$.

---

## 5. Why Synthetic Data is Used
1. **Privacy & Commercial Sensitivity:** Commercial food providers rarely publish granular shift-by-shift surplus and waste metrics due to brand perception and liability concerns.
2. **Controlled Experimental Design:** Enables testing non-linear regression response under known statistical interaction conditions.
3. **Rapid Academic Prototyping:** Provides a robust, leak-free benchmark dataset for PBL development without reliance on incomplete third-party web scrapers.

---

## 6. Critical Data-Leakage Prevention Rule

### The `Meals_Sold` Exclusion Rule
In catering accounting, actual leftover is defined post-event as:
$$\text{Surplus\_Meals} = \text{Meals\_Prepared} - \text{Meals\_Sold}$$

**Why `Meals_Sold` is Strictly Omitted:**
1. **Target Leakage:** Including `Meals_Sold` reduces the machine learning problem to trivial arithmetic, preventing the model from discovering real behavioral interactions.
2. **Temporal Invalidity:** `Meals_Sold` is only known **after** service closure. A model requiring `Meals_Sold` cannot make pre-service advance predictions needed to coordinate timely NGO food redistribution.

---

## 7. Limitations of Synthetic Data
- **Distributional Assumptions:** Underlying parameters assume stationary seasonal habits; sudden macro-economic shifts or supply chain shortages are not modeled.
- **Micro-climate Granularity:** Weather is modeled categorically rather than through localized continuous meteorological measurements (e.g., millimeter precipitation, humidity).
- **Homogeneous Menu Profile:** All meal portions are treated as standardized aggregate meal units rather than itemized per-dish perishability profiles.
