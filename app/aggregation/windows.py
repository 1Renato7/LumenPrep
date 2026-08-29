"""TASK-AGG-001. SQL/Python sobre DuckDB, janelas de 5min, dois denominadores (attempt/payment)."""

import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from . import WindowMetrics

WINDOW_SECONDS = 300
TERMINAL_STATUSES = {"SUCCEEDED", "DECLINED", "ERROR", "TIMEOUT", "CANCELLED"}
DIMENSION_KEYS = ("provider_id", "country")


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
        dims = tuple(c.get(k) or "unknown" for k in DIMENSION_KEYS)
        groups[(bucket, dims)].append(c)

    windows: list[WindowMetrics] = []
    for (bucket, dims), attempts in groups.items():
        eligible = [a for a in attempts if a["status"] in TERMINAL_STATUSES]
        approved = [a for a in eligible if a["status"] == "SUCCEEDED"]
        payments = {a["payment_id"] for a in eligible}
        approved_payments = {a["payment_id"] for a in approved}
        latencies = [a["timing"]["total_latency_ms"] for a in eligible]

        decline_counts: dict[str, int] = defaultdict(int)
        for a in eligible:
            if a["status"] == "DECLINED" and a.get("decline"):
                key = a["decline"].get("category") or "UNKNOWN"
                decline_counts[key] += 1

        revision = 1 + sum(late_counts.get(a["attempt_id"], 0) for a in attempts)
        currency = attempts[0].get("currency", "BRL")

        windows.append(
            WindowMetrics(
                window_start=_iso_z(bucket),
                window_end=_iso_z(bucket + timedelta(seconds=WINDOW_SECONDS)),
                dimensions=dict(zip(DIMENSION_KEYS, dims)),
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
                data_quality=1.0,
                window_revision=revision,
                correlation_id=attempts[0].get("correlation_id", "corr_unknown"),
            )
        )
    return windows
