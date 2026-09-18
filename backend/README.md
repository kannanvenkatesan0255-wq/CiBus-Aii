# CIBUS-AI Backend API & Integration Layer

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *"Predict. Connect. Nourish."*  
**Module:** Backend REST API (FastAPI)  
**Version:** `1.0.0`

---

## 1. Backend Purpose
The CIBUS-AI backend serves as the production integration layer connecting external clients (web frontends, mobile apps, POS systems) to the pre-trained Machine Learning prediction engine. 

It provides high-performance, asynchronous RESTful endpoints for real-time surplus food forecasting while enforcing strict data validation, zero data leakage, and clean error handling without modifying or retraining the underlying Random Forest model.

---

## 2. Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Application                       │
│             (Web Frontend / React / Mobile App)             │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP POST /api/predict (JSON)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                       FastAPI Router                        │
│                 (backend/app/main.py)                       │
└──────────────────────────────┬──────────────────────────────┘
                               │ Pydantic Validation (schemas.py)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  Prediction Service Layer                   │
│        (backend/app/services/prediction_service.py)         │
└──────────────────────────────┬──────────────────────────────┘
                               │ Direct Call (Zero Retraining)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               Existing CIBUS-AI ML Engine                   │
│             (ai-engine/prediction/predict.py)               │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────────┐┌──────────────────────────────┐
│  Serialized Preprocessor     ││   Serialized ML Model        │
│ (food_surplus_preprocessor)  ││   (food_surplus_model.pkl)   │
└──────────────────────────────┘└──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               JSON Response (Predicted Meals)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (v0.110+)
- **ASGI Web Server:** [Uvicorn](https://www.uvicorn.org/) (v0.28+)
- **Data Validation & Schemas:** [Pydantic](https://docs.pydantic.dev/) v2 (v2.6+)
- **HTTP Client Testing:** [HTTPX](https://www.python-httpx.org/) (v0.27+)
- **ML Integration:** scikit-learn (`RandomForestRegressor`), pandas, numpy, joblib

---

## 4. Folder Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application entry point, CORS & health route
│   ├── schemas.py                  # Pydantic schemas (Request, Response, ModelInfo, Health)
│   ├── services/
│   │   ├── __init__.py
│   │   └── prediction_service.py   # Interface to ai-engine/prediction/predict.py
│   └── routes/
│       ├── __init__.py
│       └── prediction.py           # REST endpoints (/api/predict, /api/model-info)
├── tests/
│   └── test_prediction_api.py      # Automated TestClient test suite
├── requirements.txt                # Backend package dependencies
└── README.md                       # Backend documentation
```

---

## 5. API Endpoints

| Endpoint | Method | Description | Auth |
| :--- | :---: | :--- | :---: |
| `/` | `GET` | API root with service metadata & navigation | None |
| `/health` | `GET` | Health status and ML artifact readiness check | None |
| `/api/predict` | `POST` | Real-time surplus meal prediction | None |
| `/api/model-info` | `GET` | Factual model specification and evaluation metrics | None |
| `/docs` | `GET` | Interactive Swagger UI documentation | None |
| `/redoc` | `GET` | ReDoc API specifications | None |

---

## 6. Request & Response Formats

### `POST /api/predict`

#### Request Payload (JSON):
```json
{
  "Day": "Friday",
  "Weather": "Rainy",
  "Customers_Forecast": 450,
  "Meals_Prepared": 600,
  "Festival": "Diwali",
  "Event_Type": "Buffet",
  "Staff_Count": 25,
  "Avg_Rating": 4.5,
  "Special_Event": 1
}
```

#### Response Payload (JSON):
```json
{
  "predicted_surplus_meals": 230.38,
  "model_name": "RandomForestRegressor (Tuned, max_depth=15, n_estimators=200)",
  "status": "success",
  "input_summary": {
    "day": "Friday",
    "weather": "Rainy",
    "customers_forecast": 450,
    "meals_prepared": 600,
    "event_type": "Buffet",
    "festival": "Diwali",
    "staff_count": 25,
    "avg_rating": 4.5,
    "special_event": 1
  },
  "recommended_action": "High surplus forecast (~230 meals). Activate CIBUS-AI regional NGO redistribution protocol and dispatch volunteer couriers."
}
```

---

## 7. Data Validation & Leakage Prevention Rules

1. **Strict Data Leakage Rejection:** Any request payload containing `Meals_Sold` is rejected immediately with HTTP 422 (`DATA LEAKAGE REJECTION`).
2. **Domain Range Validation:**
   - `Customers_Forecast` $\ge 0$
   - `Meals_Prepared` $\ge 0$
   - `Staff_Count` $\ge 1$
   - `Avg_Rating` between $1.0$ and $5.0$
3. **Categorical Sanitization:** Automatically normalizes capitalization and validates:
   - `Day`: `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`, `Sunday`
   - `Weather`: `Sunny`, `Cloudy`, `Rainy`, `Stormy`
   - `Festival`: `No`, `Diwali`, `Eid`, `Christmas`, `New Year`
   - `Event_Type`: `Regular`, `Buffet`, `Corporate`, `Banquet`

---

## 8. Installation & Execution Guide

### Step 1: Install Dependencies
From the repository root or backend directory:
```bash
pip install -r backend/requirements.txt
```

### Step 2: Start the FastAPI Server
From the repository root:
```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Or from the `backend/` directory:
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 3: Access Interactive Documentation
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 9. Running Tests

Execute the automated test suite verifying all 10 endpoint scenarios:
```bash
python -m unittest backend/tests/test_prediction_api.py
```

---

## 10. Future Frontend Integration

The backend is pre-configured with CORS middleware allowing connections from standard development frontend ports (`http://localhost:3000`, `http://localhost:5173`, `http://127.0.0.1:3000`, `http://127.0.0.1:5173`). In future stages, the React dashboard will communicate directly with `POST /api/predict` to provide real-time dining surplus forecasts and trigger NGO dispatch logistics.
