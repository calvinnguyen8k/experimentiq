import { DesignResponse, labels } from "@/lib/contracts";

const fields = {
  hypothesis: "Hypothesis", treatment: "Treatment", control: "Control",
  randomization_unit: "Unit of randomization", primary_metric: "Primary metric",
  observation_period: "Observation period", allocation: "Allocation",
} as const;

export function DesignProposal({ result, onBack }: { result: DesignResponse; onBack: () => void }) {
  const draft = result.design;
  return <section className="panel proposal-panel" aria-labelledby="proposal-title" tabIndex={-1}>
    <div className="panel-heading"><div><p className="eyebrow">YOUR NEXT STEP</p><h2 id="proposal-title">Proposed experiment design</h2></div><button className="text-button" onClick={onBack}>Back to intake</button></div>
    <div className={`result-status ${result.status === "needs_attention" ? "attention" : ""}`}><strong>{result.status === "proposal_ready" ? "Your draft design is ready" : "This design needs clarification"}</strong><p>AI-generated suggestions for your review. This is not statistical validation or a completed risk review.</p></div>
    <p className="proposal-rationale">{draft.rationale}</p>
    <dl className="proposal-grid">{Object.entries(fields).map(([key, label]) => <div key={key} className="proposal-field"><dt>{label}<span className="provenance llm_extracted">{key === "primary_metric" && result.metric_source === "user_provided" ? "Your input" : "AI suggestion"}</span></dt><dd>{draft[key as keyof typeof fields] ?? "Needs clarification"}</dd></div>)}</dl>
    <div className="proposal-grid">{([
      ["Assumptions to confirm", draft.assumptions], ["Open questions", draft.open_questions],
      ["Limitations", draft.limitations],
    ] as const).map(([title, items]) => <section key={title}><h3>{title}</h3>{items.length ? <ul className="proposal-notes">{items.map((item, index) => <li key={index}>{item}</li>)}</ul> : <p className="muted">None listed by the proposal. Review the design before use.</p>}</section>)}</div>
    <details className="assumptions"><summary>Your confirmed planning inputs</summary><p className="muted">These are the form inputs you submitted. The AI cannot replace these numbers.</p><dl className="fact-list">{Object.entries(labels).map(([key, label]) => <div className="fact-row" key={key}><dt>{label}</dt><dd>{result.planning_inputs[key as keyof typeof labels] ?? "Not provided"}</dd></div>)}</dl></details>
    <aside className="privacy-note"><strong>What comes next</strong><p>Review these suggestions and use Back to intake to revise your inputs. Sample-size calculation, independent risk review, and report export are planned stages and are not available yet.</p></aside>
    <div className="result-meta"><span>{result.metadata.model} · {result.metadata.prompt_version}</span><span>{(result.metadata.latency_ms / 1000).toFixed(1)}s</span><small>Request {result.request_id}</small></div>
  </section>;
}
