
import math


DEFAULT_REQUIRED_FIELDS = (
    "time_seconds",
    "coolant_temp_c",
)

VALIDATION_RULES = {
    "coolant_temp_c": (-40, 200),
    "engine_load_pct": (0, 100),
    "rpm": (0, float("inf")),
    "vehicle_speed_kmh": (0, float("inf")),
}


def validate_vehicle_trace(
    readings,
    required_fields=DEFAULT_REQUIRED_FIELDS,
):
    """Validate sensor readings before diagnostic analysis."""

    if not readings:
        raise ValueError("Vehicle trace cannot be empty.")

    previous_time = None

    for index, reading in enumerate(readings):
        if not isinstance(reading, dict):
            raise ValueError(
                f"Reading {index} must be a dictionary."
            )

        for field in required_fields:
            if field not in reading or reading[field] in (None, ""):
                raise ValueError(
                    f"Reading {index}: missing value for '{field}'."

                )

        for field, value in reading.items():
            if field == "time_seconds" or field in VALIDATION_RULES:
                try:
                    number = float(value)
                except (TypeError, ValueError):
                    raise ValueError(
                        f"{field} must be numeric."
                    )

                if not math.isfinite(number):
                    raise ValueError(
                        f"{field} must be finite."
                    )

                if field in VALIDATION_RULES:
                    minimum, maximum = VALIDATION_RULES[field]

                    if not minimum <= number <= maximum:
                        raise ValueError(
                            f"{field} is outside the "
                            "configured plausible range."
                        )

        current_time = float(reading["time_seconds"])

        if current_time < 0:
            raise ValueError(
                "Timestamps cannot be negative."
            )

        if (
            previous_time is not None
            and current_time <= previous_time
        ):
            raise ValueError(
                "Timestamps must be strictly increasing."
            )

        previous_time = current_time

    return True