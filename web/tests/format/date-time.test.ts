import assert from "node:assert/strict";
import test from "node:test";

import { BRASILIA_TIME_ZONE, formatBrasiliaDateTime } from "../../lib/format/date-time";

test("formats transaction timestamps in the Brasília time zone", () => {
  assert.equal(BRASILIA_TIME_ZONE, "America/Sao_Paulo");
  assert.match(formatBrasiliaDateTime("2026-08-29T18:00:10Z"), /15:00:10/);
});

test("uses IANA historical daylight-saving rules instead of a fixed UTC offset", () => {
  assert.match(formatBrasiliaDateTime("2018-01-15T10:00:00Z"), /08:00:00/);
});
