# ExperimentIQ: implementation reflection

This reflection describes observed project work. It is a draft for the project
owner to review and personalize before submitting as an individual assignment.

ExperimentIQ started with a focused goal: help a product manager turn a vague A/B
test idea into a plan whose assumptions are visible. The most useful architectural
decision was to separate interpretation from calculation. OpenAI extracts facts,
proposes a design, and critiques risks in distinct structured calls. Python alone
calculates sample sizes. Explicitly entered values, unconfirmed extractions,
AI suggestions, and derived results retain separate provenance.

The first usable slice exposed a product problem that unit tests alone did not
catch. After extraction, the project owner could not find a way to continue.
Adding a design screen still left another dead end. The resulting four-stage
workflow now shows a destination-labelled Next button, explains missing
requirements, and lets the user revisit reached stages. Confirming a draft is
separate from confirming numeric assumptions. Editing earlier inputs clears later
results, preventing an old calculation from appearing in a new report.

The deterministic engine supports independent two-arm continuous and binary
outcomes, positive absolute or relative effects, and unequal allocation. Tests
compare its counts and rounded-allocation power against Statsmodels. Missing
baselines and unsupported designs return no sample size. The review endpoint
recomputes statistics instead of trusting client-supplied results, and the critic
cannot overwrite those numbers. This constraint matters more than persuasive
AI prose: a well-written explanation cannot rescue an invalid input.

Verification combined provider-mocked browser tests with a real 20-case model
evaluation. The first evaluation revealed ambiguous annotations and missing
eligible-population extractions. Earlier runs were preserved; annotations were
clarified and a versioned prompt correction was tested. Keyword matching is useful
for regression signals but cannot establish that a risk's evidence or severity is
correct. A human-reviewed, held-out benchmark is the next evaluation improvement.

Operational work also exposed practical limits. An incompatible Redis testing
dependency needed a version bound. Public hosting requires durable shared quotas,
not only an in-memory limiter that resets on restart. Production configuration now
fails closed without HTTPS origins and shared rate protection. The demo has a daily
request cap, bounded retries, and metadata-only logging; free hosting still does
not make OpenAI calls free.

The project demonstrates a tested local planning workflow, not proven market
fit or a guarantee of experimental validity. Public deployment, hosted CI and
submission links must be checked independently. No interviews were invented, and
the original seven course validation steps remain excluded at the owner's request.
The central lesson is to verify the whole user journey and preserve uncertainty,
while treating clear navigation, numerical correctness, and honest evidence as
parts of the same engineering task.
