"""
CIBUS-AI - End-to-End Prediction & Redistribution Workflow Test
File: backend/tests/test_e2e_workflow.py

Purpose:
Tests the complete multi-stage pipeline:
1. Operational input -> Random Forest Surplus Prediction (ML Engine).
2. Predicted Surplus -> Multi-Criteria NGO Matching & Capacity Allocation.
3. Constraint verification: Zero overflow, allocation <= capacity, total <= surplus.
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


class TestEndToEndWorkflow(unittest.TestCase):
    """
    End-to-end integration test across ML inference and rule-based redistribution.
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_complete_prediction_and_redistribution_flow(self):
        # Step 1: Execute ML Prediction
        food_input = {
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
        res_pred = self.client.post("/api/predict", json=food_input)
        self.assertEqual(res_pred.status_code, 200)
        pred_data = res_pred.json()
        predicted_surplus = pred_data["predicted_surplus_meals"]
        self.assertGreater(predicted_surplus, 0.0)

        # Step 2: Feed Forecasted Surplus to NGO Matching Module
        match_input = {
            "predicted_surplus_meals": predicted_surplus,
            "food_type": "Both",
            "source_latitude": 12.9716,
            "source_longitude": 80.2000,
            "max_matches": 3
        }
        res_match = self.client.post("/api/match-ngos", json=match_input)
        self.assertEqual(res_match.status_code, 200)
        match_data = res_match.json()

        # Step 3: Verify Physical & Logical Constraints
        self.assertLessEqual(match_data["total_allocated_meals"], match_data["predicted_surplus_meals"])
        self.assertEqual(
            round(match_data["total_allocated_meals"] + match_data["unallocated_meals"], 2),
            round(match_data["predicted_surplus_meals"], 2)
        )
        self.assertGreater(len(match_data["matches"]), 0)

        for match in match_data["matches"]:
            self.assertLessEqual(match["allocated_meals"], match["capacity_meals"])
            self.assertGreater(match["match_score"], 0.0)
            self.assertIsNotNone(match["reason"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
