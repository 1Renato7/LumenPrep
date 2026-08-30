import assert from "node:assert/strict";
import test from "node:test";

import {
  buildFixtureTransactionList,
  getOfflineTransaction,
  getOfflineTransactionList,
  hasProcessing,
  type OfflineFixtureError,
} from "../../components/transaction-log/fixture-source";
import { startProcessingPolling } from "../../components/transaction-log/polling";
import { buildTransactionUrl } from "../../components/transaction-log/url";
import { getOfflineIncident } from "../../components/incidents/fixture-source";
import { sortByMostRecent } from "../../lib/format/sort-by-date";

test("all transaction filters use their exact public status", () => {
  for (const status of ["SUCCEEDED", "FAILED", "PROCESSING", "UNKNOWN"] as const) {
    const list = buildFixtureTransactionList({ status });
    assert.ok(list.items.length > 0);
    assert.ok(list.items.every((item) => item.status === status));
  }

  const all = buildFixtureTransactionList({ status: "ALL" });
  assert.deepEqual(all.items.map((item) => item.status), ["PROCESSING", "UNKNOWN", "FAILED"]);
  assert.ok(Date.parse(all.items[0].updated_at) >= Date.parse(all.items[1].updated_at));
});

test("cursor keeps the filter and reaches the next newest-first page", () => {
  const first = buildFixtureTransactionList({ status: "ALL" });
  const second = buildFixtureTransactionList({ status: "ALL", cursor: first.next_cursor ?? undefined });
  assert.equal(first.next_cursor, "fixture-page-2");
  assert.ok(second.items.every((item) => Date.parse(item.updated_at) <= Date.parse(first.items.at(-1)?.updated_at ?? "")));
});

test("polling starts only for backend PROCESSING records and cancels cleanly", () => {
  let scheduled: (() => void) | undefined;
  let cleared = 0;
  let polls = 0;
  const timer = startProcessingPolling({
    hasProcessing: true,
    onPoll: () => { polls += 1; },
    setIntervalFn: (callback) => { scheduled = callback; return 7 as unknown as ReturnType<typeof setInterval>; },
    clearIntervalFn: () => { cleared += 1; },
  });
  assert.ok(timer);
  scheduled?.();
  assert.equal(polls, 1);
  timer?.cancel();
  assert.equal(cleared, 1);
  assert.equal(startProcessingPolling({ hasProcessing: false, onPoll: () => { polls += 1; } }), undefined);
});

test("progress is received from the fixture and never advanced locally", () => {
  const before = buildFixtureTransactionList({ status: "PROCESSING" }).items[0];
  const after = buildFixtureTransactionList({ status: "PROCESSING" }).items[0];
  assert.equal(before.processing.stage, "CLASSIFYING");
  assert.equal(before.processing.progress_percent, 45);
  assert.equal(after.processing.progress_percent, 45);
  assert.equal(hasProcessing([before]), true);
});

test("FAILED is a business outcome while PIPELINE_FAILED is UNKNOWN", async () => {
  const failed = await getOfflineTransaction("txn_demo_1001");
  const pipeline = await getOfflineTransaction("txn_pipeline_9001");
  assert.equal(failed.status, "FAILED");
  assert.equal(failed.outcome?.result, "FAILED");
  assert.equal(failed.processing.stage, "COMPLETE");
  assert.equal(pipeline.status, "UNKNOWN");
  assert.equal(pipeline.processing.stage, "PIPELINE_FAILED");
  assert.equal(pipeline.outcome, null);
  assert.equal(pipeline.classification, null);
});

test("refresh and deep link URL preserve unrelated query parameters", () => {
  const url = buildTransactionUrl(
    { batch_id: "batch_demo_0001", fixture: "stale", status: "FAILED", cursor: "fixture-page-2" },
    { status: "PROCESSING", cursor: null },
  );
  assert.equal(url, "/transactions?batch_id=batch_demo_0001&fixture=stale&status=PROCESSING");
});

test("a transaction without related incidents stays a normal empty state", async () => {
  const record = await getOfflineTransaction("txn_demo_1001");
  assert.deepEqual(record.classification?.related_incident_ids, []);
  assert.ok(record.classification?.evidence_ids.includes("evt_demo_1001_final"));
});

test("INCONCLUSIVE plus a historical match remains inconclusive", async () => {
  const detail = await getOfflineIncident("inc_current_mastercard_uncertain_002", "inconclusive");
  assert.equal(detail.incident.root_cause.status, "INCONCLUSIVE");
  assert.equal(detail.memory.memory_status, "MATCH_FOUND");
  assert.equal(detail.memory.matches[0].confirmation, "HUMAN_CONFIRMED");
  assert.equal(detail.explanation.execution, "HUMAN_ONLY");
  assert.ok(detail.explanation.recommended_action.length > 0);
  assert.ok(detail.explanation.limitations.length > 0);
});

test("incident detail exposes diagnosis, evidence, action, memory trace, and limitations", async () => {
  const detail = await getOfflineIncident("inc_current_mastercard_001");
  assert.ok(Object.keys(detail.incident.scope).length > 0);
  assert.ok(Object.keys(detail.incident.metrics).length > 0);
  assert.ok(Object.keys(detail.incident.root_cause.confidence_factors).length > 0);
  assert.ok(detail.incident.evidence.every((item) => item.evidence_id && item.statement && item.source_ref));
  assert.ok(detail.incident.recommendations.every((item) => item.execution === "HUMAN_ONLY"));
  assert.equal(detail.incident.recurrence_first_detected_at, "2026-08-22T14:06:00Z");
  assert.ok(detail.memory.retrieval_trace.index_version);
  assert.equal(detail.explanation.incident_id, detail.incident.incident_id);
  assert.ok(detail.explanation.evidence_ids.length > 0);
  const calculationLogs = detail.incident.evidence.filter((item) => item.kind !== "PAST_INCIDENT");
  assert.ok(calculationLogs.length > 0);
  assert.ok(calculationLogs.every((item) => item.source_ref.startsWith("duckdb://")));
  assert.ok(!calculationLogs.some((item) => item.kind === "PAST_INCIDENT"));
});

test("inconclusive diagnoses expose the current logs without treating history as a calculation input", async () => {
  const detail = await getOfflineIncident("inc_current_mastercard_uncertain_002", "inconclusive");
  const calculationLogs = detail.incident.evidence.filter((item) => item.kind !== "PAST_INCIDENT");

  assert.equal(detail.incident.root_cause.status, "INCONCLUSIVE");
  assert.deepEqual(calculationLogs.map((item) => item.evidence_id), ["evd_uncertain_current_rate", "evd_uncertain_low_coverage"]);
  assert.ok(detail.incident.evidence.some((item) => item.kind === "PAST_INCIDENT"));
});

test("memory unavailable is not equivalent to no precedent", async () => {
  const unavailable = await getOfflineIncident("inc_current_mastercard_001", "memory-unavailable");
  const noPrecedent = await getOfflineIncident("inc_new_provider_country_001", "no-precedent");
  assert.equal(unavailable.memory.memory_status, "MEMORY_UNAVAILABLE");
  assert.equal(noPrecedent.memory.memory_status, "NO_PRECEDENT");
});

test("incidents can be displayed newest-first by detection date", async () => {
  const older = await getOfflineIncident("inc_current_mastercard_001");
  const newer = await getOfflineIncident("inc_new_provider_country_001", "no-precedent");
  const sorted = sortByMostRecent([older.incident, newer.incident], (incident) => incident.detected_at);
  assert.ok(Date.parse(sorted[0].detected_at) >= Date.parse(sorted[1].detected_at));
});

test("loading, empty, error, and stale fixture modes remain distinguishable", async () => {
  const empty = await getOfflineTransactionList({ fixture: "empty" });
  const stale = await getOfflineTransactionList({ fixture: "stale" });
  assert.equal(empty.list.items.length, 0);
  assert.equal(stale.stale, true);
  await assert.rejects(
    getOfflineTransactionList({ fixture: "error" }),
    (error: unknown) => (error as OfflineFixtureError).name === "OfflineFixtureError",
  );
  const loading = getOfflineTransactionList({ fixture: "loading" });
  const result = await Promise.race([loading.then(() => "resolved"), Promise.resolve("pending")]);
  assert.equal(result, "pending");
});
