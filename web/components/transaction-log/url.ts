import type { TransactionFilter } from "./fixture-source";

export type SearchValues = Record<string, string | string[] | undefined>;

function firstValue(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

export function buildTransactionUrl(
  current: SearchValues,
  updates: { status?: TransactionFilter; cursor?: string | null },
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

  const query = params.toString();
  return query ? `/transactions?${query}` : "/transactions";
}

export function firstSearchValue(value: string | string[] | undefined): string | undefined {
  return firstValue(value);
}
