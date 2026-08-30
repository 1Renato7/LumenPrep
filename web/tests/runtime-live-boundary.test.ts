import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const runtimeFiles = [
  "app/incidents/[id]/page.tsx",
  "app/incidents/page.tsx",
  "app/transactions/[id]/page.tsx",
  "app/transactions/page.tsx",
  "components/incidents/incident-detail.tsx",
  "components/incidents/incidents.tsx",
  "components/transaction-detail/transaction-detail.tsx",
  "components/transaction-form/transaction-form.tsx",
  "components/transaction-log/transaction-log.tsx",
];

test("production transaction and incident surfaces do not import offline fixtures or mocks", async () => {
  const forbidden = ["fixture-source", "lib/mocks", "getOffline", "listOffline", "buildFixture"];
  for (const relativePath of runtimeFiles) {
    const source = await readFile(new URL(`../${relativePath}`, import.meta.url), "utf8");
    for (const marker of forbidden) {
      assert.equal(source.includes(marker), false, `${relativePath} contains forbidden runtime dependency ${marker}`);
    }
  }
});
