# Appendix: CIBUS-AI Machine Learning Engine

---

## Appendix A: Complete Source-Code Directory Layout
The complete implementation source code is structured as follows:

```
CIBUS-AI/
├── ai-engine/
│   ├── dataset/
│   │   ├── generate_dataset.py       # (Appendix B) Dataset generation script
│   │   ├── validate_dataset.py       # (Appendix J) Dataset validation suite
│   │   └── food_surplus.csv          # (Appendix B) 8,000-record dataset
│   │
│   ├── preprocessing/
│   │   └── preprocess.py             # (Appendix C) Preprocessing & One-Hot pipeline
│   │
│   ├── training/
│   │   ├── train_baseline.py         # (Appendix D) Baseline Random Forest training
│   │   ├── train_model.py            # (Appendix D) Hyperparameter tuning & final model
│   │   └── feature_importance.py     # (Appendix G) MDI feature importance extraction
│   │
│   ├── models/
│   │   ├── baseline_food_surplus_model.pkl   # Preserved baseline model (57.9 MB)
│   │   ├── food_surplus_model.pkl            # Final tuned model (40.4 MB)
│   │   └── food_surplus_preprocessor.pkl     # Preprocessor pipeline artifact
│   │
│   ├── evaluation/
│   │   ├── baseline_results.json     # Baseline benchmark metrics
│   │   ├── model_comparison.json     # (Appendix E) Comparison metrics
│   │   ├── model_comparison.md       # Comparative markdown report
│   │   ├── final_results.json        # (Appendix E) Final evaluation results
│   │   ├── feature_importance.csv    # (Appendix G) Ranked importance table
│   │   ├── feature_importance_summary.json
│   │   └── predictions.csv           # (Appendix E) Test predictions & residuals
│   │
│   ├── plots/
│   │   ├── actual_vs_predicted.png   # (Appendix E) Actual vs. Predicted plot
│   │   ├── residual_analysis.png     # (Appendix E) Residual scatter plot
│   │   └── feature_importance.png    # (Appendix G) MDI feature importance chart
│   │
│   ├── prediction/
│   │   ├── predict.py                # (Appendix F) Standalone inference engine & CLI
│   │   └── test_predict.py           # (Appendix J) Automated test suite
│   │
│   ├── requirements.txt
│   └── README.md
│
├── docs/
│   ├── pbl_report_content.md         # Full PBL report aligned with CIT template
│   ├── project_overview.md           # Scoping and problem formulation
│   ├── dataset_description.md        # Feature schema and leakage rules
│   ├── model_documentation.md        # ML methodology and metrics
│   ├── prediction_documentation.md   # Prediction API & CLI guide
│   ├── references.md                 # IEEE formatted citations
│   ├── appendix.md                   # This appendix document
│   ├── documentation_audit.md        # Consistency audit checklist
│   └── weekly_progress.md            # Weekly progress tracking log
│
├── .gitignore
└── README.md
```

---

## Appendix B: Dataset Generation
- **Source Script:** `ai-engine/dataset/generate_dataset.py`
- **Validation Script:** `ai-engine/dataset/validate_dataset.py`
- **Primary Data File:** `ai-engine/dataset/food_surplus.csv` ($N = 8,000$ rows, 10 columns, seed=42)
- **Zero-Leakage Assurance:** `Meals_Sold` is strictly omitted from the dataset.

---

## Appendix C: Preprocessing & Transformation Pipeline
- **Source Script:** `ai-engine/preprocessing/preprocess.py`
- **Serialized Preprocessor:** `ai-engine/models/food_surplus_preprocessor.pkl`
- **Feature Schema:** 25 transformed dimensions (20 One-Hot encoded categorical columns + 5 pass-through numerical features).
- **Leakage Prevention:** `ColumnTransformer` is fitted exclusively on $X_{\text{train}}$ ($6,400$ samples).

---

## Appendix D: Model Training & Hyperparameter Tuning
- **Baseline Training Script:** `ai-engine/training/train_baseline.py`
  - Model: `RandomForestRegressor(n_estimators=100, random_state=42)`
  - Benchmark Metrics: MAE = `14.2939`, RMSE = `20.5429`, $R^2 = 0.9549$
- **Final Refinement Script:** `ai-engine/training/train_model.py`
  - Model: `RandomForestRegressor(n_estimators=200, max_depth=15, max_features=0.8, min_samples_split=4, min_samples_leaf=1)`
  - Final Metrics: MAE = `14.5793`, RMSE = `20.6869`, $R^2 = 0.9543$
  - Serialized Artifacts: `ai-engine/models/food_surplus_model.pkl` (40.4 MB)

---

## Appendix E: Evaluation Results & Residual Plots
- **Evaluation Script:** `ai-engine/evaluation/evaluate_model.py`
- **Row-Level Test Predictions:** `ai-engine/evaluation/predictions.csv` ($1,600$ test records)
- **Machine-Readable Metrics:** `ai-engine/evaluation/final_results.json`, `ai-engine/evaluation/model_comparison.json`
- **Diagnostic Visualizations:**
  - `ai-engine/plots/actual_vs_predicted.png` (Linear diagonal calibration plot)
  - `ai-engine/plots/residual_analysis.png` (Residual distribution plot, $\bar{e} = -0.2729$ meals)

---

## Appendix F: Standalone Prediction & CLI Interface
- **Inference Script:** `ai-engine/prediction/predict.py`
- **API Function:** `predict_surplus(input_data)`
- **CLI Example:** `python ai-engine/prediction/predict.py --day Saturday --weather Sunny --customers 350 --meals 400 --event Regular --staff 12 --rating 4.3`
- **Actual CLI Output:** `>>> Predicted Surplus Meals: 41.14 meals <<<`

---

## Appendix G: Feature Importance Outputs
- **Extraction Script:** `ai-engine/training/feature_importance.py`
- **Ranking Table:** `ai-engine/evaluation/feature_importance.csv`
- **Summary JSON:** `ai-engine/evaluation/feature_importance_summary.json`
- **Visual Chart:** `ai-engine/plots/feature_importance.png` (Horizontal MDI bar chart)

---

## Appendix H: Version Control & GitHub Repository
- **Remote URL:** `https://github.com/kannanvenkatesan0255-wq/CiBus-Aii.git`
- **Tracking Branch:** `main`
- **Commit Traceability:** All incremental PBL milestones committed and synced with descriptive semantic commit messages.

---

## Appendix I: Weekly Progress Evidence Log
- **Weekly Progress Document:** `docs/weekly_progress.md`
- **Milestone Summary:**
  - Week 1: Problem Formulation & Architecture Setup
  - Week 2: Dataset Generation ($N=8,000$) & Validation
  - Week 3: Preprocessing & Encoding Pipeline
  - Week 4: Baseline Model & Hyperparameter Refinement
  - Week 5: Evaluation & Feature Importance Analysis
  - Week 6: Reusable Prediction Engine & Documentation

---

## Appendix J: Automated Testing & Verification Evidence
- **Test Suite Script:** `ai-engine/prediction/test_predict.py`
- **Test Results Summary:**
  - 9 out of 9 unit test cases passing (100% test pass rate).
  - Validates Normal Weekday, Weekend Buffet, Festival Banquet, Stormy Weather Disruption, High-Volume Corporate, Data Leakage Rejection, Missing Field Validation, Numerical Boundary Checking, and Batch DataFrame Inference.
