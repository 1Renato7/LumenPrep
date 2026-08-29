"""TASK-ING-001. Valida canonical attempt contra CTR-EVT-001 (contracts/v1/canonical-attempt.schema.json)."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator

_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "contracts" / "v1" / "canonical-attempt.schema.json"
_SCHEMA = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
_VALIDATOR = Draft202012Validator(_SCHEMA)


def validate_canonical(payload: dict) -> list[str]:
    return [f"{'.'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in _VALIDATOR.iter_errors(payload)]
