import { ReviewResponse } from "@/lib/contracts";
import { downloadReport } from "@/lib/report";

export function ReviewPanel({ result, report, acknowledged, onAcknowledge, onBack }: {
  result: ReviewResponse; report: string; acknowledged: boolean;
  onAcknowledge: (value: boolean) => void; onBack: () => void;
}) {
  return <section className="panel proposal-panel" tabIndex={-1} aria-labelledby="review-title">
    <div className="panel-heading"><div><p className="eyebrow">STEP 4 OF 4</p><h2 id="review-title">Review & export</h2></div><button className="text-button" onClick={onBack}>Back to statistics</button></div>
    <div className={`result-status ${result.status === "review_needs_attention" ? "attention" : ""}`}><strong>{result.status === "review_needs_attention" ? "Draft plan has items to address" : "Review complete"}</strong><p>AI critique is advice. Exporting this draft does not validate assumptions or authorize launching an experiment.</p></div>
    <p className="proposal-rationale">{result.critique.summary}</p>
    <h3>Ranked design risks</h3>
    {result.critique.risks.length ? result.critique.risks.map((risk, i) => <article className="risk-card" key={i}><h3><span className={`risk-level ${risk.severity}`}>{risk.severity}</span>{risk.category}</h3><blockquote>{risk.evidence}</blockquote><p>{risk.explanation}</p><p><strong>Recommended action: </strong>{risk.recommendation}</p></article>) : <p className="muted">No risks listed by the critic. This is not evidence that the experiment is risk-free.</p>}
    <div className="proposal-grid">{[["Unresolved assumptions", result.critique.unresolved_assumptions], ["Consistency and readiness checks", result.checks], ["Proposal questions", result.design.open_questions], ["Proposal assumptions", result.design.assumptions]].map(([title, items]) => <section key={title as string}><h3>{title}</h3>{(items as string[]).length ? <ul>{(items as string[]).map((x, i) => <li key={i}>{x}</li>)}</ul> : <p className="muted">None listed.</p>}</section>)}</div>
    <h3>Calculation retained by Python</h3><p>{result.statistics.n_control?.toLocaleString("en-US")} control + {result.statistics.n_treatment?.toLocaleString("en-US")} treatment = {result.statistics.total?.toLocaleString("en-US")} total. Pool feasible: {result.statistics.feasible ? "Yes" : "No"}.</p>
    <details className="assumptions"><summary>Preview complete Markdown report</summary><pre className="report-preview">{report}</pre></details>
    <label className="confirmation"><input type="checkbox" checked={acknowledged} onChange={e => onAcknowledge(e.target.checked)} />I have reviewed the risks and unresolved assumptions. I understand this export is a draft plan, not approval to run the experiment.</label>
    <div className="stage-actions"><button className="primary-button" disabled={!acknowledged} onClick={() => downloadReport(report)}>Download Markdown report</button><p className="muted">{acknowledged ? "All four workflow stages are complete. Download the draft or revisit any stage above." : "Acknowledge the review above to enable the download."}</p></div>
    <div className="result-meta"><span>{result.metadata.model} · {result.metadata.prompt_version}</span><span>{(result.metadata.latency_ms / 1000).toFixed(1)}s</span><small>Request {result.request_id}</small></div>
  </section>;
}
