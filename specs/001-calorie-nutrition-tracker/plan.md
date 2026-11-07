# Implementation Plan: Calorie and Nutrition Tracker

**Branch**: `001-calorie-nutrition-tracker` (setup-reported feature identifier)
**Date**: 2026-11-03 | **Spec**: [spec.md](spec.md)

**Input**: Approved specification and constitution v1.0.0.

**Status**: Phase 0 research and Phase 1 design complete; application not implemented.

## Summary

Build one local Flask application using server-rendered HTML, CSS, Bootstrap, and SQLite.
Users manage dated meals, see exact calorie/protein totals, set one reusable target pair,
and compare any date with the current goals. No JSON API, Postman, ORM, authentication,
or frontend build system is needed. Supporting design is in [research.md](research.md),
[data-model.md](data-model.md), [browser contracts](contracts/browser-routes.md), and
[quickstart.md](quickstart.md).

## Technical Context

**Language/Version**: Python 3.12+; record the exact tested version at implementation.

**Primary Dependencies**: Flask 3.1.x and its dependencies; locally vendored Bootstrap
5.3 CSS with license. Pin exact versions at implementation. No Bootstrap JS is required.

**Storage**: Standard-library sqlite3; instance database with two business tables and
one internal retry-receipt table; no external database service.

**Testing**: unittest, Flask test client, unittest.mock, and temporary SQLite files.

**Target Platform**: Local Windows development; modern mobile/desktop browsers;
127.0.0.1 only. Public multi-user hosting and synchronization are outside scope.

**Project Type**: Single-package, single-process server-rendered web application.

**Performance Goals**: No new business SLA. Engineering smoke check: a seeded 100-meal
day loads within one second after warm-up on the developer's machine; record the machine
and investigate regressions. This is not a product record limit.

**Constraints**: Four categories, two nutrients, no negative meal values, positive targets,
at most two decimal places without input rounding, and no unnecessary dependencies.

**Scale/Scope**: One personal record set with date-filtered history; dashboard and two
forms. No specified product record limit; individual amounts must fit SQLite integers.

## Constitution Check

Governing document: [constitution.md](../../.specify/memory/constitution.md), v1.0.0.
The specification's old dependency note about an unratified scaffold is superseded by
that constitution. Neither the specification nor constitution is changed by this plan.

| Principle | Design evidence | Before research | After design |
|-----------|-----------------|-----------------|--------------|
| Simplicity | One app, standard-library storage/tests, no separate API | PASS | PASS |
| Accuracy | Integer hundredths, per-date sums, one progress function | PASS | PASS |
| User-Friendly Design | Responsive labels/units, keyboard access, text statuses | PASS | PASS |
| Input Validation | Shared server rules; invalid submissions never write | PASS | PASS |
| Maintainability | Separate routes, validation, calculations, database functions | PASS | PASS |
| Data Integrity | Atomic mutations, persistent targets, duplicate-safe receipts | PASS | PASS |
| Testing | AC-01 through AC-23 mapped below; real SQLite failure tests | PASS | PASS |
| Error Handling | Rollback, field messages, retry, no false empty/success states | PASS | PASS |

No gate failures or unresolved technical choices remain. These are design checks, not
claims that application behavior or tests have already passed.

## Project Structure

### Documentation (this feature)

```text
specs/001-calorie-nutrition-tracker/
  plan.md
  research.md
  data-model.md
  quickstart.md
  contracts/browser-routes.md
  spec.md
  checklists/requirements.md
```

### Source Code (repository root)
Planned layout only; no application files are created during planning.

```text
tracker/
  __init__.py
  routes.py
  db.py
  validation.py
  nutrition.py
  schema.sql
  templates/
    base.html
    dashboard.html
    meal_form.html
    targets.html
    error.html
  static/
    styles.css
    vendor/bootstrap.min.css
    vendor/bootstrap.LICENSE
instance/
  nutrition.sqlite3
tests/
  test_validation.py
  test_nutrition.py
  test_routes.py
  test_persistence.py
requirements.txt
README.md
```

**Structure Decision**: One package; no separate backend/frontend, repository classes,
service hierarchy, or migration framework. Exclude instance data, secrets, and virtual
environments from version control during implementation. Generate tasks later using
`/speckit-tasks`; this command ends after design.

### Components and Responsibilities

| Component | Responsibility |
|-----------|----------------|
| Application factory | Configuration, route registration, initialization CLI, teardown |
| Routes | Request shape/tokens, helper calls, responses and safe redirects |
| Validation | Shared dates, categories, numeric syntax/scale, field errors |
| Nutrition | Pure daily sums, exact formatting, target comparison, indicator fill |
| Database | Connections, parameterized CRUD, targets, transactions, retry receipts |
| Templates | Escaped values/errors and controls, no business calculations |
| Static CSS | Local Bootstrap and small responsive/accessibility adjustments |

Shared exact amount formatting in tracker/nutrition.py is foundational work, available
before US1 meal lists and edit forms. US2 adds daily summation and reuses that formatter
rather than introducing a second formatting implementation.

### Browser Routes and Pages

| Method and path | Responsibility |
|-----------------|----------------|
| GET /?date=YYYY-MM-DD | Date selector, meals, totals, and progress dashboard |
| GET /meals/new?date=YYYY-MM-DD | Blank meal form for the selected date |
| POST /meals/new | Validate and add one meal |
| GET /meals/<int:meal_id>/edit | Prefilled meal form |
| POST /meals/<int:meal_id>/edit | Validate and replace that record's editable fields |
| POST /meals/<int:meal_id>/delete | Delete one meal; GET never deletes |
| GET /targets?date=YYYY-MM-DD | Current shared goals; date is return context only |
| POST /targets | Set/update current reusable target pair |

These are HTML/form endpoints, not a JSON API. Successful writes return 303 and a freshly
read dashboard; ordinary navigation updates totals without reopening the application.
See the browser contract for fields, errors, token checks, and replay behavior.

### Processing Flow

1. **View a day**: Validate an explicit ISO date, defaulting to today's local date only
   if omitted. Read its meals and current targets in one read transaction; sum integers,
   compute progress, and render. A failed read is an error, not empty business data.
2. **Add**: Receive meal details/tokens; validate all fields before writes. Scale numeric
   strings into integer hundredths. Handle the receipt and insert in one transaction.
   Commit then redirect to the saved date; rollback and retain inputs/key on failure.
3. **Edit**: Load by immutable ID, not name. Validate all editable fields, including date.
   Handle replay before requiring that the meal still exists. Update in one transaction
   and redirect to the new date. Both dates derive current totals; no cached sums to fix.
4. **Delete**: Validate tokens and return date, handle replay, require an existing ID,
   and delete with its receipt atomically. Redirect to its date; deleting the last meal
   naturally restores zeros. A fresh request for a missing ID returns 404.
5. **Targets**: Require both positive form values and update the singleton pair atomically.
   Blanks are invalid, not a removal operation. Read absent nutrients independently for
   initial/legacy states. All dates immediately compare against the updated pair.
6. **Retry**: Each form has a fresh random submission key distinct from its CSRF token.
   Persist operation, canonical payload, and redirect with the mutation. Identical replay
   returns the prior redirect without reapplying; changed payload under a committed key
   returns 409. A new key allows a genuinely identical meal. Keep receipts for this project.

### Calculations and Dashboard

- 100.25 kcal becomes 10025 units; 0.75 g becomes 75 units. Sum fetched values in Python
  integers, including duplicate meals; empty sums are zero. Format without float conversion.
- For each nutrient independently, I is actual and T is positive target in hundredths:
  remaining = max(T - I, 0), exceeded = max(I - T, 0), percentage = 100 * I / T.
  Determine below/reached/exceeded by exact comparisons before display rounding.
- Use Decimal for indicator fill, clamped to 0..100. Prefer no numeric percentage label:
  show exact intake/target and remaining/reached/exceeded text so near-target rounding
  cannot misrepresent the status. Full indicators never hide an exceeded amount.
- Without T, show intake and target setup navigation, not a percentage or target status.
  An empty day with configured targets shows zero fill and full remaining amounts.
- Use a restrained Bootstrap grid with date control, two nutrient summaries, and meal
  list/edit/delete controls. Stack fields on narrow screens. Include labels, kcal/g units,
  visible keyboard focus, native progress semantics, and associated field-error text.
  Do not depend on color alone for status, or add explanatory marketing content.

### Input Validation and Error Handling

- Server validation is authoritative; HTML required/min/step attributes assist only.
  Trim food names, reject blanks, match the four categories exactly, and validate canonical
  dates with datetime.date, accepting valid leap days and rejecting invalid calendar dates.
- After trimming surrounding whitespace, require the complete numeric input to match
  `[0-9]+(?:\.[0-9]{1,2})?` as confirmed in BR-12. Accept 0, 0.5, and 100.25 notation;
  reject .5, +1, 1., 1e2, blank, negative, malformed, non-finite, and excess fractional
  digits including trailing zeros. Construct Decimal from the string, never float;
  check finite value and scale before conversion. Meals allow zero, targets do not.
- Reject per-field values outside SQLite's signed 64-bit scaled range with a field error,
  not clipping or a crash. This is a technical representation limit, not a dietary cap.
  Bound numeric token length before conversion; sum outside SQLite to avoid SUM overflow.
- Invalid fields: 422 HTML with entered values/errors; no writes. Missing IDs: 404. Bad
  CSRF: 400. Conflicting committed replay: 409. Invalid query dates: 400 with correction
  guidance, never silent replacement by today.
- Use request-scoped sqlite3 connections with autocommit=False, explicit transaction
  contexts, and teardown closure. Mutation and receipt commit together. Roll back on
  execute/commit failure; catch sqlite3 errors and binding overflow without swallowing
  field-validation or missing-record responses. Never flash success before commit.
- Database unavailable/locked: 503 with retry guidance. Unexpected errors: generic 500
  and server-side logging. Do not expose SQL/tracebacks or log sensitive meal contents.
  Never replace a failed query with an empty day or missing targets.
- Use SQL parameter binding, Jinja escaping, a stable locally configured secret, and
  session CSRF validation on every POST. No meal data in cookie sessions. These measures
  do not authorize public hosting of this unauthenticated personal app.

### Testing Strategy and Acceptance Mapping

Use unittest discovery, Flask test client, subTest, and unittest.mock. Each test creates
a fresh application and TemporaryDirectory file database; close connections before
Windows cleanup. Inject read/execute/pre-commit failures through a connection wrapper,
while retaining real SQLite rollback/persistence assertions. No API test product required.

| Acceptance criteria | Planned coverage |
|---------------------|------------------|
| AC-01, AC-02 | Add, redirect, date-filtered list, displayed fields |
| AC-03, AC-04 | Edit ID, delete one/last, no unintended changes |
| AC-05, AC-06 | Required/date/category/numeric/precision errors, zero/decimals |
| AC-07, AC-08, AC-09 | Known sums, all categories, isolated dates |
| AC-10 | Empty day with and without targets |
| AC-11, AC-12 | Positive/decimal targets, invalid preservation, recalculation |
| AC-13, AC-14, AC-15 | Below/equal/above, mixed nutrients, clamped fill |
| AC-16 | Add/edit/delete update the next dashboard response |
| AC-17 | Both and individually absent targets, no misleading progress |
| AC-18 | Reopen app on same file; retained edits/deletions/targets |
| AC-19 | Move a meal and verify both dates |
| AC-20 | Four categories, invalid category, independent identical meals |
| AC-21 | Failed reads/writes/commit, rollback, retry, lost-response replay |
| AC-22 | Two dates reuse goals; updates alter historical progress only |
| AC-23 | 0.1 + 0.2 displays 0.3 before/after reopen |

Additional boundaries: 0.01 target, 1.230 rejection, valid/invalid leap dates, storage
maximum and next hundredth, daily sums beyond 64 bits, missing IDs, CSRF, replay conflict,
and replay after deletion. Test real commit followed by a discarded response, then replay
the same key and verify one effect; a fresh key must permit an identical meal.

Manual checks at 375px and 1280px cover text fit, responsive controls, keyboard operation,
focus/error discovery, and non-color statuses. Run NFR-01/SC-001's five-user walkthrough:
at least four add a meal and identify both totals without help. Review organization and
README commands for NFR-05. Record actual outcomes during implementation, not planning.

### Delivery Sequence

1. Establish package/configuration, local Bootstrap CSS, schema, and isolated tests.
2. Implement/test shared validation, exact conversion, and exact amount formatting before
  US1; add daily summation in US2 and target comparison in US3.
3. Implement/test transactional database helpers and submission receipts.
4. Implement meal list/forms and edit/delete flows using these helpers.
5. Implement shared target form and dashboard; verify historical/date-moving behavior.
6. Complete failure/retry tests, manual usability/accessibility checks, and run/test docs.

## Complexity Tracking

No constitution violations. The internal receipt table is justified by AC-21's safe-retry
requirement, not a new user feature. Direct helpers avoid additional architecture layers.
