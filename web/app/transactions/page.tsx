import { TransactionLog } from "@/components/transaction-log/transaction-log";
import type { SearchValues } from "@/components/transaction-log/url";

export default async function TransactionsPage({
  searchParams,
}: {
  searchParams: Promise<SearchValues>;
}) {
  return <TransactionLog searchValues={await searchParams} />;
}
