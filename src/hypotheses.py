def rank_hypotheses(readings):
    """
    Rank diagnostic possibilities using transparent prototype rules.

    Scores are heuristic priorities, not probabilities or
    validated estimates of real vehicle faults.
    """

    if not readings:
        raise ValueError("Cannot analyse an empty vehicle trace.")

    required_fields = [
        "time_seconds",
        "coolant_temp_c",
        "rpm",
        "engine_load_pct",
    ]

    # Validate the fields needed by this module.
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

            if not __import__("math").isfinite(value):
                raise ValueError(
                    f"Reading {index}: '{field}' must be finite."
                )

    temperatures = [
        float(row["coolant_temp_c"]) for row in readings
    ]
    loads = [
        float(row["engine_load_pct"]) for row in readings
    ]
    rpms = [
        float(row["rpm"]) for row in readings
    ]

    highest_temp = max(temperatures)
    highest_load = max(loads)
    highest_rpm = max(rpms)
    temperature_rise = temperatures[-1] - temperatures[0]

    hypotheses = []

    # Hypothesis 1: elevated engine load may contribute.
    load_score = 0
    load_evidence = []

    if highest_load >= 50:
        load_score += 1
        load_evidence.append(
            f"Engine load reached {highest_load:.1f}%."
        )

    if highest_temp >= 105 and highest_load >= 50:
        load_score += 1
        load_evidence.append(
            "Elevated temperature occurred in a trace "
            "that also recorded high engine load."
        )

    hypotheses.append({
        "name": "Engine load may be contributing",
        "score": load_score,
        "evidence": load_evidence or [
            "The configured rules found no strong high-load signal."
        ],
        "next_test": (
            "Compare temperature behaviour during similar driving "
            "conditions with lower engine load."
        ),
    })

    # Hypothesis 2: cooling-system performance warrants investigation.
    cooling_score = 0
    cooling_evidence = []

    if highest_temp >= 105:
        cooling_score += 2
        cooling_evidence.append(
            f"Coolant temperature reached {highest_temp:.1f} C."
        )

    if temperature_rise >= 15:
        cooling_score += 1
        cooling_evidence.append(
            f"Temperature increased by {temperature_rise:.1f} C "
            "over the recorded trace."
        )

    hypotheses.append({
        "name": "Cooling-system performance issue",
        "score": cooling_score,
        "evidence": cooling_evidence or [
            "The configured rules found no strong temperature signal."
        ],
        "next_test": (
            "Verify the temperature reading independently, then "
            "inspect coolant level and check the cooling system "
            "using the vehicle manufacturer's service procedure."
        ),
    })

    # A score is a rule-based investigation priority, not a probability.
    hypotheses.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return {
        "observed_condition": (
            "Elevated coolant temperature"
            if highest_temp >= 105
            else "No elevated temperature under the configured rule"
        ),
        "highest_temperature_c": highest_temp,
        "highest_engine_load_pct": highest_load,
        "highest_rpm": highest_rpm,
        "hypotheses": hypotheses,
        "score_note": (
            "Scores are prototype rule priorities, not fault "
            "probabilities or validated diagnostic confidence."
        ),
    }


def print_report(result):
    """Print a readable hypothesis report."""

    print("\n--- TorqueTrace Hypothesis Report ---")
    print(f"Observed condition: {result['observed_condition']}")
    print(
        f"Highest coolant temperature: "
        f"{result['highest_temperature_c']:.1f} C"
    )
    print(
        f"Highest engine load: "
        f"{result['highest_engine_load_pct']:.1f}%"
    )
    print(f"Highest RPM: {result['highest_rpm']:.0f}")

    print("\nRanked investigation priorities:")

    for rank, hypothesis in enumerate(result["hypotheses"], start=1):
        print(
            f"\n{rank}. {hypothesis['name']} "
            f"(rule score: {hypothesis['score']})"
        )

        print("   Evidence:")
        for item in hypothesis["evidence"]:
            print(f"   - {item}")

        print(f"   Next test: {hypothesis['next_test']}")

    print(f"\nNote: {result['score_note']}")


if __name__ == "__main__":
    from diagnostics import load_vehicle_trace

    trace = load_vehicle_trace()
    report = rank_hypotheses(trace)
    print_report(report)
