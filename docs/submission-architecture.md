# ExperimentIQ System Architecture

23 November 2026 | Deployed MVP | Technical summary for submission

## Responsibility and data flow

The browser runs a Next.js and TypeScript workbench. A separate FastAPI service validates requests, enforces usage limits, orchestrates the AI stages and calculates statistics. Both services run on Vercel Hobby. Upstash Redis holds short-lived quota state, not experiment history. The OpenAI API is called only from Python with server-side credentials.

The user journey is intake, design proposal, statistical validation, then review and export. The browser sends typed JSON over HTTPS. Each stage has a visible readiness gate. Going back preserves unchanged work; editing earlier inputs invalidates dependent results.

## AI module design

Extraction uses the versioned extract_v2 prompt and a strict Pydantic schema. Exact source quotes support extracted fields, but those fields remain unconfirmed. Unknown values stay null. Explicit user form values take precedence, with genuine conflicts surfaced for review.

Design generation uses design_v1 in a separate call. It proposes the hypothesis, arms, assignment unit, primary metric and observation period. Suggested assumptions and open questions stay visible. Generated numbers do not become calculator inputs.

The deterministic statistics module supports independent, two-arm, fixed-horizon, two-sided continuous and binary planning approximations. It accepts confirmed inputs, rounds up sample counts, checks achieved approximate power and compares the total with the eligible pool. Missing or unsupported inputs return no guessed sample size.

The critic_v1 call receives the draft design and server-recomputed statistics. It returns ranked risks, reasons, mitigations and unresolved assumptions. The server retains the Python result. The browser creates an escaped Markdown report after the user acknowledges the review.

## Interfaces and acceptance criteria

GET /health reports process liveness. POST /api/v1/experiments/extract and /design accept validated experiment inputs. POST /api/v1/statistics/sample-size accepts explicit statistical assumptions. POST /api/v1/experiments/review accepts the draft design and inputs, not client-provided statistical results. Full schemas and field bounds are in spec.md and the public /docs endpoint.

The complete synthetic example must yield 1,570 control and 1,570 treatment units. Missing SD must block continuous calculation; unsupported designs must not advance. Changing inputs must clear dependent results. A real-provider public workflow has completed all stages and downloaded a report in a fresh browser context.

## Reliability and operations

Controls include a 24 KiB body limit, strict ranges, explicit HTTPS CORS origins, bounded model output, one SDK transport retry and one schema-repair attempt. AI stages have a 45-second deadline inside a 60-second hosting limit. Errors expose safe messages and request IDs. Shared Redis quotas bound minute, concurrency and daily usage; quota outages fail closed. Logs contain request metadata and available token counts. Monetary estimates remain null until pricing is configured.

GitHub Actions runs secret-pattern checks, backend lint/tests, frontend lint/typecheck/build and browser integration tests with mocked provider responses. Deployment is performed separately through the authenticated Vercel CLI; this is automated CI with manual deployment, not an automatic deployment-on-push pipeline. Runtime and test dependencies are locked separately. Local credentials are excluded from uploads and source control.

## Decisions and limitations

Python owns domain logic and statistics so results can be tested independently of model prose. The stateless MVP avoids accounts and history because they are not needed to demonstrate planning value. Render Free creation required payment information, so the free-hosting constraint led to two Vercel projects instead. Function cold starts and provider availability can affect latency. Free hosting does not make OpenAI calls free.

The tool is planning assistance for synthetic scenarios. It does not execute experiments, demonstrate causal uplift, replace specialist review or establish market demand. Human-reviewed risk evaluation and observation of intended users are the next improvements.

References: spec.md; docs/architecture.md; docs/deployment.md; backend/app/; frontend/; output/deployment/public-smoke.json; GitHub Actions run 45187570149.
