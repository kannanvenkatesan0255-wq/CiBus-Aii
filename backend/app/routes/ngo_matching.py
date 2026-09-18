"""
CIBUS-AI - NGO Matching & Redistribution Routes
File: backend/app/routes/ngo_matching.py

Purpose:
Exposes REST endpoint for matching predicted food surplus with recipient organizations.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas import NGOMatchRequest, NGOMatchResponse
from app.services.ngo_matching_service import NGOMatchingService

router = APIRouter(prefix="/api", tags=["Redistribution Logistics"])


@router.post(
    "/match-ngos",
    response_model=NGOMatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Match NGOs & Allocate Surplus Food",
    description=(
        "Rule-based matching endpoint that receives a predicted surplus meal count, "
        "ranks synthetic partner NGOs based on availability, capacity fit, dietary compatibility, "
        "and proximity, and allocates meal portions without exceeding individual NGO capacity."
    )
)
async def match_ngos_and_allocate(payload: NGOMatchRequest) -> NGOMatchResponse:
    """
    Evaluates candidate recipient NGOs and allocates surplus food portions.
    """
    try:
        allocation_result = NGOMatchingService.match_and_allocate(
            predicted_surplus_meals=payload.predicted_surplus_meals,
            food_type=payload.food_type,
            source_latitude=payload.source_latitude,
            source_longitude=payload.source_longitude,
            max_matches=payload.max_matches or 5
        )
        return NGOMatchResponse(**allocation_result)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except FileNotFoundError as fnf_err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(fnf_err)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Redistribution allocation failed: {str(exc)}"
        )
