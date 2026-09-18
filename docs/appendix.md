# Project Appendix

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *Predict. Connect. Nourish.*  

---

## APPENDIX A: Complete Source Code Repository

The complete, version-controlled source code for CIBUS-AI is hosted on GitHub:
- **Repository URL:** [CiBus-Aii Repository](https://github.com/kannanvenkatesan0255-wq/CiBus-Aii)
- **Primary Branch:** `main`
- **Component Subdirectories:**
  - `ai-engine/`: Machine learning dataset generator, preprocessing, model training, evaluation, and inference tests.
  - `backend/`: FastAPI REST application, NGO matching engine, route optimizer, analytics service, and API test suites.
  - `frontend/`: React single-page application, interactive UI sections, SVG route visualization, and end-to-end integration tests.
  - `docs/`: Comprehensive project documentation, architectural diagrams, weekly logs, and PBL report materials.

---

## APPENDIX B: Dataset Information

- **Dataset File:** `ai-engine/dataset/food_surplus.csv`
- **Total Records:** 8,000 observations.
- **Dataset Nature:** Synthetically generated for controlled ML experimentation and educational demonstration.
- **Feature Schema (10 columns):**
  1. `Day` (*Categorical*): Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday.
  2. `Weather` (*Categorical*): Sunny, Rainy, Cloudy, Foggy, Stormy, Cold.
  3. `Customers_Forecast` (*Numerical Integer*): Estimated footfall (Range: 50–500).
  4. `Meals_Prepared` (*Numerical Integer*): Total quantity prepared (Range: 50–600).
  5. `Festival` (*Categorical/Binary*): 0 (No) or 1 (Yes).
  6. `Event_Type` (*Categorical*): None, Corporate, Wedding, Birthday.
  7. `Staff_Count` (*Numerical Integer*): Kitchen/service personnel count (Range: 2–30).
  8. `Avg_Rating` (*Numerical Float*): Historical customer review score (Range: 1.0–5.0).
  9. `Special_Event` (*Categorical/Binary*): 0 (No) or 1 (Yes).
  10. `Surplus_Meals` (*Target - Numerical Integer*): Actual leftover food surplus (Range: 0–350).
- **Target Leakage Prevention:** `Meals_Sold` is excluded from training features to ensure realistic pre-service surplus prediction.

---

## APPENDIX C: Final Model Evaluation Results

- **Model Architecture:** Scikit-Learn `RandomForestRegressor`
  - Number of Estimators (`n_estimators`): 100
  - Maximum Depth (`max_depth`): 15
  - Random Seed (`random_state`): 42
  - Preprocessing: `ColumnTransformer` with `OneHotEncoder(handle_unknown='ignore')` for categorical features and `StandardScaler()` for numerical features.
- **Data Partitioning:** 80% Training Set (6,400 samples), 20% Test Set (1,600 samples), fixed split (`random_state=42`).
- **Evaluation Metrics:**
  - **Mean Absolute Error (MAE):** `14.5793 meals`
  - **Root Mean Squared Error (RMSE):** `20.6869 meals`
  - **Coefficient of Determination ($R^2$):** `0.9543` (explains 95.43% of surplus variance)
- **Top Predictive Features (Feature Importance):**
  1. `Meals_Prepared` (~48.2%)
  2. `Customers_Forecast` (~26.7%)
  3. `Day` (Day-of-week demand fluctuations, ~8.5%)
  4. `Festival` & `Event_Type` (~6.8%)
  5. `Weather` & `Staff_Count` (~9.8%)

---

## APPENDIX D: Test Execution Report

The repository includes comprehensive automated test coverage spanning ML inference, API endpoints, heuristic logic, and security:
- **Reference Document:** [docs/final_test_report.md](file:///k:/CiBus-Ai%20R/docs/final_test_report.md)
- **Total Test Cases:** 91 automated tests
  - ML Unit Tests (`ai-engine/prediction/test_predict.py`): 9 Passed
  - Dataset Schema Validation (`ai-engine/dataset/validate_dataset.py`): 5 Checks Passed
  - Backend & Security Tests (`backend/tests/`): 54 Passed
  - Frontend Verification Tests (`frontend/tests/`): 23 Passed
- **Overall Result:** 91 / 91 Passed (100% Pass Rate).

---

## APPENDIX E: Weekly PBL Progress Log Template

| Week | Work Completed | ML / Technical Progress | Learning Outcome | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| **Week 1** | Problem formulation & baseline research | Explored food waste challenge & ML formulation | Understood regression vs classification trade-offs | Problem statement document |
| **Week 2** | Synthetic dataset generation | Built 8,000-record dataset & validated schema | Learned data distribution synthesis & leakage avoidance | `food_surplus.csv` |
| **Week 3** | Preprocessing & Baseline Model | Implemented `ColumnTransformer` & Baseline RF | Evaluated baseline metrics (MAE, RMSE, $R^2$) | `baseline_model.py` |
| **Week 4** | Model Refinement & Feature Importance | Hyperparameter tuning ($max\_depth=15$) | Analyzed Gini importance and tree depth effects | `final_results.json` |
| **Week 5** | Reusable Prediction Service | Encapsulated model persistence with Joblib | Learned offline model serialization workflows | `predict.py` |
| **Week 6** | FastAPI Backend Integration | Created REST endpoints with Pydantic validation | Built async REST APIs with CORS & schema validation | `backend/main.py` |
| **Week 7** | NGO Matching & Route Planning | Rule-based matcher & Haversine nearest neighbor | Implemented greedy heuristics & distance matrices | `ngo_service.py`, `route_service.py` |
| **Week 8** | Frontend Development & Analytics | Built React 19 SPA with impact dashboard | Developed reactive component state & SVG mapping | `frontend/src/` |
| **Week 9** | System Integration & Testing | Unified end-to-end flow; wrote 91 automated tests | Practiced test-driven integration and security checks | `test_e2e_workflow.py` |
| **Week 10** | Final Documentation & Audit | Compiled PBL report, presentation, and audit | Mastered end-to-end technical documentation | `docs/` |

---

## APPENDIX F: Interface Screenshot Checklist

The following screenshots should be captured from the running application for inclusion in the final presentation and report submission:

1. **Dashboard Home:** Overview showing real-time impact counters (Total Surplus Planned, Meals Allocated, $CO_2$ Offset, Water Saved).
2. **Prediction Input Form:** Parameter entry form displaying categorical dropdowns, sliders, and validation feedback.
3. **Prediction Result Card:** Display showing predicted surplus meal count, confidence context, and redistribution action button.
4. **NGO Matching View:** Candidate NGO table showing distance (km), meal requirements, operating hours, and allocated meals.
5. **Route Planning & Visualization:** Interactive SVG canvas plotting the multi-stop pickup trajectory from donor to recipient NGOs.
6. **Activity Log & History:** Chronological audit table showing recent redistribution sessions.
7. **Interactive API Documentation:** FastAPI Swagger UI (`/docs`) showing schema definitions and test execution.
8. **Automated Test Results:** Terminal output showing all 91 tests passing successfully.
