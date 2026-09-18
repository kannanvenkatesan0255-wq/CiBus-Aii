"""
CIBUS-AI - Route Optimization & Pickup Planning Service
File: backend/app/services/route_optimization_service.py

Purpose:
Provides deterministic, rule-based graph routing and delivery sequencing for surplus food
redistribution using geographic Haversine distances and a greedy Nearest-Neighbor (NN) heuristic.

IMPORTANT ARCHITECTURAL & ACADEMIC BOUNDARY:
- This module is a deterministic GRAPH ALGORITHM / HEURISTIC OPTIMIZER and is NOT a Machine Learning model.
- It consumes the upstream predicted surplus allocations and plans an ordered dispatch sequence.
- All distances are straight-line great-circle estimates via the Haversine formula (Earth radius = 6371.0 km).
- No external mapping APIs (e.g. Google Maps API, OSRM) or real-time road traffic layers are used.
"""

import math
from typing import Dict, List, Any, Optional, Tuple

EARTH_RADIUS_KM = 6371.0


def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great-circle distance between two geographic coordinates in kilometers
    using the Haversine formula.

    Formula:
        a = sin²(Δφ/2) + cos(φ1) * cos(φ2) * sin²(Δλ/2)
        c = 2 * atan2(√a, √(1-a))
        d = R * c
    where φ is latitude in radians, λ is longitude in radians, and R = 6,371.0 km.
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


def build_distance_matrix(locations: List[Dict[str, Any]]) -> List[List[float]]:
    """
    Constructs an N x N symmetric pairwise distance matrix for all waypoints (Source + NGOs).

    Parameters:
        locations: List of dicts containing 'latitude' and 'longitude' keys.

    Returns:
        2D List of floats representing distances between location[i] and location[j] in km.
    """
    n = len(locations)
    matrix = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(i, n):
            if i == j:
                matrix[i][j] = 0.0
            else:
                dist = calculate_haversine_distance(
                    locations[i]["latitude"],
                    locations[i]["longitude"],
                    locations[j]["latitude"],
                    locations[j]["longitude"]
                )
                matrix[i][j] = dist
                matrix[j][i] = dist

    return matrix


def calculate_route_summary(
    route: List[Dict[str, Any]],
    start_name: str
) -> Dict[str, Any]:
    """
    Aggregates route itinerary metrics including total distance, stops, and meals.
    """
    total_distance = sum(stop.get("distance_from_previous_km", 0.0) for stop in route)
    total_meals = sum(
        stop.get("allocated_meals", 0.0)
        for stop in route
        if stop.get("type") == "ngo"
    )
    ngo_stops = sum(1 for stop in route if stop.get("type") == "ngo")

    return {
        "number_of_stops": ngo_stops,
        "total_distance_km": round(total_distance, 2),
        "total_allocated_meals": round(total_meals, 2),
        "start_location": start_name
    }


class RouteOptimizationService:
    """
    Heuristic route planner generating deterministic delivery itineraries
    from a food-generating donor source to partner recipient organizations.
    """

    @classmethod
    def optimize_route(
        cls,
        source: Dict[str, Any],
        ngos: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Plans an efficient delivery itinerary starting at the food source and visiting
        each selected recipient NGO using the Nearest-Neighbor graph traversal heuristic.

        Algorithm:
            1. Node 0 = Food Source (Starting origin).
            2. Compute pairwise Haversine distance matrix across all (N+1) locations.
            3. Set Current Node = 0. Visited = {0}.
            4. While unvisited recipient NGOs exist:
               - Select unvisited NGO 'u' with min distance from Current Node.
               - Append 'u' to route sequence.
               - Mark 'u' visited; Current Node = 'u'.
            5. Aggregate cumulative distances, meals transported, and segment steps.

        Parameters:
            source: Dict with 'name', 'latitude', 'longitude'.
            ngos: List of dicts with 'ngo_id', 'name', 'latitude', 'longitude', 'allocated_meals'.

        Returns:
            Dict matching RouteOptimizeResponse schema with full route and summary.
        """
        if not ngos:
            raise ValueError("Route optimization requires at least one recipient NGO stop.")

        # Prepare unified locations list: [Source, NGO_0, NGO_1, ...]
        source_node = {
            "name": source.get("name", "Food Source"),
            "latitude": float(source["latitude"]),
            "longitude": float(source["longitude"]),
            "type": "source",
            "allocated_meals": 0.0,
            "ngo_id": None
        }

        ngo_nodes = []
        seen_ids = set()
        for ngo in ngos:
            nid = str(ngo["ngo_id"])
            if nid in seen_ids:
                raise ValueError(f"Duplicate NGO identifier '{nid}' detected in route request.")
            seen_ids.add(nid)

            meals = float(ngo.get("allocated_meals", 0.0))
            if meals < 0.0:
                raise ValueError(f"Allocated meals for NGO '{nid}' cannot be negative, got {meals}")

            ngo_nodes.append({
                "name": str(ngo.get("name", nid)),
                "latitude": float(ngo["latitude"]),
                "longitude": float(ngo["longitude"]),
                "type": "ngo",
                "allocated_meals": round(meals, 2),
                "ngo_id": nid
            })

        all_locations = [source_node] + ngo_nodes
        location_names = [loc["name"] for loc in all_locations]
        dist_matrix = build_distance_matrix(all_locations)

        # Nearest-Neighbor Traversal
        num_locations = len(all_locations)
        visited = {0}
        current_idx = 0
        route = []

        # Add Source at sequence 0
        route.append({
            "sequence": 0,
            "type": "source",
            "ngo_id": None,
            "name": source_node["name"],
            "latitude": source_node["latitude"],
            "longitude": source_node["longitude"],
            "allocated_meals": 0.0,
            "distance_from_previous_km": 0.0
        })

        sequence = 1
        while len(visited) < num_locations:
            nearest_idx = -1
            min_dist = float("inf")

            for candidate_idx in range(1, num_locations):
                if candidate_idx not in visited:
                    d = dist_matrix[current_idx][candidate_idx]
                    if d < min_dist:
                        min_dist = d
                        nearest_idx = candidate_idx

            if nearest_idx == -1:
                break

            visited.add(nearest_idx)
            chosen_node = all_locations[nearest_idx]
            seg_dist = round(min_dist, 2)

            route.append({
                "sequence": sequence,
                "type": "ngo",
                "ngo_id": chosen_node["ngo_id"],
                "name": chosen_node["name"],
                "latitude": chosen_node["latitude"],
                "longitude": chosen_node["longitude"],
                "allocated_meals": chosen_node["allocated_meals"],
                "distance_from_previous_km": seg_dist
            })

            current_idx = nearest_idx
            sequence += 1

        summary = calculate_route_summary(route, source_node["name"])

        return {
            "source": {
                "name": source_node["name"],
                "latitude": source_node["latitude"],
                "longitude": source_node["longitude"]
            },
            "route": route,
            "summary": summary,
            "distance_matrix": dist_matrix,
            "location_names": location_names,
            "status": "success",
            "message": f"Route planned with {summary['number_of_stops']} stops covering {summary['total_distance_km']} km.",
            "disclaimer": (
                "Demo Route Planner: Distances estimated via straight-line Haversine coordinates "
                "and a nearest-neighbor heuristic. Does not reflect real-time traffic or road topology."
            )
        }
