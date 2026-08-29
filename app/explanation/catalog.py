"""Versioned, validated playbook catalog for human-only recommendations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .grounded import Playbook


CATALOG_SCHEMA_VERSION = "1.0"
DEFAULT_CATALOG_PATH = Path(__file__).with_name("playbooks.v1.json")


def load_playbooks(path: str | Path | None = None) -> tuple[Playbook, ...]:
    """Load a catalog without allowing it to grant execution authority."""
    catalog_path = Path(path) if path is not None else DEFAULT_CATALOG_PATH
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("playbook catalog must be an object")
    if set(payload) != {"schema_version", "playbooks"}:
        raise ValueError("playbook catalog fields do not match catalog schema")
    if payload.get("schema_version") != CATALOG_SCHEMA_VERSION:
        raise ValueError("unsupported playbook catalog schema_version")
    entries = payload.get("playbooks")
    if not isinstance(entries, list) or not entries:
        raise ValueError("playbook catalog requires a non-empty playbooks list")

    playbooks = tuple(_parse_playbook(entry) for entry in entries)
    ids = [playbook.playbook_id for playbook in playbooks]
    if len(set(ids)) != len(ids):
        raise ValueError("playbook catalog contains duplicate playbook_id values")
    if "PB-GENERIC-INVESTIGATION" not in ids:
        raise ValueError("playbook catalog requires PB-GENERIC-INVESTIGATION")
    return playbooks


def _parse_playbook(entry: object) -> Playbook:
    if not isinstance(entry, Mapping):
        raise ValueError("playbook entry must be an object")
    expected = {
        "playbook_id",
        "cause_categories",
        "required_scope",
        "action",
        "cautions",
        "execution",
    }
    if set(entry) != expected:
        raise ValueError("playbook entry fields do not match catalog schema")
    if entry["execution"] != "HUMAN_ONLY":
        raise ValueError("playbook catalog may only declare HUMAN_ONLY execution")

    playbook_id = _required_string(entry, "playbook_id")
    action = _required_string(entry, "action")
    cause_categories = frozenset(_string_list(entry["cause_categories"], "cause_categories"))
    cautions = tuple(_string_list(entry["cautions"], "cautions"))
    required_scope = _scope(entry["required_scope"])
    return Playbook(playbook_id, cause_categories, required_scope, action, cautions)


def _required_string(entry: Mapping[str, Any], field: str) -> str:
    value = entry[field]
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ValueError(f"{field} must be a list of non-empty strings")
    return value


def _scope(value: object) -> dict[str, frozenset[str]]:
    if not isinstance(value, Mapping):
        raise ValueError("required_scope must be an object")
    scope: dict[str, frozenset[str]] = {}
    for key, values in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError("required_scope keys must be non-empty strings")
        parsed_values = _string_list(values, f"required_scope.{key}")
        if not parsed_values:
            raise ValueError(f"required_scope.{key} must not be empty")
        scope[key] = frozenset(parsed_values)
    return scope

