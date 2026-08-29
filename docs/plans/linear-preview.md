# Sincronização no Linear — base 1.0.0, revisada contra o plano 1.5.0

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
| TASK-UI-005 | Implementar construtor visual e estados da demo | 90m | High | TASK-API-003 | TASK-UI-006 |
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
| TASK-API-003 | Expor catálogo, injeção e status somente em demo mode | 75m | High | TASK-DATA-006, CORE-001 | UI-005 |
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
| TASK-DATA-006 | Implementar stream, catálogo e injeção de combinação válida | 75m | High | TASK-DATA-001 | API-003 |
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
- Revisão 1.1.0: as issues de RCA, Incident, memória, explainer e UI foram relidas. Elas já colocam cálculo causal antes da memória e proíbem tratar similaridade como causa; nenhuma tarefa, owner ou relação precisou mudar. `no-answer` em `TASK-MEM-008` significa `NO_PRECEDENT` da recuperação, nunca `INCONCLUSIVE` causal.
- Preview de mudança 1.2.0: manter as mesmas issues, owners, estimativas e dependências, mas atualizar descrições/aceites de `TASK-UI-004` (LUM2-11), `TASK-MEM-006` (LUM2-20), `TASK-EXP-002` (LUM2-23), `TASK-EXP-003` (LUM2-24), `TASK-MEM-008` (LUM2-25), `TASK-INC-003` (LUM2-37), `TASK-RCA-002` (LUM2-55) e `TASK-EVAL-001` (LUM2-56) para exigir consulta de memória em Incident `INCONCLUSIVE` e cobrir `INCONCLUSIVE + MATCH` sem promover a causa atual. Escrita externa ainda não executada para esta revisão; exige confirmação explícita deste preview conforme a skill.
- Preview de mudança 1.3.0: nas mesmas issues e sem alterar relações, atualizar também `TASK-API-002` (LUM2-39) e os contratos citados nas issues acima para CTR-MEM-001 v1.1, cujo `memory_status` obrigatório diferencia `MATCH_FOUND`, `NO_PRECEDENT` e `MEMORY_UNAVAILABLE`. A confirmação explícita deste preview continua pendente antes da escrita externa.
- Preview de mudança 1.4.0: nas mesmas issues e sem alterar relações, atualizar `TASK-UI-005` (LUM2-12), `TASK-API-003` (LUM2-40) e `TASK-DATA-006` (LUM2-48) para o construtor visual sem código, `CTR-SCN-001 v2` e `CTR-API-001 v2`. A autorização atual cobre os documentos locais; a escrita externa no Linear permanece pendente até sincronização explícita.

## Sincronização 2.0.0 — concluída em 2026-08-29

### Escopo e política de preservação

- Destino permanece team `LUMEN HACKATHON`, projeto `Lumen — Yuno Hackathon`, label `Feature`, sem ciclo.
- Nenhuma issue `Done` será reaberta, renomeada ou reescrita. `TASK-UI-001/LUM2-8`, `TASK-API-003/LUM2-40` e `TASK-DATA-006/LUM2-48` passam a ser referenciadas nos planos como protótipo/harness preservado.
- Estados atuais do Linear permanecem como encontrados; trabalho local não é usado para presumir transição externa.
- Atualizações usam o ID Linear existente e o ID estável na descrição; novas issues são pesquisadas pelo ID estável antes da criação para garantir idempotência.
- Relações são escritas em segunda passagem e relidas. Em falha parcial, parar e inventariar; não repetir cegamente.

### Issues existentes a atualizar

| Linear | ID estável | Estado observado | Novo objetivo 2.0 | Dependências propostas |
| --- | --- | --- | --- | --- |
| LUM2-4 | OBJ-ANDRE-001 | Todo | Entregar frontend transaction-first Vercel e demo | filhas abaixo |
| LUM2-9 | TASK-UI-002 | Todo | Next.js, formulário 1..100 e geração de samples por quantidade/seed | contracts v3; desbloqueia UI-005/006 |
| LUM2-10 | TASK-UI-003 | Todo | Log, filtros, progresso backend-authored e detalhe | contracts v3; desbloqueia UI-004/006 |
| LUM2-11 | TASK-UI-004 | Todo | Integrar incidentes/recorrência ao transaction detail | UI-003, EXP-004 |
| LUM2-12 | TASK-UI-005 | Todo | Adapter Railway para catalog/sample/batch/list/detail | UI-002/003, TXN-API-001 |
| LUM2-13 | TASK-UI-006 | Todo | Browser acceptance e deploy Vercel → Railway | UI-004/005, DEPLOY-API-001 |
| LUM2-14 | TASK-DEMO-001 | Todo | Ensaiar demo transaction-first com seed e fallback | UI-006, INT-002 |
| LUM2-23 | TASK-EXP-002 | Todo | ExplanationBundle resolve evidence até transactions sem LLM por item | INC-003, MEM-006, EXP-001 |
| LUM2-25 | TASK-MEM-008 | Done | Preservada sem alteração; extensão transacional foi criada como TASK-MEM-009 / LUM2-64 | nenhuma mudança na issue concluída |
| LUM2-39 | TASK-API-002 | In Progress | Incidents filtráveis por transaction ID e eixos causal/memory separados | INC-003, EXP-003 |
| LUM2-41 | TASK-INT-001 | In Progress | Fatia Vercel → Railway → worker → log/detail → analytics | TXN-WORKER-001, UI-005, DATA-009 |
| LUM2-42 | TASK-INT-002 | In Progress | Preflight de schemas v3, volume, restart, CORS e browser deployed | INT-001, UI-006, MEM-008 |
| LUM2-49 | TASK-DATA-007 | Todo | Ground truth/config de efeitos ficam somente no harness interno | DATA-008/009 |
| LUM2-56 | TASK-EVAL-001 | Todo | Casos de batch misto, low volume e equivalência manual/background | DATA-009, RCA-002 |
| LUM2-57 | TASK-EVAL-002 | Todo | Holdout usa somente logs persistidos, sem input de efeito | EVAL-001, DATA-007 |

### Novas issues criadas

| Linear | ID estável | Título | Owner | Estimativa operacional | Prioridade | Blocked by | Desbloqueia |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LUM2-58 | TASK-TXN-API-001 | Expor API transaction-first e geração de samples | Rogério | 90m | Urgent | LUM2-28 | LUM2-59, LUM2-12 |
| LUM2-59 | TASK-TXN-WORKER-001 | Persistir lifecycle e retomar processamento idempotente | Rogério | 90m | Urgent | LUM2-58, LUM2-61 | LUM2-41, LUM2-60 |
| LUM2-60 | TASK-DEPLOY-API-001 | Publicar API v3/worker no Railway com volume e CORS | Rogério | 75m | High | LUM2-59 | LUM2-13, LUM2-42 |
| LUM2-61 | TASK-DATA-008 | Adaptar TransactionInput para outcome e eventos determinísticos | Renato | 75m | Urgent | LUM2-43, LUM2-28 | LUM2-59 |
| LUM2-62 | TASK-DATA-009 | Gerar samples e tráfego de fundo pela batch API comum | Renato | 75m | High | LUM2-61, LUM2-48 | LUM2-41, LUM2-56, LUM2-64 |
| LUM2-63 | TASK-EXP-004 | Validar trace grounded de transaction até incident | Gabriel Altoé | 60m | High | LUM2-23, LUM2-39 | LUM2-11, LUM2-64 |
| LUM2-64 | TASK-MEM-009 | Estender evals de memória para o fluxo transacional 2.0 | Gabriel Altoé | 60m | High | LUM2-25, LUM2-62, LUM2-63 | LUM2-42 |

### Corpo canônico das novas issues

#### TASK-TXN-API-001 — Expor API transaction-first e geração de samples

- **Problema:** a UI final não pode usar endpoints de efeito nem acessar stores; precisa cadastrar e consultar transações pelo Railway.
- **Outcome:** `CTR-API-001 v3` implementado para catalog, sample, batch, get batch, list e detail.
- **Inclui:** allowlist de campos, IDs server-side, batch atômico 1..100, idempotency key, seed efetiva, cursor/status filters e errors `404/409/422/503`.
- **Não inclui:** worker, outcome simulator, deploy, autenticação real ou endpoints públicos de cenário.
- **Aceite/teste:** schemas/fixtures validam; mesma seed repete samples; sample não persiste nem contém outcome; key repetida igual devolve IDs e conflitante retorna `409`; 101 itens retorna `422`.
- **Contratos/handoff:** produz `CTR-API-001 v3` e integra `CTR-TXN-001`; entrega OpenAPI/error map para André e interface ao worker.

#### TASK-TXN-WORKER-001 — Persistir lifecycle e retomar processamento idempotente

- **Problema:** progresso visual não pode ser timer do frontend nem desaparecer em restart.
- **Outcome:** worker durável grava stage/progress/outcome/classification e reconcilia jobs presos.
- **Inclui:** persist before `202`, lease/retry, stage monotônico, duplicate delivery e separação transaction failure/pipeline failure.
- **Não inclui:** SSE, queue externa ou Postgres migration.
- **Aceite/teste:** crash entre stages retoma o mesmo ID; reentrega não duplica eventos/métricas; terminal tem 100%; pipeline error nunca vira decline.
- **Contratos/handoff:** produz `CTR-TXL-001`; entrega records reais à API/UI.

#### TASK-DEPLOY-API-001 — Publicar FastAPI/worker no Railway com volume e CORS

- **Problema:** a Vercel precisa de uma única API pública com persistência privada.
- **Outcome:** Railway health, domínio, volume, env, start command e CORS validados.
- **Inclui:** origem Vercel production/preview/local explícita, volume path, restart smoke e degraded health.
- **Não inclui:** múltiplas replicas ou migração Postgres.
- **Aceite/teste:** Vercel permitida e origem aleatória negada; batch sobrevive restart; store/Neo4j não têm exposição pública.
- **Contratos/handoff:** produz `CTR-DEP-001`; entrega base URL a André.

#### TASK-DATA-008 — Adaptar TransactionInput para outcome e eventos determinísticos

- **Problema:** agora o usuário fornece fatos, mas a pipeline ainda precisa produzir resposta simulada e eventos sem receber o resultado esperado.
- **Outcome:** adapter puro `TransactionInput + seed/context → outcome/events CTR-EVT-001`.
- **Inclui:** regras condicionais, status, response/decline normalizado, latência e reprodutibilidade.
- **Não inclui:** API, persistência, métricas agregadas ou LLM.
- **Aceite/teste:** mesma seed/contexto repete; cobre success/failure/unknown; não aceita PAN/PII nem effect/ground truth; retry não duplica.
- **Handoff:** Rogério integra no worker.

#### TASK-DATA-009 — Gerar samples e tráfego de fundo pela batch API comum

- **Problema:** a demo precisa de inputs rápidos e volume para analytics sem configuração manual nem escrita direta no banco.
- **Outcome:** sample generator por quantidade/seed e harness interno que chama a batch API.
- **Inclui:** catálogo vigente, defaults opcionais, seed retornada e background traffic.
- **Não inclui:** outcome no sample ou formulário de efeitos público.
- **Aceite/teste:** 1..100 samples válidos/reprodutíveis; todos os valores pertencem ao catálogo; harness não escreve no DuckDB; métricas só mudam após processamento.
- **Handoff:** sample function para Rogério; fixtures/seed para André.

#### TASK-EXP-004 — Validar trace grounded de transaction até incident

- **Problema:** o detalhe precisa explicar incidentes relacionados sem executar uma chamada RAG por transaction nem vazar evidência de outra.
- **Outcome:** resolver `transaction_id → evidence → incident → ExplanationBundle` com validação de escopo.
- **Inclui:** no incident, one/multiple incidents, missing evidence, memory/model down e cross-transaction leakage.
- **Não inclui:** classificação do outcome ou causa baseada em precedente.
- **Aceite/teste:** todo related ID existe e pertence às evidências autorizadas; resumo reutiliza bundle/template; `INCONCLUSIVE` não é promovido; falhas ficam explícitas.
- **Handoff:** fixtures/semântica para André e regra de resolução para Rogério.

#### TASK-MEM-009 — Estender evals de memória para o fluxo transacional 2.0

- **Motivo da nova issue:** `TASK-MEM-008 / LUM2-25` já estava `Done`; seu escopo/evidências não foram reescritos.
- **Outcome:** cobrir transaction sem Incident, múltiplas transactions por Incident, ausência de vazamento de seed/config/ground truth, Neo4j/model down e cross-transaction leakage.
- **Aceite:** resultado sem Incident não inventa explicação; related transactions ficam no escopo; evals de LUM2-25 continuam passando.
- **Handoff:** evidência para Rogério/André e bloqueio explícito do preflight LUM2-42.

### Resultado e carga auditada

- 54 issues existentes preservadas; 14 descrições abertas/em andamento atualizadas; 7 novas issues; total final 61.
- Novas cargas: André 0 issues novas (6 abertas replanejadas), Rogério +3, Renato +2, Altoé +2.
- Caminho crítico 2.0: `contracts → DATA-008 + TXN-API-001 → TXN-WORKER-001 → UI-005 + DATA-009 → INT-001 → DEPLOY-API-001 + UI-006 → INT-002`.
- Regra solicitada aplicada: nenhuma issue `Done` teve título, descrição ou estado alterados; a nova necessidade de LUM2-25 virou LUM2-64.
- Auditoria: 21/21 issues relidas com projeto, team, owner, parent, label, estado, ID estável e relações esperadas; nenhuma divergência encontrada.
- **Estado de escrita externa:** `SYNCED`. As relações foram escritas em segunda passagem e auditadas depois.
