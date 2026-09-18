# CIBUS-AI Comprehensive Viva Voce Examination Guide

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *Predict. Connect. Nourish.*  
**Topic Areas:** Machine Learning, Data Engineering, Backend Architecture, Optimization, Frontend, Security, and System Boundaries.

---

## 1. Machine Learning & Predictive Modeling

### Q1: Why is food surplus prediction formulated as a regression problem rather than a classification problem?
> **Answer:** Surplus food is measured as a continuous numerical quantity of edible meals (e.g., 45 meals, 112 meals). While classification could bucket surplus into discrete labels (e.g., "High", "Low"), exact meal counts are necessary for the downstream NGO matching algorithm to calculate precise capacity allocations.

### Q2: Why did you select `RandomForestRegressor` over linear regression or neural networks?
> **Answer:** Random Forest is an ensemble of bagged decision trees that excels at capturing non-linear relationships and high-order feature interactions (such as the interaction between `Weather`, `Day`, and `Event_Type`) without requiring heavy feature scaling or large amounts of training compute. It also provides natural resistance to overfitting and native feature importance scoring.

### Q3: What is the exact target variable, and what are the 9 input features?
> **Answer:** The target variable is `Surplus_Meals`. The 9 input features are: `Day`, `Weather`, `Customers_Forecast`, `Meals_Prepared`, `Festival`, `Event_Type`, `Staff_Count`, `Avg_Rating`, and `Special_Event`.

### Q4: Why is `Meals_Sold` strictly excluded from the prediction model inputs?
> **Answer:** Including `Meals_Sold` would cause catastrophic **target leakage**. By definition, $\text{Meals\_Sold} + \text{Surplus\_Meals} = \text{Meals\_Prepared}$. If the model had access to meals sold, it would trivially compute $\text{Surplus} = \text{Prepared} - \text{Sold}$ with zero predictive value, and the model could never be used *before* meal service.

### Q5: What is the difference between MAE and RMSE in your evaluation?
> **Answer:** 
> - **Mean Absolute Error (MAE):** The average absolute difference between predicted and actual surplus ($14.58\text{ meals}$). It treats all error magnitudes linearly.
> - **Root Mean Squared Error (RMSE):** The square root of the average squared errors ($20.69\text{ meals}$). Because errors are squared before averaging, RMSE penalizes large outlier errors more severely.

### Q6: What does the $R^2$ score of 0.9543 represent, and why is it incorrect to call it "95.43% accuracy"?
> **Answer:** $R^2$ (the Coefficient of Determination) represents the proportion of variance in the target variable explained by the model relative to a naive mean predictor. Calling it "accuracy" is technically invalid because accuracy is a discrete classification metric (true positives/total), whereas regression evaluates continuous error residuals.

### Q7: Why did you use an 80/20 train-test split with a fixed `random_state=42`?
> **Answer:** The 80/20 split ensures 6,400 records for model fitting and 1,600 unseen records for unbiased generalizability assessment. Setting `random_state=42` ensures exact determinism and reproducibility across all test and evaluation runs.

### Q8: What hyperparameter refinement was performed on the Random Forest?
> **Answer:** We evaluated maximum tree depth (`max_depth`) constraints. Setting `max_depth=15` effectively pruned overly specific leaf nodes, preventing memorization of synthetic noise while maintaining an $R^2$ of 0.9543 on unseen test data.

### Q9: How is feature importance computed in Random Forest?
> **Answer:** In scikit-learn, feature importance is calculated as the **Mean Decrease in Impurity (MDI)** or Gini importance, measuring the total reduction in variance brought by a feature across all split nodes in all 100 decision trees.

### Q10: Does a high feature importance score for `Meals_Prepared` prove that preparing food causes waste?
> **Answer:** No. Feature importance measures predictive correlation and utility within the model's decision rules; it does **not imply causality**.

---

## 2. Data Engineering & Preprocessing

### Q11: Why is a synthetic dataset used in this project?
> **Answer:** Real-world commercial kitchens rarely publish granular hourly food surplus and customer logs due to commercial sensitivity and liability concerns. Synthetic data generation allowed us to establish a controlled, statistically sound baseline of 8,000 records with realistic domain distributions.

### Q12: How are categorical and numerical features preprocessed?
> **Answer:** We constructed a scikit-learn `ColumnTransformer`:
> - Categorical features (`Day`, `Weather`, `Event_Type`, `Festival`, `Special_Event`) are processed using `OneHotEncoder(handle_unknown='ignore')`.
> - Numerical features (`Customers_Forecast`, `Meals_Prepared`, `Staff_Count`, `Avg_Rating`) are normalized using `StandardScaler()`.

### Q13: Why is the preprocessor serialized separately from the model?
> **Answer:** The preprocessor (`food_surplus_preprocessor.pkl`) and model (`food_surplus_model.pkl`) are serialized using Joblib. This allows raw user dictionary payloads from the FastAPI backend to be transformed into identical one-hot scaled matrices at inference time without data skew.

---

## 3. Backend, Heuristics & Route Optimization

### Q14: How does the NGO Matching Engine allocate food surplus?
> **Answer:** The engine filters synthetic NGOs within a 15 km geographic radius based on operational status and accepted food types. It then executes a greedy capacity allocation algorithm, assigning surplus meals to candidate NGOs until the predicted surplus is exhausted.

### Q15: How is geographic distance calculated between food donors and NGOs?
> **Answer:** We use the spherical **Haversine formula**:
> $$d = 2r \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos \phi_1 \cos \phi_2 \sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$
> where $r = 6371\text{ km}$. It accurately computes great-circle distance between two latitude/longitude pairs on Earth.

### Q16: Is the route generated by the Route Optimizer globally optimal?
> **Answer:** No. Multi-stop routing is an instance of the Travelling Salesperson Problem (TSP), which is NP-hard. We utilize a **Greedy Nearest Neighbor Heuristic**, which selects the closest unvisited NGO at each step. This provides rapid $O(N^2)$ computation suitable for real-time web execution.

### Q17: How is travel time estimated in the route optimizer?
> **Answer:** Travel time is estimated assuming an average urban transit speed of $25\text{ km/h}$, with an additional $5\text{ minutes}$ fixed dwell time per pickup/dropoff stop:
> $$\text{Time (minutes)} = \left(\frac{\text{Distance}}{25} \times 60\right) + (5 \times N_{\text{stops}})$$

### Q18: What role does FastAPI play in the application architecture?
> **Answer:** FastAPI acts as the asynchronous backend framework. It provides high-throughput REST endpoints, automatic request data validation via Pydantic schemas, CORS header management, and OpenAPI/Swagger documentation generation.

---

## 4. System Integration & Analytics

### Q19: How are environmental impact metrics calculated on the dashboard?
> **Answer:** Standard environmental conversion factors are applied to the total allocated surplus meals:
> - **Greenhouse Gas Emissions Offset:** $2.5\text{ kg } CO_2\text{e}$ per meal.
> - **Embedded Water Conserved:** $1,000\text{ liters}$ per meal.

### Q20: How is session activity persisted in the prototype?
> **Answer:** Sessions are committed to a local JSON document store at `backend/data/activity_log.json` with timestamped records containing prediction parameters, matched NGOs, and route statistics.

---

## 5. Security, Testing & System Limitations

### Q21: What security and validation hardening measures are implemented?
> **Answer:**
> - Strict Pydantic input range validation (e.g., `Meals_Prepared` $\ge 0$, `Rating` $\in [1.0, 5.0]$).
> - Restricted CORS middleware preventing unauthorized cross-origin requests.
> - Clean `.gitignore` and `.env.example` configurations ensuring no secrets or tokens are committed.

### Q22: What is the automated test coverage of the repository?
> **Answer:** The repository contains **91 automated tests** across four distinct test suites:
> 1. ML Unit Tests (`ai-engine/prediction/test_predict.py`): 9 tests.
> 2. Dataset Validation (`ai-engine/dataset/validate_dataset.py`): 5 checks.
> 3. Backend, Heuristics & Security Tests (`backend/tests/`): 54 tests.
> 4. Frontend Integration Tests (`frontend/tests/`): 23 tests.
> All 91 tests pass with 100% pass rate.

### Q23: What are the primary limitations of the current CIBUS-AI system?
> **Answer:**
> 1. **Synthetic Data:** Trained and evaluated on synthetic records; real-world kitchen dynamics may differ.
> 2. **Distance Approximations:** Uses straight-line Haversine math rather than live turn-by-turn road networks or live traffic APIs.
> 3. **Software Planning vs Physical Dispatch:** The software creates a logistics redistribution plan; it does not execute physical transport or confirm live deliveries.

### Q24: How does CIBUS-AI prevent negative or non-physical surplus predictions?
> **Answer:** The inference module enforces physical boundary clamping (`max(0, prediction)`), guaranteeing that predicted surplus meals can never be negative or exceed the number of meals prepared.

### Q25: What are the key directions for future scope?
> **Answer:** Future enhancements include integration with real-time restaurant POS systems, live Google Maps Directions API for turn-by-turn routing with traffic, a mobile driver app with barcode delivery confirmation, and migration to a cloud PostgreSQL database.
