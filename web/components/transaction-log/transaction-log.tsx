"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { createPollingController, LumenApiError, pollTransactions, type LumenApiClient } from "@/lib/api/client-interface";
import { apiErrorMessage, resolveLumenClient } from "@/lib/api/client-runtime";
import type { TransactionList, TransactionRecord, TransactionStatus } from "@/lib/api/types";
import { formatBrasiliaDateTime } from "@/lib/format/date-time";

import { normalizeFilter, transactionFilters } from "./filters";
import { buildTransactionUrl, firstSearchValue, type SearchValues } from "./url";
import styles from "./transaction-log.module.css";

export function TransactionLog({ searchValues, api: suppliedApi }: { searchValues: SearchValues; api?: LumenApiClient }) {
  const router = useRouter();
  const client = useMemo(() => resolveLumenClient(suppliedApi), [suppliedApi]);
  const api = client.api;
  const status = normalizeFilter(firstSearchValue(searchValues.status));
  const cursor = firstSearchValue(searchValues.cursor);
  const batchId = firstSearchValue(searchValues.batch_id);
  const queryKey = JSON.stringify({ status, cursor, batchId });
  const [list, setList] = useState<TransactionList | null>(null);
  const [loading, setLoading] = useState(true);
  const [stale, setStale] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  const [resetOpen, setResetOpen] = useState(false);
  const [resetKey, setResetKey] = useState("");
  const [resetting, setResetting] = useState(false);
  const [resetMessage, setResetMessage] = useState<string | null>(null);
  const [resetError, setResetError] = useState<string | null>(null);
  const cache = useRef(new Map<string, TransactionList>());

  const reload = useCallback(() => setReloadKey((value) => value + 1), []);

  useEffect(() => {
    const cached = cache.current.get(queryKey) ?? null;
    setList(cached);
    setLoading(!cached);
    setStale(false);
    setError(client.error);
    if (!api) return;

    let active = true;
    const polling = createPollingController();
    const apply = (next: TransactionList) => {
      if (!active) return;
      const visible = batchId && status !== "ALL" ? filterList(next, status) : next;
      cache.current.set(queryKey, visible);
      setList(visible);
      setLoading(false);
      setStale(false);
      setError(null);
    };
    void pollTransactions(api, {
      batchId,
      query: batchId ? undefined : { status: status === "ALL" ? undefined : status, cursor },
      signal: polling.signal,
      onUpdate: apply,
    }).catch((reason: unknown) => {
      if (!active || reason instanceof LumenApiError && reason.code === "CANCELLED") return;
      setError(apiErrorMessage(reason, "The transaction log could not reach the Lumen API."));
      setStale(cache.current.has(queryKey));
      setLoading(false);
    });

    return () => {
      active = false;
      polling.cancel("transaction query changed");
    };
  }, [api, batchId, client.error, cursor, queryKey, reloadKey, status]);

  const navigate = (nextStatus: typeof status, nextCursor: string | null) => {
    router.replace(buildTransactionUrl(searchValues, { status: nextStatus, cursor: nextCursor }));
  };

  const resetTransactionData = async () => {
    if (!api) return;
    setResetting(true);
    setResetError(null);
    try {
      const result = await api.resetTransactionData(resetKey);
      cache.current.clear();
      setResetKey("");
      setResetOpen(false);
      setResetMessage(`${result.removed.transaction_records} transaction(s) and their derived data were removed.`);
      setList({ schema_version: "1.0", items: [], next_cursor: null, correlation_id: result.correlation_id });
      setError(null);
      setStale(false);
      setLoading(false);
      router.replace(buildTransactionUrl(searchValues, { status: "ALL", cursor: null, batchId: null }));
    } catch (reason) {
      setResetError(apiErrorMessage(reason, "The transaction data could not be cleared."));
    } finally {
      setResetting(false);
    }
  };

  return (
    <main className={styles.shell}>
      <div className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Transaction workspace</p>
          <h1>Transaction <span>logs</span></h1>
          <p className={styles.muted}>Newest records first. Status and progress come from the backend contract.</p>
        </div>
        <span className={styles.offline}>{client.source === "MOCK_FIXTURE" ? "Explicit mock data" : "Live Lumen API"}</span>
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

      {client.source === "LIVE_API" ? (
        <section className={`${styles.card} ${styles.resetCard}`} aria-labelledby="reset-title">
          <div>
            <strong id="reset-title">Demo data</strong>
            <p className={styles.muted}>Remove all saved synthetic transactions, events, and derived incidents. This cannot be undone.</p>
          </div>
          <button className={`${styles.button} ${styles.dangerButton}`} type="button" onClick={() => { setResetError(null); setResetOpen((open) => !open); }} disabled={!api || resetting}>
            Clear saved data
          </button>
          {resetOpen ? (
            <form className={styles.resetForm} onSubmit={(event) => { event.preventDefault(); void resetTransactionData(); }}>
              <label htmlFor="transaction-reset-key">Administrator reset key</label>
              <input id="transaction-reset-key" type="password" value={resetKey} onChange={(event) => setResetKey(event.target.value)} autoComplete="off" required />
              <p className={styles.muted}>The key is sent only for this request and is not saved by Lumen.</p>
              {resetError ? <p className={styles.error} role="alert">{resetError}</p> : null}
              <div className={styles.resetActions}>
                <button className={styles.button} type="button" onClick={() => { setResetOpen(false); setResetKey(""); setResetError(null); }} disabled={resetting}>Cancel</button>
                <button className={`${styles.button} ${styles.dangerButton}`} type="submit" disabled={resetting}>{resetting ? "Clearing data…" : "Confirm permanent deletion"}</button>
              </div>
            </form>
          ) : null}
          {resetMessage ? <p className={styles.notice} role="status">{resetMessage}</p> : null}
        </section>
      ) : null}

      {stale ? (
        <section className={`${styles.card} ${styles.notice}`} aria-live="polite">
          <strong>Stale data</strong>
          <p className={styles.muted}>The last successful response for this query is still visible. Retry the live API.</p>
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
                  <tr><th>Status</th><th>Transaction</th><th>Payment</th><th>Lifecycle</th><th>Diagnostic returned</th><th>Updated (Brasília)</th><th><span className={styles.visuallyHidden}>Actions</span></th></tr>
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
                      <td><time dateTime={record.updated_at}>{formatBrasiliaDateTime(record.updated_at)}</time></td>
                      <td><Link className={styles.rowLink} href={`/transactions/${encodeURIComponent(record.transaction_id)}`}>Open detail<span aria-hidden="true"> →</span></Link></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <div className={styles.pager}>
            <span className={styles.muted}>{batchId ? `Batch: ${batchId}` : `Cursor: ${cursor ?? "first page"}`}</span>
            <button
              className={styles.button}
              type="button"
              disabled={Boolean(batchId) || !list.next_cursor}
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

function filterList(list: TransactionList, status: TransactionStatus): TransactionList {
  return { ...list, items: list.items.filter((item) => item.status === status), next_cursor: null };
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
    {outcome?.normalized_decline_code ? <span>Normalized decline: {outcome.normalized_decline_code}</span> : null}
    <span>Evidence: {classification.evidence_ids.length ? classification.evidence_ids.join(", ") : "None returned"}</span>
    {classification.related_incident_ids.length ? <span>Incident: {classification.related_incident_ids.map((id, index) => { const related = classification.related_incidents?.find((item) => item.incident_id === id); return <span key={id}><Link href={`/incidents/${encodeURIComponent(id)}`}>{id}</Link>{related?.recurrence_first_detected_at ? <> · First occurrence: <time dateTime={related.recurrence_first_detected_at}>{formatBrasiliaDateTime(related.recurrence_first_detected_at)}</time></> : null}{index < classification.related_incident_ids.length - 1 ? "; " : ""}</span>; })}</span> : <span>No related incident.</span>}
  </div>;
}

function StatusBadge({ status }: { status: "PROCESSING" | "SUCCEEDED" | "FAILED" | "UNKNOWN" }) {
  const className = status === "PROCESSING" ? styles.processing : status === "SUCCEEDED" ? styles.succeeded : status === "FAILED" ? styles.failed : styles.unknown;
  return <span className={`${styles.badge} ${className}`}>{status}</span>;
}

function formatMoney(amountMinor: number, currency: string): string {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency }).format(amountMinor / 100);
}
