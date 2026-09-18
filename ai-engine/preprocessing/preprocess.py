"""
CIBUS-AI - Data Preprocessing & Encoding Pipeline
File: ai-engine/preprocessing/preprocess.py

Purpose:
Loads, validates, and preprocesses the food surplus dataset for model training:
1. Enforces data-leakage prevention (omits Meals_Sold and keeps Target isolated).
2. Performs data validation checks (missing values, duplicates, physical constraints).
3. Partitions data into 80% training and 20% testing subsets (random_state=42).
4. Fits categorical One-Hot Encoders strictly on training data (X_train) to prevent leakage.
5. Transforms both training and testing feature matrices.
6. Serializes the fitted preprocessor object to ai-engine/models/ for reuse in inference.
"""

import os
from typing import Dict, List, Tuple, Union, Any
import numpy as np
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split

# Directory Constants
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_ENGINE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
DATASET_PATH = os.path.join(AI_ENGINE_DIR, "dataset", "food_surplus.csv")
MODELS_DIR = os.path.join(AI_ENGINE_DIR, "models")
PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "preprocessor.joblib")
ENCODERS_BACKUP_PATH = os.path.join(MODELS_DIR, "label_encoders.pkl")

# Schema Definitions
CATEGORICAL_FEATURES: List[str] = ["Day", "Weather", "Festival", "Event_Type"]
NUMERICAL_FEATURES: List[str] = [
    "Customers_Forecast",
    "Meals_Prepared",
    "Staff_Count",
    "Avg_Rating",
    "Special_Event"
]
FEATURE_COLUMNS: List[str] = CATEGORICAL_FEATURES + NUMERICAL_FEATURES
TARGET_COLUMN: str = "Surplus_Meals"
EXPECTED_ALL_COLUMNS: List[str] = FEATURE_COLUMNS + [TARGET_COLUMN]


def validate_raw_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validates dataset integrity and checks against data leakage.

    Raises:
        ValueError: If unexpected schema or data leakage (e.g. Meals_Sold) is detected.
    """
    # 1. Leakage check
    if "Meals_Sold" in df.columns:
        raise ValueError(
            "CRITICAL DATA LEAKAGE: 'Meals_Sold' detected in dataset! "
            "Meals_Sold is a post-service metric and must not be used."
        )

    # 2. Schema check
    missing_cols = [col for col in EXPECTED_ALL_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset is missing required columns: {missing_cols}")

    # 3. Integrity calculations
    missing_count = int(df.isnull().sum().sum())
    duplicate_count = int(df.duplicated().sum())
    target_negative_count = int((df[TARGET_COLUMN] < 0).sum())

    if target_negative_count > 0:
        raise ValueError(f"Found {target_negative_count} records with negative Surplus_Meals!")

    return {
        "total_rows": len(df),
        "total_cols": len(df.columns),
        "missing_values": missing_count,
        "duplicate_rows": duplicate_count,
        "target_min": float(df[TARGET_COLUMN].min()),
        "target_max": float(df[TARGET_COLUMN].max()),
        "target_mean": float(df[TARGET_COLUMN].mean()),
        "target_std": float(df[TARGET_COLUMN].std())
    }


def build_preprocessor() -> ColumnTransformer:
    """
    Constructs a scikit-learn ColumnTransformer for categorical One-Hot Encoding
    while passing numerical features through in their original physical units.

    Returns:
        ColumnTransformer: Configured preprocessor.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                    drop=None
                ),
                CATEGORICAL_FEATURES
            ),
            (
                "num",
                "passthrough",
                NUMERICAL_FEATURES
            )
        ],
        remainder="drop"
    )
    return preprocessor


def get_feature_names(preprocessor: ColumnTransformer) -> List[str]:
    """
    Extracts human-readable names for all transformed columns.
    """
    try:
        cat_encoder = preprocessor.named_transformers_["cat"]
        cat_feature_names = list(cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES))
    except Exception:
        cat_feature_names = [f"cat_{i}" for i in range(len(CATEGORICAL_FEATURES))]

    return cat_feature_names + NUMERICAL_FEATURES


def preprocess_pipeline(
    dataset_path: str = DATASET_PATH,
    test_size: float = 0.2,
    random_state: int = 42,
    save_artifacts: bool = True
) -> Tuple[np.ndarray, np.ndarray, pd.Series, pd.Series, ColumnTransformer, List[str]]:
    """
    Executes the end-to-end data preprocessing pipeline:
    1. Loads dataset and validates schema/leakage rules.
    2. Separates input features X and target y.
    3. Splits data into train (80%) and test (20%) partitions with fixed random seed.
    4. Fits preprocessor strictly on X_train.
    5. Transforms X_train and X_test.
    6. Saves preprocessor artifact to models/ directory for production reuse.

    Returns:
        Tuple containing:
        - X_train_proc (np.ndarray)
        - X_test_proc (np.ndarray)
        - y_train (pd.Series)
        - y_test (pd.Series)
        - preprocessor (ColumnTransformer)
        - feature_names (List[str])
    """
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset file not found at: {dataset_path}")

    # Step 1: Load raw data
    df = pd.read_csv(dataset_path)

    # Step 2: Validate dataset integrity
    validation_info = validate_raw_dataframe(df)

    # Step 3: Separate X and y (Target is NEVER included in X)
    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].copy()

    # Step 4: Split data BEFORE fitting transformations (prevents data leakage)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        shuffle=True
    )

    # Step 5: Build and fit preprocessor ONLY on X_train
    preprocessor = build_preprocessor()
    preprocessor.fit(X_train)

    # Step 6: Transform both training and testing feature matrices
    X_train_proc = preprocessor.transform(X_train)
    X_test_proc = preprocessor.transform(X_test)
    feature_names = get_feature_names(preprocessor)

    # Step 7: Serialize preprocessor objects for inference reuse
    if save_artifacts:
        os.makedirs(MODELS_DIR, exist_ok=True)
        joblib.dump(preprocessor, PREPROCESSOR_PATH)
        joblib.dump(preprocessor, ENCODERS_BACKUP_PATH)

    return X_train_proc, X_test_proc, y_train, y_test, preprocessor, feature_names


def transform_single_input(
    input_data: Union[Dict[str, Any], pd.DataFrame],
    preprocessor: ColumnTransformer = None
) -> np.ndarray:
    """
    Transforms a single operational record or batch dataframe using the fitted preprocessor.
    Used by predict.py for real-time inference.

    Parameters:
        input_data: Dictionary or DataFrame containing pre-service operational features.
        preprocessor: Fitted ColumnTransformer instance. If None, loads from disk.

    Returns:
        np.ndarray: Transformed numerical feature vector ready for model.predict().
    """
    if preprocessor is None:
        if not os.path.exists(PREPROCESSOR_PATH):
            raise FileNotFoundError(
                f"Pre-fitted preprocessor not found at {PREPROCESSOR_PATH}. "
                "Run preprocess.py first to build artifacts."
            )
        preprocessor = joblib.load(PREPROCESSOR_PATH)

    if isinstance(input_data, dict):
        df_input = pd.DataFrame([input_data])
    else:
        df_input = input_data.copy()

    # Verify input features
    missing_inputs = [col for col in FEATURE_COLUMNS if col not in df_input.columns]
    if missing_inputs:
        raise ValueError(f"Input data is missing required feature columns: {missing_inputs}")

    # Enforce leakage check
    if "Meals_Sold" in df_input.columns:
        raise ValueError("Target leakage error: 'Meals_Sold' must not be provided at prediction time!")

    df_selected = df_input[FEATURE_COLUMNS]
    return preprocessor.transform(df_selected)


def run_and_print_summary():
    """Runs the preprocessing pipeline and displays a formatted summary."""
    print("=" * 65)
    print("        CIBUS-AI DATA PREPROCESSING & ENCODING REPORT")
    print("=" * 65)

    X_train_proc, X_test_proc, y_train, y_test, preprocessor, feature_names = preprocess_pipeline(
        dataset_path=DATASET_PATH,
        test_size=0.2,
        random_state=42,
        save_artifacts=True
    )

    df_raw = pd.read_csv(DATASET_PATH)

    print("\n[1] DATASET INTEGRITY & LEAKAGE CHECK:")
    print(f"    - Original Shape: {df_raw.shape[0]} rows x {df_raw.shape[1]} columns")
    print(f"    - Missing Values: {df_raw.isnull().sum().sum()}")
    print(f"    - Duplicate Rows: {df_raw.duplicated().sum()}")
    print(f"    - Meals_Sold Present: {'Meals_Sold' in df_raw.columns} (Leakage-Free)")
    print(f"    - Target Name: '{TARGET_COLUMN}' (Continuous Regression Target)")

    print("\n[2] TRAIN / TEST PARTITIONING (80/20 Split, random_state=42):")
    print(f"    - Training Set Shape (X_train): {X_train_proc.shape[0]} rows x {X_train_proc.shape[1]} features")
    print(f"    - Testing Set Shape  (X_test):  {X_test_proc.shape[0]} rows x {X_test_proc.shape[1]} features")
    print(f"    - Training Target (y_train):    {len(y_train)} labels (Mean={y_train.mean():.2f}, Std={y_train.std():.2f})")
    print(f"    - Testing Target  (y_test):     {len(y_test)} labels (Mean={y_test.mean():.2f}, Std={y_test.std():.2f})")

    print("\n[3] TRANSFORMED FEATURE SCHEMA:")
    print(f"    - Total Transformed Features: {len(feature_names)}")
    print("    - Feature List:")
    for idx, fname in enumerate(feature_names, 1):
        print(f"       {idx:2d}. {fname}")

    print(f"\n[4] SERIALIZED ARTIFACTS:")
    print(f"    - Preprocessor Saved: {PREPROCESSOR_PATH} ({os.path.getsize(PREPROCESSOR_PATH)} bytes)")
    print(f"    - Backup Encoders Saved: {ENCODERS_BACKUP_PATH} ({os.path.getsize(ENCODERS_BACKUP_PATH)} bytes)")

    print("\n" + "=" * 65)
    print("      PREPROCESSING PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 65)


if __name__ == "__main__":
    run_and_print_summary()
