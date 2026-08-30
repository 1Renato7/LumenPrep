# Aceitação — trials live da demo

- **Data:** 2026-08-30
- **Ambiente:** navegador local, `http://localhost:3000`, FastAPI local em `http://127.0.0.1:8000/v1`
- **Dados:** DuckDB sintético isolado em `.acceptance-data`; `DEMO_LIVE_TRIALS_ENABLED=true`, `DEMO_MODE=false`
- **Escopo:** `CTR-DEMO-002 v1`, revisão 2.10.6

| ID | Critério | Precondição | Ações exatas | Esperado | Observado | Console | Rede | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B-01 | Dois controles disponíveis | Flags de trial ativas | Abrir `/transactions/new` | Dois botões de 25 transações, um por fluxo | Cards determinístico e Graph enrichment visíveis | Sem erros | `GET /demo/live-trials` 200 | PASS |
| B-02 | Trial determinístico | B-01 | Clicar o botão do México | Batch de 25 e Incident `SUPPORTED`/82% | Batch enfileirado; card de Incident MX mostrou `PROVIDER_DEGRADATION`, 82% | Sem erros | `POST /demo/live-trials/deterministic` 202 | PASS |
| B-03 | Trial por grafo inconclusivo | B-01 | Clicar o botão do Brasil e abrir o Incident | Batch de 25, Current Cause inconclusivo, 58%, memória sem promoção causal | Card BR `INCONCLUSIVE`/58%; detalhe mostrou `Not isolated`, alternativa `ISSUER_OUTAGE · 58%`, precedente `MATCH_FOUND` e limite explícito | Sem erros | `POST /demo/live-trials/graph_enriched` 202; `GET /incidents/*` e `/suggestion` 200 | PASS |
| B-04 | Diagnóstico alternado | B-02/B-03 | Conferir métricas e evidências do detalhe Graph | Códigos `DO_NOT_HONOR` e `PROVIDER_TIMEOUT` presentes | Métrica retornou ambos os códigos; hipótese do agente continuou `HUMAN_ONLY` | Sem erros | `GET /incidents/*` 200 | PASS |

**Gate:** PASS. A execução local usou dados sintéticos. Deploy Railway/Vercel não foi operado nesta validação.

## Pós-integração

Após rebase em `origin/main@87e6b73`, a suíte combinada passou com 55 testes. O smoke no navegador repetiu o trial por grafo e confirmou `INCONCLUSIVE`/58%, ao lado do trial determinístico `SUPPORTED`/82%, sem erros no console.

Após a atualização posterior de `main` (`d35c9f6`), 62 testes Python, 50 testes web (1 skip) e o lint do cliente passaram.
