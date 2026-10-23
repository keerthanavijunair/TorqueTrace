
from hypotheses import rank_hypotheses


def make_trace(temperatures, loads=None, interval_seconds=10):
    """Create a synthetic trace for stress testing."""

    if loads is None:
        loads = [30] * len(temperatures)

    readings = []

    for index, temperature in enumerate(temperatures):
        readings.append({
            "time_seconds": str(index * interval_seconds),
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
            "expected_top_hypothesis": None,
        },
        {
            "name": "Exactly at threshold",
            "temperatures": [95, 98, 101, 103, 104, 105],
            "expected_elevated": True,
            "expected_anomaly": False,
            "expected_top_hypothesis": "Cooling-system performance issue",
        },
        {
            "name": "Just above threshold",
            "temperatures": [95, 98, 101, 103, 104, 105.1],
            "expected_elevated": True,
            "expected_anomaly": False,
            "expected_top_hypothesis": "Cooling-system performance issue",
        },
        {
            "name": "Noisy readings near threshold",
            "temperatures": [103, 104.8, 104.5, 105.2, 104.9, 105.1],
            "expected_elevated": True,
            "expected_anomaly": False,
            "expected_top_hypothesis": "Cooling-system performance issue",
        },
        {
            "name": "Sudden spike and fall",
            "temperatures": [90, 92, 120, 94, 95, 96],
            "expected_elevated": True,
            "expected_anomaly": True,
            "expected_top_hypothesis": "Cooling-system performance issue",
        },
        {
            "name": "Gradual heating below threshold",
            "temperatures": [80, 84, 88, 92, 96, 100],
            "interval_seconds": 60,
            "expected_elevated": False,
            "expected_anomaly": False,
            "expected_top_hypothesis": None,
        },
    ]

    passed = 0

    print("--- TorqueTrace Stress Tests ---\n")

    for case in cases:
        result = rank_hypotheses(
            make_trace(
                case["temperatures"],
                interval_seconds=case.get("interval_seconds", 10),
            )
        )

        actual_elevated = (
            result["observed_condition"]
            == "Elevated coolant temperature"
        )

        actual_anomaly = result["sensor_anomaly"]["suspected"]

        actual_top_hypothesis = (
            result["hypotheses"][0]["name"]
            if result["hypotheses"]
            else None
        )

        elevated_ok = (
            actual_elevated == case["expected_elevated"]
        )
        anomaly_ok = (
            actual_anomaly == case["expected_anomaly"]
        )
        hypothesis_ok = (
            actual_top_hypothesis
            == case["expected_top_hypothesis"]
        )

        success = elevated_ok and anomaly_ok and hypothesis_ok

        if success:
            passed += 1

        print(f"{'PASS' if success else 'FAIL'}: {case['name']}")
        print(
            f"  Highest temperature: "
            f"{max(case['temperatures']):.1f} C"
        )
        print(f"  Elevated condition: {actual_elevated}")
        print(f"  Sensor anomaly suspected: {actual_anomaly}")
        print(f"  Expected top hypothesis: {case['expected_top_hypothesis']}")
        print(f"  Actual top hypothesis: {actual_top_hypothesis}")

        if not success:
            print(f"  Expected elevated: {case['expected_elevated']}")
            print(f"  Expected anomaly: {case['expected_anomaly']}")
            print(f"  Hypothesis ranking correct: {hypothesis_ok}")

        print()

    print(f"Stress tests passed: {passed}/{len(cases)}")
    print(
        "Note: These are synthetic rule checks, not proof of "
        "real-world diagnostic accuracy."
    )


if __name__ == "__main__":
    run_stress_tests()
