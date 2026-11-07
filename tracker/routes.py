import re
import secrets
import sqlite3
from datetime import date

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.exceptions import BadRequest, HTTPException

from . import db
from .nutrition import daily_totals, format_amount, progress
from .validation import CATEGORIES, calendar_date, validate_meal, validate_targets

bp = Blueprint("main", __name__)


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


def new_submission():
    return secrets.token_hex(32)


@bp.before_request
def check_tokens():
    if request.method == "POST":
        supplied = request.form.get("csrf_token", "")
        expected = session.get("csrf_token", "")
        if not expected or not re.fullmatch(r"[a-f0-9]{64}", supplied) or not secrets.compare_digest(supplied, expected):
            return render_template("error.html", title="Form expired", message="Open the form again and retry."), 400
        if not re.fullmatch(r"[a-f0-9]{64}", request.form.get("submission_key", "")):
            return render_template("error.html", title="Invalid form", message="Open a new form and retry."), 400


def storage_error(error):
    current_app.logger.error("Database operation failed: %s", type(error).__name__)
    return render_template("error.html", title="Data unavailable", message="Could not load or save your data. Please retry."), 503


def page_error(error):
    return render_template("error.html", title=error.name, message=error.description), error.code


def unexpected_error(error):
    if isinstance(error, HTTPException):
        return page_error(error)
    current_app.logger.error("Unexpected application error: %s", type(error).__name__)
    return render_template("error.html", title="Something went wrong", message="Please retry the action."), 500


def selected_date(raw=None):
    try:
        return calendar_date(date.today().isoformat() if raw is None else raw)
    except ValueError as error:
        raise BadRequest(str(error)) from None


@bp.get("/")
def dashboard():
    day = selected_date(request.args.get("date"))
    meals = db.list_meals(day)
    goals = db.read_targets()
    totals = daily_totals(meals)
    states = {
        "calories": progress(totals["calories"], goals["calorie_target_hundredths"]),
        "protein": progress(totals["protein"], goals["protein_target_hundredths"]),
    }
    return render_template("dashboard.html", day=day, meals=meals, totals=totals, states=states)


@bp.route("/meals/new", methods=["GET", "POST"])
@bp.route("/meals/<int:meal_id>/edit", methods=["GET", "POST"])
def meal_form(meal_id=None):
    errors, message, status = {}, None, 200
    if request.method == "POST":
        fields = request.form.to_dict()
        values, errors = validate_meal(fields)
        if errors:
            status = 422
        else:
            try:
                destination = url_for("main.dashboard", date=values["meal_date"])
                destination = db.save_meal(values, fields["submission_key"], destination, meal_id)
                flash("Meal saved.")
                return redirect(destination, code=303)
            except (sqlite3.Error, OverflowError) as error:
                current_app.logger.error("Meal save failed: %s", type(error).__name__)
                message, status = "Your meal could not be saved. Please retry.", 503
    else:
        fields = {"meal_date": selected_date(request.args.get("date")), "submission_key": new_submission()}
        if meal_id is not None:
            record = db.get_meal(meal_id)
            fields.update(dict(record))
            fields.update(calories=format_amount(record["calories_hundredths"]),
                          protein=format_amount(record["protein_hundredths"]))
    return render_template("meal_form.html", fields=fields, errors=errors,
                           message=message, editing=meal_id is not None, categories=CATEGORIES), status


@bp.post("/meals/<int:meal_id>/delete")
def remove_meal(meal_id):
    day = selected_date(request.form.get("return_date", ""))
    try:
        destination = db.delete_meal(meal_id, request.form["submission_key"], day,
                                     url_for("main.dashboard", date=day))
    except (sqlite3.Error, OverflowError) as error:
        current_app.logger.error("Meal deletion failed: %s", type(error).__name__)
        return render_template("error.html", title="Meal not deleted",
                               message="Your meal could not be deleted. Please retry.",
                               retry_fields=request.form, retry_action=request.path), 503
    flash("Meal deleted.")
    return redirect(destination, code=303)


@bp.route("/targets", methods=["GET", "POST"])
def targets():
    errors, message, status = {}, None, 200
    if request.method == "POST":
        fields = request.form.to_dict()
        values, errors = validate_targets(fields)
        if errors:
            status = 422
        else:
            try:
                destination = url_for("main.dashboard", date=values["return_date"])
                destination = db.save_targets(values, fields["submission_key"], destination)
                flash("Daily targets updated.")
                return redirect(destination, code=303)
            except (sqlite3.Error, OverflowError) as error:
                current_app.logger.error("Target save failed: %s", type(error).__name__)
                message, status = "Your targets could not be saved. Please retry.", 503
    else:
        goals = db.read_targets()
        fields = {"return_date": selected_date(request.args.get("date")), "submission_key": new_submission()}
        for field in ("calorie_target", "protein_target"):
            value = goals[field + "_hundredths"]
            fields[field] = "" if value is None else format_amount(value)
    return render_template("targets.html", fields=fields, errors=errors, message=message), status


def register(app):
    app.register_blueprint(bp)
    app.jinja_env.globals.update(csrf_token=csrf_token, new_submission=new_submission)
    app.jinja_env.filters["amount"] = format_amount
    app.register_error_handler(sqlite3.Error, storage_error)
    app.register_error_handler(OverflowError, storage_error)
    app.register_error_handler(HTTPException, page_error)
    app.register_error_handler(Exception, unexpected_error)