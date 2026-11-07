# Calorie and Nutrition Tracker

A local, single-user meal diary with daily calorie and protein totals and reusable targets.
Uses Python 3.12+ (tested with 3.13.0), Flask 3.1.2, SQLite, and local Bootstrap CSS.

## Features

- Add, view, edit, and delete meals for a selected calendar date.
- Choose Breakfast, Lunch, Dinner, or Snacks.
- See selected-day calorie and protein totals; totals update after meal changes.
- Set one reusable calorie/protein target pair for all dates, including historical dates.
- View remaining, reached, or exceeded progress independently for each nutrient.
- Use a responsive interface with keyboard-accessible forms.
- Use the application without accounts, food lookup, external APIs, or CDN assets.

Frontend assets are local: Bootstrap 5.3.8, Bootstrap Icons 1.13.1, and Manrope from
@fontsource/manrope 5.2.8. Their licenses are included beside the assets. The interface
does not require a CDN or JavaScript framework.

## Requirements

- Python 3.12 or newer (tested with Python 3.13.0) and pip.
- Windows PowerShell examples below. Flask and SQLite also work on other platforms;
  use the equivalent Python command for your shell.

Flask 3.1.2 is pinned in `requirements.txt`. SQLite, exact decimal handling, and tests use
Python's standard library. The local frontend includes Bootstrap 5.3.8, Bootstrap Icons
1.13.1, and Manrope from @fontsource/manrope 5.2.8; license files accompany the assets.
No JavaScript framework, CDN, JSON API, Postman, or external database is required.

## Install and Run

```powershell
py -3 -m pip install -r requirements.txt
$env:TRACKER_SECRET_KEY = (py -3 -c "import secrets; print(secrets.token_hex(32))")
py -3 -m flask --app tracker init-db
py -3 -m flask --app tracker run --host 127.0.0.1 --port 5000
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). If port 5000 is occupied, change
`5000` to `5001` in the run command and use that address. These commands install Flask
into the selected system Python environment.

The secret command creates a random Flask session key for the current terminal session.
Keep it private and stable while using the app. A new key after restarting signs users out
of old forms but does not delete database data. The app binds to localhost and has no
authentication; do not expose it to a public network.

`init-db` creates missing tables and preserves existing records. It is safe to rerun.
The database is `instance/nutrition.sqlite3`; back up that file to retain local data.

## Use the App

1. The dashboard opens on today's date. Use the date field to view another day.
2. Select **Add meal**, then enter a food name, date, category, calories in kcal, and
   protein in grams. Save to return to that date's dashboard.
3. Use a meal's edit or delete icon to change or remove that record. Identical meals are
   allowed and count separately.
4. Choose **Set a target** or **Edit daily targets** to enter both positive daily goals.
   This single pair applies to every date. A meal-free day has zero intake.
5. Review actual intake, the progress indicator, and remaining/reached/exceeded status
   for each nutrient. Without configured targets, intake remains visible with a setup link.

Meal values may be zero or positive; targets must be positive. Numeric fields accept digits
with an optional decimal point and one or two decimal places (for example `0`, `0.5`, or
`100.25`). Inputs like `.5`, `+1`, exponent notation, or more than two decimal places are
rejected rather than rounded. Dates use the calendar's `YYYY-MM-DD` value.

## Tests

```powershell
py -3 -m unittest discover -s tests -v
```

Tests use temporary SQLite databases, not personal data. They cover validation, meal routes,
exact calculations, persistence, target progress, error handling, and safe retries. No
pytest, Node.js, Postman, or separate API-testing tool is required.

The current suite has 32 passing tests. Browser checks cover desktop/mobile layouts and
keyboard workflows; the specification's five-person usability walkthrough still requires
real participants. See the feature quickstart validation record for details.

## Troubleshooting

- **`Could not import 'tracker'`**: Run Flask from the repository root and use
  `py -3`; check that `tracker/__init__.py` exists.
- **Missing `TRACKER_SECRET_KEY`**: Generate/set it in the same PowerShell window where
  Flask will run, then launch Flask from that window.
- **Port already in use**: Choose another port in the run command, such as `5001`.
- **Meals or targets appear missing**: Confirm the same checkout and
	`instance/nutrition.sqlite3` are in use. Re-running `init-db` does not seed or reset data.
- **Dependency installation fails**: Check Python is 3.12+ and pip can access PyPI, then
  retry `py -3 -m pip install -r requirements.txt`.

## Project Structure

- `tracker/__init__.py`: application factory and Flask configuration.
- `tracker/routes.py`: dashboard, meal/target forms, and error handling.
- `tracker/db.py`, `tracker/schema.sql`: SQLite connections, schema, persistence, and retry receipts.
- `tracker/validation.py`, `tracker/nutrition.py`: shared validation and exact calculations.
- `tracker/templates/`, `tracker/static/`: HTML templates, CSS, Bootstrap/icons/fonts.
- `tests/`: unittest and Flask test-client suite.
- `specs/001-calorie-nutrition-tracker/`: approved specification and design documents.
- `docs/spec-kit-prompts-and-responses.md`: project workflow prompts, responses, and screenshots.

## Project Status

The latest recorded automated run passed 32 tests. Desktop/mobile layouts and keyboard
workflows were also checked. The specification's five-person usability walkthrough is a
separate manual acceptance activity and is not claimed complete. See the
[validation record](specs/001-calorie-nutrition-tracker/quickstart.md) for details.