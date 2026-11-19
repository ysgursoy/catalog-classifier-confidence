import math
import unittest

from confidence_score import EXAMPLE, confidence, prediction_array, weight


class ConfidenceScoreTest(unittest.TestCase):
    def test_weight(self):
        self.assertAlmostEqual(weight([60, 20, 5]), math.sqrt(2))
        self.assertAlmostEqual(weight([50, 30, 5]), math.sqrt(2 / 3))

    def test_tie_has_zero_confidence(self):
        self.assertEqual(weight([40, 40, 20]), 0)
        self.assertEqual(confidence([40, 40, 20]), 0)

    def test_order_does_not_matter(self):
        self.assertAlmostEqual(confidence([5, 30, 50]), confidence([50, 30, 5]))

    def test_zero_runner_up_is_fully_confident(self):
        self.assertEqual(confidence([100, 0, 0]), 1.0)

    def test_confidence_grows_with_gap(self):
        self.assertLess(confidence([40, 35, 25]), confidence([60, 20, 20]))

    def test_single_array_passes_through(self):
        for got, expected in zip(prediction_array([[50, 30, 20]]), [50, 30, 20]):
            self.assertAlmostEqual(got, expected)

    def test_example_prediction_array(self):
        combined = prediction_array(list(EXAMPLE.values()))
        self.assertAlmostEqual(sum(combined), 100)
        self.assertEqual(combined.index(max(combined)), 0)

    def test_all_ties_cannot_be_combined(self):
        with self.assertRaises(ValueError):
            prediction_array([[40, 40, 20], [30, 40, 40]])


if __name__ == "__main__":
    unittest.main()
