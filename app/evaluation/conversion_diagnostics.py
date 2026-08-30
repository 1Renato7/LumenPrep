"""Evidence-first diagnostics for isolated synthetic conversion evaluations.

The evaluator receives an alert package and its referenced CSV, never hidden
labels.  It compares two temporal cohorts and ranks explainable segments using
only fields available before or at the terminal transaction outcome.  This is
an offline harness, not a production API or a replacement for the streaming
detector.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from math import sqrt
from pathlib import Path
from statistics import quantiles
from typing import Any, Iterable, Protocol


REQUIRED_COLUMNS = {
    "data_hora",
    "pais",
    "merchant",
    "moeda",
    "metodo_pagamento",
    "valor",
    "status_transacao",
    "motivo_recusa_erro",
    "etapa_funil",
    "versao",
    "canal",
    "emissor_sintetico",
}
MIN_SEGMENT_SAMPLE = 20
STRONG_SCORE = 3.0


@dataclass(frozen=True)
class Record:
    occurred_at: datetime
    country: str
    merchant: str
    currency: str
    method: str
    amount: float
    approved: bool
    reason: str
    stage: str
    version: str
    channel: str
    issuer: str


@dataclass(frozen=True)
class Candidate:
    kind: str
    values: tuple[str, ...]
    before_rate: float
    after_rate: float
    before_count: int
    after_count: int

    @property
    def drop(self) -> float:
        return self.before_rate - self.after_rate

    @property
    def score(self) -> float:
        return max(self.drop, 0.0) * sqrt(min(self.before_count, self.after_count))


@dataclass(frozen=True)
class Diagnosis:
    status: str
    category: str | None
    confidence: float
    scope: dict[str, str]
    evidence: tuple[str, ...]
    alternatives: tuple[str, ...]


class MemoryRetriever(Protocol):
    """Small port used by the evaluator to prove an operational retrieval."""

    def retrieve(self, incident: Any) -> Any: ...


def analyze_csv(path: Path) -> Diagnosis:
    """Diagnose one CSV without consulting any companion metadata or labels."""

    records = _read_records(path)
    before, after = _temporal_cohorts(records)
    overall = _candidate("overall", (), before, after)
    candidates = _segment_candidates(before, after, records)
    strong = [item for item in candidates if item.score >= STRONG_SCORE]

    technical = _technical_candidate(before, after)
    issuer = _issuer_candidate(before, after)
    mix = _traffic_mix_candidate(before, after)

    special = [item for item in (technical, issuer) if item is not None and item.score >= STRONG_SCORE]
    if special:
        return _supported(max(special, key=lambda item: item.score), candidates)

    # A composition change can make country and merchant aggregates look bad.
    # Explain it away before selecting a correlating segment.
    if mix is not None:
        return _supported(mix, candidates)

    if strong:
        return _supported(max(strong, key=lambda item: item.score), candidates)

    # A small aggregate movement with two or more weak explanations is evidence
    # of ambiguity, not a license to promote the largest random slice.
    weak = sorted(
        (item for item in [*candidates, *_candidates_for("issuer_signal", before, after, lambda record: (record.issuer,))] if item.score >= 1.0),
        key=lambda item: item.score,
        reverse=True,
    )
    if len({item.kind for item in weak[:3]}) >= 2:
        return Diagnosis(
            status="INCONCLUSIVE",
            category=None,
            confidence=0.35,
            scope={},
            evidence=(
                _rate_statement("Conversão agregada", overall),
                "Existem sinais segmentados concorrentes abaixo do limiar de atribuição única.",
            ),
            alternatives=tuple(_category_label(item.kind) for item in weak[:3]),
        )

    return Diagnosis(
        status="NO_INCIDENT",
        category=None,
        confidence=0.8,
        scope={},
        evidence=(
            _rate_statement("Conversão agregada", overall),
            "Nenhum recorte atingiu o limiar de queda material e sustentada.",
        ),
        alternatives=("Monitorar novas janelas antes de atribuir uma causa.",),
    )


def native_result(
    scenario_id: str,
    diagnosis: Diagnosis,
    *,
    operational_memory: dict[str, object] | None = None,
) -> dict[str, object]:
    """Return the documented native bundle consumed by the LumenPrep adapter."""

    incident: dict[str, object] | None
    if diagnosis.status == "NO_INCIDENT":
        incident = None
    else:
        incident = {
            "incident_id": f"eval_{scenario_id}",
            "scope": diagnosis.scope,
            "root_cause": {
                "status": diagnosis.status,
                "category": diagnosis.category,
                "confidence": diagnosis.confidence,
                "alternatives": [{"category": item} for item in diagnosis.alternatives],
            },
            "evidence": [
                {"statement": statement, "source_ref": f"evaluation://{scenario_id}"}
                for statement in diagnosis.evidence
            ],
        }
    offline_memory = {
        "memory_status": "MEMORY_UNAVAILABLE",
        "retrieval_trace": {
            "schema_version": "1.0",
            "incident_id": f"eval_{scenario_id}",
            "status": "MEMORY_UNAVAILABLE",
            "filter_criteria": "offline evaluation; no operational memory queried",
            "candidate_count": 0,
            "index_version": "offline-evaluator-v1",
            "fallback_used": True,
            "sources": [],
            "authorized_evidence_ids": [],
        },
    }
    memory = operational_memory or offline_memory
    trace = memory["retrieval_trace"]
    return {
        "incident": incident,
        "memory": memory,
        "suggestion": {
            "status": "INSUFFICIENT_EVIDENCE" if diagnosis.status == "INCONCLUSIVE" else "SUGGESTED",
            "confidence": diagnosis.confidence,
            "reasons": [{"statement": statement} for statement in diagnosis.evidence],
            "recommended_actions": [
                {"action": "Validar a janela, o tamanho da amostra e o recorte afetado antes de agir.", "execution": "HUMAN_ONLY"}
            ],
            "retrieval_trace": trace,
        },
    }


def retrieve_operational_memory(
    scenario_id: str,
    diagnosis: Diagnosis,
    retriever: MemoryRetriever,
) -> dict[str, object]:
    """Retrieve through the real memory runtime and reject every fallback.

    The function deliberately accepts the runtime service as a port so unit
    tests can prove the gate without treating an in-memory repository as Graph
    RAG. The runner only calls it when ``--require-graph-rag`` is explicit.
    """

    from app.memory import Incident

    incident = Incident(
        incident_id=f"eval_{scenario_id}",
        detected_at=datetime.now(timezone.utc),
        scope={key: (value,) for key, value in diagnosis.scope.items()},
        metrics={},
        root_cause_status=diagnosis.status,
        root_cause_category=diagnosis.category,
        evidence_ids=(),
        correlation_id=f"evaluation-{scenario_id}",
    )
    result = retriever.retrieve(incident)
    trace = result.retrieval_trace
    if trace.fallback_used or result.memory_status.value == "MEMORY_UNAVAILABLE":
        raise RuntimeError(
            "Graph RAG requirement was not met: memory retrieval used a fallback or was unavailable."
        )
    sources = [
        {
            "source": "incident_memory",
            "source_id": match.incident_id,
            "confirmed_cause": match.confirmed_cause,
        }
        for match in result.matches
    ]
    evidence_ids = sorted({evidence_id for match in result.matches for evidence_id in match.evidence_ids})
    return {
        "memory_status": result.memory_status.value,
        "retrieval_trace": {
            "schema_version": "1.0",
            "incident_id": incident.incident_id,
            "status": result.memory_status.value,
            "filter_criteria": trace.cypher_filter,
            "candidate_count": trace.candidate_count,
            "index_version": trace.index_version,
            "fallback_used": False,
            "sources": sources,
            "authorized_evidence_ids": evidence_ids,
        },
    }


def _read_records(path: Path) -> list[Record]:
    with path.open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        headers = set(reader.fieldnames or ())
        missing = REQUIRED_COLUMNS - headers
        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")
        records = [_record(row) for row in reader]
    if len(records) < MIN_SEGMENT_SAMPLE * 2:
        raise ValueError("CSV has insufficient records for a temporal comparison")
    return records


def _record(row: dict[str, str]) -> Record:
    try:
        occurred_at = datetime.fromisoformat(row["data_hora"].replace("Z", "+00:00"))
        amount = float(row["valor"])
    except (TypeError, ValueError) as error:
        raise ValueError("CSV contains an invalid timestamp or amount") from error
    return Record(
        occurred_at=occurred_at,
        country=row["pais"].strip(), merchant=row["merchant"].strip(), currency=row["moeda"].strip(),
        method=row["metodo_pagamento"].strip(), amount=amount, approved=row["status_transacao"].strip().lower() == "aprovada",
        reason=row["motivo_recusa_erro"].strip(), stage=row["etapa_funil"].strip(), version=row["versao"].strip(),
        channel=row["canal"].strip(), issuer=row["emissor_sintetico"].strip(),
    )


def _temporal_cohorts(records: list[Record]) -> tuple[list[Record], list[Record]]:
    start, end = min(item.occurred_at for item in records), max(item.occurred_at for item in records)
    midpoint = start + (end - start) / 2
    before = [item for item in records if item.occurred_at < midpoint]
    after = [item for item in records if item.occurred_at >= midpoint]
    if min(len(before), len(after)) < MIN_SEGMENT_SAMPLE:
        raise ValueError("CSV cannot be split into two viable temporal cohorts")
    return before, after


def _segment_candidates(before: list[Record], after: list[Record], all_records: list[Record]) -> list[Candidate]:
    result: list[Candidate] = []
    dimensions = {
        "country": lambda item: (item.country,),
        "merchant": lambda item: (item.merchant,),
        "country_merchant": lambda item: (item.country, item.merchant),
        "version_channel": lambda item: (item.version, item.channel),
    }
    for kind, selector in dimensions.items():
        result.extend(_candidates_for(kind, before, after, selector))

    threshold = quantiles([item.amount for item in all_records], n=4, method="inclusive")[2]
    result.extend(_candidates_for("currency_ticket", before, after, lambda item: (item.currency, "HIGH") if item.amount >= threshold else None))
    return result


def _technical_candidate(before: list[Record], after: list[Record]) -> Candidate | None:
    candidates: list[Candidate] = []
    keys = {(item.channel, item.stage, item.reason) for item in after if _technical_reason(item.reason)}
    for channel, stage, reason in keys:
        before_population = [item for item in before if item.channel == channel]
        after_population = [item for item in after if item.channel == channel]
        if min(len(before_population), len(after_population)) < MIN_SEGMENT_SAMPLE:
            continue
        baseline_rate = sum(item.stage == stage and item.reason == reason for item in before_population) / len(before_population)
        current_rate = sum(item.stage == stage and item.reason == reason for item in after_population) / len(after_population)
        if current_rate > baseline_rate:
            # Candidate.drop is normally a conversion drop.  For a technical
            # signature it instead represents the increase in failure share.
            candidates.append(Candidate("technical_checkout", (channel, stage, reason), current_rate, baseline_rate, len(before_population), len(after_population)))
    return max(candidates, key=lambda item: item.score) if candidates else None


def _issuer_candidate(before: list[Record], after: list[Record]) -> Candidate | None:
    candidates = _candidates_for("issuer_decline", before, after, lambda item: (item.issuer,))
    candidates = [item for item in candidates if _dominant_issuer_reason(after, item.values[0])]
    return max(candidates, key=lambda item: item.score) if candidates else None


def _traffic_mix_candidate(before: list[Record], after: list[Record]) -> Candidate | None:
    before_shares, after_shares = _shares(before, lambda item: item.method), _shares(after, lambda item: item.method)
    # The affected mix component is the method whose share grew.  Choosing the
    # absolute delta would label its displaced counterpart instead.
    shifted = [(method, after_shares.get(method, 0.0) - before_shares.get(method, 0.0)) for method in set(before_shares) | set(after_shares)]
    method, shift = max(shifted, key=lambda item: item[1])
    within_method = _candidates_for("method", before, after, lambda item: (item.method,))
    max_within = max((item.score for item in within_method), default=0.0)
    if shift < 0.12 or max_within >= STRONG_SCORE:
        return None
    return Candidate("traffic_mix", (method,), 1.0 - before_shares.get(method, 0.0), 1.0 - after_shares.get(method, 0.0), len(before), len(after))


def _candidates_for(kind: str, before: Iterable[Record], after: Iterable[Record], selector) -> list[Candidate]:
    before_groups, after_groups = _group(before, selector), _group(after, selector)
    result: list[Candidate] = []
    for values in before_groups.keys() & after_groups.keys():
        candidate = _candidate(kind, values, before_groups[values], after_groups[values])
        if min(candidate.before_count, candidate.after_count) >= MIN_SEGMENT_SAMPLE:
            result.append(candidate)
    return result


def _group(records: Iterable[Record], selector) -> dict[tuple[str, ...], list[Record]]:
    groups: dict[tuple[str, ...], list[Record]] = defaultdict(list)
    for item in records:
        key = selector(item)
        if key is not None:
            groups[key].append(item)
    return groups


def _candidate(kind: str, values: tuple[str, ...], before: Iterable[Record], after: Iterable[Record]) -> Candidate:
    before_list, after_list = list(before), list(after)
    return Candidate(
        kind=kind, values=values,
        before_rate=sum(item.approved for item in before_list) / len(before_list),
        after_rate=sum(item.approved for item in after_list) / len(after_list),
        before_count=len(before_list), after_count=len(after_list),
    )


def _supported(winner: Candidate, all_candidates: list[Candidate]) -> Diagnosis:
    scope = _scope(winner)
    alternatives = tuple(
        _category_label(item.kind) for item in sorted(all_candidates, key=lambda item: item.score, reverse=True)
        if item != winner and item.score >= max(0.45, winner.score * 0.45)
    )[:2]
    label = _scope_label(winner)
    evidence = (
        _rate_statement(f"Recorte {label}", winner),
        f"Baseline e janela atual têm respectivamente {winner.before_count} e {winner.after_count} transações no recorte {label}.",
    )
    if winner.kind == "traffic_mix":
        evidence = (
            f"O mix de método {winner.values[0]} mudou de {(1 - winner.before_rate):.1%} no baseline para {(1 - winner.after_rate):.1%} na janela atual.",
            "As taxas de conversão dentro de cada método não atingiram o limiar de queda causal.",
        )
    if winner.kind == "technical_checkout":
        evidence = (
            f"O motivo técnico {winner.values[2]} no estágio {winner.values[1]} subiu de {winner.after_rate:.1%} no baseline para {winner.before_rate:.1%} na janela atual.",
            f"O sinal está restrito ao canal {winner.values[0]} e deve ser validado por uma pessoa antes de qualquer ação.",
        )
    if winner.kind == "issuer_decline":
        evidence = (*evidence, f"Recusas do emissor {winner.values[0]} cresceram na janela atual.")
    return Diagnosis(
        status="SUPPORTED", category=_category(winner.kind), confidence=min(0.95, 0.55 + winner.score / 12),
        scope=scope, evidence=evidence, alternatives=alternatives or ("Validar segmentos vizinhos para descartar propagação.",),
    )


def _scope(candidate: Candidate) -> dict[str, str]:
    keys = {
        "country": ("country",), "merchant": ("merchant",), "country_merchant": ("country", "merchant"),
        "issuer_decline": ("issuer",), "technical_checkout": ("channel", "checkout_stage", "decline_reason"),
        "traffic_mix": ("payment_method_category",), "version_channel": ("version", "channel"),
        "currency_ticket": ("currency", "amount_band"),
    }[candidate.kind]
    return dict(zip(keys, candidate.values, strict=True))


def _category(kind: str) -> str:
    return {
        "country": "COUNTRY_DEGRADATION", "merchant": "MERCHANT_DEGRADATION",
        "country_merchant": "COUNTRY_MERCHANT_DEGRADATION", "issuer_decline": "ISSUER_OUTAGE",
        "technical_checkout": "TECHNICAL_CHECKOUT_FAILURE", "traffic_mix": "TRAFFIC_MIX_SHIFT",
        "version_channel": "VERSION_CHANNEL_DEGRADATION", "currency_ticket": "CURRENCY_TICKET_DEGRADATION",
    }[kind]


def _category_label(kind: str) -> str:
    if kind == "issuer_signal":
        return "ISSUER_OUTAGE"
    return _category(kind) if kind in {"country", "merchant", "country_merchant", "issuer_decline", "technical_checkout", "traffic_mix", "version_channel", "currency_ticket"} else kind


def _scope_label(candidate: Candidate) -> str:
    return ", ".join(f"{key}={value}" for key, value in _scope(candidate).items())


def _rate_statement(label: str, candidate: Candidate) -> str:
    return f"{label}: conversão caiu de {candidate.before_rate:.1%} no baseline para {candidate.after_rate:.1%} na janela atual."


def _technical_reason(reason: str) -> bool:
    lowered = reason.lower()
    return "timeout" in lowered or "error" in lowered or "erro" in lowered


def _dominant_issuer_reason(records: Iterable[Record], issuer: str) -> bool:
    reasons = Counter(
        item.reason for item in records
        if item.issuer == issuer and item.reason and _issuer_reason(item.reason)
    )
    return bool(reasons) and reasons.most_common(1)[0][1] >= MIN_SEGMENT_SAMPLE


def _issuer_reason(reason: str) -> bool:
    lowered = reason.lower()
    return "issuer" in lowered or "do_not_honor" in lowered or "insufficient_funds" in lowered


def _shares(records: Iterable[Record], selector) -> dict[str, float]:
    values = list(records)
    counts = Counter(selector(item) for item in values)
    return {key: count / len(values) for key, count in counts.items()}
