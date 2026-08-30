import assert from "node:assert/strict";
import test from "node:test";

import { sortByMostRecent } from "../../lib/format/sort-by-date";

test("sortByMostRecent orders valid timestamps descending and leaves invalid ones last", () => {
  const entries = [
    { id: "old", timestamp: "2026-08-29T18:00:00Z" },
    { id: "invalid", timestamp: "not-a-date" },
    { id: "new", timestamp: "2026-08-30T18:00:00Z" },
  ];

  assert.deepEqual(sortByMostRecent(entries, (entry) => entry.timestamp).map((entry) => entry.id), ["new", "old", "invalid"]);
  assert.deepEqual(entries.map((entry) => entry.id), ["old", "invalid", "new"]);
});
