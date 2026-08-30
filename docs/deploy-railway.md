# Deploy da API v3 no Railway

Este runbook cobre `TASK-DEPLOY-API-001` / `LUM2-60`. A API FastAPI e o lifecycle worker usam uma única réplica Railway com DuckDB no Volume. A Vercel acessa somente a API HTTPS; ela nunca recebe acesso a DuckDB, Neo4j, OpenAI ou ao Volume.

## Arquivos versionados

- `Dockerfile`: fixa Python 3.14.4, instala o `uv.lock` congelado com o extra Neo4j e o SDK OpenAI, inclui o catálogo versionado em `data/`, cria `/data` para smoke sem Volume, inicia `uvicorn main:app` em `$PORT` e define `LUMEN_DATA_DIR=/data` e `DUCKDB_PATH=/data/lumen.duckdb`.
- `railway.toml`: usa o Dockerfile, testa `GET /v1/health` durante o deploy e reinicia apenas em falha.
- `app/api/health.py`: devolve `200` somente quando DuckDB e a reconciliação inicial do worker estão prontos; Neo4j/OpenAI são opcionais.

## Configuração no Railway

1. Conecte o repositório e selecione a branch que contém a API v3.
2. Adicione um **Volume** com mount path `/data` e mantenha **uma réplica**. Um redeploy com Volume pode ter uma breve indisponibilidade; não escale horizontalmente com DuckDB.
3. Em **Variables**, configure:

   - `LUMEN_DATA_DIR=/data`
   - `DUCKDB_PATH=/data/lumen.duckdb`
   - `CORS_ALLOWED_ORIGINS=https://<dominio-vercel-production>,https://<dominio-vercel-preview>,http://localhost:3000`
   - `TRANSACTION_RESET_KEY` como segredo forte se o botão **Clear saved data** deve ser habilitado. Não use prefixo `NEXT_PUBLIC_`, não o inclua no build da Vercel e informe-o apenas no modal no momento da limpeza.
   - `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` e, quando necessário, `NEO4J_DATABASE` somente se o grafo estiver disponível. Bootstrap e runtime leem o mesmo database; o default é `neo4j`.
   - `OPENAI_API_KEY` como segredo somente se a hipótese generativa do agente deve ficar ativa. Com a chave, o agente usa `gpt-5.6-sol` com esforço de raciocínio `medium`; sem a chave, usa o template determinístico.
   - Opcionalmente, mantenha os defaults versionados: `OPENAI_MODEL=gpt-5.6-sol`, `OPENAI_REASONING_EFFORT=medium` e `OPENAI_TIMEOUT_SECONDS=20`. Não exponha nenhuma dessas variáveis ao browser e não use prefixo `NEXT_PUBLIC_`.

`CORS_ALLOWED_ORIGINS` aceita uma lista separada por vírgulas de origins HTTP(S) completos. Não use `*`, paths, secrets ou domínios fictícios: substitua os placeholders pelas URLs reais entregues pela Vercel.

Quando um grafo novo for provisionado, execute uma vez no ambiente configurado `python -m app.memory.neo4j_bootstrap`. O bootstrap é idempotente, cria as constraints e semeia o precedente determinístico; nunca coloque a senha na linha de comando ou no repositório.

## Verificação de deploy

1. Aguarde o Railway aprovar o health check em `GET /v1/health`.
2. Confirme resposta `200` com `dependencies.duckdb == "ready"` e `dependencies.worker.status == "ready"`. Se Neo4j estiver configurado, consulte um Incident de smoke e confirme `memory.retrieval_trace.fallback_used == false`; o campo `configured` do health sozinho não prova conectividade. Se OpenAI estiver ativa, gere um Incident sintético e confirme no endpoint de sugestão `model_version == "openai:gpt-5.6-sol"`; `dependencies.openai == "configured"` somente confirma a presença da chave, não uma chamada bem-sucedida.
3. Da Vercel autorizada, faça `OPTIONS /v1/transaction-batches` com `Origin`, `Content-Type` e `Idempotency-Key`; a resposta deve expor somente aquela origin.
4. Repita com uma origin aleatória: ela não pode receber `Access-Control-Allow-Origin`.
5. Envie um batch, reinicie/redeploye o serviço e confirme que o mesmo `transaction_id` e seu lifecycle continuam disponíveis pelo Volume.
6. Se o reset administrativo estiver habilitado, use uma chave de teste para chamar `POST /v1/admin/transaction-data/reset` com `X-Lumen-Admin-Key` e o corpo `{"confirmation":"DELETE_SYNTHETIC_TRANSACTION_DATA"}`. Confirme que a resposta informa as contagens e que `GET /v1/transactions` retorna uma lista vazia. Use dados sintéticos descartáveis.

## Limites conhecidos

- O health check do Railway valida a promoção do deploy; não é monitoramento contínuo.
- Sem Neo4j ou OpenAI a API usa seus fallbacks tipados, não deve falhar o boot.
- Se o Volume falhar ou houver necessidade de múltiplas réplicas, abra change control antes de migrar o adapter para Postgres.
