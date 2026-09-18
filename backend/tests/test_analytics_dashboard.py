"""
CIBUS-AI - Impact Dashboard & Analytics Test Suite
File: backend/tests/test_analytics_dashboard.py

Purpose:
Validates activity persistence, metrics aggregation, schema validation boundaries,
ML evaluation metric retrieval, and REST API endpoints.
"""

import sys
import json
import tempfile
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
from app.services.analytics_service import AnalyticsService, ACTIVITY_FILE


class TestAnalyticsDashboard(unittest.TestCase):
    """
    Unit and integration tests for AnalyticsService and Dashboard API.
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        # Backup existing activity history if present
        self.original_content = None
        if ACTIVITY_FILE.exists():
            with open(ACTIVITY_FILE, "r", encoding="utf-8") as f:
                self.original_content = f.read()

    def tearDown(self):
        # Restore original activity history
        if self.original_content is not None:
            with open(ACTIVITY_FILE, "w", encoding="utf-8") as f:
                f.write(self.original_content)

    def _set_activities(self, activities):
        with open(ACTIVITY_FILE, "w", encoding="utf-8") as f:
            json.dump(activities, f, indent=2)

    def test_01_empty_activity_history(self):
        """
        TEST 1: Empty activity history must return clean zero aggregates without errors.
        """
        self._set_activities([])
        summary = AnalyticsService.get_dashboard_summary()

        self.assertEqual(summary["summary"]["total_activities"], 0)
        self.assertEqual(summary["summary"]["total_predicted_surplus_meals"], 0.0)
        self.assertEqual(summary["summary"]["total_allocated_meals"], 0.0)
        self.assertEqual(summary["summary"]["allocation_rate_pct"], 0.0)
        self.assertEqual(summary["summary"]["total_matched_ngos"], 0)
        self.assertEqual(summary["summary"]["total_route_stops"], 0)
        self.assertEqual(summary["summary"]["total_route_distance_km"], 0.0)

    def test_02_single_valid_activity(self):
        """
        TEST 2: One valid activity must be aggregated accurately into summary metrics.
        """
        act = {
            "activity_id": "ACT_001",
            "timestamp": "2026-09-18T10:00:00Z",
            "source_name": "Hub A",
            "predicted_surplus_meals": 100.0,
            "allocated_meals": 80.0,
            "matched_ngo_count": 2,
            "route_stop_count": 2,
            "route_distance_km": 6.5,
            "status": "planned"
        }
        self._set_activities([act])
        summary = AnalyticsService.get_dashboard_summary()["summary"]

        self.assertEqual(summary["total_activities"], 1)
        self.assertEqual(summary["total_predicted_surplus_meals"], 100.0)
        self.assertEqual(summary["total_allocated_meals"], 80.0)
        self.assertEqual(summary["allocation_rate_pct"], 80.0)
        self.assertEqual(summary["total_matched_ngos"], 2)
        self.assertEqual(summary["total_route_stops"], 2)
        self.assertEqual(summary["total_route_distance_km"], 6.5)

    def test_03_multiple_activities_aggregation(self):
        """
        TEST 3: Multiple activities must aggregate sums and calculate allocation percentage correctly.
        """
        activities = [
            {
                "activity_id": "ACT_1",
                "timestamp": "2026-09-17T10:00:00Z",
                "source_name": "Hub 1",
                "predicted_surplus_meals": 200.0,
                "allocated_meals": 150.0,
                "matched_ngo_count": 2,
                "route_stop_count": 2,
                "route_distance_km": 8.0,
                "status": "completed"
            },
            {
                "activity_id": "ACT_2",
                "timestamp": "2026-09-18T10:00:00Z",
                "source_name": "Hub 2",
                "predicted_surplus_meals": 300.0,
                "allocated_meals": 300.0,
                "matched_ngo_count": 3,
                "route_stop_count": 3,
                "route_distance_km": 12.0,
                "status": "planned"
            }
        ]
        self._set_activities(activities)
        summary = AnalyticsService.get_dashboard_summary()["summary"]

        self.assertEqual(summary["total_activities"], 2)
        self.assertEqual(summary["total_predicted_surplus_meals"], 500.0)
        self.assertEqual(summary["total_allocated_meals"], 450.0)
        self.assertEqual(summary["allocation_rate_pct"], 90.0)
        self.assertEqual(summary["total_matched_ngos"], 5)
        self.assertEqual(summary["total_route_stops"], 5)
        self.assertEqual(summary["total_route_distance_km"], 20.0)

    def test_04_allocated_meals_cannot_exceed_surplus(self):
        """
        TEST 4: Validation error when allocated meals > predicted surplus.
        """
        invalid_payload = {
            "source_name": "Invalid Hub",
            "predicted_surplus_meals": 100.0,
            "allocated_meals": 150.0,  # Exceeds surplus
            "matched_ngo_count": 2,
            "route_stop_count": 2,
            "route_distance_km": 5.0
        }
        response = self.client.post("/api/dashboard/activity", json=invalid_payload)
        self.assertEqual(response.status_code, 422)

    def test_05_negative_values_rejection(self):
        """
        TEST 5: Negative quantities must trigger HTTP 422 validation errors.
        """
        neg_surplus = {
            "source_name": "Hub",
            "predicted_surplus_meals": -20.0,
            "allocated_meals": 0.0,
            "matched_ngo_count": 1,
            "route_stop_count": 1,
            "route_distance_km": 3.0
        }
        resp1 = self.client.post("/api/dashboard/activity", json=neg_surplus)
        self.assertEqual(resp1.status_code, 422)

        neg_dist = {
            "source_name": "Hub",
            "predicted_surplus_meals": 50.0,
            "allocated_meals": 50.0,
            "matched_ngo_count": 1,
            "route_stop_count": 1,
            "route_distance_km": -4.0
        }
        resp2 = self.client.post("/api/dashboard/activity", json=neg_dist)
        self.assertEqual(resp2.status_code, 422)

    def test_06_model_performance_loading(self):
        """
        TEST 6: Model evaluation metrics (MAE, RMSE, R²) must load from evaluation file.
        """
        perf = AnalyticsService.get_model_performance()
        self.assertIn("RandomForestRegressor", perf["model_name"])
        self.assertAlmostEqual(perf["mae"], 14.58, places=1)
        self.assertAlmostEqual(perf["rmse"], 20.69, places=1)
        self.assertAlmostEqual(perf["r2"], 0.9543, places=2)
        self.assertTrue("not a classification accuracy" in perf["note"].lower())

    def test_07_recent_activity_limit_validation(self):
        """
        TEST 7: Limit query parameter must be enforced (1 <= limit <= 100).
        """
        resp_invalid_low = self.client.get("/api/dashboard/recent?limit=0")
        self.assertEqual(resp_invalid_low.status_code, 422)

        resp_invalid_high = self.client.get("/api/dashboard/recent?limit=150")
        self.assertEqual(resp_invalid_high.status_code, 422)

    def test_08_recent_activities_ordering(self):
        """
        TEST 8: Most recent activities must be ordered descending by timestamp.
        """
        activities = [
            {"activity_id": "A1", "timestamp": "2026-09-15T09:00:00Z", "source_name": "H1", "predicted_surplus_meals": 50.0, "allocated_meals": 50.0, "matched_ngo_count": 1, "route_stop_count": 1, "route_distance_km": 2.0, "status": "planned"},
            {"activity_id": "A3", "timestamp": "2026-09-18T12:00:00Z", "source_name": "H3", "predicted_surplus_meals": 70.0, "allocated_meals": 70.0, "matched_ngo_count": 1, "route_stop_count": 1, "route_distance_km": 4.0, "status": "planned"},
            {"activity_id": "A2", "timestamp": "2026-09-16T11:00:00Z", "source_name": "H2", "predicted_surplus_meals": 60.0, "allocated_meals": 60.0, "matched_ngo_count": 1, "route_stop_count": 1, "route_distance_km": 3.0, "status": "planned"}
        ]
        self._set_activities(activities)
        recent = AnalyticsService.get_recent_activities(limit=2)

        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0]["activity_id"], "A3")
        self.assertEqual(recent[1]["activity_id"], "A2")

    def test_09_route_distance_aggregation(self):
        """
        TEST 9: Total route distance in summary must be exact sum of recorded distances.
        """
        activities = [
            {"activity_id": "D1", "timestamp": "2026-09-18T08:00:00Z", "source_name": "H1", "predicted_surplus_meals": 50.0, "allocated_meals": 50.0, "matched_ngo_count": 1, "route_stop_count": 1, "route_distance_km": 4.75, "status": "planned"},
            {"activity_id": "D2", "timestamp": "2026-09-18T09:00:00Z", "source_name": "H2", "predicted_surplus_meals": 50.0, "allocated_meals": 50.0, "matched_ngo_count": 1, "route_stop_count": 1, "route_distance_km": 6.25, "status": "planned"}
        ]
        self._set_activities(activities)
        summary = AnalyticsService.get_dashboard_summary()["summary"]
        self.assertAlmostEqual(summary["total_route_distance_km"], 11.0, places=2)

    def test_10_ngo_count_aggregation(self):
        """
        TEST 10: Total matched NGOs must be exact sum of individual activity NGO counts.
        """
        activities = [
            {"activity_id": "N1", "timestamp": "2026-09-18T08:00:00Z", "source_name": "H1", "predicted_surplus_meals": 50.0, "allocated_meals": 50.0, "matched_ngo_count": 3, "route_stop_count": 3, "route_distance_km": 4.0, "status": "planned"},
            {"activity_id": "N2", "timestamp": "2026-09-18T09:00:00Z", "source_name": "H2", "predicted_surplus_meals": 50.0, "allocated_meals": 50.0, "matched_ngo_count": 4, "route_stop_count": 4, "route_distance_km": 5.0, "status": "planned"}
        ]
        self._set_activities(activities)
        summary = AnalyticsService.get_dashboard_summary()["summary"]
        self.assertEqual(summary["total_matched_ngos"], 7)

    def test_11_activity_persistence_lifecycle(self):
        """
        TEST 11: Create a record via save_activity_record, retrieve it, and verify fields.
        """
        self._set_activities([])
        new_act = {
            "source_name": "Persisted Catering Hall",
            "predicted_surplus_meals": 175.5,
            "allocated_meals": 150.0,
            "matched_ngo_count": 3,
            "route_stop_count": 3,
            "route_distance_km": 9.42,
            "status": "planned",
            "notes": "Test persistence verification"
        }
        saved = AnalyticsService.save_activity_record(new_act)
        self.assertTrue(saved["activity_id"].startswith("ACT_"))
        self.assertEqual(saved["source_name"], "Persisted Catering Hall")

        history = AnalyticsService.load_activity_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["predicted_surplus_meals"], 175.5)
        self.assertEqual(history[0]["allocated_meals"], 150.0)

    def test_12_dashboard_rest_endpoints(self):
        """
        TEST 12: Verify GET /api/dashboard/summary and GET /api/dashboard/recent endpoints.
        """
        self._set_activities([
            {
                "activity_id": "REST_1",
                "timestamp": "2026-09-18T10:00:00Z",
                "source_name": "API Hub",
                "predicted_surplus_meals": 120.0,
                "allocated_meals": 120.0,
                "matched_ngo_count": 2,
                "route_stop_count": 2,
                "route_distance_km": 7.3,
                "status": "planned"
            }
        ])

        # Summary Endpoint
        summary_resp = self.client.get("/api/dashboard/summary")
        self.assertEqual(summary_resp.status_code, 200)
        summary_json = summary_resp.json()
        self.assertEqual(summary_json["status"], "success")
        self.assertEqual(summary_json["summary"]["total_predicted_surplus_meals"], 120.0)
        self.assertEqual(summary_json["summary"]["allocation_rate_pct"], 100.0)
        self.assertIn("mae", summary_json["model_performance"])

        # Recent Endpoint
        recent_resp = self.client.get("/api/dashboard/recent?limit=5")
        self.assertEqual(recent_resp.status_code, 200)
        recent_json = recent_resp.json()
        self.assertEqual(len(recent_json), 1)
        self.assertEqual(recent_json[0]["activity_id"], "REST_1")


if __name__ == "__main__":
    unittest.main()
