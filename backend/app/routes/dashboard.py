"""
CIBUS-AI - Impact Dashboard & Analytics API Router
File: backend/app/routes/dashboard.py

Purpose:
Exposes REST endpoints for the operational impact dashboard:
- GET /api/dashboard/summary  -> Aggregate operational stats + ML model evaluation performance
- GET /api/dashboard/recent   -> List recent planned redistribution activities
- POST /api/dashboard/activity -> Record completed/planned redistribution workflow activity
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas import (
    DashboardResponse,
    ActivityRecord,
    ActivityRecordCreate
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Impact Dashboard & Analytics"]
)


@router.get(
    "/summary",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Impact Dashboard Summary",
    description=(
        "Returns aggregated operational redistribution statistics (predicted surplus, planned allocation, "
        "matched NGOs, route distance) and active ML regression performance metrics (MAE, RMSE, R²)."
    )
)
async def get_dashboard_summary() -> DashboardResponse:
    """
    Retrieves operational totals and ML model evaluation metrics.
    """
    try:
        data = AnalyticsService.get_dashboard_summary()
        return DashboardResponse(**data)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compile dashboard summary: {str(exc)}"
        )


@router.get(
    "/recent",
    response_model=List[ActivityRecord],
    status_code=status.HTTP_200_OK,
    summary="Get Recent Activity Log",
    description="Retrieves the most recent planned redistribution activity logs ordered descending by timestamp."
)
async def get_recent_activities(
    limit: int = Query(default=10, ge=1, le=100, description="Maximum number of recent activities to return")
) -> List[ActivityRecord]:
    """
    Retrieves recent logged workflow records.
    """
    try:
        activities = AnalyticsService.get_recent_activities(limit=limit)
        return [ActivityRecord(**act) for act in activities]
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recent activities: {str(exc)}"
        )


@router.post(
    "/activity",
    response_model=ActivityRecord,
    status_code=status.HTTP_201_CREATED,
    summary="Record Redistribution Activity",
    description="Persists a completed surplus prediction, NGO matching, and route planning workflow."
)
async def record_activity(activity: ActivityRecordCreate) -> ActivityRecord:
    """
    Records a new planned redistribution workflow entry.
    """
    try:
        record_dict = activity.model_dump()
        saved = AnalyticsService.save_activity_record(record_dict)
        return ActivityRecord(**saved)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record activity: {str(exc)}"
        )
