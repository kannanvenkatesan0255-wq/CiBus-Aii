"""
CIBUS-AI - End-to-End Prediction, Redistribution, Routing & Analytics Workflow Test
File: backend/tests/test_e2e_workflow.py

Purpose:
Tests the complete multi-stage pipeline:
1. Operational input -> Random Forest Surplus Prediction (ML Engine).
2. Predicted Surplus -> Multi-Criteria NGO Matching & Capacity Allocation.
3. Matched NGO Stops + Source -> Heuristic Nearest-Neighbor Route Optimization.
4. Planned Route Plan -> Activity Logging & Persistence.
5. Impact Dashboard -> Telemetry Summary & Activity History Verification.
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
    End-to-end integration test across ML inference, heuristic redistribution,
    route optimization, activity recording, and dashboard telemetry.
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_complete_prediction_matching_routing_dashboard_flow(self):
        # -------------------------------------------------------------
        # Step 1: Execute ML Prediction (Inference from 9 features)
        # -------------------------------------------------------------
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

        # -------------------------------------------------------------
        # Step 2: Feed Forecasted Surplus to NGO Matching Module
        # -------------------------------------------------------------
        match_input = {
            "predicted_surplus_meals": predicted_surplus,
            "food_type": "Both",
            "source_latitude": 13.0067,
            "source_longitude": 80.2026,
            "max_matches": 4
        }
        res_match = self.client.post("/api/match-ngos", json=match_input)
        self.assertEqual(res_match.status_code, 200)
        match_data = res_match.json()

        # Verify Allocation Constraints
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

        # -------------------------------------------------------------
        # Step 3: Route Optimization for Matched NGO Stops
        # -------------------------------------------------------------
        ngos_payload = [
            {
                "ngo_id": m["ngo_id"],
                "name": m["ngo_name"],
                "latitude": 13.0000 + idx * 0.01,  # synthetic demo coords
                "longitude": 80.2000 + idx * 0.01,
                "allocated_meals": m["allocated_meals"]
            }
            for idx, m in enumerate(match_data["matches"])
        ]

        route_input = {
            "source": {
                "name": "Guindy Central Dispatch Facility",
                "latitude": 13.0067,
                "longitude": 80.2026
            },
            "ngos": ngos_payload
        }
        res_route = self.client.post("/api/optimize-route", json=route_input)
        self.assertEqual(res_route.status_code, 200)
        route_data = res_route.json()

        self.assertEqual(route_data["summary"]["number_of_stops"], len(ngos_payload))
        self.assertGreaterEqual(route_data["summary"]["total_distance_km"], 0.0)
        self.assertEqual(len(route_data["route"]), len(ngos_payload) + 1)
        self.assertEqual(route_data["route"][0]["type"], "source")

        # -------------------------------------------------------------
        # Step 4: Record Planned Workflow Activity
        # -------------------------------------------------------------
        activity_input = {
            "source_name": route_data["summary"]["start_location"],
            "predicted_surplus_meals": predicted_surplus,
            "allocated_meals": route_data["summary"]["total_allocated_meals"],
            "matched_ngo_count": route_data["summary"]["number_of_stops"],
            "route_stop_count": route_data["summary"]["number_of_stops"],
            "route_distance_km": route_data["summary"]["total_distance_km"],
            "status": "planned",
            "notes": "E2E automated integration test workflow"
        }
        res_act = self.client.post("/api/dashboard/activity", json=activity_input)
        self.assertEqual(res_act.status_code, 201)
        act_data = res_act.json()
        self.assertTrue(act_data["activity_id"].startswith("ACT_"))

        # -------------------------------------------------------------
        # Step 5: Verify Telemetry in Dashboard Summary
        # -------------------------------------------------------------
        res_dash = self.client.post if False else self.client.get("/api/dashboard/summary")
        self.assertEqual(res_dash.status_code, 200)
        dash_data = res_dash.json()

        self.assertIn("summary", dash_data)
        self.assertIn("model_performance", dash_data)
        self.assertGreaterEqual(dash_data["summary"]["total_activities"], 1)
        self.assertGreaterEqual(dash_data["summary"]["total_allocated_meals"], route_data["summary"]["total_allocated_meals"])
        self.assertGreater(dash_data["model_performance"]["r2"], 0.90)


if __name__ == "__main__":
    unittest.main(verbosity=2)
