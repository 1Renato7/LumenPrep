import assert from "node:assert/strict";
import test from "node:test";

import incidentFixture from "../../../contracts/fixtures/incident-mastercard-recurrence.json";
import explanationFixture from "../../../contracts/fixtures/explanation-bundle.json";
import memoryFixture from "../../../contracts/fixtures/similar-incidents.json";
import { isRejectedIncident, selectAuthorizedIncidentLink } from "../../components/transaction-detail/grounding";
import type { TransactionIncidentDetail } from "../../lib/api/types";

test("PARTIAL grounding never substitutes an authorized Incident for a rejected classification ID", () => {
  const authorized = { incident: incidentFixture, memory: memoryFixture, explanation: explanationFixture, evidence_ids: ["evt_1"], limitations: [] } as TransactionIncidentDetail["incidents"][number];
  const grounding: TransactionIncidentDetail = {
    schema_version: "1.0",
    transaction_id: "txn_1",
    status: "PARTIAL",
    incidents: [authorized],
    rejected_incident_ids: ["inc_rejected"],
    limitations: [],
  };

  assert.equal(selectAuthorizedIncidentLink(grounding, ["inc_rejected"]), null);
  assert.equal(isRejectedIncident(grounding, "inc_rejected"), true);
  assert.equal(selectAuthorizedIncidentLink(grounding, ["inc_rejected", incidentFixture.incident_id])?.incident.incident_id, incidentFixture.incident_id);
});

test("NO_INCIDENT cannot produce an authorized link", () => {
  const grounding: TransactionIncidentDetail = { schema_version: "1.0", transaction_id: "txn_2", status: "NO_INCIDENT", incidents: [], rejected_incident_ids: [], limitations: [] };
  assert.equal(selectAuthorizedIncidentLink(grounding, ["inc_unknown"]), null);
});
