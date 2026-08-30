"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { LumenApiError, type LumenApiClient } from "../../lib/api/client-interface";
import { resolveLumenClient } from "../../lib/api/client-runtime";
import type { TransactionCatalog } from "../../lib/api/types";
import {
  addTransactionRow,
  catalogOptions,
  createInitialFormState,
  duplicateTransactionRow,
  issuesFromApiError,
  removeTransactionRow,
  replaceRowsWithSamples,
  submitTransactionBatch,
  type FieldIssue,
  type TransactionField,
  type TransactionFormRow,
  updateTransactionField,
  validateTransactionRows,
} from "./form-state";
import styles from "./transaction-form.module.css";

export interface TransactionFormProps { api?: LumenApiClient; }

export function TransactionForm({ api: suppliedApi }: TransactionFormProps) {
  const router = useRouter();
  const client = useMemo(() => resolveLumenClient(suppliedApi), [suppliedApi]);
  const api = client.api;
  const [catalog, setCatalog] = useState<TransactionCatalog | null>(null);
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [form, setForm] = useState(createInitialFormState);
  const [issues, setIssues] = useState<FieldIssue[]>([]);
  const [sampleCount, setSampleCount] = useState("1");
  const [sampleError, setSampleError] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [idempotencyKey, setIdempotencyKey] = useState(() => createIdempotencyKey());

  useEffect(() => {
    if (!api) return;
    let active = true;
    api.getTransactionCatalog().then(
      (nextCatalog) => { if (active) { setCatalog(nextCatalog); setCatalogError(null); } },
      (error: unknown) => { if (active) { setCatalog(null); setCatalogError(errorMessage(error, "The transaction catalog is unavailable.")); } },
    );
    return () => { active = false; };
  }, [api]);

  const retryCatalog = async () => {
    if (!api) return;
    setCatalogError(null);
    try { setCatalog(await api.getTransactionCatalog()); }
    catch (error) { setCatalogError(errorMessage(error, "The transaction catalog is unavailable.")); }
  };
  const resetIdempotency = () => setIdempotencyKey(createIdempotencyKey());
  const changeField = (rowId: string, field: TransactionField, value: string) => {
    setForm((current) => updateTransactionField(current, rowId, field, value));
    setIssues((current) => current.filter((issue) => !(issue.field === field && form.rows[issue.rowIndex]?.id === rowId)));
    resetIdempotency();
  };
  const addRow = () => { setForm((current) => addTransactionRow(current)); setIssues([]); resetIdempotency(); };
  const duplicateRow = (rowId: string) => { setForm((current) => duplicateTransactionRow(current, rowId)); setIssues([]); resetIdempotency(); };
  const removeRow = (rowId: string) => { setForm((current) => removeTransactionRow(current, rowId)); setIssues([]); resetIdempotency(); };

  const generateSamples = async () => {
    if (!api) return;
    const count = Number(sampleCount);
    if (!Number.isInteger(count) || count < 1 || count > 100) { setSampleError("Sample quantity must be a whole number between 1 and 100."); return; }
    setSampleError(null); setIsGenerating(true);
    try { const response = await api.generateTransactionSamples({ schema_version: "1.0", count }); setForm((current) => replaceRowsWithSamples(current, response)); setIssues([]); resetIdempotency(); }
    catch (error) { setSampleError(errorMessage(error, "Sample transactions could not be generated.")); }
    finally { setIsGenerating(false); }
  };

  const submitBatch = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!catalog || !api) return;
    const nextIssues = validateTransactionRows(form.rows, catalog);
    if (nextIssues.length > 0) { setIssues(nextIssues); setSubmitError("Review the highlighted transaction fields before submitting."); return; }
    setIssues([]); setSubmitError(null); setIsSubmitting(true);
    try { const accepted = await submitTransactionBatch(api, form.rows, idempotencyKey); router.push(`/transactions?batch_id=${encodeURIComponent(accepted.batch_id)}`); }
    catch (error) {
      if (error instanceof LumenApiError && error.status === 422) {
        const apiIssues = issuesFromApiError(error.body);
        setIssues(apiIssues);
        setSubmitError(apiIssues.length > 0 ? "The batch was rejected. Review the transaction and field shown below." : "The batch was rejected. Your entries are still available to edit.");
      } else setSubmitError(errorMessage(error, "The batch could not be submitted. Your entries are still available to edit."));
    } finally { setIsSubmitting(false); }
  };

  if (!catalog || !api) return <FormState error={client.error ?? catalogError} onRetry={retryCatalog} />;

  const options = catalogOptions(catalog);
  const maximumRows = Math.min(catalog.max_batch_size, 100);
  return (
    <main className={styles.shell}>
      <div className={styles.content}>
        <header className={styles.hero}>
          <div><p className={styles.eyebrow}>Synthetic transaction input</p><h1>Build <span>a</span> <strong>batch.</strong></h1><p className={styles.heroCopy}>Compose only transaction facts. The backend owns outcomes, progress and diagnosis after submission.</p></div>
          <aside className={styles.contractCard}><p>CTR-TXN-001</p><strong>1–100 transactions</strong><span>Inputs remain editable until the batch is queued.</span></aside>
        </header>

        <section className={styles.panel} aria-labelledby="sample-title">
          <div className={styles.panelHeader}><div><h2 className={styles.sectionTitle} id="sample-title">Generate samples</h2><p className={styles.sectionHint}>Create valid synthetic inputs, then adjust any value before submit.</p></div></div>
          <div className={styles.generatorGrid}>
            <TextInput id="sample-count" label="Quantity (1–100)" type="number" min="1" max="100" value={sampleCount} onChange={setSampleCount} />
            <button className={`${styles.button} ${styles.secondaryButton}`} type="button" onClick={() => void generateSamples()} disabled={isGenerating}>{isGenerating ? "Generating samples…" : "Generate samples"}</button>
          </div>
          {sampleError ? <p className={styles.errorPanel} role="alert">{sampleError}</p> : null}
        </section>

        <form className={styles.batchForm} onSubmit={(event) => void submitBatch(event)} noValidate>
          <div className={styles.batchHeader}><div><h2 className={styles.sectionTitle}>Transactions</h2><p className={styles.sectionHint}>All fields are synthetic and validated against the current catalog.</p></div><span className={styles.counter}>{form.rows.length} / {maximumRows}</span></div>
          {submitError ? <p className={styles.errorPanel} role="alert">{submitError}</p> : null}
          <div className={styles.rows}>{form.rows.map((row, rowIndex) => <TransactionRow key={row.id} row={row} rowIndex={rowIndex} options={options} issues={issues.filter((issue) => issue.rowIndex === rowIndex)} canRemove={form.rows.length > 1} canDuplicate={form.rows.length < maximumRows} onChange={changeField} onDuplicate={() => duplicateRow(row.id)} onRemove={() => removeRow(row.id)} />)}</div>
          <div className={styles.formActions}><button className={`${styles.button} ${styles.secondaryButton}`} type="button" onClick={addRow} disabled={form.rows.length >= maximumRows}>Add transaction</button><button className={`${styles.button} ${styles.primaryButton}`} type="submit" disabled={isSubmitting}>{isSubmitting ? "Submitting batch…" : "Submit batch"}</button></div>
        </form>
      </div>
    </main>
  );
}

function FormState({ error, onRetry }: { error: string | null; onRetry: () => Promise<void> }) {
  return <main className={styles.shell} aria-busy={error ? undefined : true}><div className={styles.content}><section className={`${styles.panel} ${styles.stateShell} ${styles.stateCard}`}>{error ? <><h1>Catalog unavailable</h1><p>{error}</p><button className={`${styles.button} ${styles.primaryButton}`} type="button" onClick={() => void onRetry()}>Retry catalog</button></> : <><span className={styles.spinner} aria-hidden="true" /><h1>Loading input</h1><p role="status">Loading the transaction catalog…</p></>}</section></div></main>;
}

interface TransactionRowProps { row: TransactionFormRow; rowIndex: number; options: ReturnType<typeof catalogOptions>; issues: FieldIssue[]; canRemove: boolean; canDuplicate: boolean; onChange(rowId: string, field: TransactionField, value: string): void; onDuplicate(): void; onRemove(): void; }
function TransactionRow({ row, rowIndex, options, issues, canRemove, canDuplicate, onChange, onDuplicate, onRemove }: TransactionRowProps) {
  const issueFor = (field: TransactionField) => issues.find((issue) => issue.field === field)?.message;
  return <fieldset className={styles.transactionCard}><legend>Transaction {rowIndex + 1}</legend><div className={styles.rowHeader}><span className={styles.rowNumber}>Transaction {rowIndex + 1}</span><div className={styles.rowActions}><button className={`${styles.button} ${styles.quietButton}`} type="button" onClick={onDuplicate} disabled={!canDuplicate}>Duplicate</button><button className={`${styles.button} ${styles.quietButton} ${styles.removeButton}`} type="button" onClick={onRemove} disabled={!canRemove}>Remove</button></div></div>{issues.filter((issue) => !issue.field).map((issue) => <p className={styles.errorPanel} key={issue.message} role="alert">{issue.message}</p>)}<div className={styles.fieldGrid}><FieldInput field="client_reference" label="Client reference (optional)" row={row} onChange={onChange} /><FieldInput field="occurred_at" label="Timestamp (optional, UTC ISO 8601)" row={row} onChange={onChange} /><SelectField field="merchant_id" label="Merchant" row={row} options={options.merchants} error={issueFor("merchant_id")} onChange={onChange} /><SelectField field="provider_id" label="Provider" row={row} options={options.providers} error={issueFor("provider_id")} onChange={onChange} /><SelectField field="issuer_bank" label="Issuer bank" row={row} options={options.issuer_banks} error={issueFor("issuer_bank")} onChange={onChange} /><SelectField field="country" label="Country" row={row} options={options.countries} error={issueFor("country")} onChange={onChange} /><SelectField field="currency" label="Currency" row={row} options={options.currencies} error={issueFor("currency")} onChange={onChange} /><FieldInput field="amount_minor" label="Amount (minor units)" row={row} type="number" min="1" error={issueFor("amount_minor")} onChange={onChange} /><SelectField field="payment_method_category" label="Payment method" row={row} options={options.payment_method_categories} error={issueFor("payment_method_category")} onChange={onChange} /><SelectField field="card_brand" label="Card brand (optional)" row={row} options={options.card_brands} error={issueFor("card_brand")} onChange={onChange} /><SelectField field="card_type" label="Card type (optional)" row={row} options={options.card_types} error={issueFor("card_type")} onChange={onChange} /><FieldInput field="provider_connection_id" label="Provider connection (optional)" row={row} onChange={onChange} /></div></fieldset>;
}

function TextInput({ id, label, value, onChange, ...props }: { id: string; label: string; value: string; onChange(value: string): void; type?: "text" | "number"; min?: string; max?: string }) { return <div className={styles.field}><label htmlFor={id}>{label}</label><input className={styles.input} id={id} value={value} onChange={(event) => onChange(event.target.value)} {...props} /></div>; }
function FieldInput({ field, label, row, type = "text", min, error, onChange }: { field: TransactionField; label: string; row: TransactionFormRow; type?: "text" | "number"; min?: string; error?: string; onChange(rowId: string, field: TransactionField, value: string): void }) { const id = `${row.id}-${field}`; return <div className={styles.field}><label htmlFor={id}>{label}</label><input className={styles.input} id={id} type={type} min={min} value={row.values[field]} aria-invalid={error ? true : undefined} aria-describedby={error ? `${id}-error` : undefined} onChange={(event) => onChange(row.id, field, event.target.value)} />{error ? <span className={styles.fieldError} id={`${id}-error`} role="alert">{error}</span> : null}</div>; }
function SelectField({ field, label, row, options, error, onChange }: { field: TransactionField; label: string; row: TransactionFormRow; options: string[]; error?: string; onChange(rowId: string, field: TransactionField, value: string): void }) { const id = `${row.id}-${field}`; return <div className={styles.field}><label htmlFor={id}>{label}</label><select className={styles.input} id={id} value={row.values[field]} aria-invalid={error ? true : undefined} aria-describedby={error ? `${id}-error` : undefined} onChange={(event) => onChange(row.id, field, event.target.value)}><option value="">Select an option</option>{options.map((option) => <option key={option} value={option}>{option}</option>)}</select>{error ? <span className={styles.fieldError} id={`${id}-error`} role="alert">{error}</span> : null}</div>; }
function createIdempotencyKey(): string { return typeof crypto !== "undefined" && typeof crypto.randomUUID === "function" ? crypto.randomUUID() : `transaction-batch-${Date.now()}-${Math.random().toString(36).slice(2)}`; }
function errorMessage(error: unknown, fallback: string): string { return error instanceof Error && error.message ? error.message : fallback; }
