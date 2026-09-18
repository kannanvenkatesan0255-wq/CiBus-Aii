# CIBUS-AI

> **“Predict. Connect. Nourish.”**  
> *AI-Based Food Surplus Prediction and Redistribution Network*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.0-61DAFB.svg)](https://react.dev/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-F7931E.svg)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/Tests-91%20Passed%20(100%25)-brightgreen.svg)]()

---

## 1. Problem Statement & Overview

Commercial food establishments (restaurants, hotels, canteens, and catering services) frequently generate substantial volumes of edible food surplus due to unpredictable customer footfall, weather shifts, and rigid batch preparation schedules. Simultaneously, local relief organizations and shelters face persistent food insecurity.

Conventional food redistribution suffers from a major operational bottleneck: **surplus is recognized reactively after business hours**, when it is too late to coordinate volunteer transport and ensure food safety.

**CIBUS-AI** resolves this through proactive, AI-driven decision support:
1. **Predict:** Forecasts surplus meal counts *before meal service begins* using a trained `RandomForestRegressor`.
2. **Connect:** Automatically matches surplus food with nearby NGOs based on distance and daily capacity.
3. **Nourish:** Generates an optimized pickup trajectory using Haversine distance heuristics, tracking environmental impact ($CO_2$ and water savings) on an interactive dashboard.

---

## 2. Key System Features

- **Pre-Service ML Forecasting:** Predicts surplus meals from operational inputs (forecast footfall, weather, day, events, staff).
- **Target Leakage Prevention:** `Meals_Sold` is strictly excluded from inputs to ensure valid pre-service forecasting.
- **Rule-Based NGO Matching:** Filters candidate NGOs within a 15 km radius and executes greedy meal capacity allocation.
- **Haversine Route Optimization:** Solves multi-stop pickup ordering via Nearest Neighbor heuristics with travel time estimations.
- **Interactive Single-Page UI:** Built with React 19 and Tailwind CSS featuring a step-by-step workflow wizard and SVG route map.
- **Impact Analytics Dashboard:** Quantifies aggregate meals saved, $CO_2$ emissions avoided ($2.5\text{ kg } CO_2\text{e/meal}$), and water conserved ($1,000\text{ L/meal}$).
- **Zero-Dependency Persistence:** Persists redistribution sessions to local JSON storage for instant local demonstration.

---

## 3. System Architecture & Tech Stack

```
                         RESTAURANT / DONOR
                                 │
                                 ▼
                     REACT FRONTEND (VITE/SPA)
              (Prediction UI, NGO Table, SVG Route, Dashboard)
                                 │  HTTP / JSON REST
                                 ▼
                          FASTAPI BACKEND
             (Pydantic Validation, CORS, Activity Logger)
            ┌────────────────────┼────────────────────┐
            ▼                    ▼                    ▼
     PREDICTION API        NGO MATCHING API     DASHBOARD API
            │                    │                    │
            ▼                    ▼                    ▼
     ML MODEL (.pkl)        SYNTHETIC NGOS     ANALYTICS SERVICE
    (RandomForestRegressor) (Capacity Rules)  (Offset Counters)
            │                    │
            └──────────┬─────────┘
                       ▼
             ROUTE OPTIMIZER (Haversine / Nearest Neighbor)
                       │
                       ▼
             LOCAL ACTIVITY LOG (backend/data/activity_log.json)
```

### Technology Stack
- **AI/ML Engine:** Python, Scikit-Learn, Pandas, NumPy, Joblib
- **Backend API:** FastAPI, Uvicorn, Pydantic
- **Frontend:** React 19, Vite, Tailwind CSS, Lucide React, Axios
- **Testing:** Python `unittest`, Node.js automated test suites

---

## 4. Machine Learning Results

Evaluated on an unseen 20% test partition (1,600 samples) from an 8,000-sample synthetic dataset:

| Metric | Baseline Model | Final Refined Model | Unit / Interpretation |
| :--- | :--- | :--- | :--- |
| **Mean Absolute Error (MAE)** | 15.1200 | **14.5793** | Average deviation in surplus meals |
| **Root Mean Squared Error (RMSE)** | 21.4500 | **20.6869** | Residual standard error |
| **Coefficient of Determination ($R^2$)** | 0.9521 | **0.9543** | Explains 95.43% of surplus variance |

*Top Predictive Features:* `Meals_Prepared` (48.2%), `Customers_Forecast` (26.7%), `Day` (8.5%), `Festival`/`Event_Type` (6.8%), `Weather`/`Staff` (9.8%).

---

## 5. Quickstart & Installation

### Prerequisites
- Python 3.10+
- Node.js v18+ and `npm`
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/kannanvenkatesan0255-wq/CiBus-Aii.git
cd "CiBus-Ai R"
```

### 2. Backend Setup & Startup
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI development server (runs at http://localhost:8000)
uvicorn main:app --reload --port 8000
```
*Interactive API Swagger Documentation is accessible at [http://localhost:8000/docs](http://localhost:8000/docs).*

### 3. Frontend Setup & Startup
```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start Vite development server (runs at http://localhost:5173)
npm run dev
```
*Open [http://localhost:5173](http://localhost:5173) in your web browser to interact with CIBUS-AI.*

---

## 6. Running Automated Tests

The repository contains **91 automated test cases** across 4 test suites:

```bash
# 1. Run Machine Learning unit tests (9 tests)
python -m unittest ai-engine/prediction/test_predict.py

# 2. Run Dataset schema validation checks (5 checks)
python ai-engine/dataset/validate_dataset.py

# 3. Run Backend, NGO matching, Routing & Security tests (54 tests)
python -m unittest discover -s backend/tests -p "test_*.py"

# 4. Run Frontend verification tests (23 tests)
npm test --prefix frontend
```
**Total Test Results: 91 / 91 Passed (100% Pass Rate).**

---

## 7. Project Documentation Index

Comprehensive academic and technical documentation is maintained in [`docs/`](docs/):
- **[Documentation Index](docs/README.md)**
- **[PBL Academic Report](docs/pbl_report_content.md)**
- **[Final Architecture](docs/final_architecture.md)**
- **[IEEE References](docs/references.md)**
- **[Project Appendix](docs/appendix.md)**
- **[Oral Demo Script](docs/demo_script.md)**
- **[Presentation Content (15 Slides)](docs/presentation_content.md)**
- **[Viva Voce Exam Guide (25+ Q&As)](docs/viva_questions.md)**
- **[Project Limitations](docs/limitations.md)**
- **[Final Project Audit](docs/final_project_audit.md)**

---

## 8. System Boundaries & Limitations

- **Synthetic Data:** The dataset and recipient directory are synthetic, designed for academic demonstration.
- **Routing Heuristic:** Route optimization uses straight-line Haversine math and nearest-neighbor ordering rather than live road turn-by-turn navigation or real-time traffic data.
- **Planning vs. Delivery:** CIBUS-AI provides software-based *redistribution planning*; it does not execute physical food transport or confirm live deliveries.

---

## 9. Team Roles & Academic Information

| Role | Member | Responsibilities |
| :--- | :--- | :--- |
| **ML & Data Lead** | `[STUDENT 1 NAME]` | Dataset generation, preprocessing, model training & evaluation |
| **Backend Architect** | `[STUDENT 2 NAME]` | FastAPI REST services, NGO matching, Haversine routing |
| **Frontend Developer** | `[STUDENT 3 NAME]` | React 19 SPA, SVG map visualization, impact dashboard |
| **QA & Integration** | `[STUDENT 4 NAME]` | End-to-end integration, security verification, automated testing |

**Faculty Mentor:** `[FACULTY MENTOR NAME]`, `[DESIGNATION]`, `[DEPARTMENT]`  
**Institution:** `[COLLEGE / UNIVERSITY NAME]`
