# CIBUS-AI: PROJECT-BASED LEARNING (PBL) ACADEMIC REPORT

---

## COVER PAGE INFORMATION

**Project Title:**  
CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network

**Tagline:**  
*Predict. Connect. Nourish.*

**Course / Curriculum:**  
Machine Learning Project-Based Learning (PBL)

**Student Details:**  
- Student 1: `[STUDENT 1 NAME]` (Register No: `[REGISTER NUMBER 1]`)  
- Student 2: `[STUDENT 2 NAME]` (Register No: `[REGISTER NUMBER 2]`)  
- Student 3: `[STUDENT 3 NAME]` (Register No: `[REGISTER NUMBER 3]`)  
- Student 4: `[STUDENT 4 NAME]` (Register No: `[REGISTER NUMBER 4]`)  

**Department:**  
`[DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING / INFORMATION TECHNOLOGY]`

**Institution:**  
`[COLLEGE / UNIVERSITY NAME]`

**Academic Year:**  
`[202X - 202Y]`

**Faculty Mentor:**  
`[FACULTY MENTOR NAME]`, `[DESIGNATION]`, `[DEPARTMENT]`

---

## CERTIFICATE

This is to certify that the project entitled **"CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network"** is a bonafide record of work carried out by:

- `[STUDENT 1 NAME]` (`[REGISTER NUMBER 1]`)
- `[STUDENT 2 NAME]` (`[REGISTER NUMBER 2]`)
- `[STUDENT 3 NAME]` (`[REGISTER NUMBER 3]`)
- `[STUDENT 4 NAME]` (`[REGISTER NUMBER 4]`)

in partial fulfillment of the requirements for the award of the degree of **`[DEGREE NAME, e.g., Bachelor of Technology / Engineering]`** during the academic year **`[ACADEMIC YEAR]`**.

\
\
__________________________  
**`[FACULTY MENTOR NAME]`**  
Faculty Mentor / Project Supervisor  

\
\
__________________________  
**`[HEAD OF DEPARTMENT NAME]`**  
Head of Department  

**Date:** `[DD/MM/YYYY]`  
**Place:** `[INSTITUTION LOCATION]`  

---

## DECLARATION

We hereby declare that the project entitled **"CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network"** submitted to **`[COLLEGE / UNIVERSITY NAME]`** is our original work conducted under the guidance of **`[FACULTY MENTOR NAME]`**.

This work has not previously formed the basis for the award of any degree, diploma, associate-ship, or other similar title to the best of our knowledge.

- `[STUDENT 1 NAME]` (Signature: _____________________)
- `[STUDENT 2 NAME]` (Signature: _____________________)
- `[STUDENT 3 NAME]` (Signature: _____________________)
- `[STUDENT 4 NAME]` (Signature: _____________________)

**Date:** `[DD/MM/YYYY]`  

---

## ACKNOWLEDGEMENT

We express our sincere gratitude to our faculty mentor, **`[FACULTY MENTOR NAME]`**, for continuous encouragement, insightful technical guidance, and valuable constructive feedback throughout the design, implementation, and evaluation of the CIBUS-AI project.

We also thank the Head of the Department, **`[HEAD OF DEPARTMENT NAME]`**, and our esteemed institution, **`[COLLEGE / UNIVERSITY NAME]`**, for providing the computational laboratory facilities and academic environment essential for completing this Machine Learning Project-Based Learning work.

Finally, we extend our heartfelt appreciation to our peers and family members for their sustained support and cooperation during the project lifecycle.

---

## ABSTRACT

Commercial food establishments, such as restaurants, banquet halls, and institutional canteens, routinely generate substantial quantities of edible food surplus due to uncertain customer footfall, weather variations, and rigid batch preparation practices. Concurrently, community relief organizations and shelters face daily food supply deficits. A critical operational challenge in conventional food redistribution is that surplus is typically recognized reactively after business hours, leaving insufficient lead time to organize pickup logistics before spoilage occurs. This project presents **CIBUS-AI**, an end-to-end intelligent decision-support system designed to forecast commercial food surplus prior to meal service and automate redistribution planning. An 8,000-record synthetic dataset incorporating operational, environmental, and event factors was generated and validated to train a supervised `RandomForestRegressor` model while strictly preventing target leakage by excluding post-service sales metrics. On unseen test data, the refined model achieved a Mean Absolute Error (MAE) of $14.58\text{ meals}$, a Root Mean Squared Error (RMSE) of $20.69\text{ meals}$, and a Coefficient of Determination ($R^2$) of $0.9543$. The predicted surplus directly feeds a rule-based matching engine that greedily allocates meals to compatible nearby NGOs and computes an efficient multi-stop pickup trajectory using spherical Haversine distance heuristics. An interactive React 19 web application and FastAPI backend provide real-time decision support, route visualization, and sustainability impact tracking ($CO_2$ and water savings). CIBUS-AI demonstrates the feasibility of combining predictive machine learning with automated logistics heuristics to transform reactive food waste into proactive community nourishment.

**Keywords:** Food Surplus Prediction, Random Forest Regression, Haversine Route Optimization, NGO Matching, Decision Support System.

---

## CHAPTER 1: INTRODUCTION

### 1.1 Background & Motivation
Food waste is a major global economic, social, and environmental crisis. According to international reports by the Food and Agriculture Organization (FAO) and the United Nations Environment Programme (UNEP), approximately one-third of all food produced globally for human consumption is lost or wasted annually. This waste contributes significantly to greenhouse gas emissions ($CO_2\text{e}$) and squanders massive volumes of embedded agricultural water and energy.

In commercial hospitality sectors—including restaurants, hotels, corporate canteens, and banquet facilities—food surplus arises from a fundamental mismatch between fixed pre-service food preparation volumes and variable consumer demand. Kitchen managers face severe uncertainty driven by day-of-week demand patterns, adverse weather conditions, localized events, and footfall fluctuations. 

Currently, surplus food management is almost entirely reactive. Surplus is quantified only at the end of the business day when kitchens close. By that time, communication with local Non-Governmental Organizations (NGOs) and charitable shelters is delayed, volunteer transport cannot be mobilized on short notice, and hot edible meals are frequently discarded. Applying machine learning for *pre-service prediction* allows commercial donors to anticipate surplus hours in advance, triggering automated matching and route planning so that food can be rescued while strictly fresh.

### 1.2 Driving Question
> *"How can machine learning regression models and algorithmic logistics heuristics be unified into an automated decision-support system to accurately predict commercial food surplus and optimize local redistribution planning before waste occurs?"*

### 1.3 Technical & Learning Objectives

#### Technical Objectives:
1. **Dataset Construction:** Synthesize a statistically representative 8,000-sample dataset modeling commercial food surplus dynamics across 10 operational features while strictly eliminating target leakage.
2. **Preprocessing Pipeline:** Construct a standardized `ColumnTransformer` applying one-hot encoding for categorical variables and z-score scaling for numerical inputs.
3. **Machine Learning Modeling:** Train, evaluate, and tune a `RandomForestRegressor` to achieve high explanatory capability ($R^2 > 0.90$) with low error residuals (MAE $< 20\text{ meals}$).
4. **Interpretability Analysis:** Quantify feature importance (Mean Decrease in Impurity) to understand key predictors governing surplus variance.
5. **Rule-Based NGO Matching:** Formulate a constraint-aware greedy allocation engine to match surplus meals against recipient capacities within local geographic radii.
6. **Route Planning Heuristics:** Implement a Haversine distance matrix calculator and greedy nearest-neighbor route optimizer for efficient multi-stop pickup dispatch.
7. **Interactive Prototype:** Deploy an asynchronous FastAPI REST backend and responsive React 19 web application featuring real-time environmental impact dashboards.

#### Learning Objectives:
- Master the end-to-end supervised machine learning lifecycle from problem formulation to model deployment.
- Identify and prevent target leakage during feature engineering.
- Implement and interpret regression metrics (MAE, RMSE, $R^2$) without confounding explained variance with classification accuracy.
- Integrate serialized machine learning artifacts (`.pkl`) within modern asynchronous REST APIs.
- Apply algorithmic heuristics (Haversine distance, Travelling Salesperson approximations) to practical logistics challenges.

### 1.4 Scope and Limitations

#### In-Scope:
- Supervised regression forecasting using pre-service operational parameters.
- Synthetic 8,000-row dataset modeling urban restaurant operations.
- Rule-based recipient NGO filtering and greedy capacity allocation.
- Haversine straight-line distance computation and nearest-neighbor route ordering.
- Full-stack prototype with interactive user interface, SVG route visualization, and sustainability analytics.

#### Out-of-Scope & Limitations:
- **Synthetic Data:** The dataset is synthetic and does not represent live restaurant POS feeds.
- **Physical Transport:** The system generates software redistribution plans; it does not execute physical transport or confirm live deliveries.
- **Routing Simplifications:** Distance calculations use spherical Haversine math rather than live road turn-by-turn navigation or real-time traffic APIs.
- **Static NGO Directory:** Recipient NGOs are synthetically modeled with static capacities rather than real-time availability feeds.

---

## CHAPTER 2: CONCEPT EXPLORATION & LITERATURE REVIEW

### 2.1 Literature Review Summary Table

| Source / Approach | Problem Addressed | Method / Model | Key Finding | Relevance to CIBUS-AI |
| :--- | :--- | :--- | :--- | :--- |
| **Breiman (2001) [1]** | High variance & overfitting in single decision trees | Bagged ensemble of randomized decision trees (Random Forest) | Demonstrated superior generalization and variance reduction on tabular data | Forms the core ML algorithm for CIBUS-AI food surplus regression. |
| **Pedregosa et al. (2011) [2]** | Standardized ML pipelines & preprocessing | Scikit-learn Python framework (`ColumnTransformer`, `StandardScaler`) | Standardized reproducible feature transformation and model persistence | Used for preprocessor and model serialization (`.pkl`). |
| **FAO (2019) [3]** | Global food loss and supply chain inefficiencies | Macroeconomic analysis of food distribution bottlenecks | Over 30% of edible food is lost due to reactive supply chain logistics | Motivates pre-service surplus prediction to enable proactive logistics. |
| **UNEP (2021) [4]** | Urban food waste in commercial and retail sectors | Sectoral waste index modeling | Food service sector accounts for substantial edible urban waste | Informs the operational parameters modeled in the synthetic dataset. |
| **Sinnott (1984) [6]** | Accurate spherical distance calculation on Earth | Trigonometric Haversine formula | Provides robust great-circle distance computation between geographic coordinates | Utilized in CIBUS-AI route distance matrix computation. |
| **Russell & Norvig (2020) [7]** | Combinatorial optimization in vehicle routing | Greedy Nearest Neighbor Heuristic for TSP | Provides fast, deterministic near-optimal route construction for small stop counts | Serves as the dispatch ordering algorithm in the route service. |

### 2.2 What This Exploration Told Us
Review of existing literature and domain methods established three fundamental design decisions:
1. **Regression over Classification:** Quantifying exact surplus meal volumes is essential for downstream capacity matching; discrete classification labels (e.g., "high/low") cannot drive precise meal allocations.
2. **Tree Ensembles for Non-Linear Tabular Data:** Random Forest Regression was chosen because tabular kitchen data features complex non-linear interactions (e.g., weather conditions interacting with holiday events) that tree ensembles model naturally without extensive feature scaling.
3. **Leakage Avoidance:** Previous studies highlighted that utilizing post-service indicators (e.g., sales revenue or meals sold) leads to trivial, invalid models. Pre-service operational forecasting requires strict feature isolation.

---

## CHAPTER 3: PROJECT PLANNING AND FEASIBILITY

### 3.1 Weekly PBL Progress Log
*(A detailed chronological log of weekly development milestones is maintained in [docs/weekly_progress.md](file:///k:/CiBus-Ai%20R/docs/weekly_progress.md) and summarized in Appendix E).*

### 3.2 System Requirements

#### Hardware Requirements:
- **Processor:** Modern x86-64 multi-core CPU (Intel Core i5 / AMD Ryzen 5 or equivalent).
- **Memory (RAM):** 8 GB minimum (16 GB recommended for concurrent backend/frontend dev servers).
- **Storage:** 2 GB available disk space.

#### Software & Dependencies:
- **Operating System:** Windows 10/11, macOS, or Linux.
- **Python Runtime:** Python 3.10 or higher.
- **Core Python Libraries:** `scikit-learn` (1.3.0+), `pandas`, `numpy`, `fastapi`, `uvicorn`, `pydantic`, `joblib`.
- **Node.js Runtime:** Node.js v18.0+ and `npm` v9.0+.
- **Frontend Frameworks:** React 19, Vite, Tailwind CSS, Axios, Lucide React.
- **Version Control:** Git & GitHub.

### 3.3 Feasibility Analysis
- **Technical Feasibility:** High. Random Forest regression executes inference in $<10\text{ ms}$, and Haversine matrix computations for $N \le 20$ NGOs execute in $<1\text{ ms}$, ensuring sub-second API responsiveness.
- **Operational Feasibility:** High. The intuitive card-based web interface enables restaurant staff to generate complete redistribution plans in under 60 seconds without technical training.
- **Economic Feasibility:** High. The prototype utilizes open-source libraries and lightweight local persistence, incurring zero licensing or cloud hosting costs for academic demonstration.

---

## CHAPTER 4: ITERATIVE DESIGN AND DEVELOPMENT

### 4.1 System Architecture & Data Flow
CIBUS-AI operates through a decoupled three-tier architecture:
1. **Frontend Client:** React 19 SPA capturing donor parameters and rendering interactive results.
2. **FastAPI Backend:** Orchestrating Pydantic validation, ML inference, NGO matching, and route optimization.
3. **Machine Learning Pipeline:** Offline-trained `RandomForestRegressor` and preprocessor pipelines.

### 4.2 Iteration 1 — Baseline Model
In the initial baseline iteration:
- **Model:** `RandomForestRegressor(n_estimators=100, random_state=42)` without tree depth constraints.
- **Performance:** Achieved $R^2 = 0.9521$, $\text{MAE} = 15.12\text{ meals}$, $\text{RMSE} = 21.45\text{ meals}$.
- **Analysis:** While performance was strong, unconstrained tree depth risked memorizing synthetic noise patterns.

### 4.3 Iteration 2 — Refinement & Hyperparameter Tuning
In the refinement iteration:
- **Exploration:** Systematic evaluation of maximum tree depths (`max_depth` $\in [10, 15, 20]$) and split criteria (`min_samples_split` $\in [2, 5, 10]$).
- **Selected Configuration:** `n_estimators=100`, `max_depth=15`, `min_samples_split=2`, `random_state=42`.
- **Refined Results:** Achieved $R^2 = 0.9543$, $\text{MAE} = 14.5793\text{ meals}$, $\text{RMSE} = 20.6869\text{ meals}$.
- **Finding:** Constraining tree depth to 15 improved generalization on the test split while reducing model file footprint.

---

## CHAPTER 5: IMPLEMENTATION & CODE SNIPPETS

### 5.1 Key Code Implementations

#### 1. Machine Learning Model Training (`ai-engine/training/train_model.py`)
```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import joblib

# Construct preprocessing pipeline
categorical_features = ['Day', 'Weather', 'Event_Type', 'Festival', 'Special_Event']
numerical_features = ['Customers_Forecast', 'Meals_Prepared', 'Staff_Count', 'Avg_Rating']

preprocessor = ColumnTransformer(transformers=[
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
    ('num', StandardScaler(), numerical_features)
])

# Fit preprocessor and train model
X_train_trans = preprocessor.fit_transform(X_train)
model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42)
model.fit(X_train_trans, y_train)

# Serialize artifacts
joblib.dump(preprocessor, "models/food_surplus_preprocessor.pkl")
joblib.dump(model, "models/food_surplus_model.pkl")
```

#### 2. Reusable Prediction Service (`backend/services/prediction_service.py`)
```python
import numpy as np

def predict_surplus_meals(input_data: dict, preprocessor, model) -> int:
    """Transform input features and infer non-negative surplus meals."""
    df_input = pd.DataFrame([input_data])
    X_transformed = preprocessor.transform(df_input)
    raw_prediction = model.predict(X_transformed)[0]
    # Enforce physical boundary clamping
    meals_prepared = input_data.get("Meals_Prepared", 0)
    clamped_prediction = max(0, min(int(round(raw_prediction)), meals_prepared))
    return clamped_prediction
```

#### 3. Haversine Distance & Route Optimization (`backend/services/route_service.py`)
```python
import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance in kilometers using Haversine formula."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def optimize_route(donor_coords: tuple, matched_ngos: list) -> dict:
    """Solve multi-stop pickup order using Greedy Nearest Neighbor Heuristic."""
    unvisited = matched_ngos.copy()
    current_lat, current_lon = donor_coords
    route_order = []
    total_km = 0.0

    while unvisited:
        nearest = min(unvisited, key=lambda ngo: haversine_distance(
            current_lat, current_lon, ngo['latitude'], ngo['longitude']
        ))
        dist = haversine_distance(current_lat, current_lon, nearest['latitude'], nearest['longitude'])
        total_km += dist
        current_lat, current_lon = nearest['latitude'], nearest['longitude']
        route_order.append(nearest)
        unvisited.remove(nearest)

    est_minutes = round((total_km / 25.0) * 60 + (5 * len(route_order)), 1)
    return {"route": route_order, "total_distance_km": round(total_km, 2), "estimated_time_mins": est_minutes}
```

---

## CHAPTER 6: RESULTS AND DISCUSSION

### 6.1 Final Model Performance

| Iteration / Model | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | Coefficient of Determination ($R^2$) |
| :--- | :--- | :--- | :--- |
| **Baseline Random Forest** | $15.1200\text{ meals}$ | $21.4500\text{ meals}$ | $0.9521$ |
| **Refined Random Forest** | **$14.5793\text{ meals}$** | **$20.6869\text{ meals}$** | **$0.9543$** |

### 6.2 Feature Importance Breakdown
- `Meals_Prepared`: **48.2%**
- `Customers_Forecast`: **26.7%**
- `Day` (Day-of-week demand variance): **8.5%**
- `Festival` & `Event_Type`: **6.8%**
- `Weather` & `Staff_Count`: **9.8%**

### 6.3 Discussion
The empirical results confirm that pre-service surplus volume is primarily determined by preparation volume and forecast footfall divergence, while environmental factors (such as rain or storm conditions) modulate the final surplus magnitude. Setting `max_depth=15` yielded optimal generalization with an $R^2$ of 0.9543. The average prediction error of $\sim 14.6\text{ meals}$ is well within operational tolerance for banquet and restaurant redistribution.

---

## CHAPTER 7: TEAM REFLECTION AND LEARNING OUTCOMES

### 7.1 Individual Reflections

- **`[STUDENT 1 NAME]` (ML / Data Lead):**  
  *Technical Learning:* Gained deep practical experience in tabular data preprocessing with `ColumnTransformer` and avoiding target leakage.  
  *Challenge:* Ensuring that `Meals_Sold` was strictly isolated during synthetic generation and pipeline training.  
  *Solution:* Automated validation scripts to assert zero presence of target leakage columns.  
  *Future Goal:* Experiment with Gradient Boosted Trees (XGBoost/LightGBM) on real-world datasets.

- **`[STUDENT 2 NAME]` (Backend / API Architect):**  
  *Technical Learning:* Mastered FastAPI asynchronous request handling, Pydantic type validation, and serialization of ML models.  
  *Challenge:* Maintaining sub-second execution across sequential API stages (prediction $\rightarrow$ matching $\rightarrow$ routing).  
  *Solution:* Optimized mathematical calculations in numpy/math and avoided blocking I/O.  
  *Future Goal:* Implement OAuth2 JWT authentication and PostgreSQL persistence.

- **`[STUDENT 3 NAME]` (Frontend / UI Developer):**  
  *Technical Learning:* Built responsive single-page workflows in React 19 and dynamic SVG map vector rendering.  
  *Challenge:* Coordinating multi-step state transitions without losing previous prediction context.  
  *Solution:* Implemented unified state management with local storage persistence.  
  *Future Goal:* Integrate Leaflet / Mapbox for interactive map tiles.

- **`[STUDENT 4 NAME]` (Integration & Testing Lead):**  
  *Technical Learning:* Implemented comprehensive test suites spanning unit tests, integration tests, and security boundaries.  
  *Challenge:* Validating edge cases such as zero surplus or negative numbers.  
  *Solution:* Constructed 91 automated tests asserting 100% pass rate.  
  *Future Goal:* Set up continuous integration (CI) pipelines on GitHub Actions.

---

## CHAPTER 8: CONCLUSION AND FUTURE SCOPE

### 8.1 Conclusion
The CIBUS-AI project successfully demonstrated an automated, end-to-end decision-support pipeline unifying predictive machine learning with logistics heuristics. By predicting commercial food surplus before meal service begins ($R^2 = 0.9543$, $\text{MAE} = 14.58\text{ meals}$), matching compatible NGOs, and optimizing pickup routing, the system demonstrates how AI can proactively mitigate food waste and enhance community nourishment.

### 8.2 Future Scope (Future Roadmap)
1. **Real-World Restaurant POS Integration:** Direct API connectors to point-of-sale systems (Toast, Square) and inventory management tools.
2. **Turn-by-Turn Road Routing:** Replace Haversine straight-line approximations with live Google Maps / OpenStreetMap road graph routing.
3. **Live Traffic Telemetry:** Dynamic travel time estimation accounting for real-time traffic congestion.
4. **Mobile Driver Application:** Flutter/React Native mobile app for pickup drivers with QR-code delivery verification.
5. **Multi-Tenant Cloud Deployment:** Migration from local JSON files to PostgreSQL database with role-based access control.
6. **Advanced Time-Series Modeling:** Deep learning LSTM or Transformer architectures for multi-day demand forecasting.
