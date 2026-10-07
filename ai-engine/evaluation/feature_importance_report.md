# CIBUS-AI: Multi-Parameter Feature Importance & Interpretability Audit Report

**Target Variable:** `Surplus_Meals`  
**Leakage Audit:** `Meals_Sold` strictly excluded  
**Algorithm:** `RandomForestRegressor`  
**Test Partition:** Held-out test set ($N = 1,600$, 20% of 8,000 samples)  

---

## 1. Verified Operational Parameters (All 9 Features)

| Rank | Feature | Used by Model | RF Importance (MDI) | Permutation Importance (RMSE $\Delta$, meals) | Operational Interpretation |
| :---: | :--- | :---: | :---: | :---: | :--- |
| 1 | `Meals_Prepared` | **YES** | `0.6087` | `+365.0260` | Primary supply factor: Total food volume cooked directly caps maximum possible surplus. |
| 2 | `Customers_Forecast` | **YES** | `0.2794` | `+172.9879` | Primary demand factor: Baseline diner footfall expectation driving meal consumption. |
| 3 | `Staff_Count` | **YES** | `0.0501` | `+18.4530` | Operational throughput: Adequate staffing roster maintains table turns and service throughput. |
| 4 | `Weather` | **YES** | `0.0187` | `+14.9373` | Environmental shock: Severe rain and storms suppress walk-in customer turnout and elevate surplus. |
| 5 | `Event_Type` | **YES** | `0.0123` | `+10.1895` | Dining format: Buffets/banquets increase per-capita intake; corporate events reduce consumption. |
| 6 | `Special_Event` | **YES** | `0.0100` | `+9.3787` | Occasion demand surge: Themed VIP celebrations increase attendance and reduce surplus. |
| 7 | `Avg_Rating` | **YES** | `0.0090` | `+2.6142` | Establishment reputation: High ratings increase customer reservation conversion and footfall. |
| 8 | `Day` | **YES** | `0.0074` | `+3.3679` | Weekly cyclical pattern: Weekend leisure dining peaks increase consumption; Mondays slow down. |
| 9 | `Festival` | **YES** | `0.0044` | `+1.9014` | Cultural holiday surge: Festive celebrations increase dining group sizes and meal demand. |

---

## 2. Key Mathematical & Domain Findings

1. **Primary Demand and Supply Anchors:**
   - `Meals_Prepared` and `Customers_Forecast` represent the fundamental boundary variables of surplus ($S \approx M - D$). Together they account for the majority of tree variance reduction.

2. **Operational Capacity Factor:**
   - `Staff_Count` contributes meaningful predictive importance by governing kitchen and dining service throughput. Adequate staffing prevents bottlenecks and service walkouts, allowing realized consumption to reach full potential.

3. **Contextual Footfall & Consumption Modifiers:**
   - `Weather`, `Event_Type`, `Special_Event`, `Avg_Rating`, `Day`, and `Festival` all have positive MDI importance and positive held-out permutation importance.
   - Each feature provides realistic, non-zero predictive power without artificial constant coefficients.

4. **Zero Data Leakage:**
   - `Meals_Sold` is verified absent from all training, evaluation, and inference pipelines.