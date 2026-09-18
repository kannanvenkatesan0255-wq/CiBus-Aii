"""
CIBUS-AI - Pydantic Request & Response Schemas
File: backend/app/schemas.py

Purpose:
Defines strict type checking, validation rules, bounded constraints, and JSON schemas
for all API endpoints. Enforces domain constraints matching the CIBUS-AI ML dataset and
strictly prohibits post-service data leakage (e.g. Meals_Sold).
"""

import math
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator


VALID_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
VALID_WEATHERS = ["Sunny", "Cloudy", "Rainy", "Stormy"]
VALID_FESTIVALS = ["No", "Diwali", "Eid", "Christmas", "New Year"]
VALID_EVENT_TYPES = ["Regular", "Buffet", "Corporate", "Banquet"]


def validate_finite_number(v: float, field_name: str) -> float:
    """Helper to reject NaN and Infinity."""
    if math.isnan(v) or math.isinf(v):
        raise ValueError(f"Field '{field_name}' must be a finite numerical value.")
    return v


class PredictionRequest(BaseModel):
    """
    Input schema for real-time surplus meal prediction.
    Accepts operational and environmental features known *before* meal service.
    """
    Day: str = Field(
        ...,
        max_length=20,
        description="Day of the week (e.g. 'Monday', 'Friday', 'Saturday')",
        examples=["Saturday"]
    )
    Weather: str = Field(
        ...,
        max_length=20,
        description="Forecasted weather condition (Sunny, Cloudy, Rainy, Stormy)",
        examples=["Sunny"]
    )
    Customers_Forecast: int = Field(
        ...,
        ge=0,
        le=50000,
        description="Expected customer footfall count (0 to 50,000)",
        examples=[350]
    )
    Meals_Prepared: int = Field(
        ...,
        ge=0,
        le=100000,
        description="Total meal portions prepared by kitchen (0 to 100,000)",
        examples=[400]
    )
    Festival: Optional[str] = Field(
        default="No",
        max_length=30,
        description="Active holiday/festival (No, Diwali, Eid, Christmas, New Year)",
        examples=["No"]
    )
    Event_Type: Optional[str] = Field(
        default="Regular",
        max_length=30,
        description="Dining or catering service format (Regular, Buffet, Corporate, Banquet)",
        examples=["Regular"]
    )
    Staff_Count: int = Field(
        ...,
        ge=1,
        le=1000,
        description="Active kitchen and service staff on duty (1 to 1,000)",
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

    @field_validator("Avg_Rating")
    @classmethod
    def validate_rating(cls, v: float) -> float:
        return validate_finite_number(v, "Avg_Rating")

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
    System health and artifact availability status without leaking internal filesystem paths.
    """
    status: str
    model_loaded: bool
    preprocessor_loaded: bool
    version: str


class NGOMatchRequest(BaseModel):
    """
    Input schema for matching surplus food with recipient organizations.
    """
    predicted_surplus_meals: float = Field(
        ...,
        ge=0.0,
        le=100000.0,
        description="Predicted quantity of excess meals to redistribute",
        examples=[230.4]
    )
    food_type: Optional[str] = Field(
        default="Both",
        max_length=30,
        description="Dietary classification of prepared food (Both, Vegetarian, Non-Vegetarian)",
        examples=["Both"]
    )
    source_latitude: Optional[float] = Field(
        default=None,
        ge=-90.0,
        le=90.0,
        description="Latitude of food-generating establishment (-90.0 to 90.0)",
        examples=[12.9716]
    )
    source_longitude: Optional[float] = Field(
        default=None,
        ge=-180.0,
        le=180.0,
        description="Longitude of food-generating establishment (-180.0 to 180.0)",
        examples=[80.2000]
    )
    max_matches: Optional[int] = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of candidate recipient NGOs to allocate (1 to 20)",
        examples=[5]
    )

    @field_validator("predicted_surplus_meals")
    @classmethod
    def validate_surplus(cls, v: float) -> float:
        return validate_finite_number(v, "predicted_surplus_meals")

    @field_validator("food_type")
    @classmethod
    def validate_food_type(cls, v: Optional[str]) -> str:
        if not v:
            return "Both"
        cleaned = str(v).strip().capitalize()
        if cleaned in ["Veg", "Vegetarian"]:
            return "Vegetarian"
        if cleaned in ["Non-veg", "Non-vegetarian", "Nonveg"]:
            return "Non-Vegetarian"
        return "Both"


class NGOMatchItem(BaseModel):
    """
    Individual matched NGO recipient details and capacity allocation.
    """
    ngo_id: str
    ngo_name: str
    area: str
    capacity_meals: int
    allocated_meals: float
    people_served: int
    food_type: str
    availability_status: str
    distance_km: Optional[float]
    match_score: float
    reason: str


class NGOMatchResponse(BaseModel):
    """
    Response schema detailing allocated recipient organizations and remaining balance.
    """
    predicted_surplus_meals: float
    total_allocated_meals: float
    unallocated_meals: float
    matched_count: int
    matches: List[NGOMatchItem]
    status: str
    message: str


# =====================================================================
# Route Optimization & Pickup Planning Schemas
# =====================================================================

class RouteSource(BaseModel):
    """
    Geographic origin representing the food donor (caterer, hostel, restaurant).
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the food preparation facility or dispatch point",
        examples=["Central Dining Hall"]
    )
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Latitude of origin point (-90.0 to 90.0)",
        examples=[13.0067]
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitude of origin point (-180.0 to 180.0)",
        examples=[80.2026]
    )

    @field_validator("latitude")
    @classmethod
    def validate_lat(cls, v: float) -> float:
        return validate_finite_number(v, "latitude")

    @field_validator("longitude")
    @classmethod
    def validate_lon(cls, v: float) -> float:
        return validate_finite_number(v, "longitude")


class RouteNGOItem(BaseModel):
    """
    Individual recipient stop candidate with allocated surplus portions.
    """
    ngo_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique identifier of recipient organization",
        examples=["NGO_001"]
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of recipient organization",
        examples=["Annai Teresa Food Relief Foundation"]
    )
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Latitude of recipient center (-90.0 to 90.0)",
        examples=[13.0067]
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitude of recipient center (-180.0 to 180.0)",
        examples=[80.2026]
    )
    allocated_meals: float = Field(
        ...,
        ge=0.0,
        le=50000.0,
        description="Allocated meal quantity for this stop (>= 0.0)",
        examples=[150.0]
    )

    @field_validator("latitude")
    @classmethod
    def validate_lat(cls, v: float) -> float:
        return validate_finite_number(v, "latitude")

    @field_validator("longitude")
    @classmethod
    def validate_lon(cls, v: float) -> float:
        return validate_finite_number(v, "longitude")

    @field_validator("allocated_meals")
    @classmethod
    def validate_meals(cls, v: float) -> float:
        return validate_finite_number(v, "allocated_meals")


class RouteOptimizeRequest(BaseModel):
    """
    Input schema requesting heuristic route optimization from source to recipient NGOs.
    """
    source: RouteSource = Field(
        ...,
        description="Food generation facility origin"
    )
    ngos: List[RouteNGOItem] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of matched recipient NGOs to visit (1 to 50 stops)",
        examples=[[
            {"ngo_id": "NGO_001", "name": "Annai Teresa", "latitude": 13.0067, "longitude": 80.2026, "allocated_meals": 100.0}
        ]]
    )

    @field_validator("ngos")
    @classmethod
    def validate_unique_ngos(cls, ngos: List[RouteNGOItem]) -> List[RouteNGOItem]:
        if not ngos:
            raise ValueError("At least one recipient NGO stop must be provided for route planning.")
        
        seen_ids = set()
        for ngo in ngos:
            if ngo.ngo_id in seen_ids:
                raise ValueError(f"Duplicate NGO identifier '{ngo.ngo_id}' detected. Each stop must have a unique NGO_ID.")
            seen_ids.add(ngo.ngo_id)
        return ngos


class RouteStop(BaseModel):
    """
    Single sequential waypoint in the optimized distribution route.
    """
    sequence: int = Field(..., description="0-indexed route stop number")
    type: str = Field(..., description="'source' for dispatch origin or 'ngo' for recipient center")
    ngo_id: Optional[str] = Field(default=None, description="NGO identifier if type is 'ngo'")
    name: str = Field(..., description="Location or organization name")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    allocated_meals: float = Field(..., description="Meal portions delivered at this stop")
    distance_from_previous_km: float = Field(..., description="Haversine distance from previous waypoint in km")


class RouteSummary(BaseModel):
    """
    Aggregate metrics summarizing the planned distribution itinerary.
    """
    number_of_stops: int = Field(..., description="Total count of recipient NGO drop-offs")
    total_distance_km: float = Field(..., description="Total route transit distance in km (Haversine straight-line sum)")
    total_allocated_meals: float = Field(..., description="Total sum of surplus meal portions distributed")
    start_location: str = Field(..., description="Name of origin facility")


class RouteOptimizeResponse(BaseModel):
    """
    Output payload containing the sequenced route plan, distance breakdown, and summary.
    """
    source: RouteSource
    route: List[RouteStop]
    summary: RouteSummary
    distance_matrix: Optional[List[List[float]]] = None
    location_names: Optional[List[str]] = None
    status: str = "success"
    message: str = "Route optimized successfully using nearest-neighbor heuristic."
    disclaimer: str = (
        "Demo Route Planner: Route distance is estimated using straight-line geographic coordinates "
        "(Haversine formula) and a greedy nearest-neighbor heuristic. Does not use live traffic or road networks."
    )


# =====================================================================
# Impact Dashboard & Analytics Schemas
# =====================================================================

class ActivityRecordCreate(BaseModel):
    """
    Input schema to record a completed prediction, NGO matching, and route planning activity.
    """
    source_name: str = Field(
        default="Central Dining Facility",
        max_length=100,
        description="Name of the food preparation establishment"
    )
    predicted_surplus_meals: float = Field(
        ...,
        ge=0.0,
        le=100000.0,
        description="Forecasted excess meals from ML model (non-negative)"
    )
    allocated_meals: float = Field(
        ...,
        ge=0.0,
        le=100000.0,
        description="Total meals allocated across matched NGOs (non-negative)"
    )
    matched_ngo_count: int = Field(
        ...,
        ge=0,
        le=1000,
        description="Count of partner recipient NGOs matched"
    )
    route_stop_count: int = Field(
        ...,
        ge=0,
        le=1000,
        description="Count of distribution stops in planned route"
    )
    route_distance_km: float = Field(
        ...,
        ge=0.0,
        le=50000.0,
        description="Total estimated route distance in km"
    )
    status: Optional[str] = Field(
        default="planned",
        max_length=30,
        description="Activity status ('planned', 'completed', 'cancelled')"
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional contextual remarks or event notes"
    )

    @field_validator("predicted_surplus_meals", "allocated_meals", "route_distance_km")
    @classmethod
    def validate_finite_numbers(cls, v: float, info) -> float:
        return validate_finite_number(v, info.field_name)

    @model_validator(mode="after")
    def validate_allocation_bounds(self) -> "ActivityRecordCreate":
        if self.allocated_meals > self.predicted_surplus_meals + 0.01:
            raise ValueError(
                f"Data Consistency Error: Allocated meals ({self.allocated_meals}) "
                f"cannot exceed predicted surplus ({self.predicted_surplus_meals})."
            )
        return self


class ActivityRecord(ActivityRecordCreate):
    """
    Stored activity item with assigned identifier and ISO timestamp.
    """
    activity_id: str
    timestamp: str


class ModelPerformanceMetrics(BaseModel):
    """
    Factual performance metrics of the trained ML model loaded from evaluation artifacts.
    """
    model_name: str
    mae: float = Field(..., description="Mean Absolute Error in meals (average magnitude of errors)")
    rmse: float = Field(..., description="Root Mean Squared Error in meals (penalizes large deviations)")
    r2: float = Field(..., description="Proportion of variance explained by regression model relative to mean baseline")
    evaluation_dataset: str = "Held-out unseen test set (N=1,600 records)"
    note: str = "R² represents the proportion of explained variance and is not a classification accuracy percentage."


class DashboardSummary(BaseModel):
    """
    Aggregated operational impact statistics derived from recorded workflows.
    """
    total_predicted_surplus_meals: float
    total_allocated_meals: float
    allocation_rate_pct: float
    total_matched_ngos: int
    total_route_stops: int
    total_route_distance_km: float
    total_activities: int
    data_source_mode: str = "Local demonstration activity store (JSON)"


class DashboardResponse(BaseModel):
    """
    Consolidated response payload for the Impact Dashboard.
    """
    summary: DashboardSummary
    model_performance: ModelPerformanceMetrics
    status: str = "success"
    message: str = "Dashboard operational metrics and ML model performance retrieved successfully."
    disclaimer: str = (
        "Demonstration Dashboard: Metrics summarize planned redistribution workflows and estimated "
        "Haversine transit distances. Confirmed real-world physical delivery requires on-ground verification."
    )
