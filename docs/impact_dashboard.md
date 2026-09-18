# CIBUS-AI Impact Dashboard & Operational Analytics

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *"Predict. Connect. Nourish."*  
**Document:** Impact Dashboard & Analytics System  
**Date:** September 2026  

---

## 1. Objective & Architectural Scope

The **Impact Dashboard & Analytics Module** provides real-time visibility into the operational performance of the CIBUS-AI ecosystem. It aggregates redistribution records generated across active sessions and exposes factual Machine Learning model evaluation statistics.

### Clear Academic & Operational Boundaries
- **Real Application Telemetry:** Aggregates operational totals from actual prediction, NGO matching, and route optimization workflows recorded within the system.
- **Factual ML Performance:** Exposes active test-set metrics (MAE = `14.58`, RMSE = `20.69`, $R^2$ = `0.9543`) loaded directly from `ai-engine/evaluation/final_results.json`.
- **Honest Academic Terminology:**
  - *"Predicted Surplus"* (not "Actual Food Waste")
  - *"Planned Allocation"* (not "Delivered Food")
  - *"Matched Partner NGOs"* (not "NGOs Served")
  - *"Estimated Route Distance"* (not "Actual Delivery Distance")
  - *"Planned Redistribution"* (not "Confirmed Physical Delivery")

> [!IMPORTANT]
> **No Fake Data / No False Accuracy Claims:**
> - The dashboard does not fabricate inflated statistics.
> - $R^2$ is strictly documented as the **proportion of target variance explained relative to the baseline** and is **NEVER** labeled as a classification accuracy percentage.

---

## 2. Activity Data Model & Local Persistence

### Demonstration Activity Store
For prototyping and development, activity records are persisted in a lightweight, local JSON file:
`backend/data/activity_history.json`

### Record Schema:
```json
{
  "activity_id": "ACT_20260918_103000_001",
  "timestamp": "2026-09-18T10:30:00Z",
  "source_name": "Guindy Central Catering Facility",
  "predicted_surplus_meals": 230.38,
  "allocated_meals": 230.38,
  "matched_ngo_count": 2,
  "route_stop_count": 2,
  "route_distance_km": 5.88,
  "status": "planned",
  "notes": "Demonstration baseline itinerary recorded during system verification."
}
```

### Data Consistency Invariants:
1. **Allocation Upper Bound:** $\text{Allocated Meals} \le \text{Predicted Surplus Meals} + 0.01$.
2. **Physical Positivity:** All meal counts, stop counts, and distances must be non-negative ($\ge 0$).
3. **Allocation Rate Percentage:**
   $$\text{Allocation Rate} = \begin{cases} \left(\frac{\text{Total Allocated Meals}}{\text{Total Predicted Surplus Meals}}\right) \times 100\% & \text{if } \text{Total Predicted} > 0 \\ 0.0\% & \text{otherwise} \end{cases}$$

---

## 3. Backend Analytics Service Architecture

Located at [`backend/app/services/analytics_service.py`](file:///k:/CiBus-Ai%20R/backend/app/services/analytics_service.py):

- `load_activity_history() -> List[Dict[str, Any]]`: Reads records from `activity_history.json` safely.
- `save_activity_record(record: Dict[str, Any]) -> Dict[str, Any]`: Validates bounds, timestamps with UTC ISO string, and appends to local storage.
- `get_model_performance() -> Dict[str, Any]`: Dynamically loads metrics from `ai-engine/evaluation/final_results.json` without recalculating or retraining.
- `get_dashboard_summary() -> Dict[str, Any]`: Aggregates operational totals across all activities and pairs with ML metrics.
- `get_recent_activities(limit: int = 10) -> List[Dict[str, Any]]`: Returns recent activities ordered descending by timestamp.

---

## 4. API Endpoints

### 1. `GET /api/dashboard/summary`
Returns aggregate operational impact statistics and ML model evaluation metrics.

**Sample Response:**
```json
{
  "summary": {
    "total_predicted_surplus_meals": 230.38,
    "total_allocated_meals": 230.38,
    "allocation_rate_pct": 100.0,
    "total_matched_ngos": 2,
    "total_route_stops": 2,
    "total_route_distance_km": 5.88,
    "total_activities": 1,
    "data_source_mode": "Local demonstration activity store (JSON)"
  },
  "model_performance": {
    "model_name": "RandomForestRegressor",
    "mae": 14.5793,
    "rmse": 20.6869,
    "r2": 0.9543,
    "evaluation_dataset": "Held-out unseen test set (N=1,600 records)",
    "note": "R² represents the proportion of explained variance and is not a classification accuracy percentage."
  },
  "status": "success",
  "message": "Dashboard operational metrics and ML model performance retrieved successfully.",
  "disclaimer": "Demonstration Dashboard: Metrics summarize planned redistribution workflows and estimated Haversine transit distances. Confirmed real-world physical delivery requires on-ground verification."
}
```

### 2. `GET /api/dashboard/recent?limit=10`
Returns recent activity records sorted newest first. Enforces $1 \le \text{limit} \le 100$.

### 3. `POST /api/dashboard/activity`
Records a newly planned workflow itinerary into the persistent log.

---

## 5. Frontend User Interface

Located at [`frontend/src/components/ImpactDashboard.jsx`](file:///k:/CiBus-Ai%20R/frontend/src/components/ImpactDashboard.jsx):

1. **Redistribution Impact Summary:** 6 responsive metric cards:
   - Predicted Surplus (meals)
   - Planned Allocation (meals)
   - Allocation Rate (%)
   - Matched Partner NGOs
   - Est. Route Distance (km)
   - Redistribution Plans Recorded
2. **ML Model Performance Panel:**
   - Highlights MAE (`14.58 meals`), RMSE (`20.69 meals`), and $R^2$ (`0.9543`) with contextual definitions.
3. **Recent Activity Table:**
   - Interactive table detailing timestamps, source facilities, quantities, stops, and status.
4. **Header Navigation:**
   - Quick navigation links across Dashboard, Predictor, Redistribution, and Routing.

---

## 6. Verification and Testing

Verified via automated test suites:
- **Backend Unit Tests:** `backend/tests/test_analytics_dashboard.py` (12 tests) verifying empty history, single/multi aggregation, allocation bounds, negative value rejections, limit validation, ordering, and REST responses.
- **Total Backend Tests:** 43 tests passing with 100% success rate.
- **Frontend Verification:** `frontend/tests/frontend_test.cjs` (18 tests) passing with 100% success rate.
