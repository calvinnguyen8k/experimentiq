import { ApiError } from "@/lib/api";
import { StatisticalForm, StatisticalResult } from "@/lib/contracts";

export function StageError({ error }: { error: ApiError | null }) {
  return error && <div className="error-box" role="alert" aria-label="Step could not finish"><strong>This step could not finish</strong><p>{error.message}</p>{error.requestId && <small>Request {error.requestId}</small>}</div>;
}

export function StatisticsPanel({ form, onChange, confirmed, onConfirm, result, error, busy, onCalculate, onNext, onBack }: {
  form: StatisticalForm; onChange: (key: keyof StatisticalForm, value: string) => void;
  confirmed: boolean; onConfirm: (value: boolean) => void; result: StatisticalResult | null;
  error: ApiError | null; busy: boolean; onCalculate: () => void; onNext: () => void; onBack: () => void;
}) {
  const fields: { key: keyof StatisticalForm; label: string; hint: string; min?: number; max?: number; step?: string }[] = [
    { key: "population_size", label: "Eligible population", hint: "Independent eligible units", min: 2, max: 1e9, step: "1" },
    ...(form.metric_type === "continuous" ? [
      { key: "baseline_mean" as const, label: "Baseline mean", hint: "Same metric and observation window", min: -1e12, max: 1e12 },
      { key: "baseline_sd" as const, label: "Baseline standard deviation", hint: "Positive; common SD in both arms", min: 1e-12, max: 1e12 },
    ] : form.metric_type === "binary" ? [
      { key: "baseline_conversion_rate" as const, label: "Baseline conversion rate", hint: "Decimal: 0.10 means 10%", min: 1e-12, max: .999999999999 },
    ] : []),
    { key: "effect_value", label: "Minimum detectable increase", hint: form.effect_type === "relative" ? "Decimal: 0.05 means 5% relative increase" : "Metric units; for binary, 0.02 means 2 percentage points", min: 1e-12, max: 1e12 },
    { key: "alpha", label: "Significance level (alpha)", hint: "Two-sided; default 0.05", min: .000001, max: .5 },
    { key: "power", label: "Target power", hint: "Decimal; default 0.80", min: .500001, max: .999999 },
    { key: "allocation_ratio", label: "Treatment/control allocation ratio", hint: "1 = equal groups; 2 = twice as many treatment units", min: .01, max: 100 },
  ];
  const missing = !form.metric_type || fields.some(f => form[f.key].trim() === "");
  return <section className="panel proposal-panel" tabIndex={-1} aria-labelledby="statistics-title">
    <div className="panel-heading"><div><p className="eyebrow">STEP 3 OF 4</p><h2 id="statistics-title">Statistical validation</h2></div><button className="text-button" disabled={busy} onClick={onBack}>Back to design</button></div>
    <p className="muted">Confirm the numeric assumptions below. Values come from your intake entries, never AI extraction. Alpha, power and allocation start with visible defaults. Use the same metric and window as your design.</p>
    <form onSubmit={e => { e.preventDefault(); onCalculate(); }}>
      <fieldset disabled={busy}>
        <div className="form-grid">
          <div className="field"><label htmlFor="stats-metric">Outcome type</label><select id="stats-metric" required value={form.metric_type} onChange={e => onChange("metric_type", e.target.value)}><option value="">Choose outcome type</option><option value="continuous">Continuous · a mean</option><option value="binary">Binary · a rate</option></select></div>
          <div className="field"><label htmlFor="stats-effect">Effect definition</label><select id="stats-effect" value={form.effect_type} onChange={e => onChange("effect_type", e.target.value)}><option value="relative">Relative increase</option><option value="absolute">Absolute increase</option></select></div>
          {fields.map(({ key, label, hint, min, max, step }) => <div className="field" key={key}><label htmlFor={`stats-${key}`}>{label}</label><input id={`stats-${key}`} type="number" required min={min} max={max} step={step ?? "any"} value={form[key]} onChange={e => onChange(key, e.target.value)} aria-describedby={`hint-${key}`} aria-invalid={error?.fields.includes(key) || undefined} /><span id={`hint-${key}`} className="field-hint">{hint}</span></div>)}
        </div>
        <label className="confirmation"><input type="checkbox" checked={confirmed} onChange={e => onConfirm(e.target.checked)} />I confirm these numerical inputs and an independent two-arm, fixed-horizon comparison, without clustering, pairing, repeated measures or heavy interference.</label>
        <button className="primary-button" disabled={!confirmed || missing} type="submit">{busy ? "Working…" : "Calculate sample size"}</button>
        {(!confirmed || missing) && <p className="muted">{missing ? "Fill in all applicable fields, then confirm the assumptions to calculate." : "Confirm the assumptions above to enable calculation."}</p>}
      </fieldset>
    </form>
    <StageError error={error} />
    {result && <div aria-live="polite">
      {result.status === "computed" ? <>
        <div className={`result-status ${result.feasible ? "" : "attention"}`}><strong>{result.feasible ? "Fits your eligible population" : "Sample exceeds your eligible population"}</strong><p>Python calculation · planning approximation · no observed experiment results</p></div>
        <dl className="stat-cards"><div><dt>Control</dt><dd>{result.n_control?.toLocaleString("en-US")}</dd></div><div><dt>Treatment</dt><dd>{result.n_treatment?.toLocaleString("en-US")}</dd></div><div><dt>Total required</dt><dd>{result.total?.toLocaleString("en-US")}</dd></div></dl>
        <p>Approximate power after rounding: {((result.achieved_power ?? 0) * 100).toFixed(2)}%. Actual treatment/control ratio: {result.actual_allocation_ratio?.toFixed(4)}. Absolute increase: {result.absolute_effect?.toLocaleString("en-US", { maximumSignificantDigits: 8 })}.</p>
        {result.warnings.length > 0 && <div className="conflict-list"><strong>Planning limitations</strong><ul>{result.warnings.map(x => <li key={x}>{x}</li>)}</ul></div>}
        <details className="assumptions"><summary>Formula and assumptions</summary><p>{result.formula_id}</p><ul>{result.assumptions.map(x => <li key={x}>{x}</li>)}</ul><p>Request {result.request_id}</p></details>
      </> : <div className="result-status attention"><strong>Calculation needs attention</strong><ul>{result.questions.map(x => <li key={x}>{x}</li>)}</ul></div>}
    </div>}
    <div className="stage-actions"><button className="primary-button" disabled={busy || result?.status !== "computed"} onClick={onNext}>{busy ? "Working…" : "Next: Review & export →"}</button><p className="muted">{result?.status === "computed" ? "Review design risks next. Infeasible plans can be reviewed and exported as drafts with warnings." : "Calculate a sample size before moving to the review."}</p></div>
  </section>;
}
