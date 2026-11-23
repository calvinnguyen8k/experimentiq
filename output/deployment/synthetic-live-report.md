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

- treatment: Personalized credit-card promotions offered to assigned customers.

- control: Generic credit-card promotions offered to assigned customers.

- randomization\_unit: Individual eligible customer.

- primary\_metric: average card spending

- observation\_period: 30 days post-assignment for each customer.

- allocation: 1:1 random assignment to personalized or generic promotion groups.

- rationale: Randomly assigning individual customers to treatment or control groups avoids contamination and allows measurement of spending behavior caused by promotion personalization. The primary metric is total spending summed per customer within 30 days post-exposure, capturing short-term impact on spending. The 1:1 allocation balances power and resource use for the planned sample size of 100,000.

### Proposal assumptions

- No spillover or interaction effects between customers.
- Customers remain in the study and spend data are fully observed for the entire 30-day period.
- Baseline mean and standard deviation are accurate for the population and time window.
- A 5% uplift in average spending is practically meaningful and detectable with planned sample size.

### Open questions

- Confirm method for handling and verifying zero-spend customers in analysis.
- Plan for controlling or monitoring other campaigns that might start during the experiment.
- Confirm exact start and end dates for 30-day observation to avoid overlapping promotions or seasonal effects.

### Proposal limitations

- Design assumes no customer interactions or interference, which may not perfectly hold in reality.
- Variation in individual spending and external factors may affect metric \(e.g., economic conditions\).
- Fixed horizon design does not allow early stopping or adaptive allocation.

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

The design aligns well with the objective and confirmed inputs, using individual randomization, correct metric, and matching observation window. Power and sample size calculations are consistent with assumptions. However, some risks related to operational and external validity remain unaddressed in the design and assumptions.

### MEDIUM: Contamination/Spillover

Evidence: Design assumes no spillover or interaction effects between customers; no overlapping campaigns assumed.

Despite assumptions, customers may share or discuss promotions or respond to other concurrent marketing efforts, potentially contaminating groups and diluting measured effects.

Mitigation: Monitor and control for concurrent campaigns during the experiment period; consider surveys or logs to detect cross-group interactions.

### MEDIUM: Attrition and Data Completeness

Evidence: Assumes customers remain in study and data is fully observed for 30 days; no allowance made for attrition or missing spend data.

Loss to follow-up, account closures, or unobserved spending could introduce attrition bias or reduce effective sample size, affecting power and internal validity.

Mitigation: Implement plans to track customer participation and identify missing data; include all assigned customers in analysis and consider sensitivity analyses for attrition.

### MEDIUM: Variance Assumptions and Metric Definition

Evidence: Baseline mean and standard deviation are assumed accurate and equal across arms; zero-spend customers included in primary metric.

If the real variance differs between groups or if spending distributions are highly skewed \(common in spending data\), the normal approximation and power calculation may be inaccurate.

Mitigation: Validate baseline variance with historical data; consider non-parametric or transformation methods if spending is highly skewed; pre-specify handling of zero-spend customers.

### MEDIUM: Open Operational Questions

Evidence: Open questions remain on zero-spend customer handling, controlling external campaigns, exact observation dates to avoid seasonality.

Without firm plans on these operational details, experiment validity and interpretability could be compromised due to uncontrolled confounding or inconsistent measurement windows.

Mitigation: Finalize and document procedures for identified open questions before launch, including start/end date confirmation to avoid seasonal or promotional overlaps.

### LOW: Selection Bias

Evidence: Randomization is at individual customer level with 1:1 allocation, intended to balance groups.

Although randomization minimizes selection bias, any deviations in random assignment implementation or enrollment filtering could bias results if not monitored.

Mitigation: Verify randomization integrity and monitor enrollment to ensure balance and no systematic differences between groups.

### LOW: Randomization and Analysis Unit Mismatch

Evidence: Randomization unit and analysis unit are both individual eligible customers with spending aggregated per customer over 30 days.

No mismatch observed; unit of randomization corresponds to unit of analysis, avoiding aggregation bias or interference at unit level.

Mitigation: Maintain this alignment throughout data processing and ensure outcome attribution strictly per assigned customers.

## Unresolved assumptions

- Zero-spend customer inclusion method and verification approach in analysis are not confirmed.
- Monitoring and controlling of other potential overlapping campaigns during experiment unclear.
- Exact start and end dates for the 30-day observation window not yet specified, risking overlap with other promotions or seasonal effects.

## Consistency and readiness checks

- Proposal questions remain open; review them before running an experiment.
- Proposal assumptions are acknowledged, not independently verified.

## Traceability

- Extraction request: f8cb253a-526b-4d88-adb0-8a2696d2570c
- Design request: ead28cac-bc25-4e4c-9552-eba784724f3d
- Review and recomputed statistics request: 8271a4d5-7682-4ed4-a4a9-5fd260352fb9

Extraction: \{"model":"gpt-4.1-mini-2025-04-14","prompt\_version":"extract\_v2","latency\_ms":3922,"attempts":1,"input\_tokens":1512,"output\_tokens":112,"estimated\_cost\_usd":null\}

Design: \{"model":"gpt-4.1-mini-2025-04-14","prompt\_version":"design\_v1","latency\_ms":5183,"attempts":1,"input\_tokens":890,"output\_tokens":349,"estimated\_cost\_usd":null\}

Critique: \{"model":"gpt-4.1-mini-2025-04-14","prompt\_version":"critic\_v1","latency\_ms":8416,"attempts":1,"input\_tokens":1501,"output\_tokens":675,"estimated\_cost\_usd":null\}

## Statistical references

- https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html

- https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.power_proportions_2indep.html
