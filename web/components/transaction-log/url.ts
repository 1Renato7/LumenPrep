import type { TransactionFilter } from "./filters";

export type SearchValues = Record<string, string | string[] | undefined>;

function firstValue(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

export function buildTransactionUrl(
  current: SearchValues,
  updates: { status?: TransactionFilter; cursor?: string | null; batchId?: string | null },
): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(current)) {
    const first = firstValue(value);
    if (first) params.set(key, first);
  }

  if (updates.status && updates.status !== "ALL") params.set("status", updates.status);
  else params.delete("status");
  if (updates.cursor) params.set("cursor", updates.cursor);
  else params.delete("cursor");
  if (updates.batchId === undefined) {
    // Preserve the current batch scope for ordinary filtering/paging.
  } else if (updates.batchId) {
    params.set("batch_id", updates.batchId);
  } else {
    params.delete("batch_id");
  }

  const query = params.toString();
  return query ? `/transactions?${query}` : "/transactions";
}

export function firstSearchValue(value: string | string[] | undefined): string | undefined {
  return firstValue(value);
}
