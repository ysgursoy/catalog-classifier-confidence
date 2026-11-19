import unittest

from categories_to_be_explored import categories_to_be_explored, scores_to_prediction


def explore(scores, models_available=None):
    return categories_to_be_explored(scores_to_prediction(scores), models_available)


class CategoriesToBeExploredTest(unittest.TestCase):
    def test_close_runner_up_explores_two_categories(self):
        qualifying, explored, is_confident = explore([55, 44, 0.5, 0.5])
        self.assertEqual(explored, ["category 1", "category 2"])
        self.assertFalse(is_confident)

    def test_distant_runner_ups_explore_leader_only(self):
        qualifying, explored, is_confident = explore([55, 15, 15, 15])
        self.assertEqual(explored, ["category 1"])
        self.assertTrue(is_confident)

    def test_runner_up_at_exactly_forty_percent_qualifies(self):
        self.assertEqual(explore([55, 22, 12, 11])[0], ["category 1", "category 2"])

    def test_runner_up_just_below_forty_percent_is_dropped(self):
        self.assertEqual(explore([55, 21.9, 12, 11])[0], ["category 1"])

    def test_input_order_does_not_matter(self):
        self.assertEqual(explore([44, 55])[0], ["category 2", "category 1"])

    def test_category_without_models_is_not_explored(self):
        qualifying, explored, is_confident = explore(
            [55, 44, 0.5, 0.5], models_available={"category 1"})
        self.assertEqual(qualifying, ["category 1", "category 2"])
        self.assertEqual(explored, ["category 1"])
        self.assertFalse(is_confident)


if __name__ == "__main__":
    unittest.main()
