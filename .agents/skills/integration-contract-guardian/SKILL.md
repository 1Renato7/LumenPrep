---
name: integration-contract-guardian
description: Mapeia e protege integrações entre componentes tanto durante o planejamento quanto antes de merges, rebases e PRs. Use ao definir arquitetura paralela, contratos, ownership, ordem de integração ou ao analisar se um diff pode ser integrado; não use como revisão geral de estilo ou qualidade interna de um único componente.
---

# Integration Contract Guardian

Atue em um dos dois modos e declare o modo escolhido.

## Modo de planejamento

1. Leia o problema, o fluxo de demo, os componentes propostos e a divisão de trabalho.
2. Modele cada fronteira entre componentes: produtor, consumidor, entrada, saída, estados, erros, autenticação, persistência e timing.
3. Dê um ID estável a cada contrato e registre schema ou exemplo mínimo.
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

## Modo de integração

1. Determine branch-base, merge-base e diff exato. Preserve mudanças não relacionadas do usuário.
2. Compare o diff com os contratos e o plano geral. Liste contratos adicionados, alterados, removidos ou implementados parcialmente.
3. Verifique consumidores, compatibilidade, migrations, env vars, imports/exports, build, testes de contrato e arquivos compartilhados.
4. Reconstrua a cadeia upstream/downstream e confira se o handoff prometido no plano individual realmente existe no diff.
5. Procure conflitos semânticos mesmo quando o Git não relata conflito textual.
6. Execute checagens proporcionais ao risco e o smoke test do checkpoint. Não faça merge, rebase, push ou alteração externa sem autorização correspondente.
7. Classifique o resultado como `READY`, `READY WITH WARNINGS` ou `BLOCKED`, usando [a checklist](references/integration-checklist.md).

## Sincronização documental

Mudança de contrato começa em `docs/plans/system-plan.md`. Depois atualize os planos individuais de produtores e consumidores, e sinalize issues do Linear afetadas. Nunca faça o plano individual divergir silenciosamente do geral.
