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

## Validação contra Neo4j local

Em 2026-08-29, os cenários críticos foram executados contra a instância Neo4j
local saudável, usando o bootstrap da aplicação e o adaptador
`Neo4jIncidentRepository` da mesma cópia Git. O seed foi reaplicado de forma
idempotente antes da consulta.

| Caso | Resultado observado |
| --- | --- |
| Recorrência Mastercard D-2 | `MATCH_FOUND` para `INC-HIST-002D-MASTERCARD` |
| Combinação nova Visa | `NO_PRECEDENT` |
| Mesma marca, mas decline codes e forma temporal incompatíveis | `NO_PRECEDENT` |
| Dependência indisponível | `MEMORY_UNAVAILABLE` |

## Limitações remanescentes

Este conjunto ainda não mede recall, latência sob carga, rerank vetorial,
isolamento por tenant nem um holdout independente de combinações geradas pelo
Renato. Esses pontos não invalidam os critérios de aceitação da baseline
determinística; tornam-se gates quando houver corpus e rerank correspondentes.

