# Oral Presentation and Demonstration Script

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *Predict. Connect. Nourish.*  
**Target Duration:** 5 to 7 Minutes  
**Demonstration Mode:** Live Web Application Prototype (React + FastAPI + Scikit-Learn)

---

## 1. Timing Breakdown & Speaker Cue Sheet

```
+------------------+------------------------------------------------------+
| Timing           | Demonstration Stage                                  |
+------------------+------------------------------------------------------+
| 0:00 - 0:30      | Problem Introduction & Project Context               |
| 0:30 - 1:15      | Core Architecture & Technical Approach               |
| 1:15 - 2:30      | Live ML Food Surplus Prediction Demonstration        |
| 2:30 - 3:30      | NGO Matching & Intelligent Meal Allocation           |
| 3:30 - 4:30      | Haversine Multi-Stop Route Optimization & SVG Plot   |
| 4:30 - 5:30      | Real-Time Environmental Impact Dashboard             |
| 5:30 - 6:30      | Machine Learning Evaluation Metrics & Feature Weight |
| 6:30 - 7:00      | Technical Limitations, Future Scope & Conclusion     |
+------------------+------------------------------------------------------+
```

---

## 2. Detailed Demonstration Walkthrough

### 0:00 – 0:30 | Problem Introduction
> **Speaker:** "Respected evaluators, every day commercial food establishments—including restaurants, banquet halls, and institutional canteens—generate substantial edible food surplus due to unpredictable customer footfall and inflexible preparation schedules. Simultaneously, local relief organizations and shelters struggle with daily food insecurity.  
> The core bottleneck is that surplus notifications typically occur reactively *after* kitchen closing, leaving insufficient time to organize redistribution logistics.  
> To solve this, we present **CIBUS-AI**, an intelligent decision-support system under the motto: *Predict. Connect. Nourish.*"

---

### 0:30 – 1:15 | Architecture & Technical Approach
> **Speaker:** "CIBUS-AI bridges this gap through a unified three-tier architecture:
> 1. An offline-trained **Machine Learning Engine** using Random Forest Regression to predict surplus meal quantities before meal service begins.
> 2. A **FastAPI Application Layer** orchestrating rule-based NGO matching and Haversine distance-based route optimization.
> 3. A modern **React 19 Frontend** offering an interactive decision-support workflow and environmental impact analytics.  
> Let us now demonstrate the complete end-to-end workflow on the live application."

---

### 1:15 – 2:30 | ML Food Surplus Prediction Demo
> *(Action: Open the browser to the Prediction Interface).*
>
> **Speaker:** "Here on the prediction screen, a restaurant manager enters their operational parameters for the day:
> - **Day of Week:** Saturday
> - **Weather:** Rainy
> - **Expected Customer Footfall:** 280
> - **Meals Prepared:** 350
> - **Festival / Special Event:** Yes (Wedding reception)
> - **Staff Count:** 12, **Rating:** 4.5  
>
> When we click **'Predict Surplus'**, the input payload is sent to our FastAPI backend. The input is transformed through our scikit-learn `ColumnTransformer` (applying standard scaling and one-hot encoding) and evaluated by our trained `RandomForestRegressor`.  
> In less than 50 milliseconds, CIBUS-AI predicts an estimated surplus of **68 meals** (approx. 19.4% of total preparation).  
> Notice that `Meals_Sold` is strictly excluded from our model inputs to prevent target leakage and ensure true pre-service forecasting."

---

### 2:30 – 3:30 | NGO Matching & Meal Allocation Demo
> *(Action: Click 'Proceed to NGO Matching').*
>
> **Speaker:** "Now that we know we have 68 surplus meals to redistribute, we initiate the **NGO Matching Module**.  
> The system queries our synthetic local NGO database within a 15 km radius. The matching engine filters recipients based on operational status, meal acceptance criteria, and daily capacity.  
> Using a greedy allocation algorithm, CIBUS-AI distributes the 68 meals across compatible NGOs:
> - *Hope Shelter Home:* Allocated 40 meals (Capacity: 50)
> - *City Food Mission:* Allocated 28 meals (Capacity: 35)  
> All 68 meals are fully allocated, ensuring zero avoidable waste."

---

### 3:30 – 4:30 | Route Optimization & Visualization Demo
> *(Action: Click 'Generate Optimized Route').*
>
> **Speaker:** "Next, logistics planning requires an efficient delivery sequence to minimize travel time and transportation emissions.  
> When we trigger route optimization, our backend calculates the pairwise spherical distance matrix using the **Haversine formula**:
> $$d = 2r \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos \phi_1 \cos \phi_2 \sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$  
> It then solves the multi-stop dispatch using a greedy nearest-neighbor heuristic.  
> As shown on the screen, CIBUS-AI outputs the exact pickup sequence: *Donor Kitchen $\rightarrow$ Hope Shelter $\rightarrow$ City Food Mission*.  
> It calculates a total trip distance of **8.4 km** with an estimated travel duration of **21 minutes**, visualized dynamically via an interactive SVG route plot."

---

### 4:30 – 5:30 | Environmental Impact Dashboard Demo
> *(Action: Navigate to the Impact Dashboard).*
>
> **Speaker:** "Upon completing a planning session, the session is saved to our local activity persistence store, and the **Impact Dashboard** updates instantly.  
> The dashboard aggregates historical sessions and converts redistributed meals into standard environmental impact indicators:
> - **Total Meals Planned & Saved**
> - **Estimated Greenhouse Gas ($CO_2$) Emissions Prevented** ($2.5\text{ kg } CO_2\text{e per meal}$)
> - **Estimated Embedded Water Conserved** ($1,000\text{ liters per meal}$)  
> This provides actionable accountability metrics for sustainability reporting."

---

### 5:30 – 6:30 | ML Model Metrics & Validation
> **Speaker:** "Let us examine the empirical performance of our machine learning pipeline.  
> Trained on an 8,000-record dataset with an 80/20 train-test partition ($random\_state=42$), our refined Random Forest model achieves:
> - **Mean Absolute Error (MAE):** $14.58\text{ meals}$
> - **Root Mean Squared Error (RMSE):** $20.69\text{ meals}$
> - **Coefficient of Determination ($R^2$):** $0.9543$  
> Importantly, $R^2$ represents the proportion of variance explained by the model, not a percentage accuracy.  
> Feature importance analysis reveals that `Meals_Prepared` (48.2%) and `Customers_Forecast` (26.7%) are the strongest predictors for the decision trees, while day-of-week and weather conditions provide crucial demand modulation."

---

### 6:30 – 7:00 | Limitations, Future Scope & Conclusion
> **Speaker:** "To maintain academic honesty, we highlight key project limitations:
> - The dataset and NGO directory are synthetic and designed for prototype demonstration.
> - Route distances are calculated via straight-line Haversine math rather than live road turn-by-turn navigation or real-time traffic APIs.
> - The software provides a *redistribution plan*; it does not execute physical transport or confirm live deliveries.  
> In future work, we aim to integrate real-world food bank APIs, GPS fleet tracking, and deep learning time-series architectures.  
> In conclusion, CIBUS-AI demonstrates how machine learning and algorithmic planning can transform surplus food management from reactive disposal into proactive community nourishment.  
> Thank you, and we look forward to your questions."
