"""Process-local wiring for the MVP transaction server and its sole listener."""

from __future__ import annotations

from app.streaming.listener import IngestionListener
from app.streaming.server import TransactionServer

_server = TransactionServer()
_listener = IngestionListener(_server)


def get_transaction_server() -> TransactionServer:
    return _server


def get_ingestion_listener() -> IngestionListener:
    return _listener


def reset_transaction_pipeline() -> None:
    """Reset process-local state for tests; production starts with an empty server."""
    global _server, _listener
    _server = TransactionServer()
    _listener = IngestionListener(_server)
