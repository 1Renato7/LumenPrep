# Deploy da API v3 no Railway

Este runbook cobre `TASK-DEPLOY-API-001` / `LUM2-60`. A API FastAPI e o lifecycle worker usam uma única réplica Railway com DuckDB no Volume. A Vercel acessa somente a API HTTPS; ela nunca recebe acesso a DuckDB, Neo4j, OpenAI ou ao Volume.

## Arquivos versionados

- `Dockerfile`: fixa Python 3.14.4, inicia `uvicorn main:app` em `$PORT` e define `LUMEN_DATA_DIR=/data` e `DUCKDB_PATH=/data/lumen.duckdb`.
- `railway.toml`: usa o Dockerfile, testa `GET /v1/health` durante o deploy e reinicia apenas em falha.
- `app/api/health.py`: devolve `200` somente quando DuckDB e a reconciliação inicial do worker estão prontos; Neo4j/OpenAI são opcionais.

## Configuração no Railway

1. Conecte o repositório e selecione a branch que contém a API v3.
2. Adicione um **Volume** com mount path `/data` e mantenha **uma réplica**. Um redeploy com Volume pode ter uma breve indisponibilidade; não escale horizontalmente com DuckDB.
3. Em **Variables**, configure:

   - `LUMEN_DATA_DIR=/data`
   - `DUCKDB_PATH=/data/lumen.duckdb`
   - `CORS_ALLOWED_ORIGINS=https://<dominio-vercel-production>,https://<dominio-vercel-preview>,http://localhost:3000`
   - `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` somente se o grafo estiver disponível.
   - `OPENAI_API_KEY` somente se a explicação generativa for usada; o template determinístico permanece disponível sem ela.

`CORS_ALLOWED_ORIGINS` aceita uma lista separada por vírgulas de origins HTTP(S) completos. Não use `*`, paths, secrets ou domínios fictícios: substitua os placeholders pelas URLs reais entregues pela Vercel.

## Verificação de deploy

1. Aguarde o Railway aprovar o health check em `GET /v1/health`.
2. Confirme resposta `200` com `dependencies.duckdb == "ready"` e `dependencies.worker.status == "ready"`.
3. Da Vercel autorizada, faça `OPTIONS /v1/transaction-batches` com `Origin`, `Content-Type` e `Idempotency-Key`; a resposta deve expor somente aquela origin.
4. Repita com uma origin aleatória: ela não pode receber `Access-Control-Allow-Origin`.
5. Envie um batch, reinicie/redeploye o serviço e confirme que o mesmo `transaction_id` e seu lifecycle continuam disponíveis pelo Volume.

## Limites conhecidos

- O health check do Railway valida a promoção do deploy; não é monitoramento contínuo.
- Sem Neo4j ou OpenAI a API usa seus fallbacks tipados, não deve falhar o boot.
- Se o Volume falhar ou houver necessidade de múltiplas réplicas, abra change control antes de migrar o adapter para Postgres.
