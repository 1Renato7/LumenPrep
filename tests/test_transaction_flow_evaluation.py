"""TASK-EVAL-001 / LUM2-56 regression matrix for the transaction-first flow."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.aggregation import WindowMetrics
from app.api.transactions import BatchRequest, TransactionInput, _create_batch
from app.detection import detect_candidates
from app.ingestion.storage import CONNECTION_LOCK, get_connection
from app.rca import RcaHypothesis, rank_hypotheses
from app.simulation.background_traffic import generate_background_transactions
from app.simulation.transaction_outcomes import adapt_transaction
from app.worker.transaction_worker import run_batch_to_completion


def _input(*, method: str = "CARD") -> dict:
    is_card = method == "CARD"
    return {
        "merchant_id": "merchant_br_01",
        "provider_id": "provider_alpha",
        "issuer_bank": "bank_br_a",
        "country": "BR",
        "currency": "BRL",
        "amount_minor": 12990,
        "payment_method_category": method,
        "card_brand": "VISA" if is_card else None,
        "card_type": "CREDIT" if is_card else "NOT_APPLICABLE",
        "channel": "WEB",
    }


def _window(start: datetime, *, attempts: int, approval_rate: float, correlation_id: str) -> WindowMetrics:
    return WindowMetrics(
        window_start=start.isoformat().replace("+00:00", "Z"),
        window_end=(start + timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
        dimensions={"provider_id": "stripe", "country": "BR"},
        eligible_attempts=attempts,
        approved_attempts=round(attempts * approval_rate),
        unique_payments=attempts,
        approved_payments=round(attempts * approval_rate),
        amount_minor=attempts * 100,
        currency="BRL",
        approval_rate=approval_rate,
        payment_conversion=approval_rate,
        latency_p50_ms=60.0,
        latency_p95_ms=100.0,
        timeout_rate=0.01,
        decline_counts={"GENERIC": attempts - round(attempts * approval_rate)},
        data_quality=0.98,
        window_revision=1,
        correlation_id=correlation_id,
    )


def test_mixed_batch_reaches_success_failure_and_unknown(monkeypatch):
    ids = iter(("batch-eval-mixed", "corr-eval-mixed", "eval-0", "eval-1", "eval-unknown"))
    monkeypatch.setattr("app.api.transactions.uuid4", lambda: SimpleNamespace(hex=next(ids)))
    request = BatchRequest(
        schema_version="1.0",
        idempotency_key="eval-mixed-batch-0001",
        transactions=[
            TransactionInput(**_input()),
            TransactionInput(**_input()),
            TransactionInput(**_input(method="OTHER")),
        ],
    )

    accepted = _create_batch(request)
    run_batch_to_completion(accepted["batch_id"])

    with CONNECTION_LOCK:
        statuses = [
            row[0]
            for row in get_connection().execute(
                "SELECT status FROM transaction_records WHERE batch_id = ? ORDER BY batch_position",
                [accepted["batch_id"]],
            ).fetchall()
        ]
    assert statuses == ["SUCCEEDED", "FAILED", "UNKNOWN"]


def test_manual_submission_and_background_input_have_transport_independent_event_shape():
    seed, background_transactions = generate_background_transactions(1, seed=404)
    transaction = background_transactions[0]

    # A generated background input is exactly a public TransactionInput, so a
    # manual client can submit the identical facts through the batch boundary.
    manual = TransactionInput.model_validate(transaction).model_dump(mode="json")
    background = adapt_transaction(
        transaction,
        transaction_id="eval-background-input",
        correlation_id="corr-eval-transport",
        seed_context=str(seed),
    )
    submitted_manually = adapt_transaction(
        manual,
        transaction_id="eval-background-input",
        correlation_id="corr-eval-transport",
        seed_context=str(seed),
    )

    assert background == submitted_manually
    assert "outcome" not in transaction
    assert "status" not in transaction
    assert background.event["schema_version"] == "1.0"


def test_low_volume_window_emits_no_candidate_or_cause():
    start = datetime(2026, 7, 6, 10, tzinfo=timezone.utc)
    history = [
        _window(start + timedelta(weeks=index), attempts=100, approval_rate=0.9, correlation_id=f"history-{index}")
        for index in range(4)
    ]
    low_volume = _window(
        start + timedelta(weeks=4), attempts=11, approval_rate=0.0, correlation_id="corr-low-volume-eval"
    )

    candidates = detect_candidates([*history, low_volume], low_sample_attempts=12)
    assert candidates == []
    ranking = rank_hypotheses([])
    assert ranking.to_root_cause().status == "INCONCLUSIVE"
    assert ranking.to_root_cause().alternatives == []


def test_simultaneous_hypotheses_preserve_inconclusive_ranking():
    paths = [
        RcaHypothesis(
            correlation_id="corr-eval-tie",
            slice={"provider_id": "stripe"},
            score=0.8,
            support=80,
            candidate_ids=("provider",),
            evidence_refs=("evidence://provider",),
        ),
        RcaHypothesis(
            correlation_id="corr-eval-tie",
            slice={"issuer_bank": "bank_br_a"},
            score=0.8,
            support=80,
            candidate_ids=("issuer",),
            evidence_refs=("evidence://issuer",),
        ),
    ]

    ranking = rank_hypotheses(paths)
    assert ranking.ambiguous is True
    assert ranking.winner is None
    assert ranking.to_root_cause().status == "INCONCLUSIVE"
