import unittest

from tracker.nutrition import format_amount, daily_totals, progress


class FormattingTests(unittest.TestCase):
    def test_exact_formatter(self):
        for value, expected in ((0, "0"), (50, "0.5"), (10025, "100.25"), (120, "1.2"),
                                (2**63 - 1, "92233720368547758.07")):
            with self.subTest(value=value):
                self.assertEqual(format_amount(value), expected)


class TotalsTests(unittest.TestCase):
    def test_ac07_ac08_known_sums(self):
        meals = [{"calories_hundredths": calories, "protein_hundredths": protein}
                 for calories, protein in ((30000, 1200), (45000, 2550), (60000, 4000), (15000, 750))]
        self.assertEqual(daily_totals(meals), {"calories": 150000, "protein": 8500})

    def test_ac10_ac23_zero_decimals_and_large_totals(self):
        self.assertEqual(daily_totals([]), {"calories": 0, "protein": 0})
        meals = [{"calories_hundredths": value, "protein_hundredths": value} for value in (10, 20)]
        self.assertEqual(format_amount(daily_totals(meals)["calories"]), "0.3")
        self.assertEqual(daily_totals([{"calories_hundredths": 2**63-1, "protein_hundredths": 0}] * 2)["calories"], 2*(2**63-1))


class ProgressTests(unittest.TestCase):
    def test_ac13_ac14_ac15_states(self):
        below = progress(150000, 200000)
        self.assertEqual((below["status"], below["remaining"], below["fill"]), ("below", 50000, "75"))
        equal = progress(200000, 200000)
        self.assertEqual((equal["status"], equal["remaining"], equal["fill"]), ("reached", 0, "100"))
        above = progress(220000, 200000)
        self.assertEqual((above["status"], above["exceeded"], above["fill"]), ("exceeded", 20000, "100"))

    def test_ac10_ac17_missing_and_zero_intake(self):
        self.assertEqual(progress(0, 100)["remaining"], 100)
        self.assertEqual(progress(0, 100)["fill"], "0")
        self.assertEqual(progress(100, None)["status"], "missing_target")
        self.assertIsNone(progress(100, None)["fill"])

    def test_near_equality_is_not_rounded_into_reached(self):
        self.assertEqual(progress(200001, 200000)["status"], "exceeded")
        self.assertEqual(progress(199999, 200000)["status"], "below")