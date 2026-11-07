# Quickstart and Validation Guide

**Status**: Application implemented and running locally. Automated and browser checks
have passed; the real five-user walkthrough and dependent final acceptance remain pending.

## Verified Results (2026-11-03)

- Python 3.13.0, Flask 3.1.2, Windows 11 AMD64; pinned runtime dependency installed in .venv.
- Foundation checkpoint: 6 tests passed. Meal workflow checkpoint: 8 browser-contract
   tests passed. Totals checkpoint: 18 tests passed. Complete implementation: 32 tests passed.
- Functional checks cover AC-01 through AC-23: meal creation/view/edit/delete/move,
   category/date isolation, exact decimals and sums, precision/notation rejection,
   reusable goals and historical comparisons, missing targets/empty days, reopen
   persistence, commit failures, rollback, and duplicate-safe retry.
- Real init-db CLI passed non-destructive initialization tests. Existing meals and targets
   survive repeated initialization. Connections close before temporary-directory cleanup.
- Injected read, write, and pre-commit failures return non-success responses without
   exposing private diagnostics or claiming an empty day. Selected-date Retry preserves
   its query string. Failed deletion retains its submission key for retry.
- Browser automation checked the actual Flask application at requested 375px and 1280px
   viewports: no horizontal overflow; desktop/mobile screenshots captured under instance/;
   local Bootstrap, icon sprite, CSS, and font requests returned 200.
- Browser precision rejection, successful add, exact totals, target updates, and reached
   states passed. Keyboard-only add/edit/delete and target update flows passed. Screenshots
   were reviewed for text/control overlap; the brand icon contrast issue was corrected.
- Browser test meals were deleted through the interface; targets were restored only if
   they still matched the test values. No sample meals or default goals were left behind.
- Five warm 100-meal requests using an isolated temporary database took 5.64, 4.77, 4.48,
   4.33, and 5.30 ms using Flask's test client. This is a local server-rendering smoke
   measurement, not an end-to-end network or production performance claim.
- pip check reported no broken requirements. Editor diagnostics reported no source/test
   errors. Maintainability review confirmed separate route, validation, calculation, and
   storage responsibilities, shared exact formatting, parameterized SQL, escaped templates,
   safe error logging, and documented run/test commands.
- No extension hooks are configured. No commits or branches were created.

**Remaining gate**: T043 requires five real first-time participants, with at least four
successful unassisted completions of the specified task. This has not been performed;
browser automation is not a substitute. T046 final acceptance remains pending that gate.

## Prerequisites

Python 3.12+ with pip, a local terminal/browser, and the implemented package, requirements,
tests, and local Bootstrap CSS/license. No Node.js, external database, Postman, or pytest
is needed. Run from repository root; commands below are Windows PowerShell examples.

## Setup and Run

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:TRACKER_SECRET_KEY = .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python.exe -m flask --app tracker init-db
.\.venv\Scripts\python.exe -m flask --app tracker run --host 127.0.0.1 --port 5000
```

The factory reads TRACKER_SECRET_KEY and defaults to instance/nutrition.sqlite3.
Keep the secret local/stable for the run, never committed. Initialization must not erase
saved data when repeated. Open http://127.0.0.1:5000. If occupied, choose another port such
as 5001. Public hosting is not included.

## Automated Checks

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Expected: all tests pass, using temporary databases only. The factory
accepts a test configuration with database path and deterministic secret. Clients fetch
forms to obtain CSRF/submission tokens before each POST; do not globally disable CSRF.
Close connections before Windows temporary-directory cleanup.

See [plan.md](plan.md) for all acceptance-to-test mappings, [data-model.md](data-model.md)
for transactions/storage, and [browser routes](contracts/browser-routes.md) for HTTP rules.

## End-to-End Scenarios

1. **Empty day/missing targets (AC-10, AC-17)**: Select 2026-11-01 before recording data.
   Expect empty meals, zero intake, and setup prompts, not target percentages. Test-client
   fixtures also cover a single absent nutrient target.
2. **Add/view/totals (AC-01, AC-02, AC-07, AC-08, AC-20)**: Add Breakfast 300/12,
   Lunch 450/25.5, Dinner 600/40, Snacks 150/7.5 on that date. Expect four matching
   records, 1500 kcal, and 85 g.
3. **Date isolation (AC-09)**: Add 700/30 on 2026-11-02. Each date shows only its records;
   switching back retains 1500/85 on the first date.
4. **Goals/progress (AC-11 to AC-15)**: Set 2000/100. First-date remaining is 500/15.
   Exercise exact equality, exceeded calories with protein below, and positive decimal
   target updates using the specification fixtures. Indicators never overflow their track.
5. **Edit/delete/move (AC-03, AC-04, AC-16, AC-19)**: Change name/category/amounts, move
   one record to the other date, then delete it. Compare each date's summary with saved
   meals after each action. Delete the last meal on a day and verify zero totals.
6. **Validation/precision (AC-05, AC-06, AC-11, AC-23)**: Try whitespace-only name,
   missing fields, invalid category/date, negative/non-numeric values, NaN/infinity,
   and 1.234 or 1.230 in each numeric field. Expect clear errors, no writes, and no
   rounding. Zero meals and two-decimal amounts save; zero targets do not. Two meals of
   0.1/0.1 and 0.2/0.2 display 0.3/0.3 before/after reopen.
7. **Reusable goals/history (AC-22)**: Follow AC-22's exact two-date fixture; update
   2000/100 to 1800/90 on the later date. Revisit the older date: remaining is 300/15,
   with unchanged meals and intake. Reopening retains the same current target pair.
8. **Persistence (AC-18)**: Stop/restart Flask with the same database. Saved meals,
   edits/deletions, and current goals remain correct.
9. **Failures/retry (AC-21)**: Inject read/execute/pre-commit failures in automated tests.
   Expect no false success/empty day, unchanged saved data, and retry with the same key.
   Discard a successful POST response and replay its payload/key: exactly one mutation.
   A fresh key permits identical meals; changed-payload replay returns 409.

## Boundaries and Manual Review

- Cover zero versus blank, minimum target 0.01, leap-day validity, the storage maximum
  and next hundredth, daily sums beyond 64 bits, missing IDs, CSRF, replay after deletion.
- At 375px and 1280px widths, check readable labels/units, text fit, no control overlap,
  keyboard-only workflows, visible focus, associated errors, and non-color statuses.
- Ask five first-time users to add a meal and identify both totals without help; at least
  four must succeed for NFR-01/SC-001. Record outcomes, not assumed passes.
- Smoke-check a 100-meal day load; record elapsed time and developer-machine details.
- Review component responsibilities and README run/test instructions for NFR-05 and all
  eight constitution principles. Record actual automated/manual results at implementation.