# Synthetic model evaluation

Run from the repository root with the locally configured backend key:

```sh
backend/.venv/bin/python evals/run_evals.py --live --output evals/results/new-run.json
```

This explicitly opts into real OpenAI calls: up to 20 cases x three stages, plus
bounded schema/transport retries. Ordinary CI never calls the provider. The
production app does not import this evaluator. Cases contain only synthetic data.

## Recorded runs, 23 November 2026

| Run | Validated stages | Annotated extraction | Design family | Risk keyword proxy |
|---|---:|---:|---:|---:|
| Initial wording/labels, extract_v1 | 60/60 | 78.81% | 90% | 100% |
| Revised wording/labels, extract_v1 | 60/60 | 77.12% | 100% | 100% |
| Same revised cases, extract_v2 | 60/60 | 100% | 100% | 100% |

Latest run: 20/20 completed cases, median 14.31 seconds per three-stage case,
p95 17.79 seconds, 69,084 known input tokens, 19,098 known output tokens.
Estimated USD cost is null because operator-maintained prices were not configured.
These are actual provider runs, not fixture measurements. The model recorded in
stage metadata is `gpt-4.1-mini-2025-04-14`.

The initial dataset confused a number proposed for assignment with a clearly
stated eligible pool. Revised objectives explicitly state the eligible pool.
Two gold design labels were corrected to unsupported: deliberately nonrandom
selection and choosing a significant outcome from 20 candidates. The two missing
baseline cases were made distinct. Initial results are preserved in
`results/baseline-v1.json`; the repeated initial file `results/live.json` is the
original command's output. `results/revised-v2.json` used revised cases with the
old prompt. `results/extract-v2.json` used those same revised cases with the new
prompt. The new prompt explicitly preserves stated eligible pools and extracts
facts independently of whether the requested design is supported.

## What the metrics mean

- **Validated stage rate:** expected stages successfully parsed after bounded
  repair. This is not first-attempt schema validity or availability under load.
- **Annotated extraction accuracy:** exact/near-numeric agreement on annotated
  fields, including expected nulls. It excludes unannotated metric wording and
  does not evaluate all semantic claims or evidence quality.
- **Design family accuracy:** agreement with the curated expected family. This
  does not prove every proposed design field is correct.
- **Risk keyword recall proxy:** at least one listed term for each expected risk
  appears in the critique. It can pass on a poor explanation and must not be
  presented as human-validated high-priority risk recall.
- **Latency:** full sequential three-stage case wall time, including calculations,
  with nearest-rank p95. Not production request latency or concurrent-load testing.

Twenty development cases are too small for broad quality claims. There is no
held-out benchmark, independent human adjudication, user study, or measured
market demand. Unsupported designs are deliberately sent to the critic as offline
quality probes; the application correctly gates them before calculation/review.
The evaluator never promotes an extracted value into calculator inputs.

Keep all failures and prior runs. Do not re-label cases simply to improve scores;
record the reason for any annotation correction. The next benchmark work is
specified in `docs/v2-issue.md`.
