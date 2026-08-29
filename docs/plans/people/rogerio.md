# Plano individual — Rogério

## Missão

- **Plano geral:** 1.3.1
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

Schema executável: `contracts/v1/incident.schema.json`. `INCONCLUSIVE` é válido e depende apenas de evidência atual. Impacto sempre local e `GMV_AT_RISK`. Todo Incident segue para memória; causa atual e estado da memória são eixos separados. Memória/explicação são anexadas sem alterar fatos originais; `matches=[]` significa ausência de precedente.

### CTR-API-001 v1

Endpoints conforme plano geral; localhost; scenario injection somente em demo; responses incluem `correlation_id`; detalhe do incidente retorna separadamente `incident`, `memory` (`CTR-MEM-001 v1.1`) e `explanation`; OpenAPI é mock para André.

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
- **Teste:** OpenAPI/contract tests, timeout states e matriz `SUPPORTED|INCONCLUSIVE × MATCH|NO_PRECEDENT`, confirmando que memória nunca altera `root_cause.status`.

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

## Mapa de módulos internos

Detalhe interno de implementação (autônomo, não altera contratos — ver §Riscos e autonomia). Define fronteiras de arquivo entre os dois blocos de tarefas deste componente (Bloco 1: `TASK-ING-*`+`TASK-AGG-*`; Bloco 2: `TASK-INC-*`+`TASK-API-*`+`TASK-INT-*`), para que possam avançar sem escrever nos mesmos arquivos e sem divergir na fronteira entre eles — útil independente de quem/o que implementa cada bloco.

### Estrutura de pacotes

```text
app/
├── main.py              # FastAPI app + registro de routers — dono único, escrito 1x no TASK-CORE-001
├── config.py             # settings tipadas — TASK-CORE-001
├── ingestion/              # Bloco 1 — TASK-ING-001..004
│   ├── __init__.py          # expõe: ingest_event, IngestResult
│   ├── validate.py            # valida contra contracts/v1/canonical-attempt.schema.json
│   ├── normalize.py             # status/method/decline mapping
│   ├── dedupe.py                  # idempotency key + quarantine
│   ├── ordering.py                  # watermark + terminal-state guard
│   └── storage.py                     # único módulo que fala DuckDB para raw/canonical
├── aggregation/             # Bloco 1 — TASK-AGG-001..002
│   ├── __init__.py           # expõe: compute_windows, get_current_metrics, WindowMetrics
│   └── windows.py              # SQL DuckDB, janelas de 5min, dois denominadores
├── incidents/                # Bloco 2 — TASK-INC-001..003
│   └── __init__.py             # expõe: correlate_candidates, compute_impact, to_incident
├── api/                       # Bloco 2 — TASK-API-001..003
│   ├── __init__.py              # expõe: router (um único APIRouter)
│   ├── health.py
│   ├── metrics.py                 # chama aggregation.get_current_metrics — nunca acessa DuckDB direto
│   ├── incidents.py                 # chama incidents.*, memory.* e explanation.* — monta {incident, memory, explanation}
│   └── demo.py                        # DEMO_MODE injection
└── integration/                       # Bloco 2 — TASK-INT-001..002
    └── smoke.py                         # chama ingestion + aggregation + incidents + api em sequência real
```

**Regra de ferro:** `incidents/` e `api/` (Bloco 2) nunca importam `duckdb` nem tocam schema diretamente — só chamam as funções públicas exportadas por `ingestion/__init__.py` e `aggregation/__init__.py`. Isso impede duplicação de lógica de storage e mantém owner único de schema (linha "pyproject.toml/lockfile" acima).

`api/incidents.py` é o único módulo que também atravessa fronteira de pessoa: além de `incidents.*` (próprio), chama `app/memory/__init__.py` e `app/explanation/__init__.py` — pacotes de Altoé (`CMP-MEM-001`/`CMP-EXP-001`), não deste plano. A chamada é só pelo tipo do contrato (`SimilarIncidentResult` via `CTR-MEM-001 v1.1`, `ExplanationBundle` via `CTR-LLM-001 v1`); layout interno desses pacotes é decisão de Altoé, não coordenada aqui.

### Assinaturas congeladas nas fronteiras

Seam 1 — `aggregation` (Bloco 1) → `api` (Bloco 2), usado por `TASK-API-001`:

```python
# app/aggregation/__init__.py
def get_current_metrics(dimensions: dict[str, str] | None = None) -> list[WindowMetrics]: ...
```

`WindowMetrics` é o modelo Pydantic gerado a partir de `contracts/v1/window-metrics.schema.json` — mesmo arquivo, sem reinterpretar campo.

Seam 2 — `ingestion` (Bloco 1) → `integration.smoke` (Bloco 2), usado por `TASK-INT-001/002`:

```python
# app/ingestion/__init__.py
def ingest_event(raw_payload: dict) -> IngestResult: ...
```

Seam 3 — `main.py` (dono único, TASK-CORE-001) → `api.router` (Bloco 2), editado uma vez só:

```python
# main.py — escrito 1x no CORE-001, nunca mais editado por quem fizer API-*
from app.api import router as api_router
app.include_router(api_router)
```

`app/api/router.py` é criado depois (Bloco 2); `main.py` nunca precisa de segunda edição.

Seam 4 — `app/memory` e `app/explanation` (Altoé) → `api/incidents.py` (Bloco 2, `TASK-API-001`), fronteira de pessoa, não de bloco:

```python
# assumido de app/memory/__init__.py e app/explanation/__init__.py (Altoé) — CTR-MEM-001 v1.1 / CTR-LLM-001 v1
def find_similar_incidents(incident: Incident) -> SimilarIncidentResult: ...
def explain_incident(incident: Incident, memory: SimilarIncidentResult) -> ExplanationBundle: ...
```

Nomes de função são placeholder de Rogério até Altoé confirmar a assinatura real; o que é congelado é só o tipo de retorno (schema). `api/incidents.py` monta a resposta como `{incident, memory, explanation}` (`CTR-API-001 v1`) sem reinterpretar nenhum dos três — `memory_status` e `root_cause.status` nunca se misturam.

### Stub no dia zero

`TASK-CORE-001` entrega, junto do esqueleto, uma implementação-stub de `get_current_metrics` e `ingest_event` com dados fake já validados contra o schema. O Bloco 2 codifica `incidents/`/`api/` contra essa stub desde a primeira hora, sem esperar a implementação real do Bloco 1 — troca a stub pela real quando `TASK-AGG-001`/`TASK-ING-001` fecharem.

Para a Seam 4, não há stub de código — Altoé entrega mock de `CTR-MEM-001` em H3 (compromisso já registrado no plano dele). Até lá, `TASK-API-001` codifica `api/incidents.py` direto contra as fixtures `contracts/fixtures/similar-incidents{,-empty,-inconclusive-current,-unavailable}.json` e `explanation-bundle{,-no-precedent,-inconclusive-with-precedent}.json`, cobrindo os três `memory_status` e os dois `root_cause.status`.

### Teste de contrato automático

`scripts/validate_contracts.py` roda `jsonschema.validate` da saída real de `get_current_metrics()` contra `window-metrics.schema.json`, e da saída de `ingest_event` (canonical) contra `canonical-attempt.schema.json`. Roda antes de qualquer handoff entre os dois blocos — falha é bloqueante, não é opinião.

Mesmo script valida a resposta de `GET /incidents/{incident_id}` nos quatro casos de fixture acima: `matches` presente só quando `memory_status=MATCH_FOUND`; `root_cause.status` do `incident` idêntico em todas as combinações com o mesmo incidente base (memória nunca altera fato). Cobre a matriz `SUPPORTED|INCONCLUSIVE × MATCH|NO_PRECEDENT` exigida pelo teste de `TASK-ROGERIO-005`.

### Ownership de arquivo compartilhado

- `main.py`, `config.py`, `pyproject.toml`, `.env.example`, schema DuckDB → Bloco 1 (TASK-CORE-001).
- `app/api/*`, `app/incidents/*` em diante → Bloco 2.
- `app/memory/*`, `app/explanation/*` → fora deste plano, owner Altoé; `api/incidents.py` só os importa pelo `__init__.py` deles, nunca edita.
- Nenhum bloco edita o pacote do outro. Mudança de contrato é change control (system-plan primeiro), nunca edição direta na fronteira.
