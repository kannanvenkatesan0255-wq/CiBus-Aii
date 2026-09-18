# CIBUS-AI Backend Integration Architecture & API Design

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *"Predict. Connect. Nourish."*  
**Document:** Backend Integration Architecture  
**Date:** September 2026  

---

## 1. Backend Objective
The primary objective of the CIBUS-AI backend layer is to establish a secure, decoupled, and high-throughput RESTful interface that exposes the trained Machine Learning prediction engine to external systems. 

Key architectural principles:
- **Zero Retraining Overhead:** The backend operates purely in inference mode, dynamically loading serialized model artifacts (`food_surplus_model.pkl`) and preprocessing transformers (`food_surplus_preprocessor.pkl`).
- **Separation of Concerns:** ML model logic remains isolated in `ai-engine/`, while HTTP routing, serialization, schema validation, and error translation reside in `backend/app/`.
- **Defensive API Design:** Prevents post-service data leakage (`Meals_Sold`) and validates physical input boundaries prior to reaching the ML pipeline.

---

## 2. System Architecture Diagram

```
+-----------------------------------------------------------------------+
|                         External Clients                              |
|          Web Frontend (React/Vite) / Mobile App / POS Terminal        |
+-----------------------------------+-----------------------------------+
                                    |
                                    | HTTP Requests (JSON)
                                    v
+-----------------------------------------------------------------------+
|                    FastAPI Application Layer                          |
|                       (backend/app/main.py)                           |
|                                                                       |
|  * CORS Middleware (localhost:3000, 5173, 8000)                       |
|  * OpenAPI / Swagger Documentation (/docs, /redoc)                    |
|  * Global Health Endpoint (GET /health)                               |
+-----------------------------------+-----------------------------------+
                                    |
                                    | Routed Requests
                                    v
+-----------------------------------------------------------------------+
|                        API Router Layer                               |
|                  (backend/app/routes/prediction.py)                   |
|                                                                       |
|  * POST /api/predict       --> Food Surplus Forecasting               |
|  * POST /api/match-ngos    --> Heuristic NGO Matching & Allocation     |
|  * GET  /api/model-info    --> Active ML Metadata & Metrics           |
+-----------------------------------+-----------------------------------+
                                    |
                                    | Pydantic Validation
                                    v
+-----------------------------------------------------------------------+
|                     Data Validation & Schemas                         |
|                     (backend/app/schemas.py)                          |
|                                                                       |
|  * Enforces: Customers_Forecast >= 0, Meals_Prepared >= 0             |
|  * Enforces: 1.0 <= Avg_Rating <= 5.0, Staff_Count >= 1               |
|  * Sanitizes: Day, Weather, Festival, Event_Type                      |
|  * Strict Rule: Rejects 'Meals_Sold' (Zero Data Leakage)              |
|  * NGO Matching: predicted_surplus >= 0, lat/lon in valid ranges      |
+-----------------------------------+-----------------------------------+
                                    |
                                    | Validated Payload
                                    v
+-----------------------------------------------------------------------+
|                        Service Bridges                                |
|                                                                       |
|  * PredictionService (backend/app/services/prediction_service.py)     |
|      -> Calls ML Engine (ai-engine/prediction/predict.py)             |
|  * NGOMatchingService (backend/app/services/ngo_matching_service.py)  |
|      -> Evaluates Synthetic NGO Dataset (backend/data/ngos.csv)       |
|      -> Computes Haversine distance, suitability score, and capacity  |
+-----------------------------------+-----------------------------------+
                                    |
                                    | Forecast / Matching Matrix
                                    v
+-----------------------------------------------------------------------+
|                      Structured JSON Response                         |
|  Prediction: { "predicted_surplus_meals": 230.38, ... }               |
|  NGO Match:  { "matches": [...], "unallocated_meals": 0.0, ... }      |
+-----------------------------------------------------------------------+
```

---

## 3. Detailed Request-Response Flows

### A. Health Check Flow (`GET /health`)
1. Client issues `GET /health`.
2. Router invokes `PredictionService.check_artifacts()`.
3. Service verifies that both `food_surplus_model.pkl` and `food_surplus_preprocessor.pkl` are loadable from disk.
4. Returns `200 OK` with JSON payload:
   ```json
   {
     "status": "healthy",
     "model_loaded": true,
     "preprocessor_loaded": true,
     "version": "1.0.0"
   }
   ```

### B. Prediction Flow (`POST /api/predict`)
1. Client issues `POST /api/predict` with operational data.
2. Pydantic parser evaluates field types, categories, and numerical bounds.
3. If `Meals_Sold` is detected, request is immediately rejected with HTTP `422 Unprocessable Entity`.
4. Validated payload is passed to `PredictionService.predict()`.
5. `predict_surplus()` in `ai-engine/prediction/predict.py` executes:
   - One-hot encoding and pass-through column transformation (9 raw $\rightarrow$ 25 features).
   - Scikit-learn Random Forest inference (`model.predict()`).
   - Boundary clipping: $0.0 \le \hat{y} \le \text{Meals\_Prepared}$.
6. Service layer attaches operational guidance based on surplus volume:
   - $< 15$ meals: Low surplus (standard inventory).
   - $15 - 60$ meals: Moderate surplus (local shelter notification).
   - $> 60$ meals: High surplus (activate regional NGO redistribution dispatch).
7. Returns `200 OK` with `PredictionResponse`.

### C. NGO Matching & Allocation Flow (`POST /api/match-ngos`)
1. Client issues `POST /api/match-ngos` with `predicted_surplus_meals`, optional `food_type`, and optional source coordinates (`source_latitude`, `source_longitude`).
2. Pydantic validates `predicted_surplus_meals >= 0`, latitude within $[-90, 90]$, and longitude within $[-180, 180]$.
3. `NGOMatchingService.match_and_allocate()` queries `backend/data/ngos.csv`.
4. Filters organizations by availability (`Available` vs `Unavailable`) and food type compatibility (`Both` matches all; specific types match identical or compatible types).
5. Computes transparent composite suitability score:
   $$\text{Score} = 0.35 S_{\text{avail}} + 0.25 S_{\text{dist}} + 0.20 S_{\text{compat}} + 0.20 S_{\text{cap}}$$
6. Distributes surplus sequentially across top-ranked NGOs without exceeding individual capacities:
   $$\text{Allocated}_i = \min(\text{Surplus}_{\text{remaining}}, \text{Capacity}_i)$$
   Ensuring: $\sum \text{Allocated}_i \le \text{Predicted Surplus}$.
7. Returns `200 OK` with `NGOMatchResponse` including ranked recipients, allocated portions, distances, match scores, and remaining unallocated surplus.

### D. Route Optimization Flow (`POST /api/optimize-route`)
1. Client issues `POST /api/optimize-route` with `source` (name, latitude, longitude) and `ngos` (list of matched recipient centers with allocated meal counts).
2. Pydantic validates non-empty list ($N \ge 1$), geographic coordinate boundaries, non-negative meal quantities, and enforces unique `ngo_id` constraints.
3. `RouteOptimizationService.optimize_route()` computes an $(N+1) \times (N+1)$ pairwise Haversine distance matrix.
4. Traverses the graph from the food source using a greedy **Nearest-Neighbor** heuristic ($O(N^2)$), sequencing stops by minimal marginal transit distance.
5. Calculates step-by-step segment distances and validates distance/meal conservation invariants.
6. Returns `200 OK` with `RouteOptimizeResponse` containing ordered waypoints, segment distances, total route distance, total meals, and pairwise distance matrix.

### E. Impact Dashboard & Analytics Flow (`GET /api/dashboard/summary`, `GET /api/dashboard/recent`, `POST /api/dashboard/activity`)
1. **Summary Retrieval (`GET /api/dashboard/summary`):**
   - Reads recorded activities from `backend/data/activity_history.json`.
   - Sums predicted surplus, allocated meals, NGO matches, route stops, and transit distances.
   - Computes allocation rate percentage ($\frac{\text{Allocated}}{\text{Predicted}} \times 100\%$).
   - Loads factual evaluation metrics directly from `ai-engine/evaluation/final_results.json` (MAE: `14.58`, RMSE: `20.69`, $R^2$: `0.9543`).
   - Returns structured `DashboardResponse`.
2. **Recent Activities Retrieval (`GET /api/dashboard/recent`):**
   - Validates `1 <= limit <= 100`.
   - Returns activity records ordered descending by timestamp.
3. **Workflow Activity Recording (`POST /api/dashboard/activity`):**
   - Validates that `allocated_meals <= predicted_surplus_meals + 0.01` and non-negativity.
   - Generates unique ID (`ACT_YYYYMMDD_HHMMSS_XXX`), UTC ISO timestamp, and appends to persistent storage.

---

## 4. Error Handling Matrix

| Failure Condition | HTTP Status | Response Schema | Rationale |
| :--- | :---: | :--- | :--- |
| Missing required parameter | `422` | Validation Error JSON | Incomplete operational profile cannot produce reliable forecast. |
| Negative meal or customer count | `422` | Validation Error JSON | Violates physical reality constraints. |
| Rating out of range ($<1.0$ or $>5.0$) | `422` | Validation Error JSON | Out-of-bounds restaurant rating. |
| Presence of `Meals_Sold` | `422` | Data Leakage Violation JSON | Post-service outcome cannot enter pre-service prediction. |
| Negative surplus in NGO matching | `422` | Validation Error JSON | Surplus meals must be non-negative. |
| Invalid latitude/longitude coordinates | `422` | Validation Error JSON | Coordinates out of valid geographic range. |
| Empty NGO list in route planning | `422` | Validation Error JSON | Route optimization requires at least one recipient stop. |
| Duplicate NGO IDs in route request | `422` | Validation Error JSON | Each route stop must have a unique identifier. |
| Allocated meals exceed surplus in activity | `422` | Validation Error JSON | Inconsistent activity data violates physical conservation. |
| Invalid activity query limit ($<1$ or $>100$) | `422` | Validation Error JSON | Query limit out of acceptable operational bounds. |
| Model files missing or unreadable | `503` | Service Unavailable JSON | Server artifact path or storage error. |
| Unhandled runtime error | `500` | Internal Server Error JSON | Safe sanitized message preventing stack trace leakage. |

---

## 5. Verification & Testing

The backend is verified through automated test suites:
- `backend/tests/test_prediction_api.py` (10 tests): Health endpoint, prediction inference, schema boundary validation, data leakage prevention, model metadata.
- `backend/tests/test_ngo_matching.py` (10 tests): NGO capacity constraints, zero surplus, multi-NGO distribution, dietary filtering, invalid inputs.
- `backend/tests/test_route_optimization.py` (10 tests): Single/multiple NGO routing, nearest-neighbor sequencing, Haversine accuracy, distance/meal sum invariants, error rejections.
- `backend/tests/test_analytics_dashboard.py` (12 tests): Empty activity history, aggregation accuracy, allocation rate %, bounds validation, ML evaluation loading, and REST endpoints.
- `backend/tests/test_e2e_workflow.py` (1 test): Complete end-to-end integration passing real Random Forest prediction outputs directly into the NGO matching service.

All 43 test cases execute deterministically with 100% pass rate.

---

## 6. Current Boundaries & Limitations
- **Local Activity Store:** Activity logs reside in a demonstration JSON file (`backend/data/activity_history.json`) suitable for prototype evaluation.
- **Rule-Based Matching & Routing:** NGO matching and route planning are purely deterministic algorithms; they do not utilize machine learning.
- **Straight-Line Haversine Approximation:** Route distances represent straight-line coordinates rather than road turn-by-turn routing.
- **Synthetic NGO Dataset:** NGO profiles are synthetic demo representations for academic prototyping.
- **Zero Retraining:** The backend strictly consumes the trained model; online learning or automatic continuous retraining is intentionally avoided to preserve reproducibility.

---

## 7. Frontend Integration Flow

The React/Vite web application (`frontend/`) interacts seamlessly with the FastAPI backend:
1. **Heartbeat Health Monitoring:** The `HealthStatus.jsx` component queries `GET /health` periodically (30s) to indicate backend and ML model availability to dining operators.
2. **Prediction Submission:** The `PredictionForm.jsx` component collects 9 operational parameters, validates domain bounds on the client, and sends `POST /api/predict`.
3. **CORS Configuration:** The backend CORS middleware permits communication from Vite development origins (`http://localhost:5173` and `http://127.0.0.1:5173`).
4. **Result Rendering:** The `ResultCard.jsx` component displays the forecast, model metadata, and logistics recommendations returned by the backend.
5. **Redistribution Planning:** The `NGOMatchingSection.jsx` component consumes the predicted surplus from the ResultCard, presents optional dietary and location filters, and queries `POST /api/match-ngos` to display matched recipient organizations and capacity allocations.
6. **Dispatch Routing:** The `RoutePlanningSection.jsx` component consumes the matched recipient centers, sends `POST /api/optimize-route`, and renders a sequenced delivery timeline with distance breakdowns.
7. **Impact Analytics & Activity Logging:** The `ImpactDashboard.jsx` component loads `GET /api/dashboard/summary` and `GET /api/dashboard/recent`, and allows users to persist planned itineraries via `POST /api/dashboard/activity`.


