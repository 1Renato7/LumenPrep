# Handoff — Altoé: memória/explanation e prontidão de deploy

## Objetivo

Continuar a partir do runtime já integrado e tornar explícita a fronteira entre os componentes de memória/explanation e o deploy final Vercel → Railway. Este arquivo registra uma inspeção de repositório feita em 2026-08-29; não afirma que algum deploy externo foi executado.

## O que está pronto e comprovado no código

- A antiga branch `feat/OBJ-ROGERIO-001-platform-core` já é ancestral de `main`; o runbook que diz que ela ainda não foi mergeada está desatualizado.
- O `Dockerfile` instala o pacote, sobe o FastAPI com `uvicorn`, respeita `PORT` e define `DUCKDB_PATH=/data/lumen.duckdb`.
- `DEMO_MODE` protege `POST /demo/scenarios/{scenario_id}/inject`; sem a variável, a rota retorna `403 DEMO_MODE_REQUIRED`.
- `app/memory` aceita Neo4j quando configurado e mantém fallback in-memory; `app/explanation` mantém o template determinístico sem `OPENAI_API_KEY`.
- `.env.example` documenta `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` e `OPENAI_API_KEY` sem valores secretos.

## Pendências que impedem declarar o deploy 2.0 pronto

1. **Nenhum deploy Railway foi comprovado.** Rogério ainda precisa criar o serviço, montar o Volume em `/data`, configurar as variáveis reais e executar o smoke público.
2. **A topologia mudou.** O frontend final é Next.js na Vercel; Streamlit é apenas protótipo/fallback. O runbook antigo `docs/deploy-railway.md` ainda descreve a decisão anterior e deve ser considerado histórico até ser adaptado.
3. **CORS ainda não existe no runtime.** O plano 2.0 exige `CORS_ALLOWED_ORIGINS` para Vercel e localhost, mas `app/config.py` e `main.py` ainda não leem nem aplicam essa configuração.
4. **Os nomes de configuração divergem.** O plano 2.0 cita `NEO4J_USERNAME` e `LUMEN_DATA_DIR`; o runtime atual usa `NEO4J_USER` e `DUCKDB_PATH`. Escolher e padronizar os nomes antes do deploy, sem aceitar aliases silenciosos.
5. **A rota de health diverge.** O plano 2.0 prevê `/v1/health`, mas a API atual expõe `/health`.
6. **Worker/lifecycle e API v3 continuam pendentes.** O plano de deployment declara explicitamente que o Docker/Railway atual atende apenas a API anterior.
7. **Runtime inconsistente.** O `Dockerfile` usa Python 3.12, enquanto `tests/test_environment.py` exige Python 3.14.4. Alinhar imagem e teste antes do build Railway.

## Papel do Altoé

O escopo do Altoé não é provisionar Railway nem escolher volume/CORS. Seu trabalho é garantir que a memória e a explicação permaneçam corretas quando o ambiente estiver degradado:

- Validar a conexão Neo4j real com `NEO4J_URI`, `NEO4J_USER` e `NEO4J_PASSWORD` definidos no ambiente Railway.
- Confirmar que indisponibilidade, timeout ou credenciais inválidas retornam `MEMORY_UNAVAILABLE`, sem transformar o precedente em causa atual.
- Confirmar que a ausência de `OPENAI_API_KEY` preserva o ExplanationBundle determinístico e que nenhuma chave aparece em logs, respostas ou arquivos versionados.
- Entregar ao Rogério fixtures e smoke checks para `MATCH_FOUND`, `NO_PRECEDENT` e `MEMORY_UNAVAILABLE` no serviço publicado.

## Critérios de aceite para o handoff do Altoé

- Neo4j configurado: a consulta retorna o contrato `CTR-MEM-001` e evidencia o trace de retrieval.
- Neo4j indisponível: a API conserva o diagnóstico atual e devolve `memory_status=MEMORY_UNAVAILABLE`.
- Sem chave OpenAI: a explanation continua válida, determinística e grounded nos evidence IDs disponíveis.
- Nenhum caminho exige segredo no frontend Vercel ou o expõe por `/health`.
- A validação é executada contra uma URL Railway real após o deploy do Rogério; antes disso, o estado é `NOT RUN`.

## Referências

- `docs/plans/deployment-vercel-railway.md`
- `docs/plans/system-plan.md` (DEC-016, CTR-DEP-001)
- `docs/plans/people/altoe.md`
- `docs/plans/people/rogerio.md`
- `docs/deploy-railway.md` (runbook histórico a adaptar)
