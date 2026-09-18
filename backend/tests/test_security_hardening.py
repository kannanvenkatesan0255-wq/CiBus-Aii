"""
CIBUS-AI - Security, Error Handling & Production Hardening Test Suite
File: backend/tests/test_security_hardening.py

Purpose:
Verifies input validation constraints, data leakage prevention, boundary conditions,
information leak protection, and centralized exception handling.
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


class TestSecurityAndHardening(unittest.TestCase):
    """
    Security and validation hardening test cases.
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    # 1. Data Leakage Prevention
    def test_rejection_of_meals_sold_leakage(self):
        payload = {
            "Day": "Saturday",
            "Weather": "Sunny",
            "Customers_Forecast": 300,
            "Meals_Prepared": 350,
            "Meals_Sold": 320,  # FORBIDDEN
            "Festival": "No",
            "Event_Type": "Regular",
            "Staff_Count": 10,
            "Avg_Rating": 4.2,
            "Special_Event": 0
        }
        res = self.client.post("/api/predict", json=payload)
        self.assertEqual(res.status_code, 422)
        self.assertIn("DATA LEAKAGE REJECTION", str(res.json()))

    # 2. Rating Bounds Validation
    def test_invalid_rating_bounds(self):
        payload = {
            "Day": "Saturday",
            "Weather": "Sunny",
            "Customers_Forecast": 300,
            "Meals_Prepared": 350,
            "Festival": "No",
            "Event_Type": "Regular",
            "Staff_Count": 10,
            "Avg_Rating": 6.5,  # Out of range (1.0 to 5.0)
            "Special_Event": 0
        }
        res = self.client.post("/api/predict", json=payload)
        self.assertEqual(res.status_code, 422)

    # 3. Negative Quantities Rejection
    def test_negative_values_rejection(self):
        payload = {
            "Day": "Saturday",
            "Weather": "Sunny",
            "Customers_Forecast": -50,  # Invalid negative
            "Meals_Prepared": 350,
            "Staff_Count": 0,  # Invalid < 1
            "Avg_Rating": 4.0,
            "Special_Event": 0
        }
        res = self.client.post("/api/predict", json=payload)
        self.assertEqual(res.status_code, 422)

    # 4. Out-of-Range Coordinates Validation
    def test_out_of_range_coordinates_route(self):
        payload = {
            "source": {
                "name": "Invalid Location",
                "latitude": 95.0,  # Lat > 90
                "longitude": 80.0
            },
            "ngos": [
                {
                    "ngo_id": "NGO_001",
                    "name": "Relief NGO",
                    "latitude": 13.0,
                    "longitude": 190.0,  # Lon > 180
                    "allocated_meals": 50.0
                }
            ]
        }
        res = self.client.post("/api/optimize-route", json=payload)
        self.assertEqual(res.status_code, 422)

    # 5. Duplicate NGO IDs Rejection
    def test_duplicate_ngo_ids_in_route(self):
        payload = {
            "source": {
                "name": "Origin Hub",
                "latitude": 13.00,
                "longitude": 80.20
            },
            "ngos": [
                {
                    "ngo_id": "NGO_DUP",
                    "name": "Shelter A",
                    "latitude": 13.01,
                    "longitude": 80.21,
                    "allocated_meals": 30.0
                },
                {
                    "ngo_id": "NGO_DUP",  # Duplicate ID
                    "name": "Shelter B",
                    "latitude": 13.02,
                    "longitude": 80.22,
                    "allocated_meals": 40.0
                }
            ]
        }
        res = self.client.post("/api/optimize-route", json=payload)
        self.assertEqual(res.status_code, 422)
        self.assertIn("Duplicate NGO identifier", str(res.json()))

    # 6. Allocation Exceeding Predicted Surplus
    def test_activity_allocation_exceeding_surplus(self):
        payload = {
            "source_name": "Central Kitchen",
            "predicted_surplus_meals": 100.0,
            "allocated_meals": 150.0,  # Greater than surplus
            "matched_ngo_count": 2,
            "route_stop_count": 2,
            "route_distance_km": 12.5,
            "status": "planned"
        }
        res = self.client.post("/api/dashboard/activity", json=payload)
        self.assertEqual(res.status_code, 422)
        self.assertIn("Data Consistency Error", str(res.json()))

    # 7. Dashboard Recent Limit Range
    def test_dashboard_recent_invalid_limit(self):
        res_zero = self.client.get("/api/dashboard/recent?limit=0")
        self.assertEqual(res_zero.status_code, 422)

        res_excess = self.client.get("/api/dashboard/recent?limit=500")
        self.assertEqual(res_excess.status_code, 422)

    # 8. Health Endpoint Safe Output
    def test_health_endpoint_safe_response(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("status", data)
        self.assertIn("model_loaded", data)
        self.assertIn("preprocessor_loaded", data)
        self.assertIn("version", data)
        # Ensure no filesystem paths are leaked
        self.assertNotIn("path", str(data).lower())
        self.assertNotIn("k:\\", str(data).lower())
        self.assertNotIn("c:\\", str(data).lower())

    # 9. Malformed JSON Body Handling
    def test_malformed_json_handling(self):
        res = self.client.post(
            "/api/predict",
            content="NOT_VALID_JSON_STRING",
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("detail", res.json())

    # 10. Empty Payload Handling
    def test_empty_payload_handling(self):
        res = self.client.post("/api/predict", json={})
        self.assertEqual(res.status_code, 422)
        self.assertIn("detail", res.json())

    # 11. CORS Header Inspection
    def test_cors_headers(self):
        res = self.client.options(
            "/api/predict",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST"
            }
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("access-control-allow-origin"), "http://localhost:5173")


if __name__ == "__main__":
    unittest.main(verbosity=2)
