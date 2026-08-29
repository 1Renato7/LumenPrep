# Regras do projeto do hackathon

## Idioma e fonte de verdade

- Escreva planos, issues e relatórios em português, preservando nomes técnicos em inglês quando forem termos do código.
- Tudo que for do código é em inglês, esse hackathon tem entregável em inglês
- Trate `docs/plans/system-plan.md` como fonte de verdade arquitetural.
- Trate `docs/plans/people/*.md` como projeções individuais do plano geral, nunca como fontes independentes.
- Registre contratos compartilhados com identificadores estáveis, por exemplo `CTR-API-001`, e repita esses identificadores nos planos das pessoas envolvidas.

## Encadeamento obrigatório das skills

- Ao descobrir, planejar ou replanejar o sistema, use `$hackathon-system-planner` e depois `$integration-contract-guardian` em modo de planejamento. Gere ou atualize o plano geral antes dos planos individuais.
- Ao decompor trabalho ou preparar issues, use `$linear-microtask-planner`. Não crie ou altere itens no Linear sem pedido ou autorização explícita do usuário.
- Ao implementar ou modificar RAG, busca semântica, embeddings, recuperação ou grounding, use `$rag-quality-engineer`.
- Ao implementar agentes que propõem, autorizam ou executam pagamentos, use `$agent-payment-safety`.
- Antes de declarar concluída qualquer alteração de código, use `$code-review-gate` sobre o diff relevante.
- Depois da revisão e das correções, use `$browser-acceptance-gate` para toda mudança com comportamento observável na aplicação local.
- Antes de merge, rebase, abertura de PR ou integração entre branches, use `$integration-contract-guardian` em modo de integração.

## Ordem de entrega

1. Implementar somente o escopo da microtarefa.
2. Executar testes automatizados proporcionais à mudança.
3. Revisar o diff com `$code-review-gate`.
4. Corrigir achados bloqueantes e repetir os testes afetados.
5. Validar o fluxo real com `$browser-acceptance-gate` quando houver comportamento observável.
6. Validar contratos e prontidão de integração com `$integration-contract-guardian` quando a tarefa atravessar componentes ou estiver pronta para merge.
7. Atualizar plano e Linear somente com evidências reais; nunca declarar um teste executado quando ele não foi executado.

## Planejamento e integração

- Congele contratos mínimos antes de distribuir implementação paralela: tipos, endpoints, eventos, estados, erros, variáveis de ambiente, migrations e ownership de arquivos compartilhados.
- Cada componente deve declarar entradas, saídas, dependências, consumidor, mock disponível e teste de contrato.
- Cada pessoa deve receber um objetivo global e microtarefas pequenas, ordenadas e verificáveis.
- Não gere planos individuais nem issues definitivas até `$integration-contract-guardian` classificar o plano geral como `PLAN READY`.
- Se uma fronteira, contrato, owner, decisão crítica ou dependência estiver ambígua, classifique o planejamento como `PLAN BLOCKED` e liste exatamente as decisões que faltam.
- Cada plano individual deve explicar o contexto do sistema, por que a parte existe, como começa isoladamente, o que entrega aos colegas e como provar que está pronta para integração.
- Arquivos compartilhados devem ter um único coordenador de mudança. Nenhuma área crítica pode ficar com ownership simultâneo e implícito.
- Evite branches pessoais longas. Prefira branches curtas por issue, como `feat/LUM-123-resumo`, com um único responsável.
- `main` deve permanecer executável. Integre contratos e esqueletos cedo; não reserve a integração para o final do evento.
- Planeje checkpoints de integração durante o evento: contratos/esqueletos, primeira fatia ponta a ponta e integração final.
- Alterações em contrato começam no plano geral e depois são propagadas aos planos individuais e às issues impactadas.

## Definition of Done

Uma tarefa só está concluída quando seus critérios de aceitação foram atendidos, os testes relevantes passaram, a revisão não possui achados bloqueantes, o comportamento observável foi validado localmente e os contratos/documentos afetados estão sincronizados. Se alguma validação não puder ser executada, registre exatamente o que falta e por quê.
