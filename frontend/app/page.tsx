"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { ApiError, extractExperiment } from "@/lib/api";
import { emptyForm, example, ExtractionResponse, FieldName, FormValues, labels } from "@/lib/contracts";

const numberFields: { name: FieldName; hint: string; min?: number; max?: number; step?: string }[] = [
  { name: "population_size", hint: "Independent eligible units", min: 2, max: 1_000_000_000, step: "1" },
  { name: "target_relative_uplift", hint: "Decimal · 0.05 means a 5% increase", min: 0.000000001, max: 10 },
  { name: "baseline_mean", hint: "In your metric’s units", min: -1e12, max: 1e12 },
  { name: "baseline_sd", hint: "Same units as the mean · must be positive", min: 0.000000001, max: 1e12 },
  { name: "baseline_conversion_rate", hint: "Decimal · 0.10 means 10%", min: 0.000000001, max: 0.999999999 },
];

export default function Home() {
  const [form, setForm] = useState<FormValues>({ ...emptyForm });
  const [result, setResult] = useState<ExtractionResponse | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [busy, setBusy] = useState(false);
  const active = useRef<AbortController | null>(null);
  useEffect(() => () => active.current?.abort(), []);

  function update(name: keyof FormValues, value: string) {
    setForm((old) => ({ ...old, [name]: value,
      ...(name === "metric_type" && value === "continuous" ? { baseline_conversion_rate: "" } : {}),
      ...(name === "metric_type" && value === "binary" ? { baseline_mean: "", baseline_sd: "" } : {}),
    }));
    setResult(null); setError(null);
  }

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    if (form.objective.trim().length < 20) {
      setError(new ApiError("Describe the experiment in at least 20 characters.", undefined, ["objective"]));
      return;
    }
    setBusy(true); setResult(null); setError(null);
    const controller = new AbortController(); active.current = controller;
    const timeout = setTimeout(() => controller.abort(), 50_000);
    try { setResult(await extractExperiment(form, controller.signal)); }
    catch (caught) {
      setError(caught instanceof ApiError ? caught : new ApiError(
        controller.signal.aborted ? "The request timed out. Please try again." :
          "Could not reach the API. Check that the backend is running, then try again.",
      ));
    } finally { clearTimeout(timeout); setBusy(false); active.current = null; }
  }

  const known = result ? Object.values(result.facts).filter((fact) => fact.value !== null).length : 0;
  return (
    <main>
      <header className="topbar">
        <Link href="/" className="brand" aria-label="ExperimentIQ home"><span className="brand-mark" aria-hidden="true">E</span>Experiment<span className="brand-iq">IQ</span></Link>
        <span className="topbar-label">EXPERIMENT DESIGN WORKSPACE</span>
        <span className="edition">First slice · Intake</span>
      </header>

      <section className="intro">
        <div><p className="eyebrow">START WITH WHAT YOU KNOW</p><h1>Better experiments<br />begin with clear inputs.</h1>
          <p className="intro-copy">Unpack your idea into traceable facts. Find the missing assumptions before you design the test.</p></div>
        <aside className="scope-note"><span className="scope-icon" aria-hidden="true">≋</span><strong>Clarity before calculation</strong><p>This step extracts and checks your inputs. Design recommendations and sample-size calculations come later.</p></aside>
      </section>

      <nav aria-label="Workflow" className="workflow">
        <span className="step active" aria-current="step">Experiment intake</span>
        <span className="step">Design proposal <small>Planned</small></span>
        <span className="step">Statistical validation <small>Planned</small></span>
        <span className="step">Review & export <small>Planned</small></span>
      </nav>

      <div className="workspace">
        <section className="panel intake-panel" aria-labelledby="intake-title">
          <div className="panel-heading"><div><p className="eyebrow">YOUR STARTING POINT</p><h2 id="intake-title">Describe the experiment</h2></div><span className="tag">Input</span></div>
          <p className="privacy-note">Use synthetic or public toy data only. Do not paste confidential information or customer data. Your description is sent to OpenAI for extraction.</p>
          <form onSubmit={submit}>
            <fieldset disabled={busy}>
              <div className="label-row"><label htmlFor="objective">Experiment objective <span className="required">*</span></label>
                <button type="button" className="text-button" onClick={() => { setForm({ ...emptyForm, objective: example }); setError(null); setResult(null); }}>Load synthetic example</button></div>
              <textarea id="objective" name="objective" required minLength={20} maxLength={4000} rows={7}
                placeholder="What are you changing, who is eligible, and what outcome do you want to improve?"
                value={form.objective} onChange={(event) => update("objective", event.target.value)}
                aria-describedby="objective-hint" aria-invalid={error?.fields.includes("objective") || undefined} />
              <div id="objective-hint" className="field-footer"><span>Include the comparison, metric, and any known assumptions.</span><span>{form.objective.length}/4,000</span></div>
              <details className="assumptions">
                <summary>Optional confirmed inputs <span>Fill in what you know</span></summary>
                <p className="muted">Leave unknowns blank. Values entered here are treated as your confirmed inputs. Correct conflicting prose before rerunning.</p>
                <div className="form-grid">
                  <div className="field"><label htmlFor="metric_type">Outcome type</label><select id="metric_type" value={form.metric_type} onChange={(e) => update("metric_type", e.target.value)} aria-describedby="metric-type-hint" aria-invalid={error?.fields.includes("metric_type") || undefined}><option value="">Not yet known</option><option value="continuous">Continuous · a mean</option><option value="binary">Binary · a conversion rate</option></select><span id="metric-type-hint" className="field-hint">Average spending is continuous; converted/not converted is binary. Changing type clears incompatible baseline inputs.</span></div>
                  <div className="field"><label htmlFor="primary_metric">Primary metric</label><input id="primary_metric" maxLength={200} value={form.primary_metric} onChange={(e) => update("primary_metric", e.target.value)} placeholder="e.g. mean spending per customer over 30 days" /></div>
                  {numberFields.filter(({ name }) =>
                    !(form.metric_type === "continuous" && name === "baseline_conversion_rate") &&
                    !(form.metric_type === "binary" && ["baseline_mean", "baseline_sd"].includes(name))
                  ).map(({ name, hint, min, max, step }) => <div className="field" key={name}>
                    <label htmlFor={name}>{labels[name]}</label><input id={name} type="number" min={min} max={max} step={step || "any"}
                      value={form[name]} onChange={(e) => update(name, e.target.value)} aria-describedby={`${name}-hint`} aria-invalid={error?.fields.includes(name) || undefined} />
                    <span id={`${name}-hint`} className="field-hint">{hint}</span></div>)}
                </div>
              </details>
              <button className="primary-button" type="submit">{busy ? <><span className="spinner" aria-hidden="true" />Extracting facts…</> : "Extract experiment facts"}</button>
              <p className="submit-note">Unknowns stay unknown. AI interpretations always need your confirmation.</p>
            </fieldset>
          </form>
          {error && <div className="error-box" role="alert" aria-labelledby="extraction-error-heading"><strong id="extraction-error-heading">Extraction could not finish</strong><p>{error.message}</p>{error.fields.length > 0 && <p>Check: {error.fields.map((f) => labels[f as FieldName] || f).join(", ")}</p>}{error.requestId && <small>Request {error.requestId}</small>}</div>}
        </section>

        <section className="panel result-panel" aria-labelledby="results-title" aria-live="polite" aria-busy={busy}>
          <div className="panel-heading"><div><p className="eyebrow">MAKE THE GAPS VISIBLE</p><h2 id="results-title">Your experiment, unpacked</h2></div><span className="tag">{result ? `${known} facts` : "Output"}</span></div>
          {!result && <div className="empty-state"><div className="empty-illustration" aria-hidden="true"><span /><span /><span /><i /></div>
            <h3>{busy ? "Reading your experiment idea" : "A clearer starting point"}</h3><p>{busy ? "Extracting stated facts and checking the supporting evidence. This can take a few moments." : "Add your objective to see what’s known, what needs confirmation, and what’s still missing."}</p>
            <ul className="expectations"><li>Facts linked to your description</li><li>Explicit unknowns, without invented values</li><li>Focused questions for the next iteration</li></ul></div>}
          {result && <>
            <div className={`result-status ${result.status === "needs_attention" ? "attention" : ""}`}><strong>{result.status === "needs_attention" ? "Resolve conflicting assumptions" : result.status === "missing_information" ? "A few details need your attention" : "Intake complete"}</strong><p>Extraction only. No design validation or sample size has been calculated.</p></div>
            {result.conflicts.length > 0 && <div className="conflict-list"><h3>Conflicts to resolve</h3>{result.conflicts.map((conflict, index) => <p key={index}><strong>{labels[conflict.field as FieldName] || conflict.field}: </strong>{conflict.message}{conflict.supplied_value !== null && <> Form: {conflict.supplied_value}. Prose: {conflict.extracted_value}.</>}</p>)}</div>}
            {result.metric_wording_note && <aside className="privacy-note" style={{ marginTop: 16 }}><strong>Metric wording note</strong><p>{result.metric_wording_note.message}</p><p>Your metric: {result.metric_wording_note.supplied_value}. AI wording: {result.metric_wording_note.extracted_value}.</p></aside>}
            <dl className="fact-list">{(Object.keys(labels) as FieldName[]).map((name) => {
              const fact = result.facts[name];
              return <div className="fact-row" key={name}><dt>{labels[name]}</dt><dd>
                <div className="fact-value"><span>{fact.value === null ? <span className="unknown">Not provided</span> : typeof fact.value === "number" ? fact.value.toLocaleString("en-US", { maximumFractionDigits: 9 }) : fact.value}</span>
                  {fact.source !== "missing" && <span className={`provenance ${fact.source}`}>{fact.requires_confirmation ? "Confirm extraction" : "Your input"}</span>}</div>
                {fact.evidence && <blockquote>{fact.evidence}</blockquote>}
              </dd></div>;
            })}</dl>
            {result.questions.length > 0 && <div className="questions"><h3>What to clarify next <span>{result.questions.length}</span></h3><p className="muted">Update your description or the optional confirmed inputs, then extract again.</p><ul>{result.questions.map((question) => <li key={question.field}><span className="question-kind">{question.reason === "missing" ? "Missing" : "Confirm"}</span>{question.question}</li>)}</ul></div>}
            <div className="result-meta"><span>{result.metadata.model} · {result.metadata.prompt_version}</span><span>{(result.metadata.latency_ms / 1000).toFixed(1)}s</span><small>Request {result.request_id}</small></div>
          </>}
        </section>
      </div>
      <footer><span>ExperimentIQ</span><p>Make assumptions visible. Make the next decision clearer.</p><span>Local development · v0.1</span></footer>
    </main>
  );
}
