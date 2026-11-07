# Research: Calorie and Nutrition Tracker

**Date**: 2026-11-03 | **Status**: Complete

## Runtime and Application Shape

- **Decision**: Python 3.12 or later, Flask 3.1.x, Jinja-rendered HTML, Bootstrap 5.3
  CSS, and a small application factory. Bootstrap CSS is served locally; no JavaScript
  framework, public JSON API, Postman, ORM, or additional runtime packages are required.
- **Rationale**: Flask supplies routing, forms, templates, and its test client. Standard
  library modules supply storage, decimal arithmetic, dates, security tokens, and tests.
- **Alternatives considered**: A separate frontend/API, SQLAlchemy, and Flask extensions
  add concepts unnecessary for the approved single-user assignment.

## Exact Nutrition Values

- **Decision**: Validate original decimal strings before conversion. Accept plain decimal
  notation with zero to two fractional digits, reject greater precision (including 1.230),
  non-finite numbers, missing values, and negatives. Use Decimal from strings, never float.
  Store integer hundredths; sum fetched integers in Python and format without floats.
- **Rationale**: SQLite REAL and binary floating point can introduce visible arithmetic
  artifacts. Checking precision before rounding preserves the confirmed business rule.
- **Alternatives considered**: REAL is inexact; text decimals complicate aggregation;
  quantize alone can incorrectly accept extra trailing zero digits.
- **Technical bound**: Each stored amount must fit a signed 64-bit integer after scaling:
  at most 92233720368547758.07. Reject larger inputs with a field error, not a crash.
  This is a storage representation limit, not a new dietary rule. Python integer totals
  can exceed this bound across multiple meals without overflowing SQLite SUM.

## Persistence and Targets

- **Decision**: Use one request-scoped sqlite3 connection, parameterized SQL, explicit
  transaction handling with Python 3.12's autocommit=False, and teardown closure. A
  singleton targets row holds independently nullable positive target amounts, with no
  date column. Each mutation and its submission receipt commit together.
- **Rationale**: Short transactions preserve data on failure. Current targets apply to
  every date; daily summaries are derived, not stored or cached.
- **Alternatives considered**: Date-specific targets contradict the confirmed policy;
  cached summaries introduce synchronization problems. A global connection risks leaks.

## Browser Forms and Safe Retry

- **Decision**: GET reads; POST mutates; successful writes use 303 redirects to a GET.
  Use session CSRF tokens and a separate random submission key per mutation form.
  A receipt stores the key, operation, validated payload, and safe redirect in the same
  transaction as the change. Matching replay returns the prior redirect; changed payload
  under a committed key returns 409. A fresh key permits an identical meal.
- **Rationale**: Redirects prevent refresh resubmission but cannot alone protect against
  a committed write followed by a lost response. Persisted receipts meet AC-21 without
  deduplicating by food contents or adding infrastructure.
- **Alternatives considered**: Content uniqueness breaks AC-20; session-only receipts
  can be lost when a response is lost. A meal-only unique key does not cover edit/delete.
- **Boundary**: Keep receipts for this assignment; pruning limits replay protection.
  Use separate CSRF and submission tokens, a persistent local secret, escaped templates,
  and localhost-only access. Authentication and public hosting remain outside scope.

## Tests and Failure Behavior

- **Decision**: unittest, Flask test client, TemporaryDirectory SQLite files, and
  unittest.mock failure injection. Test real transactions, reopen persistence, failed
  commits, lost responses, field validation, numeric boundaries, and all AC-01 to AC-23.
- **Rationale**: These tools are already supplied by Python/Flask and can verify the
  browser-facing contract without an API testing product.
- **Alternatives considered**: pytest and Postman are unnecessary additional tools;
  mocked-only storage cannot prove transaction rollback or persistence.

## Reference Material

- Flask database lifecycle: https://flask.palletsprojects.com/en/stable/tutorial/database/
- Flask forms: https://flask.palletsprojects.com/en/stable/tutorial/blog/
- Flask testing: https://flask.palletsprojects.com/en/stable/testing/
- Flask security: https://flask.palletsprojects.com/en/stable/web-security/
- Python sqlite3: https://docs.python.org/3/library/sqlite3.html
- Python Decimal: https://docs.python.org/3/library/decimal.html
- Python unittest: https://docs.python.org/3/library/unittest.html
- SQLite storage types: https://www.sqlite.org/datatype3.html
- SQLite conflict handling: https://www.sqlite.org/lang_upsert.html
- Bootstrap forms: https://getbootstrap.com/docs/5.3/forms/overview/

All technical choices are resolved. Existing specification assumptions about kcal, grams,
local dates, and a single personal record set are retained, not new business decisions.