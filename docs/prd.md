# ExperimentIQ product requirements

Status: implementation increment 2; validation hypotheses are unverified.

**User and problem.** Product Managers and Growth Analysts need to turn vague A/B
test ideas into reviewable designs. Analytics Leads need to see missing assumptions
before approving an experiment. We hypothesize that ambiguous metrics, assignment,
and sample-size assumptions create avoidable review work; interviews and market
evidence have not yet established this.

**Value.** A structured design review with attributable facts, explicit questions,
deterministic statistical checks, and actionable methodological concerns.

**Journey.** Describe a synthetic experiment → inspect extracted facts and their
evidence → supply missing inputs → review a proposed design → examine deterministic
sample-size feasibility → review risks → export Markdown.

**Implemented scope.** A usable intake form, complete/incomplete synthetic presets,
OpenAI structured extraction, server validation, provenance, missing questions,
recoverable errors, and a separate generated design proposal with back/edit flow.
No numerical calculations or independent risk review yet.

**MVP next.** Independent two-arm binary/continuous sample sizes, critique,
consistency checks, Markdown export, synthetic evaluations, monitoring, deployment.
No accounts, history, uploads, real customer data, RAG, or experiment execution.

**Acceptance for increment 1.** The synthetic credit-card example retains population
100,000 and relative effect 0.05 as unconfirmed extracted candidates, asks for mean
and standard deviation, and never supplies a sample-size result. A structured input
is authoritative, but contradictions remain visible. Editing and resubmitting cannot
show an old result as current. Missing credentials produce an honest setup error.

**Targets, not results.** Eventual ≥95% schema validity and ≥90% high-priority risk
recall on a curated suite; zero unconfirmed numeric values passed to statistics.

**Validation gaps.** Obtain the original seven course validation steps; research at
least three competitors; collect direct user evidence; validate differentiation.
These tasks are not replaced by implementation or an invented checklist.

**Submission gaps.** Public repository, five meaningful commits, verified CI, public
deployment/incognito check, demo, reflection, and v2 issue remain to be completed.
