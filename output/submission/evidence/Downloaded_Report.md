# ExperimentIQ — Draft experiment plan

Synthetic/public toy planning data only. No experiment has been run.

Status: review\_needs\_attention. Export records the plan and risks; it is not approval to launch.

## Objective

We want to test personalized credit-card promotions versus generic promotions for 100,000 eligible customers. Our goal is to increase average card spending by 5%.

This is a fully synthetic planning scenario; all values below are fictional assumptions.
Randomly assign independent eligible customers 1:1 to personalized promotions \(treatment\) or generic promotions \(control\). Observe each customer for 30 days after assignment.
The primary metric is average card spending, measured in USD per customer during that 30-day window. The baseline mean is 200 USD and the baseline standard deviation is 100 USD for the same metric and window. The minimum meaningful effect is a 5% relative increase over the baseline mean.
For this toy example, assume no overlapping campaigns or spillovers between customers. Keep every assigned customer in the analysis, including zero-spend customers. Plan a fixed-horizon, two-sided comparison with alpha 0.05 and power 0.80; do not stop early based on interim results. No experiment results have been observed.

## Intake provenance

- population\_size: 100000 — user\_provided

- primary\_metric: average card spending — user\_provided

- metric\_type: continuous — user\_provided

- baseline\_mean: 200 — user\_provided

- baseline\_sd: 100 — user\_provided

- baseline\_conversion\_rate: Not provided — missing

- target\_relative\_uplift: 0.05 — user\_provided

## Proposed design

AI suggestions reviewed by the user; assumptions are not independently verified.

- design\_family: independent\_two\_arm

- hypothesis: Personalized credit-card promotions increase average card spending by at least 5% compared to generic promotions.

- treatment: Personalized credit-card promotions tailored to individual customer profiles.

- control: Generic, non-personalized credit-card promotions.

- randomization\_unit: Individual eligible customer.

- primary\_metric: average card spending

- observation\_period: 30 days following random assignment to treatment or control.

- allocation: 1:1 random assignment of eligible customers to treatment or control groups.

- rationale: The design compares personalized versus generic promotions on average spending per customer over 30 days, capturing direct individual-level effects. Randomization at the customer level avoids interference, and the continuous spending metric enables a two-sided fixed-horizon test for detecting a 5% uplift. Equal allocation maximizes power for the given population size and effect size assumptions.

### Proposal assumptions

- No interference or spillover effects across customers.
- Customer spending during the 30-day observation window reliably reflects promotion impact.
- Baseline mean and standard deviation are accurate and stable.
- Complete follow-up data is available for all assigned customers, including zero spenders.

### Open questions

- What is the planned sample size per group if different from equal allocation?
- Are there any known subpopulations that require stratified randomization?
- Is there a need to adjust for multiple metrics or tests?

### Proposal limitations

- The design assumes no interference and purely independent customers.
- Synthetic baseline parameters may differ from real-world data, affecting power.
- Fixed 30-day observation may miss longer-term effects.
- No provisions for adaptive or sequential analysis are included.

## Confirmed calculator inputs

These explicit inputs govern the calculation and may refine the initial intake.

- design\_family: independent\_two\_arm

- design\_confirmed: true

- independent\_units: true

- primary\_metric: average card spending

- metric\_type: continuous

- population\_size: 100000

- baseline\_mean: 200

- baseline\_sd: 100

- baseline\_conversion\_rate: Not provided

- effect\_type: relative

- effect\_value: 0.05

- alpha: 0.05

- power: 0.8

- allocation\_ratio: 1

## Deterministic statistical result

- Formula: continuous\_normal\_v1

- Control: 1570
- Treatment: 1570
- Total: 3140

- Pool feasible: true
- Actual treatment/control ratio: 1

- Approximate power: 0.8000569268798245
- Absolute effect: 10
- Binary target rate: Not applicable

### Calculation assumptions

- Independent units, two arms, random assignment, fixed horizon and one primary outcome.
- Two-sided normal approximation; no continuity correction or finite-population correction.
- No clustering, pairing, repeated measures, sequential testing or heavy interference.
- No attrition allowance; counts are analyzable units. Pool feasibility is not a duration estimate.
- Power is an approximation under supplied assumptions, not an observed result or guarantee.
- A common baseline standard deviation is assumed in both arms.

### Calculation warnings

None listed.

## Independent AI critique

The proposed randomized controlled trial design is broadly consistent with the confirmed statistical assumptions and objective, comparing personalized versus generic promotions at the individual level using average card spending over 30 days. The design uses appropriate randomization, metric, and analysis assumptions, and correctly excludes interim analyses or complex designs.

### MEDIUM: Metric Validity and Window

Evidence: The primary metric is average card spending over a fixed 30-day window post-assignment. The design notes this window may miss longer-term effects.

Short observation window may not fully capture behavioral changes that develop later or decline over time.

Mitigation: Consider tracking spending beyond 30 days or adding secondary metrics to assess sustained effects.

### MEDIUM: Baseline Assumptions

Evidence: Baseline mean of $200 and SD of $100 are synthetic and may differ from real data.

Incorrect baseline parameters would affect power and sample size calculations, potentially leading to underpowered or over-resourced studies.

Mitigation: Validate assumptions with pilot or historical data before full deployment.

### MEDIUM: Attrition and Data Completeness

Evidence: The design assumes complete follow-up and includes zero spenders. No attrition allowance is included in power calculations.

If customers drop out or data is missing, effective sample size and power decline.

Mitigation: Plan for data monitoring and consider robust imputation or sensitivity analyses for missing data.

### LOW: Randomization and Unit of Analysis

Evidence: Randomization is at the individual customer level with no clusters or pairing mentioned, matching the statistical assumption of independent units.

Randomizing individuals avoids aggregation bias and reduces risk of interference. However, the assumption of no interference may be fragile in credit card promotion contexts.

Mitigation: Carefully assess any possible cross-customer spillover or social influence effects during execution or consider sensitivity analyses.

### LOW: Open Design Questions

Evidence: Unresolved questions include sample size per group \(if different from equal allocation\), need for stratified randomization, and multiplicity adjustments.

Ignoring these elements could lead to confounding, imbalance, or inflated type I error if multiple hypotheses are tested.

Mitigation: Clarify these points before implementation and consider stratified randomization or correction procedures if applicable.

## Unresolved assumptions

- No known subpopulations requiring stratified randomization
- No concurrent campaigns or external factors affect spending during observation
- Equal variance and normality of spending within groups
- No multiple hypothesis testing beyond the primary metric

## Consistency and readiness checks

- Proposal questions remain open; review them before running an experiment.
- Proposal assumptions are acknowledged, not independently verified.

## Traceability

- Extraction request: 6a6ba896-09d9-4c5a-a073-7ca065d4ac45
- Design request: e6de8169-ce8e-4d90-9a6f-cf19ae27f737
- Review and recomputed statistics request: 0eb6f747-44f9-4096-b95e-ec40140d1a1c

Extraction: \{"model":"gpt-4.1-mini-2025-04-14","prompt\_version":"extract\_v2","latency\_ms":2608,"attempts":1,"input\_tokens":1512,"output\_tokens":111,"estimated\_cost\_usd":null\}

Design: \{"model":"gpt-4.1-mini-2025-04-14","prompt\_version":"design\_v1","latency\_ms":3671,"attempts":1,"input\_tokens":890,"output\_tokens":337,"estimated\_cost\_usd":null\}

Critique: \{"model":"gpt-4.1-mini-2025-04-14","prompt\_version":"critic\_v1","latency\_ms":7507,"attempts":1,"input\_tokens":1487,"output\_tokens":639,"estimated\_cost\_usd":null\}

## Statistical references

- https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html

- https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.power_proportions_2indep.html
