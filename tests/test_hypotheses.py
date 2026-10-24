import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from hypotheses import rank_hypotheses


class TestHypothesisRanking(unittest.TestCase):



    def test_engine_load_above_100_is_rejected(self):
        readings = [
            {
                "time_seconds": 0,
                "coolant_temp_c": 90,
                "rpm": 1500,
                "engine_load_pct": 150,
            },
            {
                "time_seconds": 10,
                "coolant_temp_c": 95,
                "rpm": 1800,
                "engine_load_pct": 50,
            },
        ]

        with self.assertRaisesRegex(ValueError, "plausible range"):
            rank_hypotheses(readings)

    def test_negative_rpm_is_rejected(self):
        readings = [
            {
                "time_seconds": 0,
                "coolant_temp_c": 90,
                "rpm": -100,
                "engine_load_pct": 20,
            },
            {
                "time_seconds": 10,
                "coolant_temp_c": 95,
                "rpm": 1500,
                "engine_load_pct": 30,
            },
        ]

        with self.assertRaisesRegex(ValueError, "plausible range"):
            rank_hypotheses(readings)

    def test_nan_coolant_temperature_is_rejected(self):
        readings = [
            {
                "time_seconds": 0,
                "coolant_temp_c": "NaN",
                "rpm": 1500,
                "engine_load_pct": 20,
            },
            {
                "time_seconds": 10,
                "coolant_temp_c": 95,
                "rpm": 1800,
                "engine_load_pct": 30,
            },
        ]

        with self.assertRaisesRegex(ValueError, "finite"):
            rank_hypotheses(readings)

    def test_decreasing_timestamps_are_rejected(self):
        readings = [
            {
                "time_seconds": 10,
                "coolant_temp_c": 90,
                "rpm": 1500,
                "engine_load_pct": 20,
            },
            {
                "time_seconds": 5,
                "coolant_temp_c": 95,
                "rpm": 1800,
                "engine_load_pct": 30,
            },
        ]

        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            rank_hypotheses(readings)



    def test_high_temperature_ranks_cooling_first(self):
        readings = [
            {
                "time_seconds": "0",
                "coolant_temp_c": "88",
                "rpm": "900",
                "engine_load_pct": "20",
            },
            {
                "time_seconds": "10",
                "coolant_temp_c": "112",
                "rpm": "2200",
                "engine_load_pct": "55",
            },
        ]

        result = rank_hypotheses(readings)

        self.assertEqual(
            result["hypotheses"][0]["name"],
            "Cooling-system performance issue",
        )
        self.assertEqual(result["hypotheses"][0]["score"], 4)


    def test_cooling_hypothesis_includes_supporting_readings(self):
        readings = [
            {
                "time_seconds": 0,
                "coolant_temp_c": 88,
                "rpm": 900,
                "engine_load_pct": 20,
            },
            {
                "time_seconds": 180,
                "coolant_temp_c": 112,
                "rpm": 2200,
                "engine_load_pct": 55,
            },
        ]

        result = rank_hypotheses(readings)
        cooling = result["hypotheses"][0]

        self.assertIn("supporting_readings", cooling)
        self.assertTrue(cooling["supporting_readings"])
        self.assertEqual(
            cooling["supporting_readings"][-1]["time_seconds"],
            180,
        )
        self.assertEqual(
            cooling["supporting_readings"][-1]["coolant_temp_c"],
            112,
        )


    
    def test_normal_trace_has_no_elevated_temperature_condition(self):
        readings = [
            {
                "time_seconds": "0",
                "coolant_temp_c": "85",
                "rpm": "900",
                "engine_load_pct": "20",
            },
            {
                "time_seconds": "10",
                "coolant_temp_c": "90",
                "rpm": "1200",
                "engine_load_pct": "30",
            },
        ]

        result = rank_hypotheses(readings)

        self.assertEqual(
            result["observed_condition"],
            "No elevated temperature under the configured rule",
        )
        self.assertEqual(result["hypotheses"], [])


    def test_missing_rpm_is_rejected(self):
        readings = [
            {
                "time_seconds": "0",
                "coolant_temp_c": "85",
                "engine_load_pct": "20",
            },
        ]

        with self.assertRaisesRegex(ValueError, "rpm"):
            rank_hypotheses(readings)

    def test_malformed_temperature_is_rejected(self):
        readings = [
            {
                "time_seconds": "0",
                "coolant_temp_c": "hot",
                "rpm": "900",
                "engine_load_pct": "20",
            },
        ]

        with self.assertRaisesRegex(ValueError, "must be numeric"):
            rank_hypotheses(readings)





    def test_sudden_temperature_spike_is_detected(self):
        readings = [
            {
                "time_seconds": 0,
                "coolant_temp_c": 85,
                "rpm": 1000,
                "engine_load_pct": 25,
            },
            {
                "time_seconds": 10,
                "coolant_temp_c": 86,
                "rpm": 1100,
                "engine_load_pct": 25,
            },
            {
                "time_seconds": 20,
                "coolant_temp_c": 115,
                "rpm": 1100,
                "engine_load_pct": 25,
            },
            {
                "time_seconds": 30,
                "coolant_temp_c": 87,
                "rpm": 1100,
                "engine_load_pct": 25,
            },
        ]

        result = rank_hypotheses(readings)

        self.assertTrue(
            result["sensor_anomaly"]["suspected"]
        )
        self.assertIn(
            "sudden temperature spike",
            result["sensor_anomaly"]["reason"].lower(),
        )



    def test_temperature_just_below_threshold(self):
        readings = [
            {
                "time_seconds": 0,
                "coolant_temp_c": 90,
                "rpm": 1000,
                "engine_load_pct": 25,
            },
            {
                "time_seconds": 10,
                "coolant_temp_c": 104.9,
                "rpm": 1200,
                "engine_load_pct": 30,
            },
        ]

        result = rank_hypotheses(readings)

        self.assertEqual(
            result["observed_condition"],
            "No elevated temperature under the configured rule",
        )

    def test_temperature_exactly_at_threshold(self):
        readings = [
            {
                "time_seconds": 0,
                "coolant_temp_c": 90,
                "rpm": 1000,
                "engine_load_pct": 25,
            },
            {
                "time_seconds": 10,
                "coolant_temp_c": 105.0,
                "rpm": 1200,
                "engine_load_pct": 30,
            },
        ]

        result = rank_hypotheses(readings)

        self.assertEqual(
            result["observed_condition"],
            "Elevated coolant temperature",
        )

    def test_temperature_just_above_threshold(self):
        readings = [
            {
                "time_seconds": 0,
                "coolant_temp_c": 90,
                "rpm": 1000,
                "engine_load_pct": 25,
            },
            {
                "time_seconds": 10,
                "coolant_temp_c": 105.1,
                "rpm": 1200,
                "engine_load_pct": 30,
            },
        ]

        result = rank_hypotheses(readings)

        self.assertEqual(
            result["observed_condition"],
            "Elevated coolant temperature",
        )
    


if __name__ == "__main__":
    unittest.main()
