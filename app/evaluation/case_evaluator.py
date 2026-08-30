"""OpenAI-backed case evaluator with a fixed, local-only probe surface."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from uuid import uuid4

OPERATIONS = ("health", "neo4j", "catalog", "samples", "batch_roundtrip", "idempotency", "invalid_input")
CASE_SUMMARY = """Evaluate the Lumen payment-observability case. Inputs must be synthetic facts only; batches persist before 202; processing, diagnostics and errors are honest; idempotency is preserved; no historical precedent becomes a current cause or payment action."""
TRUTH_ORACLE_TESTS = (
    "tests/test_transaction_flow_evaluation.py",
    "tests/test_transaction_worker.py::test_terminal_records_validate_against_ctr_txl_001_schema",
    "tests/test_transaction_memory_evals.py",
    "tests/test_grounded_explainer.py",
    "tests/test_transaction_evidence_trace.py",
)


@dataclass(frozen=True)
class ProbeResult:
    name: str
    passed: bool
    evidence: str


@dataclass(frozen=True)
class EvaluationReport:
    probes: tuple[ProbeResult, ...]
    feedback: str
    model: str

    @property
    def passed(self) -> bool:
        return all(probe.passed for probe in self.probes)


class LocalApi(Protocol):
    def request(self, method: str, path: str, *, payload: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> tuple[int, dict[str, Any] | None]: ...


class Planner(Protocol):
    model: str
    def choose_operations(self, *, case_context: str, focus: str) -> list[str]: ...
    def write_feedback(self, *, case_context: str, focus: str, probes: list[ProbeResult]) -> str: ...


class LocalHttpApi:
    def __init__(self, base_url: str) -> None:
        parsed = urlsplit(base_url)
        if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"}:
            raise ValueError("The evaluator may target only a local http://localhost API.")
        self.base_url = f"{base_url.rstrip('/')}/"

    def request(self, method: str, path: str, *, payload: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> tuple[int, dict[str, Any] | None]:
        request_headers = {"Accept": "application/json", **(headers or {})}
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        if body is not None:
            request_headers["Content-Type"] = "application/json"
        request = Request(urljoin(self.base_url, path.lstrip("/")), data=body, headers=request_headers, method=method)
        try:
            with urlopen(request, timeout=15) as response:  # nosec B310: loopback URL is validated above
                return response.status, _json(response.read())
        except HTTPError as error:
            return error.code, _json(error.read())
        except URLError as error:
            return 0, {"error": type(error.reason).__name__}


class InProcessApi:
    """Adapter for FastAPI's test client; keeps evaluator runs isolated in memory."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def request(self, method: str, path: str, *, payload: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> tuple[int, dict[str, Any] | None]:
        response = self.client.request(method, path, json=payload, headers=headers)
        try:
            body = response.json()
            return response.status_code, body if isinstance(body, dict) else None
        except ValueError:
            return response.status_code, None


class OpenAIResponsesPlanner:
    """Responses API adapter: model selects only operation names, never raw URLs or commands."""

    def __init__(self, *, api_key: str, model: str) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required to run the case evaluator.")
        self.api_key, self.model = api_key, model

    def choose_operations(self, *, case_context: str, focus: str) -> list[str]:
        prompt = f"{CASE_SUMMARY}\nCase: {case_context[:12000]}\nFocus: {focus or 'whole case'}\nChoose relevant probes from {list(OPERATIONS)}. Return JSON only: {{\"operations\":[...]}}."
        response = self._post({"model": self.model, "instructions": "Be an evidence-based software evaluator.", "input": prompt, "store": False, "reasoning": {"effort": "minimal"}, "max_output_tokens": 2_000, "text": {"format": {"type": "json_schema", "name": "probe_plan", "strict": True, "schema": {"type": "object", "additionalProperties": False, "required": ["operations"], "properties": {"operations": {"type": "array", "minItems": 1, "maxItems": len(OPERATIONS), "items": {"type": "string", "enum": list(OPERATIONS)}}}}}}})
        chosen = json.loads(_output_text(response)).get("operations", [])
        return [name for name in dict.fromkeys(chosen) if name in OPERATIONS]

    def write_feedback(self, *, case_context: str, focus: str, probes: list[ProbeResult]) -> str:
        prompt = f"{CASE_SUMMARY}\nCase: {case_context[:12000]}\nFocus: {focus or 'whole case'}\nEvidence: {json.dumps([asdict(item) for item in probes], ensure_ascii=False)}\nWrite concise Portuguese feedback with evidence, gaps, and next test. State only what evidence proves. Do not state a verdict: the deterministic evaluator assigns it. Do not claim a requirement passed unless its probe explicitly proves it."
        return _output_text(self._post({"model": self.model, "instructions": "Be an evidence-based software evaluator.", "input": prompt, "store": False, "reasoning": {"effort": "minimal"}, "max_output_tokens": 2_000, "text": {"verbosity": "low"}}))

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        request = Request("https://api.openai.com/v1/responses", data=json.dumps(payload).encode("utf-8"), headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(request, timeout=45) as response:  # nosec B310: fixed OpenAI endpoint
                return json.loads(response.read())
        except HTTPError as error:
            raise RuntimeError(f"OpenAI Responses API returned {error.code}: {_json(error.read())}") from error
        except URLError as error:
            raise RuntimeError(f"OpenAI Responses API is unavailable: {type(error.reason).__name__}") from error


class CaseEvaluator:
    def __init__(self, *, api: LocalApi, planner: Planner, case_context: str, truth_root: Path | None = None) -> None:
        self.api, self.planner, self.case_context, self.truth_root = api, planner, case_context, truth_root

    def run(self, *, focus: str = "") -> EvaluationReport:
        operations = self.planner.choose_operations(case_context=self.case_context, focus=focus)
        if not operations:
            raise RuntimeError("The model did not choose any valid evaluation probe.")
        probes = []
        if self.truth_root:
            probes.extend((
                self._probe_truth_oracles(),
                self._probe_error_provenance(),
                self._probe_transport_equivalence(),
            ))
        probes.extend(getattr(self, f"_probe_{name}")() for name in operations)
        narrative = self.planner.write_feedback(case_context=self.case_context, focus=focus, probes=probes)
        verdict = "PRONTA COM LIMITAÇÕES" if all(probe.passed for probe in probes) else "NÃO PRONTA"
        return EvaluationReport(tuple(probes), f"Veredito: {verdict}\n\n{narrative}", self.planner.model)

    def _probe_truth_oracles(self) -> ProbeResult:
        """Run fixed negative tests; the model cannot alter the command or oracle."""
        assert self.truth_root is not None
        command = [sys.executable, "-m", "pytest", "-q", *TRUTH_ORACLE_TESTS]
        try:
            completed = subprocess.run(
                command, cwd=self.truth_root, capture_output=True, text=True, timeout=90, check=False
            )
        except subprocess.TimeoutExpired:
            return ProbeResult("truth_oracles", False, "Grounding oracle suite timed out after 90 seconds.")
        output = f"{completed.stdout}\n{completed.stderr}".strip()
        evidence = output[-1_500:] if output else "pytest produced no output"
        return ProbeResult("truth_oracles", completed.returncode == 0, evidence)

    def _probe_error_provenance(self) -> ProbeResult:
        """Ensure a simulated failure's public diagnosis has a real source trail."""
        from app.evaluation.provenance import audit_terminal_transaction
        from app.ingestion.storage import CONNECTION_LOCK, get_connection

        if not isinstance(self.api, InProcessApi):
            return ProbeResult(
                "error_provenance", False,
                "Error provenance requires the isolated in-process runtime so persisted events cannot come from a different database.",
            )
        key = f"qa-provenance-{uuid4().hex}"
        payload = _batch(key)
        payload["transactions"][0]["scenario_effects"] = {"timeout_rate": 1.0}
        created, accepted = self.api.request(
            "POST", "/v1/transaction-batches", payload=payload, headers={"Idempotency-Key": key}
        )
        if created != 202 or not accepted or not accepted.get("transaction_ids"):
            return _result("error_provenance", False, created, accepted)
        transaction_id = accepted["transaction_ids"][0]
        detail_status, record = self.api.request("GET", f"/v1/transactions/{transaction_id}")
        if detail_status != 200 or not record:
            return _result("error_provenance", False, detail_status, record)
        if record.get("status") != "FAILED":
            return ProbeResult("error_provenance", False, f"Controlled timeout did not produce FAILED: status={record.get('status')!r}")
        with CONNECTION_LOCK:
            con = get_connection()
            source_row = con.execute("SELECT input_json FROM transaction_records WHERE transaction_id = ?", [transaction_id]).fetchone()
            raw_row = con.execute("SELECT raw_json FROM raw_events WHERE event_id = ?", [f"evt_{transaction_id}"]).fetchone()
            canonical_row = con.execute("SELECT canonical_json FROM canonical_events WHERE event_id = ?", [f"evt_{transaction_id}"]).fetchone()
        source_input = _stored_event(source_row[0]) if source_row else None
        raw_event = _stored_event(raw_row[0]) if raw_row else None
        canonical_event = _stored_event(canonical_row[0]) if canonical_row else None
        audit = audit_terminal_transaction(
            record, source_input=source_input, raw_event=raw_event, canonical_event=canonical_event
        )
        evidence = "; ".join(audit.failures) if audit.failures else (
            f"transaction={transaction_id}, status={record.get('status')}, "
            f"provider_code={(record.get('outcome') or {}).get('provider_response_code')}, "
            f"evidence={(record.get('classification') or {}).get('evidence_ids')}"
        )
        return ProbeResult("error_provenance", audit.passed, evidence)

    def _probe_transport_equivalence(self) -> ProbeResult:
        """Same public facts must not acquire a different simulated result in transit."""
        from app.api.transactions import TransactionInput
        from app.simulation.background_traffic import generate_background_transactions
        from app.simulation.transaction_outcomes import adapt_transaction

        seed, generated = generate_background_transactions(1, seed=404)
        source = generated[0]
        boundary = TransactionInput.model_validate(source).model_dump(mode="json")
        source_result = adapt_transaction(
            source, transaction_id="qa-transport-equivalence", correlation_id="corr-qa-transport", seed_context=str(seed)
        )
        boundary_result = adapt_transaction(
            boundary, transaction_id="qa-transport-equivalence", correlation_id="corr-qa-transport", seed_context=str(seed)
        )
        if source_result == boundary_result:
            return ProbeResult("transport_equivalence", True, "Same public facts preserved the same simulated outcome and event.")
        return ProbeResult(
            "transport_equivalence",
            False,
            "Same public facts changed after TransactionInput serialization: "
            f"source_latency={source_result.outcome['latency_ms']}, boundary_latency={boundary_result.outcome['latency_ms']}. "
            "The provider simulation currently seeds from representation, not only semantic facts.",
        )

    def _probe_health(self) -> ProbeResult:
        status, body = self.api.request("GET", "/v1/health")
        return _result("health", status == 200 and (body or {}).get("status") == "ok", status, body)

    def _probe_catalog(self) -> ProbeResult:
        status, body = self.api.request("GET", "/v1/transaction-catalog")
        return _result("catalog", status == 200 and (body or {}).get("max_batch_size") == 100, status, body)

    def _probe_neo4j(self) -> ProbeResult:
        """Verify the real graph connection instead of merely checking an env var."""
        from app.config import settings
        from app.memory import Neo4jSettings, create_memory_runtime

        if not settings.neo4j_uri or not settings.neo4j_user or not settings.neo4j_password:
            return ProbeResult("neo4j", False, "Neo4j configuration is incomplete.")
        runtime = None
        try:
            runtime = create_memory_runtime(Neo4jSettings(
                uri=settings.neo4j_uri,
                user=settings.neo4j_user,
                password=settings.neo4j_password,
                database=settings.neo4j_database,
            ))
            healthy = runtime.service.primary.health()
            return ProbeResult("neo4j", healthy, "Neo4j query RETURN 1 succeeded." if healthy else "Neo4j did not answer the health query.")
        except Exception as error:
            return ProbeResult("neo4j", False, f"Neo4j health check failed: {type(error).__name__}")
        finally:
            if runtime is not None:
                runtime.close()

    def _probe_samples(self) -> ProbeResult:
        status, body = self.api.request("POST", "/v1/transaction-samples", payload={"schema_version": "1.0", "count": 1, "seed": 734})
        sample = ((body or {}).get("transactions") or [{}])[0]
        return _result("samples", status == 200 and "outcome" not in sample and "status" not in sample, status, body)

    def _probe_batch_roundtrip(self) -> ProbeResult:
        key, payload = f"qa-agent-{uuid4().hex}", None
        payload = _batch(key)
        created, accepted = self.api.request("POST", "/v1/transaction-batches", payload=payload, headers={"Idempotency-Key": key})
        if created != 202 or not accepted or not accepted.get("transaction_ids"):
            return _result("batch_roundtrip", False, created, accepted)
        detail, _ = self.api.request("GET", f"/v1/transactions/{accepted['transaction_ids'][0]}")
        batch, _ = self.api.request("GET", f"/v1/transaction-batches/{accepted['batch_id']}")
        return ProbeResult("batch_roundtrip", detail == batch == 200, f"create={created}, detail={detail}, batch={batch}")

    def _probe_idempotency(self) -> ProbeResult:
        key, payload = f"qa-agent-{uuid4().hex}", None
        payload = _batch(key)
        first, first_body = self.api.request("POST", "/v1/transaction-batches", payload=payload, headers={"Idempotency-Key": key})
        repeat, repeat_body = self.api.request("POST", "/v1/transaction-batches", payload=payload, headers={"Idempotency-Key": key})
        conflict, _ = self.api.request("POST", "/v1/transaction-batches", payload=_batch(key, amount_minor=7990), headers={"Idempotency-Key": key})
        passed = first == repeat == 202 and first_body and repeat_body and first_body.get("transaction_ids") == repeat_body.get("transaction_ids") and conflict == 409
        return ProbeResult("idempotency", bool(passed), f"first={first}, repeat={repeat}, conflict={conflict}")

    def _probe_invalid_input(self) -> ProbeResult:
        key = f"qa-agent-{uuid4().hex}"
        payload = _batch(key)
        payload["transactions"][0]["status"] = "SUCCEEDED"
        status, body = self.api.request("POST", "/v1/transaction-batches", payload=payload, headers={"Idempotency-Key": key})
        return _result("invalid_input", status == 422, status, body)


def _batch(key: str, *, amount_minor: int = 12990) -> dict[str, Any]:
    return {"schema_version": "1.0", "idempotency_key": key, "transactions": [{"merchant_id": "merchant_br_01", "provider_id": "provider_alpha", "issuer_bank": "bank_br_a", "country": "BR", "currency": "BRL", "amount_minor": amount_minor, "payment_method_category": "CARD", "card_brand": "VISA", "card_type": "CREDIT", "channel": "WEB"}]}


def _json(raw: bytes) -> dict[str, Any] | None:
    try:
        value = json.loads(raw)
        return value if isinstance(value, dict) else None
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _stored_event(raw: str) -> dict[str, Any] | None:
    try:
        value = json.loads(raw)
        return value if isinstance(value, dict) else None
    except (TypeError, json.JSONDecodeError):
        return None


def _output_text(payload: dict[str, Any]) -> str:
    if isinstance(payload.get("output_text"), str):
        return payload["output_text"]
    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                return content["text"]
    status = payload.get("status", "unknown")
    error = payload.get("error")
    incomplete = payload.get("incomplete_details")
    output_types = [item.get("type", "unknown") for item in payload.get("output", []) if isinstance(item, dict)]
    raise RuntimeError(f"OpenAI Responses API returned no output text (status={status}, error={error}, incomplete={incomplete}, output={output_types}).")


def _result(name: str, passed: bool, status: int, body: dict[str, Any] | None) -> ProbeResult:
    return ProbeResult(name, passed, f"HTTP {status}: {json.dumps(body, ensure_ascii=False)[:500] if body else 'no JSON body'}")
