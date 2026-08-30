import { TransactionDetail } from "@/components/transaction-detail/transaction-detail";

export default async function TransactionDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <TransactionDetail transactionId={id} />;
}
