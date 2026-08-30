"""Shared, validated source of truth for versioned refusal-code mappings."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_CATALOG_PATH = Path(__file__).resolve().parents[2] / "data" / "refusal-code-catalog.json"
_REQUIRED_FIELDS = (
    "mapping_id", "provider_id", "issuer_bank", "card_brand", "response_code",
    "normalized_code", "outcome", "reason", "source", "mapping_version",
)


def catalog_rows(path: Path = _CATALOG_PATH) -> tuple[dict[str, str], ...]:
    """Load mappings in their deterministic lookup form.

    Provider response codes are case-insensitive identifiers in this catalogue.
    The original provider payload remains in the transaction event's ``raw_code``;
    this normalisation only makes lookup and graph joins reliable (notably Stripe).
    """
    loaded = json.loads(path.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    mapping_ids: set[str] = set()
    for item in loaded:
        if not isinstance(item, dict) or any(not str(item.get(field, "")).strip() for field in _REQUIRED_FIELDS):
            raise ValueError("refusal-code catalog has an incomplete mapping")
        mapping_id = str(item["mapping_id"]).strip()
        if mapping_id in mapping_ids:
            raise ValueError(f"refusal-code catalog contains duplicate mapping_id {mapping_id!r}")
        mapping_ids.add(mapping_id)
        outcome = str(item["outcome"]).strip().upper()
        if outcome not in {"SUCCEEDED", "FAILED", "UNKNOWN"}:
            raise ValueError(f"refusal-code catalog has invalid outcome for {mapping_id!r}")
        row = {field: str(item[field]).strip() for field in _REQUIRED_FIELDS}
        row.update({
            "provider_id": row["provider_id"].upper(),
            "issuer_bank": row["issuer_bank"].upper(),
            "card_brand": row["card_brand"].upper(),
            "response_code": row["response_code"].upper(),
            "normalized_code": row["normalized_code"].upper(),
            "outcome": outcome,
        })
        rows.append(row)
    return tuple(rows)
