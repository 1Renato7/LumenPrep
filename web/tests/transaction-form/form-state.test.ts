import assert from "node:assert/strict";
import test from "node:test";

import type { TransactionCatalog, TransactionSampleResponse } from "../../lib/api/types";
import {
  addTransactionRow,
  catalogOptions,
  createInitialFormState,
  duplicateTransactionRow,
  issuesFromApiError,
  removeTransactionRow,
  replaceRowsWithSamples,
  submitTransactionBatch,
  toBatchRequest,
  updateTransactionField,
  validateTransactionRows,
} from "../../components/transaction-form/form-state";

const catalog: TransactionCatalog = {
  schema_version: "1.0",
  max_batch_size: 100,
  merchants: ["merchant_br_01", "merchant_mx_01"],
  providers: ["provider_alpha", "provider_beta"],
  issuer_banks: ["bank_br_a", "bank_br_b"],
  countries: ["BR", "MX"],
  currencies: ["BRL", "MXN"],
  payment_method_categories: ["CARD", "DIGITAL_WALLET"],
  card_brands: ["MASTERCARD", "VISA"],
  card_types: ["CREDIT", "DEBIT", "NOT_APPLICABLE"],
  correlation_id: "corr_catalog_test",
};

const samples: TransactionSampleResponse = {
  schema_version: "1.0",
  seed: 29082026,
  transactions: [
    {
      merchant_id: "merchant_br_01",
      provider_id: "provider_alpha",
      issuer_bank: "bank_br_a",
      country: "BR",
      currency: "BRL",
      amount_minor: 12990,
      payment_method_category: "CARD",
      card_brand: "MASTERCARD",
      card_type: "CREDIT",
      provider_response_code: "00",
    },
    {
      merchant_id: "merchant_mx_01",
      provider_id: "provider_beta",
      issuer_bank: "bank_br_b",
      country: "MX",
      currency: "MXN",
      amount_minor: 7990,
      payment_method_category: "DIGITAL_WALLET",
      card_type: "NOT_APPLICABLE",
      provider_response_code: "00",
    },
  ],
  correlation_id: "corr_sample_test",
};

test("add, duplicate, and remove keep the minimum and maximum row limits", () => {
  let state = createInitialFormState();
  const first = state.rows[0];
  state = updateTransactionField(state, first.id, "merchant_id", "merchant_br_01");
  state = duplicateTransactionRow(state, first.id);
  assert.equal(state.rows.length, 2);
  assert.equal(state.rows[1].values.merchant_id, "merchant_br_01");
  assert.notEqual(state.rows[0].id, state.rows[1].id);

  state = removeTransactionRow(state, state.rows[1].id);
  assert.equal(state.rows.length, 1);
  assert.strictEqual(removeTransactionRow(state, state.rows[0].id), state);

  for (let index = 0; index < 110; index += 1) state = addTransactionRow(state);
  assert.equal(state.rows.length, 100);
  assert.strictEqual(addTransactionRow(state), state);
});

test("catalog options contain every value supplied by the API catalog", () => {
  const options = catalogOptions(catalog);
  assert.deepEqual(options.merchants, catalog.merchants);
  assert.deepEqual(options.providers, catalog.providers);
  assert.deepEqual(options.issuer_banks, catalog.issuer_banks);
  assert.deepEqual(options.countries, catalog.countries);
  assert.deepEqual(options.currencies, catalog.currencies);
  assert.deepEqual(options.payment_method_categories, catalog.payment_method_categories);
  assert.deepEqual(options.card_brands, catalog.card_brands);
  assert.deepEqual(options.card_types, catalog.card_types);
});

test("a sample response keeps the received batch editable", () => {
  const once = replaceRowsWithSamples(createInitialFormState(), samples);
  const twice = replaceRowsWithSamples(createInitialFormState(), samples);
  assert.deepEqual(toBatchRequest(once.rows, "idempotency-key"), toBatchRequest(twice.rows, "idempotency-key"));

  const edited = updateTransactionField(once, once.rows[0].id, "amount_minor", "13000");
  assert.equal(edited.rows[0].values.amount_minor, "13000");
  assert.equal(once.rows[0].values.amount_minor, "12990");
});

test("submits one-item and multi-item batches without forbidden fields", async () => {
  const one = replaceRowsWithSamples(createInitialFormState(), { ...samples, transactions: [samples.transactions[0]] });
  const oneRequest = toBatchRequest(one.rows, "idempotency-key-1");
  assert.equal(oneRequest.transactions.length, 1);
  assert.equal(oneRequest.idempotency_key, "idempotency-key-1");
  assert.equal("status" in oneRequest.transactions[0], false);
  assert.equal("pan" in oneRequest.transactions[0], false);

  const submitted = [] as typeof oneRequest[];
  const api = {
    createTransactionBatch: async (request: typeof oneRequest) => {
      submitted.push(request);
      return {
        schema_version: "1.0" as const,
        batch_id: "batch_test",
        accepted_at: "2026-08-29T18:00:00Z",
        status: "PROCESSING" as const,
        transaction_ids: request.transactions.map((_transaction, index) => `txn_${index + 1}`),
        correlation_id: "corr_batch_test",
      };
    },
  };
  const acceptedOne = await submitTransactionBatch(api, one.rows, "idempotency-key-1");
  assert.equal(acceptedOne.transaction_ids.length, 1);

  const many = replaceRowsWithSamples(createInitialFormState(), samples);
  const manyRequest = toBatchRequest(many.rows, "idempotency-key-2");
  assert.equal(manyRequest.transactions.length, 2);
  assert.deepEqual(validateTransactionRows(many.rows, catalog), []);
  const acceptedMany = await submitTransactionBatch(api, many.rows, "idempotency-key-2");
  assert.equal(acceptedMany.transaction_ids.length, 2);
  assert.deepEqual(submitted, [oneRequest, manyRequest]);
});

test("a 422 field issue identifies its row and preserves editable row values", () => {
  const state = replaceRowsWithSamples(createInitialFormState(), samples);
  const before = state.rows.map((row) => ({ ...row.values }));
  const issues = issuesFromApiError({
    detail: [{ index: 1, field: "issuer_bank", message: "Issuer bank is unavailable." }],
  });
  assert.deepEqual(issues, [{ rowIndex: 1, field: "issuer_bank", message: "Issuer bank is unavailable." }]);
  assert.deepEqual(
    issuesFromApiError({ detail: [{ loc: ["body", "transactions", 1, "issuer_bank"], msg: "Issuer bank is unavailable." }] }),
    [{ rowIndex: 1, field: "issuer_bank", message: "Issuer bank is unavailable." }],
  );
  assert.deepEqual(state.rows.map((row) => row.values), before);
});

test("provider response code is required before submitting a batch", () => {
  const state = replaceRowsWithSamples(createInitialFormState(), samples);
  const withoutResponseCode = updateTransactionField(state, state.rows[0].id, "provider_response_code", "   ");

  assert.deepEqual(validateTransactionRows(withoutResponseCode.rows, catalog), [
    { rowIndex: 0, field: "provider_response_code", message: "provider response code is required." },
  ]);
});
