# Project Overview: CIBUS-AI

**Tagline:** *Predict. Connect. Nourish.*  
**Domain:** Artificial Intelligence & Machine Learning Applied to Sustainable Food Systems  
**Project Category:** College Machine Learning Project-Based Learning (PBL)

---

## 1. Project Background
Food loss and waste is a major economic, environmental, and humanitarian challenge. Commercial dining establishments, university canteens, catering services, and restaurants routinely produce edible surpluses because demand is subject to unpredictable daily dynamics—such as changing weather conditions, calendar events, fluctuations in attendance, and operational variations.

Currently, redistribution initiatives operate reactively: donations are negotiated only after surplus food has physically remained unconsumed at closing time. This leaves a narrow time window for pickup, safe temperature-controlled transport, and redistribution to beneficiaries before food deteriorates or passes safety thresholds.

CIBUS-AI introduces an AI-driven, predictive intervention that forecasts anticipated surplus meals hours before service closure, turning food redistribution from a rushed, reactive scramble into an organized, proactive logistics operation.

---

## 2. Driving Question
> *"How can historical operational indicators, environmental factors, and advance footfall forecasts be leveraged via Supervised Machine Learning to accurately predict pre-service food surplus, enabling timely redistribution to community organizations without data leakage?"*

---

## 3. Technical Objective
1. Formulate the food surplus estimation problem as a Supervised Machine Learning Regression task.
2. Design a clean, leakage-free data schema relying strictly on operational parameters known prior to sales conclusion.
3. Build an end-to-end Python ML pipeline encompassing data preprocessing, categorical encoding, baseline model comparison, Random Forest regression modeling, residual analysis, and model persistence.
4. Establish standardized evaluation protocols utilizing Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and Coefficient of Determination ($R^2$).

---

## 4. Learning Objectives (PBL Focus)
- **Problem Formulation:** Identifying why food surplus estimation maps to continuous regression rather than discrete classification.
- **Preventing Data Leakage:** Developing awareness of temporal and structural leakage risks (specifically why post-facto metrics like `Meals_Sold` invalidate predictive utility).
- **Ensemble Learning:** Understanding decision tree ensembles, bagging mechanics, non-linear feature interaction modeling, and feature importance rankings.
- **Model Evaluation Competence:** Correctly interpreting regression evaluation metrics ($R^2$ vs. classification accuracy) and diagnosing residual error distributions.
- **Production Pipeline Organization:** Structuring clean, modular, and reproducible machine learning repositories suitable for academic defense and production scaling.

---

## 5. Current Scope
The current phase of the project is strictly concentrated on:
- Formalizing the mathematical and operational foundation of the ML engine.
- Designing the project architecture, directory structures, and documentation.
- Defining the data schema, preprocessing steps, and training workflows.
- Establishing testable evaluation metrics and baseline comparisons.

---

## 6. Current Limitations
- **No Live Sensor Data:** Relies on structured tabular operational inputs rather than automated IoT kitchen scale feeds.
- **Pre-Service Estimate Only:** Real-time during-service kitchen replenishments or mid-shift anomalies are not dynamically streamed into the current static batch prediction interface.
- **Simulated Domain Distribution:** Initial datasets will be statistically modeled synthetic samples reflecting realistic catering scenarios prior to physical enterprise pilot deployments.

---

## 7. Future Scope
Following successful validation of the core predictive ML engine, future phases will expand into:
1. **Redistribution Logistics & NGO Matching:** Real-time distance and capacity pairing algorithms.
2. **Dynamic Route Optimization:** Multi-stop transport route calculation for food collection volunteers.
3. **Automated Volunteer Allocation:** Notification and dispatch routing engine.
4. **Full-Stack Application & Dashboard:** Web interface, NGO portals, and Google Maps integration for live tracking.
