import unittest

from example import qualifying_branches


class BranchSelectionTest(unittest.TestCase):
    def indexes(self, scores):
        return [index for index, _ in qualifying_branches(scores)]

    def test_example_02_explores_two_branches(self):
        self.assertEqual(self.indexes([55, 44, 0.5, 0.5]), [0, 1])

    def test_example_03_explores_one_branch(self):
        self.assertEqual(self.indexes([55, 15, 15, 15]), [0])

    def test_runner_up_at_exactly_forty_percent_qualifies(self):
        self.assertEqual(self.indexes([55, 22, 12, 11]), [0, 1])

    def test_runner_up_just_below_forty_percent_is_dropped(self):
        self.assertEqual(self.indexes([55, 21.9, 12, 11]), [0])

    def test_input_order_does_not_matter(self):
        self.assertEqual(self.indexes([44, 55]), [1, 0])


if __name__ == "__main__":
    unittest.main()
