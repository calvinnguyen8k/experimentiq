# Increment 2: complete synthetic example and design progression

2026-11-23. Adds the next usable stage after intake. Statistics, independent risk
review, and export remain future increments.

## User flow

1. Load complete synthetic example: fictional population 100,000, mean 200 USD,
   SD 100 USD, relative increase 0.05, continuous average spending. The description
   includes randomization, treatment/control, 30-day follow-up, and assumptions.
2. Extract experiment facts. The preset uses explicit form values and should reach
   Intake complete without missing questions. No request runs merely by loading it.
3. Click Generate experiment design, immediately below the extraction status.
4. Inspect the proposed hypothesis, arms, assignment unit, primary metric,
   observation period, allocation, rationale, assumptions, questions, and limitations.
5. Back to intake preserves the proposal for viewing; editing any input or loading
   an example invalidates it and requires new extraction.

The incomplete example still demonstrates unknown baselines. It may proceed to a
draft design. Unresolved numeric/type conflicts must be corrected first.

## Decisions

- Add a dedicated design endpoint and `design_v1` prompt instead of disguising a
  fixture as a working next step. The production service always calls the configured
  OpenAI provider; there is no fake-success mode.
- Share structured SDK parsing, retries, overall deadlines, safe provider errors,
  and metadata handling between stages. Keep prompts and schemas stage-specific.
- The design endpoint validates the original objective and explicit form inputs.
  It accepts no client-assigned fact provenance. Its separate `planning_inputs`
  snapshot is built from the validated request and never from the generated draft.
- Keep the user-defined primary metric even if the model paraphrases/replaces it.
  Other generated fields remain explicitly labeled AI suggestions.
- Classifications outside independent two-arm planning produce needs_attention,
  not a statistical result. This classification is model-assisted and unevaluated;
  no claim of methodological correctness is made from schema validation alone.
- Missing baselines remain null. No executable sample-size/result field exists in
  the proposal schema. Numeric calculations belong to the future Python engine.
- Keep extraction visible on design failure; allow retry without repeating intake.
  Share rate/concurrency limits across extraction and design.

## Verification

- 75 backend tests pass, including unchanged extraction regressions, strict design
  parsing, immutable planning inputs, missing baselines, unsupported/unclear states,
  invalid provider output, missing credentials, and shared limits.
- 10 browser tests pass with mocked provider HTTP, including full-preset progression,
  missing-baseline progression, blocked conflicting inputs, back/edit behavior,
  and a recoverable design failure. The updated desktop/mobile screenshot scenarios
  were rerun separately after adding proposal layout checks.
- Backend lint/format, frontend lint/typecheck, production build, secret-pattern
  scan, and whitespace checks pass. Run build and browser tests sequentially:
  Next.js regenerates type files during dev-server startup; concurrent runs caused
  a transient missing-generated-file build error, resolved by the serial rerun.
- Successful real-model extraction was verified in the preceding increment.
  **Live design generation is not verified.** Automatic browser approval failed
  because of a usage limit when accessing localhost:3000. That restriction was not
  bypassed. The new proposal was tested only in isolated fixture-driven test
  servers; no new production request or live-browser inspection was substituted.

## Remaining work

Desktop and mobile proposal screenshots were inspected in the isolated mocked
test environment; both render without horizontal overflow:
[desktop](screenshots/design-proposal-mocked.png) and
[mobile](screenshots/mobile-design-proposal-mocked.png).

Run the new design flow against the configured live provider when browser access
is available. Then add explicit design confirmation and the deterministic binary/
continuous sample-size engine with independently verified reference calculations.
No deployment, risk-recall metric, or complete-assignment claim is made here.
