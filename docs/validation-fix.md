# Intake validation and conflict feedback fix

2026-11-23. Follow-up to the user-reported validation error and conflict warning.

## Observed causes

The original 422 combined incompatible baseline fields under Binary and returned
one generic error without field locations. After the user cleared mean/SD, their
request succeeded, but Binary still contradicted the objective's average spending.
String inequality also incorrectly portrayed two primary-metric labels as a definite
semantic conflict.

## Changes and rationale

- Cross-field validators use stable internal codes. The API maps those codes to
  fixed corrective messages and affected field names; raw inputs and exception
  text remain excluded from responses/logs.
- Outcome type shows compatible baseline inputs. Selecting Continuous clears the
  conversion rate; selecting Binary clears mean/SD. The selector explains this
  behavior, so hidden stale values cannot cause the reported invalid combination.
- Preserve the user's explicit primary metric and show both labels in an optional
  `metric_wording_note`. A wording difference alone proves neither equivalence nor
  contradiction. Numeric/type conflicts continue to trigger `needs_attention`.
- Browser tests use `.next-e2e` so they can run while the user's dev server remains
  open. The first regression run encountered the shared Next.js dev lock; no user
  process was stopped to resolve it.

## Verification

- Backend: 64 tests pass, including specific messages/fields for all four
  cross-field constraints, numeric ranges, and wording-versus-type conflicts.
- Browser: 7 tests pass, including reproducing and resolving the reported outcome
  conflict, clearing stale baselines, and field-specific validation feedback.
- Backend lint/format, frontend lint/types/production build, source secret check,
  and Git whitespace checks pass.
- Live browser extraction: the original synthetic objective, Continuous outcome,
  user-defined `mean spending per customer`, population 100,000, effect 0.05,
  unknown mean/SD. Returned model `gpt-4.1-mini-2025-04-14`, request
  `d64a85fd-eb46-4ddd-a49c-5a503d836d45`, about 4 seconds. Facts rendered successfully;
  only mean/SD remain missing, with metric wording shown as an informational note.
  This single smoke test is not an evaluation score or statistical validation.
- [Screenshot of the corrected live extraction](screenshots/corrected-intake-live.jpg).

The earlier increment log records the initial no-key environment. The user's
running backend subsequently had provider access; no credential value was read,
changed, or committed during this fix. Existing development servers remain running.
