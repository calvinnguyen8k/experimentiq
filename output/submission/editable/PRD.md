# ExperimentIQ Product Requirements

Revision 4 | 23 November 2026 | Deployed MVP

## 1 Problem statement

Product Managers and Growth Analysts preparing A/B tests may reach review with unclear metrics, missing baselines or unsupported sample-size assumptions. ExperimentIQ helps turn an initial idea into a traceable draft before launch. Frequency, time lost and willingness to adopt remain hypotheses; project-owner feedback established navigation problems, not market demand. Structured AI output and a tested Python calculator make this workflow technically feasible now.

## 2 Target users

Primary: Product Managers and Growth Analysts planning independent two-arm experiments. Secondary: Data Scientists reviewing assumptions. Edge cases: a novice without baseline variance, a reviewer facing an unsupported clustered design, and a mobile user. The application currently accepts synthetic examples only and requires human methodological judgment.

## 3 MVP features

- Extract facts with provenance. Acceptance: unknowns stay null; extracted values require confirmation.
- Propose an experimental design. Acceptance: hypothesis, arms, assignment unit, metric and window are visible; supported designs need acknowledgement before progression.
- Calculate sample size in Python. Acceptance: confirmed continuous/binary inputs produce independently tested counts; missing or unsupported inputs produce no guessed result.
- Critique and export a draft. Acceptance: ranked risks, open assumptions and unchanged Python results appear in the downloadable Markdown report.
- Support iteration. Acceptance: destination-labelled Next buttons explain readiness; changing earlier inputs invalidates later results.

## 4 Out of scope

Experiment execution, real customer data, accounts/history, payments, uploads, RAG and outcome analysis. Statistical support excludes clustered, paired, sequential and multi-arm designs. Exporting a report does not approve an experiment or establish observed uplift.

## 5 Success metrics

Observed: 123 backend tests and 14 browser tests passed; hosted CI passed; a fresh unauthenticated public workflow completed with real OpenAI calls. The synthetic continuous example returned 1,570 units per arm. The 20-case development evaluation produced 60/60 schema-validated stages after bounded repair. The target of at least 90% meaningful high-priority risk recall is unverified: keyword matching is only a proxy. Proposed user test: at least 4 of 5 intended users complete and explain a plan without facilitator intervention; no results collected yet.

## 6 Open questions

Will intended users prefer this to their current planning process? Can they distinguish facts, proposals and assumptions? Does human-reviewed risk detection meet the quality target? What changes are needed for organizational privacy and adoption? The exact seven-step course validation framework still needs confirmation; current evidence does not establish market fit.

Framework: Week 4 Self-Learning Handbook, Chapter 6, pages 20-22. These are its six named PRD components. Evidence: README, evals/results/extract-v2.json, output/deployment/public-smoke.json and GitHub Actions run 45187570149.
