"""
CIBUS-AI - NGO Matching & Redistribution API Test Suite
File: backend/tests/test_ngo_matching.py

Purpose:
Validates the rule-based NGO matching and capacity allocation endpoint:
1. Valid redistribution matching.
2. Zero surplus handling.
3. Multi-NGO capacity distribution.
4. Total allocated meals <= Predicted surplus meals constraint.
5. NGO capacity bounds constraint.
6. Dietary food-type filtering.
7. Exclusion of unavailable recipient organizations.
8. Validation error handling for negative values and invalid coordinates.
9. Haversine distance computation.
"""

import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

TEST_DIR = Path(__file__).resolve().parent
BACKEND_DIR = TEST_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
AI_ENGINE_DIR = PROJECT_ROOT / "ai-engine"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(AI_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(AI_ENGINE_DIR))

from app.main import app


class TestNGOMatchingAPI(unittest.TestCase):
    """
    Test suite for POST /api/match-ngos endpoint.
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_valid_matching_standard(self):
        """Test 1: Standard matching with surplus and donor coordinates."""
        payload = {
            "predicted_surplus_meals": 230.4,
            "food_type": "Both",
            "source_latitude": 12.9716,
            "source_longitude": 80.2000,
            "max_matches": 3
        }
        response = self.client.post("/api/match-ngos", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["predicted_surplus_meals"], 230.4)
        self.assertGreater(len(data["matches"]), 0)
        self.assertLessEqual(len(data["matches"]), 3)
        self.assertEqual(data["total_allocated_meals"] + data["unallocated_meals"], 230.4)

    def test_02_zero_surplus(self):
        """Test 2: Zero surplus returns zero allocations gracefully."""
        payload = {
            "predicted_surplus_meals": 0.0,
            "food_type": "Both"
        }
        response = self.client.post("/api/match-ngos", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_allocated_meals"], 0.0)
        self.assertEqual(len(data["matches"]), 0)

    def test_03_capacity_constraints(self):
        """Test 3: Verify allocated meals never exceed each individual NGO's capacity."""
        payload = {
            "predicted_surplus_meals": 600.0,
            "food_type": "Both",
            "max_matches": 5
        }
        response = self.client.post("/api/match-ngos", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for match in data["matches"]:
            self.assertLessEqual(
                match["allocated_meals"],
                match["capacity_meals"],
                f"Allocated meals ({match['allocated_meals']}) exceeded capacity ({match['capacity_meals']})"
            )

    def test_04_total_allocation_bound(self):
        """Test 4: Verify total allocated meals never exceed predicted surplus."""
        surplus = 175.5
        payload = {
            "predicted_surplus_meals": surplus,
            "food_type": "Both"
        }
        response = self.client.post("/api/match-ngos", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertLessEqual(data["total_allocated_meals"], surplus)
        self.assertGreaterEqual(data["unallocated_meals"], 0.0)

    def test_05_vegetarian_filtering(self):
        """Test 5: Verify Vegetarian food matches only with Vegetarian or Both organizations."""
        payload = {
            "predicted_surplus_meals": 150.0,
            "food_type": "Vegetarian",
            "max_matches": 5
        }
        response = self.client.post("/api/match-ngos", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for match in data["matches"]:
            self.assertIn(match["food_type"], ["Vegetarian", "Both"])

    def test_06_unavailable_ngo_exclusion(self):
        """Test 6: Unavailable NGOs (e.g. NGO012) must never be matched or allocated."""
        payload = {
            "predicted_surplus_meals": 1000.0,
            "food_type": "Both",
            "max_matches": 20
        }
        response = self.client.post("/api/match-ngos", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        matched_ids = [m["ngo_id"] for m in data["matches"]]
        self.assertNotIn("NGO012", matched_ids, "NGO012 is Unavailable and must not be allocated")

    def test_07_invalid_negative_surplus(self):
        """Test 7: Negative surplus value triggers HTTP 422 validation error."""
        payload = {
            "predicted_surplus_meals": -50.0
        }
        response = self.client.post("/api/match-ngos", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_08_invalid_coordinates(self):
        """Test 8: Latitude exceeding 90.0 triggers HTTP 422 validation error."""
        payload = {
            "predicted_surplus_meals": 100.0,
            "source_latitude": 95.0  # Invalid latitude
        }
        response = self.client.post("/api/match-ngos", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_09_haversine_distance_computation(self):
        """Test 9: Distance is populated and non-negative when coordinates are supplied."""
        payload = {
            "predicted_surplus_meals": 100.0,
            "source_latitude": 13.0000,
            "source_longitude": 80.2000
        }
        response = self.client.post("/api/match-ngos", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for match in data["matches"]:
            self.assertIsNotNone(match["distance_km"])
            self.assertGreaterEqual(match["distance_km"], 0.0)

    def test_10_missing_coordinates_handling(self):
        """Test 10: Distance is null/None when coordinates are omitted, without crashing."""
        payload = {
            "predicted_surplus_meals": 100.0
            # Coordinates omitted
        }
        response = self.client.post("/api/match-ngos", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for match in data["matches"]:
            self.assertIsNone(match["distance_km"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
