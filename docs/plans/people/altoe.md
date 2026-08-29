# Plano individual — Altoé

## Missão

- **Plano geral:** 1.3.0
- **Objetivo:** `OBJ-ALTOE-001`
- **Papel:** Neo4j, memória recorrente, Graph RAG, explicação grounded e corroboration externa.
- **Orçamento:** 13–14h de implementação; H15–H19 integração/validação/pitch support.
- **Resultado:** o sistema reconhece corretamente o incidente Mastercard de dois dias antes, explica por que é semelhante e não inventa precedente quando não há evidência.

## Context pack

O detector e o RCA são determinísticos. Altoé recebe todo `Incident` já calculado — `SUPPORTED` ou `INCONCLUSIVE` —, persiste/consulta memória e devolve precedentes com trace. O LLM sintetiza somente campos estruturados e escolhe um playbook permitido. Causas antigas só têm autoridade sobre o incidente histórico quando `HUMAN_CONFIRMED`; a recomendação permanece `HUMAN_ONLY`.

Ausência de precedente não é no-answer causal: `matches=[]` preserva integralmente `Incident.root_cause`. Se a causa atual já for `INCONCLUSIVE`, somente a combinação `INCONCLUSIVE + NO_PRECEDENT` termina sem causa nem contexto histórico. Se houver match, o precedente, sua causa humana e seu playbook são exibidos como orientação, sem elevar a causa atual a `SUPPORTED`.

Memória também recupera `prior_playbook_id` e a resolução humana anterior. O explainer pode priorizar esse playbook somente quando causa, escopo e precondições atuais forem compatíveis; diferenças viram limitações explícitas. A recomendação continua `HUMAN_ONLY`.

## Ownership e limites

- **Own:** `CMP-MEM-001`, `CMP-EXP-001`, `CMP-EXT-001`; diretórios propostos `app/memory/`, `app/explanation/`, `graph/`.
- **Produz:** `CTR-MEM-001`, `CTR-LLM-001`, `CTR-EXT-001`.
- **Consome:** `CTR-INC-001`.
- **Hotspots:** env names e dependency file coordenados por Rogério; Incident schema não pode ser alterado localmente.
- **Fora de escopo:** guardar raw transactions no grafo, calcular confiança/impacto, executar playbook ou usar ground truth oculto.

## Interfaces

### CTR-INC-001 v1 — consumido

Campos mínimos: `incident_id`, `scope`, `metrics`, `root_cause`, `impact`, `evidence`, `limitations`, `correlation_id`. Taxas 0..1; dinheiro inteiro; timestamps UTC.

### CTR-MEM-001 v1.1 — produzido

```text
SimilarIncidentResult {
  schema_version: "1.1";
  query_incident_id: string;
  memory_status: "MATCH_FOUND"|"NO_PRECEDENT"|"MEMORY_UNAVAILABLE";
  matches: [{incident_id, occurred_at, confirmation,
             structured_score, semantic_score|null,
             matching_factors[], different_factors[],
             confirmed_cause, prior_playbook_id, evidence_ids[]}];
  retrieval_trace: {cypher_filter, candidate_count, embedding_model|null,
                    index_version, fallback_used};
  correlation_id: string;
}
```

Sem match válido: `memory_status="NO_PRECEDENT"` e `matches=[]`; falha depois dos fallbacks: `memory_status="MEMORY_UNAVAILABLE"` e `matches=[]`. Nunca mudar `root_cause`. A query aceita causa atual nula e recupera por escopo, métricas, decline profile e forma temporal. Timeout 2s; fallback Cypher/fixture.

### CTR-LLM-001 v1 — produzido

```text
ExplanationBundle {
  schema_version: "1.0";
  incident_id: string;
  executive_summary: string;
  operations_summary: string;
  what_happened: string;
  where_and_why: string;
  recurrence_statement: string|null;
  evidence_ids: string[];
  playbook_id: string;
  recommended_action: string;
  execution: "HUMAN_ONLY";
  limitations: string[];
  model_version: string|"deterministic-template";
}
```

Structured Output obrigatório; output com evidence ID inexistente é rejeitado e vira template.

### CTR-EXT-001 v1 — produzido, opcional

```text
ExternalCorroborationResult {
  schema_version: "1.0";
  incident_id: string;
  status: "CORROBORATED"|"NOT_CHECKED"|"UNAVAILABLE";
  sources: [{publisher, url, retrieved_at, summary, evidence_ids[]}];
  correlation_id: string;
}
```

Consulta read-only somente fontes oficiais, com timeout de 5s. O resultado é rotulado `CORROBORATION`, nunca prova da causa atual; se a funcionalidade for cortada, devolve `NOT_CHECKED` em vez de omitir o estado.

## Plano de execução

### TASK-ALTOE-001 — Modelar grafo e seed histórico

- **Tempo:** H1–H3.
- **Output:** constraints, nodes/edges e `INC-HIST-002D-MASTERCARD` confirmado.
- **Aceite:** seed idempotente; grafo liga Incident a Brand, Provider, Country, Cause e Playbook.
- **Teste:** executar seed duas vezes sem duplicar; query retorna um incidente.

### TASK-ALTOE-002 — Implementar recuperação estruturada

- **Tempo:** H3–H6.
- **Método:** Cypher prefilter por entidades compartilhadas; score ponderado por escopo, decline profile, metric shifts e temporal shape.
- **Aceite:** Mastercard retorna histórico correto em top-1; incidente diferente não retorna falso match acima do threshold.
- **Evidência:** retrieval trace completo.

### TASK-ALTOE-003 — Adicionar rerank semântico opcional

- **Tempo:** H6–H7:30.
- **Ferramenta:** `text-embedding-3-small`; índice versionado.
- **Aceite:** structured score continua visível; vector failure não quebra retorno.
- **Corte:** primeira feature removida se Neo4j/API atrasar.

### TASK-ALTOE-004 — Implementar explainer grounded e playbooks

- **Tempo:** H7:30–H10.
- **Ferramenta:** Responses API, `gpt-5.6-terra`, Structured Outputs, uma chamada por incidente.
- **Aceite:** 100% das afirmações factuais citam evidence IDs; playbook vem do catálogo; solução anterior só é priorizada como ação provável quando a causa atual é suportada e as precondições são compatíveis; com causa atual inconclusiva, aparece apenas como roteiro de investigação com limitação explícita; nenhuma tool financeira existe.
- **Fallback:** formatter determinístico.

### TASK-ALTOE-005 — No-answer, adversarial e external corroboration

- **Tempo:** H10–H12.
- **Aceite:** documento/resultado recuperado não altera instruções; cross-incident leakage falha; web somente fonte oficial e é rotulada corroboration.
- **Corte:** web externo é removido antes de reduzir memory tests.

### TASK-ALTOE-006 — Evals de memória/RAG

- **Tempo:** H12–H15.
- **Casos:** exact recurrence, partial recurrence, causa atual suportada sem match, causa atual inconclusiva com/sem match, conflicting precedent, unconfirmed cause, prompt injection, Neo4j down, model down.
- **Métricas:** precision@1, `NO_PRECEDENT` correto sem alterar causa atual, evidence coverage, applicability do playbook anterior e fallback success.

## Git e handoffs

- Branch sugerida: `feat/OBJ-ALTOE-001-incident-memory`.
- Entregar mock `CTR-MEM-001` a André/Rogério em H3 antes da implementação completa.
- Não editar DuckDB schema ou Incident schema sem change control.
- `READY TO MERGE`: seed idempotente, evals, fallback e contract tests passam.

## Riscos e autonomia

- Pode ajustar pesos de similarity com evidência do eval dataset; registre decisão se threshold material mudar.
- Deve parar se recuperação exigir acesso a ground truth ou transações de outro tenant.
- Pode cortar vector/web; não pode cortar recurrence estruturada.

## Sincronização Linear

- Parent: [LUM2-5](https://linear.app/lumenhack/issue/LUM2-5/entregar-memoria-graphrag-e-explicacao-grounded).
- Microtarefas: `TASK-MEM-001`→`LUM2-15`, `TASK-MEM-002`→`LUM2-16`, `TASK-MEM-003`→`LUM2-17`, `TASK-MEM-004`→`LUM2-18`, `TASK-MEM-005`→`LUM2-19`, `TASK-MEM-006`→`LUM2-20`, `TASK-MEM-007`→`LUM2-21`, `TASK-EXP-001`→`LUM2-22`, `TASK-EXP-002`→`LUM2-23`, `TASK-EXP-003`→`LUM2-24`, `TASK-MEM-008`→`LUM2-25`, `TASK-EXT-001`→`LUM2-26`.
- Fonte completa de dependências: `docs/plans/linear-preview.md`.
