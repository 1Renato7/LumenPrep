"use client";

import Link from "next/link";
import { useEffect, useMemo, useState, type FormEvent } from "react";

import { LumenApiError, type LumenApiClient } from "@/lib/api/client-interface";
import { apiErrorMessage, resolveLumenClient } from "@/lib/api/client-runtime";
import type { DiagnosticSuggestion, HumanReviewResponse, IncidentDetail as IncidentDetailData } from "@/lib/api/types";
import { formatMetricValue } from "@/lib/format/metric";
import styles from "./incidents.module.css";

export function IncidentDetail({ incidentId, api: suppliedApi }: { incidentId: string; api?: LumenApiClient }) {
  return <IncidentDetailView key={incidentId} incidentId={incidentId} suppliedApi={suppliedApi} />;
}

function IncidentDetailView({ incidentId, suppliedApi }: { incidentId: string; suppliedApi?: LumenApiClient }) {
  const client = useMemo(() => resolveLumenClient(suppliedApi), [suppliedApi]);
  const [detail, setDetail] = useState<IncidentDetailData | null>(null);
  const [error, setError] = useState<string | null>(client.error);
  const [suggestion, setSuggestion] = useState<DiagnosticSuggestion | null>(null);
  const [suggestionError, setSuggestionError] = useState<string | null>(null);
  const [reload, setReload] = useState(0);

  useEffect(() => {
    if (!client.api) return;
    const controller = new AbortController();
    void client.api.getIncident(incidentId, { signal: controller.signal })
      .then(setDetail)
      .catch((reason: unknown) => {
        if (reason instanceof LumenApiError && reason.code === "CANCELLED") return;
        setError(apiErrorMessage(reason, "The incident could not be loaded."));
      });
    return () => controller.abort("incident changed");
  }, [client, incidentId, reload]);

  useEffect(() => {
    if (!client.api) return;
    const controller = new AbortController();
    void client.api.getDiagnosticSuggestion(incidentId, { signal: controller.signal })
      .then(setSuggestion)
      .catch((reason: unknown) => {
        if (reason instanceof LumenApiError && reason.code === "CANCELLED") return;
        setSuggestion(null);
        setSuggestionError(reason instanceof LumenApiError && reason.code === "NOT_FOUND"
          ? "No agent hypothesis has been published for this incident."
          : apiErrorMessage(reason, "The agent hypothesis is unavailable. The engine diagnosis remains available."));
      });
    return () => controller.abort("incident changed");
  }, [client, incidentId, reload]);

  if (error) return <main className={styles.shell}><section className={`${styles.card} ${styles.alert}`} role="alert"><strong>Could not load incident</strong><p>{error}</p><button className={styles.button} type="button" onClick={() => {
    if (!client.api) { setError(client.error); return; }
    setError(null); setDetail(null); setReload((value) => value + 1);
  }}>Try again</button></section></main>;
  if (!detail) return <main className={styles.shell}><section className={styles.card} role="status">Loading incident…</section></main>;

  const { incident, memory, explanation } = detail;
  const inconclusive = incident.root_cause.status === "INCONCLUSIVE";
  const diagnosticLogs = incident.evidence.filter((evidence) => evidence.kind !== "PAST_INCIDENT");
  return <main className={styles.shell}>
    <div className={styles.top}><div><Link className={styles.back} href="/incidents" aria-label="Back to incidents"><BackIcon /></Link><p className={styles.label}>Full operational diagnosis</p><h1>{incident.title}</h1><p className={styles.muted}>Incident ID: <code>{incident.incident_id}</code></p></div><span className={styles.offline}>{client.source === "MOCK_FIXTURE" ? "Explicit test fixture" : "Live Lumen API"}</span></div>

    <section className={`${styles.card} ${styles.executiveCard}`} aria-labelledby="executive-summary-title">
      <div className={styles.cardTop}><span className={styles.state}>{incident.state}</span><span className={inconclusive ? styles.causeInconclusive : styles.causeSupported}>{incident.root_cause.status}</span></div>
      <h2 id="executive-summary-title">Executive summary</h2><p className={styles.lead}>{explanation.executive_summary}</p>
      <div className={styles.meta}><Field label="Detected" value={formatDate(incident.detected_at)} /><Field label="First occurrence" value={incident.recurrence_first_detected_at ? formatDate(incident.recurrence_first_detected_at) : "Not available"} /><Field label="Estimated start" value={formatDate(incident.estimated_started_at)} /><Field label="Correlation ID" value={incident.correlation_id} /><Field label="Model" value={explanation.model_version} /></div>
    </section>

    <section className={styles.twoColumn}>
      <article className={`${styles.card} ${styles.current}`}><p className={styles.label}>Deterministic engine</p><h2>Engine cause</h2><div className={styles.meta}><Field label="Cause status" value={incident.root_cause.status} /><Field label="Category" value={incident.root_cause.category ?? "Not isolated"} /><Field label="Confidence" value={`${Math.round(incident.root_cause.confidence * 100)}%`} /></div>
        {inconclusive ? <p className={styles.warning}><strong>Current cause remains INCONCLUSIVE.</strong> Historical similarity can guide investigation, but it does not confirm this cause.</p> : null}
        <h3>What happened</h3><p>{explanation.what_happened}</p><h3>Where and why</h3><p>{explanation.where_and_why}</p>
        <h3>Confidence factors</h3><div className={styles.factorList}>{Object.entries(incident.root_cause.confidence_factors).map(([name, value]) => <div className={styles.factor} key={name}><span>{humanize(name)}</span><progress aria-label={`${humanize(name)} confidence factor`} max={1} value={value} /><strong>{Math.round(value * 100)}%</strong></div>)}</div>
        {incident.root_cause.alternatives?.length ? <><h3>Alternative hypotheses</h3><ul className={styles.inlineIds}>{incident.root_cause.alternatives.map((alternative) => <li key={`${alternative.category}-${alternative.confidence}`}>{humanize(alternative.category)} · {Math.round(alternative.confidence * 100)}%</li>)}</ul></> : null}
      </article>

      <article className={`${styles.card} ${styles.impactCard}`}><p className={styles.label}>Business exposure</p><h2>{formatMoney(incident.impact.amount_minor, incident.impact.currency)}</h2><p className={styles.muted}>GMV at risk · {humanize(incident.impact.method)}</p><div className={styles.meta}><Field label="Lower bound" value={formatOptionalMoney(incident.impact.lower_bound_minor, incident.impact.currency)} /><Field label="Upper bound" value={formatOptionalMoney(incident.impact.upper_bound_minor, incident.impact.currency)} /></div>
        <h3>Operational summary</h3><p>{explanation.operations_summary}</p>
        <h3>Scope</h3><div className={styles.tagGroups}>{Object.entries(incident.scope).map(([dimension, values]) => <div key={dimension}><span className={styles.label}>{humanize(dimension)}</span><div className={styles.tags}>{values.map((value) => <span key={value}>{value}</span>)}</div></div>)}</div>
        <h3>Metrics returned</h3><dl className={styles.metrics}>{Object.entries(incident.metrics).map(([name, value]) => <div key={name}><dt>{humanize(name)}</dt><dd>{formatMetricValue(value)}</dd></div>)}</dl>
      </article>
    </section>

    <AgentHypothesis suggestion={suggestion} error={suggestionError} loading={!suggestion && !suggestionError} onRetry={() => { setSuggestion(null); setSuggestionError(null); setReload((value) => value + 1); }} />

    <section className={`${styles.card} ${styles.actionCard}`}><div><p className={styles.label}>Human decision</p><h2>Human recommendation</h2></div><span className={styles.humanOnly}>HUMAN_ONLY</span><p className={styles.actionText}>{explanation.recommended_action}</p><div className={styles.meta}><Field label="Explanation playbook" value={explanation.playbook_id} /><Field label="Execution" value={explanation.execution} /></div><div className={styles.actionList}>{incident.recommendations.map((item) => <article key={`${item.playbook_id}-${item.action}`}><strong>{item.playbook_id}</strong><p>{item.action}</p><small>{item.recommendation_class ? `${humanize(item.recommendation_class)} · ` : ""}{item.execution} · Rationale: {item.rationale_evidence_ids.join(", ") || "Not provided"}</small></article>)}</div></section>

    <HumanReviewPanel incident={incident} defaultPlaybookId={explanation.playbook_id} api={client.api} source={client.source} />

    <section className={`${styles.card} ${styles.diagnosticLogs}`} aria-labelledby="diagnostic-logs-title"><p className={styles.label}>Diagnosis audit trail</p><h2 id="diagnostic-logs-title">Logs used to calculate this diagnosis</h2><p className={styles.muted}>These current signals were used by the deterministic engine to determine whether this is an incident or whether the cause remains inconclusive. Historical incidents are shown separately as context and do not determine the current cause.</p>
      {diagnosticLogs.length ? <div className={styles.evidenceGrid}>{diagnosticLogs.map((evidence) => <article className={styles.evidenceItem} key={evidence.evidence_id}><div><span className={styles.evidenceKind}>{evidence.kind}</span><code>{evidence.evidence_id}</code></div><p>{evidence.statement}</p><small>Log source: {evidence.source_ref}</small></article>)}</div> : <p className={styles.warning} role="status">No current calculation logs were returned for this diagnosis.</p>}
    </section>

    <section className={styles.card}><p className={styles.label}>Complete evidence record</p><h2>Evidence</h2><div className={styles.evidenceGrid}>{incident.evidence.map((evidence) => <article className={styles.evidenceItem} key={evidence.evidence_id}><div><span className={styles.evidenceKind}>{evidence.kind}</span><code>{evidence.evidence_id}</code></div><p>{evidence.statement}</p><small>Source: {evidence.source_ref}</small></article>)}</div></section>

    <section className={`${styles.card} ${styles.memory}`}><p className={styles.label}>Historical context only</p><h2>Precedent · {memory.memory_status}</h2>
      {memory.memory_status === "MATCH_FOUND" ? <><p><strong>Historical match found.</strong> It is contextual evidence, not proof of the current cause.</p><div className={styles.matchList}>{memory.matches.map((match) => <article className={styles.match} key={match.incident_id}><h3>{match.incident_id}</h3><div className={styles.meta}><Field label="Occurred at" value={formatDate(match.occurred_at)} /><Field label="Confirmation" value={match.confirmation} /><Field label="Confirmed cause" value={match.confirmed_cause} /><Field label="Structured score" value={`${Math.round(match.structured_score * 100)}%`} /><Field label="Semantic score" value={match.semantic_score === null || match.semantic_score === undefined ? "Not available" : `${Math.round(match.semantic_score * 100)}%`} /><Field label="Prior playbook" value={match.prior_playbook_id} /></div><p><strong>Matching:</strong> {match.matching_factors.join(", ") || "None"}</p><p><strong>Different:</strong> {match.different_factors.join(", ") || "None"}</p><p><strong>Evidence:</strong> {match.evidence_ids.join(", ") || "None"}</p></article>)}</div></> : null}
      {memory.memory_status === "NO_PRECEDENT" ? <p role="status"><strong>NO_PRECEDENT.</strong> No historical match was found. This is not a memory outage.</p> : null}
      {memory.memory_status === "MEMORY_UNAVAILABLE" ? <p className={styles.warning} role="status"><strong>MEMORY_UNAVAILABLE.</strong> Historical retrieval is unavailable; this is different from NO_PRECEDENT.</p> : null}
      <details className={styles.trace}><summary>Memory retrieval trace</summary><div className={styles.meta}><Field label="Query incident" value={memory.query_incident_id} /><Field label="Correlation ID" value={memory.correlation_id} /><Field label="Filter" value={memory.retrieval_trace.cypher_filter} /><Field label="Candidates" value={String(memory.retrieval_trace.candidate_count)} /><Field label="Embedding model" value={memory.retrieval_trace.embedding_model ?? "Not used"} /><Field label="Index version" value={memory.retrieval_trace.index_version} /><Field label="Fallback" value={memory.retrieval_trace.fallback_used ? "Used" : "Not used"} /></div></details>
    </section>

    <section className={styles.card}><p className={styles.label}>Scope and interpretation limits</p><h2>Operational notes</h2><p>{explanation.recurrence_statement ?? "No recurrence statement was returned."}</p><h3>Evidence IDs used by the operational explanation</h3><EvidenceIds ids={explanation.evidence_ids} /><h3>Limitations</h3><ul className={styles.limitations}>{[...new Set([...incident.limitations, ...explanation.limitations])].map((item) => <li key={item}>{item}</li>)}</ul></section>
  </main>;
}

function AgentHypothesis({ suggestion, error, loading, onRetry }: { suggestion: DiagnosticSuggestion | null; error: string | null; loading: boolean; onRetry: () => void }) {
  return <section className={`${styles.card} ${styles.agentCard}`} aria-labelledby="agent-hypothesis-title"><div className={styles.cardTop}><div><p className={styles.label}>Read-only agent</p><h2 id="agent-hypothesis-title">Agent hypothesis</h2></div><span className={styles.agentBadge}>{suggestion?.status ?? (loading ? "LOADING" : "NOT PUBLISHED")}</span></div>
    {loading ? <p role="status">Loading the separately published agent hypothesis…</p> : null}
    {error ? <div className={styles.agentNotice} role="status"><p>{error}</p><button className={styles.button} type="button" onClick={onRetry}>Retry hypothesis</button></div> : null}
    {suggestion ? <><div className={styles.meta}><Field label="Suggested category" value={suggestion.suggested_category ?? "No category suggested"} /><Field label="Confidence" value={`${Math.round(suggestion.confidence * 100)}%`} /><Field label="Model" value={suggestion.model_version} /></div><p className={styles.agentSummary}>{suggestion.summary_for_operations}</p>
      {suggestion.status === "SUGGESTED" ? <><h3>Reasons cited by the agent</h3><div className={styles.agentReasons}>{suggestion.reasons.map((reason) => <article key={`${reason.statement}-${reason.evidence_ids.join("-")}`}><p>{reason.statement}</p><EvidenceIds ids={reason.evidence_ids} /></article>)}</div><h3>Agent-proposed investigation steps</h3><div className={styles.actionList}>{suggestion.recommended_actions.map((action) => <article key={`${action.action}-${action.rationale_evidence_ids.join("-")}`}><p>{action.action}</p><small>{action.execution} · Rationale: {action.rationale_evidence_ids.join(", ") || "Not provided"}</small></article>)}</div></> : <p className={styles.warning}><strong>{suggestion.status}.</strong> The agent did not publish a causal hypothesis; use the engine cause and current evidence for the investigation.</p>}
      {suggestion.limitations.length ? <><h3>Agent limitations</h3><ul className={styles.limitations}>{suggestion.limitations.map((item) => <li key={item}>{item}</li>)}</ul></> : null}</> : null}
  </section>;
}

function HumanReviewPanel({ incident, defaultPlaybookId, api, source }: { incident: IncidentDetailData["incident"]; defaultPlaybookId: string; api: LumenApiClient | null; source: string }) {
  const [decision, setDecision] = useState<"APPROVED" | "REJECTED">("APPROVED");
  const [reviewerId, setReviewerId] = useState("");
  const [reason, setReason] = useState("");
  const [cause, setCause] = useState(incident.root_cause.category ?? "");
  const [playbookId, setPlaybookId] = useState(defaultPlaybookId);
  const [reviewId, setReviewId] = useState<string | null>(null);
  const [result, setResult] = useState<HumanReviewResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!api) { setError("The live API is not configured for human review."); return; }
    setSubmitting(true); setError(null);
    try {
      // Keep the key stable after a timeout or a failed response, so retrying does
      // not create a second human decision.
      const stableReviewId = reviewId ?? `review-${crypto.randomUUID()}`;
      setReviewId(stableReviewId);
      const review = await api.submitHumanReview(incident.incident_id, {
        schema_version: "1.0", review_id: stableReviewId, reviewer_id: reviewerId.trim(), decision, reason: reason.trim(),
        ...(decision === "APPROVED" ? { confirmed_cause: cause.trim(), playbook_id: playbookId.trim() } : {}),
      });
      setResult(review);
    } catch (failure) {
      setError(apiErrorMessage(failure, "The human review could not be saved."));
    } finally { setSubmitting(false); }
  }

  return <section className={`${styles.card} ${styles.reviewCard}`} aria-labelledby="human-review-title"><div className={styles.cardTop}><div><p className={styles.label}>Human review</p><h2 id="human-review-title">Confirm or reject this cause</h2></div><span className={styles.humanOnly}>HUMAN_ONLY</span></div><p className={styles.muted}>Only an approval becomes a GraphRAG precedent. A rejection keeps the reviewer reason in the audit graph without influencing future matches.</p>
    {source === "MOCK_FIXTURE" ? <p className={styles.warning}>Fixture mode: this validates the interaction but does not write to Aura.</p> : null}
    {result ? <div className={styles.reviewResult} role="status"><strong>{result.review.decision === "APPROVED" ? "Approved and promoted to GraphRAG." : "Rejection recorded in the audit graph."}</strong><p>{result.review.reason}</p></div> : null}
    {error ? <p className={styles.alert} role="alert">{error}</p> : null}
    <form className={styles.reviewForm} onSubmit={submit}><label>Reviewer ID<input required value={reviewerId} onChange={(event) => setReviewerId(event.target.value)} /></label><label>Decision<select value={decision} onChange={(event) => { setDecision(event.target.value as "APPROVED" | "REJECTED"); setReviewId(null); }}><option value="APPROVED">Approve cause</option><option value="REJECTED">Reject cause</option></select></label>{decision === "APPROVED" ? <><label>Confirmed cause<input required value={cause} onChange={(event) => setCause(event.target.value)} /></label><label>Playbook<input required value={playbookId} onChange={(event) => setPlaybookId(event.target.value)} /></label></> : null}<label className={styles.reviewReason}>Reason<textarea required minLength={3} value={reason} onChange={(event) => setReason(event.target.value)} placeholder={decision === "APPROVED" ? "Why was this cause confirmed?" : "Why is this cause being rejected?"} /></label><button className={styles.button} type="submit" disabled={submitting}>{submitting ? "Saving review…" : decision === "APPROVED" ? "Approve and promote" : "Record rejection"}</button></form>
  </section>;
}

function Field({ label, value }: { label: string; value: string }) { return <div><p className={styles.label}>{label}</p><p className={styles.value}>{value}</p></div>; }
function EvidenceIds({ ids }: { ids: string[] }) { return ids.length ? <ul className={styles.inlineIds}>{ids.map((id) => <li key={id}><code>{id}</code></li>)}</ul> : <p>No evidence IDs were returned.</p>; }
function formatMoney(amountMinor: number, currency: string): string { return new Intl.NumberFormat("pt-BR", { style: "currency", currency }).format(amountMinor / 100); }
function formatOptionalMoney(amountMinor: number | null | undefined, currency: string): string { return amountMinor === null || amountMinor === undefined ? "Not provided" : formatMoney(amountMinor, currency); }
function formatDate(value: string): string { return new Intl.DateTimeFormat("pt-BR", { dateStyle: "medium", timeStyle: "short", timeZone: "UTC" }).format(new Date(value)); }
function humanize(value: string): string { return value.toLowerCase().replaceAll("_", " ").replace(/^./, (letter) => letter.toUpperCase()); }
function BackIcon() { return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="m15 18-6-6 6-6" /><path d="M9 12h10" /></svg>; }
