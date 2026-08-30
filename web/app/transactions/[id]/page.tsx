import { TransactionDetail } from "@/components/transaction-detail/transaction-detail";
import { firstSearchValue, type SearchValues } from "@/components/transaction-log/url";

export default async function TransactionDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<SearchValues>;
}) {
  const [{ id }, query] = await Promise.all([params, searchParams]);
  return <TransactionDetail transactionId={id} fixture={firstSearchValue(query.fixture)} />;
}
