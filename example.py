"""Branch selection for a hierarchical product classifier.

Given the category scores a model assigns to one product, a candidate branch
qualifies when its score divided by the leading score is at least 0.4. Every
qualifying branch is explored by the next-level model.

The example reproduces routing from supplied scores. It does not measure
classifier performance.
"""

from fractions import Fraction

CONVERGENCE_CONSTANT = Fraction(2, 5)  # 0.4, kept exact so boundary cases are exact


def qualifying_branches(scores, constant=CONVERGENCE_CONSTANT):
    """Return (index, score) pairs for branches whose score / leader >= constant.

    Scores are processed from highest to lowest and the loop stops at the first
    branch that does not qualify. Comparison is inclusive.
    """
    exact = [Fraction(str(s)) for s in scores]
    ranked = sorted(enumerate(exact), key=lambda item: item[1], reverse=True)
    leader = ranked[0][1]
    selected = []
    for index, score in ranked:
        if score / leader >= constant:
            selected.append((index, score))
        else:
            break
    return selected


EXAMPLES = {
    "02": [55, 44, 0.5, 0.5],
    "03": [55, 15, 15, 15],
    "boundary": [55, 22, 12, 11],  # runner-up is exactly 40% of the leader
}


def main():
    for name, scores in EXAMPLES.items():
        leader = max(scores)
        selected = qualifying_branches(scores)
        ratio = float(Fraction(str(sorted(scores, reverse=True)[1])) / Fraction(str(leader)))
        print(f"example {name}: scores={scores} runner-up/leader={ratio:.2f}")
        for index, score in selected:
            print(f"  explore branch {index + 1} (score {float(score):g}, "
                  f"ratio {float(score / Fraction(str(leader))):.2f})")
        print(f"  -> {len(selected)} branch(es) explored")


if __name__ == "__main__":
    main()
