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
+-----------------------------------+-----------------------------------+
                                    |
                                    | Validated Dictionary
                                    v
+-----------------------------------------------------------------------+
|                    Prediction Service Bridge                          |
|           (backend/app/services/prediction_service.py)                |
|                                                                       |
|  * Dispatches to: ai-engine/prediction/predict.py                     |
|  * Contextual Action Engine: Generates redistribution advice          |
+-----------------------------------+-----------------------------------+
                                    |
                                    | Preprocessed Array
                                    v
+-----------------------------------------------------------------------+
|                  CIBUS-AI Trained ML Engine                           |
|                      (ai-engine/models/)                              |
|                                                                       |
|  * ColumnTransformer (food_surplus_preprocessor.pkl)                  |
|  * RandomForestRegressor (food_surplus_model.pkl: depth=15, n=200)    |
+-----------------------------------+-----------------------------------+
                                    |
                                    | Output: float >= 0.0
                                    v
+-----------------------------------------------------------------------+
|                      Structured JSON Response                         |
|  { "predicted_surplus_meals": 230.38, "status": "success", ... }      |
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

---

## 4. Error Handling Matrix

| Failure Condition | HTTP Status | Response Schema | Rationale |
| :--- | :---: | :--- | :--- |
| Missing required parameter | `422` | Validation Error JSON | Incomplete operational profile cannot produce reliable forecast. |
| Negative meal or customer count | `422` | Validation Error JSON | Violates physical reality constraints. |
| Rating out of range ($<1.0$ or $>5.0$) | `422` | Validation Error JSON | Out-of-bounds restaurant rating. |
| Presence of `Meals_Sold` | `422` | Data Leakage Violation JSON | Post-service outcome cannot enter pre-service prediction. |
| Model files missing or unreadable | `503` | Service Unavailable JSON | Server artifact path or storage error. |
| Unhandled runtime error | `500` | Internal Server Error JSON | Safe sanitized message preventing stack trace leakage. |

---

## 5. Verification & Testing

The backend is verified through an automated test suite located at `backend/tests/test_prediction_api.py`:
- **Test 1:** Health endpoint readiness and artifact loading.
- **Test 2:** API root metadata and navigation.
- **Test 3:** Standard valid operational prediction execution.
- **Test 4:** Missing required field handling.
- **Test 5:** Negative numerical input handling.
- **Test 6:** Out-of-bounds rating rejection.
- **Test 7:** Invalid categorical enumeration handling.
- **Test 8:** Strict `Meals_Sold` data leakage prevention.
- **Test 9:** Complete response schema and metadata verification.
- **Test 10:** Model info endpoint evaluation metrics retrieval.

All 10 tests execute deterministically with 100% pass rate.

---

## 6. Current Boundaries & Limitations
- **Stateless Inference:** The backend does not persist predictions to an external SQL/NoSQL database at this stage.
- **Zero Retraining:** The backend strictly consumes the trained model; online learning or automatic continuous retraining is intentionally avoided to preserve reproducibility.
- **Future Scope:** Full-stack React client dashboard, NGO profile registration, geospatial Google Maps routing, and volunteer push notifications will interface with this API in subsequent development phases.
