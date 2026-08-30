import type { TransactionIncidentDetail, TransactionIncidentLink } from "@/lib/api/types";

/** Select only an Incident link explicitly authorized by both classification and CTR-TDI. */
export function selectAuthorizedIncidentLink(
  grounding: TransactionIncidentDetail | null,
  relatedIncidentIds: string[],
): TransactionIncidentLink | null {
  if (!grounding) return null;
  return grounding.incidents.find((link) => relatedIncidentIds.includes(link.incident.incident_id)) ?? null;
}

export function isRejectedIncident(grounding: TransactionIncidentDetail | null, incidentId: string): boolean {
  return grounding?.rejected_incident_ids.includes(incidentId) ?? false;
}
