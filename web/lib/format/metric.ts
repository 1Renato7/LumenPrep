export function formatMetricValue(value: number | string | string[] | null | undefined): string {
  if (value === null || value === undefined) return "Not available";
  return Array.isArray(value) ? value.join(", ") || "Not available" : String(value);
}
