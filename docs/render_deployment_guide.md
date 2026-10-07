# CIBUS-AI: Production Deployment Guide for Render

**Project:** CIBUS-AI – AI-Powered Food Surplus Prediction and Redistribution Network  
**Platform:** Render ([render.com](https://render.com))  
**Configuration File:** [`render.yaml`](../render.yaml)  

---

## 1. System Deployment Architecture

```
┌────────────────────────────────────────────────────────┐
│               Render Static Site (Frontend)            │
│  - Runtime: Static (Node.js build -> static CDN)       │
│  - Build: cd frontend && npm install && npm run build  │
│  - Publish Directory: frontend/dist                    │
│  - Environment: VITE_API_BASE_URL, VITE_MAPBOX_TOKEN   │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTPS REST API Requests
                           ▼
┌────────────────────────────────────────────────────────┐
│              Render Web Service (Backend)              │
│  - Runtime: Python (FastAPI + Uvicorn)                 │
│  - Build: pip install -r backend/requirements.txt      │
│  - Start: cd backend && uvicorn app.main:app           │
│           --host 0.0.0.0 --port $PORT                  │
│  - Environment: FRONTEND_URL, PORT, ENVIRONMENT        │
└──────────────────────────┬─────────────────────────────┘
                           │ Loads pre-trained model
                           ▼
┌────────────────────────────────────────────────────────┐
│               Trained ML Model Artifacts               │
│  - ai-engine/models/food_surplus_model.pkl (37.1 MB)   │
│  - ai-engine/models/label_encoders.pkl (3.2 KB)        │
│  (Tracked directly in Git; no rebuild on startup)      │
└────────────────────────────────────────────────────────┘
```

---

## 2. Environment Variables Specification

Only the environment variables that the code actually requires are listed below. No secrets are stored in code or configuration files.

### Backend Web Service

| Variable | Required | Default / Example | Purpose |
| :--- | :---: | :--- | :--- |
| **`PORT`** | Auto | `10000` (Render injected) | Port bound by Uvicorn server in production container. |
| **`ENVIRONMENT`** | Yes | `production` | Sets application mode and disables debug reloaders. |
| **`FRONTEND_URL`** | Yes | `https://cibus-ai-frontend.onrender.com` | Configures FastAPI `CORSMiddleware` allow_origins. |
| **`CORS_ORIGINS`** | Optional | `http://localhost:5173,http://127.0.0.1:5173` | Additional trusted development or preview origins. |

### Frontend Static Site

| Variable | Required | Default / Example | Purpose |
| :--- | :---: | :--- | :--- |
| **`VITE_API_BASE_URL`** | Yes | `https://cibus-ai-backend.onrender.com` | Public base URL of the deployed FastAPI backend service. |
| **`VITE_MAPBOX_TOKEN`** | Optional | `pk.eyJ1Ijoi...` | Public Mapbox token enabling interactive Mapbox tile rendering. Falls back to deterministic SVG if omitted. |

---

## 3. Render Blueprint Setup Steps

1. **Connect GitHub Repository:**
   - Log into [Render Dashboard](https://dashboard.render.com).
   - Click **New +** $\rightarrow$ **Blueprint**.
   - Select the `CiBus-Aii` repository.

2. **Render Automatic Detection:**
   - Render detects `render.yaml` at the root and plans two services:
     - `cibus-ai-backend` (Web Service)
     - `cibus-ai-frontend` (Static Site)

3. **Configure Environment Variables:**
   - On `cibus-ai-backend`: Set `FRONTEND_URL` to your frontend service URL once provisioned.
   - On `cibus-ai-frontend`: Set `VITE_API_BASE_URL` to your backend URL (e.g. `https://cibus-ai-backend.onrender.com`) and `VITE_MAPBOX_TOKEN` to your Mapbox token.

4. **Deploy:**
   - Click **Apply**. Render will automatically build both services.

---

## 4. Verification & Health Checks

Once deployed, verify the endpoints:

1. **Health Check:**
   ```bash
   curl -s https://cibus-ai-backend.onrender.com/health
   # Response: {"status":"healthy","model_loaded":true,"preprocessor_loaded":true,"version":"1.0.0"}
   ```

2. **Prediction Endpoint:**
   ```bash
   curl -X POST https://cibus-ai-backend.onrender.com/api/predict \
     -H "Content-Type: application/json" \
     -d '{"Day":"Wednesday","Weather":"Sunny","Customers_Forecast":200,"Meals_Prepared":500,"Festival":"No","Event_Type":"Regular","Staff_Count":10,"Avg_Rating":4.0,"Special_Event":0}'
   ```

3. **Frontend Application:**
   - Open `https://cibus-ai-frontend.onrender.com` in Google Chrome or any modern browser.
   - Enter operational parameters and click **Predict Food Surplus**.
   - Review redistribution matching, route optimization, and impact metrics.
