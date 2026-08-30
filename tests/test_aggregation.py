from app.aggregation import get_current_metrics
from app.ingestion import ingest_event


def _attempt(base, **overrides):
    a = dict(base)
    a.update(overrides)
    return a


def test_window_denominators_known_fixture(valid_attempt):
    base = dict(valid_attempt)
    base["provider_id"] = "stripe"
    base["country"] = "BR"
    base["decline"] = None

    # 4 attempts terminais na mesma janela de 5min: 3 SUCCEEDED (2 payments distintos), 1 TIMEOUT.
    ingest_event(_attempt(base, event_id="e1", attempt_id="a1", payment_id="p1", status="SUCCEEDED", amount_minor=1000))
    ingest_event(_attempt(base, event_id="e2", attempt_id="a2", payment_id="p1", status="SUCCEEDED", amount_minor=1000))
    ingest_event(_attempt(base, event_id="e3", attempt_id="a3", payment_id="p2", status="SUCCEEDED", amount_minor=2000))
    ingest_event(
        _attempt(
            base,
            event_id="e4",
            attempt_id="a4",
            payment_id="p3",
            status="TIMEOUT",
            amount_minor=500,
            decline=None,
        )
    )
    # 1 attempt não-terminal — não deve entrar nos denominadores.
    ingest_event(_attempt(base, event_id="e5", attempt_id="a5", payment_id="p4", status="PROCESSING", decline=None))

    windows = get_current_metrics(dimensions={"provider_id": "stripe", "country": "BR"})
    assert len(windows) == 1
    w = windows[0]

    assert w.eligible_attempts == 4  # 3 SUCCEEDED + 1 TIMEOUT, exclui PROCESSING
    assert w.approved_attempts == 3
    assert w.unique_payments == 3  # p1 (2x), p2, p3 -> 3 payments distintos elegíveis
    assert w.approved_payments == 2  # p1, p2
    assert w.amount_minor == 4000  # soma dos 3 SUCCEEDED (1000+1000+2000)
    assert w.approval_rate == 3 / 4
    assert w.payment_conversion == 2 / 3
    assert w.timeout_rate == 1 / 4


def test_get_current_metrics_filters_by_dimension(valid_attempt):
    base = dict(valid_attempt)
    base["decline"] = None
    ingest_event(_attempt(base, event_id="e1", attempt_id="a1", provider_id="stripe", country="BR", status="SUCCEEDED"))
    ingest_event(_attempt(base, event_id="e2", attempt_id="a2", provider_id="adyen", country="MX", status="SUCCEEDED"))

    stripe_only = get_current_metrics(dimensions={"provider_id": "stripe"})
    assert len(stripe_only) == 1
    assert stripe_only[0].dimensions["provider_id"] == "stripe"


def test_same_slice_and_bucket_remain_isolated_by_correlation(valid_attempt):
    base = dict(valid_attempt)
    base.update(provider_id="stripe", country="BR", decline=None, status="SUCCEEDED")
    ingest_event(_attempt(base, event_id="corr-a-event", attempt_id="corr-a-attempt", payment_id="corr-a-payment", correlation_id="corr-a"))
    ingest_event(_attempt(base, event_id="corr-b-event", attempt_id="corr-b-attempt", payment_id="corr-b-payment", correlation_id="corr-b"))

    windows = get_current_metrics(dimensions={"provider_id": "stripe", "country": "BR"})

    assert len(windows) == 2
    assert {window.correlation_id for window in windows} == {"corr-a", "corr-b"}
    assert all(window.eligible_attempts == 1 for window in windows)


def test_same_correlation_slice_and_bucket_never_mix_currencies(valid_attempt):
    brl = dict(valid_attempt)
    brl.update(provider_id="stripe", country="BR", currency="BRL", amount_minor=10_000, decline=None, status="SUCCEEDED")
    mxn = dict(brl)
    mxn.update(currency="MXN", amount_minor=20_000)
    ingest_event(_attempt(brl, event_id="brl-event", attempt_id="brl-attempt", payment_id="brl-payment", correlation_id="corr-mixed"))
    ingest_event(_attempt(mxn, event_id="mxn-event", attempt_id="mxn-attempt", payment_id="mxn-payment", correlation_id="corr-mixed"))

    windows = get_current_metrics(dimensions={"provider_id": "stripe", "country": "BR"})

    assert len(windows) == 2
    by_currency = {window.currency: window for window in windows}
    assert by_currency["BRL"].dimensions["currency"] == "BRL"
    assert by_currency["BRL"].amount_minor == 10_000
    assert by_currency["MXN"].dimensions["currency"] == "MXN"
    assert by_currency["MXN"].amount_minor == 20_000
