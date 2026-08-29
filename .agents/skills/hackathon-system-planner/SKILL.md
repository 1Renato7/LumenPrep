---
name: hackathon-system-planner
description: Planeja ou replaneja um sistema de hackathon a partir do problema, das ideias da equipe e das restrições, produzindo um plano geral integrado e planos individuais derivados. Use em descoberta, arquitetura, divisão de responsabilidades, definição do MVP ou reorganização do trabalho; não use para uma microtarefa de implementação já bem especificada.
---

# Hackathon System Planner

Transforme entendimento difuso em um plano executável por quatro pessoas sem perder coerência entre componentes.

## Fluxo

1. Reúna problema, usuário, critério de vitória, restrições, tempo, stack, integrações, capacidades da equipe e roteiro da demo. Separe fatos, hipóteses e dúvidas.
2. Defina o menor fluxo ponta a ponta que demonstra valor. Explicite não objetivos.
3. Desenhe componentes, dados, estados e caminhos críticos. Prefira limites que reduzam edição concorrente dos mesmos arquivos.
4. Acione `$integration-contract-guardian` em modo de planejamento para criar o mapa de integração, contratos e ordem de montagem.
5. Divida o sistema em quatro objetivos globais. Não atribua pelo nome sem conhecer experiência, preferência e disponibilidade; quando isso não estiver disponível, proponha papéis provisórios e marque a hipótese.
6. Decomponha cada objetivo em entregas independentes e demonstráveis. Identifique dependências cruzadas e oportunidades de mocks.
7. Gere `docs/plans/system-plan.md` seguindo [o formato do plano geral](references/plan-formats.md).
8. Submeta o plano ao quality gate de `$integration-contract-guardian`. Se o resultado for `PLAN BLOCKED`, resolva ou registre as decisões humanas necessárias; não distribua implementação baseada em fronteiras ambíguas.
9. Somente após `PLAN READY`, gere um arquivo por participante em `docs/plans/people/`, usando o mesmo formato de referência.
10. Faça uma checagem bidirecional: todo componente, contrato, risco e critério da demo deve ter responsável; nenhuma microtarefa pode existir apenas no plano individual; tudo que aparece em um plano individual deve apontar para um ID do plano geral.
11. Faça um teste mental de execução: simule o primeiro bloco de trabalho de cada pessoa e os checkpoints de integração. Se alguém depender de informação não documentada ou de código ainda inexistente sem mock, o plano não está pronto.

## Invariantes

- O plano geral é autoritativo; planos individuais são projeções filtradas e contextualizadas.
- Use os nomes reais informados pela equipe. Para a equipe atual, os nomes esperados são André, Altoé, Rogério e Renato, mas confirme identidades e especialidades antes de atribuir trabalho definitivo.
- Dê IDs estáveis a componentes, decisões, contratos, riscos e microtarefas.
- Inclua uma matriz de ownership que tenha exatamente um responsável primário por entrega e revisores quando necessário.
- Inclua uma sequência de integração baseada em dependências, não na ordem em que as pessoas terminarem.
- Dê a cada pessoa contexto suficiente para tomar decisões locais sem reinterpretar arquitetura, contratos ou comportamento de outro componente.
- Marque decisões como `DECIDED`, `ASSUMED` ou `OPEN`. Toda hipótese deve ter owner, prazo de validação e consequência caso esteja errada.
- Reserve decisões irreversíveis ou com grande efeito transversal para o plano geral; não as delegue implicitamente a uma microtarefa.
- Se RAG ou pagamentos fizerem parte do desenho, incorpore as restrições das skills especializadas ao plano antes da divisão do trabalho.

## Atualizações

Ao replanejar, atualize primeiro o plano geral, incremente sua versão e liste mudanças. Depois regenere apenas as seções afetadas dos planos individuais, preservando progresso e evidências já registrados.
