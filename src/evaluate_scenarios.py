
from hypotheses import rank_hypotheses


def make_reading(time, temperature, rpm, load):
    return {
        "time_seconds": str(time),
        "coolant_temp_c": str(temperature),
        "rpm": str(rpm),
        "engine_load_pct": str(load),
    }


SCENARIOS = [
    {
        "name": "Normal temperature",
        "readings": [
            make_reading(0, 85, 900, 20),
            make_reading(10, 88, 1100, 25),
            make_reading(20, 91, 1300, 30),
        ],
        "expected_condition": (
            "No elevated temperature under the configured rule"
        ),
        "expected_first_hypothesis": None,
        "expected_anomaly": False,
    },
    {
        "name": "High temperature, low engine load",
        "readings": [
            make_reading(0, 88, 900, 15),
            make_reading(10, 100, 1100, 20),
            make_reading(20, 112, 1200, 25),
        ],
        "expected_condition": "Elevated coolant temperature",
        "expected_first_hypothesis": (
            "Cooling-system performance issue"
        ),
        "expected_anomaly": False,
    },
    {
        "name": "High temperature, high engine load",
        "readings": [
            make_reading(0, 88, 1200, 35),
            make_reading(10, 101, 1800, 55),
            make_reading(20, 112, 2200, 65),
        ],
        "expected_condition": "Elevated coolant temperature",
        "expected_first_hypothesis": (
            "Cooling-system performance issue"
        ),
        "expected_anomaly": False,
    },
    {
        "name": "Rapid temperature rise",
        "readings": [
            make_reading(0, 85, 1000, 25),
            make_reading(10, 100, 1200, 30),
            make_reading(20, 112, 1400, 35),
        ],
        "expected_condition": "Elevated coolant temperature",
        "expected_first_hypothesis": (
            "Cooling-system performance issue"
        ),
        "expected_anomaly": False,
    },
    {
        "name": "Sudden temperature spike",
        "readings": [
            make_reading(0, 85, 1000, 25),
            make_reading(10, 86, 1100, 25),
            make_reading(20, 115, 1100, 25),
            make_reading(30, 87, 1100, 25),
        ],
        "expected_condition": "Elevated coolant temperature",
        "expected_first_hypothesis": (
            "Cooling-system performance issue"
        ),
        "expected_anomaly": True,
    },
    {
        "name": "Gradual heating below threshold",
        "readings": [
            make_reading(0, 80, 900, 20),
            make_reading(30, 84, 1000, 22),
            make_reading(60, 88, 1100, 25),
            make_reading(90, 92, 1200, 28),
        ],
        "expected_condition": (
            "No elevated temperature under the configured rule"
        ),
        "expected_first_hypothesis": None,
        "expected_anomaly": False,
    },
    {
        "name": "Temperature cools after elevated peak",
        "readings": [
            make_reading(0, 90, 1500, 40),
            make_reading(10, 110, 1700, 45),
            make_reading(20, 100, 1400, 35),
        ],
        "expected_condition": "Elevated coolant temperature",
        "expected_first_hypothesis": (
            "Cooling-system performance issue"
        ),
        "expected_anomaly": False,
    },
]


def evaluate_scenarios():
    passed = 0

    print("--- TorqueTrace Scenario Evaluation ---\n")

    for scenario in SCENARIOS:
        result = rank_hypotheses(scenario["readings"])

        condition_ok = (
            result["observed_condition"]
            == scenario["expected_condition"]
        )

        expected_top = scenario["expected_first_hypothesis"]

        if expected_top is None:
            first_hypothesis_ok = not result["hypotheses"]
        else:
            first_hypothesis_ok = (
                bool(result["hypotheses"])
                and result["hypotheses"][0]["name"] == expected_top
            )

        anomaly_ok = (
            result["sensor_anomaly"]["suspected"]
            == scenario["expected_anomaly"]
        )

        scenario_passed = (
            condition_ok
            and first_hypothesis_ok
            and anomaly_ok
        )

        if scenario_passed:
            passed += 1

        status = "PASS" if scenario_passed else "FAIL"

        print(f"{status}: {scenario['name']}")
        print(f"  Observed: {result['observed_condition']}")
        print(
            "  Top hypothesis: "
            f"{result['hypotheses'][0]['name']}"
            if result["hypotheses"]
            else "  Top hypothesis: None supported by current rules"
        )
        print(
            "  Sensor anomaly suspected: "
            f"{result['sensor_anomaly']['suspected']}"
        )

        if not scenario_passed:
            if not condition_ok:
                print(
                    "  Expected condition: "
                    f"{scenario['expected_condition']}"
                )

            if not first_hypothesis_ok:
                print(
                    "  Expected top hypothesis: "
                    f"{expected_top}"
                )

            if not anomaly_ok:
                print(
                    "  Expected sensor anomaly: "
                    f"{scenario['expected_anomaly']}"
                )

        print()

    print(f"Scenarios passed: {passed}/{len(SCENARIOS)}")

    print(
        "Note: These synthetic scenarios test prototype rules, "
        "not real-world diagnostic accuracy."
    )

    return passed == len(SCENARIOS)


if __name__ == "__main__":
    if not evaluate_scenarios():
        raise SystemExit(1)