# Plano individual — André

## Missão

- **Plano geral:** 1.3.1
- **Objetivo:** `OBJ-ANDRE-001`
- **Papel:** frontend, experiência da demo, recorder transversal e pitch.
- **Orçamento:** 6–7h de implementação; H15–H19 prioritariamente integração visual, acceptance, ensaio e pitch.
- **Resultado:** um estranho entende o incidente em uma linha executiva e consegue auditar causa, evidência, memória e playbook no drill-down.

## Context pack

O Lumen observa attempts de pagamentos, detecta quedas de approval/latência, localiza o slice causal, separa incidentes, recupera precedentes confirmados no Neo4j e recomenda ação humana. A UI não recalcula fatos nem consulta DuckDB/Neo4j diretamente; ela renderiza contratos do backend.

A memória nunca decide o estado causal. André renderiza dois sinais independentes: `root_cause.status` (`SUPPORTED` ou `INCONCLUSIVE`) e memória (`MATCH`, `NO_PRECEDENT` ou `UNAVAILABLE`). Mesmo `INCONCLUSIVE` consulta memória. Com match, a UI mostra o precedente e a solução anterior como orientação; sem match, declara que não há causa atual sustentada nem precedente.

Quando houver precedente, a UI mostra separadamente o playbook usado antes, por que ele parece aplicável agora e quais diferenças exigem validação humana. O botão/controle nunca executa a solução.

No roteiro, André demonstra: silêncio no normal, provider degradado no Brasil, emissor mexicano simultâneo, repetição Mastercard de dois dias antes, `INCONCLUSIVE` e trial by fire.

## Ownership e limites

- **Own:** `CMP-UI-001`, diretório proposto `app/ui/`, roteiro da demo e materiais de pitch.
- **Consome:** `CTR-API-001` e fixtures `CTR-INC-001`/`CTR-LLM-001`.
- **Somente leitura:** contratos, detector, DuckDB e Neo4j.
- **Hotspot compartilhado:** alterações no endpoint passam por Rogério; decisões transversais são registradas na lane Team do Flight Log.
- **Fora de escopo:** estatística, ingestão, query Cypher, prompts de produção e mudança de schema.

## Interfaces

### CTR-API-001 v1 — consumido

- `GET /health` → estados `api`, `duckdb`, `neo4j`, `openai`, `demo_mode`.
- `GET /metrics/current` → janelas com current/baseline.
- `GET /incidents` → lista `CTR-INC-001`.
- `GET /incidents/{id}` → Incident completo + `memory` (`CTR-MEM-001 v1.1`) + `explanation`; a UI lê `memory_status` e nunca infere indisponibilidade por lista vazia.
- `POST /demo/scenarios/{scenario_id}/inject` → `202` com `correlation_id`; somente ambiente demo.
- UI timeout: 2s; fallback: renderizar fixtures marcadas `DEMO FALLBACK`.

### CTR-INC-001 v1 — campos necessários

`incident_id`, `state`, `detected_at`, `estimated_started_at`, `title`, `scope`, `metrics`, `root_cause.{status,category,confidence,confidence_factors}`, `impact.{metric,amount_minor,currency,method,bounds}`, `evidence[]`, `memory_matches[]`, `recommendations[]`, `limitations[]`, `correlation_id`.

## Plano de execução

### TASK-ANDRE-001 — Montar dashboard a partir de fixture

- **Tempo:** H1–H3.
- **Input:** `contracts/fixtures/incident-mastercard-recurrence.json`.
- **Output:** cards de incidentes, gráfico current/baseline, impacto local e drill-down de evidência.
- **Aceite:** funciona sem backend; nenhuma evidência é inventada; `INCONCLUSIVE` tem visual próprio.
- **Teste:** render desktop e resolução de apresentação; smoke sem API.
- **Handoff:** URL/comando local para Rogério integrar em H3.

### TASK-ANDRE-002 — Implementar controles e estados da demo

- **Tempo:** H3–H5.
- **Inclui:** normal, injecting, detected, recovered, backend unavailable, memory unavailable e LLM fallback.
- **Aceite:** botões chamam apenas scenario IDs existentes; estado de fallback é explícito.
- **Teste:** mock de 202/4xx/timeout.

### TASK-ANDRE-003 — Criar visual de recorrência explicável

- **Tempo:** H5–H6:30.
- **Inclui:** “aconteceu há 2 dias”, confirmação humana anterior, fatores iguais/diferentes e scores separados.
- **Aceite:** não usa “mesma causa” quando status corrente não sustenta; linka evidence IDs; cobre visualmente `SUPPORTED + MATCH`, `SUPPORTED + NO_PRECEDENT`, `INCONCLUSIVE + MATCH` e `INCONCLUSIVE + NO_PRECEDENT`; no terceiro caso mostra precedente sem afirmar a causa atual.
- **Handoff:** Altoé revisa semântica e groundedness.

### TASK-ANDRE-004 — Preparar pitch e roteiro resiliente

- **Tempo:** H11–H15 e H17–H19, intercalado sem bloquear código.
- **Inclui:** problema, insight, arquitetura, demo, trade-offs, limites e Q&A.
- **Aceite:** demo de 5–7 minutos com caminho normal e fallback; uma linha executiva e detalhe ops.
- **Evidência:** roteiro cronometrado e ao menos dois ensaios completos.

### TASK-ANDRE-005 — Acceptance visual

- **Tempo:** H15–H17.
- **Aceite:** browser gate cobre normal, dois incidentes, recurrence, no-answer, console e rede.
- **Stop condition:** somente bug bloqueante após H17.

## Git e handoffs

- Branch sugerida: `feat/OBJ-ANDRE-001-dashboard-pitch`.
- Commits separados: shell/fixture; incident cards; recurrence; demo states; pitch assets.
- Não editar schemas/lockfile sem Rogério.
- `READY TO HAND OFF`: fixture e API produzem a mesma UI; screenshots/fluxo documentados.
- `READY TO MERGE`: review gate, browser gate e CTR-API compatível.

## Riscos e autonomia

- Pode decidir layout, hierarquia visual e copy sem mudar significado técnico.
- Deve parar se UI precisar derivar confiança, causa ou impacto.
- Fallback: fixtures locais rotuladas, nunca fingir conexão live.

## Sincronização Linear

- Parent: [LUM2-4](https://linear.app/lumenhack/issue/LUM2-4/entregar-narrativa-dashboard-e-demo-executiva).
- Microtarefas: `TASK-UI-001`→`LUM2-8`, `TASK-UI-002`→`LUM2-9`, `TASK-UI-003`→`LUM2-10`, `TASK-UI-004`→`LUM2-11`, `TASK-UI-005`→`LUM2-12`, `TASK-UI-006`→`LUM2-13`, `TASK-DEMO-001`→`LUM2-14`.
- Fonte completa de dependências: `docs/plans/linear-preview.md`.
