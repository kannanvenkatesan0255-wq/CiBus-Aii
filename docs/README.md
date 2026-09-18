# CIBUS-AI Documentation Index

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *Predict. Connect. Nourish.*  

Welcome to the comprehensive technical and academic documentation suite for CIBUS-AI. All documents below are structured, cross-referenced, and aligned with project-based learning (PBL) standards.

---

## 1. Master Documentation Index

| Document | Description | Key Topics Covered |
| :--- | :--- | :--- |
| [Final Architecture](final_architecture.md) | High-level system architecture and data flow | 3-tier structure, component specs, sequence diagram |
| [PBL Academic Report](pbl_report_content.md) | Complete engineering PBL report content | Cover, Certificate, Declaration, Abstract, Chapters 1–8 |
| [IEEE References](references.md) | Verified academic literature citations | Breiman, Scikit-learn, FAO/UNEP, Haversine |
| [Project Appendix](appendix.md) | Appendices A through F | Source code, dataset schema, ML metrics, test logs |
| [Team Roles & Contributions](team_roles.md) | Organizational matrix and member placeholders | ML lead, backend, frontend, QA, mentor details |
| [Oral Demo Script](demo_script.md) | 5–7 minute presentation and demo cue sheet | Time-stamped script, speech cues, click sequence |
| [Presentation Deck](presentation_content.md) | 15-slide presentation deck specification | Problem, dataset, ML models, results, route, impact |
| [Viva Voce Examination Guide](viva_questions.md) | 25+ comprehensive exam questions with answers | ML theory, target leakage, metrics, algorithms, limits |
| [Project Structure](project_structure.md) | Repository directory and module breakdown | `ai-engine/`, `backend/`, `frontend/`, `docs/`, `tests/` |
| [System Limitations](limitations.md) | Complete technical and heuristic boundaries | Synthetic data, straight-line routing, software scope |
| [Final Project Audit](final_project_audit.md) | 11-point subsystem verification audit | Empirical metrics, test pass rates, readiness |
| [Verified Demo Inputs](demo_input.md) | Safe synthetic input test scenarios | Weekend banquet, corporate lunch, stormy weather |
| [Screenshot Checklist](screenshot_checklist.md) | 10-point interface screenshot capture guide | Interface targets, capture tips, document mapping |
| [Submission Checklist](final_submission_checklist.md) | Master readiness checklist for evaluation | Technical, documentation, and student action items |
| [Final Test Report](final_test_report.md) | Comprehensive automated test execution log | 91 automated tests across 4 test suites |
| [Weekly Progress Log](weekly_progress.md) | 10-week chronological progress record | Milestone-by-milestone technical achievements |

---

## 2. Key Project Facts & Metrics Summary

- **Problem Domain:** AI-driven pre-service commercial food surplus forecasting and redistribution planning.
- **Machine Learning Architecture:** Scikit-Learn `RandomForestRegressor` ($n\_estimators=100$, $max\_depth=15$, $random\_state=42$).
- **Dataset:** 8,000 synthetic observations, 10 feature attributes (Leakage strictly prevented by omitting `Meals_Sold`).
- **Evaluation Performance (Unseen Test Data):**
  - **Mean Absolute Error (MAE):** `14.5793 meals`
  - **Root Mean Squared Error (RMSE):** `20.6869 meals`
  - **Coefficient of Determination ($R^2$):** `0.9543`
- **Heuristics:** Greedy capacity allocation + Spherical Haversine Nearest Neighbor route optimizer.
- **Automated Test Coverage:** 91 / 91 passed (100% pass rate).
