import sys
import unittest
from pathlib import Path

# Make the src folder importable.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from diagnostics import analyse_coolant_temperature


class TestCoolantDiagnostics(unittest.TestCase):


    def test_missing_temperature_is_rejected(self):
        readings = [
            {"time_seconds": "0", "coolant_temp_c": "85"},
            {"time_seconds": "10", "coolant_temp_c": ""},
        ]

        with self.assertRaisesRegex(ValueError, "missing value"):
            analyse_coolant_temperature(readings)

    def test_non_increasing_timestamps_are_rejected(self):
        readings = [
            {"time_seconds": "10", "coolant_temp_c": "85"},
            {"time_seconds": "10", "coolant_temp_c": "90"},
        ]

        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            analyse_coolant_temperature(readings)

    def test_non_numeric_temperature_is_rejected(self):
        readings = [
            {"time_seconds": "0", "coolant_temp_c": "85"},
            {"time_seconds": "10", "coolant_temp_c": "hot"},
        ]

        with self.assertRaisesRegex(ValueError, "must be numeric"):
            analyse_coolant_temperature(readings)




    def test_high_temperature_is_flagged(self):
        readings = [
            {"time_seconds": "0", "coolant_temp_c": "88"},
            {"time_seconds": "10", "coolant_temp_c": "96"},
            {"time_seconds": "20", "coolant_temp_c": "112"},
        ]

        result = analyse_coolant_temperature(readings)

        self.assertEqual(
            result["status"],
            "HIGH TEMPERATURE WARNING"
        )
        self.assertEqual(result["highest_temperature_c"], 112.0)

    def test_normal_temperature_is_not_flagged_as_high(self):
        readings = [
            {"time_seconds": "0", "coolant_temp_c": "85"},
            {"time_seconds": "10", "coolant_temp_c": "88"},
            {"time_seconds": "20", "coolant_temp_c": "91"},
        ]

        result = analyse_coolant_temperature(readings)

        self.assertEqual(
            result["status"],
            "TEMPERATURE WITHIN INITIAL SCREENING RANGE"
        )

    def test_temperature_rise_is_calculated_correctly(self):
        readings = [
            {"time_seconds": "0", "coolant_temp_c": "80"},
            {"time_seconds": "30", "coolant_temp_c": "90"},
            {"time_seconds": "60", "coolant_temp_c": "100"},
        ]

        result = analyse_coolant_temperature(readings)

        self.assertEqual(result["temperature_rise_c"], 20.0)
        self.assertAlmostEqual(
            result["temperature_rise_c_per_minute"],
            20.0
        )

    def test_zero_elapsed_time_is_rejected(self):
        readings = [
            {"time_seconds": "10", "coolant_temp_c": "85"},
            {"time_seconds": "10", "coolant_temp_c": "90"},
        ]

        with self.assertRaises(ValueError):
            analyse_coolant_temperature(readings)


if __name__ == "__main__":
    unittest.main()