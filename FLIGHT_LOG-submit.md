# Lumen — Flight Log

## Jury summary

This is the concise submission version of Lumen's decision log. The complete,
append-only record — including timestamps, owners, alternatives, validation and
revisions — remains in [`docs/flight-log.md`](docs/flight-log.md). This document
selects only the four code decisions that define how Lumen works.

Lumen is a transaction-first control tower: persisted synthetic payment facts flow
through deterministic processing, detection and RCA before memory or AI can offer a
human-only recommendation.

### 1. Transaction facts are the public input; diagnosis is derived

**Decision.** The public API accepts batches of 1–100 factual synthetic
`TransactionInput` records. Approval, conversion, outcome, impact and root-cause
hypotheses are produced by the backend, never supplied by the browser.

**Why it matters.** This makes the demonstrable path
`input → persistence → processing → evidence → Incident` real. The frontend cannot
predeclare the answer it later displays.

**Trade-off.** A small or ambiguous batch may create no Incident or an
`INCONCLUSIVE` one. That is intentional: the product prefers insufficient evidence
to a scripted diagnosis.

**Trace.** `FL-20260829-TEAM-015`; `CTR-TXN-001`.

### 2. Persist first, then process a durable transaction lifecycle

**Decision.** `POST /v1/transaction-batches` persists the batch and returns `202`;
`transaction_worker.py` then advances durable lifecycle stages, generates the
canonical event, derives Incidents and links them before recording a terminal state.

**Why it matters.** The transaction detail is an auditable record, not a browser timer:
a restart or failure can reconcile persisted work and the Incident link is tied to the
same correlation context.

**Trade-off.** The MVP uses DuckDB, an in-process worker and one deployable replica.
That favors reproducibility and a clear failure boundary over horizontal scale.

**Trace.** `FL-20260830-TEAM-024`; `CTR-TXL-001`.

### 3. Detection and RCA are deterministic, baseline-aware and allowed to abstain

**Decision.** Closed windows are compared with strictly prior historical baselines.
The detector applies volume/statistical guardrails; RCA ranks evidence over merchant,
provider, payment method, country and issuer-bank slices. Decline codes are supporting
post-outcome evidence, not a circular causal key.

**Why it matters.** Lumen separates a material drop from ordinary variation and
separates evidence from a claim of cause. The system can return no candidate or
`INCONCLUSIVE` rather than inventing an explanation.

**Trade-off.** Rare or new slices may remain unresolved until more evidence arrives.
We accept lower apparent coverage to avoid false confidence.

**Trace.** `FL-20260830-TEAM-025`; `CTR-INC-001`.

### 4. Memory and AI assist after the Incident; a human retains authority

**Decision.** An Incident is persisted before memory retrieval or an agent suggestion.
Neo4j is optional and stores/retrieves confirmed historical context; the agent receives
an immutable evidence pack and returns a separate, grounded `HUMAN_ONLY` suggestion.
Only an explicit human review can promote a precedent.

**Why it matters.** A precedent or fluent model response cannot rewrite the current
RCA, and an unavailable model cannot erase the evidence-backed Incident. No component
can retry, reroute, capture, refund or otherwise act on a payment.

**Trade-off.** The default experience is deliberately more constrained than autonomous
AI. Memory can be unavailable and an agent can return insufficient evidence.

**Trace.** `FL-20260830-TEAM-029`; `CTR-MEM-001`; `CTR-AGT-003`.

## Evidence and open limits

- The current review found **245 passing backend tests and two reproducible failures**:
  duplicate multi-metric Incidents in one causal slice, and non-identical deterministic
  behavior when optional fields are omitted versus `null`.
- Public Railway/Vercel, Volume/restart/CORS and browser acceptance evidence is
  **NOT RUN** in the current review.
- The demo incident read path uses fixtures when `DEMO_MODE=true`; normal mode reads
  persisted DuckDB Incidents.

These limits are intentional disclosure, not acceptance claims. The full decision
history and its evidence are available in [`docs/flight-log.md`](docs/flight-log.md).
