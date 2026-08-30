import { IncidentDetail } from "@/components/incidents/incident-detail";

export default async function IncidentDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <IncidentDetail incidentId={id} />;
}
