# ExperimentIQ

AI-assisted experiment intake for Product Managers and Growth Analysts. Describe a
synthetic A/B test and inspect extracted values, supporting quotes, conflicts, and
missing-information questions before making design or sample-size decisions.

**Current scope: the first extraction vertical slice.** Next.js form → FastAPI →
OpenAI structured output → Pydantic/evidence checks → rendered facts and questions.
Design generation, numerical statistics, critique, export, real-model evaluations,
and public deployment are later increments. This is not the completed assignment.

## Local setup

Prerequisites: Python 3.11+ (tested locally with 3.13), Node 22, npm, and Git on
macOS/Linux. An OpenAI API account/key with model access is required for **real**
extraction; a ChatGPT subscription is not an API credential. Tests need no key.

From the repository root:

```sh
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
test -f backend/.env || cp .env.example backend/.env
cd frontend
npm ci
test -f .env.local || cp .env.example .env.local
```

Edit `backend/.env` locally and set `OPENAI_API_KEY`. Never paste a key into the
browser, source code, a commit, or chat. The backend reads `.env` relative to its
working directory, so use the commands below. `OPENAI_MODEL` defaults to
`gpt-4.1-mini` and is configurable. A live synthetic extraction was verified on
2026-11-23; broader model quality remains unevaluated. Optional token prices enable approximate cost reporting;
otherwise cost is null. Recheck prices when changing model/provider settings.

Terminal 1, from repository root:

```sh
cd backend
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --no-access-log
```

Terminal 2, from repository root:

```sh
cd frontend
npm run dev
```

Open [the local UI](http://127.0.0.1:3000),
[API health](http://127.0.0.1:8000/health), or
[interactive API schema](http://127.0.0.1:8000/docs).
Health verifies process liveness only; absent credentials cause an explicit 503 on
extraction. There is no simulated-success switch in the production application.

## Try the synthetic scenario

Click **Load synthetic example**, then **Extract experiment facts**. Expected behavior:

- Population 100,000, continuous average card spending, relative increase 0.05.
- Evidence quotes and a confirmation requirement for every prose-extracted value.
- Questions for baseline mean and standard deviation, with both values null.
- No fabricated numeric result or claim that an experiment is valid.

Open **Optional confirmed inputs** to confirm or correct known values and rerun.
Use decimals: `0.05` means 5%, `0.10` means 10%. Leave unknown fields blank. A
conflicting form value wins, but a conflict warning asks you to reconcile the prose.
Editing clears stale results. Continuous mean/SD and binary conversion inputs
cannot be combined under a selected outcome type.
The form shows only the relevant baseline fields and clears incompatible baseline
inputs when you change outcome type. Different primary-metric wording is shown as
an informational note; numeric/outcome-type conflicts still need resolution.

## Architecture and decisions

```text
Next.js UI → FastAPI validation / request limits
           → OpenAI Responses API + strict Pydantic extraction
           → evidence checks / explicit-input merge / deterministic questions
           → UI facts, conflicts, unknowns, and confirmation prompts
```

Python owns domain logic; TypeScript owns display and a runtime-validated API
client. Exact supporting quotes reduce unsupported extraction but cannot prove
semantic correctness: **all prose extraction remains unconfirmed**. Explicit form
values are user-provided. No extracted number can silently feed future statistics.
There is no database, history, auth, or persistent storage.

The [technical spec](spec.md), [architecture decisions](docs/architecture.md), and
[one-page PRD](docs/prd.md) explain contracts, scope, tradeoffs, and future work.
[agents.md](agents.md) and [.cursorrules](.cursorrules) preserve these boundaries.
The original [handoff](ExperimentIQ_Codex_Handoff.md) is unchanged.

See the [desktop](docs/screenshots/desktop-extraction-mocked.png) and
[mobile](docs/screenshots/mobile-extraction-mocked.png) browser-test screenshots.
Both use a mocked OpenAI response and synthetic data, not a live model run.

## Verification

Backend, from repository root:

```sh
cd backend
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python -m pytest -q
```

Frontend, from repository root:

```sh
cd frontend
npm run lint
npm run typecheck
npm run build
npx playwright install chromium
npm test
```

Browser tests use an isolated `.next-e2e` build directory, start their own servers
on 3100/8100, and invoke the actual frontend,
FastAPI application, official OpenAI SDK, and validators. Only OpenAI HTTP is
mocked for success scenarios. Additional UI error scenarios intercept the API.
The fixture service lives exclusively in `backend/tests/e2e_api.py`; it is never
selected by the production entry point. Ensure ports 3100/8100 are free.

Secret pattern check, from repository root:

```sh
python3 scripts/check_secrets.py
```

This lightweight scanner checks tracked and nonignored working files and refuses
tracked environment files. It reports locations, not matched secret text. It is
not an exhaustive secret-detection product. Environment files and dependency/build
directories are ignored. Dependency resolutions are checked in for repeatability.

The [GitHub Actions workflow](.github/workflows/ci.yml) runs these checks on pushes
and pull requests without an OpenAI key. A checked-in workflow is not evidence of
a successful hosted CI run. Actual local results are recorded in
[the increment log](docs/increment-1.md).

## Operational limits

- Input: 20–4,000 characters; body ≤24 KiB; strict finite numeric ranges.
- Default limits: 5 requests/client/minute, 30 total/minute, 3 concurrent provider
  operations per process; use one worker for local verification.
- SDK timeout 15 seconds and one transport retry; one schema/evidence repair;
  overall 45-second extraction deadline, 50-second browser deadline.
- CORS permits only configured origins; socket peer identity ignores untrusted
  forwarded headers. Behind a proxy, clients may share the same rate budget.
- Metadata logs contain request IDs, model/usage where available, latency, statuses,
  and validation/error categories. They exclude raw objectives and provider text.
  Failed/invalid responses may have unknown usage/cost; configured cost is an
  estimate without cache discounts, not a billing reconciliation.
- Requests use OpenAI `store=False`. This does not establish zero provider retention;
  synthetic/public toy examples only. No confidential/customer data.

Before public deployment: select a Python host, add shared/edge throttling and
trusted proxy configuration, verify host budgets, configure HTTPS/origin allowlist,
set the frontend API URL at build time, and run a live incognito smoke test.
Vercel remains the intended frontend host. Nothing has been published.

## Assignment and next increments

- [x] PRD with explicit unvalidated hypotheses
- [x] Technical specification, architecture notes, agent instructions, cursor rules
- [x] Extraction implementation with input validation, missing questions, provenance
- [x] 64 backend tests, 7 browser tests, lint/typecheck, and production build pass locally
- [x] Local secret pattern check and metadata-only request logging
- [x] Five meaningful local commits (public repository still pending)
- [x] Successful live OpenAI extraction of the synthetic scenario in the UI
- [ ] AI design generation and explicit confirmation flow
- [ ] Independently tested binary/continuous sample-size engine
- [ ] Critique, consistency checks, Markdown report/export
- [ ] ~20 synthetic model evaluation cases and measured quality metrics
- [ ] Original seven course validation steps; user/market/competitor evidence
- [ ] Public GitHub repository and successful hosted CI run
- [ ] Production abuse protection, monitoring, live deployment/incognito verification
- [ ] Finished README/screenshots, 2-minute demo, 1-page reflection, v2 issue

Local test results and commit history are recorded separately; no assignment or
portfolio quality target is marked achieved without evidence. Next implementation
increment: generate a proposed design from normalized facts, preserve suggestion
provenance, and obtain confirmed statistical inputs before implementing the engine.
