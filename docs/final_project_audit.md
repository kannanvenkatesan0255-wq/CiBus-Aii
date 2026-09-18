# CIBUS-AI Final Project Audit Report

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *Predict. Connect. Nourish.*  
**Date:** 2026-09-18  
**Audit Scope:** Complete Machine Learning Pipeline, FastAPI Backend, React Frontend, NGO Matching, Route Optimizer, Analytics Dashboard, Security Configuration, Automated Test Suites, and PBL Documentation.

---

## 1. Machine Learning Engine
- **Status:** Verified and Complete
- **Target Variable:** `Surplus_Meals` (Continuous regression target).
- **Target Leakage Check:** Passed. `Meals_Sold` is strictly excluded from training features.
- **Model Architecture:** Scikit-Learn `RandomForestRegressor` ($n\_estimators=100$, $max\_depth=15$, $random\_state=42$).
- **Actual Evaluation Metrics (Unseen Test Data):**
  - **Mean Absolute Error (MAE):** `14.5793 meals`
  - **Root Mean Squared Error (RMSE):** `20.6869 meals`
  - **Coefficient of Determination ($R^2$):** `0.9543`
- **Feature Importance:** `Meals_Prepared` (48.2%), `Customers_Forecast` (26.7%), `Day` (8.5%), `Festival`/`Event_Type` (6.8%), `Weather`/`Staff` (9.8%).
- **Inference Verification:** 9/9 ML unit tests passed (`ai-engine/prediction/test_predict.py`).

---

## 2. Dataset & Preprocessing
- **Status:** Verified and Complete
- **Dataset File:** `ai-engine/dataset/food_surplus.csv`
- **Total Records:** Exactly 8,000 rows, 10 columns.
- **Nature:** Synthetic dataset generated for academic experimentation and reproducible demonstration.
- **Validation Script:** 5/5 automated validation checks passed (`ai-engine/dataset/validate_dataset.py`).
- **Preprocessor Artifact:** Serialized `ColumnTransformer` (`ai-engine/models/food_surplus_preprocessor.pkl`).

---

## 3. Backend Architecture & REST APIs
- **Status:** Verified and Complete
- **Framework:** FastAPI with Uvicorn ASGI server.
- **Endpoints Implemented:**
  - `GET /api/health`: Health & subsystem verification.
  - `POST /api/predict`: ML surplus prediction.
  - `POST /api/match-ngos`: Synthetic NGO matching & meal allocation.
  - `POST /api/optimize-route`: Haversine distance matrix & route optimizer.
  - `GET /api/dashboard/summary`: Aggregate impact analytics.
  - `GET /api/dashboard/recent-activity`: Recent session history.
  - `POST /api/dashboard/record-activity`: Planning session persistence.
- **Validation:** Pydantic schemas enforce type safety and domain bounds across all inputs.

---

## 4. Frontend Application & UI/UX
- **Status:** Verified and Complete
- **Framework:** React 19 with Vite bundler and Tailwind CSS.
- **Components Implemented:**
  - `PredictionForm.jsx`: Parameter inputs, validation alerts, and result card.
  - `NgoMatchingSection.jsx`: Radius filtering, candidate table, and meal allocation breakdown.
  - `RoutePlanningSection.jsx`: Waypoint sequence list, transit estimates, and interactive SVG route map.
  - `ImpactDashboard.jsx`: Metric counters ($CO_2$, Water, Surplus Meals) and activity history.
  - `WorkflowTracker.jsx`: Step-by-step progress indicator and reset controls.
- **Build Verification:** Clean compilation (`npm run build`), 23/23 frontend verification tests passed.

---

## 5. NGO Matching Module
- **Status:** Verified and Complete
- **Recipient Directory:** Synthetic local NGO database (`backend/data/ngos.json`).
- **Matching Heuristics:** Radius filtering ($d \le 15\text{ km}$), active status validation, and greedy capacity allocation.
- **Allocation Rule:** Deterministically divides predicted surplus among compatible NGOs until surplus is fully assigned.

---

## 6. Route Optimization Module
- **Status:** Verified and Complete
- **Distance Formula:** Spherical Haversine formula ($r = 6371\text{ km}$).
- **Optimization Strategy:** Greedy Nearest Neighbor heuristic starting from donor coordinates.
- **Metrics Computed:** Total travel distance (km), estimated duration (minutes at $25\text{ km/h} + 5\text{ min/stop}$), and waypoint ordering.

---

## 7. Impact Dashboard & Analytics
- **Status:** Verified and Complete
- **Persistence:** Local file store (`backend/data/activity_log.json`).
- **Environmental Factors:** $2.5\text{ kg } CO_2\text{e}$ and $1,000\text{ liters}$ water saved per redistributed meal.
- **Live Sync:** Real-time refresh upon session completion and explicit reset capabilities.

---

## 8. Security & Error Hardening
- **Status:** Verified and Complete
- **CORS Policy:** Explicitly configured origins.
- **Input Boundaries:** Physical boundary clamping on ML predictions; negative numbers and out-of-range ratings rejected with HTTP 422.
- **Credential Hygiene:** No API keys, database passwords, or private tokens committed. Clean `.env.example` provided.

---

## 9. Automated Testing
- **Status:** Verified and Complete
- **Total Automated Tests:** **91 tests**
  - ML Unit Tests: 9 Passed
  - Dataset Validation Checks: 5 Passed
  - Backend & Security Tests: 54 Passed
  - Frontend Verification Tests: 23 Passed
- **Test Pass Rate:** **100% (91 / 91 Passed, 0 Failures)**.

---

## 10. Documentation Suite
- **Status:** Verified and Complete
- **Documents Available in `docs/`:**
  - `final_architecture.md`: Complete system architecture & data flow.
  - `pbl_report_content.md`: Full academic PBL report (Cover, Certificate, Declaration, Abstract, Chapters 1–8, References, Appendix).
  - `references.md`: 10 verified IEEE-style academic citations.
  - `appendix.md`: Appendices A through F.
  - `team_roles.md`: Team role allocation with student placeholders.
  - `demo_script.md`: 5–7 minute oral presentation and demonstration script.
  - `presentation_content.md`: 15-slide presentation deck specification.
  - `viva_questions.md`: 25+ comprehensive viva questions with answers.
  - `project_structure.md`: Directory and file architecture index.
  - `limitations.md`: Complete system, ML, data, and heuristic boundaries.
  - `demo_input.md`: Verified synthetic test input payloads.
  - `screenshot_checklist.md`: 10-point interface screenshot guide.
  - `final_submission_checklist.md`: PBL readiness checklist.
  - `final_test_report.md`: Complete automated test execution log.
  - `weekly_progress.md`: 10-week progress tracking log.
  - `README.md`: Documentation master index.

---

## 11. PBL Academic Readiness
- **Status:** Verified and Ready
- **PBL Structure Alignment:** Fully aligned with standard engineering PBL evaluation criteria.
- **Student Placeholders:** Preserved clearly marked placeholders (`[STUDENT NAME]`, `[REGISTER NUMBER]`, `[FACULTY MENTOR]`, `[MENTOR SIGNATURE]`) to avoid fabricating student or institutional identities.

---

## 12. Known Technical Limitations
- All training data and NGO recipient directories are synthetic.
- Route optimization uses straight-line Haversine math and nearest-neighbor heuristics rather than live turn-by-turn road networks or real-time traffic APIs.
- The system generates a software-based *redistribution plan*; it does not execute physical transport or confirm live deliveries.

---

## 13. Final Recommendation

**Project verified and ready for demonstration, with team-specific report fields still requiring completion.**
