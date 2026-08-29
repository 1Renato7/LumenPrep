# Checklist de auditoria

Use somente seções aplicáveis e justifique exclusões relevantes.

## Identidade, sessão e autorização

- autenticação, recuperação, expiração, revogação e proteção contra enumeração;
- cookies/tokens, armazenamento, rotação, audience, issuer e clock skew;
- autorização server-side por recurso e ação; IDOR/BOLA; roles e least privilege;
- isolamento multi-tenant, service accounts, impersonation e rotas administrativas;
- step-up ou aprovação humana para ações críticas.

## Entrada, saída e execução

- SQL/NoSQL/command/template/LDAP injection;
- XSS armazenado, refletido e DOM; escaping contextual e CSP;
- CSRF, CORS, redirects, SSRF, path traversal, deserialização e prototype pollution;
- uploads, MIME, tamanho, nome, armazenamento, parsing e conteúdo ativo;
- URLs, webhooks, assinaturas, replay, ordem, retries e idempotência;
- validação server-side, mass assignment, over-posting e limites numéricos.

## Dados, segredos e criptografia

- classificação, minimização, retenção, deleção e exposição em logs;
- secrets em código, histórico, build, client bundle, CI e mensagens de erro;
- criptografia em trânsito e repouso, gestão de chaves e uso de primitives maduras;
- backups, exports, caches, analytics e dados de teste;
- acesso direto ao banco, policies/RLS e migrations.

## APIs, frontend e infraestrutura

- rate limits, quotas, timeouts, tamanho de payload e abuso de custo;
- headers, TLS, cache, clickjacking, content types e source maps;
- endpoints esquecidos, debug, health checks, metadata e documentação pública;
- containers, usuário root, capabilities, imagens, portas e filesystem;
- IaC, security groups, storage público, IAM, ambientes e defaults inseguros;
- CI/CD, proteção de branch, permissões de workflow, artifacts e provenance.

## Dependências e supply chain

- lockfile, proveniência, versões, vulnerabilidades conhecidas e dependências abandonadas;
- scripts de instalação, typosquatting, registries, integrity e pinning;
- ferramentas de build, ações de CI e imagens por digest quando necessário;
- SBOM ou inventário proporcional ao projeto e processo de atualização.

## Agentes, LLM e RAG

- prompt injection direta e indireta; conteúdo recuperado tratado como não confiável;
- separação entre instruções, dados e autoridade;
- allowlist de ferramentas, schema estrito, least privilege e aprovação humana;
- exfiltração por tool calls, URLs, logs, citações ou contexto;
- isolamento de memória, conversas, tenants, embeddings e vector store;
- poisoning, fontes, grounding, permissões por documento e fallback seguro;
- limites de loops, tokens, custo, retries e ações autônomas.

## Pagamentos e lógica de negócio

- valores inteiros, moeda, arredondamento, limites e beneficiário;
- autorização determinística, idempotência, ledger, reconciliação e estados terminais;
- concorrência, double-spend, replay, webhook fora de ordem e falha parcial;
- descontos, convites, créditos, quotas e bypass de sequência;
- sandbox/produção e ausência de dados financeiros em prompts ou logs.

## Detecção e resposta

- logs úteis sem segredos, correlation IDs e trilha de auditoria;
- alertas para ações críticas, falhas de autorização e abuso;
- mensagens de erro seguras e observabilidade de dependências;
- rotação/revogação, rollback, feature flag e resposta a incidente.
