# Plano individual — Renato

## Missão 2.0

> A `main` recebeu primeiro este replanejamento documental. Os drafts de sample/batch/scenario v2 estão em `codex/andre-dashboard-pitch@cc24c7a` e exigem revisão do owner antes da integração.

- **Plano geral:** 2.0.0
- **Objetivo:** `OBJ-RENATO-001`
- **Papel:** geração sintética, outcome adapter, tráfego de fundo, baseline, detector, RCA e avaliação.
- **Resultado:** inputs sintéticos viram outcomes/events reprodutíveis; o conjunto de logs gera métricas/anomalias sem o usuário informar efeitos.

## O que mudou

`TASK-DATA-006 / LUM2-48` concluída não é descartada: o scenario generator passa a `CMP-HARNESS-001`, interno. O formulário público não recebe mais `approval_rate_multiplier`, latency, timeout ou causa esperada. Renato deve adaptar o motor para duas entradas:

1. um `TransactionInput` individual, que produz outcome/evento determinístico;
2. uma configuração interna de cenário/tráfego, usada para volume de fundo e evals, enviada pela mesma batch API do produto.

Também fornece geração rápida de `TransactionInput` a partir de quantidade + seed. Essa geração apenas escolhe fatos válidos do catálogo; outcome e anomalia continuam posteriores.

## Ownership e limites

- **Own:** `CMP-DATA-001`, `CMP-HARNESS-001`, `CMP-DET/RCA-001`.
- **Produz:** domínio do `CTR-TXN-001`, outcomes/events `CTR-EVT-001` e `CTR-DET-001`.
- **Consome:** `TransactionInput` e `CTR-AGG-001`.
- **Fora de escopo:** API/persistência, UI, Neo4j, narrativa LLM, cálculo no browser e dados reais.
- **Ground truth:** separado do runtime, API pública, log e RAG.

## Trabalho preservado

Histórico de 90 dias, distributions, stream, scenarios, baseline, detector e RCA continuam válidos. Scenario schemas/fixtures v2 permanecem para teste interno e nunca reaparecem como formulário público.

## Novas microtarefas

### TASK-DATA-008 — Transaction outcome adapter

- Receber os fatos allowlisted de `TransactionInput`.
- Gerar IDs/timestamps de evento, status/outcome, provider response, decline normalizado e latência com PRNG seedado e regras condicionais existentes.
- Não receber nem emitir approval rate, effect multiplier, expected cause ou ground truth na interface pública.
- **Teste:** mesma seed/contexto produz mesmo outcome; invariantes por método; nenhum PAN/PII; success/failure/unknown; retry não duplica.
- **Desbloqueia:** worker Rogério e primeira fatia live.

### TASK-DATA-009 — Samples e background traffic pela API comum

- Gerar 1..100 inputs válidos por quantidade/seed para `POST /transaction-samples`.
- Fazer o harness de tráfego de fundo submeter `CTR-TXN-001` pela mesma batch API, em vez de escrever direto no banco.
- Permitir defaults opcionais de merchant/country/currency sem hardcode no frontend.
- **Teste:** seed reproduzível, todos os valores pertencem ao catálogo, sample não contém outcome; cenário interno altera distribuição só depois do processamento.
- **Desbloqueia:** demo rápida e volume suficiente para analytics.

## Tarefas existentes impactadas

- `TASK-DATA-007 / LUM2-49`: reforçar que ground truth e config de efeitos ficam apenas no harness/eval.
- `TASK-DET-001..004 / LUM2-50..53`: métricas derivadas exclusivamente dos eventos persistidos.
- `TASK-EVAL-001/002 / LUM2-56/57`: adicionar batches mistos, low volume honesto e equivalência entre tráfego manual e interno.

## Handoffs

- Para Rogério: interface pura `TransactionInput + seed/context → outcome/events` e catálogo/sample generator.
- Para André: somente catálogo e sample API via Rogério; nenhum import direto do generator.
- Para Altoé: Incident/signature derivado; nunca ground truth ou config interna.

## Definition of Done

Reprodutibilidade, contract tests, evals, review gate e integração ponta a ponta. A demo deve funcionar com lote aleatório e com seed fixa de ensaio; nenhum threshold é ajustado usando o holdout final.

## Linear

Parent: [LUM2-7](https://linear.app/lumenhack/issue/LUM2-7/entregar-dados-sinteticos-deteccao-e-rca). `TASK-DATA-008/009` são novas issues propostas no preview 2.0; atualizações das tarefas existentes aguardam sincronização confirmada.

Mapeamento corrigido já publicado: `LUM2-44` = Gerar 90 dias com sazonalidade (`TASK-DATA-004` no texto legado), `LUM2-45` = outcomes condicionais/retries (`TASK-DATA-002`) e `LUM2-46` = latências/declines (`TASK-DATA-003`). Não reescrever esses IDs concluídos; o preview 2.0 só adiciona tarefas novas e atualiza descrições ainda abertas.
