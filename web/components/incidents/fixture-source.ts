import type { ExplanationBundle, Incident, SimilarIncidentResult } from "@/lib/api/types";

export type IncidentFixtureMode = "default" | "inconclusive" | "no-precedent" | "memory-unavailable" | "error";

export interface OfflineIncidentDetail {
  incident: Incident;
  memory: SimilarIncidentResult;
  explanation: ExplanationBundle;
}

export class OfflineIncidentFixtureError extends Error {
  constructor(message: string) { super(message); this.name = "OfflineIncidentFixtureError"; }
}

/** Component-local snapshots of the frozen Incident and memory fixtures. */
const recurrenceFixture: Incident = {
  schema_version: "1.0", incident_id: "inc_current_mastercard_001", state: "SUPPORTED", detected_at: "2026-08-29T14:06:00Z", estimated_started_at: "2026-08-29T14:03:00Z", title: "Mastercard approval drop on Stripe in Brazil", scope: { provider_id: ["stripe"], country: ["BR"], card_brand: ["MASTERCARD"] }, metrics: { eligible_attempts: 492, lost_approvals: 162 }, root_cause: { status: "SUPPORTED", category: "PROVIDER_DEGRADATION", confidence: .93, confidence_factors: { statistical_strength: .97, loss_coverage: .91, temporal_consistency: .94, data_quality: .9 } }, impact: { metric: "GMV_AT_RISK", amount_minor: 2419000, currency: "BRL", method: "EXPECTED_APPROVAL_SHORTFALL" }, evidence: [{ evidence_id: "evd_current_rate", kind: "METRIC_SHIFT", statement: "Approval rate dropped from 84% to 51%.", source_ref: "duckdb://window/current" }, { evidence_id: "evd_current_scope", kind: "SLICE_CONCENTRATION", statement: "Stripe × Brazil × Mastercard explains most lost approvals.", source_ref: "duckdb://slice/provider-country-brand" }, { evidence_id: "evd_prior_confirmed", kind: "PAST_INCIDENT", statement: "Historical incident was human confirmed.", source_ref: "neo4j://incident/INC-HIST-002D-MASTERCARD" }], memory_matches: [], recommendations: [{ playbook_id: "PB-PROVIDER-DEGRADATION-001", action: "Validate provider health before any human rerouting.", execution: "HUMAN_ONLY", rationale_evidence_ids: ["evd_current_rate", "evd_current_scope", "evd_prior_confirmed"] }], limitations: ["Recurrence is contextual evidence, not proof."], correlation_id: "corr_inc_001",
};
const inconclusiveFixture: Incident = { ...recurrenceFixture, incident_id: "inc_current_mastercard_uncertain_002", state: "INCONCLUSIVE", title: "Diffuse Mastercard payment drop in Brazil", root_cause: { status: "INCONCLUSIVE", category: null, confidence: .42, confidence_factors: { statistical_strength: .55, loss_coverage: .38, temporal_consistency: .47, data_quality: .88 } }, evidence: [{ evidence_id: "evd_uncertain_current_rate", kind: "METRIC_SHIFT", statement: "Current approval rate declined.", source_ref: "duckdb://window/current-uncertain" }, { evidence_id: "evd_uncertain_low_coverage", kind: "LOW_CONCENTRATION", statement: "No current slice explains enough of the loss to support one cause.", source_ref: "duckdb://slice/current-uncertain" }, { evidence_id: "evd_prior_confirmed_uncertain", kind: "PAST_INCIDENT", statement: "Historical match may guide investigation.", source_ref: "neo4j://incident/INC-HIST-002D-MASTERCARD" }], recommendations: [{ playbook_id: "PB-PROVIDER-DEGRADATION-001", action: "Use the prior playbook only as an investigation checklist.", execution: "HUMAN_ONLY", rationale_evidence_ids: ["evd_uncertain_current_rate", "evd_uncertain_low_coverage", "evd_prior_confirmed_uncertain"] }], correlation_id: "corr_inc_uncertain_002" };
const memoryMatchFixture: SimilarIncidentResult = { schema_version: "1.1", query_incident_id: recurrenceFixture.incident_id, memory_status: "MATCH_FOUND", matches: [{ incident_id: "INC-HIST-002D-MASTERCARD", occurred_at: "2026-08-27T14:02:00Z", confirmation: "HUMAN_CONFIRMED", structured_score: .96, semantic_score: .91, matching_factors: ["provider_id", "country", "card_brand"], different_factors: ["merchant_scope"], confirmed_cause: "PROVIDER_DEGRADATION", prior_playbook_id: "PB-PROVIDER-DEGRADATION-001", evidence_ids: ["evd_prior_confirmed"] }], retrieval_trace: { cypher_filter: "confirmed incidents only", candidate_count: 3, embedding_model: "text-embedding-3-small", index_version: "incident-memory-v1", fallback_used: false }, correlation_id: "corr_inc_001" };
const memoryInconclusiveFixture: SimilarIncidentResult = { ...memoryMatchFixture, query_incident_id: inconclusiveFixture.incident_id, matches: [{ ...memoryMatchFixture.matches[0], structured_score: .84, semantic_score: .79, different_factors: ["provider_scope", "sample_size"], evidence_ids: ["evd_prior_confirmed_uncertain"] }], correlation_id: "corr_inc_uncertain_002" };
const memoryNoPrecedentFixture: SimilarIncidentResult = { ...memoryMatchFixture, query_incident_id: "inc_new_provider_country_001", memory_status: "NO_PRECEDENT", matches: [], retrieval_trace: { ...memoryMatchFixture.retrieval_trace, candidate_count: 0, embedding_model: null }, correlation_id: "corr_new_provider_country_001" };
const memoryUnavailableFixture: SimilarIncidentResult = { ...memoryMatchFixture, memory_status: "MEMORY_UNAVAILABLE", matches: [], retrieval_trace: { ...memoryMatchFixture.retrieval_trace, candidate_count: 0, embedding_model: null, fallback_used: true } };

const explanationFixture: ExplanationBundle = {
  schema_version: "1.0", incident_id: recurrenceFixture.incident_id, executive_summary: "Há BRL 24.190,00 de GMV estimado em risco em pagamentos Mastercard processados pela Stripe no Brasil.", operations_summary: "A approval rate caiu de 84% para 51%; o slice explica 91% das aprovações perdidas e a latência p95 subiu de 820 ms para 4.100 ms.", what_happened: "Approval rate e latência degradaram simultaneamente.", where_and_why: "O efeito está concentrado em Stripe × Brasil × Mastercard e é dominado por timeouts do provider.", recurrence_statement: "É uma recorrência provável do incidente humano confirmado INC-HIST-002D-MASTERCARD, ocorrido dois dias antes; provider, país, bandeira, declines e forma de latência coincidem, mas o escopo de merchants difere.", evidence_ids: ["evd_current_rate", "evd_current_scope", "evd_prior_confirmed"], playbook_id: "PB-PROVIDER-DEGRADATION-001", recommended_action: "Validar a saúde da conexão Stripe no Brasil e preparar rerouting humano para uma conexão alternativa.", execution: "HUMAN_ONLY", limitations: ["Similaridade histórica não substitui confirmação humana da causa atual."], model_version: "gpt-5.6-terra",
};
const inconclusiveExplanation: ExplanationBundle = {
  schema_version: "1.0", incident_id: inconclusiveFixture.incident_id, executive_summary: "Há BRL 1.940,00 de GMV estimado em risco; a causa atual ainda é inconclusiva, mas existe um precedente Mastercard semelhante de dois dias atrás.", operations_summary: "A approval rate Mastercard no Brasil caiu de 82% para 67% em 86 attempts. Nenhum slice atual explica mais de 38% da perda.", what_happened: "Há uma queda relevante de aprovação e aumento de latência em pagamentos Mastercard no Brasil.", where_and_why: "Os dados atuais não sustentam uma origem única entre provider, merchant e issuer; a causa corrente permanece INCONCLUSIVE.", recurrence_statement: "Existe um precedente humano confirmado de dois dias atrás com sinais semelhantes, mas diferenças de provider e amostra impedem afirmar a mesma causa.", evidence_ids: ["evd_uncertain_current_rate", "evd_uncertain_low_coverage", "evd_prior_confirmed_uncertain"], playbook_id: "PB-PROVIDER-DEGRADATION-001", recommended_action: "Usar o playbook anterior como checklist de investigação e confirmar a concentração antes de considerar rerouting humano.", execution: "HUMAN_ONLY", limitations: ["O precedente é evidência histórica de similaridade, não prova da causa atual.", "É necessário aumentar a amostra ou observar concentração para sustentar uma causa atual."], model_version: "deterministic-template",
};
const noPrecedentExplanation: ExplanationBundle = {
  schema_version: "1.0", incident_id: "inc_new_provider_country_001", executive_summary: "Há BRL 18.400,00 de GMV estimado em risco em pagamentos processados pelo provider_new no Brasil.", operations_summary: "A approval rate caiu de 82% para 58%; o slice provider_new × Brasil explica 88% das aprovações perdidas.", what_happened: "A taxa de aprovação caiu de forma estatisticamente relevante.", where_and_why: "O efeito atual está concentrado em provider_new × Brasil e é sustentado pelas métricas e códigos de recusa correntes.", recurrence_statement: null, evidence_ids: ["evd_current_rate_new", "evd_current_scope_new", "evd_current_declines_new"], playbook_id: "PB-PROVIDER-DEGRADATION-001", recommended_action: "Validar a saúde da conexão do provider_new no Brasil e comparar os códigos de recusa com uma conexão alternativa.", execution: "HUMAN_ONLY", limitations: ["Nenhum precedente histórico suficientemente semelhante foi encontrado."], model_version: "deterministic-template",
};

const noPrecedentIncident: Incident = {
  ...recurrenceFixture,
  incident_id: "inc_new_provider_country_001",
  title: "New provider-country degradation without a historical precedent",
  scope: { provider_id: ["provider_new"], country: ["BR"] },
  evidence: [{ evidence_id: "evd_current_rate_new", kind: "METRIC_SHIFT", statement: "Approval rate dropped from 82% to 58%.", source_ref: "duckdb://window/provider-new" }, { evidence_id: "evd_current_scope_new", kind: "SLICE_CONCENTRATION", statement: "provider_new × Brazil explains 88% of lost approvals.", source_ref: "duckdb://slice/provider-new-country" }, { evidence_id: "evd_current_declines_new", kind: "DECLINE_PROFILE", statement: "Current decline codes support the provider-country concentration.", source_ref: "duckdb://declines/provider-new" }],
  recommendations: [{ playbook_id: "PB-PROVIDER-DEGRADATION-001", action: "Validate provider_new health in Brazil and compare decline codes with an alternative connection.", execution: "HUMAN_ONLY", rationale_evidence_ids: ["evd_current_rate_new", "evd_current_scope_new", "evd_current_declines_new"] }],
  limitations: ["No sufficiently similar historical precedent was found."],
  correlation_id: "corr_new_provider_country_001",
};

export function normalizeIncidentFixture(value: string | undefined): IncidentFixtureMode {
  return value === "inconclusive" || value === "no-precedent" || value === "memory-unavailable" || value === "error"
    ? value
    : "default";
}

export async function listOfflineIncidents(): Promise<Incident[]> {
  return [recurrenceFixture, inconclusiveFixture, noPrecedentIncident];
}

export async function getOfflineIncident(
  incidentId: string,
  fixture: IncidentFixtureMode = "default",
): Promise<OfflineIncidentDetail> {
  if (fixture === "error") throw new OfflineIncidentFixtureError("The offline incident source is unavailable.");
  if (fixture === "inconclusive" || incidentId === inconclusiveFixture.incident_id) {
    return { incident: inconclusiveFixture, memory: memoryInconclusiveFixture, explanation: inconclusiveExplanation };
  }
  if (fixture === "no-precedent" || incidentId === noPrecedentIncident.incident_id) {
    return { incident: noPrecedentIncident, memory: memoryNoPrecedentFixture, explanation: noPrecedentExplanation };
  }
  if (fixture === "memory-unavailable") {
    return { incident: recurrenceFixture, memory: memoryUnavailableFixture, explanation: explanationFixture };
  }
  if (incidentId !== recurrenceFixture.incident_id) {
    throw new OfflineIncidentFixtureError(`Incident ${incidentId} is not available in the offline fixtures.`);
  }
  return { incident: recurrenceFixture, memory: memoryMatchFixture, explanation: explanationFixture };
}
