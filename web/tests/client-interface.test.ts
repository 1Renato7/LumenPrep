import assert from "node:assert/strict";
import test from "node:test";

import {
  createLumenApiClient,
  createPollingController,
  LumenApiError,
} from "../lib/api/client-interface";

const originalBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

function withBaseUrl(): void {
  process.env.NEXT_PUBLIC_API_BASE_URL = "https://api.example.test/v1/";
}

test("batch calls use the configured public API URL and Idempotency-Key header", async () => {
  withBaseUrl();
  let receivedUrl = "";
  let receivedHeaders: Headers | undefined;
  const client = createLumenApiClient({
    fetchImpl: async (url, init) => {
      receivedUrl = String(url);
      receivedHeaders = new Headers(init?.headers);
      return Response.json({
        schema_version: "1.0",
        batch_id: "batch_1",
        accepted_at: "2026-08-29T18:00:00Z",
        status: "PROCESSING",
        transaction_ids: ["txn_1"],
        correlation_id: "corr_1",
      });
    },
  });

  await client.createTransactionBatch({
    schema_version: "1.0",
    idempotency_key: "idem-key-1",
    transactions: [
      {
        merchant_id: "merchant_br_01",
        provider_id: "provider_alpha",
        issuer_bank: "bank_br_a",
        country: "BR",
        currency: "BRL",
        amount_minor: 100,
        payment_method_category: "CARD",
      },
    ],
  });

  assert.equal(receivedUrl, "https://api.example.test/v1/transaction-batches");
  assert.equal(receivedHeaders?.get("Idempotency-Key"), "idem-key-1");
});

test("live demo trial calls stay under the versioned API path and retain their retry key", async () => {
  withBaseUrl();
  let receivedUrl = "";
  let receivedHeaders: Headers | undefined;
  const client = createLumenApiClient({
    fetchImpl: async (url, init) => {
      receivedUrl = String(url);
      receivedHeaders = new Headers(init?.headers);
      return Response.json({
        schema_version: "1.0",
        trial_id: "deterministic",
        flow: "DETERMINISTIC",
        execution_mode: "QUEUED_SAFE",
        baseline_batch_ids: ["batch_baseline_1"],
        batch_id: "batch_trial_1",
        accepted_at: "2026-08-29T18:00:00Z",
        status: "PROCESSING",
        transaction_ids: Array.from({ length: 25 }, (_unused, index) => `txn_${index + 1}`),
        correlation_id: "corr_trial_1",
      });
    },
  });

  const accepted = await client.startLiveDemoTrial("deterministic", "demo-retry-key");

  assert.equal(accepted.transaction_ids.length, 25);
  assert.equal(receivedUrl, "https://api.example.test/v1/demo/live-trials/deterministic");
  assert.equal(receivedHeaders?.get("Idempotency-Key"), "demo-retry-key");
});

test("specified HTTP responses become typed API errors", async () => {
  withBaseUrl();
  for (const [status, code] of [
    [404, "NOT_FOUND"],
    [409, "CONFLICT"],
    [422, "VALIDATION"],
    [503, "SERVICE_UNAVAILABLE"],
  ] as const) {
    const client = createLumenApiClient({
      fetchImpl: async () => Response.json({ status }, { status }),
    });

    await assert.rejects(
      client.getTransaction("txn_1"),
      (error: unknown) =>
        error instanceof LumenApiError && error.code === code && error.status === status,
    );
  }
});

test("timeout and polling cancellation are observable through AbortSignal", async () => {
  withBaseUrl();
  const client = createLumenApiClient({
    defaultTimeoutMs: 5,
    fetchImpl: async (_url, init) =>
      new Promise<Response>((_resolve, reject) => {
        init?.signal?.addEventListener("abort", () => reject(new DOMException("Aborted", "AbortError")));
      }),
  });

  await assert.rejects(
    client.getTransactionCatalog(),
    (error: unknown) => error instanceof LumenApiError && error.code === "TIMEOUT",
  );

  const polling = createPollingController();
  const cancelledClient = createLumenApiClient({
    fetchImpl: async (_url, init) =>
      new Promise<Response>((_resolve, reject) => {
        init?.signal?.addEventListener("abort", () => reject(new DOMException("Aborted", "AbortError")));
      }),
  });
  const cancelledRequest = cancelledClient.getTransactionCatalog({ signal: polling.signal });
  polling.cancel();

  await assert.rejects(
    cancelledRequest,
    (error: unknown) => error instanceof LumenApiError && error.code === "CANCELLED",
  );
  assert.equal(polling.signal.aborted, true);
});

test.after(() => {
  if (originalBaseUrl === undefined) delete process.env.NEXT_PUBLIC_API_BASE_URL;
  else process.env.NEXT_PUBLIC_API_BASE_URL = originalBaseUrl;
});
