from hypotheses import rank_hypotheses


def make_trace(temperatures, loads=None):
    """Create a synthetic trace for stress testing."""

    if loads is None:
        loads = [30] * len(temperatures)

    readings = []

    for index, temperature in enumerate(temperatures):
        readings.append({
            "time_seconds": str(index * 10),
            "coolant_temp_c": str(temperature),
            "rpm": "1500",
            "engine_load_pct": str(loads[index]),
        })

    return readings


def run_stress_tests():
    """Exercise diagnostic rules with challenging synthetic traces."""

    cases = [
        {
            "name": "Just below threshold",
            "temperatures": [95, 98, 101, 103, 104, 104.9],
            "expected_elevated": False,
            "expected_anomaly": False,
        },
        {
            "name": "Exactly at threshold",
            "temperatures": [95, 98, 101, 103, 104, 105],
            "expected_elevated": True,
            "expected_anomaly": False,
        },
        {
            "name": "Just above threshold",
            "temperatures": [95, 98, 101, 103, 104, 105.1],
            "expected_elevated": True,
            "expected_anomaly": False,
        },
        {
            "name": "Noisy readings near threshold",
            "temperatures": [103, 104.8, 104.5, 105.2, 104.9, 105.1],
            "expected_elevated": True,
            "expected_anomaly": False,
        },
        {
            "name": "Sudden spike and fall",
            "temperatures": [90, 92, 120, 94, 95, 96],
            "expected_elevated": True,
            "expected_anomaly": True,
        },
        {
            "name": "Gradual heating below threshold",
            "temperatures": [80, 84, 88, 92, 96, 100],
            "expected_elevated": False,
            "expected_anomaly": False,
        },
    ]

    passed = 0

    print("--- TorqueTrace Stress Tests ---\n")

    for case in cases:
        result = rank_hypotheses(
            make_trace(case["temperatures"])
        )

        actual_elevated = (
            result["observed_condition"]
            == "Elevated coolant temperature"
        )

        actual_anomaly = result["sensor_anomaly"]["suspected"]

        elevated_ok = (
            actual_elevated == case["expected_elevated"]
        )
        anomaly_ok = (
            actual_anomaly == case["expected_anomaly"]
        )

        success = elevated_ok and anomaly_ok

        if success:
            passed += 1

        print(f"{'PASS' if success else 'FAIL'}: {case['name']}")
        print(f"  Highest temperature: {max(case['temperatures']):.1f} C")
        print(f"  Elevated condition: {actual_elevated}")
        print(f"  Sensor anomaly suspected: {actual_anomaly}")

        if not success:
            print(f"  Expected elevated: {case['expected_elevated']}")
            print(f"  Expected anomaly: {case['expected_anomaly']}")

        if result["hypotheses"]:
            print(
                "  Top hypothesis: "
                f"{result['hypotheses'][0]['name']}"
            )
        else:
            print("  Top hypothesis: None supported by current rules")

        print()

    print(f"Stress tests passed: {passed}/{len(cases)}")
    print(
        "Note: These are synthetic rule checks, not proof of "
        "real-world diagnostic accuracy."
    )


if __name__ == "__main__":
    run_stress_tests()
