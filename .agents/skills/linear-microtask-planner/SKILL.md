---
name: linear-microtask-planner
description: Converte um plano geral e planos individuais em parent issues e microtarefas acionáveis no Linear, com responsáveis, dependências e critérios de aceitação. Use ao preparar, criar, reorganizar ou sincronizar trabalho no Linear; não use para planejar a arquitetura do zero.
---

# Linear Microtask Planner

Use `docs/plans/system-plan.md` como fonte de verdade e os planos individuais como contexto de execução.

## Fluxo

1. Confirme workspace, equipe/projeto, ciclo quando houver e identidade dos quatro responsáveis.
2. Valide que o plano possui contratos e dependências aprovados. Se faltar arquitetura, devolva ao `$hackathon-system-planner`.
3. Crie uma prévia usando [o schema de issues](references/issue-schema.md). Não grave no Linear antes de pedido ou autorização explícita.
4. Crie um parent issue por objetivo global e child issues para microtarefas.
5. Atribua uma única pessoa responsável, prioridade, estimativa curta, labels úteis e relações `blocked by`/`blocks`.
6. Inclua os IDs de contrato e componente relevantes na descrição.
7. Após criar, releia as issues e confira contagem, responsáveis, hierarquia e dependências. Devolva links e discrepâncias.

## Granularidade

Uma microtarefa deve produzir uma saída demonstrável em aproximadamente 20 a 60 minutos. Divida tarefas que misturem contrato, implementação e validação quando puderem ser concluídas ou desbloquear trabalho separadamente. Não fragmente em passos mecânicos sem valor verificável.

## Atualizações

Ao sincronizar um replanejamento, preserve progresso real. Atualize apenas issues afetadas, marque obsoletas de forma explícita e nunca duplique uma microtarefa porque seu título mudou.
