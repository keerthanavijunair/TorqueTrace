import csv
from pathlib import Path


def generate_vehicle_trace():
    """Generate synthetic vehicle sensor readings for testing."""

    readings = [
        {
            "time_seconds": 0,
            "rpm": 900,
            "coolant_temp_c": 88,
            "vehicle_speed_kmh": 0,
            "engine_load_pct": 20,
        },
        {
            "time_seconds": 10,
            "rpm": 1200,
            "coolant_temp_c": 90,
            "vehicle_speed_kmh": 10,
            "engine_load_pct": 30,
        },
        {
            "time_seconds": 20,
            "rpm": 1600,
            "coolant_temp_c": 94,
            "vehicle_speed_kmh": 20,
            "engine_load_pct": 40,
        },
        {
            "time_seconds": 30,
            "rpm": 1800,
            "coolant_temp_c": 99,
            "vehicle_speed_kmh": 25,
            "engine_load_pct": 45,
        },
        {
            "time_seconds": 40,
            "rpm": 2000,
            "coolant_temp_c": 105,
            "vehicle_speed_kmh": 30,
            "engine_load_pct": 50,
        },
        {
            "time_seconds": 50,
            "rpm": 2200,
            "coolant_temp_c": 112,
            "vehicle_speed_kmh": 35,
            "engine_load_pct": 55,
        },
    ]

    return readings


def save_trace(readings):
    """Save sensor readings to a CSV file."""

    project_root = Path(__file__).resolve().parent.parent
    output_file = project_root / "data" / "vehicle_trace.csv"

    with output_file.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=readings[0].keys())
        writer.writeheader()
        writer.writerows(readings)

    print(f"Vehicle trace saved to: {output_file}")


def main():
    readings = generate_vehicle_trace()
    save_trace(readings)

    print(f"Total sensor readings: {len(readings)}")
    print("Data source: SYNTHETIC TEST DATA")


if __name__ == "__main__":
    main()
