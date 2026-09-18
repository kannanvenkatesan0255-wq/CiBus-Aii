"""
CIBUS-AI - Prediction Engine Automated Test Suite
File: ai-engine/prediction/test_predict.py

Purpose:
Validates the inference engine across diverse operational scenarios, defensive
boundary validations, error handling, and data leakage enforcement.
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np

# Ensure ai-engine root is in python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_ENGINE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if AI_ENGINE_DIR not in sys.path:
    sys.path.insert(0, AI_ENGINE_DIR)

from prediction.predict import predict_surplus, validate_prediction_input, load_inference_artifacts


class TestFoodSurplusPrediction(unittest.TestCase):
    """Test cases for CIBUS-AI surplus meal prediction engine."""

    @classmethod
    def setUpClass(cls):
        """Verify model artifacts load successfully once before running test cases."""
        cls.model, cls.preprocessor = load_inference_artifacts()
        self_assert = unittest.TestCase()
        self_assert.assertIsNotNone(cls.model, "Failed to load model artifact!")
        self_assert.assertIsNotNone(cls.preprocessor, "Failed to load preprocessor artifact!")

    def test_scenario_1_normal_weekday(self):
        """Scenario 1: Standard Wednesday lunch with regular service."""
        payload = {
            "Day": "Wednesday",
            "Weather": "Sunny",
            "Customers_Forecast": 250,
            "Meals_Prepared": 290,
            "Festival": "No",
            "Event_Type": "Regular",
            "Staff_Count": 14,
            "Avg_Rating": 4.2,
            "Special_Event": 0
        }
        pred = predict_surplus(payload)
        print(f"\n[Test Output] Scenario 1 (Normal Weekday): Predicted = {pred:.2f} meals")
        self.assertIsInstance(pred, float)
        self.assertGreaterEqual(pred, 0.0)
        self.assertLessEqual(pred, payload["Meals_Prepared"])

    def test_scenario_2_weekend_buffet(self):
        """Scenario 2: Saturday high-capacity buffet service."""
        payload = {
            "Day": "Saturday",
            "Weather": "Sunny",
            "Customers_Forecast": 450,
            "Meals_Prepared": 560,
            "Festival": "No",
            "Event_Type": "Buffet",
            "Staff_Count": 24,
            "Avg_Rating": 4.4,
            "Special_Event": 0
        }
        pred = predict_surplus(payload)
        print(f"[Test Output] Scenario 2 (Weekend Buffet): Predicted = {pred:.2f} meals")
        self.assertIsInstance(pred, float)
        self.assertGreaterEqual(pred, 0.0)
        self.assertLessEqual(pred, payload["Meals_Prepared"])

    def test_scenario_3_festival_banquet(self):
        """Scenario 3: Festive season banquet with high preparation buffers."""
        payload = {
            "Day": "Friday",
            "Weather": "Cloudy",
            "Customers_Forecast": 500,
            "Meals_Prepared": 680,
            "Festival": "Diwali",
            "Event_Type": "Banquet",
            "Staff_Count": 30,
            "Avg_Rating": 4.5,
            "Special_Event": 1
        }
        pred = predict_surplus(payload)
        print(f"[Test Output] Scenario 3 (Festival Banquet): Predicted = {pred:.2f} meals")
        self.assertIsInstance(pred, float)
        self.assertGreaterEqual(pred, 0.0)
        self.assertLessEqual(pred, payload["Meals_Prepared"])

    def test_scenario_4_stormy_weather_special_event(self):
        """Scenario 4: Special event severely disrupted by stormy weather."""
        payload = {
            "Day": "Sunday",
            "Weather": "Stormy",
            "Customers_Forecast": 320,
            "Meals_Prepared": 420,
            "Festival": "No",
            "Event_Type": "Buffet",
            "Staff_Count": 18,
            "Avg_Rating": 3.9,
            "Special_Event": 1
        }
        pred = predict_surplus(payload)
        print(f"[Test Output] Scenario 4 (Stormy Weather Disruption): Predicted = {pred:.2f} meals")
        self.assertIsInstance(pred, float)
        self.assertGreaterEqual(pred, 0.0)
        self.assertLessEqual(pred, payload["Meals_Prepared"])

    def test_scenario_5_high_forecast_corporate(self):
        """Scenario 5: High-volume corporate dining on rainy Thursday."""
        payload = {
            "Day": "Thursday",
            "Weather": "Rainy",
            "Customers_Forecast": 750,
            "Meals_Prepared": 860,
            "Festival": "No",
            "Event_Type": "Corporate",
            "Staff_Count": 35,
            "Avg_Rating": 4.1,
            "Special_Event": 0
        }
        pred = predict_surplus(payload)
        print(f"[Test Output] Scenario 5 (High-Volume Corporate): Predicted = {pred:.2f} meals")
        self.assertIsInstance(pred, float)
        self.assertGreaterEqual(pred, 0.0)
        self.assertLessEqual(pred, payload["Meals_Prepared"])

    def test_data_leakage_rejection(self):
        """Verify Meals_Sold is strictly rejected with a ValueError."""
        payload_with_leakage = {
            "Day": "Monday",
            "Weather": "Sunny",
            "Customers_Forecast": 200,
            "Meals_Prepared": 250,
            "Meals_Sold": 210,  # LEAKAGE
            "Festival": "No",
            "Event_Type": "Regular",
            "Staff_Count": 10,
            "Avg_Rating": 4.0,
            "Special_Event": 0
        }
        with self.assertRaises(ValueError) as ctx:
            predict_surplus(payload_with_leakage)
        self.assertIn("Meals_Sold", str(ctx.exception))
        print("[Test Output] Data Leakage Rejection: PASSED (Meals_Sold rejected successfully)")

    def test_missing_fields_validation(self):
        """Verify missing required fields raise descriptive ValueErrors."""
        incomplete_payload = {
            "Day": "Monday",
            "Weather": "Sunny",
            "Customers_Forecast": 200
            # Missing Meals_Prepared, Festival, Event_Type, etc.
        }
        with self.assertRaises(ValueError) as ctx:
            predict_surplus(incomplete_payload)
        self.assertIn("Missing required prediction fields", str(ctx.exception))
        print("[Test Output] Missing Field Validation: PASSED")

    def test_invalid_numerical_bounds(self):
        """Verify negative meal counts and out-of-bounds ratings are caught."""
        negative_meals_payload = {
            "Day": "Monday",
            "Weather": "Sunny",
            "Customers_Forecast": 200,
            "Meals_Prepared": -50,  # INVALID
            "Festival": "No",
            "Event_Type": "Regular",
            "Staff_Count": 10,
            "Avg_Rating": 4.0,
            "Special_Event": 0
        }
        with self.assertRaises(ValueError):
            predict_surplus(negative_meals_payload)

        invalid_rating_payload = {
            "Day": "Monday",
            "Weather": "Sunny",
            "Customers_Forecast": 200,
            "Meals_Prepared": 250,
            "Festival": "No",
            "Event_Type": "Regular",
            "Staff_Count": 10,
            "Avg_Rating": 6.8,  # INVALID (> 5.0)
            "Special_Event": 0
        }
        with self.assertRaises(ValueError):
            predict_surplus(invalid_rating_payload)
        print("[Test Output] Numerical Boundary Validation: PASSED")

    def test_batch_dataframe_prediction(self):
        """Verify batch predictions on a DataFrame."""
        batch_df = pd.DataFrame([
            {
                "Day": "Tuesday", "Weather": "Sunny", "Customers_Forecast": 150,
                "Meals_Prepared": 180, "Festival": "No", "Event_Type": "Regular",
                "Staff_Count": 8, "Avg_Rating": 4.0, "Special_Event": 0
            },
            {
                "Day": "Friday", "Weather": "Rainy", "Customers_Forecast": 400,
                "Meals_Prepared": 500, "Festival": "No", "Event_Type": "Buffet",
                "Staff_Count": 20, "Avg_Rating": 4.2, "Special_Event": 0
            }
        ])
        results = predict_surplus(batch_df)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        print(f"[Test Output] Batch Prediction Test: PASSED (Results: {results})")


if __name__ == "__main__":
    unittest.main(verbosity=2)
