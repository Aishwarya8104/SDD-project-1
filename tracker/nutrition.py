from decimal import Decimal, localcontext


def format_amount(value):
    whole, fraction = divmod(value, 100)
    return str(whole) if not fraction else f"{whole}.{fraction:02d}".rstrip("0")


def daily_totals(meals):
    return {nutrient: sum(meal[nutrient + "_hundredths"] for meal in meals)
            for nutrient in ("calories", "protein")}


def progress(actual, target):
    result = {"actual": actual, "target": target, "status": "missing_target",
              "remaining": None, "exceeded": None, "fill": None}
    if target is None:
        return result
    with localcontext() as context:
        context.prec = 40
        fill = min(Decimal(100), Decimal(actual) * 100 / Decimal(target))
        result["fill"] = format(fill, ".2f").rstrip("0").rstrip(".") if fill % 1 else str(int(fill))
    result.update(remaining=max(target - actual, 0), exceeded=max(actual - target, 0),
                  status="below" if actual < target else "reached" if actual == target else "exceeded")
    return result