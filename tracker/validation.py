import re
from datetime import date
from decimal import Decimal, localcontext

CATEGORIES = ("Breakfast", "Lunch", "Dinner", "Snacks")
MAX_AMOUNT = 2**63 - 1


def amount(raw, positive=False):
    value = str(raw or "").strip()
    if len(value) > 32 or not re.fullmatch(r"[0-9]+(?:\.[0-9]{1,2})?", value):
        raise ValueError("Enter digits with at most two decimal places, such as 100 or 0.5.")
    with localcontext() as context:
        context.prec = 40
        number = Decimal(value)
        if not number.is_finite() or number * 100 > MAX_AMOUNT:
            raise ValueError("Enter an amount no greater than 92233720368547758.07.")
        if positive and number <= 0:
            raise ValueError("Enter a target greater than zero.")
        return int(number * 100)


def calendar_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("Choose a valid date in YYYY-MM-DD format.")
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        raise ValueError("Choose a valid calendar date.") from None


def validate_meal(fields):
    values, errors = {}, {}
    name = fields.get("food_name", "").strip()
    if not name:
        errors["food_name"] = "Enter a food name."
    else:
        values["food_name"] = name
    category = fields.get("category", "")
    if category not in CATEGORIES:
        errors["category"] = "Choose Breakfast, Lunch, Dinner, or Snacks."
    else:
        values["category"] = category
    try:
        values["meal_date"] = calendar_date(fields.get("meal_date", ""))
    except ValueError as error:
        errors["meal_date"] = str(error)
    for field in ("calories", "protein"):
        try:
            values[field + "_hundredths"] = amount(fields.get(field, ""))
        except ValueError as error:
            errors[field] = str(error)
    return values, errors


def validate_targets(fields):
    values, errors = {}, {}
    for field in ("calorie_target", "protein_target"):
        try:
            values[field + "_hundredths"] = amount(fields.get(field, ""), positive=True)
        except ValueError as error:
            errors[field] = str(error)
    try:
        values["return_date"] = calendar_date(fields.get("return_date", ""))
    except ValueError as error:
        errors["return_date"] = str(error)
    return values, errors