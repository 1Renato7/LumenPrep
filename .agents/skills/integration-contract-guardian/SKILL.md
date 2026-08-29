---
name: integration-contract-guardian
description: Mapeia e protege integrações entre componentes tanto durante o planejamento quanto antes de merges, rebases e PRs. Use ao definir arquitetura paralela, contratos, ownership, ordem de integração ou ao analisar se um diff pode ser integrado; não use como revisão geral de estilo ou qualidade interna de um único componente.
---

# Integration Contract Guardian

Atue em um dos três modos e declare o modo escolhido: `PLANNING`, `CHANGE CONTROL` ou `INTEGRATION`.

## Modo de planejamento

1. Leia o problema, o fluxo de demo, os componentes propostos e a divisão de trabalho.
2. Modele cada fronteira usando [contract-catalog.md](references/contract-catalog.md): produtor, consumidores, schema, exemplos, estados, erros, autenticação, persistência, timing e comportamento de falha.
3. Dê ID e versão estáveis a cada contrato. Defina compatibilidade, owner, mock, teste e procedimento de mudança.
4. Identifique hotspots compartilhados: configuração, lockfiles, roteamento, schema, tipos, migrations e variáveis de ambiente.
5. Defina ownership primário, consumidor, mock/stub e teste de contrato.
6. Monte o grafo de dependências, o caminho crítico e a ordem segura de integração.
7. Detecte ciclos ou dependências tardias. Quebre-os com interfaces antecipadas, adapters, mocks ou feature flags.
8. Simule a execução paralela: para cada pessoa, confirme que consegue começar sem esperar código real de outra pessoa, ou registre o mock/fixture necessário.
9. Simule a integração: percorra cada merge na ordem planejada e confirme build, contrato, migration, configuração e smoke test esperados naquele checkpoint.
10. Verifique colisões de ownership em componentes, dados e arquivos. Todo hotspot deve ter um coordenador e protocolo de mudança.
11. Aplique [a checklist](references/integration-checklist.md) e classifique o plano como `PLAN READY` ou `PLAN BLOCKED`.
12. Escreva o mapa e o parecer no plano geral e devolva ao `$hackathon-system-planner` os campos necessários para os planos individuais.

O planejamento só recebe `PLAN READY` quando cada tarefa paralela consegue começar com entradas estáveis ou mocks explícitos, existe um responsável por cada contrato e arquivo compartilhado, a ordem de integração foi ensaiada logicamente e não há decisão crítica sem owner. Não transforme desconhecimento em detalhe inventado: use `PLAN BLOCKED` com perguntas objetivas.

## Modo de change control

Use quando código ou plano precisar alterar um contrato já distribuído.

1. Identifique contrato, versão atual, motivo, produtores, consumidores, planos e issues afetados.
2. Classifique a mudança como compatível, incompatível ou comportamentalmente arriscada.
3. Proponha migração: nova versão, período de compatibilidade, adapter, feature flag, ordem de atualização e fallback.
4. Obtenha decisão do owner/coordenador quando houver escolha transversal.
5. Atualize primeiro o plano geral, depois planos individuais, mocks/testes e issues. Só então implemente.
6. Não permita que um consumidor descubra a mudança apenas no merge.

## Modo de integração

1. Siga [merge-protocol.md](references/merge-protocol.md). Determine branch-base, merge-base, commits e diff exato. Preserve mudanças não relacionadas do usuário.
2. Compare o diff com os contratos e o plano geral. Liste contratos adicionados, alterados, removidos ou implementados parcialmente.
3. Verifique consumidores, compatibilidade, migrations, env vars, imports/exports, build, testes de contrato e arquivos compartilhados.
4. Reconstrua a cadeia upstream/downstream e confira se o handoff prometido no plano individual realmente existe no diff.
5. Procure conflitos semânticos mesmo quando o Git não relata conflito textual.
6. Execute preflight, checagens proporcionais ao risco e smoke test do checkpoint. Não faça merge, rebase, push ou alteração externa sem autorização correspondente.
7. Classifique o resultado como `READY`, `READY WITH WARNINGS` ou `BLOCKED`, usando [a checklist](references/integration-checklist.md).

## Sincronização documental

Mudança de contrato começa em `docs/plans/system-plan.md`. Depois atualize planos individuais, mocks, testes e issues afetadas. Registre versão e migração. Nunca faça o plano individual divergir silenciosamente do geral nem considere documentação sincronizada sem checagem bidirecional.
