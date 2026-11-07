import json
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.exceptions import Conflict, NotFound


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"], autocommit=False, timeout=5)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db():
    connection = get_db()
    with current_app.open_resource("schema.sql") as schema:
        with connection:
            connection.executescript(schema.read().decode("utf-8"))


@click.command("init-db")
@with_appcontext
def init_db_command():
    init_db()
    click.echo("Database ready; existing records preserved.")


def mutate(submission_key, operation, resource_id, payload, destination, change):
    connection = get_db()
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    with connection:
        inserted = connection.execute(
            "INSERT INTO submission_receipts VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(submission_key) DO NOTHING",
            (submission_key, operation, resource_id, canonical, destination),
        )
        if inserted.rowcount == 0:
            receipt = connection.execute(
                "SELECT * FROM submission_receipts WHERE submission_key = ?", (submission_key,)
            ).fetchone()
            if (receipt["operation"], receipt["resource_id"], receipt["payload_json"]) != (
                operation, resource_id, canonical
            ):
                raise Conflict("This form was already submitted with different values. Open a new form.")
            return receipt["redirect_path"]
        change(connection)
    return destination


def list_meals(selected_date):
    return get_db().execute("SELECT * FROM meals WHERE meal_date = ? ORDER BY id", (selected_date,)).fetchall()


def get_meal(meal_id):
    if meal_id > 2**63 - 1:
        raise NotFound("Meal not found.")
    record = get_db().execute("SELECT * FROM meals WHERE id = ?", (meal_id,)).fetchone()
    if record is None:
        raise NotFound("Meal not found.")
    return record


def save_meal(values, submission_key, destination, meal_id=None):
    def change(connection):
        parameters = tuple(values[field] for field in (
            "meal_date", "food_name", "category", "calories_hundredths", "protein_hundredths"
        ))
        if meal_id is None:
            connection.execute(
                "INSERT INTO meals (meal_date,food_name,category,calories_hundredths,protein_hundredths) "
                "VALUES (?,?,?,?,?)", parameters,
            )
        else:
            get_meal(meal_id)
            connection.execute(
                "UPDATE meals SET meal_date=?,food_name=?,category=?,calories_hundredths=?,"
                "protein_hundredths=? WHERE id=?", (*parameters, meal_id),
            )
    return mutate(submission_key, "add_meal" if meal_id is None else "edit_meal",
                  meal_id, values, destination, change)


def delete_meal(meal_id, submission_key, selected_date, destination):
    def change(connection):
        get_meal(meal_id)
        connection.execute("DELETE FROM meals WHERE id = ?", (meal_id,))
    return mutate(submission_key, "delete_meal", meal_id, {"return_date": selected_date}, destination, change)


def read_targets():
    record = get_db().execute("SELECT * FROM nutrition_targets WHERE id=1").fetchone()
    return dict(record) if record is not None else {
        "calorie_target_hundredths": None, "protein_target_hundredths": None
    }


def save_targets(values, submission_key, destination):
    def change(connection):
        connection.execute(
            "INSERT INTO nutrition_targets VALUES (1, ?, ?) ON CONFLICT(id) DO UPDATE SET "
            "calorie_target_hundredths=excluded.calorie_target_hundredths, "
            "protein_target_hundredths=excluded.protein_target_hundredths",
            (values["calorie_target_hundredths"], values["protein_target_hundredths"]),
        )
    return mutate(submission_key, "save_targets", None, values, destination, change)