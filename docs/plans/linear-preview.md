# Preview de publicação no Linear — Plano 1.0.0

## Destino descoberto

- Workspace confirmado: `Lumen` (`https://linear.app/lumenhack`)
- Team confirmado: `LUMEN HACKATHON`
- Projeto criado: [Lumen — Yuno Hackathon](https://linear.app/lumenhack/project/lumen-yuno-hackathon-fd0533f171d5)
- Ciclo: nenhum ciclo existe para o team `Lumen`; proposta: sem ciclo
- Estado inicial: `Todo`
- Label existente: `Feature`
- Estimativa do Linear: não preencher, pois não existe convenção observável; duração operacional fica na descrição
- Hierarquia criada: 4 parent issues + 50 microtarefas abaixo

## Mapeamento de pessoas

| Pessoa do plano | Usuário Linear | Estado |
| --- | --- | --- |
| André | André Ferreira — `decente_primitiva1o@icloud.com` | match exato e ativo |
| Rogério | `Rogerio '` — `rogeriodelimaf@gmail.com` | match exato e ativo |
| Altoé | Gabriel Altoé Batista — `gabrielaltoebatista000@gmail.com` | match exato e ativo |
| Renato | Renato Bello — `renatolimabello@gmail.com` | match exato e ativo |

## Parent issues

| ID | Título | Responsável | Prioridade | Estado |
| --- | --- | --- | --- | --- |
| OBJ-ANDRE-001 / [LUM2-4](https://linear.app/lumenhack/issue/LUM2-4/entregar-narrativa-dashboard-e-demo-executiva) | Entregar dashboard e narrativa da demo | André | High | Todo |
| OBJ-ALTOE-001 / [LUM2-5](https://linear.app/lumenhack/issue/LUM2-5/entregar-memoria-graphrag-e-explicacao-grounded) | Provar memória recorrente grounded | Altoé | High | Todo |
| OBJ-ROGERIO-001 / [LUM2-6](https://linear.app/lumenhack/issue/LUM2-6/entregar-ingestao-contratos-e-api-integradora) | Entregar core contratual e API integrada | Rogério | High | Todo |
| OBJ-RENATO-001 / [LUM2-7](https://linear.app/lumenhack/issue/LUM2-7/entregar-dados-sinteticos-deteccao-e-rca) | Entregar dados, detector e RCA preciso | Renato | High | Todo |

## Microtarefas — André

| ID | Título | Duração | Prioridade | Bloqueada por | Desbloqueia |
| --- | --- | --- | --- | --- | --- |
| TASK-UI-001 | Montar shell Streamlit com Incident fixture | 45m | High | TASK-CON-001 | TASK-UI-002,003 |
| TASK-UI-002 | Renderizar resumo executivo e impacto local | 45m | High | TASK-UI-001 | TASK-UI-006 |
| TASK-UI-003 | Renderizar drill-down operacional e evidence IDs | 60m | High | TASK-UI-001 | TASK-UI-004 |
| TASK-UI-004 | Explicar recorrência com fatores iguais e diferentes | 45m | High | TASK-UI-003, TASK-MEM-006 | TASK-UI-006 |
| TASK-UI-005 | Implementar controles e estados da demo | 60m | High | TASK-API-003 | TASK-UI-006 |
| TASK-UI-006 | Validar dashboard no navegador e projetor | 60m | High | TASK-UI-002,004,005 | TASK-DEMO-001 |
| TASK-DEMO-001 | Ensaiar pitch, Q&A e fallback da demo | 60m | High | TASK-INT-002, TASK-UI-006 | apresentação |

Carga: 7 microtarefas, aproximadamente 6h15, intencionalmente menor.

## Microtarefas — Altoé

| ID | Título | Duração | Prioridade | Bloqueada por | Desbloqueia |
| --- | --- | --- | --- | --- | --- |
| TASK-MEM-001 | Criar adapter Neo4j com health e fallback | 45m | High | TASK-CORE-001 | TASK-MEM-002 |
| TASK-MEM-002 | Criar constraints e modelo do grafo | 45m | High | TASK-MEM-001 | TASK-MEM-003,005 |
| TASK-MEM-003 | Semear incidente Mastercard de dois dias antes | 45m | High | TASK-MEM-002 | TASK-MEM-004,005 |
| TASK-MEM-004 | Provar idempotência do seed histórico | 30m | Medium | TASK-MEM-003 | TASK-MEM-008 |
| TASK-MEM-005 | Recuperar candidatos confirmados com Cypher | 60m | High | TASK-MEM-002,003 | TASK-MEM-006 |
| TASK-MEM-006 | Calcular similaridade e trace de diferenças | 60m | High | TASK-MEM-005 | TASK-UI-004, EXP-002 |
| TASK-MEM-007 | Adicionar rerank vetorial com fallback | 60m | Low | TASK-MEM-006 | TASK-MEM-008 |
| TASK-EXP-001 | Implementar catálogo versionado de playbooks | 45m | High | TASK-CON-001 | TASK-EXP-002 |
| TASK-EXP-002 | Gerar ExplanationBundle estruturado | 60m | High | TASK-MEM-006, EXP-001 | TASK-EXP-003 |
| TASK-EXP-003 | Validar evidence IDs e criar template fallback | 60m | High | TASK-EXP-002 | TASK-API-002, MEM-008 |
| TASK-MEM-008 | Executar evals de recurrence, no-answer e injection | 60m | High | TASK-MEM-004,006, EXP-003 | TASK-INT-002 |
| TASK-EXT-001 | Corroborar incidente em fonte oficial | 45m | Low | TASK-EXP-003 | opcional |

Carga: 12 microtarefas, aproximadamente 10h15; vector e web são cortes explícitos.

## Microtarefas — Rogério

| ID | Título | Duração | Prioridade | Bloqueada por | Desbloqueia |
| --- | --- | --- | --- | --- | --- |
| TASK-CORE-001 | Preparar package, env e health skeleton | 45m | High | nenhuma | MEM-001, API-001 |
| TASK-CON-001 | Validar schemas, fixtures e OpenAPI v1 | 45m | High | nenhuma | todos os consumidores |
| TASK-ING-001 | Persistir raw imutável e canonical em DuckDB | 60m | High | TASK-CON-001 | ING-002, AGG-001 |
| TASK-ING-002 | Normalizar status, methods e decline codes | 60m | High | TASK-ING-001 | ING-003,004 |
| TASK-ING-003 | Deduplicar eventos e quarentenar inválidos | 45m | High | TASK-ING-002 | AGG-001 |
| TASK-ING-004 | Aplicar ordering, watermark e terminal guard | 60m | High | TASK-ING-002 | AGG-001 |
| TASK-AGG-001 | Agregar janelas e dois denominadores | 60m | High | TASK-ING-001,003,004 | AGG-002, DET-001 |
| TASK-AGG-002 | Testar métricas e revisões de janela | 45m | High | TASK-AGG-001 | INT-001 |
| TASK-INC-001 | Separar candidatos em incidentes independentes | 60m | High | TASK-RCA-002 | INC-002 |
| TASK-INC-002 | Calcular prioridade e GMV local em risco | 45m | High | TASK-INC-001 | INC-003 |
| TASK-INC-003 | Serializar Incident v1 e estado INCONCLUSIVE | 45m | High | TASK-INC-002 | API-002, MEM-005 |
| TASK-API-001 | Expor health e current metrics | 45m | High | TASK-CORE-001, AGG-001 | INT-001 |
| TASK-API-002 | Expor incidents e explanation | 45m | High | TASK-INC-003, EXP-003 | UI-005, INT-002 |
| TASK-API-003 | Expor injection somente em demo mode | 45m | High | TASK-DATA-006, CORE-001 | UI-005 |
| TASK-INT-001 | Integrar primeira fatia ponta a ponta | 60m | High | TASK-AGG-002, DET-004, API-001, UI-002 | demais profundidade |
| TASK-INT-002 | Executar preflight, contratos e smoke final | 60m | High | objetivos completos | TASK-DEMO-001 |

Carga: 16 microtarefas, aproximadamente 14h15 incluindo coordenação de integração.

## Microtarefas — Renato

| ID | Título | Duração | Prioridade | Bloqueada por | Desbloqueia |
| --- | --- | --- | --- | --- | --- |
| TASK-DATA-001 | Definir dimensões e probabilidades do gerador | 45m | High | TASK-CON-001 | DATA-002,003,004 |
| TASK-DATA-002 | Gerar 90 dias com sazonalidade | 60m | High | TASK-DATA-001 | DATA-005, DET-001 |
| TASK-DATA-003 | Gerar outcomes condicionais e retries | 60m | High | TASK-DATA-001 | DATA-005 |
| TASK-DATA-004 | Gerar latências e decline distributions | 60m | High | TASK-DATA-001 | DATA-005 |
| TASK-DATA-005 | Persistir Parquet e medir benchmark | 45m | Medium | TASK-DATA-002,003,004 | ING-001 |
| TASK-DATA-006 | Implementar live stream e scenario injection | 60m | High | TASK-DATA-001 | API-003 |
| TASK-DATA-007 | Isolar ground truth do runtime | 30m | High | TASK-DATA-006 | EVAL-002 |
| TASK-DET-001 | Calcular baseline sazonal com pooling | 60m | High | TASK-AGG-001, DATA-002 | DET-002,003 |
| TASK-DET-002 | Detectar queda de approval com baixa amostra | 60m | High | TASK-DET-001 | DET-004 |
| TASK-DET-003 | Detectar p95 e timeout robustamente | 60m | High | TASK-DET-001 | DET-004 |
| TASK-DET-004 | Emitir AnomalyCandidate v1 e evidências | 45m | High | TASK-DET-002,003 | RCA-001, INT-001 |
| TASK-RCA-001 | Explorar slices com beam search hierárquico | 60m | High | TASK-DET-004 | RCA-002 |
| TASK-RCA-002 | Ranquear contribuição e eliminar redundância | 60m | High | TASK-RCA-001 | INC-001, EVAL-001 |
| TASK-EVAL-001 | Cobrir simultâneos, mix shift e inconclusive | 60m | High | TASK-RCA-002 | EVAL-002 |
| TASK-EVAL-002 | Rodar holdout e congelar thresholds | 60m | High | TASK-EVAL-001, DATA-007 | INT-002 |

Carga: 15 microtarefas, aproximadamente 13h45.

## Totais e caminho crítico

- 4 parent issues + 50 microtarefas = 54 issues.
- André: 7; Altoé: 12; Rogério: 16; Renato: 15.
- Caminho crítico: `CON → DATA/ING → AGG → DET → RCA → INC → MEM/EXP → API → UI → INT/DEMO`.
- As relações foram criadas somente após todos os identificadores existirem, na segunda passagem.

## Confirmação

Autorização recebida em 2026-08-29 para criar o projeto `Lumen — Yuno Hackathon` no team `LUMEN HACKATHON`, sem ciclo, estado `Todo`, label existente `Feature`, com os quatro assignees acima.

## Resultado da sincronização

- Publicação concluída: 4 parent issues + 50 microtarefas = 54 issues.
- Auditoria de destino: 54/54 no project e team corretos, em `Todo`, com label `Feature` e descrição contendo ID estável.
- Auditoria de carga: André 7 filhas; Gabriel Altoé 12; Rogério 16; Renato 15.
- Auditoria de relações: 50 microtarefas relidas; 48 com `blockedBy` e duas raízes (`TASK-CORE-001`, `TASK-CON-001`); zero divergências.
- Auditoria de contratos: 21 descrições tiveram aliases corrigidos para `CTR-EVT-001`, `CTR-AGG-001` e `CTR-DET-001`; releitura confirmou zero referência não canônica.
- Faixas Linear: André `LUM2-8`–`LUM2-14`; Altoé `LUM2-15`–`LUM2-26`; Rogério `LUM2-27`–`LUM2-42`; Renato `LUM2-43`–`LUM2-57`.
- Evidência e decisão: `FL-20260829-TEAM-009` em `docs/flight-log.md`.
