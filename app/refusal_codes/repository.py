"""Deterministic, versioned lookup of provider response codes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ResolutionStatus(StrEnum):
    MATCH_FOUND = "MATCH_FOUND"
    NOT_FOUND = "NOT_FOUND"
    AMBIGUOUS = "AMBIGUOUS"


@dataclass(frozen=True)
class RefusalCodeLookup:
    provider_id: str
    issuer_bank: str
    card_brand: str
    response_code: str

    def normalized(self) -> "RefusalCodeLookup":
        values = {key: str(value).strip().upper() for key, value in self.__dict__.items()}
        if any(not value for value in values.values()):
            raise ValueError("provider_id, issuer_bank, card_brand and response_code are required")
        return RefusalCodeLookup(**values)


@dataclass(frozen=True)
class RefusalCodeResolution:
    lookup_status: ResolutionStatus
    provider_id: str
    issuer_bank: str
    card_brand: str
    response_code: str
    outcome: str
    normalized_code: str | None
    reason: str | None
    source: str | None
    mapping_version: str | None

    def as_payload(self) -> dict[str, str | None]:
        return {
            "lookup_status": self.lookup_status.value,
            "provider_id": self.provider_id,
            "issuer_bank": self.issuer_bank,
            "card_brand": self.card_brand,
            "response_code": self.response_code,
            "outcome": self.outcome,
            "normalized_code": self.normalized_code,
            "reason": self.reason,
            "source": self.source,
            "mapping_version": self.mapping_version,
        }


def resolve_refusal_code(con, lookup: RefusalCodeLookup) -> RefusalCodeResolution:
    """Resolve by exact provider, issuer and brand before wildcard rows.

    A tie with different meanings is explicitly unknown. This keeps a catalogue
    import error from becoming a false approval/refusal in the transaction record.
    """
    value = lookup.normalized()
    rows = con.execute(
        """SELECT provider_id, issuer_bank, card_brand, response_code, outcome, normalized_code, reason, source,
                  mapping_version,
                  (CASE WHEN provider_id = ? THEN 4 ELSE 0 END +
                   CASE WHEN issuer_bank = ? THEN 2 ELSE 0 END +
                   CASE WHEN card_brand = ? THEN 1 ELSE 0 END) AS specificity
           FROM refusal_code_catalog
           WHERE active = TRUE AND provider_id IN (?, '*') AND issuer_bank IN (?, '*')
             AND card_brand IN (?, '*') AND response_code = ?
           ORDER BY specificity DESC, mapping_version DESC""",
        [value.provider_id, value.issuer_bank, value.card_brand, value.provider_id,
         value.issuer_bank, value.card_brand, value.response_code],
    ).fetchall()
    if not rows:
        return RefusalCodeResolution(ResolutionStatus.NOT_FOUND, value.provider_id, value.issuer_bank,
            value.card_brand, value.response_code, "UNKNOWN", None, None, None, None)
    best = [row for row in rows if row[9] == rows[0][9]]
    if len({(row[4], row[5], row[6], row[7], row[8]) for row in best}) != 1:
        return RefusalCodeResolution(ResolutionStatus.AMBIGUOUS, value.provider_id, value.issuer_bank,
            value.card_brand, value.response_code, "UNKNOWN", None, None, None, None)
    row = best[0]
    return RefusalCodeResolution(ResolutionStatus.MATCH_FOUND, value.provider_id, value.issuer_bank,
        value.card_brand if row[2] == "*" else row[2], row[3], row[4], row[5], row[6], row[7], row[8])
