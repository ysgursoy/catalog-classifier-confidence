# Catalog classifier confidence

A case study of how Artifica's hierarchical product classifier, built in 2022, handled competing category predictions, with a runnable example of its branch-selection rule.

The case study addresses four questions that arise when several models classify the same product within a category tree:

1. **Combining model responses.** How can the responses of different model types, such as image-, title-, description- and attribute-based models predicting over the same set of categories, be combined into a single prediction array?
2. **Selecting branches.** Given a prediction array, how can one decide whether it is sufficiently confident, and which categories warrant a prediction at the next level?
3. **Stopping.** When should iteration stop, and what is the deepest category prediction that remains sufficiently confident?
4. **Overall confidence.** How can the confidence of all iterations be summarised in a single score that an automated production pipeline can use to accept a result or route it to manual review?

The classifier walks the category tree from the root. At each branch, several models predict over the categories beneath it, and the classifier decides which of those categories to follow next or whether to stop. The top score alone does not determine how much work the classifier does: two products can each receive a top category score of 55% and still warrant different amounts of exploration, depending on how close the runner-up is. [PROJECT.md](PROJECT.md) describes the problem the classifier solved, the category tree it walked, a worked classification step, and [why close runner-up branches are kept](PROJECT.md#why-keep-a-second-branch).

## The decision rule

1. **Score each model response.** Each model returns a probability array, which is rescaled to percentages that sum to 100. The response's confidence weight, where `top` and `second` are its two highest scores, is

   ```math
   w = \sqrt{\frac{\text{top}}{\text{second}} - 1}
   ```

   It is 0 when the top two scores tie and grows as the leader pulls ahead.
2. **Calculate the prediction array.** The prediction array holds, for each category, the average of the models' scores for it, weighted by each response's confidence weight:

   ```math
   \text{score}(c) = \frac{\sum_i w_i \cdot s_i(c)}{\sum_i w_i}
   ```

   Here `s_i(c)` is model `i`'s score for category `c` and `w_i` is that response's confidence weight. A single model's response passes through unchanged, provided its top two scores are not tied, because

   ```math
   \frac{w \cdot s(c)}{w} = s(c)
   ```

   If they tie, its weight is 0 and every category's score becomes 0.
3. **Calculate the prediction's confidence.** The same weight `w` is computed on the prediction array, and its confidence is

   ```math
   \text{confidence} = \frac{w}{1 + w}
   ```

4. **Select branches.** Sort the prediction array from highest to lowest. Keep each category whose score divided by the leader's score is at least 0.4, and stop at the first one that is not. The comparison is inclusive: a runner-up at exactly 40% of the leader qualifies.
5. **Judge each level.** A level is confident when exactly one branch qualifies. When several branches qualify, each is explored and the next iteration continues only if exactly one of the resulting categories is confident. The root level's prediction is always recorded, so a fallback result exists.
6. **Stop and fall back.** Iteration ends when none or more than one of the returned categories is confident, or when no models exist for the categories under the selected branch. The result is then the last recorded confident prediction. If classification stopped at the root and the root itself had several qualifying branches, the result is flagged as not confident, so a caller can route it to review instead of applying it automatically.
7. **Combine iterations.** Each iteration `k`, whose confidence `c` is the confidence from step 3 for that iteration's prediction array, contributes the term

   ```math
   1 - k \, (1 - c)^k
   ```

   and the contributions are multiplied. For example, iteration confidences of 0.90, 0.88 and 0.76 give per-iteration terms of about 0.90, 0.97 and 0.96, and a combined confidence of about 0.84.

The 0.4 ratio was chosen by testing the rule on sample categorization cases and is stored as a configuration value rather than fixed in code.

## Run the example

The scripts use only the Python standard library and no external services.

`confidence_score.py` calculates each model's weight and confidence, and the combined prediction array:

```bash
python3 confidence_score.py
```

```text
Images       scores=[50, 30, 5, 5, 5, 5] w=0.816 confidence=0.449
Title        scores=[60, 20, 5, 5, 5, 5] w=1.414 confidence=0.586
Description  scores=[40, 35, 10, 5, 5, 5] w=0.378 confidence=0.274
Attributes   scores=[25, 45, 10, 10, 5, 5] w=0.894 confidence=0.472
Prediction   scores=[46.6, 30.3, 6.8, 6.3, 5.0, 5.0] w=0.732 confidence=0.423
```

`categories_to_be_explored.py` selects the categories whose models run next:

```bash
python3 categories_to_be_explored.py
```

```text
root prediction:
  Electronics        score  46.6  ratio 1.00  selected
  Home & Garden      score  30.3  ratio 0.65  selected
  Fashion            score   6.8  ratio 0.15  below threshold, stop
  -> not confident; next models: Electronics, Home & Garden
example 02:
  category 1         score  55.0  ratio 1.00  selected
  category 2         score  44.0  ratio 0.80  selected
  category 3         score   0.5  ratio 0.01  below threshold, stop
  -> not confident; next models: category 1, category 2
example 03:
  category 1         score  55.0  ratio 1.00  selected
  category 2         score  15.0  ratio 0.27  below threshold, stop
  -> confident; next models: category 1
boundary:
  category 1         score  55.0  ratio 1.00  selected
  category 2         score  22.0  ratio 0.40  selected
  category 3         score  12.0  ratio 0.22  below threshold, stop
  -> not confident; next models: category 1, category 2
no models for category 2:
  category 1         score  55.0  ratio 1.00  selected
  category 2         score  44.0  ratio 0.80  selected, no models
  category 3         score   0.5  ratio 0.01  below threshold, stop
  -> not confident; next models: category 1
```

The root prediction is the prediction array from the [sample classification step](PROJECT.md#a-sample-classification-step). The boundary case has a runner-up at exactly 40% of the leader, and it is kept. Ratios are computed with exact fractions, so the boundary is not affected by floating-point rounding. The last case shows that a qualifying category is skipped when no trained models exist for its subcategories.

Both scripts also accept your own arrays, for example `python3 categories_to_be_explored.py 55,44,0.5,0.5`.

Run the tests with:

```bash
python3 -m unittest -v
```

The scripts reproduce routing from supplied scores. Their output does not measure classifier performance.

## Contributions

Sadi Gürsoy designed and implemented the confidence layer as an abstract microservice described here: the confidence weighting of model responses, the branch-selection rule, the stopping and fallback logic, and the way confidence is combined across iterations. The Artifica team prepared the training data and trained the category models whose outputs the layer combines.

## Files

| File                                | Purpose                                                      |
| ----------------------------------- | ------------------------------------------------------------ |
| `PROJECT.md`                        | Problem, category tree, worked examples and design rationale |
| `confidence_score.py`               | Model weights, prediction array and confidence               |
| `categories_to_be_explored.py`      | Selecting the categories to explore from a prediction array  |
| `test_confidence_score.py`          | Tests for the confidence calculation                         |
| `test_categories_to_be_explored.py` | Tests for category selection, including the 40% boundary     |
| `assets/`                           | Decision-flow diagram used in `PROJECT.md`                   |

## License

Released under the [MIT License](LICENSE).
