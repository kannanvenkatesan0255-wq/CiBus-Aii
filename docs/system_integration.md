# CIBUS-AI System Integration & Location Visualization Architecture
**File:** `docs/system_integration.md`  
**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *“Predict. Connect. Nourish.”*  

---

## 1. System Integration Overview

CIBUS-AI connects real-time food surplus machine learning forecasting with a multi-criteria heuristic redistribution pipeline, nearest-neighbor graph route planning, lightweight SVG spatial mapping, and persistent prototype telemetry.

```
+-------------------------------------------------------------------------+
|                              USER (Client)                              |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                  Vite / React Frontend Single-Page App                  |
|  - WorkflowStepper (IDLE -> PREDICTED -> MATCHED -> ROUTED -> RECORDED) |
|  - ImpactDashboard (Telemetry KPI Cards + ML Performance)               |
|  - PredictionForm & ResultCard (9 Operational Features)                 |
|  - NGOMatchingSection (Dietary & Capacity Filtering)                    |
|  - RoutePlanningSection & RouteMapVisualization (SVG Plane)             |
+-------------------------------------------------------------------------+
                                     |
                                     | REST (JSON / CORS)
                                     v
+-------------------------------------------------------------------------+
|                          FastAPI Backend Server                         |
+-------------------------------------------------------------------------+
      |                   |                     |                    |
      v                   v                     v                    v
+---------------+  +---------------+  +-------------------+  +---------------+
| /api/predict  |  |/api/match-ngos|  |/api/optimize-route|  |/api/dashboard |
+---------------+  +---------------+  +-------------------+  +---------------+
      |                   |                     |                    |
      v                   v                     v                    v
+---------------+  +---------------+  +-------------------+  +---------------+
| ML Model      |  | Synthetic NGO |  | Nearest-Neighbor  |  | Activity JSON |
| (RandomForest |  | Directory     |  | Haversine Distance|  | Store & Eval  |
|  max_depth=15)|  | (15 records)  |  | Graph Sequencer   |  | Metrics Reader|
+---------------+  +---------------+  +-------------------+  +---------------+
```

---

## 2. End-to-End Workflow Stages

### Stage 1: Pre-Service Surplus Prediction
- **Input:** 9 pre-service operational features (`Day`, `Weather`, `Customers_Forecast`, `Meals_Prepared`, `Festival`, `Event_Type`, `Staff_Count`, `Avg_Rating`, `Special_Event`).
- **Data Leakage Rule:** `Meals_Sold` and `Surplus_Meals` are strictly rejected as inputs.
- **Inference:** The frozen `RandomForestRegressor` (`n_estimators=100`, `max_depth=15`) executes in $<10\text{ ms}$.
- **Output:** Forecasted excess meals (e.g. `230.4 meals`).

### Stage 2: Recipient NGO Matching & Capacity Allocation
- **Input:** `predicted_surplus_meals`, `food_type` (`Vegetarian`, `Non-Vegetarian`, `Both`), optional source coordinates, `max_matches`.
- **Heuristic:** Multi-criteria scoring evaluating dietary match, capacity adequacy, and geographic proximity.
- **Physical Invariants:**
  $$\sum \text{allocated\_meals} \le \text{predicted\_surplus\_meals}$$
  $$\text{allocated\_meals}_i \le \text{capacity\_meals}_i \quad \forall i$$

### Stage 3: Nearest-Neighbor Route Optimization
- **Input:** Food source facility origin (`name`, `latitude`, `longitude`) + list of matched NGO recipients.
- **Sequencing:** Greedy nearest-neighbor TSP heuristic starting from origin and picking the closest unvisited stop via pairwise Haversine great-circle distances:
  $$d = 2R \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos\phi_1 \cos\phi_2 \sin^2\left(\frac{\Delta \lambda}{2}\right)} \right)$$
- **Output:** Sequenced waypoints, segment-by-segment distances, total route distance ($\text{km}$), and pairwise distance matrix.

### Stage 4: Location & Route SVG Visualization
- **Deterministic Coordinate Normalization:** Projects geographic coordinates into SVG viewport without external map APIs.
- **Visual Features:**
  - Origin Marker: Purple glowing coordinate anchor with facility metadata.
  - Recipient Stops: Cyan/teal numbered sequence badges ($1, 2, 3\dots$) with meal drop indicators.
  - Segment Vectors: Directional arrows, glow filter, and segment distance badges ($\text{km}$).
  - Orientation: Compass rose and coordinate bounds overlay.

### Stage 5: Activity Logging & Impact Telemetry
- **Persistence:** Local JSON activity ledger (`backend/data/activity_history.json`).
- **Telemetry Aggregation:** Total planned redistribution events, total allocated meals, total route distance, and allocation rate percentage.
- **Verified ML Panel:** Dynamic retrieval of test metrics ($R^2 = 0.9543$, $\text{MAE} = 14.58$, $\text{RMSE} = 20.69$).

---

## 3. Deterministic Coordinate Normalization Algorithm

To display geographic coordinates on a 2D SVG canvas without external tile servers or mapping SDKs, the system normalizes latitude and longitude into Cartesian pixel coordinates $(x, y)$:

```javascript
// Given viewport dimensions W = 700, H = 420, Padding P = 65:
minLat = min(lats); maxLat = max(lats); latSpan = maxLat - minLat;
minLon = min(lons); maxLon = max(lons); lonSpan = maxLon - minLon;

// Normalize X (Longitude increases Eastwards -> Right):
x = (lonSpan <= 0.00001) ? W / 2 : P + ((lon - minLon) / lonSpan) * (W - 2 * P);

// Normalize Y (Latitude increases Northwards -> Upwards; SVG Y increases Downwards):
y = (latSpan <= 0.00001) ? H / 2 : H - (P + ((lat - minLat) / latSpan) * (H - 2 * P));
```

### Edge Case Handling:
- If all points share identical coordinates ($\text{latSpan} \approx 0$ or $\text{lonSpan} \approx 0$), nodes are positioned at viewport center ($W/2, H/2$) without division by zero.
- Generous padding ($65\text{px}$) ensures markers, outer glowing rings, and text labels remain fully visible within SVG boundaries.

---

## 4. Academic Integrity & Terminology Guardrails

| Module | Approved Academic Terminology | Prohibited Unverified Claims |
| :--- | :--- | :--- |
| **ML Engine** | Surplus Forecast, $R^2 = 0.9543$ | "95.4% Accuracy", "Zero Waste Guarantee" |
| **NGO Matching** | Candidate Allocation, Capacity Matching | "Guaranteed Delivery", "Live NGO Confirmation" |
| **Route Planner** | Heuristic Itinerary, Haversine Estimation | "Optimal Turn-by-Turn Route", "Live Traffic Routing" |
| **Visualization** | Relative Coordinate Projection | "Interactive Google Map", "Live GPS Tracking" |
| **Telemetry** | Planned Telemetry, Activity Ledger | "Physical Food Rescued", "Delivered Meals" |

---

## 5. Security & Boundary Checks
- **No External Secrets:** Zero external API keys or credentials required.
- **Input Validation:** Pydantic validators on backend + HTML5/React bounds checking on frontend (Latitude: $[-90, +90]$, Longitude: $[-180, +180]$).
- **Duplicate Prevention:** Activity recording button disables upon submission to prevent duplicate telemetry records.
- **Fail-Safe Graceful Degradation:** Upstream failures preserve entered form data and display actionable alerts without exposing internal stack traces.
