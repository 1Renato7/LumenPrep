import type { TransactionRecord } from "@/lib/api/types";

export const transactionFilters = ["ALL", "SUCCEEDED", "FAILED", "PROCESSING", "UNKNOWN"] as const;
export type TransactionFilter = (typeof transactionFilters)[number];

export function normalizeFilter(value: string | undefined): TransactionFilter {
  return transactionFilters.includes(value as TransactionFilter) ? (value as TransactionFilter) : "ALL";
}

export function hasProcessing(items: TransactionRecord[]): boolean {
  return items.some((item) => item.status === "PROCESSING");
}
