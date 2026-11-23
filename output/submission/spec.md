# ExperimentIQ technical specification

Revision 3, 2026-11-23. Scope: **intake through review and Markdown export**.
The revision 3 contract below supersedes the earlier increment descriptions.

## Runtime and structure

Next.js App Router + TypeScript + Tailwind; Python 3.11+ + FastAPI + Pydantic v2;
official OpenAI async SDK. `backend/app/{api,llm,schemas,services}` separate routing,
provider integration, data contracts, and deterministic policy. No experiment-history
database or user authentication; Redis stores production quota state.

## Current API

`GET /health` → 200 `{"status":"ok","service":"experimentiq","version":"0.1.0"}`.
It needs no credentials and does not test the provider.

`POST /api/v1/experiments/extract` accepts JSON:

```json
{
  "objective": "We want to test personalized credit-card promotions versus generic promotions for 100,000 eligible customers. Our goal is to increase average card spending by 5%.",
  "metric_type": "continuous",
  "population_size": null,
  "primary_metric": null,
  "baseline_mean": null,
  "baseline_sd": null,
  "baseline_conversion_rate": null,
  "target_relative_uplift": null
}
```

Only `objective` is required. Unknown values are null, never 0. Optional form inputs
are explicit user confirmation. `metric_type` accepts binary/continuous or null.
Objective: trimmed 20–4000 chars. Text fields: 1–200 chars. Population: integer
2–1,000,000,000. Baseline mean: finite, absolute value ≤1e12. SD: >0 and ≤1e12.
Conversion rate: strictly between 0 and 1. Relative uplift: >0 and ≤10 (positive
increase only in this slice, decimal: 5% = 0.05). Reject extra fields, booleans as
numbers, non-finite numbers, and wrong JSON types. Body maximum 24 KiB, including
chunked requests. Cross-field rejection: binary target rate must be <1; continuous
relative uplift needs a positive mean when provided; incompatible baseline fields
for a selected metric type are rejected. Missing values are allowed.

Response 200, abbreviated example (all seven fact keys are always present):

```json
{
  "request_id": "server-generated-uuid",
  "status": "missing_information",
  "states": ["input_received", "facts_extracted", "missing_info"],
  "facts": {
    "population_size": {"value":100000,"source":"llm_extracted","evidence":"100,000 eligible customers","requires_confirmation":true},
    "metric_type": {"value":"continuous","source":"user_provided","evidence":null,"requires_confirmation":false},
    "baseline_mean": {"value":null,"source":"missing","evidence":null,"requires_confirmation":false}
  },
  "questions": [{"field":"baseline_mean","reason":"missing","question":"What is the baseline mean in the metric's units?"}],
  "conflicts": [],
  "statistics_status": "not_computed",
  "metadata": {"model":"gpt-4.1-mini","prompt_version":"extract_v2","latency_ms":1234,"attempts":1,"input_tokens":500,"output_tokens":200,"estimated_cost_usd":null}
}
```

Full executable response schema: `/openapi.json` and `/docs`. `Fact` values are
field-validated in `Extraction`/`ExperimentInput` before normalization; response
fact keys use a fixed schema. Exact supporting quote required for each non-null
model field; quote must appear in objective. Quoted extraction still needs human
confirmation. Model cannot set source, confirmation state, questions, or status.
Conflicting explicit/extracted values keep the explicit value and record both.
Primary-metric wording differences alone are not proven semantic contradictions:
retain the explicit definition and both labels in optional `metric_wording_note`
(`supplied_value`, `extracted_value`, `message`). This is an informational note;
numeric and outcome-type differences still trigger `needs_attention`.

Status priority: `needs_attention` for conflicts or incompatible merged values,
then `missing_information` for missing/confirmation questions, otherwise
`extraction_complete`. This never means a valid design or sufficient power.
Required questions: metric type, primary metric, population, relative uplift;
continuous additionally mean/SD; binary additionally conversion. Every other
unconfirmed extracted field also receives a confirmation question. Irrelevant
numeric inputs receive attention warnings; they are never used for calculation.

## Errors and resource controls

Envelope: `{"error":{"code":"...","message":"...","request_id":"...","fields":[]}}`.
All documented errors have a generated request ID, safe text, and field names only.
Validation uses fixed corrective messages for the specific failed constraint, with
affected field names even for cross-field errors. No raw validation input is echoed.

| HTTP | Code | Meaning |
|---|---|---|
| 413 | payload_too_large | Body exceeds 24 KiB |
| 415 | unsupported_media_type | POST must use application/json |
| 422 | invalid_input | Malformed JSON or field/cross-field validation failure |
| 429 | rate_limited | Per-client 5/min, global 30/min, or 3 concurrent calls; Retry-After |
| 502 | llm_invalid_response | Invalid structure/evidence after one repair |
| 503 | llm_not_configured | Backend key absent |
| 503 | llm_unavailable | Provider transport/auth/quota/refusal failure |
| 504 | llm_timeout | Overall 45-second deadline or provider timeout |
| 500 | internal_error | Unexpected failure; no exception details returned |

SDK timeout 15 seconds/attempt, SDK transport retries 1, schema/evidence repair
once; entire extraction is capped at 45 seconds. Frontend aborts after 50 seconds.
Responses are not cached. CORS allows configured origins only, no cookies; expose
request ID and Retry-After. Default origins localhost:3000 and 127.0.0.1:3000.
Input cap, per-process rate limits, token cap (2500), and no automatic UI retries
bound development usage. Deployment requires shared/edge abuse protection.

## UI acceptance

One responsive workbench: editable objective, load synthetic example, optional
confirmed assumptions, primary submit button, pending state, safe actionable errors,
fact cards with evidence/provenance, and questions. Empty inputs stay null. Inputs
use decimals for rates with explicit hints. All controls have labels, errors use
alerts, results use a live region, keyboard focus is visible. Edits clear previous
results/errors. Requests disable editing; unmount aborts in-flight work. There is
no fixture-success mode or API key field in the shipped UI.
The selected outcome type shows only compatible baseline inputs. Changing to
Continuous clears the conversion rate; changing to Binary clears mean/SD, as
explained beside the selector. Unknown type shows all baseline inputs.
Two explicit demo buttons load either a complete synthetic preset (objective plus
confirmed inputs) or the original incomplete objective. The complete preset uses
population 100,000, a continuous spending metric, mean 200 USD, SD 100 USD, and
relative increase 0.05; conversion rate remains null because it is inapplicable.
It opens the input section and explains that values are fictional demo assumptions,
not AI-inferred facts. Loading never submits automatically. Successful full intake
has no missing questions; it can then proceed to design generation. Statistics are computed only in the next explicit, confirmed stage.

## Design proposal increment

`POST /api/v1/experiments/design` accepts the same `ExperimentInput` as extraction.
The frontend enables **Generate experiment design** after a successful extraction,
including when baselines are missing; unresolved extraction conflicts disable it.
Editing/reloading an example clears both extraction and design. This endpoint can
also be used directly; it validates inputs but does not claim a completed extraction.

The backend sends the original objective and explicitly entered, validated inputs
to a separate `design_v1` prompt. It does not trust client-supplied provenance or
promote prose extractions to confirmed inputs. No second extraction call is needed.
The returned `planning_inputs` is the unchanged validated request, never LLM output.

`DesignDraft`: design_family (`independent_two_arm`, `unsupported`, `unclear`),
hypothesis, treatment, control, randomization_unit, primary_metric,
observation_period, allocation, rationale, assumptions, open_questions, limitations.
Text fields are bounded; unknown/unsupported fields may be null. A draft in the
independent-two-arm family must provide all seven core design fields. All generated
fields are suggestions. The explicit primary metric, if supplied, is retained and
marked `user_provided`; otherwise the generated metric is `llm_suggested`.

`DesignResponse`: request_id, status (`proposal_ready` or `needs_attention` for
unsupported/unclear families), design, source (`llm_suggested`), metric_source,
planning_inputs, statistics_status (`not_computed`), metadata. All numeric
planning inputs remain unchanged, including null mean/SD. The proposal cannot
provide an executable statistical result. A proposal is not a validated design.

Same body/rate/concurrency limits, error envelope, transport/schema retry budget,
45-second stage deadline, and metadata logging as extraction. Provider failures
leave extraction visible and allow retrying design. The UI provides a distinct proposal screen, Back to intake control, and
confirmed progression to the statistics and review stages described below.

## Revision 3: complete workflow contract

Four navigable stages: intake, design proposal, statistics, review/export. Only
reached stages are clickable. Next buttons state the destination and explain
missing requirements. Editing intake invalidates all downstream state; changing
statistical assumptions invalidates the calculation and review. Back preserves
unchanged work. No automatic submission or approval.

Design must be supported and explicitly accepted before statistics. Calculator
inputs are user-entered or prefilled from explicit intake fields, never extracted
prose or generated numbers. The statistical form visibly defaults alpha=.05,
power=.8, treatment/control ratio=1; the user confirms these numerical settings
and independent, two-arm, fixed-horizon assumptions. Absolute MDE is supported
there, including continuous baselines <=0. Relative effects are positive increases.

POST /api/v1/statistics/sample-size accepts StatisticalRequest: design_family,
design_confirmed, independent_units, primary_metric, metric_type, population_size,
baseline_mean, baseline_sd, baseline_conversion_rate, effect_type (absolute/relative),
effect_value, alpha, power, allocation_ratio. Unknowns are null. Finite alpha is
[.000001,.5], power (.5,.999999], ratio [.01,100], effect (0,1e12]. Baseline
ranges match intake. Binary target must be strictly <1; relative continuous MDE
requires positive mean. Incompatible baseline fields are rejected. These explicit
operational bounds avoid numerical singularities and excessive resource usage.

Result: request_id, source=derived, status computed/insufficient_information/
unsupported_design/calculation_limit, inputs snapshot, n_control/n_treatment/total,
actual_allocation_ratio, achieved_power (normal approximation), absolute_effect,
target_rate, feasible, formula_id, assumptions, questions, warnings. Uncomputed
states have null numeric results. Per-arm count is capped at 1 billion; minimum
2/arm. Compute the specified closed-form approximations, round up, and verify
power using actual rounded allocation; bounded upward search corrects rounding.
Sparse binary counts and small continuous arms have explicit approximation warnings.
Pool feasibility is required for a complete result but does not prevent reviewing
an infeasible plan. No claim of observed outcomes or exact power.

POST /api/v1/experiments/review accepts objective, DesignDraft, StatisticalRequest.
It validates supported/confirmed design, matching primary metric/family, and
recomputes statistics server-side. Client-supplied sample sizes/results are forbidden.
Missing/unsupported statistics return actionable 422 before any provider call.
Critic receives the design and immutable calculator result in a separate critic_v1
call with the established time/retry/limit budget. Critique has summary, bounded
ranked risks (category, severity, evidence, explanation, recommendation), unresolved
assumptions. It cannot supply a statistical result. Server-derived feasibility and
approximation warnings remain independent of AI opinions. Proposal questions and
assumptions remain visible, never silently resolved by critique.

ReviewResponse includes request_id, objective, design, derived statistics, critique,
checks, status (review_complete/review_needs_attention), metadata. Export is a
client-side Markdown draft containing all of these plus intake provenance and
stage request IDs. User acknowledges risks before downloading. High risks,
infeasibility or unresolved assumptions keep the report marked needs attention;
export is documentation, never permission to run an experiment.

Validation: SciPy normal quantiles/CDF; compare continuous counts/power to
statsmodels NormalIndPower and binary counts/power to its two-proportion functions,
including unequal allocations. Provider-mocked browser tests must traverse every
stage, download and inspect report content, test disabled gates, error retry and
stale-result invalidation on desktop and mobile.


## Formula definitions and reference checks

Let r=n_treatment/n_control, z_a=Phi^-1(1-alpha/2), z_b=Phi^-1(power).
Continuous n_control=ceil((z_a+z_b)^2 sigma^2(1+1/r)/delta^2).
Binary q=(p0+r*p1)/(1+r),
n_control=ceil([z_a sqrt(q(1-q)(1+1/r)) +
z_b sqrt(p0(1-p0)+p1(1-p1)/r)]^2/(p1-p0)^2).
n_treatment=ceil(r*n_control), with minimum 2 per arm. Report actual rounded ratio.
Re-evaluate two-sided normal power after rounding; at most 64 upward corrections
of max(1,ceil(.001*n_control)) are permitted before calculation_limit.
Operational bounds protect against underflow/overflow. Reference tests compare
against Statsmodels: sigma=1, delta=.5 gives 63/arm; complete demo gives 1570/arm.

## Production configuration

Production mode requires an HTTPS origin allowlist and shared Redis REST quotas.
The atomic script uses Redis time, a sliding 60-second request window, 75-second
concurrency leases and a UTC daily request cap. Limits survive process restarts.
Quota errors fail closed with 503; exhausted caps return 429. Per-process limits
remain as a first guard. No untrusted forwarded client addresses are used.
See docs/deployment.md for free-hosting and verification requirements.
