# Plano individual — André

## Missão 2.2.1

> A pasta `web/` está integrada ao backend transaction-first pelos contratos v3. Fixtures permanecem apenas no modo offline explícito; deploy e smoke Railway/Vercel continuam pendentes até evidência no ambiente real.

- **Plano geral:** 2.2.1
- **Objetivo:** `OBJ-ANDRE-002`
- **Papel:** frontend Next.js, experiência transaction-first, integração Vercel → Railway e acceptance visual.
- **Resultado:** inserir uma ou várias transações manualmente ou gerar samples por quantidade, acompanhar logs e abrir classificação/incidentes sem calcular nenhum fato no navegador; seed permanece capacidade opcional da API.
- **Prioridade atual:** sistema front funcional; pitch só depois da fatia ao vivo.

## O que mudou

O Streamlit de `TASK-UI-001` continua como protótipo visual e fallback. O produto final passa a ser Next.js na Vercel. O construtor de efeitos de `TASK-UI-005` não é mais uma tela pública: cenários ficam internos para gerar tráfego/evals. André não pede approval rate, queda, latência, timeout, decline, causa ou ground truth.

A tela inicial aceita de 1 a 100 `TransactionInput`. Para acelerar a demo, `Generate sample transactions` chama o Railway somente com a quantidade visível, recebe inputs válidos e editáveis e os mostra antes do `Submit batch`; seed permanece opcional/interna na API. Todos os outcomes, classificações, métricas e incidentes surgem depois, no backend.

O shell desktop usa sidebar `sticky` e conteúdo em colunas separadas; em mobile, os mesmos destinos ficam numa barra inferior fixa com safe area. Logs destacam dados retornados para `FAILED` e `UNKNOWN`; Incidents expõe diagnóstico, memória e uma atenção técnica sem inventar causa para `UNKNOWN`.

## Ownership e limites

- **Own:** `CMP-WEB-001`, diretório `web/`, rotas `/transactions/*`, `/incidents/*`, client HTTP e configuração Vercel.
- **Consome:** `CTR-TXN-001 v1`, `CTR-TXL-001 v1`, `CTR-API-001 v3`, `CTR-INC-001` (incluindo `root_cause.alternatives` e `recommendation_class` quando presentes), `CTR-MEM-001` e `CTR-LLM-001`.
- **Somente API:** nenhuma query a DuckDB/Neo4j e nenhum cálculo de taxa, causa, confiança ou impacto.
- **Segurança:** campos allowlisted; não coletar PAN, CVV, nome, e-mail ou PII; não oferecer ação financeira.
- **Hotspot:** contratos e env são coordenados por Rogério; André coordena somente `web/`.

## Rotas e estados

### `/transactions/new`

- linhas dinâmicas com add, duplicate, remove e validação por campo;
- gerador de samples: quantidade 1..100, `POST /v1/transaction-samples`; seed é opcional/interna na API;
- review dos samples; nada é persistido até `Submit batch`;
- `POST /v1/transaction-batches` com idempotency key; resposta `202` redireciona para o log do batch;
- erro preserva todas as linhas e indica exatamente o item/campo inválido.

### `/transactions`

- filtros `ALL|SUCCEEDED|FAILED|PROCESSING|UNKNOWN` e paginação por cursor;
- polling 1–2s somente quando há item `PROCESSING`;
- progress bar recebe `stage` e `progress_percent` do Railway; sem timer simulado;
- status não depende apenas de cor; loading, empty, error, stale e retry são explícitos.
- cada linha expõe somente outcome, classificação, reason, confidence, evidence IDs e incidentes retornados pelo backend.

### `/transactions/[id]`

- input, timeline, outcome, classification, evidence IDs e incidentes relacionados;
- decline de negócio não é confundido com `PIPELINE_FAILED`;
- sem incidente relacionado é um estado normal, não erro.

### `/incidents`

- migra os cards já construídos, incluindo recorrência e limites causais;
- mostra separadamente causa atual e memória histórica, incluindo recommendation `HUMAN_ONLY`, limitations e trace.
- inclui fila de atenção para `UNKNOWN`; somente `CTR-INC-001` recebe causa/recommendation de Incident.

## Microtarefas e ordem

### TASK-UI-001 / LUM2-8 — protótipo Streamlit

- **Estado:** concluída; preservar como referência/fallback, sem expandir para o produto final.
- **Evidência existente:** shell, fixtures, estados causais e UI de recorrência.

### TASK-UI-002 / LUM2-9 — Next.js + formulário multi-input + samples

- **Linear:** `Done`; a integração live permanece em `LUM2-12`.

- Criar shell Next.js responsivo, client tipado, `NEXT_PUBLIC_API_BASE_URL` e `/transactions/new`.
- Implementar 1..100 linhas, add/duplicate/remove e `Generate sample transactions` por quantidade.
- **Mock:** catálogo, sample request/response e batch fixtures.
- **Aceite:** nenhum option hardcoded; geração preenche lote editável; envio 1 e múltiplos funciona; erro preserva formulário.
- **Independe de:** backend real; começa pelas fixtures congeladas.

### TASK-UI-003 / LUM2-10 — log, filtros, progresso e detalhe

- **Estado:** concluída localmente; suite web e teste live são gates da integração.

- Implementar `/transactions`, `/transactions/[id]`, filtros, cursor, polling e estados.
- **Aceite:** processing mostra stage real; filtros não misturam falha técnica e decline; falha/UNKNOWN exibem diagnóstico disponível; refresh preserva URLs; detalhe linka Incident sem fabricar action.
- **Independe de:** API real usando `transaction-list.json` e records.

### TASK-UI-004 / LUM2-11 — incidentes e recorrência dentro do novo fluxo

- **Estado:** concluída localmente; detalhe usa `GET /transactions/{id}/incidents` e lista usa o filtro homogêneo contratado.

- Migrar cards para `/incidents`, adicionar o destino à sidebar e linkar a partir do detalhe da transação.
- **Aceite:** `INCONCLUSIVE + MATCH` continua inconclusivo; diagnóstico contratado fica legível; `UNKNOWN` aparece em atenção técnica sem causa inventada.
- **Bloqueio live:** `TASK-EXP-004` e filtro `transaction_id` de Rogério; layout pode avançar por fixture.

### TASK-UI-005 / LUM2-12 — adapter Railway e estados live

- **Estado:** concluída localmente; falta somente comprovação no Railway/Vercel real.

- Substituir o adapter de cenário público por catalog/sample/batch/list/detail/incident.
- Centralizar timeout, base URL, error mapping e polling cancellation.
- **Aceite:** browser não acessa store/secret; API down mostra `BACKEND UNAVAILABLE`; chamadas duplicadas preservam idempotência.
- **Bloqueio live:** `TASK-TXN-API-001`; pode avançar por OpenAPI/mocks.

### TASK-UI-006 / LUM2-13 — Vercel e browser acceptance

- Configurar production/preview env, executar build e validar Vercel → Railway.
- Cobrir teclado, foco, contraste, reduced motion, add/remove, samples, batch misto, filtros, progress, detail, refresh, API down, console e rede.
- **Bloqueio:** API Railway e CORS prontos.

### TASK-DEMO-001 / LUM2-14 — demo final

- Somente após a fatia deployed: seed de ensaio, lote rápido, incidente e fallback honesto.

## Paralelismo recomendado para André

Rodar simultaneamente três tasks Codex sem colisão de arquivos:

1. **Lane A:** `web/app/transactions/new/**` e componentes de formulário/sample.
2. **Lane B:** `web/app/transactions/**` exceto `new`, tabela, filtros, progress e detail.
3. **Lane C:** client tipado/testes/fixtures em `web/lib/api/**` e `web/tests/**`.

Um único integrador edita `web/package.json`, lockfile, layout raiz e env. Integrar A/B sobre o client de C somente depois de seus tipos estarem estáveis.

## Definition of Done

- testes unitários/contract do client passam;
- `code-review-gate` sem achado bloqueante;
- `browser-acceptance-gate` executado no fluxo local e deployed;
- `integration-contract-guardian` confirma `CTR-API-001 v3` antes do merge;
- nenhum claim de teste ou deploy sem evidência real.

## Linear

Parent: [LUM2-4](https://linear.app/lumenhack/issue/LUM2-4/entregar-frontend-transaction-first-vercel-e-demo). `LUM2-9`–`14` foram replanejadas para o fluxo 2.0. Dependências novas principais: `TASK-TXN-API-001`→`LUM2-58`, `TASK-DEPLOY-API-001`→`LUM2-60` e `TASK-EXP-004`→`LUM2-63`.

## Recuperação 2.2 — Pessoa B

- **Plano geral:** 2.2.1; **objetivo:** `OBJ-ANDRE-002`; **base integrada:** `main@23b9061` + merge A+B `9be8853` + hardening `05c61d8`.
- **Limite:** `web/` é ownership exclusivo. Não alterar `contracts/v1/`, backend, Docker, migrations ou API em resposta a payload inesperado; abrir contract issue para Rogério.
- **Início independente:** factory única com live quando `NEXT_PUBLIC_API_BASE_URL` existe e mock somente explícito. Corrigir CTR-TDI para `/transactions/{id}/incidents`; preservar a lista homogênea de `Incident[]` em `/incidents?transaction_id=`.
- **Handoff recebido de Rogério:** OpenAPI, comando/API local e pipeline persistido estão integrados; `NO_INCIDENT/PARTIAL/RESOLVED` e erros continuam explícitos. Rotas live não fazem fallback automático a fixture.
- **Evidência local:** suite web live 35/35, build e browser desktop/mobile passam; sample → submit → log/detail → Incidents usa FastAPI real, e memória Neo4j retorna `MATCH_FOUND` sem fallback. Browser deployed, CORS real e persistência/restart Railway continuam `NOT RUN` até URLs/ambiente estarem disponíveis.
