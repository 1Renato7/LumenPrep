# Plano individual — Altoé

## Missão 2.0

> A `main` recebeu primeiro este replanejamento documental. O contrato transacional v3 é um draft em `codex/andre-dashboard-pitch@cc24c7a`; os contratos de Incident/memory já publicados continuam canônicos até a integração.

- **Plano geral:** 2.0.3
- **Objetivo:** `OBJ-ALTOE-001`
- **Papel:** Neo4j, memória recorrente, RAG e explicação grounded de incidentes.
- **Resultado:** quando os logs agregados formarem um Incident, o detalhe da transação consegue navegar até uma explicação auditável e, quando houver, um precedente humano relevante.

## O que mudou

Não será criado um agente/RAG por transação. Outcome e classificação transacional são determinísticos e pertencem à pipeline; RAG continua depois de `Incident`. Isso evita custo, latência e alucinação no log. O novo trabalho de Altoé é preservar traceabilidade entre `transaction_id → evidence → incident → memory/explanation` sem transformar o precedente em causa atual.

O scenario generator vira harness interno; Graph RAG nunca recebe ground truth, configuração de efeitos, PAN/PII nem raw payload completo.

## Missão 2.3 — explicação grounded da interseção causal

- **Plano geral:** 2.3.0; **objetivo:** `OBJ-RCA6-ALTOE-001`; **own:** `TASK-RCA6-006` em memória e explicação.
- Consome `CTR-INC-001 v2` no CP2: a explicação apresenta interseção, início, impacto, perfil de decline, evidências e limitações. Decline profile é evidência, nunca a fonte da causa.
- Precedente histórico pode orientar playbook, mas não altera `SUPPORTED|INCONCLUSIVE`, categoria, valores ou ranking atuais.
- Handoff: fixture v2 com IDs rastreáveis para André e testes que provam preservação de autoridade causal para Rogério.

## Ownership e contratos

- **Own:** `CMP-MEM/EXP-001`, `CTR-MEM-001 v1.1`, `CTR-LLM-001 v1` e graph schema/prompts.
- **Consome:** `CTR-INC-001` com evidence refs/transaction links e alternativas causais; memória pode contextualizá-las, mas não reordená-las nem promover a causa atual.
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

### TASK-MEM-009 / LUM2-64 — evals do fluxo transacional 2.0

- Estender os evals do detalhe `CTR-TDI-001 v1` para falha sem Incident,
  isolamento de evidência entre transações, seed/configuração interna ausentes e
  memória indisponível com ExplanationBundle determinístico.
- **Pronto agora:** testes controlados que usam batch/transaction records e não
  importam o harness de background traffic.
- **Evidência de integração:** a branch
  `codex/integrate-grounded-transactions` valida tráfego de fundo → batch →
  worker → métricas → detalhe grounded; sem RCA, cada transação retorna
  `NO_INCIDENT` sem expor a seed.
- **Pendente de entrega:** revisão e merge dessa integração na `main`; a regra
  de vínculo continua aguardando o RCA real para preencher Incident/evidência.
- **Teste:** `tests/test_transaction_memory_evals.py`, além das regressões de
  `test_incident_transaction_filter.py` e `test_transaction_grounding.py`.

## Nova microtarefa

### TASK-EXP-004 — Trace transaction-to-incident grounded

- Validar que todo `related_incident_id` exposto no transaction detail resolve para Incident existente e que seus `evidence_ids` pertencem ao conjunto autorizado.
- Produzir resumo curto para o detalhe sem nova chamada LLM por transação; reutilizar ExplanationBundle do Incident ou template determinístico.
- Publicar o detalhe somente em `GET /v1/transactions/{transaction_id}/incidents` sob `CTR-TDI-001 v1`; a lista de Incidents permanece homogênea e o endpoint explicita `RESOLVED`, `PARTIAL` ou `NO_INCIDENT`.
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

## Adendo 2.4.4 — runtime OpenAI do agente

- **Plano geral:** 2.4.4; **contrato interno:** `CTR-AGT-RUN-001 v1`; **decisão:** `DEC-030` / `FL-20260830-TEAM-031`.
- O cliente configurado é `gpt-5.6-terra` com `reasoning.effort=high`, selecionado apenas no backend quando `OPENAI_API_KEY` estiver presente. O input continua restrito ao `EvidencePack` e ao `RetrievalTrace`; o contrato publicado `CTR-AGT-003 v1` não muda.
- Sem chave, o template determinístico permanece o fallback de demo. Com chave, falha do SDK, timeout ou resposta rejeitada persiste `UNAVAILABLE`; não há retry automático, ferramenta de pagamento, promoção de causa ou mutação de Incident.
- **Handoff para Rogério:** dependency lock, Railway Variables e smoke. **Prova:** teste do request Responses e dos guardrails existentes; validação online depende de credencial configurada fora do repositório.

## Adendo 2.5.1 — grounding de categoria causal

- **Plano geral:** 2.5.1; **contrato interno:** `CTR-AGT-GRD-001 v1`; **decisão:** `DEC-032` / `FL-20260830-TEAM-033`.
- **Entrada isolada:** `EvidencePack.root_cause.category` e `EvidencePack.rca_alternatives` já persistidos pelo motor; `RetrievalTrace` é apenas contexto recuperado.
- **Entrega:** prompt explicita que precedente não escolhe categoria e o validador recusa `suggested_category` fora do conjunto atual. Não há mudança em `CTR-AGT-003 v1`, API, UI, banco ou permissões de pagamento.
- **Prova de integração:** teste offline rejeita `ISSUER_OUTAGE` quando existe somente em precedente e aceita `PROVIDER_DEGRADATION` quando é alternativa atual; rerun sintético com chave retorna alternativa atual ou `UNAVAILABLE`, nunca categoria exclusiva do precedente.
- **Handoff para Rogério:** revisar/push do patch e registrar o resultado do rerun. Risco residual: o modelo pode ignorar o prompt, mas a saída será bloqueada de forma segura pelo validador.

## Adendo 2.7.0 — revisão humana auditável

- **Plano geral:** 2.7.0; **contrato:** `CTR-HRV-001 v1`; **decisão:** `DEC-035` / `FL-20260830-TEAM-038`.
- `APPROVED` chama a promoção já existente e adiciona o motivo do revisor como `HumanReview` no Neo4j. `REJECTED` cria o mesmo registro de auditoria, sem criar `HUMAN_CONFIRMED` nem contaminar a recuperação de precedentes.
- Persistência local por `review_id` é idempotente; uma repetição com conteúdo diferente é conflito. Se Neo4j estiver indisponível, a API informa falha e a mesma revisão pode ser reenviada, sem perder o motivo durável.
- A UI de detalhe envia a decisão explícita e mostra o resultado; ela nunca permite que o agente aprove ou recuse uma causa.

## Adendo 2.8.0 — primeira ocorrência de recorrência

- **Plano geral:** 2.8.0; **contratos:** `CTR-INC-001 v1` e `CTR-TXL-001 v1` aditivos; **decisão:** `DEC-036` / `FL-20260830-TEAM-039`.
- A persistência calcula uma assinatura de recorrência por categoria causal, métrica e escopo completo, separada do fingerprint de entrega por janela. O primeiro `detected_at` dessa assinatura permanece estável nas ocorrências futuras.
- A API devolve `recurrence_first_detected_at` no Incident e, nos logs de transação, em cada Incident relacionado. A interface deve exibir a data explicitamente, sem inferi-la de precedentes GraphRAG.

## Adendo 2.9.1 — default do runtime OpenAI

- **Plano geral:** 2.9.1; **contrato interno:** `CTR-AGT-RUN-001 v1`; **decisão:** `DEC-039` / `FL-20260830-ROGERIO-031`.
- O runtime configurado passa a `gpt-5.6-sol` com `reasoning.effort=medium`; o `EvidencePack`, o `RetrievalTrace`, o prompt e a validação grounded não mudam.
- A saída segue somente `HUMAN_ONLY`: sem ferramentas, promoção causal, escrita de Incident ou ação financeira. Falha de modelo, SDK ou timeout continua `UNAVAILABLE` e sem retry; sem chave, o fallback é `deterministic-template-v1`.
- **Handoff para Rogério:** defaults e runbook sincronizados; a prova externa permanece um smoke sintético no Railway, condicionado à chave e ao acesso ao modelo.

## Definition of Done

Evals de grounding/no-answer/injection/leakage passam; review gate sem bloqueantes; integration guardian valida Incident/API/UI; browser acceptance conjunto comprova links e estados.

## Linear

Parent: [LUM2-5](https://linear.app/lumenhack/issue/LUM2-5/entregar-memoria-graphrag-e-explicacao-grounded). `LUM2-23` foi atualizada; `TASK-EXP-004`→`LUM2-63`. Como `LUM2-25` já estava `Done`, ela foi preservada e a extensão transacional virou `TASK-MEM-009`→`LUM2-64`.
