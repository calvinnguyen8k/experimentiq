# ExperimentIQ Idea Validation Report

23 November 2026 | Evidence-based assessment of a deployed planning MVP

## Conclusion and framework status

ExperimentIQ is technically feasible as a constrained experiment-planning workbench. Its public workflow and numerical implementation have been tested. Product demand, comparative advantage and willingness to adopt remain unverified. The appropriate decision is to continue with a small user-validation study before expanding the product.

The assignment requires all seven steps of its Idea Validation Framework. The supplied assignment lists that requirement but does not enumerate the steps. The available Week 4 Self-Learning Handbook, Chapter 3, pages 10-12, instead presents problem evidence, user profile, current alternative, advantage, cheap test and decision rule. This report organizes available evidence into seven provisional areas, adding the requested “why now” analysis. These headings are not claimed to be the official seven-step framework. Exact course mapping and independent user evidence remain outstanding.

## Evidence area 1 Problem and impact

Working problem statement: a Product Manager or Growth Analyst preparing an A/B test may struggle to turn an objective into a reviewable plan with a clear outcome, assignment rule and defensible numerical assumptions. Missing variance, ambiguous success metrics or inappropriate randomization can prevent useful sample-size planning. The frequency and business cost of these problems have not been measured for the intended users.

Observed project evidence: the project owner reported being unable to continue after extraction and design, requested a full synthetic example and asked for a Next button at every ready stage. These observations support a usability problem in the initial implementation. They do not independently validate the broader market problem.

## Evidence area 2 Users and context

The primary persona is a PM or Growth Analyst preparing a two-arm test for review by an analytics colleague. This is a proposed persona, not an interviewed participant. The desired job is to produce an auditable draft before configuring an experimentation platform. A Data Scientist is a secondary reviewer rather than an autonomous decision delegate.

Important edge cases are a novice with no baseline standard deviation, a team proposing household-level or sequential assignment, and a mobile user reviewing a plan. Missing information and unsupported designs are handled explicitly. Likely adoption barriers include trust in AI-generated advice, organizational privacy policies and preference for existing tools. These barriers need interviews or observation to confirm.

## Evidence area 3 Current alternatives and market evidence

Three primary-source competitors were reviewed on 23 November 2026. Statsig documents a power-analysis workflow using historical metric and population information, with sizing reports attached to experiments [1]. GrowthBook's version 4.0 announcement documents decision criteria, experiment insights/timelines and an MCP integration [2]. Optimizely offers a conversion-based sizing calculator using its sequential Stats Engine [3]. This is evidence of existing adjacent capabilities, not market sizing or proof of unmet demand.

A spreadsheet or statistical notebook with a specialist review is another plausible alternative, but its use by this target group has not been observed in this project. Existing tools show that sample-size calculation alone is not a novel differentiator. Counts from different statistical methods should not be presented as interchangeable.

## Evidence area 4 Why now and proposed advantage

The technical opportunity is to combine structured language interpretation with deterministic statistical tools. In this project, real OpenAI calls generated typed extractions, proposals and critiques, while SciPy performed the calculation. The hosted workflow demonstrates that this combination can operate today; it does not establish a market-growth trend.

The proposed advantage is a small pre-launch review experience: source-labelled facts, explicit unknowns, confirmed numerical assumptions, a constrained calculation and an exportable critique in one flow. Competitors already offer planning and AI-related capabilities, so uniqueness and superior usefulness remain hypotheses. A comparison task is needed to test whether the workflow reduces planning effort or improves understanding.

## Evidence area 5 Feasibility and risks

Technical evidence includes 123 backend tests, 14 browser tests, independent Statsmodels comparisons, green hosted CI and a fresh public browser workflow with real OpenAI calls. The continuous demo used mean 200, SD 100, 5% relative effect, alpha .05, power .8 and equal allocation; the result was 1,570 per arm, 3,140 total. The 20-case development evaluation completed 60 schema-validated stages after bounded repair. Keyword-based risk checks are not human-adjudicated quality scores.

Controls include strict input validation, explicit confirmation, server-only credentials, daily/shared Redis quotas, request limits and safe errors. Remaining risks include misleading AI advice, overconfidence in approximate calculations, free-host availability and billable provider usage. The app uses synthetic examples only; it does not execute experiments or authorize launch.

## Evidence area 6 Cheap validation test and evidence to collect

Proposed study, not conducted: recruit five intended users by role, with voluntary consent, using fictional scenarios only. Ask each to prepare plans using both their usual approach and ExperimentIQ, counterbalancing task order. Record completion time, assistance needed, missing assumptions identified and whether they can explain which statements are facts, proposals or calculated results. Do not request confidential work data.

Before running the study, set these learning criteria: at least four of five complete the app task without facilitator intervention and correctly distinguish the three information types; no participant treats a generated assumption as confirmed data. Compare task times and review quality descriptively. Five participants can inform usability changes, not establish market demand or statistically reliable superiority. Record actual feedback and retain negative findings.

## Evidence area 7 Decision and next evidence

Current decision: continue with bounded validation of the deployed MVP; do not claim product-market fit or broaden statistical scope. The user-value assumption is the most important unresolved risk. A positive engineering evaluation is insufficient to answer it.

Continue to a larger pilot if the proposed usability criteria are met and users demonstrate a concrete use for the report. Change the interaction if users need help progressing or cannot distinguish sources. Pause broader rollout if participants repeatedly misinterpret AI advice as verified statistical approval or report no relevant planning need. These thresholds are prospective, not retrospective claims of success.

## Sources and evidence register

[1] Statsig, Power Analysis. https://docs.statsig.com/experiments/power-analysis

[2] GrowthBook, Version 4.0, 9 July 2025. https://www.growthbook.io/blog/growthbook-version-4-0

[3] Optimizely, Sample size calculator. https://www.optimizely.com/tools/sample-size-calculator

[4] Week 4 Self-Learning Handbook, Chapter 3, pages 10-12; Chapter 6, pages 20-22. Local course material; not republished in this repository.

[5] Project-owner feedback in the development conversation: unclear progression, requests for a complete synthetic example and explicit Next buttons. One owner; no independent interview sample.

[6] Technical evidence: README; output/deployment/public-smoke.json; output/deployment/quota-cors.json; evals/results/extract-v2.json; GitHub Actions run 45187570149. These establish implementation observations, not user demand.
