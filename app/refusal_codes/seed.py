"""Bootstrap the versioned response-code catalogue from repository data."""

from __future__ import annotations

from .catalog import catalog_rows


def seed_catalog(con) -> None:
    for item in catalog_rows():
        con.execute(
            """INSERT INTO refusal_code_catalog
               (mapping_id, provider_id, issuer_bank, card_brand, response_code, normalized_code, outcome, reason, source, mapping_version, active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, TRUE)
               ON CONFLICT (mapping_id) DO UPDATE SET provider_id=excluded.provider_id,
                 issuer_bank=excluded.issuer_bank, card_brand=excluded.card_brand,
                 response_code=excluded.response_code, normalized_code=excluded.normalized_code,
                 outcome=excluded.outcome, reason=excluded.reason,
                 source=excluded.source, mapping_version=excluded.mapping_version, active=TRUE""",
            [item[key] for key in ("mapping_id", "provider_id", "issuer_bank", "card_brand", "response_code", "normalized_code", "outcome", "reason", "source", "mapping_version")],
        )
