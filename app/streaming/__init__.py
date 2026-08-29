"""CTR-STR-001 transaction-server boundary and its ingestion listener.

Only the server contract is imported eagerly.  A simulation producer must be
able to import that contract without accidentally loading the ingestion stack.
"""

from app.streaming.server import PublishReceipt, PublishedTransaction, TransactionPublisher, TransactionServer

__all__ = [
    "ConsumeReport",
    "IngestionListener",
    "IngestionListenerWorker",
    "PublishReceipt",
    "PublishedTransaction",
    "TransactionPublisher",
    "TransactionServer",
    "get_ingestion_listener",
    "get_transaction_server",
    "reset_transaction_pipeline",
]


def __getattr__(name: str):
    if name in {"ConsumeReport", "IngestionListener", "IngestionListenerWorker"}:
        from app.streaming.listener import ConsumeReport, IngestionListener, IngestionListenerWorker

        return {
            "ConsumeReport": ConsumeReport,
            "IngestionListener": IngestionListener,
            "IngestionListenerWorker": IngestionListenerWorker,
        }[name]
    if name in {"get_ingestion_listener", "get_transaction_server", "reset_transaction_pipeline"}:
        from app.streaming.runtime import get_ingestion_listener, get_transaction_server, reset_transaction_pipeline

        return {
            "get_ingestion_listener": get_ingestion_listener,
            "get_transaction_server": get_transaction_server,
            "reset_transaction_pipeline": reset_transaction_pipeline,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
