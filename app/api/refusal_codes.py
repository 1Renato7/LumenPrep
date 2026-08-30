"""Public read-only CTR-RFC-001 endpoint."""

from fastapi import APIRouter, HTTPException, Query

from app.ingestion.storage import CONNECTION_LOCK, get_connection
from app.refusal_codes import RefusalCodeLookup, resolve_refusal_code

router = APIRouter(prefix="/v1/refusal-codes", tags=["refusal-codes"])


@router.get("/resolve")
def resolve(provider_id: str = Query(min_length=1), issuer_bank: str = Query(min_length=1),
            card_brand: str = Query(min_length=1), response_code: str = Query(min_length=1, max_length=32)) -> dict[str, str | None]:
    try:
        with CONNECTION_LOCK:
            resolved = resolve_refusal_code(get_connection(), RefusalCodeLookup(provider_id, issuer_bank, card_brand, response_code))
    except ValueError as error:
        raise HTTPException(status_code=422, detail="INVALID_REFUSAL_CODE_LOOKUP") from error
    return {"schema_version": "1.0", **resolved.as_payload()}
