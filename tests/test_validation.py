import unittest

from tracker.validation import amount, calendar_date, validate_meal


class ValidationTests(unittest.TestCase):
    def test_numeric_notation_and_bounds(self):
        for value, expected in (("0", 0), ("0.5", 50), ("100.25", 10025),
                                (" 1.20 ", 120), ("92233720368547758.07", 2**63 - 1)):
            with self.subTest(value=value):
                self.assertEqual(amount(value), expected)
        for value in ("", "-1", ".5", "+1", "1.", "1e2", "1.234", "1.230", "NaN",
                      "Infinity", "92233720368547758.08", "9" * 1000):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    amount(value)
        with self.assertRaises(ValueError):
            amount("0", positive=True)
        self.assertEqual(amount("0.01", positive=True), 1)

    def test_dates(self):
        self.assertEqual(calendar_date("2024-02-29"), "2024-02-29")
        for value in ("2025-02-29", "2026-2-1", "20261103", "", "2026-13-01"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                calendar_date(value)

    def test_meal_fields(self):
        fields = dict(meal_date="2026-11-03", food_name=" Oats ", category="Breakfast",
                      calories="100.25", protein="0")
        values, errors = validate_meal(fields)
        self.assertFalse(errors)
        self.assertEqual(values["food_name"], "Oats")
        self.assertEqual(values["calories_hundredths"], 10025)
        for field in fields:
            with self.subTest(field=field):
                _, errors = validate_meal({**fields, field: " "})
                self.assertIn(field, errors)
        for category in ("Breakfast", "Lunch", "Dinner", "Snacks"):
            self.assertFalse(validate_meal({**fields, "category": category})[1])
        self.assertIn("category", validate_meal({**fields, "category": "Brunch"})[1])