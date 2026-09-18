"""
CIBUS-AI - FastAPI Backend & Prediction API Test Suite
File: backend/tests/test_prediction_api.py

Purpose:
Validates backend REST endpoints using FastAPI TestClient:
1. Health and readiness endpoints.
2. Prediction endpoint with valid operational payloads.
3. Strict validation on required fields, bounds, and categories.
4. Rejection of data-leakage attempts ('Meals_Sold').
5. Model information metadata endpoint.
6. Execution using the pre-trained ML model (Zero Retraining).
"""

import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# Resolve paths
TEST_DIR = Path(__file__).resolve().parent
BACKEND_DIR = TEST_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
AI_ENGINE_DIR = PROJECT_ROOT / "ai-engine"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(AI_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(AI_ENGINE_DIR))

from app.main import app


class TestPredictionAPI(unittest.TestCase):
    """
    Test suite for CIBUS-AI FastAPI endpoints.
    """

    @classmethod
    def setUpClass(cls):
        """Initializes the FastAPI TestClient instance."""
        cls.client = TestClient(app)

    def test_01_health_endpoint(self):
        """Test 1: Verify /health returns 200 and confirms ML artifacts are loaded."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["model_loaded"], "Model artifact should be loaded")
        self.assertTrue(data["preprocessor_loaded"], "Preprocessor artifact should be loaded")
        self.assertEqual(data["version"], "1.0.0")

    def test_02_root_endpoint(self):
        """Test 2: Verify / returns project metadata and navigation links."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("project", data)
        self.assertEqual(data["prediction_endpoint"], "/api/predict")

    def test_03_valid_prediction_request(self):
        """Test 3: Verify POST /api/predict with standard operational payload."""
        payload = {
            "Day": "Friday",
            "Weather": "Rainy",
            "Customers_Forecast": 450,
            "Meals_Prepared": 600,
            "Festival": "Diwali",
            "Event_Type": "Buffet",
            "Staff_Count": 25,
            "Avg_Rating": 4.5,
            "Special_Event": 1
        }
        response = self.client.post("/api/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("predicted_surplus_meals", data)
        self.assertIsInstance(data["predicted_surplus_meals"], (int, float))
        self.assertGreaterEqual(data["predicted_surplus_meals"], 0.0)
        self.assertLessEqual(data["predicted_surplus_meals"], 600.0)
        self.assertIn("recommended_action", data)
        print(f"\n[Test 3 Output] Predicted surplus for Friday Buffet: {data['predicted_surplus_meals']} meals")

    def test_04_missing_required_field(self):
        """Test 4: Verify 422 Unprocessable Entity when required field is missing."""
        payload = {
            "Day": "Monday",
            "Weather": "Sunny",
            # Missing Customers_Forecast
            "Meals_Prepared": 400,
            "Festival": "No",
            "Event_Type": "Regular",
            "Staff_Count": 15,
            "Avg_Rating": 4.0,
            "Special_Event": 0
        }
        response = self.client.post("/api/predict", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_05_invalid_numerical_input(self):
        """Test 5: Verify 422 Unprocessable Entity when numerical values violate constraints."""
        payload = {
            "Day": "Monday",
            "Weather": "Sunny",
            "Customers_Forecast": -50,  # Invalid: negative
            "Meals_Prepared": 400,
            "Festival": "No",
            "Event_Type": "Regular",
            "Staff_Count": 15,
            "Avg_Rating": 4.0,
            "Special_Event": 0
        }
        response = self.client.post("/api/predict", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_06_invalid_rating(self):
        """Test 6: Verify 422 Unprocessable Entity when Avg_Rating is out of bounds (1.0 - 5.0)."""
        payload = {
            "Day": "Tuesday",
            "Weather": "Sunny",
            "Customers_Forecast": 300,
            "Meals_Prepared": 350,
            "Festival": "No",
            "Event_Type": "Regular",
            "Staff_Count": 10,
            "Avg_Rating": 5.8,  # Invalid: exceeds 5.0
            "Special_Event": 0
        }
        response = self.client.post("/api/predict", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_07_invalid_categorical_input(self):
        """Test 7: Verify 422 Unprocessable Entity when categorical field is invalid."""
        payload = {
            "Day": "Funday",  # Invalid day
            "Weather": "Sunny",
            "Customers_Forecast": 300,
            "Meals_Prepared": 350,
            "Festival": "No",
            "Event_Type": "Regular",
            "Staff_Count": 10,
            "Avg_Rating": 4.2,
            "Special_Event": 0
        }
        response = self.client.post("/api/predict", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_08_meals_sold_leakage_rejection(self):
        """Test 8: Verify strict rejection when client attempts to submit 'Meals_Sold'."""
        payload = {
            "Day": "Wednesday",
            "Weather": "Cloudy",
            "Customers_Forecast": 400,
            "Meals_Prepared": 450,
            "Festival": "No",
            "Event_Type": "Regular",
            "Staff_Count": 18,
            "Avg_Rating": 4.1,
            "Special_Event": 0,
            "Meals_Sold": 380  # FORBIDDEN DATA LEAKAGE FIELD
        }
        response = self.client.post("/api/predict", json=payload)
        self.assertEqual(response.status_code, 422)
        response_text = response.text.lower()
        self.assertTrue("data leakage" in response_text or "meals_sold" in response_text)

    def test_09_prediction_response_structure(self):
        """Test 9: Verify response schema completeness and model identification."""
        payload = {
            "Day": "Saturday",
            "Weather": "Sunny",
            "Customers_Forecast": 350,
            "Meals_Prepared": 400,
            "Festival": "No",
            "Event_Type": "Regular",
            "Staff_Count": 12,
            "Avg_Rating": 4.3,
            "Special_Event": 0
        }
        response = self.client.post("/api/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("predicted_surplus_meals", data)
        self.assertIn("model_name", data)
        self.assertIn("status", data)
        self.assertIn("input_summary", data)
        self.assertIn("recommended_action", data)

    def test_10_model_info_endpoint(self):
        """Test 10: Verify /api/model-info returns metadata and evaluation metrics."""
        response = self.client.get("/api/model-info")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["target_variable"], "Surplus_Meals")
        self.assertEqual(data["feature_count"], 9)
        self.assertIn("Meals_Prepared", data["features"])
        self.assertNotIn("Meals_Sold", data["features"])
        self.assertIn("evaluation_metrics", data)
        self.assertEqual(data["status"], "active")


if __name__ == "__main__":
    unittest.main(verbosity=2)
