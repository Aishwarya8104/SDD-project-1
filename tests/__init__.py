import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from tracker import create_app
from tracker.db import get_db, init_db


class FormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = {}
        self.select_name = None
        self.option_selected = False
        self.option_value = None
        self.option_text = ""

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "input" and attributes.get("name"):
            self.values[attributes["name"]] = attributes.get("value", "")
        elif tag == "select":
            self.select_name = attributes.get("name")
            self.values[self.select_name] = ""
        elif tag == "option":
            self.option_selected = "selected" in attributes
            self.option_value = attributes.get("value")
            self.option_text = ""

    def handle_data(self, data):
        if self.option_selected:
            self.option_text += data

    def handle_endtag(self, tag):
        if tag == "option" and self.option_selected and self.select_name:
            self.values[self.select_name] = self.option_value if self.option_value is not None else self.option_text.strip()
            self.option_selected = False
        elif tag == "select":
            self.select_name = None


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.config = {
            "TESTING": True, "SECRET_KEY": "test-only",
            "DATABASE": str(Path(self.directory.name) / "test.sqlite3"),
        }
        self.app = create_app(self.config)
        self.client = self.app.test_client()
        with self.app.app_context():
            init_db()

    def form(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        parser = FormParser()
        parser.feed(response.get_data(as_text=True))
        return parser.values

    def query(self, sql, parameters=()):
        with self.app.app_context():
            return [dict(row) for row in get_db().execute(sql, parameters).fetchall()]

    def add_meal(self, **changes):
        fields = self.form("/meals/new?date=2026-11-03")
        fields.update(meal_date="2026-11-03", food_name="Oats", category="Breakfast",
                      calories="300", protein="12")
        fields.update(changes)
        response = self.client.post("/meals/new", data=fields)
        self.assertEqual(response.status_code, 303)
        return fields

    def set_targets(self, calories="2000", protein="100"):
        fields = self.form("/targets?date=2026-11-03")
        fields.update(calorie_target=calories, protein_target=protein)
        response = self.client.post("/targets", data=fields)
        self.assertEqual(response.status_code, 303)
        return fields