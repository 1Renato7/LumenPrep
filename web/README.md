# Lumen web scaffold

This directory is the Next.js consumer of `CTR-API-001 v3`. Browser code reads only
`NEXT_PUBLIC_API_BASE_URL`; it must never contain backend credentials, DuckDB/Neo4j
access, payment execution, or locally computed transaction progress.

## Frozen integration surface

- `web/lib/api/types.ts` mirrors the frozen JSON schemas under `contracts/v1/`.
- `web/lib/api/client-interface.ts` owns all API operation IDs, typed errors,
  timeout behavior, and polling cancellation. Routes must depend on `LumenApiClient`.
- Backend-authored record responses can contain outcomes and diagnoses. They are not
  accepted in `TransactionInput`, generated on the client, or inferred by the UI.
- `FAILED` is a transaction outcome; `PIPELINE_FAILED` is a processing stage under
  `UNKNOWN`, never a decline label.

## Exact three-lane ownership map

| Lane | May edit | Must not edit | Contract handoff |
| --- | --- | --- | --- |
| A — transaction input | `web/app/transactions/new/**`, `web/components/transaction-form/**` | root config, `web/lib/api/**`, log/detail/incidents paths | `LumenApiClient.getTransactionCatalog`, `generateTransactionSamples`, `createTransactionBatch` |
| B — transaction log/detail | `web/app/transactions/**` excluding `new/**`, `web/components/transaction-log/**` | root config, `web/lib/api/**`, form/incidents paths | `getTransactionBatch`, `listTransactions`, `getTransaction`, `createPollingController` |
| C — incidents | `web/app/incidents/**`, `web/components/incidents/**` | root config, `web/lib/api/**`, transaction paths | `listIncidents`, `getIncident` |

The integrator alone owns `package.json`, `package-lock.json`, TypeScript/build/test
config, `app/layout.tsx`, `app/globals.css`, `.env.example`, and the two frozen API
surface files. Lanes consume these files without editing them; additions need an
explicit integration handoff.

## Commands

```bash
npm run lint
npm test
npm run build
```
