# CIBUS-AI System Architecture

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *Predict. Connect. Nourish.*  
**Document:** Final System Architecture Specification  

---

## 1. High-Level Architecture Overview

CIBUS-AI is architected as a modular, decoupled decision-support and planning prototype consisting of three primary layers:
1. **Frontend Presentation Layer:** A responsive single-page web application built with React 19 and Tailwind CSS, providing intuitive interfaces for surplus prediction, NGO matching, pickup routing, and impact analytics.
2. **Backend Application Layer:** A high-performance RESTful API service built with FastAPI, handling request validation, orchestration, algorithm execution, and local JSON-based activity persistence.
3. **AI/ML Engine Layer:** An offline-trained machine learning inference pipeline utilizing scikit-learn (`RandomForestRegressor`), specialized preprocessing pipelines, and mathematical optimization modules.

```
                         +-----------------------------------+
                         |         RESTAURANT / USER         |
                         +-----------------------------------+
                                           |
                                           v
                         +-----------------------------------+
                         |      REACT FRONTEND (VITE/SPA)    |
                         |   - PredictionForm                |
                         |   - NgoMatchingSection            |
                         |   - RoutePlanningSection          |
                         |   - ImpactDashboard               |
                         |   - WorkflowTracker & Navbar      |
                         +-----------------------------------+
                                           |  (HTTP / JSON REST)
                                           v
                         +-----------------------------------+
                         |          FASTAPI BACKEND          |
                         |  - CORS & Security Middleware     |
                         |  - Pydantic Schema Validation     |
                         |  - Activity Logger / Store        |
                         +-----------------------------------+
                             |             |             |
           +-----------------+             |             +-----------------+
           |                               |                               |
           v                               v                               v
+---------------------+         +---------------------+         +---------------------+
|   PREDICTION API    |         |   NGO MATCHING API  |         |    DASHBOARD API    |
|  POST /api/predict  |         |  POST /api/match-ngo|         |  GET /api/dashboard |
+---------------------+         +---------------------+         +---------------------+
           |                               |                               |
           v                               v                               v
+---------------------+         +---------------------+         +---------------------+
|  ML MODEL & PIPELINE|         |  NGO DATA & MATCHER |         |  ANALYTICS SERVICE  |
|  - Preprocessor.pkl |         |  - Synthetic NGOs   |         |  - Aggregations     |
|  - RandomForest.pkl |         |  - Capacity Rules   |         |  - Activity History |
+---------------------+         +---------------------+         +---------------------+
           |                               |
           +---------------+---------------+
                           |
                           v
           +---------------------------------+
           |     ROUTE OPTIMIZATION API      |
           |      POST /api/optimize-route   |
           +---------------------------------+
                           |
                           v
           +---------------------------------+
           |   HAVERSINE ROUTE OPTIMIZER     |
           |   - Pairwise Distance Matrix    |
           |   - Greedy Nearest Neighbor     |
           +---------------------------------+
                           |
                           v
           +---------------------------------+
           |     ACTIVITY RECORDING STORE    |
           |  backend/data/activity_log.json |
           +---------------------------------+
                           |
                           v
           +---------------------------------+
           |     AGGREGATED IMPACT STATS     |
           |  (Meals, CO2, Water Saved)      |
           +---------------------------------+
```

---

## 2. Component Specifications

### 2.1 Machine Learning Pipeline (`ai-engine/`)
- **Dataset:** `ai-engine/dataset/food_surplus.csv` (8,000 synthetic records, 10 feature columns).
- **Target Variable:** `Surplus_Meals` (Continuous non-negative integer).
- **Excluded Features:** `Meals_Sold` is strictly excluded from training and inference to prevent target leakage ($Meals\_Prepared - Meals\_Sold = Surplus\_Meals$).
- **Features Used (9 Inputs):**
  1. `Day` (Categorical: Monday–Sunday)
  2. `Weather` (Categorical: Sunny, Rainy, Cloudy, etc.)
  3. `Customers_Forecast` (Numerical integer)
  4. `Meals_Prepared` (Numerical integer)
  5. `Festival` (Categorical: 0 or 1 / Yes or No)
  6. `Event_Type` (Categorical: None, Corporate, Wedding, Birthday)
  7. `Staff_Count` (Numerical integer)
  8. `Avg_Rating` (Numerical float: 1.0 to 5.0)
  9. `Special_Event` (Categorical: 0 or 1 / Yes or No)
- **Artifacts:**
  - `ai-engine/models/food_surplus_preprocessor.pkl` (`ColumnTransformer` with `OneHotEncoder` and `StandardScaler`)
  - `ai-engine/models/food_surplus_model.pkl` (`RandomForestRegressor`, $n\_estimators=100$, $max\_depth=15$, $random\_state=42$)
- **Performance:** $R^2 = 0.9543$, $\text{MAE} = 14.58\text{ meals}$, $\text{RMSE} = 20.69\text{ meals}$.

### 2.2 Backend Service (`backend/`)
- **Framework:** FastAPI (Python 3.10+ ASGI framework).
- **Endpoints:**
  - `GET /api/health`: System health and status check.
  - `POST /api/predict`: ML surplus meal inference.
  - `POST /api/match-ngos`: Synthetic NGO filtering and meal capacity allocation.
  - `POST /api/optimize-route`: Haversine matrix computation and nearest-neighbor route ordering.
  - `GET /api/dashboard/summary`: Aggregate metrics (total meals, surplus, allocated, CO2 saved).
  - `GET /api/dashboard/recent-activity`: Chronological list of recorded planning sessions.
  - `POST /api/dashboard/record-activity`: Manual/automated session recording.
- **Data Persistence:** Lightweight local file store at `backend/data/activity_log.json` for reproducible prototype operation without requiring an external database server.

### 2.3 Frontend Application (`frontend/`)
- **Framework:** React 19 with Vite bundler.
- **State Management:** React Component State + Local Storage fallback for seamless single-page workflow orchestration.
- **UI System:** Modern responsive card-based layout, color-coded status badges, step-by-step interactive workflow wizard, SVG route trajectory visualization, and analytical metric counters.
- **Communication:** Axios-based HTTP client communicating with FastAPI backend via `VITE_API_URL` (default `http://localhost:8000`).

---

## 3. Data Flow & Sequential Workflow

The end-to-end planning cycle follows an 11-step deterministic sequence:
1. **Input Generation:** The donor enters operational parameters (e.g., meals prepared, weather, expected customers).
2. **Request Validation:** FastAPI receives input and validates data types and ranges via Pydantic (`PredictionInput`).
3. **ML Inference:** The input dictionary is transformed using the saved preprocessor and scored with `RandomForestRegressor`.
4. **Surplus Estimation:** Backend returns the predicted surplus meals count and estimated surplus percentage.
5. **Redistribution Initiation:** User transitions to the NGO matching phase; the predicted surplus is submitted to `/api/match-ngos`.
6. **Rule-Based Allocation:** Matching engine filters candidate NGOs by proximity, operating status, food type compatibility, and greedy capacity allocation.
7. **Route Request:** Matched NGOs and donor coordinates are forwarded to `/api/optimize-route`.
8. **Trajectory Optimization:** Optimizer computes Haversine distance matrix and solves the multi-stop route via nearest-neighbor heuristic.
9. **Visualization:** The optimized stop sequence, total estimated distance (km), and travel time (mins) are returned and plotted on the frontend route map.
10. **Session Persistence:** The complete session (prediction, allocation, route metrics) is committed to `activity_log.json`.
11. **Dashboard Aggregation:** The impact dashboard refreshes aggregate totals (total surplus planned, environmental offset metrics).

---

## 4. Key Architectural Boundaries & Distinctions

- **Prediction vs. Planning vs. Execution:** The system provides software-based *prediction* and *planning recommendations*. It does not perform physical food transport or real-world dispatch.
- **Distance Calculation:** All route metrics use spherical Haversine trigonometric calculations ($d = 2r \arcsin(\dots)$), not live turn-by-turn road navigation or traffic APIs.
- **Data Isolation:** All training and NGO recipient records are synthetically generated for academic demonstration and reproducible PBL assessment.
