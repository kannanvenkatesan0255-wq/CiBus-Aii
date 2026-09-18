# Project Presentation Deck Content (15 Slides)

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *Predict. Connect. Nourish.*  
**Format:** Slide Deck Specification for Evaluator Presentation  

---

### SLIDE 1: Title Slide
- **Header:** CIBUS-AI
- **Subtitle:** AI-Based Food Surplus Prediction and Redistribution Network
- **Tagline:** *Predict. Connect. Nourish.*
- **Academic Context:** Machine Learning Project-Based Learning (PBL)
- **Team Details:** `[STUDENT NAMES & REGISTER NUMBERS]`
- **Mentor:** `[FACULTY MENTOR NAME]`, `[DEPARTMENT]`, `[INSTITUTION]`

---

### SLIDE 2: Problem Statement & Motivation
- **The Challenge:** Commercial food operations generate tons of edible food waste daily due to footfall uncertainty.
- **The Bottleneck:** Surplus is typically quantified *after* business hours, resulting in late NGO notification and spoilage.
- **The Core Need:** An automated system capable of *pre-service prediction* coupled with *algorithmic redistribution logistics*.

---

### SLIDE 3: Driving Question & Technical Objectives
- **Driving Question:** *"How can machine learning be leveraged to predict commercial food surplus and optimize redistribution planning before waste occurs?"*
- **Technical Objectives:**
  - Build a high-accuracy regression model ($R^2 > 0.90$) to forecast surplus meals.
  - Implement rule-based matching to allocate meals among nearby NGOs based on capacity.
  - Formulate a nearest-neighbor route optimizer using the Haversine distance metric.
  - Develop an interactive web application and environmental impact dashboard.

---

### SLIDE 4: Dataset & Schema Overview
- **Dataset Source:** Synthetic dataset (`food_surplus.csv`) generated for reproducible research.
- **Volume:** 8,000 observations, 10 feature attributes.
- **Inputs (9 Features):** `Day`, `Weather`, `Customers_Forecast`, `Meals_Prepared`, `Festival`, `Event_Type`, `Staff_Count`, `Avg_Rating`, `Special_Event`.
- **Target:** `Surplus_Meals` (Continuous non-negative integer).
- **Integrity Rule:** `Meals_Sold` strictly excluded to eliminate target leakage ($Meals\_Prepared - Meals\_Sold = Surplus$).

---

### SLIDE 5: Data Preprocessing Pipeline
- **Categorical Encoding:** `OneHotEncoder(handle_unknown='ignore')` applied to `Day`, `Weather`, `Event_Type`, `Festival`, `Special_Event`.
- **Numerical Scaling:** `StandardScaler()` applied to `Customers_Forecast`, `Meals_Prepared`, `Staff_Count`, `Avg_Rating`.
- **Pipeline Architecture:** Scikit-Learn `ColumnTransformer` serialized to `food_surplus_preprocessor.pkl`.
- **Validation Partition:** 80% Training (6,400 rows) / 20% Testing (1,600 rows) with fixed seed (`random_state=42`).

---

### SLIDE 6: Machine Learning Model Selection
- **Algorithm:** `RandomForestRegressor` (Ensemble of Bagged Decision Trees).
- **Selection Rationale:**
  - Robust handling of non-linear multi-factor interactions (e.g., Weather $\times$ Event).
  - High resistance to overfitting via feature subsampling and tree aggregation.
  - Direct interpretability through tree Gini impurity and mean decrease in impurity.
- **Artifact:** Model serialized to `food_surplus_model.pkl` via Joblib.

---

### SLIDE 7: Model Development & Refinement
- **Baseline Model:** Default parameters ($n\_estimators=100$, unconstrained depth).
- **Refinement Strategy:** Grid exploration of `max_depth` (10, 15, 20) and `min_samples_split` (2, 5, 10).
- **Selected Hyperparameters:**
  - `n_estimators`: 100
  - `max_depth`: 15 (controls variance and prevents memorization)
  - `random_state`: 42

---

### SLIDE 8: Final Evaluation & Empirical Metrics
| Metric | Final Model Value | Interpretation |
| :--- | :--- | :--- |
| **Mean Absolute Error (MAE)** | **14.5793 meals** | Average prediction deviation is ~14.6 meals. |
| **Root Mean Squared Error (RMSE)** | **20.6869 meals** | Penalizes large variance; demonstrates tight error spread. |
| **Coefficient of Determination ($R^2$)** | **0.9543** | Explains 95.43% of total variance in surplus meals. |

> *Note: $R^2$ is an explained variance metric, not a classification accuracy percentage.*

---

### SLIDE 9: Feature Importance Analysis
- **Top Feature Contributions:**
  1. `Meals_Prepared` (~48.2% weight)
  2. `Customers_Forecast` (~26.7% weight)
  3. `Day` (Day-of-week demand variations, ~8.5% weight)
  4. `Festival` / `Event_Type` (~6.8% weight)
  5. `Weather` & `Staff_Count` (~9.8% weight)
- **Key Insight:** While preparation volume sets the baseline, footfall forecasts and event flags drive the surplus divergence.

---

### SLIDE 10: End-to-End System Architecture
- **Three-Tier Architecture:**
  - **Frontend:** React 19 + Tailwind CSS (Responsive UI, Interactive Step Wizard, SVG Route Plotting).
  - **Backend:** FastAPI (Pydantic validation, Async REST APIs, CORS security, Activity logging).
  - **ML Engine:** Preprocessing & Random Forest inference pipeline.
- **Persistence:** Local JSON activity storage (`activity_log.json`).

---

### SLIDE 11: NGO Matching & Meal Allocation
- **Recipient Database:** Synthetic directory of local NGOs with geographic coordinates, meal requirements, and operating hours.
- **Matching Rules:**
  - Radius filter ($d \le 15\text{ km}$).
  - Operational status check (active status).
  - Food type compatibility (Cooked / Packaged).
- **Greedy Allocation:** Matches predicted surplus against NGO daily capacity until surplus is fully assigned.

---

### SLIDE 12: Route Optimization & Heuristics
- **Distance Formula:** Spherical Haversine calculation:
  $$d = 2r \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos \phi_1 \cos \phi_2 \sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$
- **Optimization Strategy:** Greedy Nearest Neighbor heuristic constructs a multi-stop dispatch sequence starting from the food donor location.
- **Output:** Ordered waypoint sequence, total route distance (km), and estimated travel time (mins).

---

### SLIDE 13: Impact Dashboard & Environmental Analytics
- **Sustainability Metrics:**
  - **Surplus Meals Planned & Saved**
  - **Greenhouse Gas Emissions Offset:** Calculated at $2.5\text{ kg } CO_2\text{e}$ per rescued meal.
  - **Embedded Water Conserved:** Calculated at $1,000\text{ liters}$ per rescued meal.
- **Activity Log:** Real-time audit trail of all historical redistribution sessions.

---

### SLIDE 14: System Boundaries & Limitations
- **Synthetic Data:** Model is evaluated on synthetic data; real-world commercial distributions may vary.
- **Heuristic Routing:** Utilizes straight-line Haversine math and nearest-neighbor ordering rather than live road turn-by-turn navigation or real-time traffic data.
- **Planning vs. Delivery:** Provides a software-based redistribution *plan*; does not execute physical dispatch or confirm live delivery.

---

### SLIDE 15: Conclusion & Future Scope
- **Conclusion:** CIBUS-AI successfully demonstrates that machine learning and algorithmic logistics can transform reactive food disposal into proactive community nourishment.
- **Future Roadmap:**
  - Integrate real-world restaurant POS & inventory feeds.
  - Connect with live Google Maps Directions & traffic APIs.
  - Mobile application for real-time driver delivery confirmation.
  - Cloud migration with PostgreSQL database and JWT authentication.
