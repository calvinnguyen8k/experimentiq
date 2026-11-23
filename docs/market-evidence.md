# Problem and competitor evidence

Research date: 2026-11-23. Desk research only; no user interviews, demand validation,
market sizing, or uniqueness claim has been established.

| Adjacent product | Observed primary-source capability | Implication for ExperimentIQ |
|---|---|---|
| Statsig | Its [Power Analysis Calculator](https://docs.statsig.com/experiments/power-analysis) uses historical metric/traffic information and planned allocation, alpha and power; reports can remain attached to experiments. | Experiment sizing and traceable planning already have established tools. A standalone calculator is not a novel differentiator. |
| GrowthBook | [Version 4.0 release notes](https://www.growthbook.io/blog/growthbook-version-4-0) describe experiment decision criteria, insights, an experiment timeline and MCP integration. | Do not claim that structured experimentation workflows or AI integrations are absent from competitors. |
| Optimizely | Its [sample-size calculator](https://www.optimizely.com/tools/sample-size-calculator) accepts baseline conversion, relative MDE and significance; its stated method uses a sequential Stats Engine. | ExperimentIQ's fixed-horizon normal approximation is a different method; counts should not be advertised as interchangeable. |

The product hypothesis is narrower: PMs and growth analysts may benefit from a
small pre-launch workbench that makes missing assumptions, provenance and risks
visible before they configure an experiment platform. The app combines a draft,
a constrained Python calculation and an exportable critique. Whether users prefer
this workflow or would pay for it remains unknown.

Observed project feedback provides limited usability evidence: the project owner
could not find a next step after extraction or design, and requested a complete
synthetic example and Next buttons. These are direct workflow observations, not
independent market interviews. The implemented progression and gated controls
respond to that feedback; automated browser tests verify the mechanics, not user
satisfaction or market fit.

The user requested that the original seven course idea-validation steps not be
pursued. Record them as excluded by user direction, not completed. The supplied
assignment brief still lists those steps; this scope decision does not establish
course compliance. No checklist or interviews have been invented in their place.
