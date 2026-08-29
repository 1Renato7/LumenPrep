# Checklist de revisão

Use seções aplicáveis e procure comportamento, não palavras-chave.

## Correção

- critérios e fora de escopo;
- estados inicial/intermediário/final;
- null/empty/boundaries/timezones/unicode/overflow;
- erro, timeout, retry, cancelamento e partial failure;
- concorrência, ordering, stale state, duplicação e idempotência;
- resource lifecycle, cleanup e leaks;
- determinismo e comportamento após refresh/restart.

## Contratos e integração

- IDs/versões/schemas e exemplos do plano;
- compatibilidade de callers/consumers;
- imports/exports, rotas, events, env vars e migrations;
- serialização, unidades, currency, datas e enums;
- mocks/flags temporários;
- handoff prometido e observabilidade.

## Dados e segurança funcional

- autorização server-side e isolamento;
- validação na trust boundary;
- exposição de dados/segredos/logs;
- injection, unsafe rendering, redirects, URLs e uploads quando aplicáveis;
- permissões excessivas e defaults inseguros.

Não transforme revisão comum em auditoria completa; recomende `$deep-security-audit` apenas se o usuário solicitar profundidade de segurança.

## Manutenibilidade com impacto

- duplicação que causa divergência;
- abstração que esconde estado/erro;
- mudanças de API sem migração;
- dead code/feature flag que altera runtime;
- dependência nova desnecessária ou configuração não documentada.

## Testes

- cobrem comportamento e falha, não implementação acidental;
- falham antes da correção quando possível;
- não são flaky nem dependem de ordem/tempo indevido;
- fixtures representam contratos reais;
- ausência de teste relevante é achado quando permite regressão material.
