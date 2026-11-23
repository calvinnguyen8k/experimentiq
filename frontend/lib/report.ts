import { DesignResponse, ExtractionResponse, ReviewResponse } from "./contracts";

// Escape untrusted prose so downloaded Markdown cannot introduce HTML, links or images.
const safe = (value: unknown): string => String(value ?? "Not provided")
  .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
  .replace(/([\\`*_{}\[\]()#!|])/g, "\\$1");
const list = (items: string[]) => items.length ? items.map(x => `- ${safe(x)}`).join("\n") : "None listed.";
export function markdownReport(review: ReviewResponse, extraction: ExtractionResponse, proposal: DesignResponse): string {
  const s = review.statistics;
  return [
    "# ExperimentIQ — Draft experiment plan", "Synthetic/public toy planning data only. No experiment has been run.",
    `Status: ${safe(review.status)}. Export records the plan and risks; it is not approval to launch.`,
    "## Objective", safe(review.objective),
    "## Intake provenance", ...Object.entries(extraction.facts).map(([key, f]) =>
      `- ${safe(key)}: ${safe(f.value)} — ${safe(f.source)}${f.requires_confirmation ? "; unconfirmed extraction" : ""}${f.evidence ? `; evidence: ${safe(f.evidence)}` : ""}`),
    "## Proposed design", "AI suggestions reviewed by the user; assumptions are not independently verified.",
    ...Object.entries(review.design).filter(([, v]) => !Array.isArray(v)).map(([k, v]) => `- ${safe(k)}: ${safe(v)}`),
    "### Proposal assumptions", list(review.design.assumptions), "### Open questions", list(review.design.open_questions),
    "### Proposal limitations", list(review.design.limitations),
    "## Confirmed calculator inputs", "These explicit inputs govern the calculation and may refine the initial intake.",
    ...Object.entries(s.inputs).map(([k, v]) => `- ${safe(k)}: ${safe(v)}`),
    "## Deterministic statistical result", `- Formula: ${safe(s.formula_id)}`,
    `- Control: ${s.n_control}\n- Treatment: ${s.n_treatment}\n- Total: ${s.total}`,
    `- Pool feasible: ${s.feasible}\n- Actual treatment/control ratio: ${s.actual_allocation_ratio}`,
    `- Approximate power: ${s.achieved_power}\n- Absolute effect: ${s.absolute_effect}\n- Binary target rate: ${s.target_rate ?? "Not applicable"}`,
    "### Calculation assumptions", list(s.assumptions), "### Calculation warnings", list(s.warnings),
    "## Independent AI critique", safe(review.critique.summary),
    ...review.critique.risks.map(r => `### ${safe(r.severity.toUpperCase())}: ${safe(r.category)}\n\nEvidence: ${safe(r.evidence)}\n\n${safe(r.explanation)}\n\nMitigation: ${safe(r.recommendation)}`),
    "## Unresolved assumptions", list(review.critique.unresolved_assumptions),
    "## Consistency and readiness checks", list(review.checks),
    "## Traceability", `- Extraction request: ${safe(extraction.request_id)}\n- Design request: ${safe(proposal.request_id)}\n- Review and recomputed statistics request: ${safe(review.request_id)}`,
    ...[["Extraction", extraction.metadata], ["Design", proposal.metadata], ["Critique", review.metadata]].map(([stage, metadata]) => `${stage}: ${safe(JSON.stringify(metadata))}`),
    "## Statistical references", "- https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html",
    "- https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.power_proportions_2indep.html",
  ].join("\n\n") + "\n";
}
export function downloadReport(text: string) {
  const url = URL.createObjectURL(new Blob([text], { type: "text/markdown;charset=utf-8" }));
  const link = document.createElement("a"); link.href = url; link.download = "experimentiq-draft-plan.md";
  document.body.appendChild(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
