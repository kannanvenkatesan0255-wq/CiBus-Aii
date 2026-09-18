# CIBUS-AI Engine

This directory houses the core Machine Learning engine for predicting food surplus in commercial food establishments.

---

## Directory Architecture

```
ai-engine/
│
├── dataset/
│   ├── generate_dataset.py       # Script to generate realistic synthetic dataset
│   └── food_surplus.csv          # Generated dataset file (produced after generation step)
│
├── preprocessing/
│   └── preprocess.py             # Feature encoding, scaling, and train/test split utilities
│
├── training/
│   ├── train_baseline.py         # Linear regression benchmark baseline
│   ├── train_model.py            # Primary Random Forest regressor training pipeline
│   └── feature_importance.py     # Script to extract and analyze feature importances
│
├── models/
│   ├── food_surplus_model.pkl    # Serialized trained model (generated after training)
│   └── label_encoders.pkl        # Serialized categorical encoders (generated after preprocessing)
│
├── prediction/
│   └── predict.py                # Standalone inference script for new pre-service input records
│
├── evaluation/
│   └── evaluate_model.py         # Model evaluation script (computes MAE, RMSE, R² & generates plots)
│
├── plots/
│   ├── actual_vs_predicted.png   # True vs. Predicted residual plot (generated after evaluation)
│   └── feature_importance.png    # Feature importance bar chart (generated after evaluation)
│
├── requirements.txt              # Python library dependencies
└── README.md                     # Engine documentation
```

---

## Setup & Installation

To set up the Python environment:

```bash
# 1. Navigate to the ai-engine directory
cd ai-engine

# 2. Create a virtual environment (optional but recommended)
python -m venv venv

# 3. Activate the virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Windows CMD:
.\venv\Scripts\activate.bat
# On Linux/macOS:
source venv/bin/activate

# 4. Install required dependencies
pip install -r requirements.txt
```

---

## Execution Workflow (Standard Execution Sequence)

1. **Dataset Generation:**
   ```bash
   python dataset/generate_dataset.py
   ```
2. **Model Training:**
   ```bash
   python training/train_baseline.py
   python training/train_model.py
   ```
3. **Evaluation & Visualization:**
   ```bash
   python evaluation/evaluate_model.py
   python training/feature_importance.py
   ```
4. **Single-Record Prediction:**
   ```bash
   python prediction/predict.py
   ```

*Note: Execution scripts are structured for upcoming project phases.*
