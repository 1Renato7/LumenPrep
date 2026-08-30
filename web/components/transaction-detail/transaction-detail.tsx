"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import { createPollingController, LumenApiError, pollTransaction, type LumenApiClient } from "@/lib/api/client-interface";
import { apiErrorMessage, resolveLumenClient } from "@/lib/api/client-runtime";
import type { TransactionIncidentDetail, TransactionRecord } from "@/lib/api/types";

import { isRejectedIncident, selectAuthorizedIncidentLink } from "./grounding";
import styles from "./transaction-detail.module.css";

export function TransactionDetail({ transactionId, api: suppliedApi }: { transactionId: string; api?: LumenApiClient }) {
  return <TransactionDetailView key={transactionId} transactionId={transactionId} suppliedApi={suppliedApi} />;
}

function TransactionDetailView({ transactionId, suppliedApi }: { transactionId: string; suppliedApi?: LumenApiClient }) {
  const router = useRouter();
  const client = useMemo(() => resolveLumenClient(suppliedApi), [suppliedApi]);
  const api = client.api;
  const [record, setRecord] = useState<TransactionRecord | null>(null);
  const [loading, setLoading] = useState(Boolean(client.api));
  const [error, setError] = useState<string | null>(client.error);
  const [reloadKey, setReloadKey] = useState(0);
  const [hasRecord, setHasRecord] = useState(false);
  const [grounding, setGrounding] = useState<TransactionIncidentDetail | null>(null);
  const [groundingError, setGroundingError] = useState<string | null>(null);

  const reload = useCallback(() => {
    setError(null);
    setGroundingError(null);
    setGrounding(null);
    setLoading(true);
    setReloadKey((value) => value + 1);
  }, []);
  const refresh = () => {
    reload();
    router.refresh();
  };

  useEffect(() => {
    if (!api) return;
    let active = true;
    const polling = createPollingController();
    void pollTransaction(api, transactionId, {
      signal: polling.signal,
      onUpdate: (next) => {
        if (!active) return;
        setRecord(next);
        setHasRecord(true);
        setError(null);
        setLoading(false);
      },
    }).catch((reason: unknown) => {
      if (!active || reason instanceof LumenApiError && reason.code === "CANCELLED") return;
      setError(apiErrorMessage(reason, "The transaction could not be loaded from the Lumen API."));
      setLoading(false);
    });
    return () => { active = false; polling.cancel("transaction detail changed"); };
  }, [api, reloadKey, transactionId]);

  const relatedIncidentIds = record?.classification?.related_incident_ids ?? [];
  useEffect(() => {
    if (!api || !record || record.status === "PROCESSING") return;
    let active = true;
    const controller = new AbortController();
    void api.listTransactionIncidents(transactionId, { signal: controller.signal })
      .then((next) => {
        if (active) setGrounding(next);
      })
      .catch((reason: unknown) => {
        if (!active || reason instanceof LumenApiError && reason.code === "CANCELLED") return;
        setGroundingError(apiErrorMessage(reason, "Grounded Incident detail is unavailable."));
      });
    return () => { active = false; controller.abort("transaction grounding changed"); };
  }, [api, record, transactionId]);

  if (loading && !record) return <main className={styles.shell}><section className={styles.card} role="status">Loading transaction detail…</section></main>;
  if (error && !record) return <main className={styles.shell}><section className={`${styles.card} ${styles.error}`} role="alert"><strong>Could not load transaction</strong><p>{error}</p><button className={styles.button} type="button" onClick={reload}>Retry</button></section></main>;
  if (!record) return null;

  const isPipelineFailure = record.processing.stage === "PIPELINE_FAILED";
  const classification = record.classification;
  const needsAttention = record.status === "FAILED" || record.status === "UNKNOWN";
  const groundedIncident = selectAuthorizedIncidentLink(grounding, relatedIncidentIds);
  const incidentActionLoading = relatedIncidentIds.length > 0 && !grounding && !groundingError;
  const rejectedIncidentIds = relatedIncidentIds.filter((id) => isRejectedIncident(grounding, id));

  return (
    <main className={styles.shell}>
      <div className={styles.top}>
        <div><Link className={styles.back} href="/transactions" aria-label="Back to transaction log"><BackIcon /></Link><div className={styles.titleRow}><h1>Transaction {record.transaction_id}</h1><span className={`${styles.status} ${record.status === "FAILED" ? styles.failedStatus : record.status === "UNKNOWN" ? styles.unknownStatus : styles.standardStatus}`}>{record.status}</span></div></div>
        <button className={styles.button} type="button" onClick={refresh}>Refresh data</button>
      </div>
      {error && hasRecord ? <section className={`${styles.card} ${styles.notice}`} role="status">Showing stale transaction data. Refresh failed: {error}</section> : null}
      {needsAttention ? <section className={`${styles.card} ${styles.diagnosticHero} ${isPipelineFailure ? styles.technicalHero : styles.failedHero}`} aria-labelledby="diagnostic-overview-title"><p className={styles.label}>{isPipelineFailure ? "Technical attention" : "Failure diagnosis"}</p><h2 id="diagnostic-overview-title">{isPipelineFailure ? "The processing pipeline did not produce a business outcome." : classification?.reason ?? "The backend returned a failed outcome without a diagnostic reason."}</h2><div className={styles.grid}><Value label="Category" value={classification?.category ?? "Not available"} /><Value label="Failure code" value={record.processing.failure_code ?? "None"} /><Value label="Normalized decline" value={record.outcome?.normalized_decline_code ?? "None"} /><Value label="Confidence" value={classification ? `${Math.round(classification.confidence * 100)}%` : "Not available"} /></div>{isPipelineFailure ? <div className={styles.actionPanel}><div><p className={styles.label}>Recommended next step</p><p className={styles.actionText}>Review the technical failure before retrying or changing payment routing.</p></div><Link className={styles.actionButton} href="/incidents#technical-attention">View technical attention <span aria-hidden="true">→</span></Link></div> : groundedIncident ? <div className={styles.actionPanel}><div><div className={styles.actionHeading}><p className={styles.label}>Recommended human action</p><span className={styles.actionMode}>{groundedIncident.explanation.execution.replaceAll("_", " ")}</span></div><p className={styles.actionText}>{groundedIncident.explanation.recommended_action}</p></div><Link className={styles.actionButton} href={`/incidents/${encodeURIComponent(groundedIncident.incident.incident_id)}`}>View incident analysis <span aria-hidden="true">→</span></Link></div> : relatedIncidentIds.length ? <div className={styles.actionPanel} role="status"><div><p className={styles.label}>Incident authorization</p><p className={styles.actionText}>{incidentActionLoading ? "Verifying the grounded incident…" : groundingError ?? (rejectedIncidentIds.length ? `The API rejected these Incident IDs for this transaction: ${rejectedIncidentIds.join(", ")}.` : "No Incident was authorized for this transaction.")}</p></div></div> : <div className={styles.actionPanel} role="status"><div><p className={styles.label}>Recommended human action</p><p className={styles.actionText}>No incident-level recommendation was returned for this isolated business failure.</p></div></div>}</section> : null}
      <section className={styles.card}><h2>Input</h2><div className={styles.grid}>
        <Value label="Merchant" value={record.input.merchant_id} /><Value label="Provider" value={record.input.provider_id} /><Value label="Issuer bank" value={record.input.issuer_bank} />
        <Value label="Amount" value={formatMoney(record.input.amount_minor, record.input.currency)} /><Value label="Country" value={record.input.country} /><Value label="Method" value={record.input.payment_method_category} />
        <Value label="Reference" value={record.input.client_reference ?? "Not provided"} /><Value label="Occurred at" value={record.input.occurred_at ?? "Not provided"} />
      </div></section>
      <section className={styles.card}><h2>Lifecycle</h2><div className={styles.grid}>
        <Value label="Public status" value={record.status} /><Value label="Stage" value={record.processing.stage} /><Value label="Progress" value={`${record.processing.progress_percent}%`} />
        <Value label="Pipeline failure code" value={record.processing.failure_code ?? "None"} />
      </div></section>
      <section className={`${styles.card} ${isPipelineFailure ? styles.pipeline : ""}`}><h2>Outcome</h2>
        {isPipelineFailure ? <p><strong>Technical pipeline failure.</strong> No business decline was received; this record is correctly classified as <strong>UNKNOWN</strong>.</p> : record.outcome ? <div className={styles.grid}>
          <Value label="Business result" value={record.outcome.result} /><Value label="Provider response" value={record.outcome.provider_response_code ?? "Not provided"} /><Value label="Normalized decline" value={record.outcome.normalized_decline_code ?? "None"} /><Value label="Latency" value={`${record.outcome.latency_ms} ms`} />
        </div> : <p className={styles.muted}>Outcome is not available while processing.</p>}
      </section>
      <section className={styles.card}><h2>Classification</h2>
        {classification ? <><div className={styles.grid}><Value label="Category" value={classification.category} /><Value label="Reason" value={classification.reason} /><Value label="Confidence" value={`${Math.round(classification.confidence * 100)}%`} /></div>
          <h3>Evidence IDs</h3><IdList ids={classification.evidence_ids} empty="No evidence IDs were returned." />
          <h3>Related incidents</h3>{classification.related_incident_ids.length ? <ul className={styles.list}>{classification.related_incident_ids.map((id) => { const authorized = grounding?.incidents.some((link) => link.incident.incident_id === id); return <li key={id}>{authorized ? <Link className={styles.incidentLink} href={`/incidents/${encodeURIComponent(id)}`}>{id}</Link> : <><code>{id}</code> <span>· {isRejectedIncident(grounding, id) ? "rejected by grounding" : "not authorized"}</span></>}</li>; })}</ul> : <p role="status">No related incident. This is a normal transaction state.</p>}</>
          : <p className={styles.muted}>Classification is not available while processing or after a technical pipeline failure.</p>}
      </section>
      {grounding && record.status !== "PROCESSING" ? <section className={styles.card} aria-live="polite"><h2>Grounded incident trace</h2><div className={styles.grid}><Value label="Status" value={grounding.status} /><Value label="Authorized incidents" value={String(grounding.incidents.length)} /><Value label="Rejected incident IDs" value={grounding.rejected_incident_ids.join(", ") || "None"} /></div>{grounding.limitations.length ? <><h3>Limitations</h3><IdList ids={grounding.limitations} empty="No limitations were returned." /></> : null}</section> : null}
    </main>
  );
}

function Value({ label, value }: { label: string; value: string }) { return <div><p className={styles.label}>{label}</p><p className={styles.value}>{value}</p></div>; }
function IdList({ ids, empty }: { ids: string[]; empty: string }) { return ids.length ? <ul className={styles.list}>{ids.map((id) => <li key={id}><code>{id}</code></li>)}</ul> : <p>{empty}</p>; }
function formatMoney(amountMinor: number, currency: string): string { return new Intl.NumberFormat("pt-BR", { style: "currency", currency }).format(amountMinor / 100); }
function BackIcon() { return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="m15 18-6-6 6-6" /><path d="M9 12h10" /></svg>; }
