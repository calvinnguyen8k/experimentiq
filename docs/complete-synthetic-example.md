# Complete synthetic intake example

All values are fictional planning assumptions. No real customer data or observed
experiment results are represented.

## Copy-ready objective

We want to test personalized credit-card promotions versus generic promotions for
100,000 eligible customers. Our goal is to increase average card spending by 5%.

This is a fully synthetic planning scenario. Randomly assign independent eligible
customers 1:1 to personalized promotions (treatment) or generic promotions (control).
Observe each customer for 30 days after assignment.

The primary metric is average card spending, measured in USD per customer during
that 30-day window. The baseline mean is 200 USD and the baseline standard deviation
is 100 USD for the same metric and window. The minimum meaningful effect is a 5%
relative increase over the baseline mean.

For this toy example, assume no overlapping campaigns or spillovers between
customers. Keep every assigned customer in the analysis, including zero-spend
customers. Plan a fixed-horizon, two-sided comparison with alpha 0.05 and power
0.80; do not stop early based on interim results. No experiment results have been
observed.

## Confirmed form inputs

| Field | Synthetic value |
|---|---|
| Outcome type | Continuous · a mean |
| Primary metric | average card spending |
| Eligible population | 100000 |
| Target relative increase | 0.05 (5%) |
| Baseline mean | 200 USD per customer over 30 days |
| Baseline standard deviation | 100 USD, for the same metric/window |
| Baseline conversion rate | Leave blank; not applicable |

## Use in the app

Click **Load complete synthetic example**, review the populated fields, then click
**Extract experiment facts**. The expected status is **Intake complete**, with no
missing questions. A metric-wording note may appear if the AI paraphrases the metric.
Then click **Generate experiment design** to open the proposed design screen.

The preset does not auto-submit, bypass OpenAI, or fabricate output. Its numbers
become user-provided inputs because the user explicitly selects and submits the
demo. **Load example with missing data** resets the fields and demonstrates the
missing-information workflow instead.

“Complete” describes current intake completeness. A design draft can now be
generated; statistical calculation, independent risk review, and export remain
unimplemented. The alpha,
power, assignment, and observation-window details are narrative context for future
stages; this increment does not calculate a sample size or validate these plans.
