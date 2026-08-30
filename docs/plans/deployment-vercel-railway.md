# Deployment — Vercel + Railway

> Estado integrado: API v3, lifecycle, pipeline real de Incident e frontend live existem no código; smoke Railway e acceptance Vercel continuam pendentes. Este arquivo é subordinado ao plano geral 2.2.1.

## Topologia

- `web/`: Next.js implantado na Vercel.
- `app/`: FastAPI e worker implantados no Railway.
- Railway Volume: path de DuckDB/Parquet do MVP.
- Neo4j/OpenAI: acessados somente pelo backend.
- O browser usa apenas `NEXT_PUBLIC_API_BASE_URL`, que já inclui o prefixo `/v1`.

## Variáveis de ambiente

| Runtime | Variável | Pública? | Propósito |
| --- | --- | --- | --- |
| Vercel | `NEXT_PUBLIC_API_BASE_URL` | sim | base HTTPS Railway terminando em `/v1`, sem trailing slash |
| Railway | `CORS_ALLOWED_ORIGINS` | não | lista exata de URLs Vercel/local |
| Railway | `LUMEN_DATA_DIR` | não | mount path do volume |
| Railway | `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` | não | memória |
| Railway | `OPENAI_API_KEY` | não | explanation |
| Railway | `DEMO_MODE` | não | habilita harness interno, nunca endpoints públicos de efeito |

## Regras

- Vercel production e previews autorizados são listados explicitamente; sem `*` quando houver credentials.
- Configure, por exemplo, `NEXT_PUBLIC_API_BASE_URL=https://<servico>.up.railway.app/v1`; o client acrescenta somente os paths de cada endpoint.
- O serviço Railway responde `/v1/health`; worker/store degraded aparecem separadamente.
- `202` só é emitido após persistência inicial durável.
- O volume contém dados, não secrets; nenhum domínio público é criado para banco/store.
- O harness chama a API comum, não escreve direto no DuckDB.
- Sample generation não persiste; batch submission persiste.

## Ordem de deploy

1. Provisionar serviço Railway e volume; configurar env e health.
2. Publicar API v3 e executar schema/contract smoke.
3. Validar restart e retomada de `PROCESSING`.
4. Publicar preview Vercel com base URL Railway.
5. Autorizar a preview no CORS e executar fluxo batch.
6. Promover Vercel production, atualizar allowlist e repetir smoke.

## Smoke obrigatório

- health 200 e dependências visíveis;
- sample com seed fixa retorna somente inputs válidos;
- batch com três itens retorna IDs e aparece no log;
- processing progride sem timer local e termina;
- refresh mantém registros após restart;
- filtros e detalhe funcionam;
- origem Vercel permitida e origem aleatória negada;
- API/worker down produzem estado honesto, não dados fixture sem rótulo.

## Limitação aceita

Railway Volume implica uma réplica do serviço stateful no MVP. Se replicas ou alta disponibilidade se tornarem requisito, migrar o persistence adapter para Railway Postgres em change control; não mudar `CTR-API-001` para isso.
