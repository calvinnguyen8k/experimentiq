# v2: add a human-reviewed benchmark for evidence-grounded risk critique

The current synthetic evaluation uses annotated extraction fields and keyword-based
risk detection. Those checks do not establish that a critique's evidence, severity,
or recommendations are correct.

After P0 deployment is complete, add a held-out benchmark with independently
reviewed risk labels and evidence spans. Include unsupported designs, contradictory
allocation/window assumptions, prompt injection, and uncertainty as the right answer.

Acceptance criteria:

- Separate development and held-out cases and version the annotations.
- Score evidence support, severity agreement, high-priority risk recall and
  unsupported claims; record disagreements for human adjudication.
- Compare prompt versions on identical held-out inputs and report failures,
  latency, and available token/cost data.
- Preserve Python-calculated statistics and explicit confirmation throughout.
- Publish limitations; do not substitute keyword matches for methodological validation.

This records future work only. Do not implement P2 before P0 deployment and verification.
