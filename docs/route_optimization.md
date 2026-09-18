# CIBUS-AI Route Optimization & Pickup Planning Module

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *"Predict. Connect. Nourish."*  
**Document:** Route Optimization & Logistics Planning  
**Date:** September 2026  

---

## 1. Objective & Scope

The **Route Optimization & Pickup Planning Module** extends the CIBUS-AI ecosystem by translating forecasted surplus food allocations into an actionable, sequenced dispatch itinerary.

### Clear Academic & Architectural Distinction
- **Core ML Contribution:** Food surplus volume forecasting using Random Forest Regression on historical operational features.
- **Redistribution Layer:** Deterministic rule-based NGO matching and capacity allocation.
- **Logistics Layer (This Module):** Deterministic graph heuristic utilizing the **Haversine formula** and a greedy **Nearest-Neighbor (NN)** traversal algorithm.

> [!IMPORTANT]
> **No Machine Learning in Routing:** Route optimization is an algorithmic graph traversal problem, **NOT** an AI/ML model.
> **No External Map Dependencies:** The current system executes deterministically without external API dependencies (such as Google Maps API or Mapbox) using synthetic geographic coordinates.

---

## 2. Mathematical Formulation & Distance Calculation

### Great-Circle Haversine Formula
Because Earth is spherical, straight-line distance across geographic coordinates $(\phi_1, \lambda_1)$ and $(\phi_2, \lambda_2)$ is computed using the Haversine formula:

$$\Delta\phi = \phi_2 - \phi_1, \quad \Delta\lambda = \lambda_2 - \lambda_1$$

$$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)$$

$$c = 2 \cdot \text{atan2}\left(\sqrt{a}, \sqrt{1 - a}\right)$$

$$d = R \cdot c$$

Where:
- $\phi_1, \phi_2$ are latitudes in radians.
- $\lambda_1, \lambda_2$ are longitudes in radians.
- $R = 6,371.0 \text{ km}$ (mean radius of the Earth).
- $d$ is the great-circle transit distance in kilometers.

---

## 3. Route Optimization Algorithm: Greedy Nearest-Neighbor

The food delivery route is modeled as an open-path directed graph where:
- Node $0$: Food Donor / Dispatch Facility (Origin).
- Nodes $1 \dots N$: Matched recipient NGOs with allocated meal portions.
- Edge Weights $W(u, v)$: Pairwise Haversine distance between Node $u$ and Node $v$.

```
Food Source (Origin)
        │
        ├── Haversine Distance d(0, 1)
        ↓
  Stop 1 (NGO 1)
        │
        ├── Haversine Distance d(1, 2)
        ↓
  Stop 2 (NGO 2)
        │
        ├── Haversine Distance d(2, 3)
        ↓
  Stop 3 (NGO 3)
```

### Algorithm Pseudocode

```text
Algorithm: GreedyNearestNeighborRouting
Input: 
  source: (name, lat_0, lon_0)
  ngos: [(id_1, name_1, lat_1, lon_1, meals_1), ..., (id_N, name_N, lat_N, lon_N, meals_N)]
Output: 
  sequenced_route, route_summary

1. Initialize locations = [source, ngo_1, ngo_2, ..., ngo_N]
2. Compute (N+1) x (N+1) symmetric distance matrix M where M[i][j] = Haversine(loc_i, loc_j)
3. Set visited = {0}
4. Set current_node = 0
5. Set route = [ Stop(seq=0, type='source', dist_from_prev=0.0) ]
6. Set sequence = 1

7. While |visited| < (N + 1):
     Find unvisited index k in {1 ... N} that minimizes M[current_node][k]
     Append Stop(seq=sequence, type='ngo', ngo=locations[k], dist_from_prev=M[current_node][k]) to route
     Add k to visited
     Set current_node = k
     Set sequence = sequence + 1

8. Compute summary:
     total_distance_km = Sum(stop.dist_from_prev for stop in route)
     total_meals = Sum(stop.meals for stop in route if stop.type == 'ngo')
     number_of_stops = N

9. Return route, summary
```

### Complexity & Optimality Analysis
- **Time Complexity:** $O(N^2)$ where $N$ is the number of recipient stops. Constructing the distance matrix takes $O(N^2)$ and greedy selection takes $O(N^2)$.
- **Space Complexity:** $O(N^2)$ for the pairwise distance matrix.
- **Optimality Disclaimer:** Nearest-Neighbor is a greedy heuristic for the Traveling Salesman / Vehicle Routing Problem. It produces fast, practical sequences for small-to-medium recipient batches ($N \le 20$), but does not guarantee global TSP optimality.

---

## 4. API Specification

### Endpoint: `POST /api/optimize-route`

#### Request Payload (`RouteOptimizeRequest`):
```json
{
  "source": {
    "name": "Central Catering Hub - Guindy",
    "latitude": 13.0067,
    "longitude": 80.2026
  },
  "ngos": [
    {
      "ngo_id": "NGO_001",
      "name": "Annai Teresa Food Relief Foundation",
      "latitude": 13.0067,
      "longitude": 80.2026,
      "allocated_meals": 150.0
    },
    {
      "ngo_id": "NGO_002",
      "name": "Karunai Ullangal Trust",
      "latitude": 13.0012,
      "longitude": 80.2565,
      "allocated_meals": 80.38
    }
  ]
}
```

#### Response Payload (`RouteOptimizeResponse`):
```json
{
  "source": {
    "name": "Central Catering Hub - Guindy",
    "latitude": 13.0067,
    "longitude": 80.2026
  },
  "route": [
    {
      "sequence": 0,
      "type": "source",
      "ngo_id": null,
      "name": "Central Catering Hub - Guindy",
      "latitude": 13.0067,
      "longitude": 80.2026,
      "allocated_meals": 0.0,
      "distance_from_previous_km": 0.0
    },
    {
      "sequence": 1,
      "type": "ngo",
      "ngo_id": "NGO_001",
      "name": "Annai Teresa Food Relief Foundation",
      "latitude": 13.0067,
      "longitude": 80.2026,
      "allocated_meals": 150.0,
      "distance_from_previous_km": 0.0
    },
    {
      "sequence": 2,
      "type": "ngo",
      "ngo_id": "NGO_002",
      "name": "Karunai Ullangal Trust",
      "latitude": 13.0012,
      "longitude": 80.2565,
      "allocated_meals": 80.38,
      "distance_from_previous_km": 5.88
    }
  ],
  "summary": {
    "number_of_stops": 2,
    "total_distance_km": 5.88,
    "total_allocated_meals": 230.38,
    "start_location": "Central Catering Hub - Guindy"
  },
  "distance_matrix": [
    [0.0, 0.0, 5.88],
    [0.0, 0.0, 5.88],
    [5.88, 5.88, 0.0]
  ],
  "location_names": [
    "Central Catering Hub - Guindy",
    "Annai Teresa Food Relief Foundation",
    "Karunai Ullangal Trust"
  ],
  "status": "success",
  "message": "Route planned with 2 stops covering 5.88 km.",
  "disclaimer": "Demo Route Planner: Distances estimated via straight-line Haversine coordinates and a nearest-neighbor heuristic. Does not reflect real-time traffic or road topology."
}
```

---

## 5. Frontend User Workflow

```
Step 1: Enter Operational Features (PredictionForm.jsx)
        ↓
Step 2: Predict Surplus Meals (Random Forest Regressor -> 230.38 meals)
        ↓
Step 3: Match Partner NGOs (NGOMatchingSection.jsx -> Top matched centers)
        ↓
Step 4: Click "Proceed to Route Optimization"
        ↓
Step 5: Select Origin Hub & Click "Optimize Delivery Route" (RoutePlanningSection.jsx)
        ↓
Step 6: Render Sequenced Itinerary Timeline & Distance Metrics
```

---

## 6. Verification and Invariants

1. **All Waypoints Visited Once:** Every NGO in the input list appears exactly once in the route.
2. **Distance Conservation Invariant:** Total reported distance equals the exact mathematical sum of segment distances:
   $$\text{Total Distance} = \sum_{k=1}^N \text{Distance}(k-1 \rightarrow k)$$
3. **Meal Conservation Invariant:** Total distributed meals equals the sum of allocated meals:
   $$\text{Total Distributed Meals} = \sum_{k=1}^N \text{Allocated Meals}_k$$
4. **Defensive Validation:** Duplicate NGO IDs, out-of-bounds geographic coordinates, negative meal allocations, and empty candidate lists are cleanly rejected with HTTP `422 Unprocessable Entity`.

---

## 7. Limitations & Future Extensions

- **Straight-Line vs Road Distance:** Straight-line Haversine estimates do not account for road turns, one-way streets, or terrain barriers. Future phases will integrate OpenStreetMap (OSRM) or Google Directions API.
- **Heuristic Suboptimality:** While Nearest-Neighbor is fast ($O(N^2)$), it can create crossover paths in large networks. Future work may evaluate 2-opt local search or Lin-Kernighan heuristics.
- **Vehicle Capacity & Time Windows:** The current model assumes a single unconstrained delivery vehicle. Multi-vehicle routing with delivery time windows (VRPTW) is reserved for future versions.
