# Free deployment runbook

Status: source/configuration prepared; account connections, secrets, deployment
and public smoke tests must be observed before marking deployment complete.

## Resources and account boundaries

- Public source: https://github.com/calvinnguyen8k/experimentiq
- Frontend: Vercel **Hobby**, root directory `frontend`, Next.js, Node 22,
  `npm ci`, `npm run build`, default `.next` output.
- API: Render **Free** web service using root `render.yaml`, root directory
  `backend`, Python selected by `.python-version`, one Uvicorn worker.
- Quotas: an account-owned **free** Upstash Redis database. Do not use a temporary
  72-hour database for a submitted deployment; it would silently expire.
- Do not select Pro trials, paid plans, automatic upgrades, or add a payment card.
  Existing OpenAI API usage remains billable; free hosting does not make AI free.

Current provider terms: [Vercel Hobby](https://vercel.com/docs/plans/hobby),
[Render Free](https://render.com/docs/free), [Upstash Free](https://upstash.com/pricing/redis).
Render Free sleeps after 15 minutes without incoming traffic; the first request
can take longer than the application's timeout. Open API health first, wait for
it to respond, then retry the stage. Do not add artificial keepalive traffic.

## Configure without disclosing secrets

1. Import the public repository into Vercel, selecting `frontend` as root. Set
   `NEXT_PUBLIC_API_URL` to the final HTTPS Render service URL and deploy/redeploy.
2. Create a free Render Blueprint from `render.yaml`. Set backend-only
   `OPENAI_API_KEY`, `REDIS_REST_URL`, and `REDIS_REST_TOKEN` in the host's secret
   environment settings. Never put them in Git, the frontend, a URL or chat.
3. Set `ALLOWED_ORIGINS` to a JSON array containing the exact HTTPS frontend URL.
   Keep `PRODUCTION_MODE=true` and `DAILY_REQUEST_LIMIT=120` (or a lower intentional
   cap). No wildcard CORS; local development uses `PRODUCTION_MODE=false`.
4. Use the existing GitHub account and restrict hosting integration access to this
   repository when supported. New app permissions, account terms, and secret
   transfers need the user's involvement/approval at their actual setup step.

## Verification required before a checked box

- GitHub Actions is green for the pushed commit; retain its run URL and SHA.
- HTTPS API `/health` returns 200; frontend loads without authentication.
- Fresh/incognito browser: complete preset → extraction → design confirmation →
  numerical confirmation → calculation → review → acknowledged Markdown download.
- Demo count: mean=200, SD=100, relative MDE=.05, alpha=.05, power=.8, ratio=1:
  control=1,570, treatment=1,570, total=3,140; pool=100,000 is feasible.
- Missing SD cannot calculate; unsupported design cannot advance; editing inputs
  invalidates later results. Errors expose request IDs, not raw provider messages.
- Observe a rejected quota request and a quota-service outage in a controlled
  test environment. Keep production quotas enabled throughout the public smoke test.
- Inspect host logs for metadata-only requests. Verify no keys in source/bundle.
- Retain public app, API, CI, demo and v2 issue links in README.

## Monitoring and rollback

Render request logs supply stage latency, response/error categories and available
model usage. `/health` is process liveness, not a provider/Redis credential check.
Use the host dashboard to inspect failures; do not expose raw logs publicly.
Redis provides the durable daily request counter and expiring leases. If quota
storage fails, requests stop instead of falling back to unbounded provider calls.
If a release fails, roll back to the last verified commit on both hosts and record
that SHA. Do not disable `PRODUCTION_MODE` to get around a deployment failure.
