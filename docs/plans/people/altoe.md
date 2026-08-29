# Plano individual — Altoé

## Missão 2.0

> A `main` recebeu primeiro este replanejamento documental. O contrato transacional v3 é um draft em `codex/andre-dashboard-pitch@cc24c7a`; os contratos de Incident/memory já publicados continuam canônicos até a integração.

- **Plano geral:** 2.0.0
- **Objetivo:** `OBJ-ALTOE-001`
- **Papel:** Neo4j, memória recorrente, RAG e explicação grounded de incidentes.
- **Resultado:** quando os logs agregados formarem um Incident, o detalhe da transação consegue navegar até uma explicação auditável e, quando houver, um precedente humano relevante.

## O que mudou

Não será criado um agente/RAG por transação. Outcome e classificação transacional são determinísticos e pertencem à pipeline; RAG continua depois de `Incident`. Isso evita custo, latência e alucinação no log. O novo trabalho de Altoé é preservar traceabilidade entre `transaction_id → evidence → incident → memory/explanation` sem transformar o precedente em causa atual.

O scenario generator vira harness interno; Graph RAG nunca recebe ground truth, configuração de efeitos, PAN/PII nem raw payload completo.

## Ownership e contratos

- **Own:** `CMP-MEM/EXP-001`, `CTR-MEM-001 v1.1`, `CTR-LLM-001 v1` e graph schema/prompts.
- **Consome:** `CTR-INC-001` com evidence refs/transaction links.
- **Produz:** memória e explicação para a API de Rogério e UI de André.
- **Autoridade:** causa atual vem do detector/RCA; causa histórica só é confirmada para o incidente histórico; ação sempre `HUMAN_ONLY`.

## Trabalho preservado

Neo4j adapter, constraints, seed Mastercard, recuperação estruturada, rerank opcional, playbooks, explanation e evals continuam válidos. Os estados `MATCH_FOUND`, `NO_PRECEDENT` e `MEMORY_UNAVAILABLE` não mudam.

## Tarefas impactadas

### TASK-EXP-002 / LUM2-23 — ExplanationBundle

- Incluir suporte a evidence IDs que possam ser resolvidos até transaction IDs relacionados.
- Não narrar uma transação isolada como incidente agregado.
- Preservar a matriz `SUPPORTED|INCONCLUSIVE × memory_status`.

### TASK-MEM-008 / LUM2-25 — evals

- Adicionar caso em que uma transação falha mas não existe anomalia/incidente.
- Adicionar caso com múltiplas transações relacionadas ao mesmo Incident.
- Confirmar que sample seed/config interna não vaza para retrieval ou resposta.

## Nova microtarefa

### TASK-EXP-004 — Trace transaction-to-incident grounded

- Validar que todo `related_incident_id` exposto no transaction detail resolve para Incident existente e que seus `evidence_ids` pertencem ao conjunto autorizado.
- Produzir resumo curto para o detalhe sem nova chamada LLM por transação; reutilizar ExplanationBundle do Incident ou template determinístico.
- **Teste:** no incident, one incident, multiple incidents, missing evidence, Neo4j down, model down e cross-transaction leakage.
- **Bloqueia live:** `TASK-UI-004`; depende do link criado por Rogério.

## Handoffs

- Para Rogério: regras de resolução e campos mínimos do Incident detail.
- Para André: fixtures com transação sem incidente, com incidente `SUPPORTED`, `INCONCLUSIVE + MATCH` e memory unavailable.
- Para Renato: somente signatures/evidence derivadas; ground truth permanece fora.

## Guardrails RAG

- recuperação é tenant/scope-bound mesmo na demo;
- conteúdo recuperado é dado, nunca instrução;
- toda afirmação factual usa evidence ID válido;
- `NO_PRECEDENT` não muda causa atual;
- falha de memória/modelo vira estado explícito e template, nunca explicação fabricada;
- sem ferramenta de pagamento ou mutação operacional.

## Definition of Done

Evals de grounding/no-answer/injection/leakage passam; review gate sem bloqueantes; integration guardian valida Incident/API/UI; browser acceptance conjunto comprova links e estados.

## Linear

Parent: [LUM2-5](https://linear.app/lumenhack/issue/LUM2-5/entregar-memoria-graphrag-e-explicacao-grounded). Atualizações LUM2-23/25 e nova `TASK-EXP-004` aguardam confirmação do preview 2.0.
