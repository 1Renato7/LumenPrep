from datetime import datetime, timedelta

import pytest

from app.ingestion import ingest_event, ingest_events, storage
from app.streaming import IngestionListener, TransactionServer


def test_valid_attempt_accepted(valid_attempt):
    result = ingest_event(valid_attempt)
    assert result.status == "ACCEPTED"
    assert result.applied_to_current_state is True
    assert result.canonical["attempt_id"] == valid_attempt["attempt_id"]


def test_duplicate_event_id_rejected(valid_attempt):
    first = ingest_event(valid_attempt)
    second = ingest_event(valid_attempt)
    assert first.status == "ACCEPTED"
    assert second.status == "DUPLICATE"


def test_listener_batch_ingestion_preserves_order_and_deduplication(valid_attempt):
    first = dict(valid_attempt)
    second = dict(valid_attempt)
    second["event_id"] = "evt_second"

    results = ingest_events([first, second, first])

    assert [result.status for result in results] == ["ACCEPTED", "ACCEPTED", "DUPLICATE"]
    assert [result.event_id for result in results] == [first["event_id"], "evt_second", first["event_id"]]


def test_batch_write_failure_rolls_back_preceding_raw_events(monkeypatch, valid_attempt):
    def fail_canonical_write(*_args):
        raise RuntimeError("simulated storage failure")

    monkeypatch.setattr(storage, "store_canonical_events_many", fail_canonical_write)

    with pytest.raises(RuntimeError, match="simulated storage failure"):
        ingest_events([valid_attempt])

    connection = storage.get_connection()
    assert connection.execute("SELECT count(*) FROM raw_events").fetchone()[0] == 0
    assert connection.execute("SELECT count(*) FROM canonical_events").fetchone()[0] == 0


def test_listener_does_not_advance_cursor_when_batch_rolls_back(monkeypatch, valid_attempt):
    server = TransactionServer()
    server.publish([valid_attempt])
    listener = IngestionListener(server)

    def fail_canonical_write(*_args):
        raise RuntimeError("simulated storage failure")

    monkeypatch.setattr(storage, "store_canonical_events_many", fail_canonical_write)

    with pytest.raises(RuntimeError, match="simulated storage failure"):
        listener.consume_available()

    assert listener.cursor == 0


def test_unknown_status_enum_quarantined(valid_attempt):
    valid_attempt["status"] = "TOTALLY_BOGUS"
    result = ingest_event(valid_attempt)
    assert result.status == "QUARANTINED"
    assert any("status" in e for e in result.errors)


def test_invalid_money_quarantined(valid_attempt):
    valid_attempt["amount_minor"] = -100
    result = ingest_event(valid_attempt)
    assert result.status == "QUARANTINED"
    assert any("amount_minor" in e for e in result.errors)


def test_late_within_tolerance_does_not_regress_current_state(valid_attempt):
    first = dict(valid_attempt)
    first["event_id"] = "evt_first"
    first["status"] = "PROCESSING"
    first["decline"] = None
    r1 = ingest_event(first)
    assert r1.status == "ACCEPTED"
    assert r1.applied_to_current_state is True

    late = dict(valid_attempt)
    late["event_id"] = "evt_late"
    late["event_time"] = "2026-08-29T14:02:00Z"  # 1m12s antes do first (14:03:12), dentro de 2m
    late["status"] = "PENDING"
    late["decline"] = None
    r2 = ingest_event(late)
    assert r2.status == "ACCEPTED"
    assert r2.applied_to_current_state is False  # não regride estado atual


def test_out_of_order_beyond_tolerance_not_applied(valid_attempt):
    first = dict(valid_attempt)
    first["event_id"] = "evt_first"
    first["status"] = "PROCESSING"
    first["decline"] = None
    ingest_event(first)

    too_late = dict(valid_attempt)
    too_late["event_id"] = "evt_too_late"
    too_late["event_time"] = "2026-08-29T13:50:00Z"  # 13m antes, fora da tolerância de 2m
    too_late["status"] = "PENDING"
    too_late["decline"] = None
    result = ingest_event(too_late)
    assert result.status == "ACCEPTED"
    assert result.applied_to_current_state is False


def test_terminal_state_guard_blocks_further_updates(valid_attempt):
    terminal = dict(valid_attempt)
    terminal["event_id"] = "evt_terminal"
    terminal["status"] = "SUCCEEDED"
    terminal["decline"] = None
    ingest_event(terminal)

    later_update = dict(valid_attempt)
    later_update["event_id"] = "evt_after_terminal"
    later_update["event_time"] = (
        datetime.fromisoformat(valid_attempt["event_time"].replace("Z", "+00:00")) + timedelta(seconds=30)
    ).isoformat().replace("+00:00", "Z")
    later_update["status"] = "PENDING"
    later_update["decline"] = None
    result = ingest_event(later_update)
    assert result.applied_to_current_state is False
