"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import type { Incident } from "@/lib/api/types";
import { buildFixtureTransactionList } from "@/components/transaction-log/fixture-source";
import { listOfflineIncidents } from "./fixture-source";
import styles from "./incidents.module.css";

export function IncidentList() {
  const [incidents, setIncidents] = useState<Incident[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { void listOfflineIncidents().then(setIncidents).catch((reason: Error) => setError(reason.message)); }, []);

  const technicalAttention = buildFixtureTransactionList({ status: "UNKNOWN" }).items;

  return <main className={styles.shell}>
    <div className={styles.top}><div><p className={styles.label}>Diagnostic aggregation</p><h1>Incidents</h1><p className={styles.muted}>Current diagnosis and historical memory are intentionally separate.</p></div><span className={styles.offline}>Offline fixtures · live correlation pending LUM2-63</span></div>
    {error ? <section className={`${styles.card} ${styles.alert}`} role="alert">{error}</section> : null}
    <section className={styles.sectionBlock} aria-labelledby="confirmed-incidents-title">
      <div className={styles.sectionHeading}><div><p className={styles.label}>Backend-derived</p><h2 id="confirmed-incidents-title">Detected incidents</h2></div><span className={styles.count}>{incidents?.length ?? 0}</span></div>
      {!incidents ? <section className={styles.card} role="status">Loading incidents…</section> : <div className={styles.grid} aria-label="Incident list">{incidents.map((incident) => <article className={`${styles.card} ${styles.incidentCard}`} key={incident.incident_id}><div className={styles.cardTop}><span className={styles.state}>{incident.state}</span><span className={styles.confidence}>{Math.round(incident.root_cause.confidence * 100)}% confidence</span></div><h3>{incident.title}</h3><p>Current cause: <strong>{incident.root_cause.category ?? incident.root_cause.status}</strong></p><div className={styles.incidentMeta}><span>{formatMoney(incident.impact.amount_minor, incident.impact.currency)} at risk</span><span>{incident.evidence.length} evidence items</span><span>{incident.recommendations.length} human action</span></div><Link className={styles.link} href={`/incidents/${encodeURIComponent(incident.incident_id)}`}>Open full diagnosis <span aria-hidden="true">→</span></Link></article>)}</div>}
    </section>

    <section className={styles.sectionBlock} id="technical-attention" aria-labelledby="technical-attention-title">
      <div className={styles.sectionHeading}><div><p className={styles.label}>Operational triage</p><h2 id="technical-attention-title">Technical attention</h2><p className={styles.muted}>UNKNOWN transactions are handled here, but remain distinct from a causal Incident until the backend correlates one.</p></div><span className={`${styles.count} ${styles.attentionCount}`}>{technicalAttention.length}</span></div>
      <div className={styles.attentionList}>{technicalAttention.map((record) => <article className={`${styles.card} ${styles.attentionCard}`} key={record.transaction_id}><span className={styles.attentionState}>UNKNOWN</span><div><h3>{record.transaction_id}</h3><p><strong>{record.processing.stage}</strong> · <code>{record.processing.failure_code ?? "No failure code"}</code></p><p className={styles.muted}>No business outcome or causal diagnosis was returned. Open the transaction to inspect lifecycle data.</p></div><Link className={styles.link} href={`/transactions/${encodeURIComponent(record.transaction_id)}`}>Inspect transaction <span aria-hidden="true">→</span></Link></article>)}</div>
    </section>
  </main>;
}

function formatMoney(amountMinor: number, currency: string): string { return new Intl.NumberFormat("pt-BR", { style: "currency", currency }).format(amountMinor / 100); }
