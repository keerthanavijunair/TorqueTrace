import math
import csv
from pathlib import Path


def load_vehicle_trace():
    """Load sensor readings from the generated CSV file."""

    project_root = Path(__file__).resolve().parent.parent
    input_file = project_root / "data" / "vehicle_trace.csv"

    with input_file.open("r", newline="") as file:
        reader = csv.DictReader(file)
        readings = list(reader)

    if not readings:
        raise ValueError("Vehicle trace contains no readings.")

    return readings


def validate_vehicle_trace(readings):
    """Validate sensor readings before diagnostic analysis."""

    if not readings:
        raise ValueError("Vehicle trace contains no readings.")

    required_fields = [
        "time_seconds",
        "coolant_temp_c",
    ]

    previous_time = None

    for index, reading in enumerate(readings):
        for field in required_fields:
            if field not in reading or reading[field] in (None, ""):
                raise ValueError(
                    f"Reading {index}: missing value for '{field}'."
                )

            try:
                value = float(reading[field])
            except (TypeError, ValueError):
                raise ValueError(
                    f"Reading {index}: '{field}' must be numeric."
                ) from None

            if not math.isfinite(value):
                raise ValueError(
                    f"Reading {index}: '{field}' must be finite."
                )

        current_time = float(reading["time_seconds"])
        coolant_temp = float(reading["coolant_temp_c"])

        if current_time < 0:
            raise ValueError(
                f"Reading {index}: timestamp cannot be negative."
            )

        if coolant_temp < -50 or coolant_temp > 200:
            raise ValueError(
                f"Reading {index}: coolant temperature is outside "
                "the configured plausibility range."
            )

        if previous_time is not None and current_time <= previous_time:
            raise ValueError(
                f"Reading {index}: timestamps must be strictly increasing."
            )

        previous_time = current_time


def analyse_coolant_temperature(readings):
    """Analyse coolant temperature and flag potential overheating."""
    validate_vehicle_trace(readings)

    temperatures = [
        float(reading["coolant_temp_c"])
        for reading in readings
    ]

    times = [
        float(reading["time_seconds"])
        for reading in readings
    ]

    start_temp = temperatures[0]
    highest_temp = max(temperatures)
    temperature_rise = highest_temp - start_temp

    elapsed_time = times[-1] - times[0]

    if elapsed_time <= 0:
        raise ValueError("Elapsed time must be positive.")

    rise_per_minute = temperature_rise / elapsed_time * 60

    # Initial screening thresholds for this prototype, not
    # universal vehicle-manufacturer specifications.
    if highest_temp >= 110:
        status = "HIGH TEMPERATURE WARNING"
    elif highest_temp >= 105:
        status = "ELEVATED TEMPERATURE"
    else:
        status = "TEMPERATURE WITHIN INITIAL SCREENING RANGE"

    return {
        "starting_temperature_c": start_temp,
        "highest_temperature_c": highest_temp,
        "temperature_rise_c": temperature_rise,
        "elapsed_time_seconds": elapsed_time,
        "temperature_rise_c_per_minute": rise_per_minute,
        "status": status,
    }


def main():
    readings = load_vehicle_trace()
    result = analyse_coolant_temperature(readings)

    print("\n--- TorqueTrace Diagnostic Report ---")
    print(f"Readings analysed: {len(readings)}")
    print(f"Starting temperature: {result['starting_temperature_c']:.1f} C")
    print(f"Highest temperature: {result['highest_temperature_c']:.1f} C")
    print(f"Temperature rise: {result['temperature_rise_c']:.1f} C")
    print(
        "Temperature rise rate: "
        f"{result['temperature_rise_c_per_minute']:.1f} C/min"
    )
    print(f"Screening result: {result['status']}")


if __name__ == "__main__":
    main()
