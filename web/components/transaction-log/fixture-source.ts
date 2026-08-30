import type { TransactionList, TransactionRecord, TransactionStatus } from "@/lib/api/types";
import { hasProcessing, normalizeFilter, transactionFilters, type TransactionFilter } from "./filters";

export { hasProcessing, normalizeFilter, transactionFilters };
export type { TransactionFilter };

export type TransactionFixtureMode = "default" | "loading" | "empty" | "error" | "stale";

export interface OfflineTransactionQuery {
  status?: TransactionFilter;
  cursor?: string;
  fixture?: TransactionFixtureMode;
}

export class OfflineFixtureError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "OfflineFixtureError";
  }
}

/** Component-local snapshots of frozen transaction-list/processing/succeeded/failed fixtures. */
const processingRecord: TransactionRecord = {
  schema_version: "1.0", transaction_id: "txn_processing_1003", batch_id: "batch_demo_0001", created_at: "2026-08-29T18:00:02Z", updated_at: "2026-08-29T18:00:10Z", status: "PROCESSING",
  input: { client_reference: "checkout-1001", occurred_at: "2026-08-29T18:00:00Z", merchant_id: "merchant_br_01", provider_id: "provider_alpha", issuer_bank: "bank_br_a", country: "BR", currency: "BRL", amount_minor: 12990, payment_method_category: "CARD", card_brand: "MASTERCARD", card_type: "CREDIT", provider_connection_id: "conn_br_primary", channel: "WEB" }, processing: { stage: "CLASSIFYING", progress_percent: 45, failure_code: null }, outcome: null, classification: null, correlation_id: "corr_demo_batch_0001",
};
const failedRecord: TransactionRecord = {
  schema_version: "1.0", transaction_id: "txn_demo_1001", batch_id: "batch_demo_0001", created_at: "2026-08-29T18:00:02Z", updated_at: "2026-08-29T18:00:06Z", status: "FAILED", input: { ...processingRecord.input }, processing: { stage: "COMPLETE", progress_percent: 100, failure_code: null }, outcome: { result: "FAILED", provider_response_code: "51", normalized_decline_code: "INSUFFICIENT_FUNDS", latency_ms: 842 }, classification: { category: "ISSUER_DECLINE", reason: "The issuer declined the authorization because the account had insufficient funds.", confidence: .99, evidence_ids: ["evt_demo_1001_final"], related_incident_ids: [] }, correlation_id: "corr_demo_batch_0001",
};
const succeededRecord: TransactionRecord = {
  schema_version: "1.0", transaction_id: "txn_demo_1002", batch_id: "batch_demo_0001", created_at: "2026-08-29T18:00:02Z", updated_at: "2026-08-29T18:00:05Z", status: "SUCCEEDED", input: { client_reference: "checkout-1002", occurred_at: "2026-08-29T18:00:01Z", merchant_id: "merchant_br_01", provider_id: "provider_alpha", issuer_bank: "bank_br_b", country: "BR", currency: "BRL", amount_minor: 25990, payment_method_category: "DIGITAL_WALLET", card_brand: null, card_type: "NOT_APPLICABLE", provider_connection_id: "conn_br_primary", channel: "MOBILE" }, processing: { stage: "COMPLETE", progress_percent: 100, failure_code: null }, outcome: { result: "SUCCEEDED", provider_response_code: "00", normalized_decline_code: null, latency_ms: 318 }, classification: { category: "APPROVED", reason: "The provider approved the authorization.", confidence: 1, evidence_ids: ["evt_demo_1002_final"], related_incident_ids: [] }, correlation_id: "corr_demo_batch_0001",
};

const pipelineFailedRecord: TransactionRecord = {
  ...processingRecord,
  transaction_id: "txn_pipeline_9001",
  updated_at: "2026-08-29T18:00:09Z",
  status: "UNKNOWN",
  processing: {
    stage: "PIPELINE_FAILED",
    progress_percent: 100,
    failure_code: "WORKER_CLASSIFICATION_TIMEOUT",
  },
  outcome: null,
  classification: null,
};

const relatedIncidentRecord: TransactionRecord = {
  ...failedRecord,
  transaction_id: "txn_related_2001",
  updated_at: "2026-08-29T18:00:08Z",
  classification: {
    ...failedRecord.classification!,
    related_incident_ids: ["inc_current_mastercard_001"],
  },
};

const records: TransactionRecord[] = [
  processingRecord,
  pipelineFailedRecord,
  relatedIncidentRecord,
  failedRecord,
  succeededRecord,
].sort((left, right) => Date.parse(right.updated_at) - Date.parse(left.updated_at));

export function normalizeFixtureMode(value: string | undefined): TransactionFixtureMode {
  return value === "loading" || value === "empty" || value === "error" || value === "stale"
    ? value
    : "default";
}

export function buildFixtureTransactionList(query: OfflineTransactionQuery = {}): TransactionList {
  const filter = query.status ?? "ALL";
  const filtered = filter === "ALL" ? records : records.filter((record) => record.status === filter);
  const pageSize = 3;
  const start = query.cursor === "fixture-page-2" ? pageSize : 0;
  const items = filtered.slice(start, start + pageSize);

  return {
    schema_version: "1.0",
    items,
    next_cursor: start + pageSize < filtered.length ? "fixture-page-2" : null,
    correlation_id: "corr_demo_list_0001",
  };
}

export async function getOfflineTransactionList(query: OfflineTransactionQuery = {}): Promise<{
  list: TransactionList;
  stale: boolean;
}> {
  const fixture = query.fixture ?? "default";
  if (fixture === "loading") return new Promise<never>(() => undefined);
  if (fixture === "error") throw new OfflineFixtureError("The offline transaction source is unavailable.");

  if (fixture === "empty") {
    return {
      list: { schema_version: "1.0", items: [], next_cursor: null, correlation_id: "corr_demo_list_0001" },
      stale: false,
    };
  }

  return { list: buildFixtureTransactionList(query), stale: fixture === "stale" };
}

export async function getOfflineTransaction(
  transactionId: string,
  fixture: TransactionFixtureMode = "default",
): Promise<TransactionRecord> {
  if (fixture === "loading") return new Promise<never>(() => undefined);
  if (fixture === "error") throw new OfflineFixtureError("The offline transaction source is unavailable.");

  const record = records.find((item) => item.transaction_id === transactionId);
  if (!record) throw new OfflineFixtureError(`Transaction ${transactionId} is not available in the offline fixtures.`);
  return record;
}

export function getFixtureRecordByStatus(status: TransactionStatus): TransactionRecord {
  const record = records.find((item) => item.status === status);
  if (!record) throw new OfflineFixtureError(`No ${status} fixture is available.`);
  return record;
}
