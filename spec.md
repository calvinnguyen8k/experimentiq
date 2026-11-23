# ExperimentIQ technical specification

Revision 1, 2026-11-23. Implemented scope: **extraction only**. This document extends
the handoff; future contracts below are design commitments, not working endpoints.

## Runtime and structure

Next.js App Router + TypeScript + Tailwind; Python 3.11+ + FastAPI + Pydantic v2;
official OpenAI async SDK. `backend/app/{api,llm,schemas,services}` separate routing,
provider integration, data contracts, and deterministic policy. No database/auth.

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
  "statistics_status": "not_implemented",
  "metadata": {"model":"gpt-4.1-mini","prompt_version":"extract_v1","latency_ms":1234,"attempts":1,"input_tokens":500,"output_tokens":200,"estimated_cost_usd":null}
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

## Future typed contracts (not implemented this increment)

- `ExperimentDesign`: hypothesis, treatment/control, randomization_unit,
  primary_outcome, observation_period, allocation ratio, assumptions. Each proposed
  field carries `llm_suggested` provenance; no assumed numeric baseline accepted.
- `StatisticalRequest`: design_family (`independent_two_arm` only), metric_type,
  confirmed numeric baselines, effect_type (`absolute`/`relative`), effect_value,
  alpha (default .05), power (.80), allocation_ratio (treatment/control, 1), pool.
  Require 0<alpha<1, .5<power<1, positive ratio/SD/effect; binary p0,p1 in (0,1).
  Relative continuous MDE requires positive baseline mean; negative/zero means
  require an explicitly supplied absolute effect.
- `StatisticalResult`: status (`computed`, `insufficient_information`,
  `unsupported_design`), n_control/n_treatment/total, feasible, immutable input
  snapshot, formula_id, assumptions, missing_questions. Missing/unsupported states
  carry null numbers. Designs involving clustering, sequential tests, repeated
  measures, pairing, multiple arms, time series, or heavy interference are blocked.
- `DesignRisk`: category, severity (high/medium/low), evidence, explanation,
  recommendation. `ExperimentReview`: design, ranked risks, unresolved assumptions.
- `ReviewResponse`: request ID, stage history, facts, design, immutable statistics,
  review, conflicts, questions, metadata, status. `APIError` is implemented now.
- Planned routes: `POST /api/v1/statistics/sample-size` and
  `POST /api/v1/experiments/review`. Unimplemented routes return 404.

### Statistical implementation contract for next increments

Let r=n_treatment/n_control, z_a=Phi^-1(1-alpha/2), z_b=Phi^-1(power).
Continuous normal approximation: n_control=ceil((z_a+z_b)^2 sigma^2(1+1/r)/delta^2).
Binary pooled-null/unpooled-alternative approximation: q=(p0+r*p1)/(1+r);
n_control=ceil([z_a sqrt(q(1-q)(1+1/r)) +
z_b sqrt(p0(1-p0)+p1(1-p1)/r)]^2/(p1-p0)^2).
n_treatment=ceil(r*n_control); report actual rounded ratio. Both are planning
approximations, two-sided independent samples; no continuity correction, no claim
of exact power. Recheck achieved approximation after rounding in implementation.
Feasible iff total<=pool. For 1:1 continuous, sigma=1, delta=.5, alpha=.05, power=.8
gives 63 per arm; binary p0=.10,p1=.12 gives 3841 per arm under this formula.
These reference values require independent verification when implementing the
engine; no calculator is delivered in this increment.

## Verification and next increments

1. Current: validate contracts, missing values, evidence, conflicts, error mapping,
   rate/body limits, provider SDK request/response handling, UI workflow and build.
2. Design generation and confirmation interaction.
3. SciPy-based statistics with independently verified reference tests.
4. Critique, contradiction checks, Markdown export.
5. ~20 synthetic evaluation cases, real model scoring, production hardening and
   deployment. Track schema %, extraction accuracy, risk recall, unsupported
   assumptions, valid tool calls, median/p95 latency, cost; no scores claimed yet.
