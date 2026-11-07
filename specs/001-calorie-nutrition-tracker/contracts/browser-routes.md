# Browser Route Contract

**Date**: 2026-11-03 | **Format**: HTML and URL-encoded POST forms

No JSON API is planned. Python unittest and Flask's test client exercise these interfaces;
Postman is not required. Redirects use validated app-local destinations only.

## Common Rules

- `date` is canonical YYYY-MM-DD. Omission on dashboard/new form means today's local
  date; local browser and local server share the assignment environment. An explicitly
  invalid date is 400 with correction guidance, never silently replaced by today.
- Every POST contains a per-session `csrf_token` and a separate random `submission_key`.
  Missing/invalid CSRF is 400 before writes. Generate a fresh submission key for each
  new form intent and retain the same key when redisplaying errors. Tokens are not meal data.
- Successful writes commit then return 303 See Other to `/?date=YYYY-MM-DD`; following
  the redirect returns 200 with freshly read data. GET never mutates business data.
- Invalid fields return 422 HTML with entered values and field-specific messages, with
  no database mutation/completed receipt. Database read/write/commit failures return 503
  with retry guidance; unexpected exceptions return generic 500. No raw SQL or tracebacks.
- Matching committed-key replay returns its original redirect with no repeated effect.
  A committed key with changed canonical payload/resource is 409. Replay matching happens
  before edit/delete record existence checks. See [data-model.md](../data-model.md).
- Meal amounts allow zero; configured targets are positive. All amounts accept at most
  two decimal places. Reject extra digits including trailing zeros; do not round input.

## Routes

| Method | Path | Fields/query | Success |
|--------|------|--------------|---------|
| GET | / | Optional date | 200 dashboard with meals, both totals, current target states |
| GET | /meals/new | Optional date | 200 empty meal form with tokens |
| POST | /meals/new | meal_date, food_name, category, calories, protein, tokens | Create one meal; 303 to meal_date |
| GET | /meals/<int:meal_id>/edit | ID in path | 200 prefilled form, or 404 |
| POST | /meals/<int:meal_id>/edit | Same meal fields and tokens | Update only this ID; 303 to resulting meal_date |
| POST | /meals/<int:meal_id>/delete | return_date and tokens | Delete only this ID; 303 to return_date |
| GET | /targets | Optional date | 200 current shared targets form |
| POST | /targets | calorie_target, protein_target, return_date, tokens | Save shared pair atomically; 303 to return_date |

Hidden return_date is a validated canonical date used only for navigation. Fresh requests
for missing edit/delete IDs return 404. Unknown routes also use a clear 404 page. Form
submissions are not an excuse to add separate API endpoints or target-history routes.

## Dashboard View

Selected date is visible/changeable. Each matching meal appears once with food name,
category, kcal, g, edit link, and POST delete control. Distinct identical meals stay
distinct. A list is empty only when a successful query returns no records.

Each nutrient shows actual intake, current target if configured, and remaining/reached/
exceeded text. Native progress indicators clamp at 100; exact exceeded values remain
visible. Omit a numeric percentage label to avoid misleading rounding near a target.

Missing target: intake stays visible, setup link appears, and percentage/target status is
absent for that nutrient. Zero meals with targets means zero fill/full remaining. Every
date uses the latest target pair; no stale cached progress. Failed queries show retrieval
errors and retry navigation, never empty-day/missing-target states.

## Forms and Accessibility

Meal form exposes date, food name, category select with exactly four approved choices,
calories (kcal), and protein (g). Edit reuses the template. Targets form exposes two
current goals, not date-specific goals or history controls.

Use associated labels, native date/select inputs, min/step hints, server-rendered errors
linked to fields, and a focusable error summary. Browser validation does not replace server
validation. Preserve entries on errors and keep Jinja escaping enabled. All controls need
accessible names and visible focus. Use Bootstrap responsive grid with small CSS adjustments
at 375px and 1280px widths. Avoid clipped/overlapping controls and color-only status.