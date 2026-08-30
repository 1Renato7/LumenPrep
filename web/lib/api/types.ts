/**
 * Wire types mirrored from the frozen v1 JSON schemas under contracts/v1.
 * Request types intentionally exclude outcome, metrics, cause, ground truth,
 * PAN, CVV, and other public-input fields forbidden by CTR-TXN-001.
 */

export type TransactionSchemaVersion = "1.0";
export type IncidentSchemaVersion = "1.0";
export type MemorySchemaVersion = "1.1";

export type PaymentMethodCategory =
  | "CARD"
  | "PIX"
  | "BOLETO"
  | "SPEI"
  | "PSE"
  | "BANK_TRANSFER"
  | "DIGITAL_WALLET"
  | "CASH_IN_STORE"
  | "OTHER";
export type CardType = "CREDIT" | "DEBIT" | "PREPAID" | "NOT_APPLICABLE" | null;
export type TransactionChannel = "WEB" | "MOBILE" | "POS" | "API" | null;

export interface TransactionInput {
  client_reference?: string | null;
  occurred_at?: string | null;
  merchant_id: string;
  provider_id: string;
  issuer_bank: string;
  country: string;
  currency: string;
  amount_minor: number;
  payment_method_category: PaymentMethodCategory;
  card_brand?: string | null;
  card_type?: CardType;
  provider_connection_id?: string | null;
  provider_response_code?: string | null;
  channel?: TransactionChannel;
}

export interface TransactionCatalog {
  schema_version: TransactionSchemaVersion;
  max_batch_size: number;
  merchants: string[];
  providers: string[];
  issuer_banks: string[];
  countries: string[];
  currencies: string[];
  payment_method_categories: string[];
  card_brands: string[];
  card_types: string[];
  correlation_id: string;
}

export interface TransactionSampleRequest {
  schema_version: TransactionSchemaVersion;
  count: number;
  seed?: number | null;
  defaults?: {
    merchant_id?: string;
    country?: string;
    currency?: string;
  };
}

export interface TransactionSampleResponse {
  schema_version: TransactionSchemaVersion;
  seed: number;
  transactions: TransactionInput[];
  correlation_id: string;
}

export interface TransactionBatchRequest {
  schema_version: TransactionSchemaVersion;
  idempotency_key: string;
  transactions: TransactionInput[];
}

export interface TransactionBatchAccepted {
  schema_version: TransactionSchemaVersion;
  batch_id: string;
  accepted_at: string;
  status: "PROCESSING";
  transaction_ids: string[];
  correlation_id: string;
}

/** Result of the explicitly confirmed, admin-authorized synthetic-data reset. */
export interface TransactionDataResetResponse {
  schema_version: TransactionSchemaVersion;
  removed: {
    transaction_incident_links: number;
    incident_notifications: number;
    incident_suggestions: number;
    incident_records: number;
    transaction_records: number;
    transaction_batches: number;
    canonical_attempts: number;
    canonical_events: number;
    raw_events: number;
    quarantine: number;
  };
  correlation_id: string;
}

export type LiveDemoTrialId = "deterministic" | "graph_enriched";
export type LiveDemoTrialFlow = "DETERMINISTIC" | "GRAPH_ENRICHED";

export interface LiveDemoTrial {
  trial_id: LiveDemoTrialId;
  flow: LiveDemoTrialFlow;
  title: string;
  description: string;
  transaction_count: 25;
}

export interface LiveDemoTrialAvailability {
  schema_version: TransactionSchemaVersion;
  enabled: boolean;
  reason: string | null;
  execution_mode: "QUEUED_SAFE";
  trials: LiveDemoTrial[];
}

export interface LiveDemoTrialAccepted extends TransactionBatchAccepted {
  trial_id: LiveDemoTrialId;
  flow: LiveDemoTrialFlow;
  execution_mode: "QUEUED_SAFE";
  baseline_batch_ids: string[];
}

export type TransactionStatus = "PROCESSING" | "SUCCEEDED" | "FAILED" | "UNKNOWN";
export type ProcessingStage =
  | "RECEIVED"
  | "NORMALIZING"
  | "CLASSIFYING"
  | "AGGREGATING"
  | "ANALYZING"
  | "COMPLETE"
  | "PIPELINE_FAILED";
export type OutcomeResult = "SUCCEEDED" | "FAILED" | "UNKNOWN";
export type ClassificationCategory =
  | "APPROVED"
  | "ISSUER_DECLINE"
  | "PROVIDER_ERROR"
  | "TIMEOUT"
  | "DATA_QUALITY"
  | "UNKNOWN";

export interface TransactionProcessing {
  stage: ProcessingStage;
  progress_percent: number;
  failure_code?: string | null;
}

export interface TransactionOutcome {
  result: OutcomeResult;
  provider_response_code: string | null;
  normalized_decline_code: string | null;
  latency_ms: number;
}

export interface TransactionClassification {
  category: ClassificationCategory;
  reason: string;
  confidence: number;
  evidence_ids: string[];
  related_incident_ids: string[];
  related_incidents?: Array<{
    incident_id: string;
    recurrence_first_detected_at: string | null;
  }>;
  refusal_resolution?: RefusalCodeResolution;
}

export interface RefusalCodeResolution {
  lookup_status: "MATCH_FOUND" | "NOT_FOUND" | "AMBIGUOUS";
  provider_id: string;
    issuer_bank: string;
    card_brand: string;
    response_code: string;
    observed_response_code: string;
    outcome: OutcomeResult;
  normalized_code: string | null;
  reason: string | null;
  source: string | null;
  mapping_version: string | null;
}

export interface HumanReviewRequest {
  schema_version: "1.0";
  review_id: string;
  reviewer_id: string;
  decision: "APPROVED" | "REJECTED";
  reason: string;
  confirmed_cause?: string | null;
  playbook_id?: string | null;
}

export interface HumanReviewResponse {
  schema_version: "1.0";
  review: {
    review_id: string;
    incident_id: string;
    decision: "APPROVED" | "REJECTED";
    reviewer_id: string;
    reason: string;
    confirmed_cause: string | null;
    playbook_id: string | null;
    reviewed_at: string;
  };
  promoted_to_memory: boolean;
}

export interface TransactionRecord {
  schema_version: TransactionSchemaVersion;
  transaction_id: string;
  batch_id: string;
  created_at: string;
  updated_at: string;
  status: TransactionStatus;
  input: TransactionInput;
  processing: TransactionProcessing;
  outcome: TransactionOutcome | null;
  classification: TransactionClassification | null;
  correlation_id: string;
}

export interface TransactionList {
  schema_version: TransactionSchemaVersion;
  items: TransactionRecord[];
  next_cursor: string | null;
  correlation_id: string;
}

export type IncidentState =
  | "DETECTED"
  | "INVESTIGATING"
  | "SUPPORTED"
  | "INCONCLUSIVE"
  | "RECOVERED"
  | "HUMAN_CONFIRMED"
  | "CLOSED";

export interface Incident {
  schema_version: IncidentSchemaVersion;
  incident_id: string;
  state: IncidentState;
  detected_at: string;
  estimated_started_at: string;
  recurrence_first_detected_at?: string | null;
  title: string;
  scope: Record<string, string[]>;
  /** CTR-INC-001 permits scalar metrics and string dimensions such as decline codes. */
  metrics: Record<string, number | string | string[] | null>;
  root_cause: {
    status: "SUPPORTED" | "INCONCLUSIVE";
    category: string | null;
    confidence: number;
    confidence_factors: Record<string, number>;
    alternatives?: Array<{
      category: string;
      confidence: number;
    }>;
  };
  impact: {
    metric: "GMV_AT_RISK";
    amount_minor: number;
    currency: string;
    method: "EXPECTED_APPROVAL_SHORTFALL";
    lower_bound_minor?: number | null;
    upper_bound_minor?: number | null;
  };
  evidence: Array<{
    evidence_id: string;
    kind: string;
    statement: string;
    source_ref: string;
  }>;
  memory_matches?: object[];
  recommendations: Array<{
    playbook_id: string;
    action: string;
    recommendation_class?: "INVESTIGATE" | "MONITOR" | "ESCALATE";
    execution: "HUMAN_ONLY";
    rationale_evidence_ids: string[];
  }>;
  limitations: string[];
  correlation_id: string;
}

export interface SimilarIncidentResult {
  schema_version: MemorySchemaVersion;
  query_incident_id: string;
  memory_status: "MATCH_FOUND" | "NO_PRECEDENT" | "MEMORY_UNAVAILABLE";
  matches: Array<{
    incident_id: string;
    occurred_at: string;
    confirmation: "HUMAN_CONFIRMED";
    structured_score: number;
    semantic_score?: number | null;
    matching_factors: string[];
    different_factors: string[];
    confirmed_cause: string;
    prior_playbook_id: string;
    evidence_ids: string[];
  }>;
  retrieval_trace: {
    cypher_filter: string;
    candidate_count: number;
    embedding_model: string | null;
    index_version: string;
    fallback_used: boolean;
  };
  correlation_id: string;
}

export interface ExplanationBundle {
  schema_version: IncidentSchemaVersion;
  incident_id: string;
  executive_summary: string;
  operations_summary: string;
  what_happened: string;
  where_and_why: string;
  recurrence_statement: string | null;
  evidence_ids: string[];
  playbook_id: string;
  recommended_action: string;
  execution: "HUMAN_ONLY";
  limitations: string[];
  model_version: string;
}

export interface IncidentDetail {
  incident: Incident;
  memory: SimilarIncidentResult;
  explanation: ExplanationBundle;
}

/** CTR-AGT-003: a read-only, non-authoritative investigation hypothesis. */
export interface DiagnosticSuggestion {
  schema_version: "1.0";
  incident_id: string;
  evidence_fingerprint: string;
  status: "SUGGESTED" | "INSUFFICIENT_EVIDENCE" | "UNAVAILABLE";
  suggested_category: string | null;
  summary_for_operations: string;
  executive_summary: string;
  reasons: Array<{ statement: string; evidence_ids: string[] }>;
  confidence: number;
  recommended_actions: Array<{ action: string; execution: "HUMAN_ONLY"; rationale_evidence_ids: string[] }>;
  limitations: string[];
  retrieval_trace: Record<string, unknown>;
  model_version: string;
}

export interface TransactionIncidentLink extends IncidentDetail {
  evidence_ids: string[];
  limitations: string[];
}

/** CTR-TDI-001: grounded Incident detail authorized for one transaction. */
export interface TransactionIncidentDetail {
  schema_version: TransactionSchemaVersion;
  transaction_id: string;
  status: "RESOLVED" | "PARTIAL" | "NO_INCIDENT";
  incidents: TransactionIncidentLink[];
  rejected_incident_ids: string[];
  limitations: string[];
}

/** CTR-NOT-001: backend-owned read state for the in-app Incident feed. */
export interface IncidentNotification {
  notification_id: string;
  incident_id: string;
  created_at: string;
  read_at: string | null;
  incident: Incident;
}

export interface NotificationFeed {
  notifications: IncidentNotification[];
  unread_count: number;
}
