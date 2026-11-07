# Calorie and Nutrition Tracker

A local, single-user meal diary with daily calorie and protein totals and reusable targets.
Uses Python 3.12+ (tested with 3.13.0), Flask 3.1.2, SQLite, and local Bootstrap CSS.

Frontend assets are local: Bootstrap 5.3.8, Bootstrap Icons 1.13.1, and Manrope from
@fontsource/manrope 5.2.8. Their licenses are included beside the assets. The interface
does not require a CDN or JavaScript framework.

## Run (Windows PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:TRACKER_SECRET_KEY = .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python.exe -m flask --app tracker init-db
.\.venv\Scripts\python.exe -m flask --app tracker run --host 127.0.0.1 --port 5000
```

Open http://127.0.0.1:5000. Choose port 5001 if 5000 is occupied. No activation script is
required. Keep the secret stable during use and do not commit it. The generated command
sets it for this terminal session. Restarting with a different secret invalidates forms,
not saved meals. Never expose this unauthenticated application to a public network.

The init-db command creates missing tables without deleting existing data. The database
is instance/nutrition.sqlite3; preserve that file to retain meals and targets.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests use temporary databases, not personal data. No Postman, pytest, Node.js, or external
database is required.

The current suite has 32 passing tests. Browser checks cover desktop/mobile layouts and
keyboard workflows; the specification's five-person usability walkthrough still requires
real participants. See the feature quickstart validation record for details.

## Structure

- tracker/__init__.py: application configuration and registration.
- tracker/routes.py: HTML form workflows, tokens, responses, and errors.
- tracker/db.py and schema.sql: SQLite lifecycle, transactions, and reliable mutations.
- tracker/validation.py: shared validation and exact input conversion.
- tracker/nutrition.py: exact formatting, daily sums, and progress calculations.
- tracker/templates/ and tracker/static/: server-rendered pages, CSS, and local Bootstrap.
- tests/: unittest and Flask test-client checks.

Meals use kcal and grams, with at most two decimal places. One current target pair applies
to all dates; updating targets also changes historical progress comparisons, not meal data.
Duplicate meals are allowed. Submission keys prevent a retried form from applying twice.