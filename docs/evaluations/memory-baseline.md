# Avaliação baseline da memória — CTR-MEM-001

- **Versão do baseline:** `structured-v1`
- **Corpus:** seed local `INC-HIST-002D-MASTERCARD`, confirmado por humano
- **Modo:** desenvolvimento, repositório in-memory; não é holdout nem validação de Neo4j real
- **Data:** 2026-08-29

| Caso | Resultado esperado | Resultado observado |
| --- | --- | --- |
| EVAL-MEM-001 — recorrência Mastercard D-2 | `MATCH_FOUND`, precedente D-2 em top-1 | PASS |
| EVAL-MEM-002 — combinação nova Visa | `NO_PRECEDENT`, sem alterar o diagnóstico atual | PASS |
| EVAL-MEM-003 — causa atual inconclusiva | `MATCH_FOUND`, mantendo `INCONCLUSIVE` | PASS |
| EVAL-MEM-004 — histórico não confirmado | `NO_PRECEDENT` | PASS |
| EVAL-MEM-005 — memória indisponível | `MEMORY_UNAVAILABLE`, distinto de ausência de precedente | PASS |

## Métricas observadas

- `memory_recurrence_precision_at_1`: 1/1 no caso de recorrência do conjunto de desenvolvimento.
- `no_precedent` correto: 2/2 nos casos de combinação nova e precedente não confirmado.
- Preservação de `INCONCLUSIVE`: 1/1.
- Distinção de falha operacional: 1/1.

## Limitações e próximo gate

Este conjunto não mede recall, latência de Neo4j, rerank vetorial, isolamento por tenant nem um holdout de combinações do Renato. Antes de marcar a tarefa como concluída, executar os mesmos cenários contra Neo4j real e acrescentar holdout independente.

