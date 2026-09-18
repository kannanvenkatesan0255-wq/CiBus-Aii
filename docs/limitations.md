# CIBUS-AI Project Limitations and System Boundaries

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *Predict. Connect. Nourish.*  

---

## 1. Data Limitations

1. **Synthetic Nature of Training Data:**  
   The primary dataset (`food_surplus.csv`, 8,000 rows) is synthetically generated using domain-informed probabilistic distributions. While designed to realistically mirror kitchen operations, it does not represent empirical sensor or telemetry logs from actual restaurants.
2. **Homogeneous Domain Assumptions:**  
   The dataset assumes a standard urban restaurant profile. Seasonal demand spikes, cultural fasts, or abrupt supply chain disruptions outside the modeled parameters are not represented.
3. **Generalization Uncertainty:**  
   Model performance on real-world commercial kitchen data cannot be guaranteed without retraining on empirical historical logs.

---

## 2. Machine Learning Limitations

1. **Static Offline Training:**  
   The `RandomForestRegressor` operates as a static, pre-trained model serialized via Joblib. It does not perform active online learning or dynamic weight adaptation from newly recorded daily sessions.
2. **Correlation vs. Causality:**  
   Feature importance metrics reflect tree split utility (Mean Decrease in Impurity); they indicate correlation within the modeled feature space and must **not** be interpreted as causal relationships.
3. **Point Estimation:**  
   The model outputs a deterministic point estimate of surplus meals rather than a full Bayesian prediction interval or confidence distribution.

---

## 3. NGO Directory & Matching Limitations

1. **Synthetic Recipient Directory:**  
   The NGO directory (`backend/data/ngos.json`) is an artificial dataset created for academic demonstration. No real-world charitable trusts or food banks are contacted, registered, or dispatched.
2. **Static Capacity & Availability:**  
   NGO capacity numbers, operating hours, and accepted food categories are fixed static parameters. The prototype does not query live recipient availability or dynamic refrigeration capacity in real time.
3. **Greedy Allocation Strategy:**  
   Meal distribution uses a straightforward greedy allocation heuristic based on distance and capacity. It does not solve a global multi-objective social welfare optimization problem.

---

## 4. Route Optimization Limitations

1. **Spherical Distance Approximation:**  
   All distance calculations utilize the **Haversine formula** (great-circle Euclidean distance over a spherical earth). It does not account for actual road topology, one-way streets, bridges, or physical urban obstacles.
2. **Heuristic Optimality (TSP):**  
   Multi-stop route planning uses a **Greedy Nearest Neighbor Heuristic**, which runs in $O(N^2)$ time. It does not guarantee the mathematically global minimum distance compared to branch-and-bound or mixed-integer linear programming (MILP).
3. **No Live Traffic or GPS Integration:**  
   The system does not interface with live traffic APIs (such as Google Maps or OpenStreetMap) or stream real-time GPS telemetry from delivery vehicles.

---

## 5. Logistics & Delivery Boundaries

1. **Planning Tool vs. Physical Transport:**  
   CIBUS-AI is strictly a **decision-support and planning software system**. It generates redistribution plans; it does not physically transport food, manage courier fleets, or execute delivery handoffs.
2. **No Real-Time Delivery Confirmation:**  
   The software records redistribution plans into its session log; it cannot verify whether planned meals were actually picked up, transported within safe temperature windows, or consumed.

---

## 6. System Architecture & Prototype Scope

1. **Local File Persistence:**  
   Session history and impact counters are persisted to a local JSON file (`activity_log.json`). While ideal for zero-dependency local demonstration, it is not suitable for high-concurrency multi-tenant production deployments without migration to PostgreSQL.
2. **Authentication & Authorization:**  
   The current prototype does not enforce multi-user role-based access control (RBAC), multi-tenant isolation, or OAuth2/JWT token sessions.
