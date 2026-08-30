import type {
  TransactionBatchAccepted,
  TransactionBatchRequest,
  TransactionCatalog,
  TransactionInput,
  TransactionSampleResponse,
} from "../../lib/api/types";
import type { LumenApiClient } from "../../lib/api/client-interface";

export const MIN_TRANSACTION_ROWS = 1;
export const MAX_TRANSACTION_ROWS = 100;

export type TransactionField =
  | "client_reference"
  | "occurred_at"
  | "merchant_id"
  | "provider_id"
  | "issuer_bank"
  | "country"
  | "currency"
  | "amount_minor"
  | "payment_method_category"
  | "card_brand"
  | "card_type"
  | "provider_connection_id"
  | "provider_response_code";

export interface TransactionFormRow {
  id: string;
  values: Record<TransactionField, string>;
}

export interface TransactionFormState {
  rows: TransactionFormRow[];
}

export interface FieldIssue {
  rowIndex: number;
  field?: TransactionField;
  message: string;
}

export type CatalogOptions = Pick<
  TransactionCatalog,
  | "merchants"
  | "providers"
  | "issuer_banks"
  | "countries"
  | "currencies"
  | "payment_method_categories"
  | "card_brands"
  | "card_types"
  | "provider_response_options"
>;

let nextRowId = 1;

export function createEmptyRow(id = createRowId()): TransactionFormRow {
  return {
    id,
    values: {
      client_reference: "",
      occurred_at: "",
      merchant_id: "",
      provider_id: "",
      issuer_bank: "",
      country: "",
      currency: "",
      amount_minor: "",
      payment_method_category: "",
      card_brand: "",
      card_type: "",
      provider_connection_id: "",
      provider_response_code: "",
    },
  };
}

export function createInitialFormState(): TransactionFormState {
  return { rows: [createEmptyRow()] };
}

export function addTransactionRow(state: TransactionFormState): TransactionFormState {
  if (state.rows.length >= MAX_TRANSACTION_ROWS) return state;
  return { ...state, rows: [...state.rows, createEmptyRow()] };
}

export function duplicateTransactionRow(
  state: TransactionFormState,
  rowId: string,
): TransactionFormState {
  if (state.rows.length >= MAX_TRANSACTION_ROWS) return state;
  const rowIndex = state.rows.findIndex((row) => row.id === rowId);
  if (rowIndex < 0) return state;

  const original = state.rows[rowIndex];
  const duplicate: TransactionFormRow = {
    id: createRowId(),
    values: { ...original.values },
  };
  return {
    ...state,
    rows: [...state.rows.slice(0, rowIndex + 1), duplicate, ...state.rows.slice(rowIndex + 1)],
  };
}

export function removeTransactionRow(
  state: TransactionFormState,
  rowId: string,
): TransactionFormState {
  if (state.rows.length <= MIN_TRANSACTION_ROWS) return state;
  return { ...state, rows: state.rows.filter((row) => row.id !== rowId) };
}

export function updateTransactionField(
  state: TransactionFormState,
  rowId: string,
  field: TransactionField,
  value: string,
): TransactionFormState {
  return {
    ...state,
    rows: state.rows.map((row) =>
      row.id === rowId ? { ...row, values: { ...row.values, [field]: value } } : row,
    ),
  };
}

export function catalogOptions(catalog: TransactionCatalog): CatalogOptions {
  return {
    merchants: catalog.merchants,
    providers: catalog.providers,
    issuer_banks: catalog.issuer_banks,
    countries: catalog.countries,
    currencies: catalog.currencies,
    payment_method_categories: catalog.payment_method_categories,
    card_brands: catalog.card_brands,
    card_types: catalog.card_types,
    provider_response_options: catalog.provider_response_options,
  };
}

export function replaceRowsWithSamples(
  state: TransactionFormState,
  response: TransactionSampleResponse,
): TransactionFormState {
  return {
    ...state,
    rows: response.transactions.map((transaction) => transactionToRow(transaction)),
  };
}

export function validateTransactionRows(
  rows: TransactionFormRow[],
  catalog: TransactionCatalog,
): FieldIssue[] {
  const issues: FieldIssue[] = [];
  if (rows.length < MIN_TRANSACTION_ROWS || rows.length > Math.min(catalog.max_batch_size, MAX_TRANSACTION_ROWS)) {
    return [{ rowIndex: 0, message: "A batch must contain between 1 and 100 transactions." }];
  }

  for (const [rowIndex, row] of rows.entries()) {
    const { values } = row;
    for (const field of requiredFields) {
      if (!values[field].trim()) {
        issues.push({ rowIndex, field, message: `${fieldLabel(field)} is required.` });
      }
    }

    const amount = Number(values.amount_minor);
    if (!Number.isInteger(amount) || amount < 1) {
      issues.push({ rowIndex, field: "amount_minor", message: "Amount must be a whole number of at least 1." });
    }

    assertOption(issues, rowIndex, "merchant_id", values.merchant_id, catalog.merchants);
    assertOption(issues, rowIndex, "provider_id", values.provider_id, catalog.providers);
    assertOption(issues, rowIndex, "issuer_bank", values.issuer_bank, catalog.issuer_banks);
    assertOption(issues, rowIndex, "country", values.country, catalog.countries);
    assertOption(issues, rowIndex, "currency", values.currency, catalog.currencies);
    assertOption(
      issues,
      rowIndex,
      "payment_method_category",
      values.payment_method_category,
      catalog.payment_method_categories,
    );
    if (values.card_brand) {
      assertOption(issues, rowIndex, "card_brand", values.card_brand, catalog.card_brands);
    }
    if (values.card_type) {
      assertOption(issues, rowIndex, "card_type", values.card_type, catalog.card_types);
    }
    const responseOption = catalog.provider_response_options.find((option) => option.code === values.provider_response_code);
    if (values.provider_response_code.trim() && !responseOption) {
      issues.push({ rowIndex, field: "provider_response_code", message: "Provider response code is not available in the Adyen reference table." });
    } else if (responseOption && values.provider_connection_id !== responseOption.reason) {
      issues.push({ rowIndex, field: "provider_connection_id", message: "Provider connection must match the selected provider response code." });
    }
    if (responseOption && values.provider_id !== "adyen") {
      issues.push({ rowIndex, field: "provider_id", message: "Adyen response codes require the Adyen provider." });
    }
  }
  return uniqueIssues(issues);
}

export function toBatchRequest(
  rows: TransactionFormRow[],
  idempotencyKey: string,
): TransactionBatchRequest {
  return {
    schema_version: "1.0",
    idempotency_key: idempotencyKey,
    transactions: rows.map(rowToTransaction),
  };
}

export function submitTransactionBatch(
  api: Pick<LumenApiClient, "createTransactionBatch">,
  rows: TransactionFormRow[],
  idempotencyKey: string,
): Promise<TransactionBatchAccepted> {
  return api.createTransactionBatch(toBatchRequest(rows, idempotencyKey));
}

export function issuesFromApiError(body: unknown): FieldIssue[] {
  const entries = extractIssueEntries(body);
  return entries.flatMap((entry) => {
    if (!isRecord(entry)) return [];
    const location = Array.isArray(entry.loc) ? entry.loc : undefined;
    const rowIndex =
      numberValue(entry.index) ??
      numberValue(entry.row_index) ??
      numberValue(entry.row) ??
      location?.map(numberValue).find((value) => value !== undefined) ??
      0;
    const rawField = stringValue(entry.field) ?? stringValue(entry.loc) ?? location?.map(stringValue).find(isTransactionField);
    const field = isTransactionField(rawField) ? rawField : undefined;
    const message = stringValue(entry.message) ?? stringValue(entry.msg) ?? "The transaction could not be accepted.";
    return [{ rowIndex, field, message }];
  });
}

function transactionToRow(transaction: TransactionInput): TransactionFormRow {
  return {
    id: createRowId(),
    values: {
      client_reference: transaction.client_reference ?? "",
      occurred_at: transaction.occurred_at ?? "",
      merchant_id: transaction.merchant_id,
      provider_id: transaction.provider_id,
      issuer_bank: transaction.issuer_bank,
      country: transaction.country,
      currency: transaction.currency,
      amount_minor: String(transaction.amount_minor),
      payment_method_category: transaction.payment_method_category,
      card_brand: transaction.card_brand ?? "",
      card_type: transaction.card_type ?? "",
      provider_connection_id: transaction.provider_connection_id ?? "",
      provider_response_code: transaction.provider_response_code ?? "",
    },
  };
}

function rowToTransaction(row: TransactionFormRow): TransactionInput {
  const { values } = row;
  return {
    client_reference: nullIfBlank(values.client_reference),
    occurred_at: nullIfBlank(values.occurred_at),
    merchant_id: values.merchant_id.trim(),
    provider_id: values.provider_id.trim(),
    issuer_bank: values.issuer_bank.trim(),
    country: values.country.trim(),
    currency: values.currency.trim(),
    amount_minor: Number(values.amount_minor),
    payment_method_category: values.payment_method_category as TransactionInput["payment_method_category"],
    card_brand: nullIfBlank(values.card_brand),
    card_type: (nullIfBlank(values.card_type) ?? null) as TransactionInput["card_type"],
    provider_connection_id: nullIfBlank(values.provider_connection_id),
    provider_response_code: nullIfBlank(values.provider_response_code),
  };
}

function createRowId(): string {
  const id = nextRowId;
  nextRowId += 1;
  return `transaction-row-${id}`;
}

function nullIfBlank(value: string): string | null {
  const normalized = value.trim();
  return normalized || null;
}

const requiredFields: TransactionField[] = [
  "merchant_id",
  "provider_id",
  "issuer_bank",
  "country",
  "currency",
  "amount_minor",
  "payment_method_category",
];

const fields = new Set<TransactionField>([
  "client_reference",
  "occurred_at",
  "merchant_id",
  "provider_id",
  "issuer_bank",
  "country",
  "currency",
  "amount_minor",
  "payment_method_category",
  "card_brand",
  "card_type",
  "provider_connection_id",
  "provider_response_code",
]);

function assertOption(
  issues: FieldIssue[],
  rowIndex: number,
  field: TransactionField,
  value: string,
  options: string[],
): void {
  if (value && !options.includes(value)) {
    issues.push({ rowIndex, field, message: `${fieldLabel(field)} is not available in the current catalog.` });
  }
}

function uniqueIssues(issues: FieldIssue[]): FieldIssue[] {
  return issues.filter(
    (issue, index) =>
      issues.findIndex(
        (candidate) => candidate.rowIndex === issue.rowIndex && candidate.field === issue.field && candidate.message === issue.message,
      ) === index,
  );
}

function fieldLabel(field: TransactionField): string {
  return field.replaceAll("_", " ");
}

function extractIssueEntries(body: unknown): unknown[] {
  if (Array.isArray(body)) return body;
  if (!isRecord(body)) return [];
  for (const key of ["errors", "detail", "issues"]) {
    const value = body[key];
    if (Array.isArray(value)) return value;
    if (isRecord(value) && Array.isArray(value.errors)) return value.errors;
  }
  return [body];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function numberValue(value: unknown): number | undefined {
  return typeof value === "number" && Number.isInteger(value) && value >= 0 ? value : undefined;
}

function stringValue(value: unknown): string | undefined {
  return typeof value === "string" && value ? value : undefined;
}

function isTransactionField(value: string | undefined): value is TransactionField {
  return value !== undefined && fields.has(value as TransactionField);
}
