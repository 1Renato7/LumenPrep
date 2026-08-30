#!/usr/bin/env python3
"""Prove a deployed Railway Incident used primary Graph RAG, read-only.

This probe deliberately stays separate from the isolated causal evaluator: it
never uploads the evaluator's CSV datasets or creates payment data. It only
uses the public read contracts already consumed by the web application.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


JsonFetcher = Callable[[str], object]
PRIMARY_MEMORY_STATUSES = {"MATCH_FOUND", "NO_PRECEDENT"}


class RailwayGraphRagProbeError(RuntimeError):
    """The deployed API did not provide auditable primary Graph RAG evidence."""


class _RejectRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, new_url):
        return None


def api_url(base_url: str, path: str) -> str:
    """Build an API URL whether the supplied base ends in `/v1` or not."""

    parsed = urlsplit(base_url)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("base_url must be an absolute HTTPS URL without query or fragment")
    base_path = parsed.path.rstrip("/")
    api_path = base_path if base_path.endswith("/v1") else f"{base_path}/v1"
    return f"https://{parsed.netloc}{api_path}/{path.lstrip('/')}"


def fetch_json(url: str, *, timeout_seconds: float = 20.0) -> object:
    """Fetch JSON without credentials, mutations, redirects, or retries."""

    request = Request(url, headers={"Accept": "application/json"}, method="GET")
    try:
        opener = build_opener(_RejectRedirects())
        with opener.open(request, timeout=timeout_seconds) as response:  # noqa: S310 -- URL is validated above.
            if response.status != 200:
                raise RailwayGraphRagProbeError(f"GET {url} returned HTTP {response.status}")
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise RailwayGraphRagProbeError(f"GET {url} returned HTTP {error.code}") from error
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RailwayGraphRagProbeError(f"GET {url} failed: {type(error).__name__}") from error


def probe_graph_rag(
    base_url: str,
    *,
    fetcher: JsonFetcher = fetch_json,
    max_incidents: int = 50,
) -> dict[str, object]:
    """Return a compact audit record only when deployed Graph RAG was primary."""

    if max_incidents < 1:
        raise ValueError("max_incidents must be at least 1")
    health = _mapping(fetcher(api_url(base_url, "health")), "health")
    dependencies = _mapping(health.get("dependencies"), "health.dependencies")
    if health.get("status") != "ok":
        raise RailwayGraphRagProbeError("Railway health is not ok")
    if dependencies.get("neo4j") != "configured":
        raise RailwayGraphRagProbeError("Railway does not report Neo4j as configured")

    incidents = fetcher(api_url(base_url, "incidents"))
    if not isinstance(incidents, list):
        raise RailwayGraphRagProbeError("GET /v1/incidents did not return a list")

    inspected: list[str] = []
    for item in incidents[:max_incidents]:
        incident = _mapping(item, "incident list item")
        incident_id = incident.get("incident_id")
        if not isinstance(incident_id, str) or not incident_id:
            continue
        inspected.append(incident_id)
        detail = _mapping(fetcher(api_url(base_url, f"incidents/{quote(incident_id, safe='')}")), "incident detail")
        memory = _mapping(detail.get("memory"), "incident detail.memory")
        trace = _mapping(memory.get("retrieval_trace"), "incident detail.memory.retrieval_trace")
        memory_status = memory.get("memory_status")
        if trace.get("fallback_used") is not False:
            continue
        if memory_status not in PRIMARY_MEMORY_STATUSES:
            continue
        if not isinstance(trace.get("candidate_count"), int) or not isinstance(trace.get("index_version"), str):
            raise RailwayGraphRagProbeError(f"Incident {incident_id} returned an incomplete retrieval trace")
        return {
            "schema_version": "1.0",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "api_base_url": _redacted_base_url(base_url),
            "incident_id": incident_id,
            "memory_status": memory_status,
            "retrieval_trace": {
                "filter_criteria": trace.get("cypher_filter"),
                "candidate_count": trace["candidate_count"],
                "index_version": trace["index_version"],
                "fallback_used": False,
            },
            "inspected_incident_count": len(inspected),
        }
    raise RailwayGraphRagProbeError(
        "No Incident with primary Graph RAG evidence was found; "
        f"inspected {len(inspected)} Incident(s) without accepting a fallback."
    )


def _mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RailwayGraphRagProbeError(f"{label} must be a JSON object")
    return value


def _redacted_base_url(value: str) -> str:
    """Keep the public origin/path only; user info is rejected before this point."""

    parsed = urlsplit(value)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True, help="public Railway API origin, with or without /v1")
    parser.add_argument("--output", type=Path, required=True, help="path for the compact proof artifact")
    parser.add_argument("--max-incidents", type=int, default=50)
    args = parser.parse_args()
    result = probe_graph_rag(args.base_url, max_incidents=args.max_incidents)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Primary Graph RAG confirmed for {result['incident_id']}; artifact: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
