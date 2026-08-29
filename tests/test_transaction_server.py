from app.streaming import IngestionListener, TransactionServer


def test_server_assigns_monotonic_sequences_and_copies_payload(valid_attempt):
    server = TransactionServer()
    event = dict(valid_attempt)
    original_status = event["status"]

    receipt = server.publish([event])
    event["status"] = "DECLINED"

    assert receipt.accepted == 1
    assert receipt.first_sequence == receipt.last_sequence == 1
    stored = server.read_after(0)
    assert stored[0].sequence == 1
    assert stored[0].payload["status"] == original_status


def test_listener_consumes_in_order_and_advances_after_quarantine(valid_attempt):
    server = TransactionServer()
    listener = IngestionListener(server)
    invalid = {"event_id": "broken-event"}

    server.publish([invalid, valid_attempt])
    report = listener.consume_available(limit=10)

    assert report.consumed == 2
    assert report.quarantined == 1
    assert report.accepted == 1
    assert report.cursor == 2
