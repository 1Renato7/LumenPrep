import {
  ApiPayloadError,
  parseDiagnosticSuggestion,
  parseIncidentDetail,
  parseIncidentList,
  parseTransactionIncidentDetail,
  parseTransactionBatchAccepted,
  parseTransactionCatalog,
  parseTransactionList,
  parseTransactionRecord,
  parseTransactionSampleResponse,
} from "./parse";
import type {
  Incident,
  IncidentDetail,
  DiagnosticSuggestion,
  TransactionBatchAccepted,
  TransactionBatchRequest,
  TransactionCatalog,
  TransactionList,
  TransactionRecord,
  TransactionSampleRequest,
  TransactionSampleResponse,
  TransactionStatus,
  TransactionIncidentDetail,
} from "./types";

export interface RequestOptions {
  signal?: AbortSignal;
  timeoutMs?: number;
}

export interface ListTransactionsQuery {
  status?: TransactionStatus;
  cursor?: string;
  limit?: number;
}

/** Stable shared surface for all web lanes; keep direct fetch calls out of pages. */
export interface LumenApiClient {
  getTransactionCatalog(options?: RequestOptions): Promise<TransactionCatalog>;
  generateTransactionSamples(request: TransactionSampleRequest, options?: RequestOptions): Promise<TransactionSampleResponse>;
  createTransactionBatch(request: TransactionBatchRequest, options?: RequestOptions): Promise<TransactionBatchAccepted>;
  getTransactionBatch(batchId: string, options?: RequestOptions): Promise<TransactionList>;
  listTransactions(query?: ListTransactionsQuery, options?: RequestOptions): Promise<TransactionList>;
  getTransaction(transactionId: string, options?: RequestOptions): Promise<TransactionRecord>;
  listIncidents(options?: RequestOptions): Promise<Incident[]>;
  listTransactionIncidents(transactionId: string, options?: RequestOptions): Promise<TransactionIncidentDetail>;
  getIncident(incidentId: string, options?: RequestOptions): Promise<IncidentDetail>;
  /** Additive CTR-AGT-003 read: never changes the engine-owned Incident. */
  getDiagnosticSuggestion(incidentId: string, options?: RequestOptions): Promise<DiagnosticSuggestion>;
}

export type LumenApiErrorCode =
  | "NOT_FOUND"
  | "CONFLICT"
  | "VALIDATION"
  | "SERVICE_UNAVAILABLE"
  | "TIMEOUT"
  | "CANCELLED"
  | "NETWORK"
  | "BACKEND_UNAVAILABLE"
  | "INVALID_RESPONSE"
  | "HTTP";

export type LumenBackendState = "READY" | "BACKEND_UNAVAILABLE";

export class LumenApiError extends Error {
  constructor(
    public readonly code: LumenApiErrorCode,
    public readonly status: 404 | 409 | 422 | 503 | null,
    public readonly body: unknown,
    message: string,
    public readonly correlationId: string | null = correlationIdFrom(body),
  ) {
    super(message);
    this.name = "LumenApiError";
  }
}

/** A network, timeout, configuration or 503 failure is rendered as this explicit UI state. */
export function backendStateFor(error: unknown): LumenBackendState {
  if (!(error instanceof LumenApiError)) return "BACKEND_UNAVAILABLE";
  return error.code === "CANCELLED" || error.code === "CONFLICT" || error.code === "VALIDATION" || error.code === "NOT_FOUND" || error.code === "INVALID_RESPONSE" || error.code === "HTTP"
    ? "READY"
    : "BACKEND_UNAVAILABLE";
}

export interface PollingController {
  readonly signal: AbortSignal;
  cancel(reason?: unknown): void;
}

/** Lets a route stop in-flight work on unmount, navigation, or filter change. */
export function createPollingController(parentSignal?: AbortSignal): PollingController {
  const controller = new AbortController();
  const relayAbort = () => controller.abort(parentSignal?.reason);
  if (parentSignal?.aborted) relayAbort();
  else parentSignal?.addEventListener("abort", relayAbort, { once: true });
  return {
    signal: controller.signal,
    cancel(reason?: unknown) {
      parentSignal?.removeEventListener("abort", relayAbort);
      controller.abort(reason);
    },
  };
}

export interface PollTransactionsOptions extends RequestOptions {
  query?: ListTransactionsQuery;
  batchId?: string;
  intervalMs?: number;
  onUpdate?: (list: TransactionList) => void | Promise<void>;
}

/** Polls only while backend-authored records are PROCESSING; callers cancel its signal during unmount/navigation. */
export async function pollTransactions(client: LumenApiClient, options: PollTransactionsOptions = {}): Promise<TransactionList> {
  const intervalMs = options.intervalMs ?? 1_000;
  if (!Number.isInteger(intervalMs) || intervalMs < 0) throw new RangeError("Polling interval must be a non-negative integer.");
  while (true) {
    throwIfAborted(options.signal);
    const list = options.batchId
      ? await client.getTransactionBatch(options.batchId, options)
      : await client.listTransactions(options.query, options);
    await options.onUpdate?.(list);
    if (!list.items.some((item) => item.status === "PROCESSING")) return list;
    await waitFor(intervalMs, options.signal);
  }
}

export interface PollTransactionOptions extends RequestOptions {
  intervalMs?: number;
  onUpdate?: (record: TransactionRecord) => void | Promise<void>;
}

/** Polls one transaction until the backend publishes a terminal public status. */
export async function pollTransaction(
  client: LumenApiClient,
  transactionId: string,
  options: PollTransactionOptions = {},
): Promise<TransactionRecord> {
  const intervalMs = options.intervalMs ?? 1_000;
  if (!Number.isInteger(intervalMs) || intervalMs < 0) throw new RangeError("Polling interval must be a non-negative integer.");
  while (true) {
    throwIfAborted(options.signal);
    const record = await client.getTransaction(transactionId, options);
    await options.onUpdate?.(record);
    if (record.status !== "PROCESSING") return record;
    await waitFor(intervalMs, options.signal);
  }
}

export interface BatchSubmission {
  readonly idempotencyKey: string;
  submit(options?: RequestOptions): Promise<TransactionBatchAccepted>;
}

/** Keeps the exact payload and Idempotency-Key stable across an explicit user retry. */
export function createBatchSubmission(client: LumenApiClient, request: TransactionBatchRequest): BatchSubmission {
  const snapshot = structuredClone(request);
  return {
    idempotencyKey: snapshot.idempotency_key,
    submit: (options) => client.createTransactionBatch(structuredClone(snapshot), options),
  };
}

export interface LumenApiClientOptions {
  fetchImpl?: typeof fetch;
  defaultTimeoutMs?: number;
  /** Test-only override. Browser code normally reads NEXT_PUBLIC_API_BASE_URL. */
  baseUrl?: string;
}

export function normalizeApiBaseUrl(value: string): string {
  const configured = value.trim();
  if (!configured) throw new Error("API base URL is empty.");
  let url: URL;
  try {
    url = new URL(configured);
  } catch {
    throw new Error("API base URL must be an absolute HTTP(S) URL.");
  }
  if ((url.protocol !== "https:" && url.protocol !== "http:") || url.username || url.password || url.search || url.hash) {
    throw new Error("API base URL must be a credential-free HTTP(S) origin and path.");
  }
  return `${url.origin}${url.pathname.replace(/\/+$/, "")}`;
}

export function createLumenApiClient(options: LumenApiClientOptions = {}): LumenApiClient {
  const fetchImpl = options.fetchImpl ?? fetch;
  const defaultTimeoutMs = options.defaultTimeoutMs ?? 10_000;
  const configuredBaseUrl = options.baseUrl ?? process.env.NEXT_PUBLIC_API_BASE_URL;
  const baseUrl = resolveBaseUrl(configuredBaseUrl);
  const request = <T>(path: string, init: RequestInit, parser: (body: unknown) => T, requestOptions?: RequestOptions) =>
    requestJson(fetchImpl, `${baseUrl}${path}`, init, parser, requestOptions, defaultTimeoutMs);

  return {
    getTransactionCatalog: (requestOptions) => request("/transaction-catalog", { method: "GET" }, parseTransactionCatalog, requestOptions),
    generateTransactionSamples: (body, requestOptions) => request("/transaction-samples", jsonPost(body), parseTransactionSampleResponse, requestOptions),
    createTransactionBatch: (body, requestOptions) => request("/transaction-batches", jsonPost(body, { "Idempotency-Key": body.idempotency_key }), parseTransactionBatchAccepted, requestOptions),
    getTransactionBatch: (batchId, requestOptions) => request(`/transaction-batches/${encodeURIComponent(batchId)}`, { method: "GET" }, parseTransactionList, requestOptions),
    listTransactions: (query, requestOptions) => request(`/transactions${toQuery(query)}`, { method: "GET" }, parseTransactionList, requestOptions),
    getTransaction: (transactionId, requestOptions) => request(`/transactions/${encodeURIComponent(transactionId)}`, { method: "GET" }, parseTransactionRecord, requestOptions),
    listIncidents: (requestOptions) => request("/incidents", { method: "GET" }, parseIncidentList, requestOptions),
    listTransactionIncidents: (transactionId, requestOptions) => {
      if (!transactionId) throw new LumenApiError("VALIDATION", 422, null, "transactionId must be non-empty.");
      return request(`/transactions/${encodeURIComponent(transactionId)}/incidents`, { method: "GET" }, parseTransactionIncidentDetail, requestOptions);
    },
    getIncident: (incidentId, requestOptions) => request(`/incidents/${encodeURIComponent(incidentId)}`, { method: "GET" }, parseIncidentDetail, requestOptions),
    getDiagnosticSuggestion: (incidentId, requestOptions) => request(`/incidents/${encodeURIComponent(incidentId)}/suggestion`, { method: "GET" }, parseDiagnosticSuggestion, requestOptions),
  };
}

function resolveBaseUrl(value: string | undefined): string {
  if (!value) throw new LumenApiError("BACKEND_UNAVAILABLE", null, null, "NEXT_PUBLIC_API_BASE_URL must be configured before calling the Lumen API.");
  try {
    return normalizeApiBaseUrl(value);
  } catch (error) {
    throw new LumenApiError("BACKEND_UNAVAILABLE", null, null, error instanceof Error ? error.message : "Invalid API base URL.");
  }
}

function jsonPost(body: unknown, headers: HeadersInit = {}): RequestInit {
  return { method: "POST", headers: { "Content-Type": "application/json", ...headers }, body: JSON.stringify(body) };
}

function toQuery(query: object | undefined): string {
  if (!query) return "";
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) if (value !== undefined) params.set(key, String(value));
  const serialized = params.toString();
  return serialized ? `?${serialized}` : "";
}

async function requestJson<T>(fetchImpl: typeof fetch, url: string, init: RequestInit, parser: (body: unknown) => T, options: RequestOptions | undefined, defaultTimeoutMs: number): Promise<T> {
  if (options?.signal?.aborted) throw new LumenApiError("CANCELLED", null, null, "Lumen API request was cancelled.");
  const controller = new AbortController();
  let timedOut = false;
  const relayAbort = () => controller.abort(options?.signal?.reason);
  if (options?.signal?.aborted) relayAbort();
  else options?.signal?.addEventListener("abort", relayAbort, { once: true });
  const timeoutMs = options?.timeoutMs ?? defaultTimeoutMs;
  const timeout = setTimeout(() => { timedOut = true; controller.abort(); }, timeoutMs);
  try {
    const response = await fetchImpl(url, { ...init, signal: controller.signal });
    const body = await responseBody(response);
    if (!response.ok) throw new LumenApiError(toErrorCode(response.status), typedStatus(response.status), body, `Lumen API request failed with HTTP ${response.status}.`);
    try {
      return parser(body);
    } catch (error) {
      if (error instanceof ApiPayloadError) throw new LumenApiError("INVALID_RESPONSE", null, error.payload, error.message, correlationIdFrom(body));
      throw error;
    }
  } catch (error) {
    if (error instanceof LumenApiError) throw error;
    if (timedOut) throw new LumenApiError("TIMEOUT", null, null, `Lumen API request timed out after ${timeoutMs}ms.`);
    if (options?.signal?.aborted) throw new LumenApiError("CANCELLED", null, null, "Lumen API request was cancelled.");
    throw new LumenApiError("NETWORK", null, null, "Lumen API request could not reach the backend.");
  } finally {
    clearTimeout(timeout);
    options?.signal?.removeEventListener("abort", relayAbort);
  }
}

async function responseBody(response: Response): Promise<unknown> {
  if (response.status === 204) return null;
  const text = await response.text();
  if (!text) return null;
  try { return JSON.parse(text) as unknown; } catch { return text; }
}

function toErrorCode(status: number): LumenApiErrorCode {
  if (status === 404) return "NOT_FOUND";
  if (status === 409) return "CONFLICT";
  if (status === 422) return "VALIDATION";
  if (status === 503) return "SERVICE_UNAVAILABLE";
  return "HTTP";
}

function typedStatus(status: number): 404 | 409 | 422 | 503 | null {
  return status === 404 || status === 409 || status === 422 || status === 503 ? status : null;
}

function correlationIdFrom(body: unknown): string | null {
  return body && typeof body === "object" && "correlation_id" in body && typeof (body as { correlation_id?: unknown }).correlation_id === "string"
    ? (body as { correlation_id: string }).correlation_id
    : null;
}

function throwIfAborted(signal: AbortSignal | undefined): void {
  if (signal?.aborted) throw new LumenApiError("CANCELLED", null, null, "Polling was cancelled.");
}

function waitFor(ms: number, signal: AbortSignal | undefined): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) { reject(new LumenApiError("CANCELLED", null, null, "Polling was cancelled.")); return; }
    const timeout = setTimeout(done, ms);
    const onAbort = () => { clearTimeout(timeout); reject(new LumenApiError("CANCELLED", null, null, "Polling was cancelled.")); };
    function done(): void { signal?.removeEventListener("abort", onAbort); resolve(); }
    signal?.addEventListener("abort", onAbort, { once: true });
  });
}
