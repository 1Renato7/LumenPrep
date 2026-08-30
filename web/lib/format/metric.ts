export function formatMetricValue(value: number | string | string[] | null | undefined): string {
  if (value === null || value === undefined) return "Not available";
  if (Array.isArray(value)) return value.join(", ") || "Not available";
  const numericValue = typeof value === "number" ? value : isDecimalString(value) ? Number(value) : null;
  if (numericValue === null || Number.isInteger(numericValue)) return String(value);
  return new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(numericValue);
}

function isDecimalString(value: string): boolean {
  return /^-?\d+\.\d+$/.test(value);
}
