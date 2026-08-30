from __future__ import annotations

import pytest

from scripts.probe_railway_graph_rag import RailwayGraphRagProbeError, api_url, probe_graph_rag


def _fetcher(values):
    def fetch(url):
        return values[url]

    return fetch


def test_probe_confirms_a_primary_railway_graph_trace():
    base = "https://lumen.up.railway.app"
    values = {
        api_url(base, "health"): {"status": "ok", "dependencies": {"neo4j": "configured"}},
        api_url(base, "incidents"): [{"incident_id": "inc_123"}],
        api_url(base, "incidents/inc_123"): {
            "memory": {
                "memory_status": "MATCH_FOUND",
                "retrieval_trace": {
                    "cypher_filter": "confirmation = 'HUMAN_CONFIRMED'",
                    "candidate_count": 1,
                    "index_version": "structured-v1",
                    "fallback_used": False,
                },
            }
        },
    }

    result = probe_graph_rag(base, fetcher=_fetcher(values))

    assert result["incident_id"] == "inc_123"
    assert result["memory_status"] == "MATCH_FOUND"
    assert result["retrieval_trace"]["fallback_used"] is False


def test_probe_rejects_an_honest_fallback_trace():
    base = "https://lumen.up.railway.app/v1"
    values = {
        api_url(base, "health"): {"status": "ok", "dependencies": {"neo4j": "configured"}},
        api_url(base, "incidents"): [{"incident_id": "inc_fallback"}],
        api_url(base, "incidents/inc_fallback"): {
            "memory": {
                "memory_status": "MATCH_FOUND",
                "retrieval_trace": {"fallback_used": True},
            }
        },
    }

    with pytest.raises(RailwayGraphRagProbeError, match="No Incident with primary Graph RAG"):
        probe_graph_rag(base, fetcher=_fetcher(values))


def test_probe_escapes_an_incident_id_before_building_the_detail_url():
    base = "https://lumen.up.railway.app"
    values = {
        api_url(base, "health"): {"status": "ok", "dependencies": {"neo4j": "configured"}},
        api_url(base, "incidents"): [{"incident_id": "inc/123"}],
        api_url(base, "incidents/inc%2F123"): {
            "memory": {
                "memory_status": "NO_PRECEDENT",
                "retrieval_trace": {
                    "cypher_filter": "confirmation = 'HUMAN_CONFIRMED'",
                    "candidate_count": 0,
                    "index_version": "structured-v1",
                    "fallback_used": False,
                },
            }
        },
    }

    result = probe_graph_rag(base, fetcher=_fetcher(values))

    assert result["incident_id"] == "inc/123"


def test_probe_rejects_unconfigured_graph_and_non_https_urls():
    base = "https://lumen.up.railway.app"

    with pytest.raises(ValueError, match="HTTPS"):
        api_url("http://localhost:8000", "health")
    with pytest.raises(ValueError, match="HTTPS"):
        api_url("https://token@example.com", "health")
    with pytest.raises(RailwayGraphRagProbeError, match="does not report Neo4j"):
        probe_graph_rag(
            base,
            fetcher=_fetcher({api_url(base, "health"): {"status": "ok", "dependencies": {"neo4j": "not_configured"}}}),
        )
