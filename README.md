# LumenPrep

Este repositório contém o sistema de trabalho do time para planejar, dividir, implementar, revisar e integrar o projeto do hackathon com Codex.

## Comece aqui

1. Abra o repositório como projeto no Codex.
2. Inicie uma nova tarefa para garantir que [AGENTS.md](AGENTS.md) seja carregado.
3. Durante a descoberta, forneça o enunciado, as ideias, as restrições, a stack e as habilidades dos quatro participantes.
4. Peça o plano geral. O Codex usará as skills de planejamento e integração antes de gerar os planos individuais.
5. Aprove o plano antes de criar as microtarefas no Linear.

As skills do projeto ficam em [`.agents/skills`](.agents/skills). Consulte [o guia completo das skills](docs/SKILLS.md) para saber quando cada uma é executada, o que recebe e o que entrega.

As decisões do time ficam no [Flight Log](docs/flight-log.md). Ele é atualizado automaticamente pelo Codex sempre que uma escolha material ou trade-off real acontece e permanece disponível para colaboração e defesa perante a banca.

As skills usam progressive disclosure: cada `SKILL.md` contém o fluxo central e carrega referências profundas somente quando necessárias. Isso mantém o contexto utilizável sem reduzir a precisão dos procedimentos.

## Fluxo principal

```text
Descoberta
  → registrar decisões e trade-offs no Flight Log durante todo o fluxo
  → plano geral
  → quality gate de integração
  → quatro planos individuais
  → microtarefas no Linear
  → implementação e testes
  → revisão de código
  → validação no navegador
  → validação de integração
  → merge
```

O plano geral em `docs/plans/system-plan.md` será a fonte de verdade arquitetural quando for gerado. Os planos em `docs/plans/people/` serão projeções individuais e não poderão redefinir contratos.

Um plano só é distribuído após `PLAN READY`. Os quality gates verificam problema, arquitetura, contratos, decomposição, autonomia individual, consistência entre os cinco planos, simulação de execução paralela, sequência de merges e ensaio da demo.

O planejamento prioriza uma fatia mínima ponta a ponta executável nas primeiras horas e usa o tempo restante para profundidade, casos difíceis e trial by fire. O número de features, integrações ou linhas de código não substitui evidência de funcionamento e julgamento técnico.

## Regra de segurança

A auditoria profunda de segurança nunca é automática. Para executá-la, peça explicitamente:

```text
Use $deep-security-audit para auditar profundamente a segurança do sistema.
```

Por padrão, a auditoria diagnostica e documenta riscos sem corrigir código ou alterar infraestrutura.
