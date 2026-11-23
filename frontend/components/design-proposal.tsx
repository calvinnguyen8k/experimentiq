import { DesignResponse, labels } from "@/lib/contracts";

const fields = {
  hypothesis: "Hypothesis", treatment: "Treatment", control: "Control",
  randomization_unit: "Unit of randomization", primary_metric: "Primary metric",
  observation_period: "Observation period", allocation: "Allocation",
} as const;

export function DesignProposal({ result, onBack, confirmed, onConfirm, onNext }: {
  result: DesignResponse; onBack: () => void; confirmed: boolean;
  onConfirm: (value: boolean) => void; onNext: () => void;
}) {
  const draft = result.design;
  return <section className="panel proposal-panel" aria-labelledby="proposal-title" tabIndex={-1}>
    <div className="panel-heading"><div><p className="eyebrow">STEP 2 OF 4</p><h2 id="proposal-title">Proposed experiment design</h2></div><button className="text-button" onClick={onBack}>Back to intake</button></div>
    <div className={`result-status ${result.status === "needs_attention" ? "attention" : ""}`}><strong>{result.status === "proposal_ready" ? "Your draft design is ready" : "This design needs clarification"}</strong><p>AI-generated suggestions for your review. This is not statistical validation or a completed risk review.</p></div>
    <p className="proposal-rationale">{draft.rationale}</p>
    <dl className="proposal-grid">{Object.entries(fields).map(([key, label]) => <div key={key} className="proposal-field"><dt>{label}<span className="provenance llm_extracted">{key === "primary_metric" && result.metric_source === "user_provided" ? "Your input" : "AI suggestion"}</span></dt><dd>{draft[key as keyof typeof fields] ?? "Needs clarification"}</dd></div>)}</dl>
    <div className="proposal-grid">{([
      ["Assumptions to confirm", draft.assumptions], ["Open questions", draft.open_questions],
      ["Limitations", draft.limitations],
    ] as const).map(([title, items]) => <section key={title}><h3>{title}</h3>{items.length ? <ul className="proposal-notes">{items.map((item, index) => <li key={index}>{item}</li>)}</ul> : <p className="muted">None listed by the proposal. Review the design before use.</p>}</section>)}</div>
    <details className="assumptions"><summary>Your confirmed planning inputs</summary><p className="muted">These are the form inputs you submitted. The AI cannot replace these numbers.</p><dl className="fact-list">{Object.entries(labels).map(([key, label]) => <div className="fact-row" key={key}><dt>{label}</dt><dd>{result.planning_inputs[key as keyof typeof labels] ?? "Not provided"}</dd></div>)}</dl></details>
    <label className="confirmation"><input type="checkbox" checked={confirmed} disabled={result.status !== "proposal_ready"} onChange={e => onConfirm(e.target.checked)} />I have reviewed this design, its assumptions and open questions, and accept it as the draft for sample-size planning.</label>
    <div className="stage-actions"><button className="primary-button" disabled={!confirmed || result.status !== "proposal_ready"} onClick={onNext}>Next: Statistical validation →</button><p className="muted">{result.status !== "proposal_ready" ? "This design is unsupported or unclear. Use Back to intake to revise it before calculating." : confirmed ? "Continue to confirm numerical inputs and calculate the required sample." : "Review and accept the draft above to enable the next step."}</p></div>
    <div className="result-meta"><span>{result.metadata.model} · {result.metadata.prompt_version}</span><span>{(result.metadata.latency_ms / 1000).toFixed(1)}s</span><small>Request {result.request_id}</small></div>
  </section>;
}
