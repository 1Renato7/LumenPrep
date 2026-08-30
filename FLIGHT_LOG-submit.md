# Lumen — Flight Log

## Decision log for submission

This is the jury-oriented version of Lumen’s decision log. It records the material choices that shaped the product, the credible alternatives, the trade-offs we accepted, and the evidence we have actually collected. The complete, append-only source history — including owners, timestamps, detailed alternatives, adenda, and validation records — is [`docs/flight-log.md`](docs/flight-log.md).

**Scope of this export:** decisions recorded through 30 August 2026. “Validated locally” never means “validated in Railway/Vercel production.” Assertions not backed by an executed check remain `NOT RUN`, `ASSUMPTION`, or `BLOCKED`.

## The product decision in one sentence

We chose a **transaction-first, evidence-first control tower**: deterministic statistics detect and isolate degradation; memory retrieves prior confirmed context; a grounded explainer recommends a human next step without changing facts or executing payments.

## What we optimized for

| Jury criterion | Lumen’s design response |
| --- | --- |
| Detect meaningful drops, not noise | Baseline-aware statistical detection and explicit low-volume abstention |
| Diagnose the real cause | Progressive multidimensional RCA over merchant, provider, method, country, issuer, and decline behavior |
| Explain with evidence | Evidence IDs, impact, time window, affected slice, alternatives, and limitations travel with the Incident |
| Handle simultaneous problems | Exact causal fingerprint and overlap rules keep distinct episodes separate |
| Recommend without remediation | Versioned playbooks and `HUMAN_ONLY` recommendations |
| Earn the uncertainty/recurrence bonuses honestly | `INCONCLUSIVE` is valid; memory is separate from current causal confidence |

## Architecture choices and trade-offs

### 1. Put deterministic evidence before AI

**Decision.** The detector and RCA calculate the current diagnosis from persisted payment data. Memory/RAG and the explainer run after an Incident exists and cannot promote a precedent or LLM output into a cause.

**Alternatives considered.** An agent per dimension or an LLM-led diagnosis would be fast to demo, but would turn narrative plausibility into a substitute for statistical evidence. A pure dashboard would be simpler, but would leave the operator to reconstruct causes manually.

**Trade-off accepted.** This creates more engineering work in aggregation, baselines, and evidence modeling; it deliberately gives up an impressive-but-unreliable “autonomous” diagnosis. The reward is an auditable answer that can say “insufficient evidence.”

**Trace.** `FL-20260829-TEAM-003`, `006`, `007`, `010`, `011`, `012`; `FL-20260829-RENATO-007`, `008`.

### 2. Move from scenario controls to transaction-first inputs

**Decision.** Users submit factual synthetic payment inputs (or request valid samples) in batches of 1–100. Approval rate, decline outcome, latency, baseline, impact, and cause are derived by the backend; they are not user-supplied knobs.

**Alternatives considered.** A public scenario/effect builder makes a rehearsed demo easy, but allows the user to inject the diagnosis. A single-transaction form cannot establish a meaningful baseline. Direct writes from a generator bypass validation and hide integration errors.

**Trade-off accepted.** The demo needs background traffic and a more disciplined data pipeline. In return, the same ingress boundary is used for manual input and harness-generated traffic, so the system demonstrates analysis of events rather than a predeclared story.

**Trace.** `FL-20260829-TEAM-013`–`017`, `023`; `FL-20260829-RENATO-003`, `005`; `FL-20260830-RENATO-008`, `009`.

### 3. Use a modular monolith with durable local-first storage

**Decision.** FastAPI, a worker, DuckDB/Parquet, aggregation, detection, and incident persistence form one MVP deployable; a Railway Volume stores state. Neo4j is only for confirmed-incident memory, not the payment event store.

**Alternatives considered.** Kafka/microservices and a dedicated warehouse would make larger-scale operations easier, but are disproportionate for a hackathon. A stateless service would simplify deployment but lose lifecycle continuity and restart recovery.

**Trade-off accepted.** The MVP is one stateful Railway replica and is not HA. This makes the flow reproducible and keeps data ownership clear. A future migration to a replicated store is an adapter change, not a reason to weaken the API contract.

**Trace.** `FL-20260829-TEAM-004`, `016`, `017`; `FL-20260829-ROGERIO-001`, `006`; `FL-20260830-ROGERIO-011`.

### 4. Detect progressively and abstain when the data cannot support a claim

**Decision.** Compute windows and baselines from canonical events; publish candidates and explore slices with deterministic beam/ranking logic. Low support, competing explanations, or weak concentration result in no claim or `INCONCLUSIVE` rather than an invented root cause.

**Alternatives considered.** Alerting on a global conversion change misses the intersection that explains the loss. Selecting the largest candidate always returns an answer, but confuses a hypothesis with evidence. Exhaustively materializing every dimensional combination is expensive and difficult to operate.

**Trade-off accepted.** A narrow or new combination can remain inconclusive until more evidence arrives. This is a deliberate product behavior and directly supports the challenge’s “admit uncertainty” bonus.

**Trace.** `FL-20260829-TEAM-005`, `006`; `FL-20260829-RENATO-002`, `006`, `007`, `008`, `009`.

### 5. Separate simultaneous incidents by full causal fingerprint

**Decision.** Candidates can share an Incident only if they have the same correlation ID, overlapping time window, and the same full slice fingerprint. Partial overlap — for example, the same country — is insufficient.

**Alternatives considered.** Grouping by batch/correlation ID alone is easy but merges unrelated incidents. Partial-scope matching can express a parent-child story, but can also collapse a Brazilian provider issue and a Mexican issuer issue into one false narrative.

**Trade-off accepted.** A real parent/child causal relationship may temporarily appear as separate Incidents. We chose false separation over false unification until the RCA publishes an explicit relationship.

**Trace.** `FL-20260829-ROGERIO-009`.

### 6. Keep money comparison honest

**Decision.** Estimate expected-approval shortfall and GMV at risk in the currency of the affected window. Prioritize only within the same-currency bucket; do not imply a global ranking without a versioned FX source.

**Alternatives considered.** Comparing raw minor units across BRL and MXN is simple but financially invalid. A live FX API would provide a global order but adds an external, time-varying dependency and harms reproducibility.

**Trade-off accepted.** The executive view may show separate currency buckets instead of one global list. The system remains explainable and does not manufacture comparability.

**Trace.** `FL-20260829-ROGERIO-008`.

### 7. Treat memory and recommendations as assistance, not authority

**Decision.** Retrieve only confirmed prior incidents, use structured precision-first matching before optional semantic reranking, ground every explanation in approved evidence/playbooks, and require `HUMAN_ONLY` execution.

**Alternatives considered.** Using a precedent as the current cause makes recurrence look more certain than it is. A free-form model response is flexible but cannot be audited. Automating routing/retries could reduce time to mitigation but exceeds the challenge and payment-safety scope.

**Trade-off accepted.** The explanation is constrained, and memory can be unavailable or yield no match. Those conditions are displayed explicitly instead of hidden behind a fluent answer.

**Trace.** `FL-20260829-TEAM-007`, `011`, `012`; `FL-20260829-ALTOE-001`–`005`, `010`.

### 8. Make source-of-truth and deployment boundaries explicit

**Decision.** The browser consumes one HTTPS API; it has no backend secrets and does not query DuckDB, Neo4j, or OpenAI. The API persists before returning `202`, owns lifecycle progress, and exposes CORS only to named origins.

**Alternatives considered.** A frontend that reads local fixtures or databases is fast to build but creates a false live demo. Permissive CORS or public stores reduce setup effort but widen exposure. A client-side progress timer looks responsive but lies about processing.

**Trade-off accepted.** Configuration and smoke testing are more involved, and live readiness depends on Railway/Vercel credentials. The production story has a single auditable data plane and honest degraded states.

**Trace.** `FL-20260829-TEAM-016`, `017`, `020`–`022`; `FL-20260829-ANDRE-003`–`006`; `FL-20260829-ROGERIO-006`.

## Evidence recorded so far

| Evidence | Result | Interpretation |
| --- | --- | --- |
| Contract validation, application compilation, and local Python suite | `PASS` — 168 tests recorded | Confirms local contracts and the transaction-to-Incident E2E without live fixtures |
| E2E path | `PASS` locally | Batch → terminal lifecycle → canonical event → detector/RCA → persisted `INCONCLUSIVE` Incident → grounded transaction detail |
| Simultaneous-incident tests | `PASS` locally | Different fingerprints remain separate; same fingerprint/multiple metrics can correlate |
| Web adapter state | `PARTIAL` | Input calls the live API; Logs, Detail, and Incidents remain visibly offline fixtures until their live adapter is integrated |
| Ingestion/materialization benchmark | 8,256 accepted events; 90 Parquet partitions; reproducible digest recorded | Evidence for the server→listener→Parquet path, not a production throughput claim |
| Holdout with independent ground truth | `NOT RUN` | No accuracy, false-incident, scope-exact-match, or abstention rate is claimed |
| Docker/Railway Volume/restart/CORS smoke | `NOT RUN` / externally blocked | Docker unavailable on the host; deployment credentials, public domain, and allowed origins were not provided |
| Vercel browser acceptance | `NOT RUN` / externally blocked | Requires the deployed API base URL and Vercel environment |

## Delivery risks we accepted and how we contain them

| Risk | Chosen containment | Trigger to revisit |
| --- | --- | --- |
| Sparse data could create a misleading diagnosis | Support thresholds and `INCONCLUSIVE`; do not let the explainer fill the gap | Holdout or a live trial shows excessive abstention or false alerts |
| One Railway Volume prevents replicas | Explicit one-replica MVP; persistence adapter boundary | HA or scale becomes a real requirement |
| Memory service is unavailable | Typed `MEMORY_UNAVAILABLE` with limited grounded fallback | Memory outage affects operator usefulness beyond the fallback |
| No FX feed | Separate currency buckets | A vetted, versioned FX source becomes available |
| Synthetic demo differs from production integration | Same public ingestion boundary for manual and harness traffic | Real Yuno/merchant fields and privacy requirements enter scope |

## Complete decision index

The following index accounts for all **60** material entries in the authoritative log. Read the linked source record for the full timestamp, owner, alternatives, trade-off, evidence, and revision trigger.

| Group | Decision IDs | Submission relevance |
| --- | --- | --- |
| Team foundations | `TEAM-001`–`004` | Append-only decision process; distinguish evaluation from history; make causal precision and recurrence core; select the original modular MVP |
| Data and diagnosis | `TEAM-005`–`007`, `010`–`012` | Vectorized historical volume; hierarchical statistical detector; Graph RAG/grounded explainer; current discovery before memory; independent uncertainty and memory states |
| Delivery and demo control | `TEAM-008`, `009`, `013`, `014`, `018`, `019` | Time/ownership guardrails; planning traceability; generic scenario construction; dual-stream rehearsal; safe replanning/integration |
| Transaction-first product | `TEAM-015`–`017`, `020`–`023` | Factual batches; Vercel/Railway split; durable progress; non-fabricated attention states; shared web integration; adapter sequencing |
| Frontend and operator clarity | `ANDRE-001`–`006` | Visual identity, causal-limit disclosure, recurrence presentation, contextual guidance, and safe integration order |
| Memory, traceability, and grounding | `ALTOE-001`–`006`, `008`–`010` | Precision-first retrieval, provenance before generation, human-only playbooks, deterministic fallback, transaction-to-Incident trace, Neo4j operations |
| Platform and safety | `ROGERIO-001`–`006` | Railway platform, open incident scope during stabilization, ownership recovery, safe Git integration, strict CORS/health |
| Simulation and RCA | `RENATO-001`–`009`, plus the separate `FL-20260830-RENATO-008` | Reproducible runtime/data, scenario contract, historical harness, outcome profiles, deterministic beam/ranking, invariant evaluation, server-bound Parquet materialization |
| Incident policy | `ROGERIO-007`–`009` | Alternatives do not replace causes; no implicit FX; exact fingerprint correlation |
| Live-recovery integration | `ROGERIO-010`–`012` | Two-lane recovery without new public contracts; Python parity; publish validated recovery into the shared base |

## How a juror can audit us

1. Start with [`README-submit.md`](README-submit.md) for the operational model and exact demo flow.
2. Inspect [`docs/plans/system-plan.md`](docs/plans/system-plan.md) for the current architecture and contract ownership.
3. Inspect [`contracts/v1/api.openapi.yaml`](contracts/v1/api.openapi.yaml) and the JSON schemas for the executable API promise.
4. Run the local validation commands in the README.
5. Read [`docs/flight-log.md`](docs/flight-log.md) for the full append-only decision evidence; this file intentionally summarizes it rather than replacing it.

## Final position

Lumen does not claim that a model can “know” a payment root cause from a few failed transactions. It earns an operator’s trust by carrying data through a repeatable pipeline, separating evidence from historical context, preserving uncertainty, and proposing only a human decision. That is the trade-off behind every major design choice in this log.
