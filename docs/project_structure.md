# CIBUS-AI Repository Project Structure

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *Predict. Connect. Nourish.*  

---

```
CiBus-Ai R/
├── ai-engine/                  # Machine Learning & Data Pipeline
│   ├── dataset/                # Dataset generation & validation
│   │   ├── food_surplus.csv    # 8,000-row synthetic surplus dataset
│   │   ├── generate_dataset.py # Synthetic data generation script
│   │   └── validate_dataset.py # Automated 5-point dataset validation script
│   ├── evaluation/             # Model evaluation & performance metrics
│   │   ├── evaluate.py         # Evaluation calculation script (MAE, RMSE, R²)
│   │   ├── feature_importance.py # Mean decrease in impurity analyzer
│   │   └── final_results.json  # Serialized metrics (MAE: 14.58, RMSE: 20.69, R²: 0.9543)
│   ├── models/                 # Serialized model & transformer artifacts
│   │   ├── food_surplus_model.pkl # Trained RandomForestRegressor (Joblib)
│   │   └── food_surplus_preprocessor.pkl # Trained ColumnTransformer pipeline
│   ├── prediction/             # Reusable inference engine
│   │   ├── predict.py          # Prediction module with boundary clamping
│   │   └── test_predict.py     # 9 unit tests for inference validity
│   └── training/               # Model training scripts
│       ├── baseline_model.py   # Baseline Random Forest training
│       ├── preprocess.py       # Preprocessor construction script
│       └── train_model.py      # Refined model training script
│
├── backend/                    # FastAPI Backend Application Layer
│   ├── data/                   # Data stores
│   │   ├── activity_log.json   # Local JSON session persistence store
│   │   └── ngos.json           # Synthetic recipient NGO directory
│   ├── routers/                # FastAPI route controllers
│   │   ├── dashboard.py        # /api/dashboard/summary & /api/dashboard/recent-activity
│   │   ├── ngo.py              # /api/match-ngos endpoint
│   │   ├── prediction.py       # /api/predict endpoint
│   │   └── route.py            # /api/optimize-route endpoint
│   ├── schemas/                # Pydantic data validation schemas
│   │   ├── dashboard.py        # Dashboard summary & activity schemas
│   │   ├── ngo.py              # NGO request & allocation schemas
│   │   ├── prediction.py       # Input feature schema with range validation
│   │   └── route.py            # Route optimization request & response schemas
│   ├── services/               # Core application logic & algorithms
│   │   ├── analytics_service.py# Dashboard aggregation & environmental offset calculations
│   │   ├── ngo_service.py      # Radius filtering & greedy meal capacity allocation
│   │   ├── prediction_service.py # Preprocessing & ML inference invocation
│   │   └── route_service.py    # Haversine distance matrix & nearest neighbor optimizer
│   ├── tests/                  # Backend & Security automated tests (54 tests)
│   │   ├── test_analytics_service.py # Analytics calculation tests
│   │   ├── test_api_prediction.py    # Prediction endpoint integration tests
│   │   ├── test_e2e_workflow.py      # Complete multi-step workflow integration tests
│   │   ├── test_error_handling.py    # Edge case & validation failure tests
│   │   ├── test_ngo_matching.py      # NGO rule-matching & allocation tests
│   │   ├── test_route_optimization.py# Haversine & routing heuristic tests
│   │   └── test_security.py          # CORS, headers, & secret exposure tests
│   ├── config.py               # Application configuration & path resolution
│   ├── logging_config.py       # Structured logging configuration
│   ├── main.py                 # FastAPI application factory & middleware setup
│   └── requirements.txt        # Backend Python dependencies
│
├── frontend/                   # React Single-Page Application
│   ├── src/                    # Source code
│   │   ├── components/         # Modular UI components
│   │   │   ├── ImpactDashboard.jsx     # Sustainability metrics & activity history
│   │   │   ├── Navbar.jsx              # Application navigation & branding
│   │   │   ├── NgoMatchingSection.jsx  # NGO selection & allocation table
│   │   │   ├── PredictionForm.jsx      # Input form with validation & result card
│   │   │   ├── RoutePlanningSection.jsx# Route waypoint list & SVG map plotting
│   │   │   └── WorkflowTracker.jsx     # Step-by-step progress indicator
│   │   ├── services/           # HTTP API client services
│   │   │   └── api.js          # Axios API wrappers for FastAPI backend
│   │   ├── App.jsx             # Main application orchestrator & state manager
│   │   ├── index.css           # Tailwind CSS directives & global styling
│   │   └── main.jsx            # React root entrypoint
│   ├── tests/                  # Frontend automated verification suite
│   │   └── frontend_test.cjs   # 23 automated frontend tests
│   ├── index.html              # HTML5 entrypoint with metadata
│   ├── package.json            # Node.js dependencies & test scripts
│   ├── postcss.config.js       # PostCSS plugins
│   ├── tailwind.config.js      # Tailwind CSS theme configuration
│   └── vite.config.js          # Vite build configuration
│
├── docs/                       # Comprehensive Project Documentation
│   ├── final_architecture.md   # System architecture diagram & component details
│   ├── pbl_report_content.md   # Complete PBL academic report content
│   ├── references.md           # Verified IEEE-format citations
│   ├── appendix.md             # Complete appendices A through F
│   ├── team_roles.md           # Team roles & member placeholders
│   ├── demo_script.md          # 5-7 minute oral presentation & demo script
│   ├── presentation_content.md # 15-slide presentation content
│   ├── viva_questions.md       # 25+ comprehensive viva questions with answers
│   ├── project_structure.md    # Repository directory & module breakdown
│   ├── limitations.md          # System, data, and algorithmic limitations
│   ├── final_project_audit.md  # 11-point factual audit report
│   ├── demo_input.md           # Verified synthetic test input payloads
│   ├── screenshot_checklist.md # 10-point interface screenshot guide
│   ├── final_submission_checklist.md # Final PBL readiness checklist
│   ├── final_test_report.md    # Automated test execution report
│   ├── weekly_progress.md      # 10-week PBL progress log
│   └── README.md               # Documentation index & navigation
│
├── .env.example                # Safe environment variable configuration template
├── .gitignore                  # Comprehensive git exclusion list (no secrets, no node_modules)
├── package.json                # Root package configuration
├── requirements.txt            # Root Python dependencies specification
└── README.md                   # Top-level project README
```
