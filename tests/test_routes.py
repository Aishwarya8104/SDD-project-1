import sqlite3
from unittest.mock import patch

from tests import AppTestCase


class MealRouteTests(AppTestCase):
    def test_ac01_ac02_add_and_view(self):
        self.add_meal(calories="100.25", protein="0.75")
        response = self.client.get("/?date=2026-11-03")
        self.assertEqual(response.status_code, 200)
        for expected in ("Oats", "Breakfast", "100.25", "0.75"):
            self.assertIn(expected, response.get_data(as_text=True))
        self.assertNotIn("Oats", self.client.get("/?date=2026-11-04").get_data(as_text=True))

    def test_ac03_ac04_ac19_edit_move_delete(self):
        self.add_meal()
        fields = self.form("/meals/1/edit")
        self.assertEqual(fields["calories"], "300")
        fields.update(food_name="Porridge", meal_date="2026-11-04", category="Lunch",
                      calories="350", protein="15")
        response = self.client.post("/meals/1/edit", data=fields)
        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.location.endswith("date=2026-11-04"))
        self.assertNotIn("Porridge", self.client.get("/?date=2026-11-03").get_data(as_text=True))
        fields = self.form("/?date=2026-11-04")
        response = self.client.post("/meals/1/delete", data=fields)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(self.query("SELECT * FROM meals"), [])

    def test_ac05_ac06_invalid_values_preserve_form_and_database(self):
        fields = self.form("/meals/new")
        fields.update(meal_date="2026-11-03", food_name="Oats", category="Breakfast",
                      calories="0", protein="0")
        cases = {"food_name": ("", "  "), "category": ("", "Brunch"),
                 "meal_date": ("2025-02-29", ""),
                 "calories": ("", "-1", ".5", "+1", "1.", "1e2", "1.234", "1.230", "NaN", "Infinity"),
                 "protein": ("", "-1", "1.234")}
        for name, values in cases.items():
            for value in values:
                with self.subTest(field=name, value=value):
                    response = self.client.post("/meals/new", data={**fields, name: value})
                    self.assertEqual(response.status_code, 422)
                    self.assertIn('id="error-' + name + '"', response.get_data(as_text=True))
                    self.assertIn(fields["submission_key"], response.get_data(as_text=True))
        self.assertEqual(self.query("SELECT * FROM meals"), [])
        self.assertEqual(self.client.post("/meals/new", data=fields).status_code, 303)

    def test_ac20_categories_and_distinct_identical_meals(self):
        for category in ("Breakfast", "Lunch", "Dinner", "Snacks"):
            self.add_meal(category=category)
        self.add_meal()
        self.assertEqual(len(self.query("SELECT * FROM meals")), 5)

    def test_csrf_dates_missing_ids_and_escape(self):
        self.assertEqual(self.client.post("/meals/new", data={}).status_code, 400)
        self.assertEqual(self.client.get("/?date=bad").status_code, 400)
        self.assertEqual(self.client.get("/meals/900/edit").status_code, 404)
        self.add_meal(food_name='<script>alert("x")</script>')
        page = self.client.get("/?date=2026-11-03").get_data(as_text=True)
        self.assertNotIn('<script>alert', page)
        self.assertIn("&lt;script&gt;", page)
        self.assertEqual(self.client.get("/meals/1/delete").status_code, 405)

    def test_ac21_replay_conflict_and_replay_after_delete(self):
        fields = self.add_meal()
        self.assertEqual(self.client.post("/meals/new", data=fields).status_code, 303)
        self.assertEqual(len(self.query("SELECT * FROM meals")), 1)
        self.assertEqual(self.client.post("/meals/new", data={**fields, "food_name": "Changed"}).status_code, 409)
        deletion = self.form("/?date=2026-11-03")
        self.assertEqual(self.client.post("/meals/1/delete", data=deletion).status_code, 303)
        self.assertEqual(self.client.post("/meals/1/delete", data=deletion).status_code, 303)
        self.assertEqual(self.client.post("/meals/new", data=fields).status_code, 303)
        self.assertEqual(self.query("SELECT * FROM meals"), [])

    def test_ac21_read_failure_is_not_empty_day(self):
        with patch("tracker.db.list_meals", side_effect=sqlite3.OperationalError("private SQL"), create=True):
            response = self.client.get("/?date=2026-11-03")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("No meals recorded", response.get_data(as_text=True))
        self.assertNotIn("private SQL", response.get_data(as_text=True))
        self.assertIn('href="/?date=2026-11-03"', response.get_data(as_text=True))

    def test_ac21_write_failure_preserves_key_for_retry(self):
        fields = self.form("/meals/new")
        fields.update(meal_date="2026-11-03", food_name="Oats", category="Breakfast",
                      calories="100", protein="5")
        with patch("tracker.db.save_meal", side_effect=sqlite3.OperationalError("private SQL"), create=True):
            response = self.client.post("/meals/new", data=fields)
        self.assertEqual(response.status_code, 503)
        self.assertIn(fields["submission_key"], response.get_data(as_text=True))
        self.assertEqual(self.query("SELECT * FROM meals"), [])
        self.assertEqual(self.client.post("/meals/new", data=fields).status_code, 303)


class TotalsRouteTests(AppTestCase):
    def test_ac07_ac08_ac09_daily_totals_and_isolation(self):
        for category, calories, protein in (("Breakfast", "300", "12"), ("Lunch", "450", "25.5"),
                                             ("Dinner", "600", "40"), ("Snacks", "150", "7.5")):
            self.add_meal(category=category, calories=calories, protein=protein)
        self.add_meal(meal_date="2026-11-04", calories="700", protein="30")
        page = self.client.get("/?date=2026-11-03").get_data(as_text=True)
        self.assertIn('id="total-calories">1500</strong>', page)
        self.assertIn('id="total-protein">85</strong>', page)
        page = self.client.get("/?date=2026-11-04").get_data(as_text=True)
        self.assertIn('id="total-calories">700</strong>', page)

    def test_ac16_ac19_ac23_modifications_and_decimal_totals(self):
        self.add_meal(calories="0.1", protein="0.1")
        self.add_meal(calories="0.2", protein="0.2")
        self.assertIn('id="total-calories">0.3</strong>', self.client.get("/?date=2026-11-03").get_data(as_text=True))
        fields = self.form("/meals/1/edit")
        fields.update(meal_date="2026-11-04", calories="100", protein="5")
        self.assertEqual(self.client.post("/meals/1/edit", data=fields).status_code, 303)
        self.assertIn('id="total-calories">0.2</strong>', self.client.get("/?date=2026-11-03").get_data(as_text=True))
        self.assertIn('id="total-calories">100</strong>', self.client.get("/?date=2026-11-04").get_data(as_text=True))
        fields = self.form("/?date=2026-11-03")
        self.assertEqual(self.client.post("/meals/2/delete", data=fields).status_code, 303)
        self.assertIn('id="total-calories">0</strong>', self.client.get("/?date=2026-11-03").get_data(as_text=True))


class TargetRouteTests(AppTestCase):
    def test_ac11_targets_and_invalid_updates(self):
        self.set_targets("2000.25", "100.75")
        before = self.query("SELECT * FROM nutrition_targets")
        fields = self.form("/targets")
        for field in ("calorie_target", "protein_target"):
            for value in ("", "0", "-1", ".5", "+1", "1.", "1e2", "1.234", "1.230", "NaN", "Infinity"):
                with self.subTest(field=field, value=value):
                    response = self.client.post("/targets", data={**fields, field: value})
                    self.assertEqual(response.status_code, 422)
                    self.assertIn('id="error-' + field + '"', response.get_data(as_text=True))
                    self.assertEqual(self.query("SELECT * FROM nutrition_targets"), before)
        self.set_targets("0.5", "0.01")

    def test_ac12_ac13_ac14_ac15_comparison_states(self):
        self.add_meal(calories="1500", protein="75")
        self.set_targets()
        page = self.client.get("/?date=2026-11-03").get_data(as_text=True)
        self.assertIn("500 kcal remaining", page)
        self.assertIn("25 g remaining", page)
        self.set_targets("1800", "90")
        page = self.client.get("/?date=2026-11-03").get_data(as_text=True)
        self.assertIn("300 kcal remaining", page)
        self.assertIn("15 g remaining", page)
        self.set_targets("1500", "75")
        self.assertEqual(self.client.get("/?date=2026-11-03").get_data(as_text=True).count("Target reached"), 2)
        self.set_targets("1000", "100")
        page = self.client.get("/?date=2026-11-03").get_data(as_text=True)
        self.assertIn("500 kcal over target", page)
        self.assertIn("25 g remaining", page)

    def test_ac16_progress_after_modifications(self):
        self.set_targets()
        self.add_meal(calories="500", protein="20")
        self.add_meal(calories="100", protein="5")
        self.assertIn("1400 kcal remaining", self.client.get("/?date=2026-11-03").get_data(as_text=True))
        fields = self.form("/meals/2/edit")
        fields.update(calories="200", protein="10")
        self.client.post("/meals/2/edit", data=fields)
        self.assertIn("1300 kcal remaining", self.client.get("/?date=2026-11-03").get_data(as_text=True))
        fields = self.form("/?date=2026-11-03")
        self.client.post("/meals/2/delete", data=fields)
        self.assertIn("1500 kcal remaining", self.client.get("/?date=2026-11-03").get_data(as_text=True))

    def test_ac10_ac17_missing_targets_and_empty_day(self):
        page = self.client.get("/?date=2026-11-03").get_data(as_text=True)
        self.assertEqual(page.count("Set a target"), 2)
        self.assertNotIn("<progress", page)
        self.set_targets()
        page = self.client.get("/?date=2026-11-03").get_data(as_text=True)
        self.assertIn("2000 kcal remaining", page)
        self.assertIn("100 g remaining", page)

    def test_ac18_ac22_current_goals_and_reopen(self):
        self.add_meal(calories="1500", protein="75")
        self.add_meal(meal_date="2026-11-04", calories="1000", protein="50")
        original_meals = self.query("SELECT * FROM meals")
        self.set_targets()
        self.set_targets("1800", "90")
        from tracker import create_app
        self.client = create_app(self.config).test_client()
        self.assertIn("300 kcal remaining", self.client.get("/?date=2026-11-03").get_data(as_text=True))
        self.assertIn("800 kcal remaining", self.client.get("/?date=2026-11-04").get_data(as_text=True))
        self.assertEqual(self.query("SELECT * FROM meals"), original_meals)

    def test_ac21_target_replay_and_read_write_failures(self):
        fields = self.set_targets()
        self.assertEqual(self.client.post("/targets", data=fields).status_code, 303)
        fields = self.form("/targets")
        fields.update(calorie_target="1900", protein_target="90")
        with patch("tracker.db.save_targets", side_effect=sqlite3.OperationalError("private SQL"), create=True):
            response = self.client.post("/targets", data=fields)
        self.assertEqual(response.status_code, 503)
        self.assertIn(fields["submission_key"], response.get_data(as_text=True))
        self.assertEqual(self.query("SELECT calorie_target_hundredths FROM nutrition_targets")[0]["calorie_target_hundredths"], 200000)
        self.assertEqual(self.client.post("/targets", data=fields).status_code, 303)
        with patch("tracker.db.read_targets", side_effect=sqlite3.OperationalError("private SQL"), create=True):
            response = self.client.get("/")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("Set a target", response.get_data(as_text=True))