import sqlite3
from unittest.mock import patch

from tests import AppTestCase
from tracker.db import get_db, init_db, mutate
from tracker import create_app


class CommitFailure:
    def __init__(self, connection):
        self.connection = connection

    def __getattr__(self, name):
        return getattr(self.connection, name)

    def __enter__(self):
        return self

    def __exit__(self, kind, value, traceback):
        self.connection.rollback()
        if kind is None:
            raise sqlite3.OperationalError("injected commit failure")
        return False


class FoundationTests(AppTestCase):
    def test_initialization_preserves_targets(self):
        with self.app.app_context():
            connection = get_db()
            with connection:
                connection.execute("UPDATE nutrition_targets SET calorie_target_hundredths=200000 WHERE id=1")
            init_db()
            self.assertEqual(connection.execute("SELECT calorie_target_hundredths FROM nutrition_targets").fetchone()[0], 200000)

    def test_receipt_replay_and_rollback(self):
        with self.app.app_context():
            def change(connection):
                connection.execute("UPDATE nutrition_targets SET calorie_target_hundredths=100 WHERE id=1")

            mutate("same", "save_targets", None, {"value": 100}, "/", change)
            mutate("same", "save_targets", None, {"value": 100}, "/", lambda connection: self.fail("Replayed mutation"))
            self.assertEqual(get_db().execute("SELECT count(*) FROM submission_receipts").fetchone()[0], 1)
            def fail(connection):
                change(connection)
                raise sqlite3.OperationalError("injected")

            with self.assertRaises(sqlite3.OperationalError):
                mutate("failed", "save_targets", None, {}, "/", fail)
            self.assertEqual(get_db().execute("SELECT count(*) FROM submission_receipts").fetchone()[0], 1)


class PersistenceTests(AppTestCase):
    def test_ac18_edits_deletes_targets_survive_restart(self):
        self.add_meal(food_name="First")
        self.add_meal(food_name="Second")
        fields = self.form("/meals/1/edit")
        fields.update(food_name="Corrected", calories="100.25", protein="0.75")
        self.assertEqual(self.client.post("/meals/1/edit", data=fields).status_code, 303)
        fields = self.form("/?date=2026-11-03")
        self.client.post("/meals/2/delete", data=fields)
        self.set_targets("2000.25", "100.75")
        client = create_app(self.config).test_client()
        page = client.get("/?date=2026-11-03").get_data(as_text=True)
        self.assertIn("Corrected", page)
        self.assertNotIn("Second", page)
        self.assertIn("100.25", page)
        self.assertIn("2000.25", page)

    def test_ac21_commit_failure_rolls_back_meal_and_receipt(self):
        fields = self.form("/meals/new")
        fields.update(meal_date="2026-11-03", food_name="Oats", category="Breakfast", calories="100", protein="5")
        with self.app.app_context():
            connection = get_db()
            with patch("tracker.db.get_db", return_value=CommitFailure(connection)):
                response = self.client.post("/meals/new", data=fields)
        self.assertEqual(response.status_code, 503)
        self.assertIn(fields["submission_key"], response.get_data(as_text=True))
        self.assertEqual(self.query("SELECT * FROM meals"), [])
        self.assertEqual(self.query("SELECT * FROM submission_receipts"), [])
        self.assertEqual(self.client.post("/meals/new", data=fields).status_code, 303)
        self.assertEqual(self.client.post("/meals/new", data=fields).status_code, 303)
        self.assertEqual(len(self.query("SELECT * FROM meals")), 1)

    def test_ac21_delete_and_target_commit_failure_preserves_previous_data(self):
        self.add_meal()
        fields = self.form("/?date=2026-11-03")
        with self.app.app_context():
            connection = get_db()
            with patch("tracker.db.get_db", return_value=CommitFailure(connection)):
                response = self.client.post("/meals/1/delete", data=fields)
        self.assertEqual(response.status_code, 503)
        self.assertIn("Retry deletion", response.get_data(as_text=True))
        self.assertIn(fields["submission_key"], response.get_data(as_text=True))
        self.assertEqual(len(self.query("SELECT * FROM meals")), 1)
        self.set_targets()
        before = self.query("SELECT * FROM nutrition_targets")
        fields = self.form("/targets")
        fields.update(calorie_target="1900", protein_target="90")
        with self.app.app_context():
            connection = get_db()
            with patch("tracker.db.get_db", return_value=CommitFailure(connection)):
                response = self.client.post("/targets", data=fields)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(self.query("SELECT * FROM nutrition_targets"), before)
        self.assertEqual(self.client.post("/targets", data=fields).status_code, 303)

    def test_ac17_one_missing_target_and_schema_constraints(self):
        with self.app.app_context():
            connection = get_db()
            with connection:
                connection.execute("UPDATE nutrition_targets SET calorie_target_hundredths=200000 WHERE id=1")
        page = self.client.get("/?date=2026-11-03").get_data(as_text=True)
        self.assertEqual(page.count("Set a target"), 1)
        self.assertEqual(page.count("<progress"), 1)
        for value in (0, -1, 0.5):
            with self.subTest(value=value), self.app.app_context():
                with self.assertRaises(sqlite3.IntegrityError):
                    with get_db():
                        get_db().execute("UPDATE nutrition_targets SET protein_target_hundredths=?", (value,))

    def test_initialization_and_context_cleanup(self):
        self.add_meal()
        self.set_targets()
        before = self.query("SELECT * FROM nutrition_targets")
        result = self.app.test_cli_runner().invoke(args=["init-db"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(self.query("SELECT * FROM nutrition_targets"), before)
        self.assertEqual(len(self.query("SELECT * FROM meals")), 1)
        with self.app.app_context():
            connection = get_db()
        with self.assertRaises(sqlite3.ProgrammingError):
            connection.execute("SELECT 1")