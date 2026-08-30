import batchAcceptedFixture from "../../../contracts/fixtures/transaction-batch-accepted.json";
import catalogFixture from "../../../contracts/fixtures/transaction-catalog.json";
import failedFixture from "../../../contracts/fixtures/transaction-failed.json";
import incidentFixture from "../../../contracts/fixtures/incident-mastercard-recurrence.json";
import explanationFixture from "../../../contracts/fixtures/explanation-bundle.json";
import listFixture from "../../../contracts/fixtures/transaction-list.json";
import processingFixture from "../../../contracts/fixtures/transaction-processing.json";
import sampleFixture from "../../../contracts/fixtures/transaction-sample-response.json";
import similarIncidentsFixture from "../../../contracts/fixtures/similar-incidents.json";
import succeededFixture from "../../../contracts/fixtures/transaction-succeeded.json";

import {
  LumenApiError,
  type ListTransactionsQuery,
  type LumenApiClient,
  type RequestOptions,
} from "../api/client-interface";
import {
  parseIncident,
  parseIncidentDetail,
  parseTransactionBatchAccepted,
  parseTransactionCatalog,
  parseTransactionList,
  parseTransactionRecord,
  parseTransactionSampleResponse,
} from "../api/parse";
import type { TransactionList } from "../api/types";

export interface MockLumenApiClient extends LumenApiClient {
  /** Makes fixture usage visible to the route or demo harness; it is never selected by the live client. */
  readonly source: "MOCK_FIXTURE";
}

/**
 * Explicit offline/demo adapter. Consumers keep the LumenApiClient interface, while the
 * source marker prevents a fixture from being mistaken for a Railway response.
 */
export function createMockLumenApiClient(): MockLumenApiClient {
  const processing = parseTransactionRecord(processingFixture);
  const succeeded = parseTransactionRecord(succeededFixture);
  const failed = parseTransactionRecord(failedFixture);
  const incident = parseIncident(incidentFixture);
  const incidentDetail = parseIncidentDetail({ incident: incidentFixture, memory: similarIncidentsFixture, explanation: explanationFixture });

  return {
    source: "MOCK_FIXTURE",
    async getTransactionCatalog(options) {
      checkCancelled(options);
      return parseTransactionCatalog(catalogFixture);
    },
    async generateTransactionSamples(request, options) {
      checkCancelled(options);
      const fixture = structuredClone(sampleFixture);
      const seed = request.seed ?? fixture.seed;
      fixture.seed = seed;
      fixture.transactions = Array.from({ length: request.count }, (_unused, index) => {
        const template = structuredClone(sampleFixture.transactions[index % sampleFixture.transactions.length]);
        return {
          ...template,
          ...request.defaults,
          client_reference: `sample-${seed}-${index + 1}`,
        };
      });
      return parseTransactionSampleResponse(fixture);
    },
    async createTransactionBatch(_request, options) {
      checkCancelled(options);
      return parseTransactionBatchAccepted(batchAcceptedFixture);
    },
    async getTransactionBatch(_batchId, options) {
      checkCancelled(options);
      return listWith([processing]);
    },
    async listTransactions(query, options) {
      checkCancelled(options);
      const records = [processing, succeeded, failed].filter((record) => !query?.status || record.status === query.status);
      return listWith(records, query);
    },
    async getTransaction(transactionId, options) {
      checkCancelled(options);
      const record = [processing, succeeded, failed].find((item) => item.transaction_id === transactionId);
      if (!record) throw new LumenApiError("NOT_FOUND", 404, { correlation_id: "corr_demo_mock_not_found" }, "Transaction fixture was not found.");
      return structuredClone(record);
    },
    async listIncidents(options) {
      checkCancelled(options);
      return [structuredClone(incident)];
    },
    async listTransactionIncidents(transactionId, options) {
      checkCancelled(options);
      if (transactionId === "missing") {
        return { schema_version: "1.0", transaction_id: transactionId, status: "NO_INCIDENT", incidents: [], rejected_incident_ids: [], limitations: [] };
      }
      return {
        schema_version: "1.0",
        transaction_id: transactionId,
        status: "RESOLVED",
        incidents: [{ ...structuredClone(incidentDetail), evidence_ids: incident.evidence.map((item) => item.evidence_id), limitations: [] }],
        rejected_incident_ids: [],
        limitations: [],
      };
    },
    async getIncident(incidentId, options) {
      checkCancelled(options);
      if (incidentId !== incident.incident_id) throw new LumenApiError("NOT_FOUND", 404, { correlation_id: "corr_demo_mock_not_found" }, "Incident fixture was not found.");
      return structuredClone(incidentDetail);
    },
  };
}

function listWith(items: TransactionList["items"], query?: ListTransactionsQuery): TransactionList {
  const fixture = structuredClone(listFixture) as unknown as {
    schema_version: unknown;
    items: unknown;
    next_cursor: unknown;
    correlation_id: unknown;
  };
  fixture.items = structuredClone(items);
  if (query?.cursor) fixture.next_cursor = null;
  return parseTransactionList(fixture);
}

function checkCancelled(options: RequestOptions | undefined): void {
  if (options?.signal?.aborted) throw new LumenApiError("CANCELLED", null, null, "Mock API request was cancelled.");
}
