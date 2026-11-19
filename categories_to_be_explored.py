"""Select the categories to explore next from a prediction array.

The prediction array is sorted from highest to lowest score. A category
qualifies while score / leader >= 0.4; selection stops at the first category
below the threshold. The prediction is confident when exactly one category
qualifies. A qualifying category is explored only if trained models exist for
its subcategories.

The simulation reproduces routing from supplied scores. It does not measure
classifier performance.

Usage:
    python3 categories_to_be_explored.py                    # built-in examples
    python3 categories_to_be_explored.py 55,44,0.5,0.5      # your own arrays
    python3 -m unittest test_categories_to_be_explored -v   # tests
"""

import sys
from fractions import Fraction

from confidence_score import EXAMPLE, prediction_array

CONVERGENCE_THRESHOLD = Fraction(2, 5)  # 0.4, exact so boundary cases are exact

CATEGORIES = ["Electronics", "Home & Garden", "Fashion",
              "Sports & Outdoors", "Toys & Games", "Books & Media"]


def ranked_ratios(prediction):
    """Return (category, score, score / leader) sorted from highest score."""
    ranked = sorted(prediction.items(), key=lambda item: item[1], reverse=True)
    leader = Fraction(str(ranked[0][1]))
    return [(category, score, Fraction(str(score)) / leader)
            for category, score in ranked]


def qualifying_categories(prediction, threshold=CONVERGENCE_THRESHOLD):
    selected = []
    for category, _, ratio in ranked_ratios(prediction):
        if ratio < threshold:
            break
        selected.append(category)
    return selected


def categories_to_be_explored(prediction, models_available=None,
                              threshold=CONVERGENCE_THRESHOLD):
    """Return (qualifying, explored, is_confident) for one prediction array.

    `models_available` is the set of categories that have trained models for
    their subcategories. None means every category has them.
    """
    qualifying = qualifying_categories(prediction, threshold)
    explored = [c for c in qualifying
                if models_available is None or c in models_available]
    return qualifying, explored, len(qualifying) == 1


def report(name, prediction, models_available=None):
    qualifying, explored, is_confident = categories_to_be_explored(
        prediction, models_available)
    print(f"{name}:")
    for category, score, ratio in ranked_ratios(prediction):
        if category in qualifying:
            status = "selected" if category in explored else "selected, no models"
        else:
            status = "below threshold, stop"
        print(f"  {category:<18} score {score:5.1f}  ratio {float(ratio):.2f}  {status}")
        if category not in qualifying:
            break
    verdict = "confident" if is_confident else "not confident"
    print(f"  -> {verdict}; next models: {', '.join(explored) or 'none'}")


def scores_to_prediction(scores):
    return {f"category {i + 1}": s for i, s in enumerate(scores)}


def main(args):
    if args:
        for i, arg in enumerate(args):
            report(f"array {i + 1}", scores_to_prediction(
                [float(x) for x in arg.split(",")]))
        return

    combined = prediction_array(list(EXAMPLE.values()))
    report("root prediction", dict(zip(CATEGORIES, (round(s, 1) for s in combined))))
    report("example 02", scores_to_prediction([55, 44, 0.5, 0.5]))
    report("example 03", scores_to_prediction([55, 15, 15, 15]))
    report("boundary", scores_to_prediction([55, 22, 12, 11]))
    report("no models for category 2", scores_to_prediction([55, 44, 0.5, 0.5]),
           models_available={"category 1"})


if __name__ == "__main__":
    main(sys.argv[1:])
