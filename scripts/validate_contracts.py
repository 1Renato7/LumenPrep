"""TASK-CON-001. Valida schemas x fixtures x OpenAPI. Falha bloqueante, roda antes de qualquer handoff."""

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
SCHEMAS = ROOT / "contracts" / "v1"
SCHEMAS_V2 = ROOT / "contracts" / "v2"
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
    "transaction-catalog.schema.json": ["transaction-catalog.json"],
    "transaction-sample-request.schema.json": ["transaction-sample-request.json"],
    "transaction-sample-response.schema.json": ["transaction-sample-response.json"],
    "transaction-batch-request.schema.json": ["transaction-batch-request.json"],
    "transaction-batch-accepted.schema.json": ["transaction-batch-accepted.json"],
    "transaction-list.schema.json": ["transaction-list.json"],
    "transaction-record.schema.json": [
        "transaction-processing.json",
        "transaction-succeeded.json",
        "transaction-failed.json",
    ],
    "transaction-incident-detail.schema.json": ["transaction-incident-detail-no-incident.json"],
    "agent-evidence-pack.schema.json": ["agent-evidence-pack.json"],
    "agent-retrieval-trace.schema.json": ["agent-retrieval-trace.json"],
    "agent-diagnostic-suggestion.schema.json": ["agent-diagnostic-suggestion.json"],
    "refusal-code-resolution.schema.json": ["refusal-code-resolution.json"],
    "human-review-request.schema.json": ["human-review-request-approved.json"],
    "../v2/payment-conversion-candidate.schema.json": ["payment-conversion-candidate.json"],
}


def validate_fixtures() -> list[str]:
    errors = []
    schemas = [json.loads(path.read_text(encoding="utf-8")) for directory in (SCHEMAS, SCHEMAS_V2) for path in directory.glob("*.schema.json")]
    registry = Registry().with_resources(
        (schema["$id"], Resource.from_contents(schema)) for schema in schemas if "$id" in schema
    )
    for schema_name, fixture_names in PAIRS.items():
        schema_path = SCHEMAS / schema_name
        if not schema_path.exists():
            errors.append(f"MISSING SCHEMA {schema_name}")
            continue
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, registry=registry)
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


def validate_incident_matrix() -> list[str]:
    """TASK-ROGERIO-005: matriz SUPPORTED|INCONCLUSIVE x MATCH_FOUND|NO_PRECEDENT|MEMORY_UNAVAILABLE.
    Prova que memory_status nunca vaza pra root_cause.status, usando build_incident_response real
    (app/api/incidents.py, Bloco 2) contra as fixtures — sem editar aquele módulo."""
    from app.api.incidents import _fixture_records, build_incident_response

    def fx(name: str) -> dict:
        return json.loads((FIXTURES / name).read_text(encoding="utf-8"))

    records = _fixture_records()
    supported = records["inc_current_mastercard_001"]
    inconclusive = records["inc_current_mastercard_uncertain_002"]

    cases = [
        (supported, "SUPPORTED", "similar-incidents.json", "MATCH_FOUND", "explanation-bundle.json"),
        (supported, "SUPPORTED", "similar-incidents-empty.json", "NO_PRECEDENT", "explanation-bundle-no-precedent.json"),
        (supported, "SUPPORTED", "similar-incidents-unavailable.json", "MEMORY_UNAVAILABLE", "explanation-bundle-no-precedent.json"),
        (inconclusive, "INCONCLUSIVE", "similar-incidents-inconclusive-current.json", "MATCH_FOUND", "explanation-bundle-inconclusive-with-precedent.json"),
        (inconclusive, "INCONCLUSIVE", "similar-incidents-empty.json", "NO_PRECEDENT", "explanation-bundle-no-precedent.json"),
        (inconclusive, "INCONCLUSIVE", "similar-incidents-unavailable.json", "MEMORY_UNAVAILABLE", "explanation-bundle-no-precedent.json"),
    ]

    errors: list[str] = []
    for incident, expected_status, memory_file, expected_memory_status, explanation_file in cases:
        label = f"{incident['incident_id']} x {memory_file}"
        try:
            response = build_incident_response(incident, fx(memory_file), fx(explanation_file))
        except ValueError as exc:
            errors.append(f"{label}: build_incident_response raised {exc}")
            continue
        if response["incident"]["root_cause"]["status"] != expected_status:
            errors.append(f"{label}: root_cause.status changed to {response['incident']['root_cause']['status']!r}, expected {expected_status!r}")
        if response["memory"]["memory_status"] != expected_memory_status:
            errors.append(f"{label}: memory_status is {response['memory']['memory_status']!r}, expected {expected_memory_status!r}")
        has_matches = bool(response["memory"]["matches"])
        if expected_memory_status == "MATCH_FOUND" and not has_matches:
            errors.append(f"{label}: MATCH_FOUND but matches is empty")
        if expected_memory_status != "MATCH_FOUND" and has_matches:
            errors.append(f"{label}: {expected_memory_status} but matches is non-empty")
    return errors


def main() -> int:
    errors = validate_fixtures() + validate_openapi() + validate_seams() + validate_incident_matrix()
    if errors:
        print(f"FAIL — {len(errors)} contract violation(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("OK — all schemas, fixtures and OpenAPI valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
