# CIBUS-AI NGO Matching and Food Redistribution Module

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *"Predict. Connect. Nourish."*  
**Document:** NGO Matching & Redistribution Logistics Specification  
**Date:** September 2026  

---

> [!IMPORTANT]
> **Methodological Clarification:**
> The NGO Matching Module is a **deterministic, rule-based capacity allocation engine** and is **NOT a Machine Learning prediction model**. 
> - **Core ML Contribution:** Forecasting continuous food surplus quantities ($\hat{y} \in \mathbb{R}_{\ge 0}$) using the pre-trained `RandomForestRegressor`.
> - **Extended Application Module:** Distributing that predicted volume across available, dietary-compatible local recipient organizations according to physical capacity and proximity constraints.

---

## 1. Module Objective
In traditional charitable food recovery, surplus food is announced reactively at the end of the day, leaving recipient organizations with insufficient time to arrange logistics. 

The CIBUS-AI NGO Matching Module bridges pre-service Machine Learning intelligence with practical logistics:
1. Takes the quantitative surplus forecast produced by the Random Forest model.
2. Identifies candidate recipient centers from a partner organization directory.
3. Ranks candidates using a transparent multi-criteria heuristic score.
4. Recommends meal portion allocations that strictly respect individual shelter capacities and total available food.

---

## 2. Synthetic Partner NGO Dataset
For this college prototype, a synthetic dataset representing community shelters, night shelters, children's homes, and food relief trusts is used.

- **File Path:** [`backend/data/ngos.csv`](file:///k:/CiBus-Ai%20R/backend/data/ngos.csv)
- **Data Status:** **100% Synthetic / Demonstration Data**. No real personal contact numbers or private individual records are stored.

### Data Schema:
| Field Name | Type | Description | Example Values |
| :--- | :---: | :--- | :--- |
| `NGO_ID` | String | Unique organizational identifier | `NGO001`, `NGO002` |
| `NGO_Name` | String | Organization name | *Annam Food Rescue Foundation* |
| `Area` | String | Operational district/locality | `Tambaram`, `Guindy`, `Adyar` |
| `Latitude` | Float | Geographic latitude coordinate | `12.9249`, `13.0067` |
| `Longitude` | Float | Geographic longitude coordinate | `80.1000`, `80.2025` |
| `Capacity_Meals` | Integer | Maximum meal storage/distribution capacity | `80 - 350 meals` |
| `People_Served` | Integer | Average beneficiary headcount | `75 - 300 individuals` |
| `Food_Type` | String | Dietary acceptance format | `Vegetarian`, `Both` |
| `Contact_Available` | String | Contact readiness indicator | `Yes` |
| `Availability_Status` | String | Current operational receiving state | `Available`, `Limited`, `Unavailable` |

---

## 3. Matching Criteria & Multi-Factor Scoring

Candidate organizations are evaluated against four operational factors:

```
┌─────────────────────────────────────────────────────────────┐
│                    Candidate Evaluation                     │
├──────────────────────────────┬──────────────────────────────┤
│ 1. Availability Status (35%) │ Available (1.0), Limited (0.5)│
│ 2. Proximity / Distance (25%)│ Linear decay within 25 km    │
│ 3. Dietary Compatibility (20%)│ Veg / Non-Veg / Both match   │
│ 4. Capacity Fit (20%)        │ Ratio of capacity to surplus │
└──────────────────────────────┴──────────────────────────────┘
```

### Composite Heuristic Scoring Formula:
$$\text{Score} = (0.35 \times S_{\text{avail}}) + (0.25 \times S_{\text{dist}}) + (0.20 \times S_{\text{compat}}) + (0.20 \times S_{\text{cap}})$$

Where:
- $S_{\text{avail}} = 1.0$ for `Available`, $0.5$ for `Limited`, $0.0$ for `Unavailable` (filtered out).
- $S_{\text{dist}} = \max(0.0, 1.0 - (\text{Distance}_{\text{km}} / 25.0))$ when coordinates are provided; neutral $0.5$ when coordinates are omitted.
- $S_{\text{compat}} = 1.0$ if dietary requirements match or if NGO accepts `Both`; $0.0$ if incompatible.
- $S_{\text{cap}} = \min(1.0, \text{Capacity} / \max(1.0, \text{Surplus}))$.

---

## 4. Constraint-Based Capacity Allocation Logic

To prevent overloading recipient shelters or fabricating nonexistent meals, the allocation engine enforces strict mathematical bounds:

$$\text{Allocated Meals}_i = \min(\text{Remaining Surplus}, \text{Capacity}_i)$$
$$\text{Remaining Surplus} \leftarrow \text{Remaining Surplus} - \text{Allocated Meals}_i$$

### Guaranteed Invariants:
1. **No Shelter Overflow:** $\forall i, \text{Allocated Meals}_i \le \text{Capacity}_i$.
2. **No Surplus Overflow:** $\sum_{i} \text{Allocated Meals}_i \le \text{Predicted Surplus Meals}$.
3. **Conservation of Food:** $\text{Total Allocated Meals} + \text{Unallocated Meals} = \text{Predicted Surplus Meals}$.

---

## 5. Great-Circle Distance Calculation (Haversine Formula)

Geographic distance between the food-generating facility $(\phi_1, \lambda_1)$ and candidate recipient $(\phi_2, \lambda_2)$ is computed using the spherical Earth model ($R = 6371.0 \text{ km}$):

$$a = \sin^2\left(\frac{\phi_2 - \phi_1}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\lambda_2 - \lambda_1}{2}\right)$$
$$d = 2 R \cdot \arctan2\left(\sqrt{a}, \sqrt{1 - a}\right)$$

*If the donor facility coordinates are omitted, distance is safely marked as "Distance unavailable" without disrupting the capacity allocation.*

---

## 6. REST API Endpoint (`POST /api/match-ngos`)

### Request Payload:
```json
{
  "predicted_surplus_meals": 230.38,
  "food_type": "Both",
  "source_latitude": 12.9716,
  "source_longitude": 80.2000,
  "max_matches": 3
}
```

### Response Payload:
```json
{
  "predicted_surplus_meals": 230.38,
  "total_allocated_meals": 230.38,
  "unallocated_meals": 0.0,
  "matched_count": 1,
  "matches": [
    {
      "ngo_id": "NGO003",
      "ngo_name": "Hope City Shelter & Relief",
      "area": "Adyar",
      "capacity_meals": 300,
      "allocated_meals": 230.38,
      "people_served": 280,
      "food_type": "Both",
      "availability_status": "Available",
      "distance_km": 6.95,
      "match_score": 0.93,
      "reason": "Active receiving capacity • High proximity (6.95 km) • Compatible dietary format"
    }
  ],
  "status": "success",
  "message": "Allocated 230.38 of 230.38 predicted meals across 1 recipient organizations."
}
```

---

## 7. Frontend User Flow

```
1. Food Surplus Forecasting Form (React)
           │
           ▼
2. Random Forest Regression Forecast (e.g. 230.4 meals)
           │
           ▼
3. Recipient Matching Parameters (Dietary type, Donor area preset)
           │
           ▼
4. Rule-Based Candidate Scoring & Capacity Distribution
           │
           ▼
5. Interactive Allocation Cards (Allocated portions, Match score %, Distance)
```

---

## 8. Current Boundaries & Future Scope

### Boundaries in Current Prototype:
- Uses a local CSV database of synthetic recipient organizations.
- Calculations run synchronously without external map service dependencies.

### Future Roadmap:
- Multi-Stop Vehicle Route Optimization with traffic heuristics.
- Volunteer Courier Push Notification dispatching.
- Live GPS Food Transit and IoT temperature tracking.
