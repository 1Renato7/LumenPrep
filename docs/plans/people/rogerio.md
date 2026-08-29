# Plano individual — Rogério

## Missão

- **Plano geral:** 1.0.0
- **Objetivo:** `OBJ-ROGERIO-001`
- **Papel:** contratos, ingestão, normalização, DuckDB, agregação, incident correlation/impact, API e coordenação de integração.
- **Orçamento:** 13–14h de implementação; H15–H19 integração e suporte à demo.
- **Resultado:** todos os componentes interpretam o mesmo evento/incidente, podem começar por fixtures e integram por uma API read-only estável.

## Context pack

Payment, Attempt e Event são identidades distintas. Approval por attempt é a métrica primária do detector; payment conversion é secundária. Raw é imutável e canonical é versionado. Rogério não escolhe causa raiz; ele transforma candidatos em incidentes separados, calcula impacto e expõe o resultado.

## Ownership e limites

- **Own:** `CMP-ING-001`, `CMP-AGG-001`, `CMP-INC-001`, `CMP-API-001`, `contracts/v1/`, DuckDB schema, `.env.example`, lockfile e integration checkpoints.
- **Produz:** `CTR-EVT-001`, `CTR-AGG-001`, `CTR-INC-001`, `CTR-API-001`.
- **Consome:** `CTR-SCN-001`, `CTR-DET-001`, `CTR-MEM-001`, `CTR-LLM-001`.
- **Fora de escopo:** detector thresholds, Cypher internals, UI layout, execução financeira.

## Interfaces

### CTR-EVT-001 v1

Schema executável: `contracts/v1/canonical-attempt.schema.json`. Obrigatórios: IDs de event/payment/attempt, event/received time, merchant/provider/country/currency/amount, method category, status, timing, correlation e `is_test`. Deduplica `event_id`; invalid vai para quarantine; late dentro de 2m revisa janela.

### CTR-AGG-001 v1

```text
WindowMetrics {
  schema_version, window_start, window_end, dimensions: map<string,string>,
  eligible_attempts:int, approved_attempts:int,
  unique_payments:int, approved_payments:int,
  amount_minor:int, currency:string,
  approval_rate:float, payment_conversion:float,
  latency_p50_ms:float, latency_p95_ms:float, timeout_rate:float,
  decline_counts:map<string,int>, data_quality:float,
  window_revision:int, correlation_id:string
}
```

### CTR-DET-001 v1 — consumido

```text
AnomalyCandidate {
  candidate_id, window, slice, metric, observed, expected,
  sample_size, effect_absolute, effect_relative,
  statistical_strength, lost_approvals, loss_coverage,
  temporal_consistency, data_quality, evidence_refs[], detector_version
}
```

### CTR-INC-001 v1

Schema executável: `contracts/v1/incident.schema.json`. `INCONCLUSIVE` é válido. Impacto sempre local e `GMV_AT_RISK`. Memória/explicação são anexadas sem alterar fatos originais.

### CTR-API-001 v1

Endpoints conforme plano geral; localhost; scenario injection somente em demo; responses incluem `correlation_id`; OpenAPI é mock para André.

## Plano de execução

### TASK-ROGERIO-001 — Congelar contratos, package e health

- **Tempo:** H0–H1.
- **Aceite:** JSON Schemas/fixtures validam; env names documentados; todos conseguem iniciar.
- **Handoff:** contratos enviados aos três consumidores.

### TASK-ROGERIO-002 — Implementar ingestion/normalization

- **Tempo:** H1–H3.
- **Inclui:** canonical validation, status/decline mapping, raw ref, dedupe, quarantine, terminal-state guard.
- **Teste:** válido, duplicado, unknown enum, invalid money, late e out-of-order.

### TASK-ROGERIO-003 — Implementar DuckDB e agregação

- **Tempo:** H3–H5.
- **Aceite:** 5m event-time windows, revision, payment/attempt denominators e dimension rollups.
- **Teste:** fixture manual com denominadores conhecidos.

### TASK-ROGERIO-004 — Correlacionar candidatos e calcular impacto

- **Tempo:** H5–H8.
- **Inclui:** overlap de attempts/tempo/signature, incident separation, ranking e GMV local.
- **Aceite:** provider BR e issuer MX viram dois incidentes; currency não é somada entre países.

### TASK-ROGERIO-005 — Implementar API e adapters

- **Tempo:** H3–H9 em incrementos.
- **Aceite:** UI funciona primeiro por fixtures e depois por serviços reais; health mostra fallback.
- **Teste:** OpenAPI/contract tests e timeout states.

### TASK-ROGERIO-006 — Coordenar checkpoints e integração

- **Tempo:** H4, H8, H13–H17.
- **Aceite:** merges na ordem do plano, build/test/smoke por checkpoint, nenhuma divergência de schema.
- **Evidência:** comandos/resultados reais, nunca marcação presumida.

## Git e handoffs

- Branch sugerida: `feat/OBJ-ROGERIO-001-platform-core`.
- Commits: contracts; ingestion; aggregation; incident; API; integration fixes.
- É o único coordenador de `pyproject.toml`, DuckDB schema e `.env.example`.
- `READY TO MERGE`: canonical fixtures, detector fixture e memory fixture percorrem API.

## Riscos e autonomia

- Pode escolher detalhes internos do FastAPI/DuckDB sem alterar contratos.
- Deve iniciar change control antes de renomear campo, unidade, enum ou estado.
- Fallback: baseline pré-agregado e adapters in-memory; contratos permanecem.

## Sincronização Linear

- Parent: [LUM2-6](https://linear.app/lumenhack/issue/LUM2-6/entregar-ingestao-contratos-e-api-integradora).
- Microtarefas: `TASK-CORE-001`→`LUM2-27`, `TASK-CON-001`→`LUM2-28`, `TASK-ING-001`→`LUM2-29`, `TASK-ING-002`→`LUM2-30`, `TASK-ING-003`→`LUM2-31`, `TASK-ING-004`→`LUM2-32`, `TASK-AGG-001`→`LUM2-33`, `TASK-AGG-002`→`LUM2-34`, `TASK-INC-001`→`LUM2-35`, `TASK-INC-002`→`LUM2-36`, `TASK-INC-003`→`LUM2-37`, `TASK-API-001`→`LUM2-38`, `TASK-API-002`→`LUM2-39`, `TASK-API-003`→`LUM2-40`, `TASK-INT-001`→`LUM2-41`, `TASK-INT-002`→`LUM2-42`.
- Fonte completa de dependências: `docs/plans/linear-preview.md`.
