# Regras do projeto do hackathon

## Idioma e fonte de verdade

- Escreva planos, issues e relatórios em português, preservando nomes técnicos em inglês quando forem termos do código.
- Escreva código, símbolos, schemas, nomes de arquivos técnicos e artefatos entregáveis em inglês. Planos e coordenação podem permanecer em português, salvo exigência do evento.
- Trate `docs/plans/system-plan.md` como fonte de verdade arquitetural.
- Trate `docs/plans/people/*.md` como projeções individuais do plano geral, nunca como fontes independentes.
- Registre contratos compartilhados com identificadores estáveis, por exemplo `CTR-API-001`, e repita esses identificadores nos planos das pessoas envolvidas.

## Encadeamento obrigatório das skills

- Ao tomar qualquer decisão material ou aceitar um trade-off real, use `$flight-log-recorder` e atualize `docs/flight-log.md` no momento da escolha. Isso vale durante descoberta, planejamento, implementação, revisão, testes, integração, correção e preparação da demo.
- Ao descobrir, planejar ou replanejar o sistema, use `$hackathon-system-planner` e depois `$integration-contract-guardian` em modo de planejamento. Gere ou atualize o plano geral antes dos planos individuais.
- Ao decompor trabalho ou preparar issues, use `$linear-microtask-planner`. Não crie ou altere itens no Linear sem pedido ou autorização explícita do usuário.
- Ao implementar ou modificar RAG, busca semântica, embeddings, recuperação ou grounding, use `$rag-quality-engineer`.
- Ao implementar agentes que propõem, autorizam ou executam pagamentos, use `$agent-payment-safety`.
- Nunca invoque `$deep-security-audit` automaticamente. Use essa skill somente quando o usuário pedir explicitamente auditoria, revisão ou verificação de segurança.
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

- Comece pela menor fatia ponta a ponta que funcione ao vivo; depois aprofunde casos difíceis, robustez e trial by fire. Não maximize features, integrações ou linhas de código como proxy de qualidade.
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
- Todo plano novo deve seguir integralmente os formatos e quality gates de `$hackathon-system-planner`; listas resumidas não substituem plano geral ou individual.
- Antes de publicar microtarefas, confirme usuários reais, destino, preview e carga. Crie relações do Linear em uma segunda passagem e releia o estado final.
- Em falha parcial de escrita externa, pare, inventarie o que aconteceu e peça direção; não repita cegamente.
- Use IDs estáveis para correlacionar plano, planos individuais, Linear, contratos, commits e evidências.

## Flight Log e decisões

- `docs/flight-log.md` é o histórico autoritativo do porquê das decisões. Ele não substitui `docs/plans/system-plan.md`, contratos, Linear ou código como fontes do estado atual.
- Considere material toda escolha que muda escopo, produto, arquitetura, contrato, dados, modelo/RAG, pagamento, segurança, UX, qualidade, operação, ownership, Git, integração, prazo ou demo; toda rejeição de alternativa plausível; e todo risco aceito ou decisão revertida.
- Não registre comandos mecânicos, formatação, execução de algo já decidido ou ideias ainda não aceitas.
- Registre imediatamente após a decisão e, quando possível, antes da implementação. Inclua contexto, alternativas reais, evidência/hipóteses, trade-offs negativos, consequências, validação, casos difíceis e gatilhos de revisão.
- Nomear framework, provider ou feature não constitui decisão fundamentada. Explique por que a escolha venceu neste contexto e o que o time perdeu ao escolhê-la.
- Nunca invente consenso, evidência ou teste. Use `NOT RUN`, `ASSUMPTION` e `UNKNOWN` quando necessário.
- O log é append-only. Correções recebem adendo; reversões recebem nova entrada com `supersedes`; nunca apague uma decisão para limpar a narrativa.
- Cada participante edita sua lane. Decisões transversais usam a lane `Team` e um único recorder. O índice cronológico é consolidado no code freeze.
- Toda decisão que altera estado operacional deve ser propagada ao plano geral, contratos, planos individuais e Linear afetados com os mesmos IDs.
- Antes de merge, preserve todas as entradas, valide IDs únicos e trate remoção, duplicação ou decisão de contrato não registrada como bloqueio.

## Change control

- Mudança de arquitetura, schema, contrato, owner, dependência ou ordem de integração exige atualização do plano geral primeiro.
- Classifique impacto, incremente versão quando aplicável e sincronize produtores, consumidores, mocks, testes, planos individuais e Linear.
- Preserve progresso e evidências ao replanejar; nunca regenere arquivos cegamente.
- Uma divergência conhecida entre plano, código e Linear bloqueia merge até resolução ou decisão explícita.

## Definition of Done

Uma tarefa só está concluída quando seus critérios de aceitação foram atendidos, os testes relevantes passaram, a revisão não possui achados bloqueantes, o comportamento observável foi validado localmente e os contratos/documentos afetados estão sincronizados. Se alguma validação não puder ser executada, registre exatamente o que falta e por quê.

Se a tarefa tomou ou alterou uma decisão material, a Definition of Done também exige uma entrada válida em `docs/flight-log.md` e backlinks sincronizados. Uma decisão sem alternativa real, custo aceito ou evidência honesta não está suficientemente documentada.

`$deep-security-audit` não faz parte automática da Definition of Done. Quando o usuário a solicitar, conduza a auditoria de forma defensiva e read-only por padrão; correções exigem um pedido separado ou autorização explícita para implementar os achados.

Ao criar ou atualizar uma skill, execute o validador oficial em todas as skills afetadas e confirme que referências citadas existem. Nunca altere a política explicit-only de `$deep-security-audit` sem pedido explícito.
