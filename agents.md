# Project guidance

Read `spec.md` and `docs/architecture.md` before changing contracts. Preserve the
handoff as the planning baseline. Work one tested increment at a time.

- Python owns validation, orchestration, and statistics; TypeScript owns UI.
- Use synthetic examples only. No keys in code, browser, logs, fixtures, or Git.
- Unknown is null. Extracted prose is unconfirmed, even when a quote matches.
- Keep user facts, LLM interpretations/proposals, and deterministic results distinct.
- Never silently promote model-provided numbers to calculator inputs.
- Mock the external provider in tests, never in production success paths.
- Run backend lint/tests, frontend lint/typecheck/tests/build and secrets scan.
- Explain decisions in architecture notes; record actual validation in README.
- Do not claim market validation, model quality, deployment, or CI execution without evidence.
- Do not add P2 scope before finishing and deploying P0.
