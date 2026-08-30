"""Validated runtime access to the versioned Adyen refusal-reason table."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from pathlib import Path
import re

_TABLE_PATH = Path(__file__).resolve().parents[2] / "data" / "adyen-refusal-reasons.md"
_ROW_PATTERN = re.compile(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|")


@dataclass(frozen=True)
class AdyenRefusalReason:
    code: str
    reason: str


@cache
def refusal_reason_options(path: Path = _TABLE_PATH) -> tuple[AdyenRefusalReason, ...]:
    """Read only the numeric-code rows from the checked-in Adyen reference table."""
    options = tuple(
        AdyenRefusalReason(code=match.group(1), reason=match.group(2).strip())
        for line in path.read_text(encoding="utf-8").splitlines()
        if (match := _ROW_PATTERN.match(line))
    )
    if not options or len({option.code for option in options}) != len(options):
        raise ValueError("Adyen refusal-reason table must contain unique numeric codes")
    if len({option.reason for option in options}) != len(options):
        raise ValueError("Adyen refusal-reason table must contain unique reasons for the form selector")
    if any(not option.reason or len(option.reason) > 100 for option in options):
        raise ValueError("Adyen refusal-reason table has an invalid reason")
    return options
