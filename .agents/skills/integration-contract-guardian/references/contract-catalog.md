# Catálogo de contratos

## Registro obrigatório

Para cada fronteira, registre:

- ID, nome, versão, estado `PROPOSED|FROZEN|IMPLEMENTED|DEPRECATED`;
- produtor, owner, consumidores e revisores;
- propósito e comportamento observável;
- transporte/direção e precondições;
- schema/tipos exatos, campos obrigatórios/opcionais, unidades e limites;
- exemplos válido, mínimo, erro e edge case;
- resposta, estados, códigos/erros e mensagens estáveis;
- autenticação, autorização e isolamento;
- timeout, retry, backoff, idempotência e deduplicação;
- persistência, transação, ordering e consistência;
- observabilidade, correlation ID e sinal de saúde;
- compatibilidade e regra de versionamento;
- mock/stub/fixture, localização e como executar;
- teste de contrato, owner e comando;
- checkpoint de integração e fallback.

Use `não aplicável` com motivo; campo vazio é uma lacuna.

## Freeze

Um contrato só fica `FROZEN` quando produtor e consumidores conseguem implementar independentemente a partir do registro e do mock. Freeze não significa imutável: significa que mudança exige `CHANGE CONTROL` e comunicação explícita.

## Mudança compatível

Normalmente inclui campo opcional novo, novo erro documentado que consumidores já toleram ou endpoint novo. Confirme comportamento real; mudança sintaticamente compatível pode quebrar ordenação, timing, semântica ou limites.

## Mudança incompatível

Inclui remoção/renomeação, alteração de tipo/unidade, novo campo obrigatório, estado terminal diferente, autenticação nova ou semântica alterada. Exija nova versão ou migração coordenada, adapter/fallback e atualização de todos os consumidores.

## Consistência documental

O mesmo ID/versão deve aparecer no geral, planos individuais, issues, mocks e testes. Divergência bloqueia integração.
