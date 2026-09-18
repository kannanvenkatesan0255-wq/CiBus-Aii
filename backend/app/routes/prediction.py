"""
CIBUS-AI - Prediction API Routes
File: backend/app/routes/prediction.py

Purpose:
Exposes RESTful endpoints for food surplus prediction and model information.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas import (
    PredictionRequest,
    PredictionResponse,
    ModelInfoResponse
)
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/api", tags=["Surplus Prediction & Intelligence"])


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict Surplus Meals",
    description=(
        "Accepts operational, meteorological, and demand features for a scheduled meal service "
        "and forecasts the quantity of surplus meals using the trained CIBUS-AI Random Forest model."
    )
)
async def predict_food_surplus(payload: PredictionRequest) -> PredictionResponse:
    """
    Real-time surplus food forecasting endpoint.
    """
    try:
        input_data = payload.model_dump()
        result = PredictionService.predict(input_data)
        return PredictionResponse(**result)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except FileNotFoundError as fnf_err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model artifact unavailable: {str(fnf_err)}"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference execution failed: {str(exc)}"
        )


@router.get(
    "/model-info",
    response_model=ModelInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Model Information & Metrics",
    description="Returns metadata, required feature schema, and evaluated performance metrics of the active ML model."
)
async def get_model_information() -> ModelInfoResponse:
    """
    Returns active ML model specifications and evaluation results.
    """
    try:
        metadata = PredictionService.get_metadata()
        return ModelInfoResponse(**metadata)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve model metadata: {str(exc)}"
        )
