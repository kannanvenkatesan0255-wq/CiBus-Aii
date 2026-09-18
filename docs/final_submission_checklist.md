# Final PBL Submission Readiness Checklist

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *Predict. Connect. Nourish.*  

---

## 1. Technical Implementation Verification

- [x] **Machine Learning Pipeline:**
  - [x] 8,000-row synthetic dataset generated and validated (`food_surplus.csv`).
  - [x] `Meals_Sold` strictly excluded from feature inputs to prevent target leakage.
  - [x] Preprocessor pipeline (`ColumnTransformer`) saved as `food_surplus_preprocessor.pkl`.
  - [x] Refined `RandomForestRegressor` saved as `food_surplus_model.pkl`.
  - [x] Evaluation results verified: MAE = $14.58$, RMSE = $20.69$, $R^2 = 0.9543$.
  - [x] 9/9 ML unit tests passing.

- [x] **Backend REST API:**
  - [x] FastAPI service configured with async handlers and Pydantic schemas.
  - [x] ML inference endpoint (`/api/predict`) operational.
  - [x] NGO matching endpoint (`/api/match-ngos`) operational with capacity allocation.
  - [x] Haversine route optimizer endpoint (`/api/optimize-route`) operational.
  - [x] Impact dashboard summary and activity persistence endpoints operational.
  - [x] 54/54 backend and security unit tests passing.

- [x] **Frontend Web Application:**
  - [x] React 19 single-page application built with Vite and Tailwind CSS.
  - [x] Prediction form, result card, NGO table, SVG route map, and dashboard operational.
  - [x] 23/23 frontend verification tests passing.
  - [x] Production build compiles cleanly (`npm run build`).

- [x] **End-to-End Integration:**
  - [x] Complete workflow tested from input $\rightarrow$ prediction $\rightarrow$ NGO allocation $\rightarrow$ route optimization $\rightarrow$ dashboard update.
  - [x] Total automated tests: 91 / 91 passing (100% pass rate).

---

## 2. PBL Academic Documentation Suite

- [x] **System Architecture Document:** `docs/final_architecture.md`
- [x] **Academic Report Content:** `docs/pbl_report_content.md` (Cover, Certificate, Declaration, Abstract, Chapters 1–8, References, Appendix)
- [x] **IEEE References:** `docs/references.md` (10 verified citations)
- [x] **Project Appendices:** `docs/appendix.md` (Appendices A through F)
- [x] **Team Roles Matrix:** `docs/team_roles.md`
- [x] **Oral Demo Script:** `docs/demo_script.md` (5–7 minute cue sheet)
- [x] **Presentation Deck Content:** `docs/presentation_content.md` (15-slide breakdown)
- [x] **Viva Voce Examination Guide:** `docs/viva_questions.md` (25+ Q&As)
- [x] **Project Structure Breakdown:** `docs/project_structure.md`
- [x] **Honest System Limitations:** `docs/limitations.md`
- [x] **Final Audit Report:** `docs/final_project_audit.md`
- [x] **Verified Demo Scenarios:** `docs/demo_input.md`
- [x] **Screenshot Capture Guide:** `docs/screenshot_checklist.md`
- [x] **Documentation Master Index:** `docs/README.md`
- [x] **Repository README:** Root `README.md`

---

## 3. Student / Institutional Finalization Tasks (Manual Action Required)

The following items contain structured placeholders in `docs/pbl_report_content.md` and `docs/team_roles.md` that should be filled by the student team before final report printing:

- [ ] Enter exact **Student Names** and **Registration Numbers**.
- [ ] Enter **Department**, **Institution**, and **Academic Year**.
- [ ] Enter **Faculty Mentor Name** and **HOD Name**.
- [ ] Collect physical or digital **Mentor Signatures** on the Certificate page.
- [ ] Review and personalize the **Individual Reflections** in Chapter 7.
- [ ] Insert captured application **Screenshots** (using `docs/screenshot_checklist.md`) into final report and presentation slides.
