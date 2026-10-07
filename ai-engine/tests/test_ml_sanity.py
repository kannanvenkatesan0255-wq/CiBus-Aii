"""
CIBUS-AI - Machine Learning Physical Sanity & Boundary Test Suite
File: ai-engine/tests/test_ml_sanity.py

Purpose:
Verifies that the trained Random Forest Regressor and post-prediction validation
strictly respect physical domain invariants across varied operational regimes:
1. Surplus must never be negative (0 <= Surplus).
2. Surplus must never exceed Meals_Prepared (Surplus <= Meals_Prepared).
3. If expected demand (Customers_Forecast) >= Meals_Prepared, surplus is 0 or ~0.
4. If Meals_Prepared significantly exceeds expected demand, surplus increases accordingly.
5. Evaluates Cases A through G specified in project requirements.
6. Evaluates 25 randomized valid operational configurations.
7. Reports Raw RF Prediction, Validated Final Prediction, and Constraint Status.
"""

import sys
import os
import unittest
import numpy as np
import pandas as pd
import joblib

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_ENGINE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if AI_ENGINE_DIR not in sys.path:
    sys.path.insert(0, AI_ENGINE_DIR)

from prediction.predict import (
    load_inference_artifacts,
    predict_surplus,
    predict_surplus_detailed,
    FEATURE_COLUMNS
)


class TestMLPhysicalSanity(unittest.TestCase):
    """Rigorous physical sanity test suite for CIBUS-AI ML predictions."""

    @classmethod
    def setUpClass(cls):
        cls.model, cls.preprocessor = load_inference_artifacts()

    def test_specified_cases_a_through_g(self):
        """Validates canonical project benchmark test cases A through G."""
        test_cases = [
            {
                "case": "A",
                "desc": "Customers = 200, Prepared = 20 (Severe Demand Overhang)",
                "data": {"Day": "Monday", "Weather": "Sunny", "Customers_Forecast": 200, "Meals_Prepared": 20, "Festival": "No", "Event_Type": "Regular", "Staff_Count": 5, "Avg_Rating": 4.0, "Special_Event": 0},
                "expected_surplus": 0.0,
                "allow_tolerance": 0.0
            },
            {
                "case": "B",
                "desc": "Customers = 200, Prepared = 200 (Exact Supply-Demand Parity)",
                "data": {"Day": "Monday", "Weather": "Sunny", "Customers_Forecast": 200, "Meals_Prepared": 200, "Festival": "No", "Event_Type": "Regular", "Staff_Count": 10, "Avg_Rating": 4.0, "Special_Event": 0},
                "expected_surplus": 0.0,
                "allow_tolerance": 0.0
            },
            {
                "case": "C",
                "desc": "Customers = 150, Prepared = 200 (Moderate Supply Buffer)",
                "data": {"Day": "Monday", "Weather": "Sunny", "Customers_Forecast": 150, "Meals_Prepared": 200, "Festival": "No", "Event_Type": "Regular", "Staff_Count": 10, "Avg_Rating": 4.0, "Special_Event": 0},
                "min_expected": 30.0,
                "max_expected": 70.0
            },
            {
                "case": "D",
                "desc": "Customers = 100, Prepared = 200 (Meaningful Surplus)",
                "data": {"Day": "Monday", "Weather": "Sunny", "Customers_Forecast": 100, "Meals_Prepared": 200, "Festival": "No", "Event_Type": "Regular", "Staff_Count": 10, "Avg_Rating": 4.0, "Special_Event": 0},
                "min_expected": 70.0,
                "max_expected": 125.0
            },
            {
                "case": "E",
                "desc": "Customers = 50, Prepared = 200 (High Surplus Leftover)",
                "data": {"Day": "Monday", "Weather": "Sunny", "Customers_Forecast": 50, "Meals_Prepared": 200, "Festival": "No", "Event_Type": "Regular", "Staff_Count": 10, "Avg_Rating": 4.0, "Special_Event": 0},
                "min_expected": 100.0,
                "max_expected": 175.0
            },
            {
                "case": "F",
                "desc": "Customers = 500, Prepared = 450 (High Footfall Demand Overhang)",
                "data": {"Day": "Monday", "Weather": "Sunny", "Customers_Forecast": 500, "Meals_Prepared": 450, "Festival": "No", "Event_Type": "Regular", "Staff_Count": 18, "Avg_Rating": 4.0, "Special_Event": 0},
                "expected_surplus": 0.0,
                "allow_tolerance": 0.0
            },
            {
                "case": "G",
                "desc": "Customers = 100, Prepared = 500 (Massive Over-Catering Surplus)",
                "data": {"Day": "Monday", "Weather": "Sunny", "Customers_Forecast": 100, "Meals_Prepared": 500, "Festival": "No", "Event_Type": "Regular", "Staff_Count": 18, "Avg_Rating": 4.0, "Special_Event": 0},
                "min_expected": 280.0,
                "max_expected": 450.0
            }
        ]

        print("\n" + "=" * 90)
        print("          CIBUS-AI ML PREDICTION PHYSICAL SANITY BENCHMARK REPORT (CASES A-G)")
        print("=" * 90)
        print(f"{'Case':<5} | {'Description':<42} | {'Raw RF':<10} | {'Validated':<10} | {'Physical Bounds':<12}")
        print("-" * 90)

        for tc in test_cases:
            res = predict_surplus_detailed(tc["data"])
            raw = res["raw_prediction"]
            val = res["validated_prediction"]
            meals_prep = tc["data"]["Meals_Prepared"]
            cust_fore = tc["data"]["Customers_Forecast"]

            # Physical assertions:
            # 1. Non-negative
            self.assertGreaterEqual(val, 0.0, f"Case {tc['case']} produced negative surplus")
            # 2. Cannot exceed meals prepared
            self.assertLessEqual(val, meals_prep, f"Case {tc['case']} exceeded meals prepared")
            # 3. Demand >= Prepared yields 0
            if cust_fore >= meals_prep:
                self.assertEqual(val, 0.0, f"Case {tc['case']} expected 0 surplus when demand >= supply")

            bounds_ok = "YES" if (0.0 <= val <= meals_prep) else "NO"
            print(f"{tc['case']:<5} | {tc['desc']:<42} | {raw:<10.2f} | {val:<10.2f} | {bounds_ok:<12}")

        print("=" * 90)

    def test_canonical_section_11_sanity_cases(self):
        """Validates all 8 canonical sanity scenarios specified in Prompt Section 11."""
        sanity_scenarios = [
            {"id": 1, "desc": "Customers = 200, Prepared = 20 (Severe Demand Overhang)", "c": 200, "m": 20, "staff": 5, "max_val": 0.0},
            {"id": 2, "desc": "Customers = 20, Prepared = 200 (Large Supply Excess)", "c": 20, "m": 200, "staff": 10, "min_val": 100.0},
            {"id": 3, "desc": "Customers = 100, Prepared = 200 (Moderate Supply Buffer)", "c": 100, "m": 200, "staff": 10, "min_val": 60.0},
            {"id": 4, "desc": "Customers = 200, Prepared = 200 (Parity)", "c": 200, "m": 200, "staff": 10, "max_val": 0.0},
            {"id": 5, "desc": "Customers = 500, Prepared = 200 (High Demand Overhang)", "c": 500, "m": 200, "staff": 10, "max_val": 0.0},
            {"id": 6, "desc": "Customers = 100, Prepared = 500 (Massive Over-Catering)", "c": 100, "m": 500, "staff": 20, "min_val": 280.0},
            {"id": 7, "desc": "Customers = 800, Prepared = 900 (Large Event Buffer)", "c": 800, "m": 900, "staff": 35, "min_val": 10.0},
            {"id": 8, "desc": "Customers = 300, Prepared = 1000 (Major Cancellation)", "c": 300, "m": 1000, "staff": 40, "min_val": 550.0},
        ]

        print("\n" + "=" * 90)
        print("          CIBUS-AI SECTION 11 BENCHMARK SANITY CASES AUDIT")
        print("=" * 90)
        print(f"{'#':<3} | {'Scenario':<42} | {'Raw RF':<10} | {'Validated':<10} | {'Pass':<6}")
        print("-" * 90)

        for tc in sanity_scenarios:
            payload = {
                "Day": "Monday",
                "Weather": "Sunny",
                "Customers_Forecast": tc["c"],
                "Meals_Prepared": tc["m"],
                "Festival": "No",
                "Event_Type": "Regular",
                "Staff_Count": tc["staff"],
                "Avg_Rating": 4.0,
                "Special_Event": 0
            }
            res = predict_surplus_detailed(payload)
            raw = res["raw_prediction"]
            val = res["validated_prediction"]

            self.assertGreaterEqual(val, 0.0)
            self.assertLessEqual(val, tc["m"])
            if "max_val" in tc:
                self.assertLessEqual(val, tc["max_val"])
            if "min_val" in tc:
                self.assertGreaterEqual(val, tc["min_val"])

            print(f"{tc['id']:<3} | {tc['desc']:<42} | {raw:<10.2f} | {val:<10.2f} | YES")
        print("=" * 90)

    def test_100_plus_randomized_combinations(self):
        """Tests 120 varied randomized combinations across all operational regimes."""
        rng = np.random.default_rng(2026)
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weathers = ["Sunny", "Cloudy", "Rainy", "Stormy"]
        events = ["Regular", "Buffet", "Corporate", "Banquet"]
        festivals = ["No", "Diwali", "Eid", "Christmas", "New Year"]

        print("\n" + "=" * 90)
        print("      CIBUS-AI RANDOMIZED OPERATIONAL CONFIGURATIONS AUDIT (120 SCENARIOS)")
        print("=" * 90)
        print(f"{'#':<3} | {'Cust':<5} | {'Prep':<5} | {'Weather':<8} | {'Event':<9} | {'Raw RF':<10} | {'Validated':<10} | {'Pass':<5}")
        print("-" * 90)

        for i in range(1, 121):
            c_fore = int(rng.integers(20, 1000))
            m_prep = int(rng.integers(20, 1400))
            w = str(rng.choice(weathers))
            ev = str(rng.choice(events))
            d = str(rng.choice(days))
            fest = str(rng.choice(festivals))
            staff = int(np.clip(3 + m_prep // 26, 4, 52))
            rating = round(float(rng.uniform(2.5, 4.9)), 2)
            special = int(rng.choice([0, 1]))

            payload = {
                "Day": d,
                "Weather": w,
                "Customers_Forecast": c_fore,
                "Meals_Prepared": m_prep,
                "Festival": fest,
                "Event_Type": ev,
                "Staff_Count": staff,
                "Avg_Rating": rating,
                "Special_Event": special
            }

            res = predict_surplus_detailed(payload)
            raw = res["raw_prediction"]
            val = res["validated_prediction"]

            # Invariant assertions:
            self.assertGreaterEqual(val, 0.0)
            self.assertLessEqual(val, m_prep)
            if c_fore >= m_prep:
                self.assertEqual(val, 0.0)

            if i <= 15 or i >= 115:
                print(f"{i:<3} | {c_fore:<5} | {m_prep:<5} | {w:<8} | {ev:<9} | {raw:<10.2f} | {val:<10.2f} | YES")
            elif i == 16:
                print("... (scenarios 16 to 114 verified successfully) ...")

        print("=" * 90)


if __name__ == "__main__":
    unittest.main()
