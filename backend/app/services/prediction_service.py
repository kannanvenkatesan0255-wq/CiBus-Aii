"""
CIBUS-AI - Backend Prediction Integration Service
File: backend/app/services/prediction_service.py

Purpose:
Acts as the bridge between FastAPI routes and the existing trained ML engine:
1. Imports and invokes predict_surplus() from ai-engine/prediction/predict.py.
2. Uses the pre-trained RandomForestRegressor and ColumnTransformer without retraining.
3. Formats predictions into structured domain responses with actionable redistribution guidance.
4. Provides health check and model metadata retrieval.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Tuple

# Locate project roots dynamically
SERVICE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SERVICE_DIR.parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
AI_ENGINE_DIR = PROJECT_ROOT / "ai-engine"

# Ensure ai-engine is in sys.path for direct module import
if str(AI_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(AI_ENGINE_DIR))

try:
    from prediction.predict import predict_surplus, load_inference_artifacts
    from preprocessing.preprocess import FEATURE_COLUMNS, TARGET_COLUMN
except ImportError as err:
    raise ImportError(
        f"Failed to import CIBUS-AI prediction engine from '{AI_ENGINE_DIR}'. Error: {err}"
    )


class PredictionService:
    """
    Encapsulates ML prediction workflow, artifact verification, and metadata queries.
    Strictly uses pre-trained serialized models (Zero Retraining).
    """

    @classmethod
    def check_artifacts(cls) -> Tuple[bool, bool]:
        """
        Verifies that serialized model and preprocessor artifacts exist and can be loaded.
        
        Returns:
            Tuple[bool, bool]: (model_loaded, preprocessor_loaded)
        """
        try:
            model, preprocessor = load_inference_artifacts()
            model_ok = model is not None
            preprocessor_ok = preprocessor is not None
            return model_ok, preprocessor_ok
        except Exception:
            return False, False

    @classmethod
    def predict(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes prediction on input features using the existing ML engine.
        
        Parameters:
            input_data: Validated dictionary matching FEATURE_COLUMNS schema.
            
        Returns:
            Dict containing predicted surplus meals and logistical recommendations.
        """
        raw_prediction = predict_surplus(input_data)
        predicted_meals = float(raw_prediction)

        # Generate contextual redistribution recommendation
        if predicted_meals < 15.0:
            recommendation = "Low surplus expected. Standard kitchen inventory management sufficient."
        elif predicted_meals < 60.0:
            recommendation = (
                f"Moderate surplus (~{int(round(predicted_meals))} meals). "
                "Alert local community shelter for same-day evening pickup."
            )
        else:
            recommendation = (
                f"High surplus forecast (~{int(round(predicted_meals))} meals). "
                "Activate CIBUS-AI regional NGO redistribution protocol and dispatch volunteer couriers."
            )

        return {
            "predicted_surplus_meals": predicted_meals,
            "model_name": "RandomForestRegressor (Tuned, max_depth=15, n_estimators=200)",
            "status": "success",
            "input_summary": {
                "day": input_data.get("Day"),
                "weather": input_data.get("Weather"),
                "customers_forecast": input_data.get("Customers_Forecast"),
                "meals_prepared": input_data.get("Meals_Prepared"),
                "event_type": input_data.get("Event_Type"),
                "festival": input_data.get("Festival"),
                "staff_count": input_data.get("Staff_Count"),
                "avg_rating": input_data.get("Avg_Rating"),
                "special_event": input_data.get("Special_Event")
            },
            "recommended_action": recommendation
        }

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """
        Retrieves factual model specifications and evaluation results.
        """
        results_path = AI_ENGINE_DIR / "evaluation" / "final_results.json"
        metrics = {}
        if results_path.exists():
            try:
                with open(results_path, "r", encoding="utf-8") as f:
                    eval_data = json.load(f)
                    metrics = eval_data.get("metrics", {})
            except Exception:
                metrics = {"note": "Could not read evaluation file"}

        return {
            "model_name": "CIBUS-AI Food Surplus Regressor",
            "model_type": "RandomForestRegressor (scikit-learn)",
            "target_variable": TARGET_COLUMN,
            "feature_count": len(FEATURE_COLUMNS),
            "features": FEATURE_COLUMNS,
            "evaluation_metrics": metrics,
            "status": "active"
        }
