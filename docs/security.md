# CIBUS-AI Security, Error Handling & Production Hardening Architecture
**File:** `docs/security.md`  
**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *“Predict. Connect. Nourish.”*  

---

## 1. Security Architecture Overview

CIBUS-AI is designed with defensive programming principles to ensure stability, information leak prevention, resilient error recovery, and clear separation between local academic demonstration and enterprise production environments.

```
+-------------------------------------------------------------------------+
|                        Client Layer (Vite / React)                      |
|  - React ErrorBoundary (Catches UI exceptions without blank screens)    |
|  - Zero dangerouslySetInnerHTML (XSS Prevention)                        |
|  - Input Validation & Button Debouncing (Duplicate Submit Guard)        |
|  - Configurable VITE_API_BASE_URL via .env.example                      |
+-------------------------------------------------------------------------+
                                     |
                                     | Validated CORS (Whitelist)
                                     v
+-------------------------------------------------------------------------+
|                     API Gateway Layer (FastAPI)                         |
|  - RequestValidationError Handler (Sanitized Field Error Payloads)      |
|  - Centralized 500 Handler (Zero Stack Trace or Path Leakage)           |
|  - Environment-based CORS Origins (CORS_ORIGINS)                        |
|  - Pydantic v2 Schema Enforcement with Finite Number Checks (No NaN/Inf)|
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                    Core Services & Data Safety                          |
|  - Machine Learning Engine: Controlled static load (No dynamic unpickle)|
|  - Path Traversal Guard: Canonical root directory resolution            |
|  - Local Demonstration Storage: Isolated JSON Activity Ledger           |
+-------------------------------------------------------------------------+
```

---

## 2. Environment Configuration & Secret Management

- **Template-Driven Configuration:** Environment variables are defined via `.env.example` templates at root, `backend/`, and `frontend/`.
- **Git Ignore Security:** `.env` and `.env.*` files are explicitly excluded in `.gitignore` to prevent credential exposure:
  ```gitignore
  .env
  .env.*
  !.env.example
  .env.*.local
  ```
- **Zero Committed Secrets:** The repository contains zero hardcoded API keys, passwords, database connection strings, or cloud tokens.

---

## 3. Cross-Origin Resource Sharing (CORS) Hardening

FastAPI dynamically parses allowed origins from the `CORS_ORIGINS` environment variable rather than using wildcard `allow_origins=["*"]`:

```python
raw_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"
)
ALLOWED_ORIGINS: List[str] = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
```

---

## 4. Input Validation & Boundary Enforcement

Every public REST endpoint enforces strict Pydantic v2 constraints:

| Endpoint | Input Constraints & Defensive Rules |
| :--- | :--- |
| `POST /api/predict` | $0 \le \text{Customers\_Forecast} \le 50,000$; $0 \le \text{Meals\_Prepared} \le 100,000$; $1 \le \text{Staff\_Count} \le 1,000$; $1.0 \le \text{Avg\_Rating} \le 5.0$; Categorical validation for `Day`, `Weather`, `Festival`, `Event_Type`; Rejection of `Meals_Sold`. |
| `POST /api/match-ngos` | $0.0 \le \text{surplus} \le 100,000.0$; $-90.0 \le \text{lat} \le 90.0$; $-180.0 \le \text{lon} \le 180.0$; $1 \le \text{max\_matches} \le 20$. |
| `POST /api/optimize-route` | Valid origin coordinates; $1 \le \text{stops} \le 50$; Unique NGO IDs (rejection of duplicate IDs); Non-negative meal drop portions. |
| `POST /api/dashboard/activity` | Consistency assertion: $\text{Allocated Meals} \le \text{Predicted Surplus} + 0.01$; Non-negative stops, distances, and counts. |
| `GET /api/dashboard/recent` | Bounded pagination query: $1 \le \text{limit} \le 100$. |

### Finite Number Guard:
All floating-point numerical inputs are validated against `NaN` and `Infinity` (`math.isnan()` / `math.isinf()`) to prevent arithmetic corruption.

---

## 5. Information Leakage Prevention & Error Sanitization

### Global Exception Handlers (`backend/app/main.py`):
1. **Validation Error Sanitization (`RequestValidationError`):** Formats validation errors into concise field messages without leaking internal Python classes or line numbers.
2. **Unhandled Exception Guard (`Exception`):** Captures server-side errors, logs the stack trace internally using Python standard `logging`, and returns a safe sanitized response:
   ```json
   {
     "detail": "An unexpected server error occurred. Please try again later."
   }
   ```
3. **Safe Health Diagnostics (`GET /health`):** Verifies ML model and preprocessor readiness without exposing host system paths, disk directories, or runtime configurations.

---

## 6. File System & Model Deserialization Safety

- **Controlled Path Resolution:** Model files (`food_surplus_model.pkl`, `food_surplus_preprocessor.pkl`), evaluation metadata (`final_results.json`), NGO records (`ngos.csv`), and activity logs (`activity_history.json`) are resolved using immutable project-relative constants (`Path(__file__).resolve().parent...`).
- **No Dynamic User-Supplied Paths:** No API parameter can define or manipulate filesystem paths, eliminating Path Traversal (`../`) vulnerabilities.
- **Trusted Pickles Only:** The application loads only the pre-compiled, frozen model files generated by the local training pipeline. Dynamic pickle uploading from API clients is strictly forbidden.

---

## 7. Frontend Hardening & XSS Prevention

- **React ErrorBoundary (`ErrorBoundary.jsx`):** Wraps the root component tree. If an unexpected JavaScript rendering error occurs, it catches the error and displays a structured recovery UI with a "Reload Application" action, preventing blank screen failures.
- **Zero `dangerouslySetInnerHTML`:** All dynamic text (NGO names, addresses, prediction outcomes) is rendered via standard React JSX text nodes, eliminating DOM-based Cross-Site Scripting (XSS).
- **Idempotency & Duplicate Prevention:** The **Record Redistribution Plan** button disables immediately upon submission to prevent accidental duplicate activity records.

---

## 8. Authentication Scope & Future Roadmap

### Prototype Scope Decision:
Because CIBUS-AI is a college Machine Learning Project-Based Learning (PBL) prototype designed for single-operator lab evaluation and educational demonstration on synthetic data, multi-tenant authentication infrastructure (JWT, OAuth2, session databases) is **intentionally outside the current prototype scope**.

### Production Hardening Roadmap:
For future commercial deployment beyond the academic prototype:
1. **Role-Based Access Control (RBAC):** Distinct roles for Commercial Food Donors, Partner NGO Coordinators, and Dispatch Drivers.
2. **Secure Authentication:** OAuth2 with JWT tokens, short-lived session cookies, and multi-factor authentication (MFA).
3. **Transport Security:** Strict HTTPS (TLS 1.3) with HSTS headers.
4. **Rate Limiting:** Distributed token-bucket rate limiting (e.g., Redis + SlowAPI).
5. **Database Storage:** Migration from JSON activity files to a managed relational PostgreSQL database with row-level security.
