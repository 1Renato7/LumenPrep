"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { LumenApiError, type LumenApiClient } from "@/lib/api/client-interface";
import { apiErrorMessage, resolveLumenClient } from "@/lib/api/client-runtime";
import type { Incident, TransactionRecord } from "@/lib/api/types";
import { formatBrasiliaDateTime } from "@/lib/format/date-time";
import { sortByMostRecent } from "@/lib/format/sort-by-date";
import styles from "./incidents.module.css";

export function IncidentList({ api: suppliedApi }: { api?: LumenApiClient } = {}) {
  const client = useMemo(() => resolveLumenClient(suppliedApi), [suppliedApi]);
  const [incidents, setIncidents] = useState<Incident[] | null>(null);
  const [technicalAttention, setTechnicalAttention] = useState<TransactionRecord[] | null>(null);
  const [incidentError, setIncidentError] = useState<string | null>(client.error);
  const [attentionError, setAttentionError] = useState<string | null>(client.error);
  const [incidentReload, setIncidentReload] = useState(0);
  const [attentionReload, setAttentionReload] = useState(0);

  useEffect(() => {
    if (!client.api) return;
    const controller = new AbortController();
    void client.api.listIncidents({ signal: controller.signal })
      .then((result) => setIncidents(sortByMostRecent(result, (incident) => incident.detected_at)))
      .catch((reason: unknown) => {
        if (reason instanceof LumenApiError && reason.code === "CANCELLED") return;
        setIncidentError(apiErrorMessage(reason, "Detected incidents could not be loaded."));
      });
    return () => controller.abort("incident query changed");
  }, [client, incidentReload]);

  useEffect(() => {
    if (!client.api) return;
    const controller = new AbortController();
    void client.api.listTransactions({ status: "UNKNOWN" }, { signal: controller.signal })
      .then((result) => setTechnicalAttention(sortByMostRecent(result.items, (record) => record.updated_at)))
      .catch((reason: unknown) => {
        if (reason instanceof LumenApiError && reason.code === "CANCELLED") return;
        setAttentionError(apiErrorMessage(reason, "Technical-attention transactions could not be loaded."));
      });
    return () => controller.abort("technical-attention query changed");
  }, [attentionReload, client]);

  const sourceLabel = client.source === "MOCK_FIXTURE" ? "Explicit test fixture" : "Live Lumen API";

  return <main className={styles.shell}>
    <div className={styles.top}><div><p className={styles.label}>Diagnostic aggregation</p><h1>Incidents</h1><p className={styles.muted}>Current diagnosis and historical memory are intentionally separate.</p></div><span className={styles.offline}>{sourceLabel}</span></div>
    <section className={styles.sectionBlock} aria-labelledby="confirmed-incidents-title">
      <div className={styles.sectionHeading}><div><p className={styles.label}>Backend-derived</p><h2 id="confirmed-incidents-title">Detected incidents</h2></div><span className={styles.count}>{incidents?.length ?? 0}</span></div>
      {incidentError ? <ErrorCard message={incidentError} onRetry={() => {
        if (!client.api) { setIncidentError(client.error); return; }
        setIncidentError(null); setIncidentReload((value) => value + 1);
      }} /> : null}
      {!incidents && !incidentError ? <section className={styles.card} role="status">Loading incidents…</section> : null}
      {incidents?.length === 0 && !incidentError ? <section className={styles.card} role="status">No detected incidents were returned by the API.</section> : null}
      {incidents?.length ? <div className={styles.grid} aria-label="Incident list, most recent first">{incidents.map((incident) => <article className={`${styles.card} ${styles.incidentCard}`} key={incident.incident_id}><div className={styles.cardTop}><span className={styles.state}>{incident.state}</span><span className={styles.confidence}>{Math.round(incident.root_cause.confidence * 100)}% confidence</span></div><h3>{incident.title}</h3><p>Detected: <time dateTime={incident.detected_at}>{formatBrasiliaDateTime(incident.detected_at)}</time></p><p>Current cause: <strong>{incident.root_cause.category ?? incident.root_cause.status}</strong></p>{incident.recurrence_first_detected_at ? <p className={styles.muted}><strong>First occurrence:</strong> <time dateTime={incident.recurrence_first_detected_at}>{formatDate(incident.recurrence_first_detected_at)}</time></p> : null}{conversionSummary(incident) ? <p className={styles.warning}><strong>Payment conversion:</strong> {conversionSummary(incident)}</p> : null}<div className={styles.incidentMeta}><span>{formatMoney(incident.impact.amount_minor, incident.impact.currency)} at risk</span><span>{incident.evidence.length} evidence items</span><span>{incident.recommendations.length} human action</span></div><Link className={styles.link} href={`/incidents/${encodeURIComponent(incident.incident_id)}`}>Open full diagnosis <span aria-hidden="true">→</span></Link></article>)}</div> : null}
    </section>

    <section className={styles.sectionBlock} id="technical-attention" aria-labelledby="technical-attention-title">
      <div className={styles.sectionHeading}><div><p className={styles.label}>Operational triage</p><h2 id="technical-attention-title">Technical attention</h2><p className={styles.muted}>UNKNOWN transactions are handled here, but remain distinct from a causal Incident until the backend correlates one.</p></div><span className={`${styles.count} ${styles.attentionCount}`}>{technicalAttention?.length ?? 0}</span></div>
      {attentionError ? <ErrorCard message={attentionError} onRetry={() => {
        if (!client.api) { setAttentionError(client.error); return; }
        setAttentionError(null); setAttentionReload((value) => value + 1);
      }} /> : null}
      {!technicalAttention && !attentionError ? <section className={styles.card} role="status">Loading technical-attention transactions…</section> : null}
      {technicalAttention?.length === 0 && !attentionError ? <section className={styles.card} role="status">No UNKNOWN transactions currently require technical attention.</section> : null}
      {technicalAttention?.length ? <div className={styles.attentionList}>{technicalAttention.map((record) => <article className={`${styles.card} ${styles.attentionCard}`} key={record.transaction_id}><span className={styles.attentionState}>UNKNOWN</span><div><h3>{record.transaction_id}</h3><p><strong>{record.processing.stage}</strong> · <code>{record.processing.failure_code ?? "No failure code"}</code></p><p>Updated: <time dateTime={record.updated_at}>{formatBrasiliaDateTime(record.updated_at)}</time></p><p className={styles.muted}>No business outcome or causal diagnosis was returned. Open the transaction to inspect lifecycle data.</p></div><Link className={styles.link} href={`/transactions/${encodeURIComponent(record.transaction_id)}`}>Inspect transaction <span aria-hidden="true">→</span></Link></article>)}</div> : null}
    </section>
  </main>;
}

function ErrorCard({ message, onRetry }: { message: string; onRetry: () => void }) {
  return <section className={`${styles.card} ${styles.alert}`} role="alert"><p>{message}</p><button className={styles.button} type="button" onClick={onRetry}>Try again</button></section>;
}

function formatMoney(amountMinor: number, currency: string): string { return new Intl.NumberFormat("pt-BR", { style: "currency", currency }).format(amountMinor / 100); }
function formatDate(value: string): string { return new Intl.DateTimeFormat("pt-BR", { dateStyle: "medium", timeStyle: "short", timeZone: "America/Sao_Paulo" }).format(new Date(value)); }
function conversionSummary(incident: Incident): string | null {
  const observed = incident.metrics.payment_conversion_observed;
  const expected = incident.metrics.payment_conversion_expected;
  const sample = incident.metrics.unique_payments;
  if (typeof observed !== "number" || typeof expected !== "number" || typeof sample !== "number") return null;
  return `${Math.round(observed * 100)}% observed vs ${Math.round(expected * 100)}% baseline · ${sample} unique payments`;
}
