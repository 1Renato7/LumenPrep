import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import test from "node:test";

import { createLumenApiClient, pollTransactions } from "../../lib/api/client-interface";

const baseUrl = process.env.LUMEN_API_TEST_BASE_URL;

test("live FastAPI supports the frontend transaction and incident journey", { skip: !baseUrl, timeout: 15_000 }, async () => {
  const client = createLumenApiClient({ baseUrl });
  const catalog = await client.getTransactionCatalog();
  assert.equal(catalog.schema_version, "1.0");

  const samples = await client.generateTransactionSamples({ schema_version: "1.0", count: 2, seed: 20260830 });
  const accepted = await client.createTransactionBatch({
    schema_version: "1.0",
    idempotency_key: `web-live-${randomUUID()}`,
    transactions: samples.transactions,
  });
  assert.equal(accepted.transaction_ids.length, 2);

  const batch = await pollTransactions(client, { batchId: accepted.batch_id, intervalMs: 50 });
  assert.equal(batch.items.length, 2);
  assert.equal(batch.items.some((record) => record.status === "PROCESSING"), false);

  const detail = await client.getTransaction(accepted.transaction_ids[0]);
  assert.equal(detail.batch_id, accepted.batch_id);
  const transactionIncidents = await client.listTransactionIncidents(detail.transaction_id);
  assert.equal(transactionIncidents.transaction_id, detail.transaction_id);
  assert.ok(["RESOLVED", "PARTIAL", "NO_INCIDENT"].includes(transactionIncidents.status));

  const incidents = await client.listIncidents();
  assert.ok(Array.isArray(incidents));
});
