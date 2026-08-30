"""CTR-STR-001 HTTP boundary for external transaction producers."""

from typing import Any

from fastapi import APIRouter

from app.streaming import get_ingestion_listener, get_transaction_server

router = APIRouter()


@router.post("/transactions", status_code=202)
def publish_transaction(event: dict[str, Any]) -> dict[str, Any]:
    receipt = get_transaction_server().publish([event])
    return {
        "status": "ACCEPTED",
        "sequence": receipt.first_sequence,
        "source": "transaction_server",
    }


@router.get("/transactions/health")
def transaction_server_health() -> dict[str, int]:
    health = get_transaction_server().health()
    health["listener_cursor"] = get_ingestion_listener().cursor
    health["backlog"] = health["last_sequence"] - health["listener_cursor"]
    return health
