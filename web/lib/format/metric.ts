export function formatMetricValue(value: number | string | string[] | null | undefined): string {
  if (value === null || value === undefined) return "Not available";
  if (Array.isArray(value)) return value.join(", ") || "Not available";
  if (typeof value !== "number" || Number.isInteger(value)) return String(value);
  return new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value);
}
