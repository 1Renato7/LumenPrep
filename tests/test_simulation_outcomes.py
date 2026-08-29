from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator
import json

from app.ingestion import ingest_event
from app.simulation import OutcomeGenerator, load_generator_config

CONFIG_PATH = Path("config/generator/v1/default.json")
SCHEMA_PATH = Path("contracts/v1/canonical-attempt.schema.json")


def _generator() -> OutcomeGenerator:
    config = load_generator_config(CONFIG_PATH)
    return OutcomeGenerator(config, reference_time=datetime(2026, 8, 29, 14, 0, 0, tzinfo=timezone.utc))


def test_canonical_events_validate_against_schema():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    generator = _generator()

    for attempts in generator.generate_payments(30):
        for event in generator.to_canonical_events(attempts):
            errors = list(validator.iter_errors(event))
            assert not errors, f"{event['event_id']}: {[e.message for e in errors]}"


def test_retry_chains_share_payment_id_and_increment_sequence():
    generator = _generator()
    retried = next(
        attempts for attempts in generator.generate_payments(200) if len(attempts) > 1
    )
    assert len({a.payment_id for a in retried}) == 1
    assert [a.attempt_sequence for a in retried] == list(range(1, len(retried) + 1))
    assert all(a.status in {"DECLINED", "TIMEOUT"} for a in retried[:-1])


def test_retry_chain_never_exceeds_max_retries():
    generator = _generator()
    for attempts in generator.generate_payments(300):
        assert len(attempts) <= 3  # 1 original + MAX_RETRIES


def test_events_flow_through_real_ingestion():
    generator = _generator()
    attempts = generator.generate_payment()
    events = generator.to_canonical_events(attempts)

    results = [ingest_event(event) for event in events]
    assert all(r.status == "ACCEPTED" for r in results)
