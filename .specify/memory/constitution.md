<!--
Sync Impact Report (temporary review material; remove before committing)
Version change: unversioned scaffold -> 1.0.0 (initial adoption)
Modified principles: five undefined template slots replaced by eight concrete principles:
I. Simplicity; II. Accuracy; III. User-Friendly Design; IV. Input Validation;
V. Maintainability; VI. Data Integrity; VII. Testing; VIII. Error Handling.
Added sections: Project Scope and Constraints; Development Guidelines
(both replace unnamed scaffold sections); concrete Governance rules.
Removed sections: none; illustrative template comments and placeholders removed.
Follow-up TODOs: none. Dependent project files are intentionally unchanged.
-->
# Calorie and Nutrition Tracker Constitution

## Core Principles

### I. Simplicity

The application MUST remain suitable for a fundamentals-level project. Changes MUST serve
meal management, calorie and protein tracking, target management, or daily progress;
additional features require explicit scope approval. Prefer the smallest design that
meets the acceptance criteria. This keeps the project understandable and achievable.

### II. Accuracy

Daily totals MUST include all saved meals for the selected date and exclude other dates.
Adding, editing, or deleting a meal MUST update affected totals and progress. One consistent
set of calculation and precision rules MUST govern totals, remaining amounts, and exceeded
amounts. Missing targets MUST NOT produce target-based progress. Accurate arithmetic makes
the nutrition summary trustworthy.

### III. User-Friendly Design

Users MUST be able to record, view, edit, and delete meals, manage targets, and understand
daily progress using clearly labeled controls and visible calorie and protein units.
The interface MUST remain usable on mobile and desktop without overlapping or clipped
controls, and core workflows MUST be operable by keyboard. Empty, reached, and exceeded
states MUST be distinguishable without relying only on color. These rules make daily
tracking understandable and accessible.

### IV. Input Validation

All required inputs MUST be validated before saving. Food names MUST contain non-whitespace
text; dates and meal categories MUST be valid. Meal calories and protein MUST be finite,
non-negative numbers; configured targets MUST be finite, positive numbers. Inputs MUST
follow the approved precision rule, and invalid submissions MUST leave saved data unchanged
with field-specific messages. Validation prevents unusable records and misleading totals.

### V. Maintainability

Code MUST use descriptive names and separate interface handling, nutrition calculations,
validation, and data management into clear responsibilities. Shared calculation and
validation rules MUST NOT be duplicated. The project structure and run/test instructions
MUST be documented. This makes changes and defect diagnosis manageable for a beginner.

### VI. Data Integrity

Saved meals and nutrition targets MUST be retrieved consistently after reopening the
application. Edits and deletions MUST affect only the intended records, including when
different meals share the same name. Failed operations MUST preserve previously saved data;
successful retries MUST NOT duplicate a change. Target updates MUST follow the approved
cross-date policy without altering meal history. Reliable records keep summaries consistent
with the user's entries.

### VII. Testing

Tests MUST cover meal creation, viewing, editing, deletion, daily totals, target updates,
and progress against the specification's acceptance criteria. Coverage MUST include normal
inputs, invalid or missing values, numeric and date boundaries, decimal precision, empty
days, absent targets, reached/exceeded targets, persistence, and operation failures.
Defect fixes MUST include a regression check. This demonstrates correctness beyond the
happy path.

### VIII. Error Handling

Validation, application, and database failures MUST produce understandable messages and
leave the user able to correct inputs or retry. Failed writes MUST NOT be reported as
successful; failed retrieval MUST NOT be presented as a genuinely empty day. User-visible
messages MUST NOT expose raw database errors or internal diagnostic details. Graceful
handling prevents confusion and accidental data loss.

## Project Scope and Constraints

The project covers manually entered meals in Breakfast, Lunch, Dinner, and Snacks; date-based
calorie and protein totals; nutrition targets; and daily progress. Only calories and protein
are tracked. Authentication, food lookup, barcode scanning, AI recommendations, social
features, advanced analytics, and diet planning remain outside the approved scope.

The approved specification defines detailed behaviors, units, precision, and target
applicability. Technology choices belong in the implementation plan, not this constitution.
Scope changes MUST be approved by the project owner and reflected in the specification
before implementation.

## Development Guidelines

- Before implementation, review the specification and plan against all eight principles
	and resolve behavior-affecting ambiguities with the project owner.
- Implement small, focused changes tied to acceptance criteria; avoid unrelated cleanup
	and abstractions without a demonstrated need.
- Verify changed behavior with focused tests, including relevant failure and boundary
	cases. Before delivery, run all major functional checks and record their results.
- Review mobile, desktop, and keyboard workflows, data persistence, calculation accuracy,
	and error messages before declaring the feature complete.
- Update affected documentation when approved behavior changes. Review every proposed
	change for constitution compliance; resolve violations before acceptance.

## Governance

This constitution governs project decisions. Specifications, plans, implementation, and
reviews MUST comply; conflicts MUST be resolved before the affected work proceeds.

Amendments MUST document the proposed change, rationale, and impact on existing artifacts.
The project owner MUST approve amendments before adoption. Each adopted amendment MUST
update the version and last-amended date and identify any dependent follow-up work.

Versions follow semantic versioning: MAJOR for incompatible principle removals or
redefinitions; MINOR for new principles or materially expanded guidance; PATCH for
clarifications or editorial corrections without semantic changes. The ratification date
records initial adoption and MUST remain unchanged by later amendments.

Compliance MUST be checked during planning, change review, and final acceptance. A
violation MUST be corrected or addressed through an approved amendment; it MUST NOT be
silently waived. The Sync Impact Report is temporary review material, not governance,
and MUST be removed before committing this amendment.

**Version**: 1.0.0 | **Ratified**: 2026-11-03 | **Last Amended**: 2026-11-03
