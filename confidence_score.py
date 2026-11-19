"""Confidence of probability arrays.

    w          = sqrt(top / second - 1)
    confidence = w / (1 + w)

`top` and `second` are the two highest scores. Several arrays are combined into
a prediction array by averaging each category's score, weighted by `w`.

Usage:
    python3 confidence_score.py                       # built-in example
    python3 confidence_score.py 50,30,5 60,20,5       # your own arrays
    python3 -m unittest test_confidence_score -v      # tests
"""

import math
import sys


def weight(scores):
    top, second = sorted(scores, reverse=True)[:2]
    if second == 0:
        return math.inf
    return math.sqrt(top / second - 1)


def confidence(scores):
    w = weight(scores)
    return 1.0 if math.isinf(w) else w / (1 + w)


def prediction_array(arrays):
    weights = [weight(a) for a in arrays]
    total = sum(weights)
    if total == 0:
        raise ValueError("every array has a tie between its top two scores")
    return [sum(w * a[i] for w, a in zip(weights, arrays)) / total
            for i in range(len(arrays[0]))]


EXAMPLE = {
    "Images": [50, 30, 5, 5, 5, 5],
    "Title": [60, 20, 5, 5, 5, 5],
    "Description": [40, 35, 10, 5, 5, 5],
    "Attributes": [25, 45, 10, 10, 5, 5],
}


def report(named_arrays):
    for name, scores in named_arrays.items():
        print(f"{name:<12} scores={scores} w={weight(scores):.3f} "
              f"confidence={confidence(scores):.3f}")
    if len(named_arrays) > 1:
        combined = prediction_array(list(named_arrays.values()))
        print(f"{'Prediction':<12} scores=[{', '.join(f'{s:.1f}' for s in combined)}] "
              f"w={weight(combined):.3f} confidence={confidence(combined):.3f}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        report({f"array {i + 1}": [float(x) for x in a.split(",")]
                for i, a in enumerate(args)})
    else:
        report(EXAMPLE)
