"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import type { TransactionList, TransactionRecord } from "@/lib/api/types";

import {
  getOfflineTransactionList,
  hasProcessing,
  normalizeFilter,
  normalizeFixtureMode,
  transactionFilters,
  type OfflineFixtureError,
} from "./fixture-source";
import { startProcessingPolling } from "./polling";
import { buildTransactionUrl, firstSearchValue, type SearchValues } from "./url";
import styles from "./transaction-log.module.css";

export function TransactionLog({ searchValues }: { searchValues: SearchValues }) {
  const router = useRouter();
  const status = normalizeFilter(firstSearchValue(searchValues.status));
  const cursor = firstSearchValue(searchValues.cursor);
  const fixture = normalizeFixtureMode(firstSearchValue(searchValues.fixture));
  const [list, setList] = useState<TransactionList | null>(null);
  const [loading, setLoading] = useState(true);
  const [stale, setStale] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  const hasCachedList = useRef(false);

  const reload = useCallback(() => setReloadKey((value) => value + 1), []);

  useEffect(() => {
    let active = true;
    void getOfflineTransactionList({ status, cursor, fixture })
      .then((result) => {
        if (!active) return;
        setList(result.list);
        hasCachedList.current = true;
        setStale(result.stale);
        setError(null);
      })
      .catch((reason: OfflineFixtureError) => {
        if (!active) return;
        setError(reason.message);
        setStale(hasCachedList.current);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [cursor, fixture, reloadKey, status]);

  useEffect(() => {
    const polling = startProcessingPolling({
      hasProcessing: Boolean(list && !error && hasProcessing(list.items)),
      onPoll: reload,
    });
    return () => polling?.cancel();
  }, [error, list, reload]);

  const navigate = (nextStatus: typeof status, nextCursor: string | null) => {
    router.replace(buildTransactionUrl(searchValues, { status: nextStatus, cursor: nextCursor }));
  };

  return (
    <main className={styles.shell}>
      <div className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Transaction workspace</p>
          <h1>Transaction <span>logs</span></h1>
          <p className={styles.muted}>Newest records first. Status and progress come from the backend contract.</p>
        </div>
        <span className={styles.offline}>Offline fixtures</span>
      </div>

      <div className={styles.filters} aria-label="Transaction status filters">
        {transactionFilters.map((filter) => (
          <button
            className={styles.filter}
            key={filter}
            type="button"
            aria-pressed={status === filter}
            onClick={() => navigate(filter, null)}
          >
            {filter}
          </button>
        ))}
      </div>

      {stale ? (
        <section className={`${styles.card} ${styles.notice}`} aria-live="polite">
          <strong>Stale data</strong>
          <p className={styles.muted}>The last fixture response is still visible. Refresh to try again.</p>
          <button className={styles.button} type="button" onClick={reload}>Retry</button>
        </section>
      ) : null}

      {error && !list ? (
        <section className={`${styles.card} ${styles.error}`} role="alert">
          <strong>Could not load transactions</strong>
          <p>{error}</p>
          <button className={styles.button} type="button" onClick={reload}>Retry</button>
        </section>
      ) : null}

      {loading && !list ? <section className={styles.card} role="status">Loading transaction log…</section> : null}

      {list ? (
        <section className={styles.card} aria-label="Transaction results">
          {error ? <p className={styles.error} role="alert">Refresh failed: {error}</p> : null}
          {list.items.length === 0 ? (
            <p role="status">No transactions match this filter.</p>
          ) : (
            <div className={styles.tableWrap}>
              <table className={styles.table}>
                <thead>
                  <tr><th>Status</th><th>Transaction</th><th>Payment</th><th>Lifecycle</th><th>Diagnostic returned</th><th>Updated</th><th><span className={styles.visuallyHidden}>Actions</span></th></tr>
                </thead>
                <tbody>
                  {list.items.map((record) => (
                    <tr className={record.status === "FAILED" || record.status === "UNKNOWN" ? styles.attentionRow : undefined} key={record.transaction_id}>
                      <td><StatusBadge status={record.status} /></td>
                      <td><strong className={styles.primaryValue}>{record.transaction_id}</strong><span className={styles.secondaryValue}>{record.input.merchant_id}</span><span className={styles.secondaryValue}>{record.input.provider_id} · {record.input.issuer_bank}</span></td>
                      <td><strong className={styles.primaryValue}>{formatMoney(record.input.amount_minor, record.input.currency)}</strong><span className={styles.secondaryValue}>{record.input.payment_method_category}</span></td>
                      <td>
                        <div className={styles.progress}>
                          <span>{record.processing.stage}</span>
                          <progress aria-label={`${record.transaction_id} progress`} max={100} value={record.processing.progress_percent} />
                          <span>{record.processing.progress_percent}%</span>
                        </div>
                      </td>
                      <td><DiagnosticSummary record={record} /></td>
                      <td><time dateTime={record.updated_at}>{formatDate(record.updated_at)}</time></td>
                      <td><Link className={styles.rowLink} href={`/transactions/${encodeURIComponent(record.transaction_id)}`}>Open detail<span aria-hidden="true"> →</span></Link></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <div className={styles.pager}>
            <span className={styles.muted}>Cursor: {cursor ?? "first page"}</span>
            <button
              className={styles.button}
              type="button"
              disabled={!list.next_cursor}
              onClick={() => navigate(status, list.next_cursor)}
            >
              Next page
            </button>
          </div>
        </section>
      ) : null}
    </main>
  );
}

function DiagnosticSummary({ record }: { record: TransactionRecord }) {
  const classification = record.classification;
  const outcome = record.outcome;
  if (record.processing.stage === "PIPELINE_FAILED") {
    return <div className={`${styles.diagnostic} ${styles.technicalDiagnostic}`}><strong>Technical attention required</strong><span>Failure code: <code>{record.processing.failure_code ?? "Not provided"}</code></span><span>No business outcome or causal diagnosis was returned.</span><Link href="/incidents#technical-attention">View in Incidents</Link></div>;
  }
  if (!classification) {
    return <div className={styles.diagnostic}><strong>Analysis in progress</strong><span>Diagnosis becomes available after backend processing.</span></div>;
  }
  return <div className={`${styles.diagnostic} ${record.status === "FAILED" ? styles.failedDiagnostic : styles.successDiagnostic}`}>
    <strong>{classification.category}</strong>
    <span>{classification.reason}</span>
    <span>Confidence: {Math.round(classification.confidence * 100)}%{outcome?.normalized_decline_code ? ` · ${outcome.normalized_decline_code}` : ""}</span>
    <span>Evidence: {classification.evidence_ids.length ? classification.evidence_ids.join(", ") : "None returned"}</span>
    {classification.related_incident_ids.length ? <span>Incident: {classification.related_incident_ids.map((id) => <Link key={id} href={`/incidents/${encodeURIComponent(id)}`}>{id}</Link>)}</span> : <span>No related incident.</span>}
  </div>;
}

function StatusBadge({ status }: { status: "PROCESSING" | "SUCCEEDED" | "FAILED" | "UNKNOWN" }) {
  const className = status === "PROCESSING" ? styles.processing : status === "SUCCEEDED" ? styles.succeeded : status === "FAILED" ? styles.failed : styles.unknown;
  return <span className={`${styles.badge} ${className}`}>{status}</span>;
}

function formatMoney(amountMinor: number, currency: string): string {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency }).format(amountMinor / 100);
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("pt-BR", { dateStyle: "short", timeStyle: "medium", timeZone: "UTC" }).format(new Date(value));
}
