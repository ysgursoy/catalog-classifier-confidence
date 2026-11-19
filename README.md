# Catalog classifier confidence

A case study of how Artifica's hierarchical product classifier handled competing category predictions, with a runnable example of its branch-selection rule.

**Two products each receive a top category score of 55%. Why does the classifier explore two branches for one product and only one for the other?**

| Example | Category scores (%) | Runner-up / leader | Qualifying branches |
| ------- | ------------------- | ------------------ | ------------------- |
| 02      | 55, 44, 0.5, 0.5    | 44/55 = 0.80       | First and second    |
| 03      | 55, 15, 15, 15      | 15/55 ≈ 0.27       | First only          |

Both rows are worked examples from the team's design workbook. Each row is a probability array in percent, like one model's response. A candidate branch qualifies when its score divided by the leading score is at least 0.4. The classifier applies this rule to the prediction array it calculates from all models' responses. The examples apply it to a single array for simplicity, and they assume that models are available to predict the next level under each qualifying branch.

## Project overview

[PROJECT.md](PROJECT.md) describes the problem the classifier solved, the category tree it walked, and a sample flow through one classification step.

In short, the classifier walks the category tree from the root. At each branch, several models predict over the categories beneath it, and the classifier decides which of those categories to follow next or whether to stop. Below, "exploring a branch" means following one of those candidate categories down the tree.

## Why keep a second branch

The classifier is hierarchical: it combines several models' predictions to choose a category, then the models trained for that category's children predict the next level, and so on. When the top score is not clearly ahead, committing to one branch early risks discarding the right answer. Keeping every plausible branch gives the next level a chance to resolve the ambiguity. The cost is an additional round of predictions from several models for each branch kept.

In example 02 the runner-up has 80% of the leader's score, so both branches are explored. In example 03 the runner-ups have about 27% of it, so the classifier follows the leader alone, even though the leading score is the same 55%. The top score alone does not determine how much work the classifier does. The gap to the runner-up does.

## Contributions

Sadi Gürsoy designed and implemented the confidence layer described here: the confidence weighting of model responses, the branch-selection rule, the stopping and fallback logic, and the way confidence is combined across iterations. The Artifica team prepared the training data and trained the category models whose outputs the layer combines.

## Training data

The team used category-level product counts and frequencies to balance how categories were represented in the training data. Whether this distribution improved accuracy has not been established; that would require comparing alternative training distributions on the same held-out products.

## The decision rule

1. **Score each model response.** Each model returns a probability array, which is rescaled to percentages that sum to 100. The response's confidence weight is the standard deviation of `[1, top/second]`, where `top` and `second` are its two highest scores. This equals `(top/second - 1) / √2`. It is 0 when the top two scores tie and grows as the leader pulls ahead.
2. **Calculate the prediction score.** For each category, the prediction score is the average of the models' scores for it, weighted by each response's confidence weight. A single model's response passes through unchanged.
3. **Calculate the prediction's confidence.** The same weight `w` is computed on the prediction array, and its confidence is `w / (1 + w)`.
4. **Select branches.** Sort the prediction array from highest to lowest. Keep each category whose score divided by the leader's score is at least 0.4, and stop at the first one that is not. The comparison is inclusive: a runner-up at exactly 40% of the leader qualifies.
5. **Judge each level.** A level is confident when exactly one branch qualifies. There is no fixed cutoff on the confidence value itself. When several branches qualify, each is explored and the next iteration continues only if exactly one of the resulting categories is confident. The root level's prediction is always recorded, so a fallback result exists.
6. **Stop and fall back.** Iteration ends when none or more than one of the returned categories is confident, or when no models exist for the categories under the selected branch. The result is then the last recorded confident prediction. If classification stopped at the root and the root itself had several qualifying branches, the result is flagged as not confident, so a caller can route it to review instead of applying it automatically.
7. **Combine iterations.** Each iteration `k`, whose confidence `c` is the confidence from step 3 for that iteration's prediction array, contributes `1 - k * (1 - c)^k`, and the contributions are multiplied. For example, iteration confidences of 0.90, 0.88 and 0.76 give per-iteration terms of about 0.90, 0.97 and 0.96, and a combined confidence of about 0.84.

The 0.4 ratio is a configuration value, not fixed in code.

## Run the example

The example uses only the Python standard library and no external services.

```bash
python3 example.py
```

Expected output:

```text
example 02: scores=[55, 44, 0.5, 0.5] runner-up/leader=0.80
  explore branch 1 (score 55, ratio 1.00)
  explore branch 2 (score 44, ratio 0.80)
  -> 2 branch(es) explored
example 03: scores=[55, 15, 15, 15] runner-up/leader=0.27
  explore branch 1 (score 55, ratio 1.00)
  -> 1 branch(es) explored
example boundary: scores=[55, 22, 12, 11] runner-up/leader=0.40
  explore branch 1 (score 55, ratio 1.00)
  explore branch 2 (score 22, ratio 0.40)
  -> 2 branch(es) explored
```

The third case checks the boundary: the runner-up is exactly 40% of the leader and is kept. Ratios are computed with exact fractions, so the boundary is not affected by floating-point rounding.

Run the tests with:

```bash
python3 -m unittest -v
```

The example reproduces routing from supplied scores. Its output does not measure classifier performance.

## Evidence available

The surviving development logs contain 373 scored prediction records across 26 distinct products. Of those records, 224 had confidence scores of at least 0.7. This count describes how often high scores occurred, not whether those predictions were correct. Repeated products and missing correctness labels limit what can be inferred. Production automation rate, accuracy and calibration were not measured in the recovered records.

## Proposed evaluation

On independently labeled products, how does the full decision rule compare with accepting predictions by top score alone?

1. Choose the convergence threshold and the top-score cutoff on development products only.
2. On held-out products, set each method to accept the same fraction of predictions, and compare the error rate among accepted predictions.
3. Count downstream model calls per product to measure the cost of exploring additional branches.

This evaluation has not been run.

## Files

| File               | Purpose                                      |
| ------------------ | -------------------------------------------- |
| `PROJECT.md`       | Problem, category tree and a sample flow     |
| `example.py`       | Branch-selection rule and the worked examples |
| `test_example.py`  | Tests, including the 40% boundary            |
| `assets/`          | Decision-flow diagram used in `PROJECT.md`   |

## License

Released under the [MIT License](LICENSE).
