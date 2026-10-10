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





        scenario_passed = condition_ok and first_hypothesis_ok

        if scenario_passed:
            passed += 1

        status = "PASS" if scenario_passed else "FAIL"

        print(f"{status}: {scenario['name']}")
        print(f"  Observed: {result['observed_condition']}")



        if result["hypotheses"]:
            print(
                "  Top hypothesis: "
                f"{result['hypotheses'][0]['name']}"
            )
        else:
            print("  Top hypothesis: None supported by current rules")




        if not scenario_passed:
            print(f"  Expected condition: {scenario['expected_condition']}")
            print(
                "  Expected top hypothesis: "
                f"{scenario['expected_first_hypothesis']}"
            )

        print()

    print(f"Scenarios passed: {passed}/{len(SCENARIOS)}")

    print(
        "Note: This evaluates synthetic test cases against "
        "prototype rules, not real-world diagnostic accuracy."
    )

    return passed == len(SCENARIOS)


if __name__ == "__main__":
    if not evaluate_scenarios():
        raise SystemExit(1)
