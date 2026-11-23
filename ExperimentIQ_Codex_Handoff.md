# ExperimentIQ — Codex Project Handoff

**Version:** 1.0 (planning baseline)  
**Date:** 2026-11-23  
**Status:** Specification; implementation, validation and deployment not yet completed  
**Primary goal:** Portfolio-quality AI engineering application that satisfies Week 4 Graded Assignment 4.2  
**User background:** Strong in Python/data science; limited Next.js/React experience  
**LLM provider:** OpenAI API  
**GitHub:** Account available; repository may need creation  
**Deployment:** Vercel setup outstanding; backend host not selected

> **For Codex:** Use this file as the project brief and initial implementation specification. Before coding, inspect the repository, identify what is already implemented, and work iteratively. Do not claim completed milestones without verifying them. Use synthetic experiment examples only. Never put API keys in source control.

## 1. Assignment requirements and traceability

Source: `Graded+Assignment_4.2_AI-Powered+Web+Application_brief.pdf`, Week 4, Graded Assignment 4.2 (20 points). The brief calls for an individually built, tested, deployed, documented *real AI-powered web application*, not a notebook or bare prototype.

### Mandatory constraints

- Solve a real problem for a specific user.
- Include at least one AI capability and a usable web UI.
- Deploy to a publicly accessible live URL.
- Use a public GitHub repository and GitHub Actions workflow.
- Never hardcode secrets.
- Include a useful README.
- At least **5 meaningful commits** and **3 unit tests**.
- Input validation and a secrets check.
- Basic monitoring/analytics.
- README, a **2-minute demo**, **1-page reflection**, and **one GitHub issue for v2**.
- Test the live site in an incognito window and ensure repository/demo links are accessible.

### Required assignment phases

1. **Validate & Define:** complete all seven course idea-validation steps; document user, problem, market evidence and differentiation; create one-page PRD.
2. **Spec & Architecture:** architecture notes; `spec.md`; `CLAUDE.md` or `agents.md`; `.cursorrules`; revise spec after review.
3. **Build:** scaffold; implement functional core AI feature; >=5 meaningful commits; >=3 unit tests; validate inputs and check secrets.
4. **Deploy:** GitHub Actions; live host; environment variables; production smoke test; monitoring/analytics.
5. **Document & Reflect:** README; 2-minute demo; one-page reflection; GitHub issue for a v2 improvement.

**Source limitation:** The provided assignment brief requires **all seven idea-validation steps** but **does not enumerate them**. Obtain the exact seven steps from course material; do not present an invented checklist as fulfilling that requirement.

The assignment *recommends* Next.js 14, Tailwind, Vercel AI SDK + OpenAI/Claude, Supabase, Clerk/Supabase Auth and Vercel; these are suggestions, not binding stack constraints. The brief discourages generic chatbot wrappers, real payment processing, landing pages without real AI functionality, and CLI-only tools.

## 2. One-page PRD

### Product
**ExperimentIQ — AI-Powered Experiment Design & Validation Assistant**

### Problem
Product Managers and Data Scientists can launch A/B tests with ambiguous hypotheses, incomplete success metrics, invalid assignment/control definitions, unreliable sample-size assumptions or unrecognized confounding. These issues weaken the interpretability of experiment results. **This is a working problem hypothesis; direct user and market validation remains pending.**

### Target users
- **Primary:** Product Managers and Growth Analysts planning randomized experiments.
- **Secondary:** Data Scientists and Analytics Leads reviewing the designs.

### Value proposition
Convert a plain-English experiment proposal into a structured, defensible experiment plan with deterministic statistical checks and transparent methodological warnings, rather than merely generating chat text.

### Main user flow
1. Enter a natural-language experiment goal plus optional population, KPI and assumptions.
2. Extract known facts into a typed schema; explicitly identify missing information.
3. Generate proposed hypothesis, experiment arms, randomization unit, primary metric and observation period.
4. Request additional numeric inputs if needed; calculate sample-size feasibility using tested Python functions.
5. Critique the design for selection bias, contamination, interference, metric ambiguity and other relevant risks.
6. Show the review with rationale, assumptions, warnings and exportable Markdown report.

### MVP scope
Experiment input form; AI extraction; AI proposal; missing-information handling; deterministic sample-size engine for two-arm independent binary/continuous outcomes; AI critique; report preview/export; error handling; unit tests and evaluation suite; basic latency/cost/error monitoring.

### Exclusions (v1)
Real banking/customer data; production campaign orchestration; executing experiments; causal estimation from real outcome datasets; file uploads; multi-agent platforms; RAG; user accounts; persistent history; payment systems; multi-arm/clustered/sequential experimentation.

### Differentiation hypothesis
Specialized design review + structured responses + transparent missing-information behavior + deterministic statistics + auditable design concerns. **Validate against existing tools before claiming market differentiation.**

### Success criteria (targets, not achieved results)
- All mandatory assignment deliverables fulfilled and verifiable.
- Public app works unauthenticated/incognito with a successful end-to-end example.
- >=95% schema-valid outputs across a curated evaluation suite.
- >=90% recall on predefined high-priority experiment-design risks in the suite.
- No guessed numeric parameters passed into the sample-size calculator.
- Statistical calculations pass independently defined test cases.

## 3. Functional specification / acceptance criteria

| ID | Requirement | Acceptance criteria |
|---|---|---|
| FR-01 | Experiment intake | User can enter a plain-language business objective and optional structured inputs. |
| FR-02 | Information extraction | LLM returns schema-validated fields; facts are traceable to input; unknowns are `null` / marked missing. |
| FR-03 | Missing information | Missing baseline/variance/etc. prevents numeric computation and triggers actionable questions. |
| FR-04 | Experiment proposal | Hypothesis, treatment, control, unit of randomization, primary outcome, timeframe and assumptions documented. |
| FR-05 | Statistics | Two-sample size approximation for independent binary and continuous outcomes; explicit assumptions and feasibility. |
| FR-06 | Risk review | Critical design concerns identified and ranked with reasoning and recommended mitigation. |
| FR-07 | Iteration | Editing inputs and rerunning analysis updates the displayed results. |
| FR-08 | Report export | User can download a complete Markdown experiment review. |
| FR-09 | Robust errors | User-friendly handling of invalid input, OpenAI errors/timeouts, schema failures, and unsupported designs. |
| FR-10 | Quality evaluation | Reproducible evaluation script and scenario file produce machine-readable scores. |

### MVP UI screens
1. **Setup:** text description, experiment type, eligible population, primary metric, treatment/control, effect assumptions.
2. **AI proposal:** extracted facts, generated hypothesis, allocation design, metric and missing items.
3. **Statistical validation:** inputs, power/alpha, required sample size per arm and total, feasibility and notes.
4. **Review/export:** design summary, ranked risks, remaining questions and Markdown download.

### Suggested demo scenario (synthetic)
> We want to test personalized credit-card promotions versus generic promotions for 100,000 eligible customers. Our goal is to increase average card spending by 5%.

Expected behavior: propose a randomized two-arm comparison; recognize `100000` eligible population and relative MDE of `0.05`; ask for baseline mean spending **and spending standard deviation** before producing continuous-outcome sample size; warn about overlapping campaigns and potential interference; avoid claiming statistically valid uplift from unobserved results.

### Statistical support: precise boundaries
- **Binary:** independent two-proportion, two-sided planning approximation with baseline rate `p0`, target rate `p1`, alpha, power, allocation ratio. Ensure `0 < p0 < 1` and `0 < p1 < 1`, with no unsupported boundary-case extrapolation.
- **Continuous:** independent two-sample mean difference under a common-variance planning assumption, requiring baseline mean, standard deviation and absolute or relative MDE; alpha, power, allocation ratio.
- Default **alpha = 0.05**, **power = 0.80**, **1:1** allocation; show and allow changes.
- Record formula/test family, approximation/assumptions and inputs in result; if data insufficient, return `insufficient_information`.
- Make clear that these planning formulas are not valid by default for cluster-randomized, sequential, time-series, repeated-measures, paired, multi-arm, or interference-heavy designs.
- The LLM may choose/request an appropriate tool; the **backend alone computes the numerical result**, and the LLM cannot overwrite it.
- If allocation is 1:1 and the available pool is `N`, feasible total sample must not exceed `N`. Round appropriately and transparently to integers.

### Non-functional requirements
- **Security:** OpenAI key only in backend environment, never in frontend bundle; strict input validation and bounded payload lengths; rate limiting/abuse protection on anonymous endpoints; appropriate CORS allowlist; do not log raw sensitive data.
- **Reliability:** bounded OpenAI timeout/retry; clear degraded states; structured error responses.
- **Observability:** record request IDs, model identifier, token counts where available, latency, estimated cost, error category, validation failures; no raw personal/business text by default.
- **Accessibility:** labeled form controls, keyboard navigation, readable error descriptions and mobile-responsive UI.
- **Cost control:** token limits, configurable model, reasonable input length and simple request throttles.
- **Privacy:** synthetic/public toy data only for demo; explicit UI advisory not to paste confidential/customer data.

## 4. Technical architecture

### Recommended technology choices
- **Frontend:** Next.js + TypeScript + Tailwind CSS (Vercel).
- **Backend:** Python 3.11+ + FastAPI + Pydantic (separately hosted Python service).
- **LLM:** OpenAI API via official Python SDK; use structured JSON/schema capabilities available for the selected model.
- **Statistics:** SciPy / Statsmodels as appropriate, with isolated deterministic Python functions.
- **Tests:** pytest for backend, optional frontend tests; mocked OpenAI API calls for CI.
- **Evaluation:** Python script and checked-in synthetic JSON cases; no live API calls required for unit tests.
- **CI/CD:** GitHub Actions runs lint/type-check/unit tests/frontend build; frontend deploy via Vercel and API deploy to an explicitly selected Python host.
- **Storage/auth:** not required for MVP. Stateless requests and client-side report download.

Architecture:

```text
Browser / Next.js UI
    |
    | HTTPS JSON
    v
FastAPI backend (validate input, rate limits, orchestration)
    |
    +--> OpenAI Extractor  --> Pydantic validation
    |                           |
    +--> OpenAI Design generator <--- normalized known facts
    |                           |
    +--> deterministic Python sample-size tool (if inputs sufficient)
    |                           |
    +--> OpenAI Critic (design + immutable numeric result)
    |                           |
    +--> consistency/schema checks + provenance + error handling
    |
    v
Structured API response --> UI review --> Markdown export
```

### LLM engineering: explicit responsibilities
1. **Prompt/task decomposition:** extraction, design, independent critique; no need for separate agents or models.
2. **Structured output:** strict Pydantic contracts; reject/repair invalid structure with bounded retry.
3. **Tool calling:** define a sample-size function schema; authorize only supported types and validate numeric arguments before tool execution. A deterministic app-directed call is also acceptable for the initial vertical slice.
4. **Orchestration:** state machine tracks `input_received`, `facts_extracted`, `missing_info`, `design_generated`, `stats_computed/skipped`, `review_complete`, or `error`.
5. **Evaluation:** curate scenarios with expected fields/risks; measure schema success, extraction, recall, unsupported assumption rate, tool-call validity, latency and cost.
6. **Guardrails:** input is untrusted; don't treat user-supplied text as a new system prompt; never silently invent statistical baselines.

### Preliminary Pydantic types (extend before implementation)

```python
from typing import Literal
from pydantic import BaseModel, Field

class ExperimentInput(BaseModel):
    objective: str
    population_size: int | None = None
    primary_metric: str | None = None
    metric_type: Literal["binary", "continuous", "unknown"] = "unknown"
    baseline_mean: float | None = None
    baseline_sd: float | None = None
    baseline_conversion_rate: float | None = None  # probability in [0, 1]
    target_relative_uplift: float | None = None    # decimal, e.g. 0.05
    missing_information: list[str] = Field(default_factory=list)

class DesignRisk(BaseModel):
    category: str
    severity: Literal["high", "medium", "low"]
    explanation: str
    recommendation: str

class ExperimentReview(BaseModel):
    hypothesis: str
    treatment: str | None = None
    control: str | None = None
    randomization_unit: str | None = None
    risks: list[DesignRisk] = Field(default_factory=list)
    unresolved_assumptions: list[str] = Field(default_factory=list)
```

**Implementation note:** These are starting contracts, not complete domain models. Add a separate `StatisticalRequest`, `StatisticalResult`, `ExperimentDesign`, `APIError` and top-level `ReviewResponse` before building the endpoints. Distinguish `user_provided`, `derived`, and `llm_suggested` fields so unsupported assumptions never become calculator inputs.

### Suggested endpoints (draft, may refine in `spec.md`)
- `GET /health` — health check, no credentials.
- `POST /api/v1/experiments/extract` — parsed facts + missing values.
- `POST /api/v1/experiments/review` — orchestrated AI review and optional stats.
- `POST /api/v1/statistics/sample-size` — stand-alone deterministic validation/calculation.
- Optionally export Markdown **client-side**, avoiding a separate report endpoint.

Define request/response JSON examples, validation constraints, status/error codes, and CORS requirements in `spec.md` prior to implementation.

### Prompt design guidance
- **Extractor system instructions:** extract only supported user statements; preserve uncertainty; produce `null` for unknown numeric assumptions; never calculate sample size; return structured schema.
- **Designer instructions:** recommend a feasible randomized design with hypothesis, arms, assignment unit, KPI and timeframe; explicitly label suggestions; do not portray suggestions as user facts.
- **Critic instructions:** evaluate experiment design independently; prioritize severity; look for baseline/variance issues, selection bias, unequal exposure, spillovers, concurrent promotions, post-treatment filtering, metric problems; explain evidence and conditions; do not invent results.
- Version prompts (`extract_v1`, `design_v1`, `critic_v1`) so evaluation regressions are traceable.

### Error strategy
- Missing numeric inputs => `insufficient_information` with questions.
- Unsupported experiment type => `unsupported_design` with explanation.
- OpenAI timeout/5xx => bounded retry and then user-friendly `llm_unavailable`.
- Schema mismatch => one retry/repair path, then `llm_invalid_response`.
- Calculator invalid values => stable 4xx validation errors; never execute on unvalidated model arguments.
- Cross-stage contradictions => mark `review_needs_attention`, do not silently resolve conflicts.

## 5. Test and evaluation plan

### Required tests (minimum 3; implement more)
1. Continuous-outcome sample size matches a verified reference calculation for known alpha/power/MDE/SD.
2. Binary-outcome sample size matches a verified reference calculation for known base/target conversion.
3. Reject invalid parameter ranges and missing baselines; never fabricate inputs.
4. Validate Pydantic extraction fields/unknown states.
5. Mock OpenAI error and assert predictable API error behavior.
6. Smoke test response contract for a full synthetic experiment review.

### LLM evaluation dataset
Start with ~20 **synthetic** cases, such as:
- Well-designed simple randomized A/B test.
- Treatment and control selected from different score distributions -> selection bias.
- Missing baseline variance -> no continuous sample-size output.
- Overlapping marketing campaigns -> contamination warning.
- Incorrect unit of randomization / household spillover.
- Sample ratio mismatch concerns.
- Ambiguous KPI or lack of observation window.
- User-provided prompt injection embedded in experiment text.
- Unsupported clustered or sequential design -> explicit limitation.

Log results as JSON/CSV with prompt version and model identifier. Suggested metrics: schema-validity %, critical-risk recall %, unsupported-assumption rate, valid tool-call %, median/p95 latency and estimated cost per review. **Do not imply targets are achieved until the suite has run.**

## 6. Repository structure

```text
experimentiq/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── llm/
│   │   │   ├── extraction.py
│   │   │   ├── design.py
│   │   │   ├── critique.py
│   │   │   └── prompts/
│   │   ├── schemas/
│   │   ├── stats/
│   │   │   └── sample_size.py
│   │   └── services/
│   ├── tests/
│   └── requirements.txt
├── evals/
│   ├── cases.json
│   └── run_evals.py
├── docs/
│   ├── prd.md
│   ├── architecture.md
│   └── reflection.md
├── .github/workflows/ci.yml
├── agents.md
├── .cursorrules
├── spec.md
├── .env.example
├── .gitignore
└── README.md
```

The main file is a **Codex handoff**, not a substitute for the separate files explicitly required by the assignment. Create those files in the repository during Phases 1–2.

## 7. Phased implementation plan

### Phase 1 — Validate & Define
**Tasks:** Obtain course's original seven validation questions/steps; investigate at least three competing or adjacent solutions; interview or test with potential users as feasible; record user/problem/market evidence; validate differentiation; finalize one-page PRD.  
**Deliverable:** `docs/prd.md` plus evidence/validation notes.  
**Exit criterion:** User, pain point, differentiation and MVP scope are explicit, with unknown assumptions labeled.

### Phase 2 — Specification & Architecture
**Tasks:** Document architecture and deployment decisions; define typed API contracts and data provenance; formalize supported statistical tests; create `spec.md`, `agents.md` or `CLAUDE.md`, `.cursorrules`; review and revise spec.  
**Deliverable:** Build-ready specifications and agent instructions.  
**Exit criterion:** Core flows, interfaces, error states, inputs/outputs and testable acceptance criteria defined.

### Phase 3 — Build
**Recommended iteration order:**
1. Scaffold FastAPI and Next.js, `.env.example`, README draft and `.gitignore`.
2. Implement `/health`, validated request contracts and input form.
3. Implement **vertical slice:** UI -> backend -> OpenAI structured extraction -> Pydantic -> UI.
4. Add design generation and missing-information interaction.
5. Add independently tested deterministic sample-size engine.
6. Connect tool selection/calling, critique and consistency checks.
7. Add report preview and client-side Markdown export.
8. Add evaluation suite, API errors, rate limits, minimal logging and security checks.
9. Create at least five meaningful, incremental commits; run at least three unit tests (ideally all planned ones).

**Deliverable:** Locally functional app with repeatable tests and documented examples.  
**Exit criterion:** Demo scenario works end-to-end; tests pass; no secrets committed.

### Phase 4 — Deploy
**Tasks:** Configure GitHub Actions (backend lint/tests + frontend lint/build); set up Vercel for frontend and choose a reliable Python API host; configure `OPENAI_API_KEY` on backend only; configure allowed CORS origins and API URL; configure request limits and basic monitoring; test live app in incognito.  
**Deliverable:** Live URL, public repo, CI status, working backend and logs.  
**Exit criterion:** External user can run the full demo without authentication; keys are not exposed; test pipeline passes.

### Phase 5 — Document & Reflect
**Tasks:** Finish README with problem, architecture, screenshots, setup, assumptions, test commands, deployment and evaluation results; record a two-minute end-to-end demo; produce one-page reflection (what worked, limitations, lessons); create one GitHub issue for v2 (e.g. RAG over experimentation methodology); verify submission links.  
**Deliverable:** Submission-ready artifact bundle.  
**Exit criterion:** Every mandatory assignment item checked against the source brief.

## 8. Priority and scope management

- **P0 (must deliver):** working UI, AI extraction/design, transparent missing data, numerical engine, risk review, report, tests, public deployment, docs, assignment deliverables.
- **P1 (portfolio quality):** actual function calling, separate evaluator pipeline, per-stage tracing, provenance, robust retries and cost logging.
- **P2 (v2):** RAG knowledge base, accounts/history, outcome analysis, multi-arm experiments, advanced estimators, agents and integrations.

**Scope discipline:** Do not implement P2 until P0 is finished and publicly deployed. If time is constrained, simplify to a two-stage LLM pipeline and application-controlled stats call while preserving structured validation, deterministic calculations, and test coverage.

## 9. Operational constraints and open decisions

- **OpenAI billing/model:** Confirm account and choose a currently available model based on structured-output support, quality, cost and latency. Never assume ChatGPT subscription covers API usage.
- **Backend hosting:** Not selected. Choose a host supporting FastAPI and server-side environment variables; verify pricing and free-tier limitations when deploying.
- **Validation evidence:** Not collected; cannot claim market demand yet.
- **Assignment's seven-step checklist:** Missing from provided brief; retrieve separately.
- **Model quality:** Targets not measured. Perform tests before representing scores as achieved.
- **Real users/confidential data:** No real banking data; synthetic scenarios only.
- **User confirmation:** Portfolio-oriented, Python-first, OpenAI provider, GitHub available; Vercel setup needed. These decisions are fixed unless revised.

## 10. Codex working instructions

1. Treat this document as the initial product brief. Keep implementation aligned to explicit requirements, and propose changes only with rationale.
2. First inspect the repository structure and existing files; do not overwrite existing work casually.
3. Create the Phase 2 files (`spec.md`, `agents.md`, `.cursorrules`, architecture note) before implementing the main feature. Also materialize a concise `docs/prd.md`.
4. Implement **one vertical slice first**: web form -> FastAPI -> OpenAI structured extraction -> Pydantic validation -> displayed result.
5. Separate LLM-generated interpretations from user-supplied facts and computed statistics. No numeric hallucination fallback.
6. Use Python for statistics and LLM orchestration; TypeScript only for UI/API client where practical.
7. Unit-test the deterministic engine independently from the network and OpenAI; mock external API calls in CI.
8. Prefer explicit typed schemas, small functions and transparent error handling over large agent frameworks.
9. Commit incremental changes with meaningful messages; never commit `.env`, credentials, local secrets or production data.
10. At each phase provide: files changed, commands/tests run, results, outstanding blockers, and next concrete step.
11. Do not deploy with an unsecured unrestricted public OpenAI proxy; use limits and server-side secrets.
12. Track the assignment checklist visibly in README or project tasks and only mark verified items done.

### Suggested first Codex prompt

```text
Read ExperimentIQ_Codex_Handoff.md in full and inspect the current repository.
We are building a portfolio-quality AI experiment-design reviewer for Week 4
Graded Assignment 4.2. Use Next.js/TypeScript/Tailwind for frontend,
FastAPI/Pydantic/Python for backend, OpenAI for structured extraction and
experiment design, and deterministic Python statistics.

Start with Phase 2: create docs/prd.md, docs/architecture.md, spec.md,
agents.md and .cursorrules. Define endpoint contracts, typed data schemas,
source/provenance rules, error states and testable acceptance criteria.
Then implement only the first end-to-end vertical slice:
experiment intake form -> FastAPI -> OpenAI structured extraction ->
Pydantic validation -> rendered structured results and missing questions.

Use synthetic data only. Do not hardcode secrets. Add .env.example,
minimum automated tests, and clear local run instructions. Show file changes,
tests actually run, remaining tasks, and suggested meaningful commits.
Do not claim assignment validation or deployment is complete.
```

## 11. Final submission checklist

- [ ] All **seven original course** idea-validation steps completed
- [ ] User/problem/market evidence and differentiated angle documented
- [ ] One-page PRD present
- [ ] Architecture notes and `spec.md` present
- [ ] `agents.md` or `CLAUDE.md` present
- [ ] `.cursorrules` present
- [ ] Reviewed/revised technical spec
- [ ] Working usable AI-powered UI
- [ ] Public GitHub repository
- [ ] Five or more meaningful commits
- [ ] Three or more passing unit tests
- [ ] Secrets check and input validation
- [ ] Working GitHub Actions CI workflow
- [ ] Live application URL and configured environment variables
- [ ] Tested in incognito
- [ ] Basic usage/error monitoring or analytics
- [ ] Complete README
- [ ] Accessible 2-minute demo link
- [ ] One-page reflection
- [ ] One GitHub issue describing a v2 improvement

---

**Handoff status:** Planning material consolidated into one Markdown file for Codex. None of the implementation, validation, test, deployment or portfolio metrics are represented here as completed.
