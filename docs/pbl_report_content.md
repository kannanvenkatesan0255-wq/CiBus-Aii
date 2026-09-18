# CIBUS-AI: Machine Learning PBL Project Report

**Project Title:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *Predict. Connect. Nourish.*  
**Institution:** Chennai Institute of Technology  
**Department:** Computer Science & Engineering / AI & Data Science  
**Course:** Machine Learning Project-Based Learning (PBL) Track  

---

# CHAPTER 1 — INTRODUCTION

## 1.1 Background
Food surplus and waste across commercial hospitality, university dining halls, institutional cafeterias, and event catering represents a massive socioeconomic and ecological challenge. Every day, kitchens prepare buffer quantities of perishable food to safeguard against stockouts; however, unpredicted fluctuations in attendance, weather disruptions, and event schedules regularly lead to large quantities of edible surplus.

Currently, surplus food recovery operates reactively: food rescue non-governmental organizations (NGOs) and charities are alerted only after service shuts down. This creates an unmanageably narrow operational window (typically 1 to 2 hours) to inspect, pack, transport, and distribute meals before perishability limits expire.

Machine learning offers an opportunity to transform this workflow from reactive crisis management into proactive logistics planning. By forecasting anticipated food surplus volume hours *before* meal consumption concludes, catering managers and NGO dispatchers can pre-schedule transport routes, verify volunteer availability, and reserve shelter capacity well in advance.

## 1.2 Driving Question
> *"How can pre-service operational indicators, environmental factors, and advance footfall forecasts be modeled using Supervised Machine Learning Regression to accurately predict food surplus volume before service conclusion, without incurring data leakage?"*

## 1.3 Objectives
- **Technical Objectives:**
  1. Formulate surplus meal forecasting as a continuous regression task.
  2. Implement an end-to-end Python pipeline using `scikit-learn` and `pandas`.
  3. Enforce strict data-leakage prevention by omitting post-service indicators (`Meals_Sold`).
  4. Provide reusable programmatic and CLI inference interfaces.
- **Machine Learning Objectives:**
  1. Train and evaluate an ensemble `RandomForestRegressor` capable of capturing non-linear interactions without overfitting.
  2. Perform cross-validated hyperparameter optimization on tree depth, split criteria, and feature sub-sampling.
  3. Extract and interpret Mean Decrease in Impurity (MDI) feature importances.
  4. Perform residual diagnostics to verify model calibration across the target domain.
- **PBL Learning Objectives:**
  1. Master the complete ML engineering lifecycle: problem formulation, data synthesis, preprocessing, baseline benchmarking, iterative tuning, and diagnostic evaluation.
  2. Maintain rigorous version control and reproducible execution standards via Git/GitHub.
  3. Defend empirical trade-offs, model limitations, and metric interpretations during academic viva.

## 1.4 Scope and Limitations

### Current ML Scope *(Implemented & Validated)*:
- **Synthetic Behavioral Dataset:** 8,000 structured operational shift records.
- **Leakage-Safe Feature Set:** 9 pre-service operational, calendar, and environmental attributes (25 transformed dimensions).
- **Core ML Modeling:** Random Forest Regressor with 3-Fold Cross-Validation tuning.
- **Model Evaluation:** Held-out test set ($N = 1,600$) evaluation with MAE, RMSE, and $R^2$.
- **Inference Engine:** Standalone CLI and Python API with defensive input validation.

### Future Scope *(Planned Next Phases)*:
- Real-time IoT smart scale integration and live kitchen telemetry.
- Dynamic NGO matching algorithms based on dietary constraints and travel distance.
- Vehicle route optimization and multi-stop dispatch.
- Full-stack web dashboard (React/FastAPI) with interactive Google Maps live tracking.

---

# CHAPTER 2 — CONCEPT EXPLORATION

## 2.1 Related Approaches & Literature
To inform the architectural design of CIBUS-AI, existing approaches in demand forecasting, food waste reduction, and ensemble regression were explored.

| Source | Approach / Domain | Technology / ML Method | Key Finding | Relevance to CIBUS-AI |
| :--- | :--- | :--- | :--- | :--- |
| *Food Waste Analytics in Hospitality* `[TODO – COMPLETE REFERENCE DETAILS]` | Commercial buffet waste tracking | Multiple Linear Regression vs Decision Trees | Non-linear tree models outperformed linear baselines in handling attendance fluctuations. | Justified selecting tree ensembles over simple linear models for banquet/buffet formats. |
| *Demand Forecasting in Catering* `[TODO – COMPLETE REFERENCE DETAILS]` | Institutional cafeteria footfall forecasting | Time-series & Random Forest | External weather shocks and calendar holidays were primary variance drivers. | Guided the inclusion of `Weather`, `Festival`, and `Day` as core predictive features. |
| *Data Leakage in Operational ML* `[TODO – COMPLETE REFERENCE DETAILS]` | Machine learning system design audits | Pipeline integrity analysis | Using post-event outcomes as inputs leads to artificial near-perfect training scores that fail in production. | Established the foundational rule strictly banning `Meals_Sold` from all feature vectors. |
| *scikit-learn Ensemble Methods* (Pedregosa et al., 2011) | General ensemble regression | Random Forest Bagging (MDI) | Bagging randomized subsets of features reduces model variance without increasing bias. | Provided the algorithmic implementation framework and feature importance methodology. |

## 2.2 Summary Table of Explored Techniques

| Technique | Strengths | Weaknesses | Decision for CIBUS-AI |
| :--- | :--- | :--- | :--- |
| **Linear Regression** | Fast, simple, highly interpretable | Cannot capture non-linear weather $\times$ event interactions | Implemented as benchmark baseline only. |
| **Random Forest Regressor** | Handles non-linearities, robust to outliers, provides MDI importance | Requires serialization packaging, higher memory | **Selected as Primary Model** for production pipeline. |
| **Deep Neural Networks** | High capacity for massive datasets | Overkill for tabular operational data, lacks native tree interpretability | Deferred to future work if multi-modal sensor scale is added. |

## 2.3 What This Told Us
1. **Regression is Necessary:** Predicting continuous meal counts ($\hat{y} \in \mathbb{R}_{\ge 0}$) is essential for logistics capacity planning; discrete classification ("High/Low") is insufficient for dispatching vehicles.
2. **Leakage is a Severe Risk:** Operational accounting formulas ($\text{Surplus} = \text{Prepared} - \text{Sold}$) must be decoupled from the predictive feature space.
3. **Ensemble Trees Fit Tabular Dynamics:** Random Forest natively models complex multi-way conditional thresholds (e.g., Stormy Weather during a Buffet service) without requiring manual polynomial feature engineering.

---

# CHAPTER 3 — PROJECT PLANNING AND TEAM ORGANISATION

## 3.1 Weekly PBL Progress Log

| Week | Completed Activity | ML Concepts Mastered | Key Deliverable / Evidence | Mentor Feedback |
| :---: | :--- | :--- | :--- | :--- |
| **W1** | Problem formulation, repository scaffolding, documentation, and data leakage audit. | Supervised Regression formulation, Target Leakage (`Meals_Sold` rule), Evaluation metrics (MAE, RMSE, $R^2$). | Initial repository layout, `docs/` architecture documents, `.gitignore`, `requirements.txt`. | `[TODO – MENTOR FEEDBACK]` |
| **W2** | Synthetic dataset generation (`generate_dataset.py`, `validate_dataset.py`), distribution checks. | Parameterized data synthesis, feature distributions, zero-leakage target formation. | `food_surplus.csv` (8,000 rows, 10 columns), validation report, `dataset_description.md`. | `[TODO – MENTOR FEEDBACK]` |
| **W3** | Preprocessing pipeline implementation (`preprocess.py`), One-Hot encoding, 80/20 split. | Transformation isolation (fit on train only), OneHotEncoder with unseen category handling, Joblib serialization. | `preprocess.py`, `models/preprocessor.joblib`, updated schema docs. | `[TODO – MENTOR FEEDBACK]` |
| **W4** | Baseline model training (`train_baseline.py`) and Hyperparameter tuning (`train_model.py`). | Ensemble Bagging, 3-Fold Cross-Validation, Negative RMSE scoring, Baseline vs. Tuned benchmarking. | `food_surplus_model.pkl`, `baseline_results.json`, `model_comparison.json`. | `[TODO – MENTOR FEEDBACK]` |
| **W5** | Diagnostic evaluation (`evaluate_model.py`), residual plotting, and MDI feature importance (`feature_importance.py`). | Mean Decrease in Impurity (MDI), Residual distribution diagnostics ($\bar{e} = -0.27$), linear calibration. | `predictions.csv`, `actual_vs_predicted.png`, `residual_analysis.png`, `feature_importance.png`. | `[TODO – MENTOR FEEDBACK]` |
| **W6** | Reusable prediction system (`predict.py`), unit testing suite (`test_predict.py`, 9 passing tests), CLI. | Inference pipelines, defensive boundary validation, runtime leakage rejection, CLI development. | `predict.py`, `test_predict.py`, `prediction_documentation.md`, final PBL report. | `[TODO – MENTOR FEEDBACK]` |

## 3.2 Requirements

### Hardware Requirements:
- **Processor:** Standard x86-64 CPU (Intel Core i3/i5/i7 or AMD Ryzen equivalent).
- **RAM:** Minimum 4 GB RAM (8 GB recommended for parallel Cross-Validation).
- **Storage:** ~200 MB free disk space for repository, dataset, and model artifacts.

### Software Requirements:
- **Operating System:** Windows 10/11, Linux, or macOS.
- **Programming Language:** Python 3.10+ (tested on Python 3.14).
- **Core Libraries:** `pandas` (>= 2.0), `numpy` (>= 1.24), `scikit-learn` (>= 1.3), `joblib` (>= 1.3), `matplotlib` (>= 3.7).
- **Version Control:** Git & GitHub.

## 3.3 Feasibility Analysis
- **Technical Feasibility:** High. The tabular dataset schema maps cleanly to scikit-learn's `ColumnTransformer` and `RandomForestRegressor`, with sub-second inference speed.
- **Economic Feasibility:** High. Built entirely on open-source Python libraries with zero commercial license or cloud hosting costs during development.
- **Operational Feasibility:** High. Standalone CLI and modular Python API allow instant integration into kitchen management software and NGO dispatch pipelines.
- **Time Feasibility:** Project completed across 6 structured weekly sprints, fulfilling all college PBL milestones on schedule.

---

# CHAPTER 4 — ITERATIVE DESIGN AND DEVELOPMENT

## 4.1 System Architecture

```
[Raw Operational Data] ──► [Leakage-Safe Validation] ──► [Train/Test Split (80/20)]
                                                                  │
                 ┌────────────────────────────────────────────────┴──────────────────────────┐
                 ▼                                                                           ▼
      [Training Set (6,400 samples)]                                              [Test Set (1,600 samples)]
                 │                                                                           │
                 ├─► Fit ColumnTransformer                                                   │
                 │                                                                           │
                 ├─► Iteration 1: Baseline RF (n=100)                                        │
                 │                                                                           │
                 └─► Iteration 2: 3-Fold CV Hyperparameter Tuning                            │
                           │                                                                 │
                           ▼                                                                 │
                 [Trained Final Model (food_surplus_model.pkl)]                              │
                           │                                                                 │
                           └─────────────────────────┬───────────────────────────────────────┘
                                                     ▼
                                       [Hold-out Test Evaluation]
                                     - MAE: 14.58 meals
                                     - RMSE: 20.69 meals
                                     - R²: 0.9543
                                                     │
                                                     ▼
                                  [Reusable Prediction Engine (predict.py)]
```

## 4.2 Iteration 1 — Baseline Model
- **Configuration:** `RandomForestRegressor(n_estimators=100, max_depth=None, min_samples_split=2, min_samples_leaf=1, max_features=1.0, random_state=42)`.
- **Training Strategy:** Fit on $X_{\text{train}}$ ($6,400$ samples), evaluated on held-out $X_{\text{test}}$ ($1,600$ samples).
- **Actual Experimental Metrics:**
  - **MAE:** `14.2939 meals`
  - **RMSE:** `20.5429 meals`
  - **$R^2$ Score:** `0.9549`
- **Observations:** The unconstrained ensemble captured the primary non-linear signal effectively, but full-depth trees generated a large model file ($57.9\text{ MB}$) with potential sensitivity to localized noise.

## 4.3 Iteration 2 — Hyperparameter Refinement
- **Motivation:** Investigate whether constraining tree depth, tuning split minimums, and sub-sampling features optimizes variance control while producing a more compact model.
- **Search Space Considered:**
  - `n_estimators`: `[100, 150, 200]`
  - `max_depth`: `[None, 15, 25]`
  - `min_samples_split`: `[2, 4, 8]`
  - `min_samples_leaf`: `[1, 2, 4]`
  - `max_features`: `['sqrt', 0.8, 1.0]`
- **Cross-Validation Strategy:** 3-Fold Cross-Validation strictly on the training partition ($X_{\text{train}}$) using `neg_root_mean_squared_error` scoring.
- **Best Selected Hyperparameters:**
  - `n_estimators`: `200`
  - `max_depth`: `15`
  - `min_samples_split`: `4`
  - `min_samples_leaf`: `1`
  - `max_features`: `0.8`
  - *Best 3-Fold CV RMSE:* `20.9391 meals`
- **Actual Final Test Metrics:**
  - **MAE:** `14.5793 meals`
  - **RMSE:** `20.6869 meals`
  - **$R^2$ Score:** `0.9543`

## 4.4 Final Approach Selection
The refined model (`n_estimators=200`, `max_depth=15`, `max_features=0.8`) was selected as the **Final Production Model**:
1. **Regularization:** Bounding `max_depth=15` prevents deep leaf memorization.
2. **Model Compactness:** Reduces model serialization footprint from $57.9\text{ MB}$ to $40.4\text{ MB}$ (a $30\%$ reduction) with virtually identical predictive accuracy ($\approx 14.5$ meals average error).
3. **Reproducibility:** Serialized to `ai-engine/models/food_surplus_model.pkl` along with `food_surplus_preprocessor.pkl`.

## 4.5 Training Procedure
1. Load `food_surplus.csv` ($N = 8,000$ records).
2. Partition into $80\%$ Train ($6,400$) and $20\%$ Test ($1,600$) with `random_state=42`.
3. Fit `ColumnTransformer` (OneHotEncoder on 4 categorical features, passthrough on 5 numerical features) on $X_{\text{train}}$.
4. Execute 3-Fold Cross-Validation parameter search on $X_{\text{train}}$.
5. Fit final ensemble ($200$ trees) on full $X_{\text{train}}$.
6. Perform single evaluation pass on untouched held-out $X_{\text{test}}$.

---

# CHAPTER 5 — IMPLEMENTATION

## 5.1 Module Descriptions

| Module / Script | File Path | Inputs | Key Processing | Outputs |
| :--- | :--- | :--- | :--- | :--- |
| **Dataset Generator** | `ai-engine/dataset/generate_dataset.py` | Configuration constants ($N=8000$, seed=42) | Generates operational features, non-linear interactions, and stochastic noise. | `food_surplus.csv` |
| **Dataset Validator** | `ai-engine/dataset/validate_dataset.py` | `food_surplus.csv` | Checks row count, schema, 0 nulls, 0 dups, and verifies `Meals_Sold` is absent. | Console validation report |
| **Preprocessing** | `ai-engine/preprocessing/preprocess.py` | `food_surplus.csv` | Train-test split (80/20), One-Hot categorical encoding, pipeline persistence. | `preprocessor.joblib`, transformed matrices |
| **Baseline Trainer** | `ai-engine/training/train_baseline.py` | Preprocessed $X_{\text{train}}, y_{\text{train}}$ | Fits default Random Forest ($n=100$). | `baseline_food_surplus_model.pkl`, `baseline_results.json` |
| **Model Refinement** | `ai-engine/training/train_model.py` | Preprocessed $X_{\text{train}}, y_{\text{train}}$ | 3-Fold Cross-Validation search, fits final model ($n=200, d=15$). | `food_surplus_model.pkl`, `model_comparison.json` |
| **Feature Importance** | `ai-engine/training/feature_importance.py` | `food_surplus_model.pkl`, Preprocessor | Extracts MDI scores, aggregates dummy columns, renders bar chart. | `feature_importance.csv`, `feature_importance.png` |
| **Model Evaluation** | `ai-engine/evaluation/evaluate_model.py` | `food_surplus_model.pkl`, $X_{\text{test}}, y_{\text{test}}$ | Computes MAE, RMSE, $R^2$, residuals, exports diagnostic scatter plots. | `predictions.csv`, `actual_vs_predicted.png`, `residual_analysis.png` |
| **Prediction Engine** | `ai-engine/prediction/predict.py` | Pre-service operational dict or CLI args | Validates inputs, rejects `Meals_Sold`, transforms and predicts surplus. | Predicted surplus meals (float) |
| **Inference Tests** | `ai-engine/prediction/test_predict.py` | 9 operational & boundary scenarios | Unittest suite verifying predictions, boundary checks, and leakage rejection. | Test execution logs |

## 5.2 Key Code Snippets

### Snippet 1: Leakage-Safe Preprocessing Pipeline (`ai-engine/preprocessing/preprocess.py`)
```python
def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
            ("num", "passthrough", NUMERICAL_FEATURES)
        ],
        remainder="drop"
    )
```
*Explanation:* Categorical features are One-Hot encoded while numerical features pass through in original physical units (meals, staff), preserving interpretability without scaling distortion.

### Snippet 2: Cross-Validated Hyperparameter Refinement (`ai-engine/training/train_model.py`)
```python
cv_search = RandomizedSearchCV(
    estimator=RandomForestRegressor(random_state=42),
    param_distributions=param_distributions,
    n_iter=10,
    cv=3,
    scoring="neg_root_mean_squared_error",
    random_state=42,
    n_jobs=1,
    refit=True
)
cv_search.fit(X_train, y_train)
```
*Explanation:* Evaluates hyperparameter candidates using 3-Fold Cross-Validation strictly on the training partition to prevent test-set leakage.

### Snippet 3: Defensive Input Validation & Leakage Rejection (`ai-engine/prediction/predict.py`)
```python
def validate_prediction_input(input_dict: Dict[str, Any]) -> Dict[str, Any]:
    if "Meals_Sold" in input_dict or "meals_sold" in input_dict:
        raise ValueError("CRITICAL ERROR: 'Meals_Sold' is a post-service outcome and cannot be accepted.")
    # Validates numerical bounds (Meals_Prepared >= 0, 1.0 <= Avg_Rating <= 5.0)
    ...
```
*Explanation:* Protects the deployed prediction engine against runtime data leakage and invalid out-of-bounds parameters.

## 5.3 UI, Backend & Extended Application Modules

### Core ML Serving & REST Architecture
The trained Random Forest model and pre-fitted `ColumnTransformer` are served via an asynchronous **FastAPI** REST backend (`backend/app/`):
- `POST /api/predict`: Executes real-time inference returning forecasted surplus meals.
- `GET /health`: Diagnostic monitor checking server and model artifact readiness.

### Extended Module 1: React Single-Page Web Dashboard (`frontend/`)
A responsive, dark-glassmorphism user interface built with **React** and **Vite** allowing dining operators to input pre-service parameters, view real-time surplus forecasts, and inspect model specifications.

### Extended Module 2: Rule-Based NGO Matching & Redistribution (`backend/app/services/ngo_matching_service.py`)
> **Important Distinction:** The NGO Matching module is a deterministic, rule-based heuristic allocation component, strictly separate from the Supervised Random Forest ML model.

It takes the forecasted surplus $\hat{y}$ from the ML engine and matches candidate partner organizations from a synthetic recipient directory (`backend/data/ngos.csv`) using:
1. **Multi-Factor Heuristic Score:** Evaluates active receiving status ($35\%$), Haversine spherical transit distance ($25\%$), dietary format compatibility ($20\%$), and capacity suitability ($20\%$).
2. **Constraint-Based Allocation:** Enforces $\text{Allocated Meals}_i \le \text{Capacity}_i$ and $\sum \text{Allocated Meals}_i \le \text{Predicted Surplus}$, preventing shelter overload.

---

# CHAPTER 6 — RESULTS AND DISCUSSION

## 6.1 Evaluation Metrics Definition
- **Mean Absolute Error (MAE):** $\text{MAE} = \frac{1}{n} \sum |y_i - \hat{y}_i| = 14.58\text{ meals}$. Measures average expected prediction error in real meal units.
- **Root Mean Squared Error (RMSE):** $\text{RMSE} = \sqrt{\frac{1}{n} \sum (y_i - \hat{y}_i)^2} = 20.69\text{ meals}$. Penalizes larger prediction misses quadratically.
- **Coefficient of Determination ($R^2$):** $R^2 = 1 - \frac{\text{SS}_{\text{res}}}{\text{SS}_{\text{tot}}} = 0.9543$. Indicates the model accounts for $95.43\%$ of surplus variance relative to a naive mean baseline.

## 6.2 Results Across Iterations

| Model Iteration | Configuration | MAE (meals) | RMSE (meals) | $R^2$ Score | Model Size |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Iteration 1: Baseline** | `n_estimators=100`, unconstrained depth | **14.2939** | **20.5429** | **0.9549** | 57.9 MB |
| **Iteration 2: Refined Final** | `n_estimators=200`, `max_depth=15`, `max_features=0.8` | **14.5793** | **20.6869** | **0.9543** | **40.4 MB** |

## 6.3 Discussion of Results
1. **Predictive Calibration:** Test predictions tightly follow the ideal diagonal reference line ($y = x$) across all operational volumes ($0$ to $640+$ meals), confirming linear reliability.
2. **Residual Properties:** Mean residual bias is near zero ($\bar{e} = -0.2729\text{ meals}$), demonstrating unbiased global predictions.
3. **Tolerance Reliability:** **$65.38\%$** of predictions fall within $\pm 15$ meals, and **$82.81\%$** fall within $\pm 25$ meals.
4. **Key Drivers (MDI):** `Meals_Prepared` ($48.96\%$), `Event_Type` ($16.51\%$), and `Weather` ($16.03\%$) account for over $81\%$ of predictive decisions.

## 6.4 Limitations
- **Synthetic Behavioral Distributions:** Does not yet incorporate live point-of-sale or IoT scale sensor streams.
- **Static Window:** Single batch predictions prior to service start; mid-service changes require re-querying.
- **Homogeneous Portions:** Measures aggregate meal portions rather than per-ingredient perishability.

---

# CHAPTER 7 — TEAM REFLECTION AND LEARNING OUTCOMES

## 7.1 Individual Team Member Reflections

### Team Member 1
- **Name / Role:** `[TODO – TEAM MEMBER NAME AND ROLE]`
- **Key Contributions:** `[TODO – SPECIFIC CONTRIBUTIONS]`
- **ML Concepts Mastered:** Data leakage prevention, Random Forest bagging mechanisms, MDI feature importance.
- **Technical Challenges & Solutions:** `[TODO – CHALLENGE AND SOLUTION]`
- **PBL Learning Takeaway:** `[TODO – PERSONAL REFLECTION]`

### Team Member 2
- **Name / Role:** `[TODO – TEAM MEMBER NAME AND ROLE]`
- **Key Contributions:** `[TODO – SPECIFIC CONTRIBUTIONS]`
- **ML Concepts Mastered:** `ColumnTransformer` pipelines, train-test isolation, evaluation metrics (MAE, RMSE, $R^2$).
- **Technical Challenges & Solutions:** `[TODO – CHALLENGE AND SOLUTION]`
- **PBL Learning Takeaway:** `[TODO – PERSONAL REFLECTION]`

### Team Member 3
- **Name / Role:** `[TODO – TEAM MEMBER NAME AND ROLE]`
- **Key Contributions:** `[TODO – SPECIFIC CONTRIBUTIONS]`
- **ML Concepts Mastered:** Cross-validated hyperparameter optimization, residual diagnostics, defensive API design.
- **Technical Challenges & Solutions:** `[TODO – CHALLENGE AND SOLUTION]`
- **PBL Learning Takeaway:** `[TODO – PERSONAL REFLECTION]`

## 7.2 Team Learning & Collaborative Outcomes
- **Iterative ML Engineering:** Understanding that model building is an empirical, evidence-driven process where hyperparameter tuning must be grounded in cross-validation.
- **Strict Data Hygiene:** Internalizing why post-facto features (`Meals_Sold`) invalidate real-world prediction systems.
- **Defensible Reporting:** Learning to report real experimental metrics truthfully rather than fabricating inflated numbers.
- **Version Control Discipline:** Maintaining an automated Git/GitHub workflow for commit traceability.

## 7.3 Course-Outcome Mapping
- **CO1 (Problem Formulation):** Formulated food waste prediction as a supervised regression task. *(Achieved)*
- **CO2 (Data Preparation):** Implemented clean, reproducible, leak-free preprocessing. *(Achieved)*
- **CO3 (Model Development):** Trained and tuned an ensemble Random Forest regressor. *(Achieved)*
- **CO4 (Evaluation & Analysis):** Conducted rigorous residual diagnostics and feature importance extraction. *(Achieved)*
- **Faculty Verification:** `[TODO – FACULTY COURSE-OUTCOME CONFIRMATION]`

---

# CHAPTER 8 — CONCLUSION AND FUTURE SCOPE

## 8.1 Conclusion
The CIBUS-AI machine learning project successfully designed, trained, tuned, and evaluated an AI engine for pre-service food surplus forecasting. Utilizing an 8,000-record synthetic operational dataset and a Random Forest Regressor ($200$ trees, `max_depth=15`), the system achieves an $R^2$ of **$0.9543$**, an MAE of **$14.58\text{ meals}$**, and an RMSE of **$20.69\text{ meals}$** with near-zero systematic bias ($\bar{e} = -0.27\text{ meals}$). 

By strictly preventing data leakage and providing a modular inference interface, CIBUS-AI proves the feasibility of pre-service surplus forecasting to power proactive food redistribution.

## 8.2 Future Scope
1. **Real-World Deployment & Sensor Telemetry:** Partner with commercial cafeterias to ingest physical POS registers, smart kitchen bin scales, and real-time food temperature sensors.
2. **Dynamic Multi-Stop Route Optimization:** Vehicle routing problem (VRP) solver calculating optimal multi-stop pickup and drop-off sequences for volunteer food couriers.
3. **Automated Volunteer Dispatch & Mobile Notifications:** Push-notification system alerting nearby verified food recovery couriers for rapid transit.
4. **Interactive GIS & Telemetry Dashboard:** Full-scale GIS mapping with live GPS driver tracking and food shelf-life countdown monitors.
