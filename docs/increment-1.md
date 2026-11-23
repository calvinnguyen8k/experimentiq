# Increment 1: specifications and extraction vertical slice

Date: 2026-11-23. Outcome: implemented and locally verified with a mocked provider.
**A successful real OpenAI extraction is not verified: no API key was configured.**

## Scope and files

- `docs/prd.md`, `docs/architecture.md`, `spec.md`, `agents.md`, `.cursorrules`:
  product boundary, executable/current versus future API contracts, provenance,
  statistical planning boundaries, acceptance criteria, decisions, and review notes.
- `backend/app/`: strict input/output models, async official SDK adapter, versioned
  extraction prompt, evidence validation, input merging, deterministic questions,
  FastAPI endpoints, bounded work, CORS, safe errors, and metadata-only logging.
- `frontend/app/` and `frontend/lib/`: responsive form, optional confirmed inputs,
  loading/error/results states, evidence/provenance/conflicts, runtime JSON contract
  checking, stale-result clearing, and accessible labels.
- `backend/tests/`, `frontend/tests/`, `frontend/playwright.config.ts`: deterministic
  unit, API, SDK adapter, request-limit, scanner, and browser integration coverage.
- `.env.example`, `frontend/.env.example`, `.gitignore`, dependency locks:
  repeatable setup and server-only credential handling.
- `scripts/check_secrets.py`, `.github/workflows/ci.yml`, `README.md`: local secret
  pattern check, hosted CI definition, operating instructions, and assignment gaps.

## Why these decisions

1. Keep the two services in the handoff: Python remains the domain implementation
   language, and the frontend is a small typed client. No framework substitution.
2. Implement extraction before proposal/statistics to expose missing input honestly
   and establish a testable transport/validation boundary without fabricated output.
3. Exact quotes are checked, but they do not prove correct interpretation. Extracted
   values remain unconfirmed. Explicit form inputs are authoritative; contradictions
   get a warning, not silent resolution.
4. Generate missing questions in Python so the provider cannot skip required fields,
   invent a baseline, mark a review complete, or report a numerical calculation.
5. Use the official SDK's strict structured parsing and independently validate data
   and evidence. One repair attempt handles malformed output; no fallback guesses.
6. Use process-local limits for local development, plus an overall timeout and
   payload cap. Document stronger shared/edge limits as a public-deployment gate.
7. Log only bounded metadata and optional estimated cost. Never include objective,
   raw provider responses, validation payloads, or exception messages.
8. Test the full browser/API/SDK chain with HTTP mocked at the provider. This proves
   integration and guardrails but cannot measure model quality or live availability.
9. Use Webpack after an observed Turbopack port-binding failure. Keep dependency
   versions locked and run `next typegen` for clean-checkout type checking.

Additional details and limitations are in `docs/architecture.md` and `spec.md`.

## Commands actually run and results

| Check | Result |
|---|---|
| `uv pip compile backend/requirements.in -o backend/requirements.txt`; `uv pip sync` | Resolved and installed locked backend dependencies |
| `npm install` in frontend | Installed and locked dependencies; npm reported 0 vulnerabilities at install time |
| `.venv/bin/ruff check .` in backend | Passed |
| `.venv/bin/ruff format --check .` in backend | Passed, 24 Python files |
| `.venv/bin/python -m pytest -q` in backend | **57 passed** |
| `npm run lint` | Passed |
| `npm run typecheck` (`next typegen && tsc --noEmit`) | Passed |
| `NEXT_TELEMETRY_DISABLED=1 npm run build` | Passed with Webpack; static root page produced |
| `PLAYWRIGHT_BROWSERS_PATH=/private/tmp/experimentiq-browsers npm test` | **5 passed**, Chromium, 1 worker |
| `python3 scripts/check_secrets.py` | Passed; scans tracked/nonignored repository files |
| Local production frontend HTTP request | 200 |
| Live local backend `/health` | 200, service `experimentiq`, version `0.1.0` |
| Production UI → actual backend without credentials | Correct `llm_not_configured` message displayed; no success fabricated |

Local runtime: Python 3.13.1, Node 22.19.0. CI targets Python 3.11/Node 22; a hosted
run has not occurred. One upstream Starlette warning recommends migrating its
TestClient from httpx to httpx2; the locked version passed all tests. The OpenAI SDK
still uses httpx. No application warning or test failure remains unresolved.

The initial browser run found selector ambiguity, not missing data: fact text and
provenance shared an element, and Next.js adds its own unnamed alert. Result markup
and the app alert's accessible name were clarified; all browser scenarios then
passed. A secret-scanner newline false positive was fixed with a regression test.

## Visual checks

Desktop (1280 px) and mobile (390 px) screenshots were inspected. The form, result
values, evidence, and questions render without horizontal overflow. **These images
use synthetic fixtures and mocked OpenAI HTTP; they are not live-model evidence.**

- [Desktop browser test](screenshots/desktop-extraction-mocked.png)
- [Mobile browser test](screenshots/mobile-extraction-mocked.png)

## Local milestones

Five meaningful local commits separate specification, backend, frontend, tests,
and CI/documentation. No remote repository was created and nothing was pushed or
deployed. The original handoff is preserved unchanged. Temporary preview/test
servers were stopped after verification; use README commands to run the app.

## Remaining work and next step

Configure an OpenAI key privately in `backend/.env`, run the README scenario, and
record actual model behavior. Then add design generation with suggestion provenance
and confirmed-input interaction. After that implement the independently tested
statistical engine, critique, consistency checks, Markdown export, and evaluation
suite. Future sample-size reference values in the spec remain to be independently
verified with that increment.

The original seven course steps, market/user evidence, public repository, hosted
CI, deployment/production protections/incognito test, demo, reflection, and v2
issue remain open. No statistical accuracy or model-quality target is claimed.
