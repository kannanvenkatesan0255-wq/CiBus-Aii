"""
CIBUS-AI - NGO Matching & Food Redistribution Service
File: backend/app/services/ngo_matching_service.py

Purpose:
Rule-based matching and capacity allocation service connecting forecasted food surplus
to nearby partner NGOs and relief centers.

IMPORTANT ARCHITECTURAL NOTE:
This module is a deterministic, rule-based heuristics engine and is NOT a Machine Learning model.
It consumes the quantitative surplus forecast produced by the Random Forest ML engine.
"""

import math
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd

SERVICE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SERVICE_DIR.parent.parent
DATA_PATH = BACKEND_DIR / "data" / "ngos.csv"

EARTH_RADIUS_KM = 6371.0


def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes the great-circle distance between two geographic points in kilometers
    using the Haversine formula.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(EARTH_RADIUS_KM * c, 2)


class NGOMatchingService:
    """
    Provides multi-factor scoring and constraint-based food redistribution allocation.
    """

    @classmethod
    def load_ngo_dataset(cls) -> pd.DataFrame:
        """Loads and returns the synthetic NGO dataset."""
        if not DATA_PATH.exists():
            raise FileNotFoundError(f"NGO dataset not found at: {DATA_PATH}")
        return pd.read_csv(DATA_PATH)

    @classmethod
    def match_and_allocate(
        cls,
        predicted_surplus_meals: float,
        food_type: Optional[str] = "Both",
        source_latitude: Optional[float] = None,
        source_longitude: Optional[float] = None,
        max_matches: int = 5
    ) -> Dict[str, Any]:
        """
        Evaluates synthetic NGOs against operational surplus, ranks by multi-criteria score,
        and allocates meals without exceeding individual NGO capacity or total surplus.

        Parameters:
            predicted_surplus_meals: Quantitative forecast (>= 0.0).
            food_type: 'Vegetarian', 'Non-Vegetarian', or 'Both'.
            source_latitude: Optional donor latitude coordinate.
            source_longitude: Optional donor longitude coordinate.
            max_matches: Maximum number of recipient organizations to return.

        Returns:
            Dict with allocation breakdown, NGO match list, and unallocated balance.
        """
        if predicted_surplus_meals < 0:
            raise ValueError(f"Surplus meals must be non-negative, got {predicted_surplus_meals}")

        df = cls.load_ngo_dataset()
        surplus = float(predicted_surplus_meals)

        # Handle zero surplus edge case cleanly
        if surplus <= 0.0:
            return {
                "predicted_surplus_meals": 0.0,
                "total_allocated_meals": 0.0,
                "unallocated_meals": 0.0,
                "matched_count": 0,
                "matches": [],
                "status": "zero_surplus",
                "message": "No surplus meals forecasted. Redistribution allocation not required."
            }

        candidates = []
        has_coords = (source_latitude is not None) and (source_longitude is not None)

        for _, row in df.iterrows():
            ngo_id = str(row["NGO_ID"])
            ngo_name = str(row["NGO_Name"])
            area = str(row["Area"])
            capacity = int(row["Capacity_Meals"])
            people_served = int(row["People_Served"])
            ngo_food_type = str(row["Food_Type"])
            avail_status = str(row["Availability_Status"])
            lat = float(row["Latitude"])
            lon = float(row["Longitude"])

            # 1. Availability Filter: skip completely unavailable shelters
            if avail_status.lower() == "unavailable":
                continue

            # 2. Food Compatibility Filter
            req_type = str(food_type or "Both").strip().capitalize()
            compatible = True
            compat_score = 1.0

            if req_type in ["Non-vegetarian", "Non-veg"] and ngo_food_type == "Vegetarian":
                compatible = False
                compat_score = 0.0
            elif req_type == "Vegetarian" and ngo_food_type == "Non-Vegetarian":
                compatible = False
                compat_score = 0.0
            elif req_type == "Both" and ngo_food_type != "Both":
                compat_score = 0.8

            if not compatible:
                continue

            # 3. Distance Calculation
            distance_km = None
            dist_score = 0.5  # Neutral default when donor coordinates unavailable
            if has_coords:
                distance_km = calculate_haversine_distance(source_latitude, source_longitude, lat, lon)
                # Proximity score decay over 25 km threshold
                dist_score = max(0.0, min(1.0, 1.0 - (distance_km / 25.0)))

            # 4. Availability Score Component
            avail_score = 1.0 if avail_status.lower() == "available" else 0.5

            # 5. Capacity Fit Score Component
            cap_score = min(1.0, capacity / max(1.0, surplus))

            # 6. Composite Rule-Based Match Score (0.0 to 1.0)
            # Weights: Availability (35%), Distance (25%), Food Compat (20%), Capacity Fit (20%)
            match_score = (
                (0.35 * avail_score)
                + (0.25 * dist_score)
                + (0.20 * compat_score)
                + (0.20 * cap_score)
            )
            match_score = round(match_score, 3)

            # Build transparent reason string
            reasons = []
            if avail_status.lower() == "available":
                reasons.append("Active receiving capacity")
            if distance_km is not None and distance_km <= 8.0:
                reasons.append(f"High proximity ({distance_km} km)")
            elif distance_km is not None:
                reasons.append(f"Transit distance: {distance_km} km")
            if ngo_food_type == "Both" or ngo_food_type == req_type:
                reasons.append("Compatible dietary format")

            candidates.append({
                "ngo_id": ngo_id,
                "ngo_name": ngo_name,
                "area": area,
                "capacity_meals": capacity,
                "people_served": people_served,
                "food_type": ngo_food_type,
                "availability_status": avail_status,
                "distance_km": distance_km,
                "latitude": lat,
                "longitude": lon,
                "match_score": match_score,
                "reason": " • ".join(reasons) if reasons else "Eligible recipient center"
            })

        # Rank candidates by match score descending
        candidates.sort(key=lambda x: x["match_score"], reverse=True)

        # Capacity Distribution & Allocation
        remaining_surplus = surplus
        allocated_matches = []

        for cand in candidates[:max_matches]:
            if remaining_surplus <= 0.001:
                break

            allocated = min(remaining_surplus, float(cand["capacity_meals"]))
            allocated = round(allocated, 2)

            if allocated > 0.0:
                cand_copy = dict(cand)
                cand_copy["allocated_meals"] = allocated
                allocated_matches.append(cand_copy)
                remaining_surplus = round(remaining_surplus - allocated, 2)

        total_allocated = round(surplus - max(0.0, remaining_surplus), 2)
        unallocated = round(max(0.0, remaining_surplus), 2)

        return {
            "predicted_surplus_meals": surplus,
            "total_allocated_meals": total_allocated,
            "unallocated_meals": unallocated,
            "matched_count": len(allocated_matches),
            "matches": allocated_matches,
            "status": "success",
            "message": f"Allocated {total_allocated} of {surplus} predicted meals across {len(allocated_matches)} recipient organizations."
        }
