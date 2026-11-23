# Two-minute ExperimentIQ walkthrough

The companion video uses screenshots from automated browser tests. AI responses
shown in those screens are provider fixtures; the sample-size calculation is real
Python. Live OpenAI evaluation is recorded separately in `evals/results/`. This
video is a reproducible product walkthrough, not evidence of public deployment.

| Time | Screen / action | Explanation |
|---|---|---|
| 0:00-0:10 | Product introduction | ExperimentIQ turns an experiment idea into a draft plan, calculation and risk review. |
| 0:10-0:20 | Intake | Use synthetic data. The complete preset supplies explicit fictional baselines and an eligible pool. |
| 0:20-0:30 | Extracted facts | User entries, quoted extractions and unknowns retain distinct provenance. |
| 0:30-0:40 | Missing inputs | Missing mean/SD stays unknown. No fabricated sample size fills the gap. |
| 0:40-0:50 | Design proposal | A separate structured AI call proposes hypothesis, arms, assignment, metric and window. |
| 0:50-1:00 | Design gate | Accept the draft before Next: Statistical validation becomes available. |
| 1:00-1:10 | Numerical inputs | Review mean 200, SD 100, 5% effect, alpha .05, power .8 and equal allocation. |
| 1:10-1:20 | Calculation | Python returns 1,570 per arm: 3,140 total, within the 100,000-unit pool. |
| 1:20-1:30 | Review | The critic ranks risks and recommends mitigations; it cannot replace the calculation. |
| 1:30-1:40 | Unresolved issues | Assumptions and open questions remain visible. Export does not authorize launch. |
| 1:40-1:50 | Markdown report | Acknowledge the review, preview the complete report, then download a Markdown draft. |
| 1:50-2:00 | Iteration and limits | Go back to edit; downstream results clear. Scope is independent two-arm, fixed-horizon planning. |

For the final public-site demonstration, repeat these actions in a fresh/incognito
browser against the deployed URL, using real OpenAI responses, and record the
verified URL alongside the video. Do not describe fixture screenshots as live AI.
