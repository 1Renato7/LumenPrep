"""TASK-CON-001. Valida schemas x fixtures x OpenAPI. Falha bloqueante, roda antes de qualquer handoff."""

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
SCHEMAS = ROOT / "contracts" / "v1"
FIXTURES = ROOT / "contracts" / "fixtures"

PAIRS: dict[str, list[str]] = {
    "canonical-attempt.schema.json": ["canonical-attempt.json"],
    "window-metrics.schema.json": ["window-metrics.json"],
    "anomaly-candidate.schema.json": ["anomaly-candidate.json"],
    "incident.schema.json": [
        "incident-mastercard-recurrence.json",
        "incident-inconclusive-with-precedent.json",
    ],
    "similar-incidents.schema.json": [
        "similar-incidents.json",
        "similar-incidents-empty.json",
        "similar-incidents-inconclusive-current.json",
        "similar-incidents-unavailable.json",
    ],
    "explanation-bundle.schema.json": [
        "explanation-bundle.json",
        "explanation-bundle-no-precedent.json",
        "explanation-bundle-inconclusive-with-precedent.json",
    ],
    "scenario.schema.json": ["scenario-provider-br.json"],
}


def validate_fixtures() -> list[str]:
    errors = []
    for schema_name, fixture_names in PAIRS.items():
        schema_path = SCHEMAS / schema_name
        if not schema_path.exists():
            errors.append(f"MISSING SCHEMA {schema_name}")
            continue
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        for fixture_name in fixture_names:
            fixture_path = FIXTURES / fixture_name
            if not fixture_path.exists():
                errors.append(f"MISSING FIXTURE {fixture_name}")
                continue
            instance = json.loads(fixture_path.read_text(encoding="utf-8"))
            for err in validator.iter_errors(instance):
                errors.append(f"{fixture_name} vs {schema_name}: {err.message} @ {list(err.path)}")
    return errors


def validate_openapi() -> list[str]:
    errors = []
    path = SCHEMAS / "api.openapi.yaml"
    if not path.exists():
        return ["MISSING contracts/v1/api.openapi.yaml"]
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    if "openapi" not in doc or "paths" not in doc:
        errors.append("api.openapi.yaml: missing 'openapi' or 'paths' top-level key")
    return errors


def validate_seams() -> list[str]:
    """Bloco 1 → Bloco 2 seams (rogerio.md §Mapa de módulos internos): saída real das
    funções expostas ainda bate no schema, mesmo em stub."""
    errors = []
    from app.aggregation import get_current_metrics
    from app.ingestion import ingest_event

    schema = json.loads((SCHEMAS / "window-metrics.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    for m in get_current_metrics():
        for err in validator.iter_errors(m.model_dump()):
            errors.append(f"get_current_metrics() vs window-metrics.schema.json: {err.message}")

    canonical_fixture = json.loads((FIXTURES / "canonical-attempt.json").read_text(encoding="utf-8"))
    result = ingest_event(canonical_fixture)
    schema = json.loads((SCHEMAS / "canonical-attempt.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    if result.canonical is not None:
        for err in validator.iter_errors(result.canonical):
            errors.append(f"ingest_event().canonical vs canonical-attempt.schema.json: {err.message}")
    return errors


def main() -> int:
    errors = validate_fixtures() + validate_openapi() + validate_seams()
    if errors:
        print(f"FAIL — {len(errors)} contract violation(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("OK — all schemas, fixtures and OpenAPI valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
