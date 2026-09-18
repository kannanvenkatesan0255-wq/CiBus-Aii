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
| Model files missing or unreadable | `503` | Service Unavailable JSON | Server artifact path or storage error. |
| Unhandled runtime error | `500` | Internal Server Error JSON | Safe sanitized message preventing stack trace leakage. |

---

## 5. Verification & Testing

The backend is verified through automated test suites:
- `backend/tests/test_prediction_api.py` (10 tests): Health endpoint, prediction inference, schema boundary validation, data leakage prevention, model metadata.
- `backend/tests/test_ngo_matching.py` (10 tests): NGO capacity constraints, zero surplus, multi-NGO distribution, dietary filtering, invalid inputs.
- `backend/tests/test_e2e_workflow.py` (1 test): Complete end-to-end integration passing real Random Forest prediction outputs directly into the NGO matching service.

All 21 test cases execute deterministically with 100% pass rate.

---

## 6. Current Boundaries & Limitations
- **Stateless Inference:** The backend does not persist predictions or matching events to an external SQL/NoSQL database at this stage.
- **Rule-Based Matching:** NGO matching is purely deterministic and heuristic; it does not utilize machine learning.
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
