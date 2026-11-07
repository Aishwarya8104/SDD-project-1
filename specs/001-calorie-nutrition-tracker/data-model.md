# Data Model: Calorie and Nutrition Tracker

**Date**: 2026-11-03 | **Storage**: SQLite via sqlite3

## Representation

Nutrition amounts are integer hundredths: kcal x 100 and grams x 100. Validate original
strings before exact Decimal conversion; never round invalid input into valid precision.
Each stored value must fit 0..9223372036854775807 units, or at most 92233720368547758.07
in the displayed unit. This is a technical storage limit, not a dietary restriction.
Sum fetched values in Python integers, avoiding SQLite aggregate overflow. Format without
float conversion. Calendar dates are validated, canonical YYYY-MM-DD strings, not timestamps.

## Meal

Table: `meals`.

| Field | SQLite type | Rules |
|-------|-------------|-------|
| id | INTEGER PRIMARY KEY | Generated immutable identity; never identify by food name |
| meal_date | TEXT NOT NULL | Valid calendar date; index for selected-date queries |
| food_name | TEXT NOT NULL | Trimmed and nonblank; duplicates allowed |
| category | TEXT NOT NULL | Breakfast, Lunch, Dinner, or Snacks |
| calories_hundredths | INTEGER NOT NULL | Actual integer storage type; value >= 0 |
| protein_hundredths | INTEGER NOT NULL | Actual integer storage type; value >= 0 |

CHECK constraints enforce nonblank name, four categories, typeof numeric fields = integer,
and non-negative amounts. Actual date validity and input precision are enforced in shared
server validation; text-shape checks alone do not validate dates. Parameterized queries
retrieve all meals for exactly one date, ordered by ID for a stable list.

Lifecycle: absent -> added -> edited (including date changes) -> deleted. Each mutation
commits with its receipt. Distinct IDs allow identical meals; edit/delete affects one ID.
No persisted totals, soft deletes, nutrition lookup, or serving-size data are needed.

## Reusable Nutrition Targets

Table: `nutrition_targets`.

| Field | SQLite type | Rules |
|-------|-------------|-------|
| id | INTEGER PRIMARY KEY | CHECK id = 1; at most one row |
| calorie_target_hundredths | INTEGER nullable | NULL or actual integer > 0 |
| protein_target_hundredths | INTEGER nullable | NULL or actual integer > 0 |

Initialize row 1 with both fields NULL. Absence of the row is also read as both targets
missing. Normal target form submissions require both positive values and upsert row 1;
blanks are invalid and never clear saved goals. Reading handles either absent nutrient
independently, supporting AC-17 without introducing a goal-removal feature.

No date, effective date, user identity, or target history column exists. The current pair
applies to every selected date, including historical dates; updates do not alter meals.

## Submission Receipt

Table: `submission_receipts`. Internal reliability data required by AC-21, not a new feature.

| Field | SQLite type | Rules |
|-------|-------------|-------|
| submission_key | TEXT PRIMARY KEY NOT NULL | Random server-issued form token |
| operation | TEXT NOT NULL | add_meal, edit_meal, delete_meal, save_targets |
| resource_id | INTEGER nullable | Meal ID for edit/delete; NULL otherwise |
| payload_json | TEXT NOT NULL | Canonical validated fields/return context, excluding tokens |
| redirect_path | TEXT NOT NULL | Validated app-local dashboard destination |

Use deterministic json.dumps serialization, not manually concatenated JSON. Do not make
meal contents unique. Receipts do not reference meals with a cascading foreign key;
deletion must not erase retry protection. Retain receipts for the assignment's lifetime.

1. Validate CSRF/key shape, then validate/canonicalize fields.
2. Begin a short transaction. Insert a pending receipt as the first write using targeted
   ON CONFLICT(submission_key) DO NOTHING; a pending receipt may never commit alone.
3. On conflict, compare operation, resource ID, and payload. Matching replay returns the
   stored redirect without mutation; changed intent returns 409. This check precedes
   requiring an edit/delete meal to exist, since an earlier request may have removed it.
4. On a new key, require any target meal to exist, perform the mutation, set its final
   redirect, and commit everything together. Any error rolls back receipt and mutation.
5. After a lost response, reposting the same key returns the saved result. A new form key
   represents a new intent and may add an identical meal. Do not retry unknown writes
   automatically with a fresh key.

## Derived Daily Summary

Not persisted. Read the selected day's meals and current target row from the same read
transaction/snapshot. Evaluate calories and protein independently:

| Value | Rule |
|-------|------|
| actual | Sum selected-date meal integers; zero if empty |
| target | Current nutrient target or absent |
| remaining | max(target - actual, 0), only if target exists |
| exceeded | max(actual - target, 0), only if target exists |
| status | missing_target, below, reached, exceeded |
| indicator_fill | min(100, 100 x actual / target), or absent |

Status uses exact integer comparison, not rounded percentages. Indicator rendering may
round Decimal values; display exact amount/status text and omit numeric percentage labels
so slight excess is never represented as exactly reached.

## Connection and Initialization Boundaries

Use a request-scoped connection with autocommit=False, transaction contexts for mutations,
and close on teardown. A connection context commits/rolls back but does not close it.
Initialize schema through an explicit CLI command, never destructively per request.
Repeated initialization must not erase meals, receipts, or saved targets. Commit schema
setup before use. Store the database in the instance directory, outside static assets.
Handle read/write/commit failures and numeric binding overflow without false success or
empty-day fallbacks. Read-only transactions are closed without applying business writes.