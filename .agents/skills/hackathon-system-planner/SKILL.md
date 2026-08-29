---
name: hackathon-system-planner
description: Planeja ou replaneja um sistema de hackathon a partir do problema, das ideias da equipe e das restrições, produzindo um plano geral integrado e planos individuais derivados. Use em descoberta, arquitetura, divisão de responsabilidades, definição do MVP ou reorganização do trabalho; não use para uma microtarefa de implementação já bem especificada.
---

# Hackathon System Planner

Transforme entendimento difuso em um plano executável por quatro pessoas sem perder coerência entre componentes.

## Fases

1. **Descoberta:** siga [discovery-protocol.md](references/discovery-protocol.md). Capture separadamente fatos, interpretação de cada participante, restrições, ideias, dúvidas e evidências; não converta consenso aparente em requisito.
2. **Resultado e demo:** defina usuário, job, resultado mensurável, critério de vitória, roteiro da demonstração, não objetivos e menor fatia ponta a ponta que prova valor.
3. **Decisões e arquitetura:** modele componentes, dados, estados, identidades, integrações, falhas, observabilidade e operações. Registre alternativas e por que foram descartadas.
4. **Contratos:** acione `$integration-contract-guardian` em modo de planejamento para versionar fronteiras, mocks, ownership, testes e ordem de integração.
5. **Decomposição:** defina quatro objetivos globais com um owner primário cada. Quebre-os em entregáveis e microtarefas independentes, demonstráveis e ligadas a contratos.
6. **Plano geral:** gere `docs/plans/system-plan.md` com [plan-formats.md](references/plan-formats.md). Não resuma se o detalhe muda decisões de implementação ou integração.
7. **Quality gate:** aplique [planning-quality-gates.md](references/planning-quality-gates.md) e o gate do guardian. Resultado incompleto é `PLAN BLOCKED`, nunca um `PLAN READY` otimista.
8. **Planos individuais:** somente após `PLAN READY`, derive um plano autocontido para André, Altoé, Rogério e Renato. Não os escreva como listas de tarefas; inclua contexto, fronteiras, contratos, setup, passos, handoffs, testes e decisões reservadas.
9. **Forward simulation:** simule o primeiro bloco de trabalho de cada pessoa, todos os handoffs, cada checkpoint de integração e o roteiro da demo. Corrija lacunas encontradas.
10. **Publicação:** apresente resumo, riscos, decisões abertas e distribuição. Só depois de aprovação encaminhe para `$linear-microtask-planner`.

## Invariantes

- O plano geral é autoritativo; planos individuais são projeções filtradas e contextualizadas.
- Use os nomes reais informados pela equipe. Para a equipe atual, os nomes esperados são André, Altoé, Rogério e Renato, mas confirme identidades e especialidades antes de atribuir trabalho definitivo.
- Dê IDs estáveis a componentes, decisões, contratos, riscos e microtarefas.
- Inclua uma matriz de ownership que tenha exatamente um responsável primário por entrega e revisores quando necessário.
- Inclua uma sequência de integração baseada em dependências, não na ordem em que as pessoas terminarem.
- Dê a cada pessoa contexto suficiente para tomar decisões locais sem reinterpretar arquitetura, contratos ou comportamento de outro componente.
- Marque decisões como `DECIDED`, `ASSUMED` ou `OPEN`. Toda hipótese deve ter owner, prazo de validação e consequência caso esteja errada.
- Reserve decisões irreversíveis ou com grande efeito transversal para o plano geral; não as delegue implicitamente a uma microtarefa.
- Não invente arquivos, endpoints ou APIs como fatos. Quando a base de código existir, inspecione-a; quando ainda não existir, marque caminhos como propostos.
- Balanceie carga pelo caminho crítico, complexidade, risco e capacidade, não apenas pelo número de tarefas.
- Planeje tempo de integração, correção e ensaio; não distribua 100% do evento como implementação paralela.
- Se RAG ou pagamentos fizerem parte do desenho, incorpore as restrições das skills especializadas ao plano antes da divisão do trabalho.

## Atualizações

Ao replanejar, atualize primeiro o plano geral, incremente sua versão, registre motivo/impacto e marque contratos modificados. Depois sincronize planos individuais e issues afetadas preservando progresso e evidências. Nunca regenere cegamente um arquivo que contenha trabalho real sem antes comparar e manter o que continua válido.
