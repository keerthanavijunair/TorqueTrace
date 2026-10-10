
import unittest

from src.validation import validate_vehicle_trace


def make_readings(
    time=0,
    coolant=90,
    rpm=1500,
    load=30,
    speed=20,
):
    return [{
        "time_seconds": time,
        "coolant_temp_c": coolant,
        "rpm": rpm,
        "engine_load_pct": load,
        "vehicle_speed_kmh": speed,
    }]


class TestVehicleTraceValidation(unittest.TestCase):

    def test_valid_reading_is_accepted(self):
        self.assertTrue(
            validate_vehicle_trace(make_readings())
        )

    def test_empty_trace_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            validate_vehicle_trace([])

    def test_missing_required_field_is_rejected(self):
        readings = make_readings()
        del readings[0]["coolant_temp_c"]

        with self.assertRaisesRegex(ValueError, "missing value"):
            validate_vehicle_trace(readings)

    def test_empty_required_value_is_rejected(self):
        readings = make_readings(coolant="")

        with self.assertRaisesRegex(ValueError, "missing value"):
            validate_vehicle_trace(readings)

    def test_infinite_temperature_is_rejected(self):
        readings = make_readings(coolant=float("inf"))

        with self.assertRaisesRegex(ValueError, "finite"):
            validate_vehicle_trace(readings)

    def test_coolant_above_configured_range_is_rejected(self):
        readings = make_readings(coolant=250)

        with self.assertRaisesRegex(ValueError, "plausible range"):
            validate_vehicle_trace(readings)

    def test_coolant_below_configured_range_is_rejected(self):
        readings = make_readings(coolant=-60)

        with self.assertRaisesRegex(ValueError, "plausible range"):
            validate_vehicle_trace(readings)

    def test_engine_load_above_100_is_rejected(self):
        readings = make_readings(load=101)

        with self.assertRaisesRegex(ValueError, "plausible range"):
            validate_vehicle_trace(
                readings,
                required_fields=(
                    "time_seconds",
                    "coolant_temp_c",
                    "engine_load_pct",
                ),
            )

    def test_negative_timestamp_is_rejected(self):
        readings = make_readings(time=-1)

        with self.assertRaisesRegex(ValueError, "negative"):
            validate_vehicle_trace(readings)

    def test_duplicate_timestamps_are_rejected(self):
        readings = [
            make_readings(time=10)[0],
            make_readings(time=10, coolant=92)[0],
        ]

        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            validate_vehicle_trace(readings)


if __name__ == "__main__":
    unittest.main()