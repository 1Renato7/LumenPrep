# Plano individual — Rogério

## Missão 2.0

> A `main` recebeu primeiro este replanejamento documental. Os drafts executáveis v3 estão em `codex/andre-dashboard-pitch@cc24c7a`; Rogério deve integrá-los por microtarefa, não copiar cegamente sobre a API atual.

- **Plano geral:** 2.0.5
- **Objetivo:** `OBJ-ROGERIO-001`
- **Papel:** contratos, batch ingestion, lifecycle durável, API FastAPI, DuckDB/Parquet e deploy Railway.
- **Resultado:** toda transação da Vercel entra por uma única API, é persistida antes do `202`, processada de modo idempotente e consultável por log/detalhe.

## O que mudou

Os endpoints públicos de criação de cenários deixam de ser a entrada do produto. O código concluído em `TASK-API-003` é preservado como ferramenta interna do harness, mas novos consumidores usam `CTR-API-001 v3`. Rogério passa a expor catálogo, geração de inputs sintéticos, batch, status/list/detail e filtro de incidentes por transaction ID.

O MVP adapta o Dockerfile e o runbook Railway já publicados para FastAPI + worker e DuckDB/Parquet em Railway Volume. Isso preserva o trabalho existente, com a limitação consciente de uma réplica. Banco/volume não são públicos. A API pública aplica CORS allowlist para Vercel e localhost.

## Ownership e contratos

- **Own:** `CMP-API-001`, `CMP-TXN-001`, `CMP-ING-001`, `CMP-AGG-001`, `CMP-INC-001`, `CMP-DEPLOY-001`.
- **Coordena:** `contracts/v1/`, OpenAPI, migrations, dependency lock e `.env.example`.
- **Produz:** `CTR-TXL-001`, `CTR-API-001 v3`, `CTR-DEP-001`; integra `CTR-TXN-001`.
- **Consome:** outcome/events de Renato, candidates do detector e memória/explicação de Altoé.

## Regras obrigatórias

- Batch 1..100 é validado e inicialmente persistido de forma atômica.
- Mesma idempotency key + mesmo payload retorna os mesmos IDs; payload diferente retorna `409`.
- `PROCESSING` tem stage/progress gravados pelo worker; não existe progresso só em memória.
- Outcome `FAILED` não é pipeline failure; falha técnica usa `PIPELINE_FAILED` + `failure_code`.
- Reentrega/restart não duplica event, metric ou transaction.
- `POST /transaction-samples` retorna somente inputs, seed e correlation; não persiste, processa ou antecipa outcomes.
- Em `CTR-INC-001 v1`, serializar `root_cause.alternatives` em ordem decrescente de confiança e `recommendation_class`, sem alterar a causa atual ou permitir execução automática.
- Priorizar `Impact.amount_minor` somente em buckets da mesma moeda; sem fonte FX versionada, não comparar BRL com MXN.
- Correlacionar candidates somente por fingerprint exato de `correlation_id + slice`; país em comum não agrega provider e issuer em uma narrativa.

## Trabalho preservado

Tarefas concluídas de contracts, ingestion, normalization, aggregation e API não são reabertas. `TASK-API-003 / LUM2-40` permanece evidência do harness de cenários interno. As tarefas de integração em andamento recebem o novo caminho público sem apagar o que já passou.

Módulos já integrados na `main` — `app/ingestion`, `app/aggregation`, `app/incidents`, `app/api`, `app/integration`, `main.py`, `Dockerfile` e `scripts/validate_contracts.py` — são a base da mudança. As novas rotas entram em `app/api` e o lifecycle em um módulo transacional próprio; nenhuma delas deve duplicar SQL fora do adapter de storage.

## Novas microtarefas

### TASK-TXN-API-001 — API transaction-first

- Implementar catalog, samples, create batch, get batch, list e detail conforme OpenAPI 3.0.0.
- `samples` usa catálogo/seed de Renato; `batch` cria IDs server-side.
- **Teste:** 1/100/101, field allowlist, sample seed, idempotência, cursor, status filter, 404/409/422/503.
- **Desbloqueia:** `TASK-UI-005`, `TASK-TXN-WORKER-001`.

### TASK-TXN-WORKER-001 — lifecycle durável e retomável

- Persistir stages, leases/retry, timestamps, outcome/classification e related incident IDs.
- Reconciliar job preso após restart sem duplicação.
- **Teste:** crash entre stages, duplicate delivery, progress monotônico, transaction failure e pipeline failure.
- **Bloqueada por:** `TASK-TXN-API-001`, outcome adapter de Renato.

### TASK-DEPLOY-API-001 — Railway, volume, CORS e smoke

- Adaptar o start command, health e runbook existentes; adicionar volume path, env e domínio público da API v3.
- CORS somente Vercel production/preview autorizados e localhost; sem wildcard com credentials.
- **Teste:** health, persistência após redeploy/restart, origem permitida/negada e Vercel live.
- **Bloqueada por:** primeira fatia do worker.

## Tarefas existentes impactadas

- `TASK-API-002 / LUM2-39`: adicionar filtro `transaction_id` e resposta que preserve Incident/memory/explanation separados.
- `TASK-INT-001 / LUM2-41`: nova fatia é Vercel → Railway → persist → worker → log/detail; cenário interno pode alimentar tráfego de fundo.
- `TASK-INT-002 / LUM2-42`: preflight inclui schemas novos, CORS, volume, restart e browser deployed.

## Handoffs

- Para André: OpenAPI, base URL por ambiente, error map e fixtures antes da implementação live.
- Para Renato: adapter que recebe `TransactionInput`, devolve outcome/event e não escolhe métricas.
- Para Altoé: `transaction_id` e evidence refs em Incident/detail, nunca raw PII.

## Definition of Done

Contract tests, worker restart/idempotency, review gate, integration guardian e deploy smoke reais. Browser gate é conjunto com André. Se Railway Volume bloquear o MVP, registrar change control antes de migrar para Postgres.

## Linear

Parent: [LUM2-6](https://linear.app/lumenhack/issue/LUM2-6/entregar-ingestao-contratos-e-api-integradora). Novas issues: `TASK-TXN-API-001`→`LUM2-58`, `TASK-TXN-WORKER-001`→`LUM2-59`, `TASK-DEPLOY-API-001`→`LUM2-60`. `LUM2-39/41/42` foram atualizadas sem mudar seus estados.

## Recuperação 2.2 — Pessoa A confirmada

- **Plano geral:** 2.2.0; **objetivo:** `OBJ-ROGERIO-002`; **base:** `main@613df52`.
- **Missão:** integrar o que já está na `main` em uma cadeia persistida `batch → worker → detector/RCA → Incident → grounding`, sem mudar contratos públicos e sem editar `web/`.
- **Autonomia:** pode alterar somente `app/`, `contracts/v1/`, migrations DuckDB, runtime/configuração/deploy e os hotspots documentais. Uma mudança de endpoint/schema/estado exige change control antes do código.

### Primeiro bloco verificável

1. Executar `TASK-REC-001/002`: fixar Python 3.14.4 também no Docker, confirmar paths DuckDB/Volume, CORS opt-in, worker de uma réplica e `CTR-SCN-001 v1` interno.
2. Rodar `python scripts/validate_contracts.py` e a suite Python no ambiente equivalente ao container. Não afirmar a conclusão se essa equivalência não for executada.
3. Implementar `TASK-PIPE-001` com migration idempotente e rollback/estratégia segura antes de tocar em `app/api/incidents.py`.

### Handoffs e condições de parada

- **Para André:** após `TASK-PIPE-003/004`, entregar comando para API local, OpenAPI validado, URL/base `/v1`, mapa `404/409/422/503`, exemplos reais de `NO_INCIDENT`, `PARTIAL` e `RESOLVED` e indicação explícita de `BACKEND_UNAVAILABLE`.

## Missão 2.3 — cube, contratos e Incident causal

- **Plano geral:** 2.3.0; **objetivo:** `OBJ-RCA6-ROGERIO-001`.
- **Own:** `TASK-RCA6-002`, `005` e `009`; coordena `CTR-EVT/AGG/DET/INC` v2, migrations, API e adaptador v1 temporário.
- **Primeiro bloco:** congelar schemas/mocks v2 e conservation tests com Renato; cube é esparso por rollups observados, nunca produto cartesiano materializado.
- **Handoff:** publicar Incident v2 e exemplos para Altoé/André após E2E de stream até API. Mudança de endpoint/schema exige change control.
- **Limite:** somente o RCA decide `SUPPORTED`; persistência, memória e UI preservam, mas nunca promovem a conclusão.
- **Parar e sincronizar:** se `CTR-*`, estado, erro, timeout, CORS público ou modelo de persistência precisar mudar; atualizar primeiro o plano geral e `FL-20260830-ROGERIO-010`/adendo.
- **Pronto para handoff:** E2E cria Incident sem inserir Incident/link diretamente; duplicado/restart/simultâneos/memory down/leakage passam; fixtures não são fonte live.
- **Pronto para integração futura:** testes afetados, `code-review-gate`, guardian `INTEGRATION`, e browser gate conjunto com André para qualquer fluxo observável.
