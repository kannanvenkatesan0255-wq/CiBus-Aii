# CIBUS-AI Project Quality Audit and Verification Report

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *"Predict. Connect. Nourish."*  
**Date:** September 2026  
**Institution:** Chennai Institute of Technology (CIT)  
**Task:** Complete Project Quality Audit and Final Machine Learning Verification  

---

## 1. Project Structure
**Status:** PASS

### Structure Verification
The physical workspace directory hierarchy conforms exactly to the architectural specification:

```
CIBUS-AI/
├── ai-engine/
│   ├── dataset/
│   │   ├── .gitkeep
│   │   ├── food_surplus.csv
│   │   ├── generate_dataset.py
│   │   └── validate_dataset.py
│   ├── preprocessing/
│   │   └── preprocess.py
│   ├── training/
│   │   ├── train_baseline.py
│   │   ├── train_model.py
│   │   └── feature_importance.py
│   ├── models/
│   │   ├── .gitkeep
│   │   ├── baseline_food_surplus_model.pkl
│   │   ├── baseline_preprocessor.pkl
│   │   ├── food_surplus_model.pkl
│   │   ├── food_surplus_preprocessor.pkl
│   │   ├── label_encoders.pkl
│   │   └── preprocessor.joblib
│   ├── prediction/
│   │   ├── predict.py
│   │   └── test_predict.py
│   ├── evaluation/
│   │   ├── baseline_results.json
│   │   ├── final_results.json
│   │   ├── model_comparison.json
│   │   ├── model_comparison.md
│   │   ├── feature_importance.csv
│   │   ├── feature_importance_summary.json
│   │   └── predictions.csv
│   ├── plots/
│   │   ├── .gitkeep
│   │   ├── feature_importance.png
│   │   ├── actual_vs_predicted.png
│   │   └── residual_analysis.png
│   ├── requirements.txt
│   └── README.md
├── docs/
│   ├── project_overview.md
│   ├── dataset_description.md
│   ├── model_documentation.md
│   ├── prediction_documentation.md
│   ├── weekly_progress.md
│   ├── pbl_report_content.md
│   ├── references.md
│   ├── appendix.md
│   ├── documentation_audit.md
│   └── project_audit.md
├── README.md
└── .gitignore
```

### Artifact & Cleanliness Findings:
- No missing required files.
- No duplicate dataset copies exist outside `ai-engine/dataset/`.
- No broken relative paths; path resolution in all scripts uses dynamic directory anchors (`Path(__file__).resolve()`).
- `.gitignore` properly excludes `__pycache__/`, `*.pyc`, `venv/`, and untracked temporary model dumps while preserving reproducible CSV datasets, plots, and `.gitkeep` directory anchors.

---

## 2. Dataset
**Status:** PASS

- **Location:** `ai-engine/dataset/food_surplus.csv`
- **Row Count:** Exactly 8,000 records.
- **Column Count:** Exactly 10 columns:
  1. `Day` (Categorical: Monday – Sunday)
  2. `Weather` (Categorical: Sunny, Cloudy, Rainy, Stormy)
  3. `Customers_Forecast` (Integer: 60 – 950)
  4. `Meals_Prepared` (Integer: 84 – 1360)
  5. `Festival` (Categorical: No, Diwali, Eid, Christmas, New Year)
  6. `Event_Type` (Categorical: Regular, Buffet, Corporate, Banquet)
  7. `Staff_Count` (Integer: 5 – 48)
  8. `Avg_Rating` (Float: 2.51 – 5.00)
  9. `Special_Event` (Binary: 0 or 1)
  10. `Surplus_Meals` (Float target: 0.0 – 686.0)
- **Missing Values:** 0 null/missing cells across all 80,000 data points.
- **Duplicate Count:** 0 duplicate rows.
- **Data Types:** Valid numerical (integer/float) and object (string categorical) representations.
- **Target Integrity:** `Surplus_Meals` is non-negative ($0.0 \le y \le 686.0$, mean = $118.59$, std = $97.27$), with realistic domain relationships based on preparation buffer, weather disruption, and banquet/buffet event multipliers.
- **Forbidden Columns:** `Meals_Sold` is strictly non-existent in the dataset.
- **Reproducibility:** Dataset is fully reproducible by running `python ai-engine/dataset/generate_dataset.py` with fixed `SEED = 42`.

---

## 3. Data Leakage
**Status:** PASS (0% Data Leakage)

- **`Meals_Sold` Audit:** Strict codebase-wide scan confirmed that `Meals_Sold` is never computed, referenced, loaded, or accepted. `ai-engine/preprocessing/preprocess.py` and `ai-engine/prediction/predict.py` both contain explicit assertions that throw a `ValueError` if `Meals_Sold` is passed in any input payload.
- **Target Leakage Audit:** `Surplus_Meals` is explicitly decoupled from feature matrix $X$ prior to any transformation, fitting, or model interaction.
- **Train/Test Leakage Audit:** Train/test split is strictly isolated at 80/20 with `random_state=42`. All test samples ($N=1600$) remained strictly unseen during all preprocessing fitting, model training, and hyperparameter tuning phases.
- **Preprocessing Leakage Audit:** The `ColumnTransformer` (incorporating `OneHotEncoder(handle_unknown='ignore')` and numerical pass-through) is fitted strictly on $X_{\text{train}}$ via `preprocessor.fit(X_train)`. Transformations on $X_{\text{test}}$ and inference samples use only learned training distributions via `.transform()`.

---

## 4. Preprocessing
**Status:** PASS

- **Implementation:** `ai-engine/preprocessing/preprocess.py`
- **Feature/Target Separation:** Correctly splits input DataFrame into $X$ (9 raw feature columns) and $y$ (`Surplus_Meals`).
- **Categorical Handling:** Encodes 4 categorical variables (`Day`, `Weather`, `Festival`, `Event_Type`) into 20 one-hot binary columns using `handle_unknown='ignore'`.
- **Numerical Handling:** Passes 5 numerical/discrete variables (`Customers_Forecast`, `Meals_Prepared`, `Staff_Count`, `Avg_Rating`, `Special_Event`) without data distortion, expanding feature space from 9 raw to 25 transformed dimensions.
- **Split Configuration:** 80% training ($N=6400$) and 20% testing ($N=1600$) using `random_state=42`.
- **Persistence & Serialization:** Serialized cleanly as `ai-engine/models/food_surplus_preprocessor.pkl`.
- **Inference Alignment:** Exact same preprocessing pipeline is invoked dynamically during inference in `ai-engine/prediction/predict.py`.

---

## 5. Baseline Model
**Status:** PASS

- **Script:** `ai-engine/training/train_baseline.py`
- **Model Type:** `RandomForestRegressor`
- **Hyperparameters:** `n_estimators=100`, `random_state=42`, all other hyperparameters at scikit-learn defaults (unconstrained tree depth).
- **Target:** `Surplus_Meals`
- **Persisted Model:** `ai-engine/models/baseline_food_surplus_model.pkl` (File size: ~57.9 MB).
- **Verified Evaluation Metrics:**
  - Mean Absolute Error (MAE): **14.2939 meals**
  - Root Mean Squared Error (RMSE): **20.5429 meals**
  - Coefficient of Determination ($R^2$): **0.9549**
- **Match Confirmation:** Results in `ai-engine/evaluation/baseline_results.json` precisely match programmatic execution.

---

## 6. Final Model
**Status:** PASS

- **Script:** `ai-engine/training/train_model.py`
- **Model Type:** `RandomForestRegressor`
- **Tuning Methodology:** 5-Fold Cross-Validation (`GridSearchCV`) evaluated strictly on training partition ($X_{\text{train}}$) across candidate parameter combinations.
- **Selected Optimal Hyperparameters:**
  - `n_estimators`: `200`
  - `max_depth`: `15` (enforcing tree depth constraint for structural regularization)
  - `max_features`: `0.8` (sub-sampling feature subsets at splits to decorrelate ensemble trees)
  - `min_samples_split`: `4`
  - `min_samples_leaf`: `1`
  - `random_state`: `42`
  - `n_jobs`: `-1`
- **Persisted Model:** `ai-engine/models/food_surplus_model.pkl` (File size: ~40.4 MB, representing a 30.2% storage reduction compared to unconstrained baseline).
- **Verified Evaluation Metrics:**
  - Mean Absolute Error (MAE): **14.5793 meals**
  - Root Mean Squared Error (RMSE): **20.6869 meals**
  - Coefficient of Determination ($R^2$): **0.9543**
- **Match Confirmation:** Saved metrics in `ai-engine/evaluation/final_results.json` and model comparison logs match actual execution outputs identically.

---

## 7. Feature Importance
**Status:** PASS

- **Script:** `ai-engine/training/feature_importance.py`
- **Source:** Extracted directly from final trained model's `feature_importances_` property (Mean Decrease in Impurity / Gini Importance).
- **Properties Checked:**
  - Dimension count matches 25 transformed input features.
  - All values are non-negative numeric floats.
  - Total importance sums to approximately $1.000000$ ($100\%$).
  - `Meals_Sold` is strictly non-existent.
- **Aggregated Logical Feature Rankings (All 9 Domain Features):**
  1. `Meals_Prepared`: **0.4896** (48.96%) – Primary operational scale driver.
  2. `Event_Type`: **0.1651** (16.51%) – Large variance in buffets/banquets.
  3. `Weather`: **0.1603** (16.03%) – Severe rain/storm dining disruptions.
  4. `Staff_Count`: **0.1166** (11.66%) – Kitchen capacity and operational throughput.
  5. `Customers_Forecast`: **0.0246** (2.46%) – Footfall demand baseline.
  6. `Festival`: **0.0238** (2.38%) – Holiday preparation surges.
  7. `Special_Event`: **0.0079** (0.79%) – Discrete catering spikes.
  8. `Avg_Rating`: **0.0072** (0.72%) – Patronage consistency.
  9. `Day`: **0.0048** (0.48%) – Day-of-week demand variance.
- **Visual Artifact:** `ai-engine/plots/feature_importance.png` exists, is readable, and visually illustrates transformed feature rankings.
- **Scientific Caveat:** Documented clearly as ensemble association/importance, without making unfounded claims of direct physical causation.

---

## 8. Evaluation
**Status:** PASS

- **Script:** `ai-engine/evaluation/evaluate_model.py`
- **Test Set Size:** Exactly 1,600 held-out samples.
- **Predictions Table:** `ai-engine/evaluation/predictions.csv` contains:
  - `Actual_Surplus_Meals`
  - `Predicted_Surplus_Meals`
  - `Residual` ($y - \hat{y}$)
- **Statistical Diagnostics:**
  - Actual Surplus Range: $[1.00, 643.70]$ meals (Mean = $116.14$)
  - Predicted Surplus Range: $[11.90, 632.70]$ meals (Mean = $116.41$)
  - Mean Residual Bias: **-0.2729 meals** (indicating an unbiased regression fit centered at 0)
  - Residual Standard Deviation: **20.6851 meals**
  - Accuracy Band ($\pm 15$ meals): **65.38%** of test samples
  - Accuracy Band ($\pm 25$ meals): **82.81%** of test samples
- **Diagnostic Plots:**
  - `ai-engine/plots/actual_vs_predicted.png`: Scatter plot showing strong alignment with the 45-degree ideal fit line ($R^2=0.9543$).
  - `ai-engine/plots/residual_analysis.png`: Residual distribution histogram + residual vs. predicted scatter plot showing homoscedastic dispersion around zero bias.

---

## 9. Prediction System
**Status:** PASS

- **Script:** `ai-engine/prediction/predict.py`
- **Components Verified:**
  - Autonomous loading of `food_surplus_model.pkl` and `food_surplus_preprocessor.pkl`.
  - Reusable programmatic API: `predict_surplus(input_data, return_details=False)`.
  - Input validation enforcing all 9 required schema fields, valid categories, and numerical boundaries.
  - Zero-floor clipping preventing negative meal predictions (`np.maximum(0.0, raw_pred)`).
  - Explicit rejection of `Meals_Sold` input payloads.
  - CLI Interface support for direct command-line arguments and `--batch` CSV file processing.
  - Zero retraining overhead; inference operates strictly via pre-trained artifacts.

---

## 10. Testing
**Status:** PASS

- **Test Suite:** `ai-engine/prediction/test_predict.py` (9 unit test cases executed using Python's `unittest` framework).
- **Dataset Suite:** `ai-engine/dataset/validate_dataset.py` (5 validation checks executed).
- **Audit Suite:** `ai-engine/audit_check.py` (Comprehensive end-to-end audit check).
- **Test Results Breakdown:**
  - `test_single_valid_prediction`: **PASSED** (Predicted = 33.79 meals)
  - `test_weekend_buffet_prediction`: **PASSED** (Predicted = 134.63 meals)
  - `test_festival_banquet_prediction`: **PASSED** (Predicted = 250.09 meals)
  - `test_stormy_weather_disruption`: **PASSED** (Predicted = 226.32 meals)
  - `test_high_volume_corporate`: **PASSED** (Predicted = 234.50 meals)
  - `test_batch_prediction`: **PASSED** (Batch shape = 2, output = `[28.49, 184.42]`)
  - `test_data_leakage_rejection`: **PASSED** (Rejects `Meals_Sold` with `ValueError`)
  - `test_missing_required_feature`: **PASSED** (Rejects incomplete schemas)
  - `test_numerical_boundary_validation`: **PASSED** (Rejects physically impossible numerical inputs)
- **Total Tests Passed:** 9 / 9 Unit Tests + All Dataset & Pipeline Verification Tests.
- **Tests Failed:** 0.
- **Issues Fixed During Audit:**
  - Removed over-constrained upper dependency pins in `ai-engine/requirements.txt` to guarantee forward compatibility across Python 3.10 through Python 3.14 environments.

---

## 11. Documentation
**Status:** PASS

All 11 project documentation files are synchronized, complete, and technically aligned:
1. `README.md`: Root project overview, architecture diagram, fast setup, CLI commands, and metrics summary.
2. `ai-engine/README.md`: AI engine pipeline execution instructions, architecture, and module breakdown.
3. `docs/project_overview.md`: Executive summary, problem definition, objectives, and workflow.
4. `docs/dataset_description.md`: Data schema, 10 column descriptions, synthesis logic, and distribution summaries.
5. `docs/model_documentation.md`: Mathematical formulations, baseline vs. final model comparison, tuning hyperparameters, and trade-off analysis.
6. `docs/prediction_documentation.md`: Inference API guide, validation rules, CLI examples, and operational workflows.
7. `docs/weekly_progress.md`: 8-week PBL development trajectory, milestones, and deliverables.
8. `docs/pbl_report_content.md`: Complete 8-chapter CIT PBL academic report content following standard institutional template.
9. `docs/references.md`: 12 scholarly literature citations (IEEE/ACM/Elsevier/Springer) and software libraries formatted in IEEE style.
10. `docs/appendix.md`: System specifications, project file tree, CLI commands, configuration parameters, and prompt execution history.
11. `docs/documentation_audit.md`: Cross-reference audit verifying metric synchronization across all markdown files.

### Integrity Checks:
- No false "accuracy percentage" terminology ($R^2$ correctly designated as explained variance).
- No fabricated mentor feedback or fake personal reflections (properly marked with `[TODO – TO BE PROVIDED]`).
- No claims of implemented full-stack web UI or live Google Maps integration (correctly documented as future scope).
- Exact match between documented numbers and JSON evaluation artifacts.

---

## 12. Reproducibility
**Status:** PASS

The entire machine learning lifecycle can be reproduced from scratch in strict deterministic order using the following execution sequence:

```bash
# 1. Install dependencies
pip install -r ai-engine/requirements.txt

# 2. Generate the 8,000-row synthetic dataset (seed=42)
python ai-engine/dataset/generate_dataset.py

# 3. Validate dataset integrity
python ai-engine/dataset/validate_dataset.py

# 4. Execute data preprocessing and fit preprocessor
python ai-engine/preprocessing/preprocess.py

# 5. Train baseline Random Forest model
python ai-engine/training/train_baseline.py

# 6. Perform hyperparameter tuning & train final regularized model
python ai-engine/training/train_model.py

# 7. Compute Random Forest feature importances & export chart
python ai-engine/training/feature_importance.py

# 8. Evaluate final model on test set & generate diagnostic plots
python ai-engine/evaluation/evaluate_model.py

# 9. Execute unit test suite
python -m unittest ai-engine/prediction/test_predict.py

# 10. Perform sample inference
python ai-engine/prediction/predict.py --day Friday --weather Rainy --customers 450 --prepared 600 --festival Diwali --event Buffet --staff 25 --rating 4.5 --special 1
```

---

## 13. Git & Repository Status
**Status:** PASS

- **Repository:** `https://github.com/kannanvenkatesan0255-wq/CiBus-Aii.git`
- **Active Branch:** `main`
- **Cleanliness:** No secrets, credentials, API keys, temporary logs, or `.env` files committed.
- **Git Tracking:** CSV dataset, diagnostic plots, code modules, and documentation files tracked; binary pickles ignored via `.gitignore` with directory `.gitkeep` placeholders.

---

## 14. Remaining Student / Academic Action Items (TODOs)
The following institutional items are strictly reserved for the student project team prior to final PBL report submission:

1. **Team Student Identification:** Insert student team member names, Register Numbers, Department, and Semester in `docs/pbl_report_content.md` (Title Page & Chapter 7).
2. **Faculty / Mentor Feedback:** Insert faculty supervisor and industry mentor review comments in `docs/pbl_report_content.md` (Chapter 3 / Chapter 7).
3. **Individual Student Learning Reflections:** Replace `[TODO – TO BE PROVIDED]` placeholders in Chapter 7 with personal first-person reflections from each team member.
4. **Institutional Sign-Off:** Print and obtain signatures on Certificate and Declaration pages for the physical report submission.

---

## 15. Final Readiness Summary
The CIBUS-AI Machine Learning Engine has completed all development, verification, and auditing requirements. The data pipeline is robust, reproducible, and mathematically sound with 0% data leakage. Model training and evaluation artifacts are fully consistent with all documentation. The codebase is clean, well-tested, beginner-friendly, and ready for institutional evaluation and future application-layer expansion.
