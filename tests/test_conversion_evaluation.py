from __future__ import annotations

import csv
from datetime import datetime, timedelta, timezone

import pytest

from app.evaluation import analyze_csv, native_result, retrieve_operational_memory
from app.memory import MemoryStatus
from app.memory.models import RetrievalTrace, SimilarIncidentResult


FIELDS = ["data_hora", "pais", "merchant", "moeda", "metodo_pagamento", "valor", "status_transacao", "motivo_recusa_erro", "etapa_funil", "versao", "canal", "emissor_sintetico"]


def _write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _row(index: int, *, after: bool, country: str = "BR", merchant: str = "alpha", method: str = "card", approved: bool = True):
    moment = datetime(2026, 7, 1, tzinfo=timezone.utc) + timedelta(days=15 if after else 1, minutes=index)
    return {"data_hora": moment.isoformat(), "pais": country, "merchant": merchant, "moeda": "BRL", "metodo_pagamento": method, "valor": "300" if index % 2 else "100", "status_transacao": "aprovada" if approved else "recusada", "motivo_recusa_erro": "recusa_generica" if not approved else "", "etapa_funil": "confirmacao", "versao": "app-5.5", "canal": "app", "emissor_sintetico": "issuer_orion"}


def test_country_drop_wins_over_smaller_country_merchant_slices(tmp_path):
    rows = []
    for after in (False, True):
        for country in ("BR", "MX", "CL"):
            for merchant in ("alpha", "beta", "gamma"):
                for index in range(60):
                    approved = not (after and country == "BR" and index < 28)
                    rows.append(_row(len(rows), after=after, country=country, merchant=merchant, approved=approved))
    source = tmp_path / "scenario.csv"
    _write(source, rows)

    result = analyze_csv(source)

    assert result.status == "SUPPORTED"
    assert result.category == "COUNTRY_DEGRADATION"
    assert result.scope == {"country": "BR"}


def test_traffic_mix_is_not_misclassified_as_a_method_failure(tmp_path):
    rows = []
    for after in (False, True):
        methods = ["card"] * (30 if after else 90) + ["bank_transfer"] * (170 if after else 110)
        for index, method in enumerate(methods):
            approved = index % (10 if method == "card" else 2) != 0
            rows.append(_row(len(rows), after=after, method=method, approved=approved))
    source = tmp_path / "scenario.csv"
    _write(source, rows)

    result = analyze_csv(source)

    assert result.status == "SUPPORTED"
    assert result.category == "TRAFFIC_MIX_SHIFT"
    assert result.scope["payment_method_category"] == "bank_transfer"


def test_new_technical_failure_signature_is_detected_without_a_baseline_occurrence(tmp_path):
    rows = []
    for after in (False, True):
        for index in range(180):
            failed = after and index < 80
            row = _row(len(rows), after=after, approved=not failed)
            if failed:
                row.update({"canal": "web", "etapa_funil": "envio_pagamento", "motivo_recusa_erro": "timeout_gateway"})
            else:
                row["canal"] = "web"
            rows.append(row)
    source = tmp_path / "scenario.csv"
    _write(source, rows)

    result = analyze_csv(source)

    assert result.status == "SUPPORTED"
    assert result.category == "TECHNICAL_CHECKOUT_FAILURE"
    assert result.scope["decline_reason"] == "timeout_gateway"


def test_native_result_never_claims_operational_graph_retrieval(tmp_path):
    rows = [_row(index, after=index >= 50, approved=True) for index in range(100)]
    source = tmp_path / "scenario.csv"
    _write(source, rows)

    bundle = native_result("scenario_01", analyze_csv(source))

    assert bundle["memory"]["retrieval_trace"]["fallback_used"] is True
    assert bundle["suggestion"]["recommended_actions"][0]["execution"] == "HUMAN_ONLY"


class _GraphService:
    def __init__(self, *, fallback_used: bool = False):
        self.fallback_used = fallback_used
        self.received = None

    def retrieve(self, incident):
        self.received = incident
        return SimilarIncidentResult(
            query_incident_id=incident.incident_id,
            memory_status=MemoryStatus.NO_PRECEDENT,
            matches=(),
            retrieval_trace=RetrievalTrace(
                cypher_filter="confirmation = 'HUMAN_CONFIRMED' AND shared_scope = true",
                candidate_count=0,
                embedding_model=None,
                index_version="structured-v1",
                fallback_used=self.fallback_used,
            ),
            correlation_id=incident.correlation_id,
        )


def test_operational_memory_trace_requires_a_non_fallback_runtime(tmp_path):
    source = tmp_path / "scenario.csv"
    _write(source, [_row(index, after=index >= 50, approved=True) for index in range(100)])
    service = _GraphService()

    memory = retrieve_operational_memory("scenario_01", analyze_csv(source), service)

    assert service.received.incident_id == "eval_scenario_01"
    assert memory["memory_status"] == "NO_PRECEDENT"
    assert memory["retrieval_trace"]["fallback_used"] is False


def test_operational_memory_rejects_fallback(tmp_path):
    source = tmp_path / "scenario.csv"
    _write(source, [_row(index, after=index >= 50, approved=True) for index in range(100)])

    with pytest.raises(RuntimeError, match="Graph RAG requirement"):
        retrieve_operational_memory("scenario_01", analyze_csv(source), _GraphService(fallback_used=True))


def test_csv_with_missing_required_column_is_rejected(tmp_path):
    source = tmp_path / "scenario.csv"
    source.write_text("data_hora\n2026-07-01T00:00:00+00:00\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required columns"):
        analyze_csv(source)
