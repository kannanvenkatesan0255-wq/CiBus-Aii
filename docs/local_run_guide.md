# CIBUS-AI Local Execution & Testing Guide

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *Predict. Connect. Nourish.*  
**Environment:** Local Development (Windows / macOS / Linux)  

---

## 1. Verified Localhost URLs

| Component | Target URL | Description |
| :--- | :--- | :--- |
| **Frontend Web App (React 19 / Vite)** | **`http://localhost:5173`** | **Primary user interface to open in Google Chrome / Browser** |
| **Backend API (FastAPI / Uvicorn)** | **`http://127.0.0.1:8000`** | RESTful API service |
| **Interactive API Documentation** | **`http://127.0.0.1:8000/docs`** | FastAPI Swagger UI |
| **System Health Check Endpoint** | **`http://127.0.0.1:8000/health`** | Model readiness & health status |
| **Vite Health Proxy** | **`http://localhost:5173/health`** | Frontend proxy to backend health |

---

## 2. Prerequisites
- **Python:** 3.10 or higher (`python --version`)
- **Node.js:** v18.0 or higher (`node --version`)
- **Package Managers:** `pip` and `npm`

---

## 3. Step-by-Step Server Startup

### Step 1: Start the Backend Service
Open a terminal in the project directory:
```bash
# Navigate to backend directory
cd "k:\CiBus-Ai R\backend"

# (Optional) Install Python dependencies if not already installed
pip install -r requirements.txt

# Start FastAPI server on port 8000
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
*Expected Terminal Output:*
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

### Step 2: Start the Frontend Application
Open a second terminal:
```bash
# Navigate to frontend directory
cd "k:\CiBus-Ai R\frontend"

# (Optional) Install Node dependencies if not already installed
npm install

# Start Vite development server
npm run dev
```
*Expected Terminal Output:*
```
  VITE v5.4.11  ready in 1200 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

## 4. How to Test the End-to-End User Workflow in Your Browser

1. Open your web browser (e.g. Google Chrome) and navigate to:
   $$\text{\bf http://localhost:5173}$$

2. **Step 1: Predict Food Surplus**
   - On the Prediction Form, input:
     - **Day:** `Saturday`
     - **Weather:** `Rainy`
     - **Expected Customers:** `280`
     - **Meals Prepared:** `350`
     - **Festival:** `No`
     - **Service Type:** `Banquet`
     - **Kitchen Staff:** `12`
     - **Rating:** `4.5`
     - **Special Event:** `Yes`
   - Click **"Predict Surplus Meals"**.
   - The result card will display the forecasted surplus (approx. **115 meals**, ~32.8% of total prepared).

3. **Step 2: Match Compatible NGOs**
   - Click **"Proceed to NGO Matching"** (or scroll to the NGO Matching section).
   - Click **"Find Matching NGOs"**.
   - The system will allocate the ~115 surplus meals across nearby recipient organizations based on capacity.

4. **Step 3: Optimize Pickup Route**
   - Click **"Proceed to Route Planning"**.
   - Select a source dispatch facility or enter custom coordinates.
   - Click **"Generate Optimized Route"**.
   - View the waypoint itinerary, estimated distance (km), travel time, and the interactive SVG route map.

5. **Step 4: Update Impact Dashboard**
   - Click **"Log Activity & Update Dashboard"**.
   - Navigate to the **"Impact Dashboard"** tab in the top navigation bar.
   - View aggregated metrics: Total Surplus Planned, Total Meals Allocated, $CO_2$ Emissions Avoided ($2.5\text{ kg } CO_2\text{e/meal}$), Water Saved ($1,000\text{ L/meal}$), and verified ML evaluation metrics ($R^2 = 0.9543$, $\text{MAE} = 14.58\text{ meals}$).

---

## 5. Running Automated Verification Tests

To verify the complete codebase offline at any time, run:

```bash
# 1. Machine Learning Unit Tests (9/9 passed)
python -m unittest ai-engine/prediction/test_predict.py

# 2. Dataset Validation Checks (5/5 passed)
python ai-engine/dataset/validate_dataset.py

# 3. Backend & Security Test Suite (54/54 passed)
python -m unittest discover -s backend/tests -p "test_*.py"

# 4. Frontend Integration Tests (23/23 passed)
npm test --prefix frontend
```
**All 91 tests execute with a 100% pass rate.**

---

## 6. Common Issues & Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `Port 8000 already in use` | Another process is holding port 8000 | Kill existing process or run uvicorn on `--port 8001` and update `frontend/vite.config.js` proxy. |
| `Port 5173 already in use` | Another Vite server is running | Vite will automatically offer port 5174; update browser URL to `http://localhost:5174`. |
| `Model artifact missing` | `.pkl` file not found | Ensure working directory is project root or backend directory. Artifacts reside in `ai-engine/models/`. |
| `CORS Error in Browser` | Backend not running or origin mismatch | Ensure backend is started at `127.0.0.1:8000`. Default CORS origins include `localhost:5173`. |

---

## 7. How to Stop the Servers

In each terminal window where the server is running, press:
```bash
Ctrl + C
```
