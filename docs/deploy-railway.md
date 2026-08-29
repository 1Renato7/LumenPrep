# Deploy no Railway (DEC-013)

Runbook manual — ninguém executou ainda, fica pra quando o Rogério decidir rodar. Contexto completo da decisão: `docs/flight-log.md` → `FL-20260829-ROGERIO-001`.

## O que já existe no repo

- `Dockerfile` (raiz) — `python:3.12-slim`, `pip install .`, sobe `uvicorn main:app` bindado em `$PORT`.
- `.dockerignore` — exclui `.venv`, testes, docs, `.git`, etc. do build context.
- `DUCKDB_PATH` já tem default `/data/lumen.duckdb` no `Dockerfile` (bate com o volume abaixo).

Validado localmente sem Docker instalado: `pip install .` numa cópia isolada só com os arquivos que o `COPY` do Dockerfile leva (`pyproject.toml`, `main.py`, `app/`, `contracts/`, `graph/`), depois rodou o `CMD` exato — `/health` e `/metrics/current` responderam 200. Não substitui um `docker build` real, mas cobre a mesma superfície de erro (dependências, imports, bind de porta).

## Passos manuais (conta Railway, ninguém além do Rogério tem acesso)

1. **Conectar o repo** — railway.com → New Project → Deploy from GitHub repo → `1Renato7/LumenPrep`. Apontar pra branch `feat/OBJ-ROGERIO-001-platform-core` (ainda não está na `main`) até o merge acontecer.
2. **Adicionar um Volume** montado em `/data` — sem isso o DuckDB é recriado do zero a cada redeploy (perde estado entre deploys).
3. **Variáveis de ambiente** do serviço:
   - `DEMO_MODE=true` — se quiser o endpoint `/demo/scenarios/{id}/inject` ativo em produção.
   - `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` — opcionais. Sem eles, `app/memory` cai no fallback in-memory (funciona, mas não persiste entre restarts).
   - `OPENAI_API_KEY` — opcional. Sem ela, `app/explanation` usa template determinístico (é o comportamento padrão hoje, funciona sem chave nenhuma).
   - `DUCKDB_PATH` — só precisa sobrescrever se o volume for montado em outro caminho que não `/data`.

Railway detecta o `Dockerfile` automaticamente, não precisa de `railway.json`/Nixpacks.

## Depois do primeiro deploy

- Checar `GET https://<url-railway>/health` — deve responder igual ao localhost.
- Streamlit (`CMP-UI-001`, André) fica fora deste runbook — ainda não existe código no repo pra ele; quando existir, decidir se entra no mesmo serviço Railway ou um separado (ver `UNKNOWN` na entrada do flight log).
