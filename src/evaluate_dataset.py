
import random

from hypotheses import rank_hypotheses


def make_trace(start_temp, end_temp, load, seed):
    """Generate a synthetic vehicle temperature trace."""

    rng = random.Random(seed)
    readings = []

    for index in range(6):
        fraction = index / 5
        temperature = (
            start_temp
            + (end_temp - start_temp) * fraction
            + rng.uniform(-1.0, 1.0)
        )

        readings.append({
            "time_seconds": str(index * 10),
            "coolant_temp_c": f"{temperature:.2f}",
            "rpm": str(1000 + index * 150),
            "engine_load_pct": str(load),
        })

    return readings


def build_dataset():
    """Build labelled synthetic traces with varied temperatures."""

    dataset = []

    # Traces expected to remain below the configured threshold.
    for index in range(50):
        start = 75 + (index % 10)
        end = 90 + (index % 10)

        dataset.append({
            "name": f"Normal trace {index + 1}",
            "readings": make_trace(start, end, 25, index),
            "expected_elevated": False,
        })

    # Traces expected to cross the configured threshold.
    for index in range(50):
        start = 85 + (index % 6)
        end = 108 + (index % 10)

        dataset.append({
            "name": f"Elevated-temperature trace {index + 1}",
            "readings": make_trace(start, end, 30, 100 + index),
            "expected_elevated": True,
        })

    return dataset


def evaluate_dataset():
    dataset = build_dataset()

    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0

    for sample in dataset:
        result = rank_hypotheses(sample["readings"])

        predicted_elevated = (
            result["observed_condition"] == "Elevated coolant temperature"
        )
        expected_elevated = sample["expected_elevated"]

        if expected_elevated and predicted_elevated:
            true_positive += 1
        elif not expected_elevated and not predicted_elevated:
            true_negative += 1
        elif not expected_elevated and predicted_elevated:
            false_positive += 1
        else:
            false_negative += 1

    total = len(dataset)
    correct = true_positive + true_negative
    accuracy = correct / total * 100

    print("--- TorqueTrace Synthetic Dataset Evaluation ---")
    print(f"Total traces: {total}")
    print(f"Correct predictions: {correct}")
    print(f"Incorrect predictions: {total - correct}")
    print(f"Accuracy against synthetic labels: {accuracy:.2f}%")
    print()
    print(f"True positives:  {true_positive}")
    print(f"True negatives:  {true_negative}")
    print(f"False positives: {false_positive}")
    print(f"False negatives: {false_negative}")
    print()
    print(
        "Important: These are synthetic traces generated from predefined "
        "rules. This score measures agreement with synthetic labels, "
        "not real-world vehicle diagnostic accuracy."
    )


if __name__ == "__main__":
    evaluate_dataset()