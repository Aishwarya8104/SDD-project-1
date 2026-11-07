# Feature Specification: Calorie and Nutrition Tracker

**Feature Branch**: Not created; no branch hook is configured.

**Created**: 2026-11-03

**Status**: Ready for planning - target applicability confirmed.

**Input**: User description: "Create a simple, beginner-level application for dated meal
management, daily calorie and protein totals, daily targets, and progress tracking, with
validation, consistent data storage, and clear error handling."

## Clarifications

### Session 2026-11-03

- Q: How should calorie, protein, and target inputs with more than two decimal places be
  handled? -> A: Accept up to two decimal places; reject greater precision with a clear
  message rather than rounding before saving.
- Q: Which numeric notation is accepted for meal amounts and targets? -> A: Digits with
  an optional decimal point followed by one or two digits, such as 0, 0.5, and 100.25;
  reject .5, +1, exponent notation, and excess precision.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record and Manage Daily Meals (Priority: P1)

As someone monitoring food intake, I want to record, view, correct, and remove meals for a
selected date so that my daily food record reflects what I consumed.

**Why this priority**: Reliable meal records are the foundation for nutrition tracking.

**Independent Test**: Without configuring targets, add a meal, view it for its date, edit
its values, and delete it. Verify each saved change and rejection of invalid input.

**Acceptance Scenarios**:

1. **Given** a selected date, **When** I save a meal with all valid required fields,
   **Then** it appears on that date with the entered details (AC-01, AC-02).
2. **Given** an existing meal, **When** I save corrected values or delete it,
   **Then** only that record changes or disappears (AC-03, AC-04).
3. **Given** missing or invalid fields, **When** I attempt to save,
   **Then** the application explains the errors and leaves saved data unchanged (AC-05).

### User Story 2 - Review Daily Nutrition Totals (Priority: P2)

As someone tracking calories and protein, I want to see totals for a selected day so that
I understand my consumption even before setting targets.

**Why this priority**: Summarizing recorded meals provides the application's core insight.

**Independent Test**: Use known meals on two dates and compare each date's summary with
the sum of its records, without configuring nutrition targets.

**Acceptance Scenarios**:

1. **Given** multiple meals on a selected date, **When** I view its summary,
   **Then** calories and protein equal the sums for that date alone (AC-07, AC-08, AC-09).
2. **Given** a daily summary, **When** I add, edit, or delete a meal,
   **Then** the totals reflect the saved records without reopening the application (AC-16).
3. **Given** a date without meals, **When** I view it,
   **Then** the list is empty and both totals are zero (AC-10).

### User Story 3 - Set Targets and Monitor Progress (Priority: P3)

As someone with personal nutrition targets, I want to set and update calorie and protein
targets and compare intake against them so that I can see what remains or is exceeded.

**Why this priority**: Progress adds context to totals but does not prevent meal tracking
when targets are absent.

**Independent Test**: With a fixed set of recorded meals, set and update targets and
verify below-target, reached, exceeded, and missing-target states for each nutrient.

**Acceptance Scenarios**:

1. **Given** no configured targets, **When** I save positive calorie and protein targets,
   **Then** their values are displayed and used for comparison (AC-11).
2. **Given** configured targets, **When** I update their values,
   **Then** progress is recalculated without changing meals (AC-12).
3. **Given** intake below, equal to, or above a target, **When** I view progress,
   **Then** the corresponding remaining, reached, or exceeded state appears (AC-13 to AC-15).
4. **Given** a missing target, **When** I view the summary,
   **Then** intake remains visible and the application prompts for that target (AC-17).
5. **Given** meals on different dates, **When** I update the current targets,
   **Then** every date uses the updated targets, including historical progress (AC-22).

### Edge Cases

- An empty or whitespace-only food name, missing category, or invalid date prevents saving.
- Blank nutrition values differ from zero; zero is valid for meals, but not for targets.
- Negative numbers, non-numeric text, and non-finite values are rejected.
- Decimal inputs must not produce visible calculation artifacts or silently change on saving.
- Meal nutrition amounts and targets with more than two decimal places are rejected,
  not rounded; previously saved values remain unchanged.
- Multiple meals, including meals with identical names, count as separate records.
- Meals on adjacent dates must not leak into each other's totals.
- Deleting the last meal returns both totals to zero.
- Moving a meal to another date updates both affected daily summaries.
- Calories may exceed their target while protein remains below its target, or vice versa.
- Missing targets must never produce a percentage, division-by-zero result, or reached state.
- Failed save, deletion, or retrieval must not be presented as a successful operation or a
  genuine empty day.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to select a calendar date and view its meal records and
  nutrition summary (AC-02, AC-09, AC-10).
- **FR-002**: Users MUST be able to add a meal with a date, food name, meal category,
  calorie amount, and protein amount (AC-01, AC-06).
- **FR-003**: The application MUST offer exactly Breakfast, Lunch, Dinner, and Snacks as
  meal categories and reject other categories (AC-05, AC-20).
- **FR-004**: The meal list MUST show each record's food name, category, calories, and
  protein for the selected date (AC-02).
- **FR-005**: Users MUST be able to edit all recorded meal details, including its date,
  and delete an existing meal (AC-03, AC-04, AC-19).
- **FR-006**: The application MUST calculate and display total calories and total protein
  from all saved meals for the selected date (AC-07, AC-08, AC-09).
- **FR-007**: Successful meal additions, edits, and deletions MUST update affected totals
  and any configured progress in the current view (AC-16, AC-19).
- **FR-008**: Users MUST be able to set and update positive calorie and protein targets;
  invalid changes MUST preserve previously saved targets (AC-11, AC-12).
- **FR-009**: The application MUST display actual intake and the applicable configured
  target separately for calories and protein (AC-13 to AC-15).
- **FR-010**: For each configured nutrient target, the application MUST show a simple
  progress indicator and distinguish below-target, reached, and exceeded states (AC-13 to AC-15).
- **FR-011**: The application MUST show remaining amounts below target and exceeded
  amounts above target without presenting negative remaining values (AC-13 to AC-15).
- **FR-012**: When a nutrient has no applicable target, the application MUST prompt the
  user to set it, keep actual intake visible, and suppress target-based progress for that
  nutrient (AC-17).
- **FR-013**: Required fields and numeric values MUST be validated before saving meals
  or targets, with clear messages identifying invalid fields. Calorie and protein amounts
  and targets MUST accept up to two decimal places and reject greater precision without
  silently rounding or changing saved values, using the numeric notation defined in BR-12
  (AC-05, AC-06, AC-11).
- **FR-014**: Saved meals and targets MUST be retrieved consistently after leaving and
  reopening the application; edits and deletions MUST remain effective (AC-18).
- **FR-015**: Failed data operations MUST display a clear error, avoid reporting success,
  preserve previously saved data, and allow retry (AC-21).
- **FR-016**: One current calorie and protein target pair MUST apply to every date.
  Updating either target MUST change progress comparisons for all dates, including
  historical dates, without changing meal records or daily intake totals (AC-22).

### Business Rules

- **BR-01**: Each meal has a valid calendar date, a nonblank food name, exactly one allowed
  category, and calorie and protein values. Surrounding whitespace does not make an empty
  food name valid.
- **BR-02**: Meal nutrition amounts are finite, non-negative numbers. Zero is valid;
  missing values, negative values, and non-numeric values are invalid.
- **BR-03**: Each configured daily target is a finite number strictly greater than zero.
  An absent target is not treated as a zero target.
- **BR-04**: Daily totals sum every saved meal for the selected date across all four
  categories, including separate records with matching names. Other dates are excluded.
- **BR-05**: Saved meal modifications immediately affect the corresponding totals.
  A date change removes the contribution from the old date and adds it to the new date.
- **BR-06**: For intake I and a configured target T, progress is 100 x I / T percent.
  Below target, remaining is T - I; at target, remaining is zero; above target,
  exceeded is I - T. Calories and protein are evaluated independently.
- **BR-07**: A bounded visual indicator fills to at most 100%; an exceeded amount remains
  visible even when the indicator is full. A displayed percentage, if used, must not
  misrepresent an above-target amount as exactly 100%.
- **BR-08**: Without a target for a nutrient, do not calculate its percentage or assign
  below/reached/exceeded status. Do not hide intake or block meal recording.
- **BR-09**: Invalid submissions do not create or alter saved records or targets.
  Storage failures do not count as successful changes.
- **BR-10**: An empty day has zero calories and zero protein. With positive targets,
  remaining amounts equal those targets; without targets, show the setup prompt.
- **BR-11**: Targets are not date-specific and have no effective-date history. Every
  selected date uses the current configured target pair, even if its meals were recorded
  before the latest target update.
- **BR-12**: Calorie and protein amounts and targets accept whole numbers or decimals
  written as one or more ASCII digits, optionally followed by a decimal point and one or
  two ASCII digits. After surrounding whitespace is trimmed, the complete input MUST
  match `[0-9]+(?:\.[0-9]{1,2})?`. Examples 0, 0.5, and 100.25 have valid notation;
  .5, +1, 1., 1e2, and inputs with more fractional digits are invalid and MUST NOT be
  rounded into valid inputs. Meal amounts remain non-negative and configured targets
  remain positive; valid notation alone does not make zero a valid target.
  Calculations preserve accepted values.

### Scope

Included: dated meal creation, viewing, editing, and deletion; daily calorie and protein
totals; target management; daily progress; basic validation and error handling; consistent
storage and retrieval of these records.

Excluded: authentication and registration; food databases and automatic nutrition lookup;
barcode scanning; AI meal recommendations; social and community features; advanced
analytics; diet planning. No additional nutrient tracking is included.

### Constraints

- This is a beginner-level project demonstrating fundamental software concepts.
- Interface and workflows MUST remain simple; advanced configuration is outside scope.
- Users manually enter nutrition amounts per meal, not per serving or from a food lookup.
- Tracking is by calendar date, not by rolling 24-hour periods.
- No technology stack, hosting model, or storage product is selected by this specification.

### Non-Functional Requirements

- **NFR-01 - Usability**: In a walkthrough with five representative first-time users,
  at least four MUST add a meal and identify both daily totals without assistance.
- **NFR-02 - Accuracy**: All accepted calculation examples MUST match independently
  calculated expected totals, remaining amounts, and exceeded amounts, with no visible
  arithmetic artifacts. Accepted values MUST retain the precision defined in BR-12.
- **NFR-03 - Consistency**: All successful record and target changes MUST survive an
  application reopen with identical saved values; a failed change MUST not overwrite
  previously saved values.
- **NFR-04 - Error Clarity**: Each invalid-input scenario MUST identify the affected field
  and valid input rule; operational failures MUST identify the failed action and allow retry.
- **NFR-05 - Maintainability**: Delivery review MUST confirm clearly named responsibilities
  for meal management, calculations, validation, and data management, a documented project
  structure, and a single consistent definition of nutrition calculation rules.

### Acceptance Criteria

All criteria are mandatory.
Examples use the provisional units listed in Assumptions and the confirmed precision rule
in BR-12.

- **AC-01**: Given date D, saving food "Oats", Breakfast, 300 calories, and 12 protein
  creates exactly one record on D with those values.
- **AC-02**: Given saved meals on D, selecting D displays every such meal once with food
  name, category, calories, and protein; no meal from another date appears.
- **AC-03**: Given Oats on D with 300 calories and 12 protein, changing it to "Porridge",
  Lunch, 350 calories, and 15 protein updates that record without adding a duplicate.
- **AC-04**: Deleting one of two meals removes only the chosen record; deleting the last
  meal leaves an empty list and zero totals for that date.
- **AC-05**: For each missing required field, whitespace-only food name, unsupported
  category, invalid date, negative amount, non-numeric amount, or non-finite amount,
  saving a new or edited meal fails with a field-specific message and unchanged saved data.
- **AC-06**: A meal with zero calories and zero protein saves successfully; a meal with
  100.25 calories and 0.75 protein saves and reloads with those same values. For each
  nutrition field, entering 1.234 when creating or editing a meal rejects the submission
  with a message stating that at most two decimal places are allowed; no record is
  created or changed and the value is not rounded before saving.
  For each field, 0.5 saves unchanged, while .5, +1, 1., 1e2, and 1.230 are rejected
  with field-specific notation or precision messages and no record creation or change.
- **AC-07**: Meals with 300, 450, 600, and 150 calories in Breakfast, Lunch, Dinner, and
  Snacks on D produce exactly 1500 total calories for D.
- **AC-08**: Meals with 12, 25.5, 40, and 7.5 protein on D produce exactly 85 total protein.
- **AC-09**: Given 500 calories and 20 protein on D and 700 calories and 30 protein on
  another date E, selecting D shows 500 and 20; selecting E shows 700 and 30.
- **AC-10**: Selecting a date with no meals displays an empty-state message and both
  totals as zero. With configured targets, remaining equals each target; otherwise the
  target setup prompt appears.
- **AC-11**: Saving targets of 2000 calories and 100 protein displays those values.
  Attempting blank, zero, negative, non-numeric, or non-finite target values displays
  field-specific errors and does not change saved targets. Targets of 2000.25 calories
  and 100.75 protein save and reload unchanged. Entering 1.234 for either target rejects
  the submission with a message stating that at most two decimal places are allowed,
  without creating or changing targets or rounding the input before saving.
  For either target, 0.5 saves unchanged, while .5, +1, 1., 1e2, and 1.230 are rejected
  with field-specific notation or precision messages and unchanged saved targets.
- **AC-12**: With intake of 1500 calories and 75 protein, changing targets from 2000/100
  to 1800/90 displays remaining amounts of 300/15 without altering any meal.
- **AC-13**: With targets 2000/100 and intake 1500/75, progress displays actual and
  target values, remaining amounts of 500/25, and indicators representing 75% for both.
- **AC-14**: With targets 2000/100 and intake 2000/100, both nutrients show reached,
  remaining zero, and fully filled indicators, without an exceeded amount greater than zero.
- **AC-15**: With targets 2000/100 and intake 2200/80, calories show exceeded by 200
  with a full indicator, while protein shows remaining 20 with an 80% indicator.
- **AC-16**: Starting with targets 2000/100 and intake 500/20, adding a 100/5 meal shows
  600/25 and remaining 1400/75; editing it to 200/10 shows 700/30 and remaining 1300/70;
  deleting it restores 500/20 and remaining 1500/80 without reopening the application.
- **AC-17**: With meals but no targets, both actual totals remain visible, the user is
  prompted to set targets, and no target percentages or reached/exceeded labels appear.
  If only one target is absent, apply that behavior only to the affected nutrient.
- **AC-18**: After successfully adding and editing a meal, deleting another, and saving
  targets, reopening the application retrieves exactly the remaining records and target
  values; the deleted meal does not reappear.
- **AC-19**: Moving a meal worth 100 calories and 5 protein from D to E decreases D's
  totals by 100/5 and increases E's by 100/5, leaving all other records unchanged.
- **AC-20**: Each of Breakfast, Lunch, Dinner, and Snacks can be saved as a category;
  an unsupported category cannot be saved. Two identical meal entries count twice in totals.
- **AC-21**: When saving, deleting, or loading fails, the application identifies the
  failed action, does not claim success or display a retrieval failure as an empty day,
  preserves previously saved data, and permits retry. A successful retry applies the
  intended change once without duplicate records.
- **AC-22**: Given a historical date D with intake 1500/75 and another date E with
  intake 1000/50, setting targets to 2000/100 displays those same targets for both dates,
  with remaining amounts 500/25 on D and 1000/50 on E. Updating the targets to 1800/90
  while viewing E and then revisiting D displays remaining amounts 800/40 on E and
  300/15 on D. Both dates retain their original meal records and intake totals; reopening
  the application retains the updated target pair for both dates.
- **AC-23**: Meals with 0.1 and 0.2 for each nutrient produce displayed totals of 0.3,
  without visible arithmetic artifacts; their values remain unchanged after reopening.

### Key Entities *(include if feature involves data)*

- **Meal Record**: A distinct recorded meal with a date, food name, category, calorie
  amount, and protein amount. Multiple records may share a name and category.
- **Nutrition Targets**: One current pair of optional configured positive calorie and
  protein goals, shared across every date without date-specific target history.
- **Daily Summary**: A selected date's calorie and protein totals, applicable targets,
  and derived remaining, reached, or exceeded progress. It reflects that date's meals.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least four of five first-time users can add a valid meal and correctly
  read both daily totals without assistance in a guided evaluation of task completion.
- **SC-002**: 100% of daily-total and progress examples in the acceptance criteria match
  their expected numeric results, including decimals, zero meals, and exceeded targets.
- **SC-003**: 100% of listed invalid-input cases are rejected with an actionable message
  and no change to previously saved data.
- **SC-004**: Every successful add, edit, delete, and target update is reflected in the
  next displayed summary and remains consistent after reopening the application.
- **SC-005**: All four categories and two distinct tracking dates pass the meal-management
  acceptance scenarios without cross-date inclusion or loss of saved data.

## Assumptions

These are provisional defaults, not additional confirmed business requirements. The owner
may revise them before planning; revisions require updates to affected acceptance criteria.

- **A-01**: Calories use kilocalories (kcal); protein uses grams (g).
- **A-02**: Today is selected initially using the user's local calendar date. A meal's
  explicit calendar date does not change because it is viewed on a different day.
- **A-03**: One personal record set is used without accounts, sharing, or synchronization.
- **A-04**: Display may omit insignificant zeros. A displayed percentage, if present,
  is rounded to at most two fractional digits. Input precision is confirmed in BR-12,
  not assumed.
- **A-05**: No default target is supplied. The calorie and protein target states are
  evaluated independently if one is absent; the interface need not add a target-removal feature.
- **A-06**: Meals may be assigned any valid calendar date; no date-range restriction is
  requested. Specific storage capacity limits are not established by this specification.

### Dependencies

- Users supply nutrition amounts; correctness of the food's real-world nutritional
  content is outside scope. The application is responsible for arithmetic on entered values.
- No external food service, authentication service, or existing application is required.
- The existing project constitution contains template placeholders and provides no
  ratified project-specific governance.

### Confirmed Business Decision

- **Q1 - Target applicability (2026-11-03)**: The business owner selected option C:
  "One current target pair applies to every date." Updating targets also changes
  historical progress comparisons, not historical meals or intake totals. This is a
  confirmed requirement, not a provisional assumption; see FR-016, BR-11, and AC-22.