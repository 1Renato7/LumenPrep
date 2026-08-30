import type {
  Incident,
  IncidentDetail,
  DiagnosticSuggestion,
  TransactionBatchAccepted,
  TransactionDataResetResponse,
  TransactionCatalog,
  TransactionClassification,
  TransactionInput,
  TransactionList,
  TransactionOutcome,
  TransactionProcessing,
  TransactionRecord,
  TransactionSampleResponse,
  TransactionStatus,
  TransactionIncidentDetail,
  NotificationFeed,
  HumanReviewResponse,
} from "./types";

export class ApiPayloadError extends Error {
  constructor(message: string, public readonly payload: unknown) {
    super(message);
    this.name = "ApiPayloadError";
  }
}

type JsonObject = Record<string, unknown>;

const transactionStatuses = new Set<TransactionStatus>([
  "PROCESSING",
  "SUCCEEDED",
  "FAILED",
  "UNKNOWN",
]);
const processingStages = new Set([
  "RECEIVED",
  "NORMALIZING",
  "CLASSIFYING",
  "AGGREGATING",
  "ANALYZING",
  "COMPLETE",
  "PIPELINE_FAILED",
]);
const paymentMethods = new Set([
  "CARD",
  "PIX",
  "BOLETO",
  "SPEI",
  "PSE",
  "BANK_TRANSFER",
  "DIGITAL_WALLET",
  "CASH_IN_STORE",
  "OTHER",
]);
const cardTypes = new Set(["CREDIT", "DEBIT", "PREPAID", "NOT_APPLICABLE"]);
const channels = new Set(["WEB", "MOBILE", "POS", "API"]);
const outcomeResults = new Set(["SUCCEEDED", "FAILED", "UNKNOWN"]);
const classificationCategories = new Set([
  "APPROVED",
  "ISSUER_DECLINE",
  "PROVIDER_ERROR",
  "TIMEOUT",
  "DATA_QUALITY",
  "UNKNOWN",
]);

function fail(message: string, payload: unknown): never {
  throw new ApiPayloadError(message, payload);
}

function object(value: unknown, context: string): JsonObject {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return fail(`${context} must be an object.`, value);
  }
  return value as JsonObject;
}

function exactObject(value: unknown, required: readonly string[], optional: readonly string[], context: string): JsonObject {
  const result = object(value, context);
  const allowed = new Set([...required, ...optional]);
  for (const key of Object.keys(result)) {
    if (!allowed.has(key)) fail(`${context} contains an unknown property: ${key}.`, value);
  }
  for (const key of required) {
    if (!(key in result)) fail(`${context} is missing required property: ${key}.`, value);
  }
  return result;
}

function string(value: unknown, context: string): string {
  if (typeof value !== "string" || value.length === 0) fail(`${context} must be a non-empty string.`, value);
  return value;
}

function nullableString(value: unknown, context: string): string | null {
  return value === null ? null : string(value, context);
}

function integer(value: unknown, context: string, min = 0, max = Number.MAX_SAFE_INTEGER): number {
  if (!Number.isInteger(value) || (value as number) < min || (value as number) > max) {
    fail(`${context} must be an integer between ${min} and ${max}.`, value);
  }
  return value as number;
}

function number(value: unknown, context: string, min = -Infinity, max = Infinity): number {
  if (typeof value !== "number" || !Number.isFinite(value) || value < min || value > max) {
    fail(`${context} must be a number between ${min} and ${max}.`, value);
  }
  return value;
}

function stringArray(value: unknown, context: string): string[] {
  if (!Array.isArray(value)) fail(`${context} must be an array.`, value);
  return value.map((item, index) => string(item, `${context}[${index}]`));
}

function uniqueStringArray(value: unknown, context: string): string[] {
  const result = stringArray(value, context);
  if (new Set(result).size !== result.length) fail(`${context} must contain unique values.`, value);
  return result;
}

function enumValue<T extends string>(value: unknown, values: Set<T>, context: string): T {
  if (typeof value !== "string" || !values.has(value as T)) fail(`${context} has an invalid value.`, value);
  return value as T;
}

function schemaVersion(value: unknown, context: string): "1.0" {
  if (value !== "1.0") fail(`${context} must be schema version 1.0.`, value);
  return value;
}

export function parseTransactionInput(value: unknown): TransactionInput {
  const input = exactObject(
    value,
    ["merchant_id", "provider_id", "issuer_bank", "country", "currency", "amount_minor", "payment_method_category"],
    ["client_reference", "occurred_at", "card_brand", "card_type", "provider_connection_id", "provider_response_code", "channel"],
    "TransactionInput",
  );
  const country = string(input.country, "TransactionInput.country");
  const currency = string(input.currency, "TransactionInput.currency");
  if (!/^[A-Z]{2}$/.test(country) || !/^[A-Z]{3}$/.test(currency)) {
    fail("TransactionInput country or currency is invalid.", value);
  }
  const cardType = input.card_type === undefined ? undefined : input.card_type === null ? null : enumValue(input.card_type, cardTypes, "TransactionInput.card_type") as TransactionInput["card_type"];
  const channel = input.channel === undefined ? undefined : input.channel === null ? null : enumValue(input.channel, channels, "TransactionInput.channel") as TransactionInput["channel"];
  return {
    ...(input.client_reference === undefined ? {} : { client_reference: nullableString(input.client_reference, "TransactionInput.client_reference") }),
    ...(input.occurred_at === undefined ? {} : { occurred_at: nullableString(input.occurred_at, "TransactionInput.occurred_at") }),
    merchant_id: string(input.merchant_id, "TransactionInput.merchant_id"),
    provider_id: string(input.provider_id, "TransactionInput.provider_id"),
    issuer_bank: string(input.issuer_bank, "TransactionInput.issuer_bank"),
    country,
    currency,
    amount_minor: integer(input.amount_minor, "TransactionInput.amount_minor", 1),
    payment_method_category: enumValue(input.payment_method_category, paymentMethods, "TransactionInput.payment_method_category") as TransactionInput["payment_method_category"],
    ...(input.card_brand === undefined ? {} : { card_brand: nullableString(input.card_brand, "TransactionInput.card_brand") }),
    ...(cardType === undefined ? {} : { card_type: cardType }),
    ...(input.provider_connection_id === undefined ? {} : { provider_connection_id: nullableString(input.provider_connection_id, "TransactionInput.provider_connection_id") }),
    ...(input.provider_response_code === undefined ? {} : { provider_response_code: nullableString(input.provider_response_code, "TransactionInput.provider_response_code") }),
    ...(channel === undefined ? {} : { channel }),
  };
}

export function parseTransactionCatalog(value: unknown): TransactionCatalog {
  const catalog = exactObject(value, ["schema_version", "max_batch_size", "merchants", "providers", "issuer_banks", "countries", "currencies", "payment_method_categories", "card_brands", "card_types", "correlation_id"], [], "TransactionCatalog");
  return {
    schema_version: schemaVersion(catalog.schema_version, "TransactionCatalog.schema_version"),
    max_batch_size: integer(catalog.max_batch_size, "TransactionCatalog.max_batch_size", 1, 100),
    merchants: stringArray(catalog.merchants, "TransactionCatalog.merchants"),
    providers: stringArray(catalog.providers, "TransactionCatalog.providers"),
    issuer_banks: stringArray(catalog.issuer_banks, "TransactionCatalog.issuer_banks"),
    countries: stringArray(catalog.countries, "TransactionCatalog.countries"),
    currencies: stringArray(catalog.currencies, "TransactionCatalog.currencies"),
    payment_method_categories: stringArray(catalog.payment_method_categories, "TransactionCatalog.payment_method_categories"),
    card_brands: stringArray(catalog.card_brands, "TransactionCatalog.card_brands"),
    card_types: stringArray(catalog.card_types, "TransactionCatalog.card_types"),
    correlation_id: string(catalog.correlation_id, "TransactionCatalog.correlation_id"),
  };
}

export function parseTransactionSampleResponse(value: unknown): TransactionSampleResponse {
  const response = exactObject(value, ["schema_version", "seed", "transactions", "correlation_id"], [], "TransactionSampleResponse");
  if (!Array.isArray(response.transactions) || response.transactions.length < 1 || response.transactions.length > 100) {
    fail("TransactionSampleResponse.transactions must contain 1..100 items.", value);
  }
  return {
    schema_version: schemaVersion(response.schema_version, "TransactionSampleResponse.schema_version"),
    seed: integer(response.seed, "TransactionSampleResponse.seed", 0),
    transactions: response.transactions.map(parseTransactionInput),
    correlation_id: string(response.correlation_id, "TransactionSampleResponse.correlation_id"),
  };
}

export function parseTransactionBatchAccepted(value: unknown): TransactionBatchAccepted {
  const response = exactObject(value, ["schema_version", "batch_id", "accepted_at", "status", "transaction_ids", "correlation_id"], [], "TransactionBatchAccepted");
  if (response.status !== "PROCESSING") fail("TransactionBatchAccepted.status must be PROCESSING.", value);
  const transactionIds = stringArray(response.transaction_ids, "TransactionBatchAccepted.transaction_ids");
  if (transactionIds.length < 1 || transactionIds.length > 100 || new Set(transactionIds).size !== transactionIds.length) {
    fail("TransactionBatchAccepted.transaction_ids must be unique and contain 1..100 items.", value);
  }
  return { schema_version: schemaVersion(response.schema_version, "TransactionBatchAccepted.schema_version"), batch_id: string(response.batch_id, "TransactionBatchAccepted.batch_id"), accepted_at: string(response.accepted_at, "TransactionBatchAccepted.accepted_at"), status: "PROCESSING", transaction_ids: transactionIds, correlation_id: string(response.correlation_id, "TransactionBatchAccepted.correlation_id") };
}

export function parseTransactionDataResetResponse(value: unknown): TransactionDataResetResponse {
  const response = exactObject(value, ["schema_version", "removed", "correlation_id"], [], "TransactionDataResetResponse");
  const removed = exactObject(
    response.removed,
    ["transaction_incident_links", "incident_notifications", "incident_suggestions", "incident_records", "transaction_records", "transaction_batches", "canonical_attempts", "canonical_events", "raw_events", "quarantine"],
    [],
    "TransactionDataResetResponse.removed",
  );
  return {
    schema_version: schemaVersion(response.schema_version, "TransactionDataResetResponse.schema_version"),
    removed: {
      transaction_incident_links: integer(removed.transaction_incident_links, "removed.transaction_incident_links"),
      incident_notifications: integer(removed.incident_notifications, "removed.incident_notifications"),
      incident_suggestions: integer(removed.incident_suggestions, "removed.incident_suggestions"),
      incident_records: integer(removed.incident_records, "removed.incident_records"),
      transaction_records: integer(removed.transaction_records, "removed.transaction_records"),
      transaction_batches: integer(removed.transaction_batches, "removed.transaction_batches"),
      canonical_attempts: integer(removed.canonical_attempts, "removed.canonical_attempts"),
      canonical_events: integer(removed.canonical_events, "removed.canonical_events"),
      raw_events: integer(removed.raw_events, "removed.raw_events"),
      quarantine: integer(removed.quarantine, "removed.quarantine"),
    },
    correlation_id: string(response.correlation_id, "TransactionDataResetResponse.correlation_id"),
  };
}

function parseProcessing(value: unknown): TransactionProcessing {
  const processing = exactObject(value, ["stage", "progress_percent"], ["failure_code"], "TransactionProcessing");
  return { stage: enumValue(processing.stage, processingStages, "TransactionProcessing.stage"), progress_percent: integer(processing.progress_percent, "TransactionProcessing.progress_percent", 0, 100), ...(processing.failure_code === undefined ? {} : { failure_code: nullableString(processing.failure_code, "TransactionProcessing.failure_code") }) } as TransactionProcessing;
}

function parseOutcome(value: unknown): TransactionOutcome | null {
  if (value === null) return null;
  const outcome = exactObject(value, ["result", "provider_response_code", "normalized_decline_code", "latency_ms"], [], "TransactionOutcome");
  return { result: enumValue(outcome.result, outcomeResults, "TransactionOutcome.result"), provider_response_code: nullableString(outcome.provider_response_code, "TransactionOutcome.provider_response_code"), normalized_decline_code: nullableString(outcome.normalized_decline_code, "TransactionOutcome.normalized_decline_code"), latency_ms: integer(outcome.latency_ms, "TransactionOutcome.latency_ms", 0) } as TransactionOutcome;
}

function parseClassification(value: unknown): TransactionClassification | null {
  if (value === null) return null;
  const classification = exactObject(value, ["category", "reason", "confidence", "evidence_ids", "related_incident_ids"], ["refusal_resolution", "related_incidents"], "TransactionClassification");
  const refusal = classification.refusal_resolution === undefined ? undefined : exactObject(classification.refusal_resolution, ["lookup_status", "provider_id", "issuer_bank", "card_brand", "response_code", "outcome", "normalized_code", "reason", "source", "mapping_version"], ["observed_response_code"], "RefusalCodeResolution");
  const relatedIncidents = classification.related_incidents === undefined ? undefined : (() => {
    if (!Array.isArray(classification.related_incidents)) fail("TransactionClassification.related_incidents must be an array.", classification.related_incidents);
    return classification.related_incidents.map((item, index) => {
      const related = exactObject(item, ["incident_id", "recurrence_first_detected_at"], [], `TransactionClassification.related_incidents[${index}]`);
      return { incident_id: string(related.incident_id, `TransactionClassification.related_incidents[${index}].incident_id`), recurrence_first_detected_at: nullableString(related.recurrence_first_detected_at, `TransactionClassification.related_incidents[${index}].recurrence_first_detected_at`) };
    });
  })();
  return { category: enumValue(classification.category, classificationCategories, "TransactionClassification.category"), reason: string(classification.reason, "TransactionClassification.reason"), confidence: number(classification.confidence, "TransactionClassification.confidence", 0, 1), evidence_ids: stringArray(classification.evidence_ids, "TransactionClassification.evidence_ids"), related_incident_ids: stringArray(classification.related_incident_ids, "TransactionClassification.related_incident_ids"), ...(relatedIncidents === undefined ? {} : { related_incidents: relatedIncidents }), ...(refusal === undefined ? {} : { refusal_resolution: { lookup_status: enumValue(refusal.lookup_status, new Set(["MATCH_FOUND", "NOT_FOUND", "AMBIGUOUS"]), "RefusalCodeResolution.lookup_status") as "MATCH_FOUND" | "NOT_FOUND" | "AMBIGUOUS", provider_id: string(refusal.provider_id, "RefusalCodeResolution.provider_id"), issuer_bank: string(refusal.issuer_bank, "RefusalCodeResolution.issuer_bank"), card_brand: string(refusal.card_brand, "RefusalCodeResolution.card_brand"), response_code: string(refusal.response_code, "RefusalCodeResolution.response_code"), outcome: enumValue(refusal.outcome, outcomeResults, "RefusalCodeResolution.outcome"), normalized_code: nullableString(refusal.normalized_code, "RefusalCodeResolution.normalized_code"), reason: nullableString(refusal.reason, "RefusalCodeResolution.reason"), source: nullableString(refusal.source, "RefusalCodeResolution.source"), mapping_version: nullableString(refusal.mapping_version, "RefusalCodeResolution.mapping_version") } }) } as TransactionClassification;
}

export function parseTransactionRecord(value: unknown): TransactionRecord {
  const record = exactObject(value, ["schema_version", "transaction_id", "batch_id", "created_at", "updated_at", "status", "input", "processing", "outcome", "classification", "correlation_id"], [], "TransactionRecord");
  const status = enumValue(record.status, transactionStatuses, "TransactionRecord.status");
  const processing = parseProcessing(record.processing);
  const outcome = parseOutcome(record.outcome);
  const classification = parseClassification(record.classification);
  if (status === "PROCESSING" && (processing.progress_percent >= 100 || outcome !== null || classification !== null)) fail("PROCESSING record has terminal data.", value);
  if (status === "SUCCEEDED" && (processing.stage !== "COMPLETE" || processing.progress_percent !== 100 || outcome?.result !== "SUCCEEDED" || classification?.category !== "APPROVED")) fail("SUCCEEDED record violates its lifecycle invariant.", value);
  if (status === "FAILED" && (processing.stage !== "COMPLETE" || processing.progress_percent !== 100 || outcome?.result !== "FAILED" || classification === null || classification.category === "APPROVED")) fail("FAILED record violates its lifecycle invariant.", value);
  if (status === "UNKNOWN") {
    const terminalUnknown = processing.stage === "COMPLETE" && processing.progress_percent === 100 && outcome?.result === "UNKNOWN" && classification?.category === "UNKNOWN";
    const pipelineFailure = processing.stage === "PIPELINE_FAILED" && processing.progress_percent === 100 && typeof processing.failure_code === "string" && processing.failure_code.length > 0 && outcome === null && classification === null;
    if (!terminalUnknown && !pipelineFailure) fail("UNKNOWN record violates its lifecycle invariant.", value);
  }
  return { schema_version: schemaVersion(record.schema_version, "TransactionRecord.schema_version"), transaction_id: string(record.transaction_id, "TransactionRecord.transaction_id"), batch_id: string(record.batch_id, "TransactionRecord.batch_id"), created_at: string(record.created_at, "TransactionRecord.created_at"), updated_at: string(record.updated_at, "TransactionRecord.updated_at"), status, input: parseTransactionInput(record.input), processing, outcome, classification, correlation_id: string(record.correlation_id, "TransactionRecord.correlation_id") };
}

export function parseTransactionList(value: unknown): TransactionList {
  const list = exactObject(value, ["schema_version", "items", "next_cursor", "correlation_id"], [], "TransactionList");
  if (!Array.isArray(list.items)) fail("TransactionList.items must be an array.", value);
  return { schema_version: schemaVersion(list.schema_version, "TransactionList.schema_version"), items: list.items.map(parseTransactionRecord), next_cursor: nullableString(list.next_cursor, "TransactionList.next_cursor"), correlation_id: string(list.correlation_id, "TransactionList.correlation_id") };
}

export function parseIncident(value: unknown): Incident {
  const incident = exactObject(value, ["schema_version", "incident_id", "state", "detected_at", "estimated_started_at", "title", "scope", "metrics", "root_cause", "impact", "evidence", "recommendations", "limitations", "correlation_id"], ["memory_matches", "recurrence_first_detected_at"], "Incident");
  if (incident.schema_version !== "1.0") fail("Incident.schema_version must be 1.0.", value);
  const states = new Set(["DETECTED", "INVESTIGATING", "SUPPORTED", "INCONCLUSIVE", "RECOVERED", "HUMAN_CONFIRMED", "CLOSED"]);
  const scope = object(incident.scope, "Incident.scope");
  const metrics = object(incident.metrics, "Incident.metrics");
  for (const [key, scopeValue] of Object.entries(scope)) scope[key] = stringArray(scopeValue, `Incident.scope.${key}`);
  for (const [key, metric] of Object.entries(metrics)) {
    if (Array.isArray(metric)) {
      stringArray(metric, `Incident.metrics.${key}`);
      continue;
    }
    if (metric !== null && typeof metric !== "string" && (typeof metric !== "number" || !Number.isFinite(metric))) fail(`Incident.metrics.${key} has an invalid value.`, metric);
  }
  const rootCause = exactObject(incident.root_cause, ["status", "category", "confidence", "confidence_factors"], ["alternatives"], "Incident.root_cause");
  if (rootCause.status !== "SUPPORTED" && rootCause.status !== "INCONCLUSIVE") fail("Incident.root_cause.status is invalid.", value);
  const confidenceFactors = object(rootCause.confidence_factors, "Incident.root_cause.confidence_factors");
  for (const [key, factor] of Object.entries(confidenceFactors)) number(factor, `Incident.root_cause.confidence_factors.${key}`, 0, 1);
  const alternatives = rootCause.alternatives === undefined
    ? undefined
    : (() => {
      if (!Array.isArray(rootCause.alternatives)) fail("Incident.root_cause.alternatives must be an array.", rootCause.alternatives);
      return rootCause.alternatives.map((item) => {
        const alternative = exactObject(item, ["category", "confidence"], [], "Incident.root_cause.alternative");
        return {
          category: string(alternative.category, "Incident.root_cause.alternative.category"),
          confidence: number(alternative.confidence, "Incident.root_cause.alternative.confidence", 0, 1),
        };
      });
    })();
  const impact = exactObject(incident.impact, ["metric", "amount_minor", "currency", "method"], ["lower_bound_minor", "upper_bound_minor"], "Incident.impact");
  if (impact.metric !== "GMV_AT_RISK" || impact.method !== "EXPECTED_APPROVAL_SHORTFALL") fail("Incident.impact has an invalid constant.", value);
  const impactCurrency = string(impact.currency, "Incident.impact.currency");
  if (!/^[A-Z]{3}$/.test(impactCurrency)) fail("Incident.impact.currency is invalid.", value);
  const evidence = parseIncidentEvidence(incident.evidence);
  const recommendations = parseRecommendations(incident.recommendations);
  return {
    schema_version: "1.0",
    incident_id: string(incident.incident_id, "Incident.incident_id"),
    state: enumValue(incident.state, states, "Incident.state") as Incident["state"],
    detected_at: string(incident.detected_at, "Incident.detected_at"),
    estimated_started_at: string(incident.estimated_started_at, "Incident.estimated_started_at"),
    ...(incident.recurrence_first_detected_at === undefined ? {} : { recurrence_first_detected_at: nullableString(incident.recurrence_first_detected_at, "Incident.recurrence_first_detected_at") }),
    title: string(incident.title, "Incident.title"),
    scope: scope as Incident["scope"],
    metrics: metrics as Incident["metrics"],
    root_cause: { status: rootCause.status, category: nullableString(rootCause.category, "Incident.root_cause.category"), confidence: number(rootCause.confidence, "Incident.root_cause.confidence", 0, 1), confidence_factors: confidenceFactors as Record<string, number>, ...(alternatives === undefined ? {} : { alternatives }) },
    impact: { metric: "GMV_AT_RISK", amount_minor: integer(impact.amount_minor, "Incident.impact.amount_minor", 0), currency: impactCurrency, method: "EXPECTED_APPROVAL_SHORTFALL", ...(impact.lower_bound_minor === undefined ? {} : { lower_bound_minor: impact.lower_bound_minor === null ? null : integer(impact.lower_bound_minor, "Incident.impact.lower_bound_minor", 0) }), ...(impact.upper_bound_minor === undefined ? {} : { upper_bound_minor: impact.upper_bound_minor === null ? null : integer(impact.upper_bound_minor, "Incident.impact.upper_bound_minor", 0) }) },
    evidence,
    ...(incident.memory_matches === undefined ? {} : { memory_matches: parseLooseObjects(incident.memory_matches, "Incident.memory_matches") }),
    recommendations,
    limitations: stringArray(incident.limitations, "Incident.limitations"),
    correlation_id: string(incident.correlation_id, "Incident.correlation_id"),
  };
}

export function parseIncidentList(value: unknown): Incident[] {
  if (!Array.isArray(value)) fail("Incident list must be an array.", value);
  return value.map(parseIncident);
}

export function parseNotificationFeed(value: unknown): NotificationFeed {
  const feed = exactObject(value, ["notifications", "unread_count"], [], "NotificationFeed");
  if (!Array.isArray(feed.notifications)) fail("NotificationFeed.notifications must be an array.", value);
  return {
    unread_count: integer(feed.unread_count, "NotificationFeed.unread_count", 0),
    notifications: feed.notifications.map((item, index) => {
      const notification = exactObject(item, ["notification_id", "incident_id", "created_at", "read_at", "incident"], [], `NotificationFeed.notifications[${index}]`);
      return {
        notification_id: string(notification.notification_id, "notification_id"),
        incident_id: string(notification.incident_id, "incident_id"),
        created_at: string(notification.created_at, "created_at"),
        read_at: nullableString(notification.read_at, "read_at"),
        incident: parseIncident(notification.incident),
      };
    }),
  };
}

export function parseIncidentDetailList(value: unknown): IncidentDetail[] {
  if (!Array.isArray(value)) fail("Incident detail list must be an array.", value);
  return value.map(parseIncidentDetail);
}

export function parseTransactionIncidentDetail(value: unknown): TransactionIncidentDetail {
  const detail = exactObject(
    value,
    ["schema_version", "transaction_id", "status", "incidents", "rejected_incident_ids", "limitations"],
    [],
    "TransactionIncidentDetail",
  );
  const schemaVersion = string(detail.schema_version, "TransactionIncidentDetail.schema_version");
  if (schemaVersion !== "1.0") return fail("TransactionIncidentDetail.schema_version must be 1.0.", value);
  const transactionId = string(detail.transaction_id, "TransactionIncidentDetail.transaction_id");
  if (!transactionId) return fail("TransactionIncidentDetail.transaction_id must be non-empty.", value);
  const status = enumValue(
    detail.status,
    new Set(["RESOLVED", "PARTIAL", "NO_INCIDENT"]),
    "TransactionIncidentDetail.status",
  ) as TransactionIncidentDetail["status"];
  if (!Array.isArray(detail.incidents)) return fail("TransactionIncidentDetail.incidents must be an array.", value);
  const incidents = detail.incidents.map((entry, index) => {
    const link = exactObject(entry, ["incident", "memory", "explanation", "evidence_ids", "limitations"], [], `TransactionIncidentDetail.incidents[${index}]`);
    return {
      incident: parseIncident(link.incident),
      memory: parseSimilarIncidents(link.memory),
      explanation: parseExplanation(link.explanation),
      evidence_ids: uniqueStringArray(link.evidence_ids, `TransactionIncidentDetail.incidents[${index}].evidence_ids`),
      limitations: stringArray(link.limitations, `TransactionIncidentDetail.incidents[${index}].limitations`),
    };
  });
  if (status === "NO_INCIDENT" && incidents.length !== 0) return fail("NO_INCIDENT must not contain incidents.", value);
  if (status === "RESOLVED" && incidents.length === 0) return fail("RESOLVED must contain at least one incident.", value);
  return {
    schema_version: "1.0",
    transaction_id: transactionId,
    status,
    incidents,
    rejected_incident_ids: uniqueStringArray(detail.rejected_incident_ids, "TransactionIncidentDetail.rejected_incident_ids"),
    limitations: stringArray(detail.limitations, "TransactionIncidentDetail.limitations"),
  };
}

export function parseIncidentDetail(value: unknown): IncidentDetail {
  const detail = exactObject(value, ["incident", "memory", "explanation"], [], "IncidentDetail");
  return { incident: parseIncident(detail.incident), memory: parseSimilarIncidents(detail.memory), explanation: parseExplanation(detail.explanation) };
}

export function parseHumanReviewResponse(value: unknown): HumanReviewResponse {
  const response = exactObject(value, ["schema_version", "review", "promoted_to_memory"], [], "HumanReviewResponse");
  if (response.schema_version !== "1.0" || typeof response.promoted_to_memory !== "boolean") fail("HumanReviewResponse is invalid.", value);
  const review = exactObject(response.review, ["review_id", "incident_id", "decision", "reviewer_id", "reason", "confirmed_cause", "playbook_id", "reviewed_at"], [], "HumanReviewResponse.review");
  return { schema_version: "1.0", promoted_to_memory: response.promoted_to_memory, review: { review_id: string(review.review_id, "review.review_id"), incident_id: string(review.incident_id, "review.incident_id"), decision: enumValue(review.decision, new Set(["APPROVED", "REJECTED"]), "review.decision") as "APPROVED" | "REJECTED", reviewer_id: string(review.reviewer_id, "review.reviewer_id"), reason: string(review.reason, "review.reason"), confirmed_cause: nullableString(review.confirmed_cause, "review.confirmed_cause"), playbook_id: nullableString(review.playbook_id, "review.playbook_id"), reviewed_at: string(review.reviewed_at, "review.reviewed_at") } };
}

/** Keep the agent's hypothesis on its additive contract; never parse it as an Incident cause. */
export function parseDiagnosticSuggestion(value: unknown): DiagnosticSuggestion {
  const suggestion = exactObject(value, ["schema_version", "incident_id", "evidence_fingerprint", "status", "suggested_category", "summary_for_operations", "executive_summary", "reasons", "confidence", "recommended_actions", "limitations", "retrieval_trace", "model_version"], [], "DiagnosticSuggestion");
  if (suggestion.schema_version !== "1.0") fail("DiagnosticSuggestion.schema_version must be 1.0.", value);
  const status = enumValue(suggestion.status, new Set(["SUGGESTED", "INSUFFICIENT_EVIDENCE", "UNAVAILABLE"]), "DiagnosticSuggestion.status") as DiagnosticSuggestion["status"];
  if (!Array.isArray(suggestion.reasons)) fail("DiagnosticSuggestion.reasons must be an array.", suggestion.reasons);
  const reasons = suggestion.reasons.map((item, index) => {
    const reason = exactObject(item, ["statement", "evidence_ids"], [], `DiagnosticSuggestion.reasons[${index}]`);
    return { statement: string(reason.statement, `DiagnosticSuggestion.reasons[${index}].statement`), evidence_ids: stringArray(reason.evidence_ids, `DiagnosticSuggestion.reasons[${index}].evidence_ids`) };
  });
  if (!Array.isArray(suggestion.recommended_actions)) fail("DiagnosticSuggestion.recommended_actions must be an array.", suggestion.recommended_actions);
  const recommendedActions = suggestion.recommended_actions.map((item, index) => {
    const action = exactObject(item, ["action", "execution", "rationale_evidence_ids"], [], `DiagnosticSuggestion.recommended_actions[${index}]`);
    if (action.execution !== "HUMAN_ONLY") fail("DiagnosticSuggestion.recommended_actions.execution must be HUMAN_ONLY.", item);
    return { action: string(action.action, `DiagnosticSuggestion.recommended_actions[${index}].action`), execution: "HUMAN_ONLY" as const, rationale_evidence_ids: stringArray(action.rationale_evidence_ids, `DiagnosticSuggestion.recommended_actions[${index}].rationale_evidence_ids`) };
  });
  return { schema_version: "1.0", incident_id: string(suggestion.incident_id, "DiagnosticSuggestion.incident_id"), evidence_fingerprint: string(suggestion.evidence_fingerprint, "DiagnosticSuggestion.evidence_fingerprint"), status, suggested_category: nullableString(suggestion.suggested_category, "DiagnosticSuggestion.suggested_category"), summary_for_operations: string(suggestion.summary_for_operations, "DiagnosticSuggestion.summary_for_operations"), executive_summary: string(suggestion.executive_summary, "DiagnosticSuggestion.executive_summary"), reasons, confidence: number(suggestion.confidence, "DiagnosticSuggestion.confidence", 0, 1), recommended_actions: recommendedActions, limitations: stringArray(suggestion.limitations, "DiagnosticSuggestion.limitations"), retrieval_trace: object(suggestion.retrieval_trace, "DiagnosticSuggestion.retrieval_trace"), model_version: string(suggestion.model_version, "DiagnosticSuggestion.model_version") };
}

function parseIncidentEvidence(value: unknown): Incident["evidence"] {
  if (!Array.isArray(value)) fail("Incident.evidence must be an array.", value);
  return value.map((item) => {
    const evidence = exactObject(item, ["evidence_id", "kind", "statement", "source_ref"], [], "Incident.evidence item");
    return { evidence_id: string(evidence.evidence_id, "Incident.evidence.evidence_id"), kind: string(evidence.kind, "Incident.evidence.kind"), statement: string(evidence.statement, "Incident.evidence.statement"), source_ref: string(evidence.source_ref, "Incident.evidence.source_ref") };
  });
}

function parseRecommendations(value: unknown): Incident["recommendations"] {
  if (!Array.isArray(value)) fail("Incident.recommendations must be an array.", value);
  return value.map((item) => {
    const recommendation = exactObject(item, ["playbook_id", "action", "execution", "rationale_evidence_ids"], ["recommendation_class"], "Incident.recommendation");
    if (recommendation.execution !== "HUMAN_ONLY") fail("Incident.recommendation.execution must be HUMAN_ONLY.", item);
    const recommendationClass = recommendation.recommendation_class === undefined
      ? undefined
      : enumValue(recommendation.recommendation_class, new Set(["INVESTIGATE", "MONITOR", "ESCALATE"]), "Incident.recommendation.recommendation_class") as NonNullable<Incident["recommendations"][number]["recommendation_class"]>;
    return { playbook_id: string(recommendation.playbook_id, "Incident.recommendation.playbook_id"), action: string(recommendation.action, "Incident.recommendation.action"), ...(recommendationClass === undefined ? {} : { recommendation_class: recommendationClass }), execution: "HUMAN_ONLY", rationale_evidence_ids: stringArray(recommendation.rationale_evidence_ids, "Incident.recommendation.rationale_evidence_ids") };
  });
}

function parseLooseObjects(value: unknown, context: string): object[] {
  if (!Array.isArray(value)) fail(`${context} must be an array.`, value);
  return value.map((item) => object(item, context));
}

function parseSimilarIncidents(value: unknown): IncidentDetail["memory"] {
  const memory = exactObject(value, ["schema_version", "query_incident_id", "memory_status", "matches", "retrieval_trace", "correlation_id"], [], "SimilarIncidentResult");
  if (memory.schema_version !== "1.1" || !Array.isArray(memory.matches)) fail("SimilarIncidentResult is invalid.", value);
  const status = enumValue(memory.memory_status, new Set(["MATCH_FOUND", "NO_PRECEDENT", "MEMORY_UNAVAILABLE"]), "SimilarIncidentResult.memory_status") as IncidentDetail["memory"]["memory_status"];
  const matches = memory.matches.map((item) => {
    const match = exactObject(item, ["incident_id", "occurred_at", "confirmation", "structured_score", "matching_factors", "different_factors", "confirmed_cause", "prior_playbook_id", "evidence_ids"], ["semantic_score"], "SimilarIncidentResult.match");
    if (match.confirmation !== "HUMAN_CONFIRMED") fail("SimilarIncidentResult.match.confirmation must be HUMAN_CONFIRMED.", item);
    return { incident_id: string(match.incident_id, "SimilarIncidentResult.match.incident_id"), occurred_at: string(match.occurred_at, "SimilarIncidentResult.match.occurred_at"), confirmation: "HUMAN_CONFIRMED" as const, structured_score: number(match.structured_score, "SimilarIncidentResult.match.structured_score", 0, 1), ...(match.semantic_score === undefined ? {} : { semantic_score: match.semantic_score === null ? null : number(match.semantic_score, "SimilarIncidentResult.match.semantic_score", 0, 1) }), matching_factors: stringArray(match.matching_factors, "SimilarIncidentResult.match.matching_factors"), different_factors: stringArray(match.different_factors, "SimilarIncidentResult.match.different_factors"), confirmed_cause: string(match.confirmed_cause, "SimilarIncidentResult.match.confirmed_cause"), prior_playbook_id: string(match.prior_playbook_id, "SimilarIncidentResult.match.prior_playbook_id"), evidence_ids: stringArray(match.evidence_ids, "SimilarIncidentResult.match.evidence_ids") };
  });
  if ((status === "MATCH_FOUND" && matches.length < 1) || (status !== "MATCH_FOUND" && matches.length > 0)) fail("SimilarIncidentResult matches do not match memory status.", value);
  const trace = exactObject(memory.retrieval_trace, ["cypher_filter", "candidate_count", "embedding_model", "index_version", "fallback_used"], [], "SimilarIncidentResult.retrieval_trace");
  if (typeof trace.fallback_used !== "boolean") fail("SimilarIncidentResult.retrieval_trace.fallback_used must be boolean.", trace.fallback_used);
  return { schema_version: "1.1", query_incident_id: string(memory.query_incident_id, "SimilarIncidentResult.query_incident_id"), memory_status: status, matches, retrieval_trace: { cypher_filter: string(trace.cypher_filter, "SimilarIncidentResult.retrieval_trace.cypher_filter"), candidate_count: integer(trace.candidate_count, "SimilarIncidentResult.retrieval_trace.candidate_count", 0), embedding_model: nullableString(trace.embedding_model, "SimilarIncidentResult.retrieval_trace.embedding_model"), index_version: string(trace.index_version, "SimilarIncidentResult.retrieval_trace.index_version"), fallback_used: trace.fallback_used }, correlation_id: string(memory.correlation_id, "SimilarIncidentResult.correlation_id") };
}

function parseExplanation(value: unknown): IncidentDetail["explanation"] {
  const explanation = exactObject(value, ["schema_version", "incident_id", "executive_summary", "operations_summary", "what_happened", "where_and_why", "recurrence_statement", "evidence_ids", "playbook_id", "recommended_action", "execution", "limitations", "model_version"], [], "ExplanationBundle");
  if (explanation.schema_version !== "1.0" || explanation.execution !== "HUMAN_ONLY") fail("ExplanationBundle is invalid.", value);
  return { schema_version: "1.0", incident_id: string(explanation.incident_id, "ExplanationBundle.incident_id"), executive_summary: string(explanation.executive_summary, "ExplanationBundle.executive_summary"), operations_summary: string(explanation.operations_summary, "ExplanationBundle.operations_summary"), what_happened: string(explanation.what_happened, "ExplanationBundle.what_happened"), where_and_why: string(explanation.where_and_why, "ExplanationBundle.where_and_why"), recurrence_statement: nullableString(explanation.recurrence_statement, "ExplanationBundle.recurrence_statement"), evidence_ids: stringArray(explanation.evidence_ids, "ExplanationBundle.evidence_ids"), playbook_id: string(explanation.playbook_id, "ExplanationBundle.playbook_id"), recommended_action: string(explanation.recommended_action, "ExplanationBundle.recommended_action"), execution: "HUMAN_ONLY", limitations: stringArray(explanation.limitations, "ExplanationBundle.limitations"), model_version: string(explanation.model_version, "ExplanationBundle.model_version") };
}
