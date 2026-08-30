export const BRASILIA_TIME_ZONE = "America/Sao_Paulo";

type DateTimeStyle = "short" | "medium" | "long" | "full";

export function formatBrasiliaDateTime(
  value: string,
  styles: { dateStyle?: DateTimeStyle; timeStyle?: DateTimeStyle } = {},
): string {
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: styles.dateStyle ?? "short",
    timeStyle: styles.timeStyle ?? "medium",
    timeZone: BRASILIA_TIME_ZONE,
  }).format(new Date(value));
}
