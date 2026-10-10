
try:
    from .validation import validate_vehicle_trace
except ImportError:
    from validation import validate_vehicle_trace


# Prototype screening rules, not universal vehicle specifications.
ELEVATED_TEMP_C = 105
HIGH_ENGINE_LOAD_PCT = 50
RAPID_RISE_C_PER_MIN = 10
SIGNIFICANT_TEMP_RISE_C = 15


def rank_hypotheses(readings):
    """
    Rank diagnostic possibilities using transparent prototype rules.

    Scores represent investigation priority, not fault probabilities.
    Synthetic thresholds require further validation before real-world use.
    """

    validate_vehicle_trace(
        readings,
        required_fields=(
            "time_seconds",
            "coolant_temp_c",
            "rpm",
            "engine_load_pct",
        ),
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
    times = [
        float(row["time_seconds"]) for row in readings
    ]

    highest_temp = max(temperatures)
    highest_load = max(loads)
    highest_rpm = max(rpms)

    temperature_rise = temperatures[-1] - temperatures[0]
    elapsed_time = times[-1] - times[0]

    if elapsed_time <= 0:
        raise ValueError(
            "Elapsed time must be positive to analyse temperature trends."
        )

    temperature_rise_rate = (
        temperature_rise / elapsed_time * 60
    )

    elevated_temp = highest_temp >= ELEVATED_TEMP_C
    high_load = highest_load >= HIGH_ENGINE_LOAD_PCT
    
    rapid_rise = (
        temperature_rise >= SIGNIFICANT_TEMP_RISE_C
        and temperature_rise_rate >= RAPID_RISE_C_PER_MIN
    )

    hypotheses = []

    # Hypothesis 1: engine load may be contributing.
    load_score = 0
    load_evidence = []

    if high_load:
        load_score += 1
        load_evidence.append(
            f"Engine load reached {highest_load:.1f}%, "
            "meeting the prototype's high-load rule."
        )

    if elevated_temp and high_load:
        load_score += 1
        load_evidence.append(
            "Elevated coolant temperature and high engine load "
            "were both observed in this trace. Their co-occurrence "
            "does not establish causation."
        )

    if elevated_temp and not high_load:
        load_evidence.append(
            f"Peak engine load was {highest_load:.1f}%, below the "
            "configured high-load threshold. High load alone is "
            "therefore not a strong explanation in this trace."
        )

    hypotheses.append({
        "name": "Engine load may be contributing",
        "score": load_score,
        "evidence": load_evidence or [
            "The configured rules found no strong high-load signal."
        ],
        "next_test": (
            "Compare temperature traces from similar operating "
            "conditions at different engine loads."
            if high_load
            else
            "Check engine load and temperature sensor readings, "
            "then compare against a trace recorded under higher load."
        ),
    })

    # Hypothesis 2: cooling-system performance warrants investigation.
    cooling_score = 0
    cooling_evidence = []

    if elevated_temp:
        cooling_score += 2
        cooling_evidence.append(
            f"Coolant temperature reached {highest_temp:.1f} C, "
            "meeting the configured elevated-temperature rule."
        )

    if temperature_rise >= SIGNIFICANT_TEMP_RISE_C:
        cooling_score += 1
        cooling_evidence.append(
            f"Temperature rose by {temperature_rise:.1f} C "
            "over the recorded trace."
        )

    if rapid_rise:
        cooling_score += 1
        cooling_evidence.append(
            f"Temperature rose at {temperature_rise_rate:.1f} C/min, "
            "above the prototype's rapid-rise screening threshold."
        )

    if elevated_temp and not high_load:
        cooling_evidence.append(
            "Elevated temperature occurred without meeting the "
            "configured high-load rule. This supports investigating "
            "the cooling system, but does not identify a specific fault."
        )
    elif elevated_temp and high_load:
        cooling_evidence.append(
            "High engine load may contribute to heat generation. "
            "Further measurements are needed to assess cooling performance."
        )

    if rapid_rise:
        cooling_next_test = (
            "Check the temperature sensor against an independent "
            "measurement, verify the time series, and follow the "
            "manufacturer's procedure for inspecting the cooling system."
        )
    elif elevated_temp and not high_load:
        cooling_next_test = (
            "Verify the temperature reading, then inspect coolant "
            "level and check the cooling system using the vehicle "
            "manufacturer's service procedure."
        )
    elif elevated_temp and high_load:
        cooling_next_test = (
            "Compare temperature behaviour at similar speeds and "
            "different loads, verify sensor readings, and inspect "
            "the cooling system according to the service procedure."
        )
    else:
        cooling_next_test = (
            "Continue monitoring coolant temperature over a longer "
            "trace under documented operating conditions."
        )

    hypotheses.append({
        "name": "Cooling-system performance issue",
        "score": cooling_score,
        "evidence": cooling_evidence or [
            "The configured rules found no strong temperature signal."
        ],
        "next_test": cooling_next_test,
    })

    # Highest rule score appears first. Ties preserve insertion order.
    hypotheses.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    hypotheses = [
        hypothesis
        for hypothesis in hypotheses
        if hypothesis["score"] > 0
    ]

    return {
        "observed_condition": (
            "Elevated coolant temperature"
            if elevated_temp
            else "No elevated temperature under the configured rule"
        ),
        "highest_temperature_c": highest_temp,
        "highest_engine_load_pct": highest_load,
        "highest_rpm": highest_rpm,
        "temperature_rise_c": temperature_rise,
        "temperature_rise_c_per_minute": temperature_rise_rate,
        "hypotheses": hypotheses,
        "score_note": (
            "Scores are prototype rule priorities, not fault "
            "probabilities or validated diagnostic confidence. "
            "Thresholds are illustrative and are not universal "
            "vehicle-manufacturer specifications."
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
    print(
        f"Temperature rise: {result['temperature_rise_c']:.1f} C"
    )
    print(
        "Temperature rise rate: "
        f"{result['temperature_rise_c_per_minute']:.1f} C/min"
    )

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
    try:
        from .diagnostics import load_vehicle_trace
    except ImportError:
        from diagnostics import load_vehicle_trace

    trace = load_vehicle_trace()
    report = rank_hypotheses(trace)
    print_report(report)