# Free deployment runbook

Hosting: two projects on the existing Vercel **Hobby** account, plus account-owned
free Upstash Redis. Render Free creation returned HTTP 402 requiring payment
information; no card, trial or paid plan was added. `render.yaml` is retained as an
optional alternative, not an active deployment.

## Resources

- Public source: https://github.com/calvinnguyen8k/experimentiq
- Frontend: https://experimentiq-omega.vercel.app (`frontend`, Node 22, Next.js).
- API: https://experimentiq-api.vercel.app (`backend`, Python 3.13, FastAPI).
- Quotas: persistent account-owned Upstash; never a temporary 72-hour database.
- Hosting tiers are free; calls using the existing OpenAI API key remain billable.

[Vercel Hobby](https://vercel.com/docs/plans/hobby),
[FastAPI support](https://vercel.com/docs/frameworks/backend/fastapi),
[Python runtime](https://vercel.com/docs/functions/runtimes/python),
[Upstash Free](https://upstash.com/pricing/redis).

## Configuration and deployment

1. Link each directory to its own Vercel project. Use `frontend/vercel.json` and
   `backend/vercel.json`; deploy from the corresponding directory.
2. Set backend production variables: `PRODUCTION_MODE=true`, `OPENAI_MODEL=gpt-4.1-mini`,
   `DAILY_REQUEST_LIMIT=120`, and
   `ALLOWED_ORIGINS=["https://experimentiq-omega.vercel.app"]`.
3. Transfer `OPENAI_API_KEY`, `REDIS_REST_URL`, and `REDIS_REST_TOKEN` through CLI
   stdin to backend-only Secret environment variables. Never put values in command
   arguments, browser code, Git, logs or chat. The local `.env` is ignored.
4. Set frontend production `NEXT_PUBLIC_API_URL=https://experimentiq-api.vercel.app`.
   This URL is public configuration; no backend credential belongs in this project.
5. Deploy with `vercel deploy --prod` in each linked directory, then verify the
   public production domains without an authentication bypass or saved cookies.
   Current deployment is CLI-based; do not assume Git pushes deploy either project.

Runtime dependencies are locked in `backend/requirements.txt`. Local/CI tests
install `backend/requirements-dev.txt`, preserving the verified versions. The
backend `.vercelignore` excludes test-only `pyproject.toml`: Vercel otherwise prefers
that file over `requirements.txt` and installs no application dependencies. Keep
local `.venv` out of uploads, but do not exclude Vercel's generated runtime virtual
environment from the function bundle. Both upload manifests exclude `.env*`.
The host function limit is 60 seconds; the application AI deadline is 45 seconds.

## Required release evidence

- Hosted GitHub Actions passes; record its URL and SHA.
- Unauthenticated HTTPS API `/health` and frontend both return 200.
- A fresh browser context completes the full synthetic example through confirmed
  design, confirmed numerical inputs, Python calculation, real AI critique and
  Markdown download. No provider interception in this smoke test.
- Demo count: mean 200, SD 100, relative MDE .05, alpha .05, power .8, ratio 1:
  control 1,570, treatment 1,570, total 3,140; pool 100,000 is feasible.
- Missing SD blocks calculation; edits invalidate later stages; unsupported designs
  cannot proceed. Unit/browser regression tests cover unsupported designs.
- Check actual shared quota behavior, fail-closed errors in a controlled test,
  CORS, metadata-only runtime logs, and no credentials in uploaded source/bundle.
- Retain public app, API, CI, demo and v2 issue links in README.

## Monitoring and rollback

Use Vercel runtime logs for request IDs, stage latency, status, error category and
available model usage. `/health` is process liveness, not a provider/Redis check.
Do not expose raw operator logs publicly. Redis stores quota counters, hashed peers,
and expiring leases. A quota outage rejects requests rather than falling back to
unbounded AI calls. Cold starts and free-tier usage limits can affect availability.

Roll back to the last verified deployment in each Vercel project and record the
source SHA. Never disable production quotas to get around a deployment failure.
