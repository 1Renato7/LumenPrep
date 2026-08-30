"""TASK-AGG-001. SQL/Python sobre DuckDB, janelas de 5min, dois denominadores (attempt/payment)."""

import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from itertools import combinations

from . import WindowMetrics

WINDOW_SECONDS = 300
TERMINAL_STATUSES = {"SUCCEEDED", "DECLINED", "ERROR", "TIMEOUT", "CANCELLED"}
# The causal cube is intentionally built from attributes known before the
# payment outcome. A decline code describes an outcome, so it is retained as
# evidence inside each slice rather than becoming a circular approval-rate key.
DIAGNOSIS_DIMENSIONS = (
    "merchant_id",
    "provider_id",
    "payment_method_category",
    "country",
    "issuer_bank_id",
)


def _window_bucket(event_time: datetime) -> datetime:
    epoch = int(event_time.timestamp())
    bucket = epoch - (epoch % WINDOW_SECONDS)
    return datetime.fromtimestamp(bucket, tz=timezone.utc)


def _iso_z(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * p
    f, c = int(k), min(int(k) + 1, len(s) - 1)
    if f == c:
        return s[f]
    return s[f] + (s[c] - s[f]) * (k - f)


def compute_windows(con) -> list[WindowMetrics]:
    current_rows = con.execute("SELECT canonical_json FROM canonical_attempts").fetchall()
    late_counts = dict(
        con.execute(
            "SELECT attempt_id, count(*) FROM canonical_events WHERE is_late GROUP BY attempt_id"
        ).fetchall()
    )

    groups: dict[tuple, list[dict]] = defaultdict(list)
    for (canonical_json,) in current_rows:
        c = json.loads(canonical_json)
        event_time = datetime.fromisoformat(c["event_time"].replace("Z", "+00:00"))
        bucket = _window_bucket(event_time)
        correlation_id = c.get("correlation_id") or "corr_unknown"
        currency = c.get("currency") or "USD"
        values = _diagnosis_values(c)
        # Every observed prefix/subset is a legitimate comparison target. This
        # avoids pre-materialising an empty Cartesian product while allowing an
        # incident to isolate merchant, provider, method, country or issuer.
        for size in range(0, len(DIAGNOSIS_DIMENSIONS) + 1):
            for names in combinations(DIAGNOSIS_DIMENSIONS, size):
                dims = tuple((name, values[name]) for name in names)
                groups[(bucket, dims, correlation_id, currency)].append(c)

    windows: list[WindowMetrics] = []
    for (bucket, dims, correlation_id, currency), attempts in groups.items():
        eligible = [a for a in attempts if a["status"] in TERMINAL_STATUSES]
        approved = [a for a in eligible if a["status"] == "SUCCEEDED"]
        payments = {a["payment_id"] for a in eligible}
        approved_payments = {a["payment_id"] for a in approved}
        latencies = [a["timing"]["total_latency_ms"] for a in eligible]

        decline_counts: dict[str, int] = defaultdict(int)
        decline_profile: dict[str, int] = defaultdict(int)
        for a in eligible:
            if a["status"] == "DECLINED" and a.get("decline"):
                key = a["decline"].get("category") or "UNKNOWN"
                decline_counts[key] += 1
            decline_profile[_decline_code(a)] += 1

        revision = 1 + sum(late_counts.get(a["attempt_id"], 0) for a in attempts)
        windows.append(
            WindowMetrics(
                window_start=_iso_z(bucket),
                window_end=_iso_z(bucket + timedelta(seconds=WINDOW_SECONDS)),
                dimensions={**dict(dims), "currency": currency},
                eligible_attempts=len(eligible),
                approved_attempts=len(approved),
                unique_payments=len(payments),
                approved_payments=len(approved_payments),
                amount_minor=sum(a["amount_minor"] for a in approved),
                currency=currency,
                approval_rate=(len(approved) / len(eligible)) if eligible else 0.0,
                payment_conversion=(len(approved_payments) / len(payments)) if payments else 0.0,
                latency_p50_ms=_percentile(latencies, 0.5),
                latency_p95_ms=_percentile(latencies, 0.95),
                timeout_rate=(sum(1 for a in eligible if a["status"] == "TIMEOUT") / len(eligible))
                if eligible
                else 0.0,
                decline_counts=dict(decline_counts),
                decline_profile=dict(decline_profile),
                data_quality=1.0,
                window_revision=revision,
                correlation_id=correlation_id,
            )
        )
    return windows


def compute_payment_conversion_observations(con, *, observation_seconds: int = 3600) -> list[WindowMetrics]:
    """Return closed, rolling conversion observations derived from canonical attempts.

    The denominator is the set of payment IDs in the preceding interval, not the
    number of attempts.  Therefore a retry can change the payment's terminal
    result but can never inflate the sample.  Each endpoint is a five-minute
    bucket boundary and only prior event times are read.
    """
    base = compute_windows(con)
    closed_through = _window_bucket(datetime.now(timezone.utc))
    endpoints = sorted({end for window in base if (end := _parse_window_end(window.window_end)) <= closed_through})
    current_rows = [json.loads(row[0]) for row in con.execute("SELECT canonical_json FROM canonical_attempts").fetchall()]
    observations: list[WindowMetrics] = []
    for end in endpoints:
        start = end - timedelta(seconds=observation_seconds)
        groups: dict[tuple[tuple[tuple[str, str], ...], str, str], list[dict]] = defaultdict(list)
        for attempt in current_rows:
            event_time = datetime.fromisoformat(attempt["event_time"].replace("Z", "+00:00"))
            if not start <= event_time < end or attempt["status"] not in TERMINAL_STATUSES:
                continue
            values = _diagnosis_values(attempt)
            correlation_id = attempt.get("correlation_id") or "corr_unknown"
            currency = attempt.get("currency") or "USD"
            for size in range(0, len(DIAGNOSIS_DIMENSIONS) + 1):
                for names in combinations(DIAGNOSIS_DIMENSIONS, size):
                    dims = tuple((name, values[name]) for name in names)
                    groups[(dims, correlation_id, currency)].append(attempt)
        for (dims, correlation_id, currency), attempts in groups.items():
            payments = {attempt["payment_id"] for attempt in attempts}
            approved_payments = {attempt["payment_id"] for attempt in attempts if attempt["status"] == "SUCCEEDED"}
            if not payments:
                continue
            observations.append(WindowMetrics(
                window_start=_iso_z(start), window_end=_iso_z(end), dimensions={**dict(dims), "currency": currency},
                eligible_attempts=len(attempts), approved_attempts=sum(a["status"] == "SUCCEEDED" for a in attempts),
                unique_payments=len(payments), approved_payments=len(approved_payments),
                amount_minor=sum(a["amount_minor"] for a in attempts if a["status"] == "SUCCEEDED"), currency=currency,
                approval_rate=sum(a["status"] == "SUCCEEDED" for a in attempts) / len(attempts),
                payment_conversion=len(approved_payments) / len(payments), latency_p50_ms=0.0, latency_p95_ms=0.0,
                timeout_rate=sum(a["status"] == "TIMEOUT" for a in attempts) / len(attempts), decline_counts={}, decline_profile={},
                data_quality=1.0, window_revision=1, correlation_id=correlation_id,
            ))
    return observations


def _parse_window_end(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _diagnosis_values(attempt: dict) -> dict[str, str]:
    card = attempt.get("card") or {}
    issuer = card.get("issuer_bank_id") or "NOT_APPLICABLE"
    return {
        "merchant_id": str(attempt.get("merchant_id") or "UNKNOWN_MERCHANT"),
        "provider_id": str(attempt.get("provider_id") or "UNKNOWN_PROVIDER"),
        "payment_method_category": str(attempt.get("payment_method_category") or "UNKNOWN_METHOD"),
        "country": str(attempt.get("country") or "UNKNOWN_COUNTRY"),
        "issuer_bank_id": str(issuer),
    }


def _decline_code(attempt: dict) -> str:
    decline = attempt.get("decline") or {}
    if attempt.get("status") == "SUCCEEDED":
        return "NO_DECLINE"
    return str(decline.get("normalized_code") or "UNMAPPED_DECLINE")
