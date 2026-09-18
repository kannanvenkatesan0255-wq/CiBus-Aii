"""
CIBUS-AI - Route Optimization & Pickup Planning Test Suite
File: backend/tests/test_route_optimization.py

Purpose:
Automated test suite validating the deterministic Haversine distance calculations,
greedy Nearest-Neighbor graph routing heuristic, capacity and distance conservation
invariants, schema validation boundaries, and error handling.
"""

import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
AI_ENGINE_DIR = PROJECT_ROOT / "ai-engine"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(AI_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(AI_ENGINE_DIR))

from app.main import app
from app.services.route_optimization_service import (
    calculate_haversine_distance,
    build_distance_matrix,
    RouteOptimizationService
)


class TestRouteOptimization(unittest.TestCase):
    """
    Test suite for Route Optimization service and API endpoint.
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.sample_source = {
            "name": "Central Catering Hub - Guindy",
            "latitude": 13.0067,
            "longitude": 80.2026
        }

    def test_01_single_ngo_route(self):
        """
        TEST 1: Single NGO. Route must sequence Source -> NGO.
        """
        payload = {
            "source": self.sample_source,
            "ngos": [
                {
                    "ngo_id": "NGO_001",
                    "name": "Annai Teresa Relief",
                    "latitude": 13.0100,
                    "longitude": 80.2100,
                    "allocated_meals": 150.0
                }
            ]
        }

        response = self.client.post("/api/optimize-route", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["route"]), 2)
        self.assertEqual(data["route"][0]["type"], "source")
        self.assertEqual(data["route"][0]["sequence"], 0)
        self.assertEqual(data["route"][1]["type"], "ngo")
        self.assertEqual(data["route"][1]["ngo_id"], "NGO_001")
        self.assertEqual(data["route"][1]["sequence"], 1)
        self.assertEqual(data["summary"]["number_of_stops"], 1)
        self.assertEqual(data["summary"]["total_allocated_meals"], 150.0)

    def test_02_multiple_ngos_all_visited_once(self):
        """
        TEST 2: Multiple NGOs. All NGOs must appear exactly once in the route.
        """
        ngos = [
            {"ngo_id": "NGO_A", "name": "Shelter A", "latitude": 13.01, "longitude": 80.21, "allocated_meals": 50.0},
            {"ngo_id": "NGO_B", "name": "Shelter B", "latitude": 13.05, "longitude": 80.25, "allocated_meals": 75.0},
            {"ngo_id": "NGO_C", "name": "Shelter C", "latitude": 12.98, "longitude": 80.18, "allocated_meals": 100.0},
            {"ngo_id": "NGO_D", "name": "Shelter D", "latitude": 13.08, "longitude": 80.27, "allocated_meals": 60.0},
        ]
        payload = {"source": self.sample_source, "ngos": ngos}

        response = self.client.post("/api/optimize-route", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        route_ngos = [stop["ngo_id"] for stop in data["route"] if stop["type"] == "ngo"]
        self.assertEqual(len(route_ngos), 4)
        self.assertEqual(set(route_ngos), {"NGO_A", "NGO_B", "NGO_C", "NGO_D"})
        self.assertEqual(data["summary"]["number_of_stops"], 4)

    def test_03_nearest_neighbor_ordering_controlled(self):
        """
        TEST 3: Nearest-neighbor ordering verification on a 1D-like coordinate path.
        Source is at lat 13.00.
        NGO_1 is at lat 13.01 (closest to source).
        NGO_2 is at lat 13.03 (closest to NGO_1).
        NGO_3 is at lat 13.06 (furthest from source, closest to NGO_2).
        Expected traversal order: Source -> NGO_1 -> NGO_2 -> NGO_3.
        """
        source = {"name": "Origin", "latitude": 13.00, "longitude": 80.20}
        ngos = [
            {"ngo_id": "NGO_3", "name": "Far", "latitude": 13.06, "longitude": 80.20, "allocated_meals": 30.0},
            {"ngo_id": "NGO_1", "name": "Near", "latitude": 13.01, "longitude": 80.20, "allocated_meals": 10.0},
            {"ngo_id": "NGO_2", "name": "Mid", "latitude": 13.03, "longitude": 80.20, "allocated_meals": 20.0},
        ]
        payload = {"source": source, "ngos": ngos}

        response = self.client.post("/api/optimize-route", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        visited_ids = [stop["ngo_id"] for stop in data["route"] if stop["type"] == "ngo"]
        self.assertEqual(visited_ids, ["NGO_1", "NGO_2", "NGO_3"])

    def test_04_haversine_distance_accuracy(self):
        """
        TEST 4: Haversine distance reasonableness check.
        Known baseline: Chennai Central (13.0827, 80.2707) to Guindy (13.0067, 80.2026) is approx 11-12 km straight line.
        """
        dist = calculate_haversine_distance(13.0827, 80.2707, 13.0067, 80.2026)
        self.assertGreater(dist, 10.0)
        self.assertLess(dist, 13.0)

        # Identical point distance must be 0.0
        dist_zero = calculate_haversine_distance(13.0067, 80.2026, 13.0067, 80.2026)
        self.assertEqual(dist_zero, 0.0)

    def test_05_total_distance_sum_invariance(self):
        """
        TEST 5: Total route distance must equal the exact sum of route segment distances.
        """
        ngos = [
            {"ngo_id": "N1", "name": "Center 1", "latitude": 12.99, "longitude": 80.21, "allocated_meals": 40.0},
            {"ngo_id": "N2", "name": "Center 2", "latitude": 13.02, "longitude": 80.23, "allocated_meals": 60.0},
            {"ngo_id": "N3", "name": "Center 3", "latitude": 13.05, "longitude": 80.24, "allocated_meals": 80.0},
        ]
        payload = {"source": self.sample_source, "ngos": ngos}

        response = self.client.post("/api/optimize-route", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        segment_sum = sum(stop["distance_from_previous_km"] for stop in data["route"])
        total_reported = data["summary"]["total_distance_km"]
        self.assertAlmostEqual(segment_sum, total_reported, places=2)

    def test_06_total_allocation_sum_invariance(self):
        """
        TEST 6: Total allocated meals must equal the exact sum of individual NGO allocations.
        """
        ngos = [
            {"ngo_id": "N1", "name": "Center 1", "latitude": 12.99, "longitude": 80.21, "allocated_meals": 45.5},
            {"ngo_id": "N2", "name": "Center 2", "latitude": 13.02, "longitude": 80.23, "allocated_meals": 62.25},
            {"ngo_id": "N3", "name": "Center 3", "latitude": 13.05, "longitude": 80.24, "allocated_meals": 122.25},
        ]
        payload = {"source": self.sample_source, "ngos": ngos}

        response = self.client.post("/api/optimize-route", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        meal_sum = sum(stop["allocated_meals"] for stop in data["route"] if stop["type"] == "ngo")
        self.assertAlmostEqual(meal_sum, 230.0, places=2)
        self.assertAlmostEqual(data["summary"]["total_allocated_meals"], 230.0, places=2)

    def test_07_empty_ngo_list_rejection(self):
        """
        TEST 7: Empty NGO list must be rejected with 422 Unprocessable Entity.
        """
        payload = {
            "source": self.sample_source,
            "ngos": []
        }
        response = self.client.post("/api/optimize-route", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_08_invalid_coordinates_rejection(self):
        """
        TEST 8: Invalid latitude/longitude (out of bounds) must be rejected with 422.
        """
        payload_invalid_lat = {
            "source": {"name": "Invalid", "latitude": 95.0, "longitude": 80.0},
            "ngos": [{"ngo_id": "N1", "name": "N1", "latitude": 13.0, "longitude": 80.0, "allocated_meals": 10.0}]
        }
        response = self.client.post("/api/optimize-route", json=payload_invalid_lat)
        self.assertEqual(response.status_code, 422)

        payload_invalid_ngo_lon = {
            "source": self.sample_source,
            "ngos": [{"ngo_id": "N1", "name": "N1", "latitude": 13.0, "longitude": 210.0, "allocated_meals": 10.0}]
        }
        response = self.client.post("/api/optimize-route", json=payload_invalid_ngo_lon)
        self.assertEqual(response.status_code, 422)

    def test_09_negative_allocation_rejection(self):
        """
        TEST 9: Negative allocated meal count must be rejected with 422.
        """
        payload = {
            "source": self.sample_source,
            "ngos": [
                {"ngo_id": "N1", "name": "N1", "latitude": 13.0, "longitude": 80.0, "allocated_meals": -50.0}
            ]
        }
        response = self.client.post("/api/optimize-route", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_10_duplicate_ngo_ids_rejection(self):
        """
        TEST 10: Duplicate NGO IDs must be caught and rejected with 422.
        """
        payload = {
            "source": self.sample_source,
            "ngos": [
                {"ngo_id": "DUP_01", "name": "Center A", "latitude": 13.01, "longitude": 80.21, "allocated_meals": 20.0},
                {"ngo_id": "DUP_01", "name": "Center B", "latitude": 13.03, "longitude": 80.23, "allocated_meals": 30.0},
            ]
        }
        response = self.client.post("/api/optimize-route", json=payload)
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertTrue("duplicate" in str(data).lower())


if __name__ == "__main__":
    unittest.main()
