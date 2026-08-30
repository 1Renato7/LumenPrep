import { IncidentDetail } from "@/components/incidents/incident-detail";
import { firstSearchValue, type SearchValues } from "@/components/transaction-log/url";

export default async function IncidentDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<SearchValues>;
}) {
  const [{ id }, query] = await Promise.all([params, searchParams]);
  return <IncidentDetail incidentId={id} fixture={firstSearchValue(query.fixture)} />;
}
