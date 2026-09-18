"""
CIBUS-AI - Pydantic Request & Response Schemas
File: backend/app/schemas.py

Purpose:
Defines strict type checking, validation rules, and JSON schemas for API endpoints.
Enforces domain constraints matching the CIBUS-AI ML dataset and strictly prohibits
post-service data leakage (e.g. Meals_Sold).
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator


VALID_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
VALID_WEATHERS = ["Sunny", "Cloudy", "Rainy", "Stormy"]
VALID_FESTIVALS = ["No", "Diwali", "Eid", "Christmas", "New Year"]
VALID_EVENT_TYPES = ["Regular", "Buffet", "Corporate", "Banquet"]


class PredictionRequest(BaseModel):
    """
    Input schema for real-time surplus meal prediction.
    Accepts operational and environmental features known *before* meal service.
    """
    Day: str = Field(
        ...,
        description="Day of the week (e.g. 'Monday', 'Friday', 'Saturday')",
        examples=["Saturday"]
    )
    Weather: str = Field(
        ...,
        description="Forecasted weather condition (Sunny, Cloudy, Rainy, Stormy)",
        examples=["Sunny"]
    )
    Customers_Forecast: int = Field(
        ...,
        ge=0,
        description="Expected customer footfall count (non-negative integer)",
        examples=[350]
    )
    Meals_Prepared: int = Field(
        ...,
        ge=0,
        description="Total meal portions prepared by kitchen (non-negative integer)",
        examples=[400]
    )
    Festival: Optional[str] = Field(
        default="No",
        description="Active holiday/festival (No, Diwali, Eid, Christmas, New Year)",
        examples=["No"]
    )
    Event_Type: Optional[str] = Field(
        default="Regular",
        description="Dining or catering service format (Regular, Buffet, Corporate, Banquet)",
        examples=["Regular"]
    )
    Staff_Count: int = Field(
        ...,
        ge=1,
        description="Active kitchen and service staff on duty (minimum 1)",
        examples=[12]
    )
    Avg_Rating: float = Field(
        ...,
        ge=1.0,
        le=5.0,
        description="Historical customer satisfaction score (1.0 to 5.0)",
        examples=[4.3]
    )
    Special_Event: Union[int, str, bool] = Field(
        default=0,
        description="Special private event or booking flag (0/1, True/False, Yes/No)",
        examples=[0]
    )

    @model_validator(mode="before")
    @classmethod
    def check_forbidden_fields(cls, data: Any) -> Any:
        """
        Enforces strict Data Leakage prevention by rejecting 'Meals_Sold'.
        """
        if isinstance(data, dict):
            for key in data.keys():
                if key.lower() in ["meals_sold", "mealssold", "meals_sold_count"]:
                    raise ValueError(
                        "DATA LEAKAGE REJECTION: 'Meals_Sold' is a post-service outcome "
                        "and cannot be accepted as a pre-service prediction input."
                    )
        return data

    @field_validator("Day")
    @classmethod
    def validate_day(cls, v: str) -> str:
        cleaned = str(v).strip().capitalize()
        if cleaned not in VALID_DAYS:
            raise ValueError(f"Invalid Day '{v}'. Must be one of: {VALID_DAYS}")
        return cleaned

    @field_validator("Weather")
    @classmethod
    def validate_weather(cls, v: str) -> str:
        cleaned = str(v).strip().capitalize()
        if cleaned not in VALID_WEATHERS:
            raise ValueError(f"Invalid Weather '{v}'. Must be one of: {VALID_WEATHERS}")
        return cleaned

    @field_validator("Festival")
    @classmethod
    def validate_festival(cls, v: Optional[str]) -> str:
        if v is None or str(v).strip().lower() in ["none", "", "null", "no"]:
            return "No"
        cleaned = str(v).strip()
        matched = [f for f in VALID_FESTIVALS if f.lower() == cleaned.lower()]
        if matched:
            return matched[0]
        return cleaned

    @field_validator("Event_Type")
    @classmethod
    def validate_event_type(cls, v: Optional[str]) -> str:
        if v is None or str(v).strip().lower() in ["none", "", "null"]:
            return "Regular"
        cleaned = str(v).strip().capitalize()
        if cleaned not in VALID_EVENT_TYPES:
            raise ValueError(f"Invalid Event_Type '{v}'. Must be one of: {VALID_EVENT_TYPES}")
        return cleaned

    @field_validator("Special_Event")
    @classmethod
    def normalize_special_event(cls, v: Any) -> int:
        if isinstance(v, str):
            return 1 if v.strip().lower() in ["yes", "y", "1", "true"] else 0
        if isinstance(v, bool):
            return 1 if v else 0
        return 1 if int(v) == 1 else 0


class PredictionResponse(BaseModel):
    """
    Standard output schema for food surplus forecasts.
    """
    predicted_surplus_meals: float = Field(
        ...,
        ge=0.0,
        description="Predicted quantity of excess meals (non-negative float)",
        examples=[45.2]
    )
    model_name: str = Field(
        default="RandomForestRegressor (Tuned, max_depth=15, n_estimators=200)",
        description="Name and configuration of the trained model generating prediction"
    )
    status: str = Field(
        default="success",
        description="Execution status indicator"
    )
    input_summary: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Summary of validated operational input parameters"
    )
    recommended_action: Optional[str] = Field(
        default=None,
        description="Operational guidance for kitchen and redistribution logistics"
    )


class ModelInfoResponse(BaseModel):
    """
    Factual metadata describing the deployed ML model and feature requirements.
    """
    model_name: str
    model_type: str
    target_variable: str
    feature_count: int
    features: List[str]
    evaluation_metrics: Dict[str, Any]
    status: str


class HealthResponse(BaseModel):
    """
    System health and artifact availability status.
    """
    status: str
    model_loaded: bool
    preprocessor_loaded: bool
    version: str
