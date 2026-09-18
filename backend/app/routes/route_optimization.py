"""
CIBUS-AI - Route Optimization API Router
File: backend/app/routes/route_optimization.py

Purpose:
Exposes REST endpoint for surplus food dispatch sequencing and route optimization:
- POST /api/optimize-route -> Plans heuristic delivery itinerary from food source to matched NGOs.

IMPORTANT ARCHITECTURAL & ACADEMIC BOUNDARY:
- This endpoint exposes a deterministic graph heuristic (Nearest-Neighbor + Haversine).
- It is NOT an ML prediction model.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas import RouteOptimizeRequest, RouteOptimizeResponse
from app.services.route_optimization_service import RouteOptimizationService

router = APIRouter(
    prefix="/api",
    tags=["Route Optimization & Logistics"]
)


@router.post(
    "/optimize-route",
    response_model=RouteOptimizeResponse,
    status_code=status.HTTP_200_OK,
    summary="Optimize Surplus Food Delivery Route",
    description=(
        "Calculates an ordered delivery itinerary starting from the food donor facility "
        "and visiting all selected partner NGOs using Haversine distance calculations and "
        "a greedy Nearest-Neighbor graph traversal heuristic."
    )
)
async def optimize_route(request: RouteOptimizeRequest) -> RouteOptimizeResponse:
    """
    Executes route sequencing across candidate recipient organizations.
    """
    try:
        source_dict = request.source.model_dump()
        ngos_list = [ngo.model_dump() for ngo in request.ngos]

        result = RouteOptimizationService.optimize_route(
            source=source_dict,
            ngos=ngos_list
        )
        return RouteOptimizeResponse(**result)

    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Route planning encountered an internal error: {str(exc)}"
        )
