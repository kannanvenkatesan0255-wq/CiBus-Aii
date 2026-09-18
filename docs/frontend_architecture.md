# CIBUS-AI Frontend Architecture & UI Design

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *"Predict. Connect. Nourish."*  
**Document:** Frontend Architecture & Design Specification  
**Date:** September 2026  

---

## 1. Frontend Objective
The CIBUS-AI frontend is engineered as a responsive, reactive single-page dashboard built with **React** and **Vite**. It provides dining establishments and catering services with a streamlined interface to input pre-service operational metrics and receive instantaneous AI-generated food surplus forecasts.

---

## 2. Component Hierarchy & Flow

```
┌─────────────────────────────────────────────────────────────┐
│                          App.jsx                            │
│  (State: prediction, error, isLoading, handlePredict/Reset) │
└──────┬───────────────────────┬───────────────────────┬──────┘
       │                       │                       │
       ▼                       ▼                       ▼
┌──────────────┐       ┌──────────────┐        ┌──────────────┐
│  Header.jsx  │       │   Hero.jsx   │        │  Footer.jsx  │
│(HealthStatus)│       └──────────────┘        └──────────────┘
└──────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                 Main Prediction Layout                      │
│                  (prediction-grid)                          │
├──────────────────────────────┬──────────────────────────────┤
│      PredictionForm.jsx      │        ResultCard.jsx        │
│  * 9 Input Form Controls     │  * Surplus Count Display     │
│  * Client-Side Validation    │  * Logistics Advisory        │
│  * Submit / Reset Actions    │  * Model Metadata Table      │
└──────────────────────────────┴──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┬──────────────────────────────┐
│       HowItWorks.jsx         │      FutureModules.jsx       │
│  * 5-Step Pipeline Overview  │  * NGO Matching & Routing    │
└──────────────────────────────┴──────────────────────────────┘
```

---

## 3. UI Components Breakdown

| Component | File Path | Responsibilities |
| :--- | :--- | :--- |
| **`Header`** | `src/components/Header.jsx` | Renders project branding, institutional PBL badge, and embeds the `HealthStatus` monitor. |
| **`HealthStatus`** | `src/components/HealthStatus.jsx` | Queries `GET /health` with a non-aggressive heartbeat (30s) to display real-time backend and ML artifact availability. |
| **`Hero`** | `src/components/Hero.jsx` | Explains the mission of the Food Surplus Prediction module and frames the problem context. |
| **`PredictionForm`** | `src/components/PredictionForm.jsx` | Houses the 9 input form controls, performs pre-flight boundary validation, and emits `onSubmit` events. |
| **`ResultCard`** | `src/components/ResultCard.jsx` | Renders a placeholder in idle state, a processing animation during submission, and a prominent quantitative card upon forecast arrival. |
| **`HowItWorks`** | `src/components/HowItWorks.jsx` | Outlines the end-to-end operational flow from kitchen parameter entry to redistribution dispatch. |
| **`FutureModules`** | `src/components/FutureModules.jsx` | Outlines the post-PBL roadmap (NGO pairing, routing heuristics, GIS tracking) to clearly mark feature boundaries. |
| **`Footer`** | `src/components/Footer.jsx` | Displays institutional attribution for Chennai Institute of Technology. |

---

## 4. Operational Form Parameters & Validation Rules

| Field Name | HTML Element | Data Type | Permitted Values / Constraints |
| :--- | :---: | :---: | :--- |
| `Day` | `<select>` | `string` | `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`, `Sunday` |
| `Weather` | `<select>` | `string` | `Sunny`, `Cloudy`, `Rainy`, `Stormy` |
| `Customers_Forecast` | `<input type="number">` | `integer` | $\ge 0$ (Expected diner footfall) |
| `Meals_Prepared` | `<input type="number">` | `integer` | $\ge 0$ (Total batch-cooked portions) |
| `Festival` | `<select>` | `string` | `No`, `Diwali`, `Eid`, `Christmas`, `New Year` |
| `Event_Type` | `<select>` | `string` | `Regular`, `Buffet`, `Corporate`, `Banquet` |
| `Staff_Count` | `<input type="number">` | `integer` | $\ge 1$ (Active kitchen & floor staff) |
| `Avg_Rating` | `<input type="number">` | `float` | $1.0 \le \text{rating} \le 5.0$ |
| `Special_Event` | `<select>` | `integer` | `0` (Standard) or `1` (Special / VIP Booking) |

> **Strict Data Leakage Rule:** `Meals_Sold` is strictly non-existent across all form inputs, state objects, and network payloads.

---

## 5. API Communication Layer (`predictionService.js`)

The service layer cleanly decouples UI views from HTTP endpoints:
- **`predictSurplus(formData)`**: Constructs a sanitized JSON payload, submits `POST /api/predict`, and catches HTTP 400/422/500 errors.
- **`checkBackendHealth()`**: Calls `GET /health` to verify server responsiveness.
- **`getModelMetadata()`**: Calls `GET /api/model-info` to fetch active model evaluation statistics.

---

## 6. Error Handling & Edge Cases

| Scenario | UI Behavior | User Message |
| :--- | :--- | :--- |
| Missing required field | Highlights form & aborts fetch | *"Please fill in all required operational fields."* |
| Negative meal/customer count | Highlights form & aborts fetch | *"Meals Prepared / Customers Forecast must be non-negative."* |
| Rating out of range | Highlights form & aborts fetch | *"Average Rating must be between 1.0 and 5.0."* |
| FastAPI backend offline | Renders error card in Result panel | *"Unable to connect to the CIBUS-AI prediction backend. Please ensure FastAPI is running on port 8000."* |
| Server 500 or validation error | Displays server message cleanly | Sanitized server error detail without exposing internal stack traces. |

---

## 7. Verification & Automated Testing

The frontend is verified via `frontend/tests/frontend_test.cjs`:
1. Full directory and component file existence.
2. Form schema completeness (all 9 operational features).
3. Data leakage audit confirming zero presence of `Meals_Sold`.
4. Payload structure alignment with backend Pydantic models.
5. Result card rendering and avoidance of false accuracy claims.
6. Form reset and state restoration.
7. Vite production bundle compilation (`npm run build`).

All 7 automated tests execute with a 100% pass rate.
