import assert from "node:assert/strict";
import test from "node:test";

import { formatMetricValue } from "../../lib/format/metric";

import batchAcceptedFixture from "../../../contracts/fixtures/transaction-batch-accepted.json";
import catalogFixture from "../../../contracts/fixtures/transaction-catalog.json";
import explanationFixture from "../../../contracts/fixtures/explanation-bundle.json";
import incidentFixture from "../../../contracts/fixtures/incident-mastercard-recurrence.json";
import listFixture from "../../../contracts/fixtures/transaction-list.json";
import processingFixture from "../../../contracts/fixtures/transaction-processing.json";
import sampleFixture from "../../../contracts/fixtures/transaction-sample-response.json";
import similarIncidentsFixture from "../../../contracts/fixtures/similar-incidents.json";
import succeededFixture from "../../../contracts/fixtures/transaction-succeeded.json";
import noIncidentFixture from "../../../contracts/fixtures/transaction-incident-detail-no-incident.json";
import humanReviewFixture from "../../../contracts/fixtures/human-review-request-approved.json";
import {
  backendStateFor,
  createBatchSubmission,
  createLumenApiClient,
  createPollingController,
  LumenApiError,
  normalizeApiBaseUrl,
  pollTransaction,
  pollTransactions,
  type LumenApiClient,
} from "../../lib/api/client-interface";
import { createMockLumenApiClient } from "../../lib/mocks/transaction-api-client";
import { parseDiagnosticSuggestion, parseIncident, parseTransactionInput, parseTransactionRecord } from "../../lib/api/parse";
import type { HumanReviewRequest, TransactionBatchRequest, TransactionList } from "../../lib/api/types";

const batchRequest: TransactionBatchRequest = {
  schema_version: "1.0",
  idempotency_key: "idem-key-123",
  transactions: [{ merchant_id: "merchant_br_01", provider_id: "provider_alpha", issuer_bank: "bank_br_a", country: "BR", currency: "BRL", amount_minor: 100, payment_method_category: "CARD" }],
};

test("accepts every payment method exposed by the expanded transaction catalog", () => {
  for (const paymentMethod of ["PIX", "BOLETO", "SPEI", "PSE", "CASH_IN_STORE"] as const) {
    const transaction = parseTransactionInput({
      merchant_id: "merchant_br_aurora",
      provider_id: "stripe",
      issuer_bank: "NOT_APPLICABLE",
      country: "BR",
      currency: "BRL",
      amount_minor: 100,
      payment_method_category: paymentMethod,
    });
    assert.equal(transaction.payment_method_category, paymentMethod);
  }
});

test("agent hypotheses reject untrusted action execution and remain a separate read model", () => {
  const valid = {
    schema_version: "1.0", incident_id: "inc_1", evidence_fingerprint: "fingerprint", status: "SUGGESTED", suggested_category: "PROVIDER_DEGRADATION",
    summary_for_operations: "Investigate the provider.", executive_summary: "A hypothesis only.", reasons: [{ statement: "Current evidence supports investigation.", evidence_ids: ["evd_1"] }], confidence: 0.5,
    recommended_actions: [{ action: "Validate provider health.", execution: "HUMAN_ONLY", rationale_evidence_ids: ["evd_1"] }], limitations: [], retrieval_trace: {}, model_version: "deterministic-template-v1",
  };
  assert.equal(parseDiagnosticSuggestion(valid).suggested_category, "PROVIDER_DEGRADATION");
  assert.throws(() => parseDiagnosticSuggestion({ ...valid, recommended_actions: [{ ...valid.recommended_actions[0], execution: "AUTOMATIC" }] }));
});

function json(body: unknown, status = 200): Response {
  return Response.json(body, { status });
}

test("normalizes public base URL and follows every CTR-API-001 v3 path/query", async () => {
  const calls: string[] = [];
  const resolvedTransactionIncident = {
    schema_version: "1.0",
    transaction_id: "txn one",
    status: "RESOLVED",
    incidents: [{ incident: incidentFixture, memory: similarIncidentsFixture, explanation: explanationFixture, evidence_ids: ["evt_demo_1001_final"], limitations: [] }],
    rejected_incident_ids: [],
    limitations: [],
  };
  const diagnosticSuggestion = {
    schema_version: "1.0",
    incident_id: "incident/one",
    evidence_fingerprint: "test-fingerprint",
    status: "SUGGESTED",
    suggested_category: "PROVIDER_DEGRADATION",
    summary_for_operations: "Investigate the provider connection.",
    executive_summary: "An agent hypothesis, not an engine cause.",
    reasons: [{ statement: "Current evidence supports this investigation.", evidence_ids: ["evd_1"] }],
    confidence: 0.7,
    recommended_actions: [{ action: "Validate provider health.", execution: "HUMAN_ONLY", rationale_evidence_ids: ["evd_1"] }],
    limitations: ["This remains a hypothesis."],
    retrieval_trace: { status: "NO_PRECEDENT" },
    model_version: "deterministic-template-v1",
  };
  const client = createLumenApiClient({
    baseUrl: " https://api.example.test/v1/// ",
    fetchImpl: async (url, init) => {
      const requestUrl = String(url);
      calls.push(`${init?.method ?? "GET"} ${requestUrl}`);
      if (requestUrl.includes("transaction-catalog")) return json(catalogFixture);
      if (requestUrl.includes("transaction-samples")) return json(sampleFixture);
      if (requestUrl.endsWith("transaction-batches")) return json(batchAcceptedFixture, 202);
      if (requestUrl.includes("transaction-batches/")) return json(listFixture);
      if (requestUrl.endsWith("transactions/txn%20one/incidents")) return json(resolvedTransactionIncident);
      if (requestUrl.endsWith("/incidents")) return json([incidentFixture]);
      if (requestUrl.endsWith("/incidents/incident%2Fone/suggestion")) return json(diagnosticSuggestion);
      if (requestUrl.includes("transactions?")) return json(listFixture);
      if (requestUrl.includes("transactions/")) return json(processingFixture);
      return json({ incident: incidentFixture, memory: similarIncidentsFixture, explanation: explanationFixture });
    },
  });

  await client.getTransactionCatalog();
  await client.generateTransactionSamples({ schema_version: "1.0", count: 1 });
  await client.createTransactionBatch(batchRequest);
  await client.getTransactionBatch("batch/one");
  await client.listTransactions({ status: "PROCESSING", cursor: "cursor one", limit: 20 });
  await client.getTransaction("txn/one");
  await client.listIncidents();
  const incidentDetails = await client.listTransactionIncidents("txn one");
  await client.getIncident("incident/one");
  const suggestion = await client.getDiagnosticSuggestion("incident/one");

  assert.deepEqual(calls, [
    "GET https://api.example.test/v1/transaction-catalog",
    "POST https://api.example.test/v1/transaction-samples",
    "POST https://api.example.test/v1/transaction-batches",
    "GET https://api.example.test/v1/transaction-batches/batch%2Fone",
    "GET https://api.example.test/v1/transactions?status=PROCESSING&cursor=cursor+one&limit=20",
    "GET https://api.example.test/v1/transactions/txn%2Fone",
    "GET https://api.example.test/v1/incidents",
    "GET https://api.example.test/v1/transactions/txn%20one/incidents",
    "GET https://api.example.test/v1/incidents/incident%2Fone",
    "GET https://api.example.test/v1/incidents/incident%2Fone/suggestion",
  ]);
  assert.deepEqual(incidentDetails.incidents[0].incident.root_cause.alternatives, [{ category: "ISSUER_DECLINE", confidence: 0.18 }]);
  assert.equal(incidentDetails.incidents[0].incident.recommendations[0].recommendation_class, "ESCALATE");
  assert.equal(suggestion.status, "SUGGESTED");
  assert.equal(normalizeApiBaseUrl("https://api.example.test/v1///"), "https://api.example.test/v1");
});

test("accepts string-array incident metrics allowed by CTR-INC-001", () => {
  const incident = parseIncident({
    ...incidentFixture,
    metrics: {
      ...incidentFixture.metrics,
      decline_codes: ["DO_NOT_HONOR", "INSUFFICIENT_FUNDS", "SUSPECTED_FRAUD"],
    },
  });

  assert.deepEqual(incident.metrics.decline_codes, ["DO_NOT_HONOR", "INSUFFICIENT_FUNDS", "SUSPECTED_FRAUD"]);
  assert.equal(formatMetricValue(incident.metrics.decline_codes), "DO_NOT_HONOR, INSUFFICIENT_FUNDS, SUSPECTED_FRAUD");
});

test("formats decimal incident metrics with two decimal places", () => {
  assert.equal(formatMetricValue(0.928374), "0,93");
  assert.equal(formatMetricValue("0.928374"), "0,93");
  assert.equal(formatMetricValue(492), "492");
});

test("submits CTR-HRV-001 to the incident review route and parses its audit response", async () => {
  let requestUrl = "";
  let requestBody = "";
  const client = createLumenApiClient({
    baseUrl: "https://api.example.test/v1",
    fetchImpl: async (url, init) => {
      requestUrl = String(url);
      requestBody = String(init?.body);
      return json({
        schema_version: "1.0",
        promoted_to_memory: true,
        review: {
          review_id: humanReviewFixture.review_id,
          incident_id: "incident/one",
          decision: "APPROVED",
          reviewer_id: humanReviewFixture.reviewer_id,
          reason: humanReviewFixture.reason,
          confirmed_cause: humanReviewFixture.confirmed_cause,
          playbook_id: humanReviewFixture.playbook_id,
          reviewed_at: "2026-08-30T12:00:00Z",
        },
      }, 201);
    },
  });

  const reviewRequest = humanReviewFixture as HumanReviewRequest;
  const response = await client.submitHumanReview("incident/one", reviewRequest);

  assert.equal(requestUrl, "https://api.example.test/v1/incidents/incident%2Fone/review");
  assert.deepEqual(JSON.parse(requestBody), reviewRequest);
  assert.equal(response.review.reason, reviewRequest.reason);
  assert.equal(response.promoted_to_memory, true);
});

test("submit preserves Idempotency-Key and an explicit retry reuses its original payload", async () => {
  const headers: string[] = [];
  const bodies: string[] = [];
  let attempts = 0;
  const client = createLumenApiClient({
    baseUrl: "https://api.example.test/v1",
    fetchImpl: async (_url, init) => {
      headers.push(new Headers(init?.headers).get("Idempotency-Key") ?? "");
      bodies.push(String(init?.body));
      attempts += 1;
      return attempts === 1 ? json({ correlation_id: "corr-retry" }, 503) : json(batchAcceptedFixture, 202);
    },
  });
  const submission = createBatchSubmission(client, batchRequest);
  batchRequest.transactions[0].amount_minor = 999; // A later form edit must not alter the retry snapshot.

  await assert.rejects(submission.submit(), (error: unknown) => error instanceof LumenApiError && error.code === "SERVICE_UNAVAILABLE" && backendStateFor(error) === "BACKEND_UNAVAILABLE");
  await submission.submit();
  assert.equal(submission.idempotencyKey, "idem-key-123");
  assert.deepEqual(headers, ["idem-key-123", "idem-key-123"]);
  assert.deepEqual(bodies, [bodies[0], bodies[0]]);
  batchRequest.transactions[0].amount_minor = 100;
});

test("admin reset sends its key only in the reset request and parses deletion counts", async () => {
  let seenUrl = "";
  let seenHeaders: Headers | undefined;
  let seenBody = "";
  const client = createLumenApiClient({
    baseUrl: "https://api.example.test/v1",
    fetchImpl: async (url, init) => {
      seenUrl = String(url);
      seenHeaders = new Headers(init?.headers);
      seenBody = String(init?.body);
      return json({
        schema_version: "1.0",
        removed: {
          transaction_incident_links: 1, incident_notifications: 2, incident_suggestions: 3, incident_records: 4,
          transaction_records: 5, transaction_batches: 6, canonical_attempts: 7, canonical_events: 8,
          raw_events: 9, quarantine: 10,
        },
        correlation_id: "corr-reset",
      });
    },
  });

  const result = await client.resetTransactionData("operator-secret");
  assert.equal(seenUrl, "https://api.example.test/v1/admin/transaction-data/reset");
  assert.equal(seenHeaders?.get("X-Lumen-Admin-Key"), "operator-secret");
  assert.equal(seenBody, '{"confirmation":"DELETE_SYNTHETIC_TRANSACTION_DATA"}');
  assert.equal(result.removed.transaction_records, 5);
  assert.equal(result.correlation_id, "corr-reset");
});

test("different payload with the same key remains a typed 409 conflict", async () => {
  let calls = 0;
  const client = createLumenApiClient({
    baseUrl: "https://api.example.test/v1",
    fetchImpl: async () => (calls++ === 0 ? json(batchAcceptedFixture, 202) : json({ correlation_id: "corr-conflict" }, 409)),
  });
  await client.createTransactionBatch(batchRequest);
  await assert.rejects(
    client.createTransactionBatch({ ...batchRequest, transactions: [{ ...batchRequest.transactions[0], amount_minor: 101 }] }),
    (error: unknown) => error instanceof LumenApiError && error.code === "CONFLICT" && error.status === 409 && error.correlationId === "corr-conflict",
  );
});

test("404/409/422/503, timeout, abort and unavailable configuration are typed", async () => {
  for (const [status, code] of [[404, "NOT_FOUND"], [409, "CONFLICT"], [422, "VALIDATION"], [503, "SERVICE_UNAVAILABLE"]] as const) {
    const client = createLumenApiClient({ baseUrl: "https://api.example.test/v1", fetchImpl: async () => json({ correlation_id: "corr-error" }, status) });
    await assert.rejects(client.getTransaction("txn_1"), (error: unknown) => error instanceof LumenApiError && error.code === code && error.status === status && error.correlationId === "corr-error");
  }
  const timedOut = createLumenApiClient({
    baseUrl: "https://api.example.test/v1", defaultTimeoutMs: 5,
    fetchImpl: async (_url, init) => new Promise<Response>((_resolve, reject) => init?.signal?.addEventListener("abort", () => reject(new DOMException("Aborted", "AbortError")))),
  });
  await assert.rejects(timedOut.getTransactionCatalog(), (error: unknown) => error instanceof LumenApiError && error.code === "TIMEOUT" && backendStateFor(error) === "BACKEND_UNAVAILABLE");

  const controller = new AbortController();
  const aborted = createLumenApiClient({
    baseUrl: "https://api.example.test/v1",
    fetchImpl: async (_url, init) => new Promise<Response>((_resolve, reject) => init?.signal?.addEventListener("abort", () => reject(new DOMException("Aborted", "AbortError")))),
  });
  const request = aborted.getTransactionCatalog({ signal: controller.signal });
  controller.abort();
  await assert.rejects(request, (error: unknown) => error instanceof LumenApiError && error.code === "CANCELLED");
  assert.throws(() => createLumenApiClient({ baseUrl: "" }), (error: unknown) => error instanceof LumenApiError && error.code === "BACKEND_UNAVAILABLE");
});

test("unknown response properties are rejected rather than cast silently", async () => {
  const invalidCatalog = { ...catalogFixture, unexpected: "not part of CTR-TXN-001" };
  const client = createLumenApiClient({ baseUrl: "https://api.example.test/v1", fetchImpl: async () => json(invalidCatalog) });
  await assert.rejects(client.getTransactionCatalog(), (error: unknown) => error instanceof LumenApiError && error.code === "INVALID_RESPONSE");
});

test("parses the normalized code preserved in a refusal resolution", () => {
  const record = parseTransactionRecord({
    ...processingFixture,
    status: "FAILED",
    processing: { stage: "COMPLETE", progress_percent: 100, failure_code: null },
    outcome: { result: "FAILED", provider_response_code: "4", normalized_decline_code: "ACQUIRER_ERROR", latency_ms: 42 },
    classification: {
      category: "PROVIDER_ERROR", reason: "Acquirer error", confidence: 1, evidence_ids: ["evt_acquirer"], related_incident_ids: [],
      refusal_resolution: { lookup_status: "MATCH_FOUND", provider_id: "ADYEN", issuer_bank: "NUBANK_BR", card_brand: "VISA", response_code: "4", observed_response_code: "4", outcome: "FAILED", normalized_code: "ACQUIRER_ERROR", reason: "Acquirer error", source: "ADYEN_REFUSAL_REASON", mapping_version: "2026.08.30" },
    },
  });
  assert.equal(record.classification?.category, "PROVIDER_ERROR");
  assert.equal(record.classification?.refusal_resolution?.normalized_code, "ACQUIRER_ERROR");
});

test("CTR-TDI-001 parses NO_INCIDENT and rejects invalid status invariants and duplicate IDs", async () => {
  const valid = createLumenApiClient({ baseUrl: "https://api.example.test/v1", fetchImpl: async () => json(noIncidentFixture) });
  const result = await valid.listTransactionIncidents("txn_missing");
  assert.equal(result.status, "NO_INCIDENT");
  assert.deepEqual(result.incidents, []);

  for (const invalid of [
    { ...noIncidentFixture, status: "RESOLVED" },
    { ...noIncidentFixture, status: "NOT_A_STATUS" },
    { ...noIncidentFixture, rejected_incident_ids: ["inc_1", "inc_1"] },
    { ...noIncidentFixture, unexpected: true },
  ]) {
    const client = createLumenApiClient({ baseUrl: "https://api.example.test/v1", fetchImpl: async () => json(invalid) });
    await assert.rejects(client.listTransactionIncidents("txn_missing"), (error: unknown) => error instanceof LumenApiError && error.code === "INVALID_RESPONSE");
  }
});

test("transaction lifecycle parser rejects FAILED without classification", async () => {
  const invalid = { ...succeededFixture, status: "FAILED", outcome: { ...succeededFixture.outcome, result: "FAILED" }, classification: null };
  const client = createLumenApiClient({ baseUrl: "https://api.example.test/v1", fetchImpl: async () => json(invalid) });
  await assert.rejects(client.getTransaction("txn_invalid"), (error: unknown) => error instanceof LumenApiError && error.code === "INVALID_RESPONSE");
});

test("polling ends without PROCESSING and cancellation stops the pending next poll", async () => {
  const processingList = { ...listFixture, items: [processingFixture] } as TransactionList;
  const terminalList = { ...listFixture, items: [succeededFixture] } as TransactionList;
  let calls = 0;
  const client = { listTransactions: async () => (++calls === 1 ? processingList : terminalList) } as LumenApiClient;
  const updates: string[] = [];
  const result = await pollTransactions(client, { intervalMs: 0, onUpdate: (list) => { updates.push(list.items[0].status); } });
  assert.equal(calls, 2);
  assert.deepEqual(updates, ["PROCESSING", "SUCCEEDED"]);
  assert.equal(result.items[0].status, "SUCCEEDED");

  const polling = createPollingController();
  const foreverProcessing = { listTransactions: async () => processingList } as LumenApiClient;
  await assert.rejects(
    pollTransactions(foreverProcessing, { signal: polling.signal, intervalMs: 100, onUpdate: () => polling.cancel("navigation") }),
    (error: unknown) => error instanceof LumenApiError && error.code === "CANCELLED",
  );
});

test("polling one transaction and one submitted batch use their dedicated endpoints", async () => {
  let recordCalls = 0;
  const single = {
    getTransaction: async () => (++recordCalls === 1 ? processingFixture : succeededFixture),
  } as unknown as LumenApiClient;
  const record = await pollTransaction(single, "txn_1", { intervalMs: 0 });
  assert.equal(record.status, "SUCCEEDED");
  assert.equal(recordCalls, 2);

  let batchCalls = 0;
  const batch = {
    getTransactionBatch: async (batchId: string) => {
      assert.equal(batchId, "batch_1");
      batchCalls += 1;
      return { ...listFixture, items: [succeededFixture] } as TransactionList;
    },
    listTransactions: async () => assert.fail("batch polling must not use the global transaction list"),
  } as unknown as LumenApiClient;
  await pollTransactions(batch, { batchId: "batch_1", intervalMs: 0 });
  assert.equal(batchCalls, 1);
});

test("a request cancelled before dispatch fails without calling fetch", async () => {
  const controller = new AbortController();
  controller.abort("navigation");
  let called = false;
  const client = createLumenApiClient({ baseUrl: "https://api.example.test/v1", fetchImpl: async () => { called = true; return json(catalogFixture); } });
  await assert.rejects(client.getTransactionCatalog({ signal: controller.signal }), (error: unknown) => error instanceof LumenApiError && error.code === "CANCELLED");
  assert.equal(called, false);
});

test("the explicitly labelled mock and live adapters share the same consumer interface", async () => {
  const mock = createMockLumenApiClient();
  const live = createLumenApiClient({ baseUrl: "https://api.example.test/v1", fetchImpl: async () => json(catalogFixture) });
  const consumer = async (client: LumenApiClient) => (await client.getTransactionCatalog()).correlation_id;
  assert.equal(mock.source, "MOCK_FIXTURE");
  assert.equal(await consumer(mock), "corr_demo_catalog_0001");
  assert.equal(await consumer(live), "corr_demo_catalog_0001");
});

test("the mock generates the requested 1..100 editable inputs deterministically", async () => {
  const mock = createMockLumenApiClient();
  const first = await mock.generateTransactionSamples({
    schema_version: "1.0",
    count: 100,
    seed: 42,
    defaults: { merchant_id: "merchant_br_01", country: "BR", currency: "BRL" },
  });
  const second = await mock.generateTransactionSamples({ schema_version: "1.0", count: 100, seed: 42 });

  assert.equal(first.transactions.length, 100);
  assert.equal(first.seed, 42);
  assert.equal(first.transactions[0].client_reference, "sample-42-1");
  assert.equal(first.transactions[99].client_reference, "sample-42-100");
  assert.deepEqual(first.transactions, second.transactions);
});
