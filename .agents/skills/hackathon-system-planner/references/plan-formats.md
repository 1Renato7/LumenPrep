# Formatos dos planos

## Plano geral

Crie `docs/plans/system-plan.md` com:

1. versão, data, estado e participantes;
2. problema, usuário, resultado esperado e critério de vitória;
3. fatos, hipóteses, dúvidas e não objetivos;
4. roteiro do fluxo principal da demo;
5. arquitetura com componentes identificados;
6. decisões arquiteturais com motivação, alternativas descartadas e estado `DECIDED`, `ASSUMED` ou `OPEN`;
7. modelo de dados, ownership dos dados, estados importantes e lifecycle;
8. mapa de integração produzido pelo guardian;
9. catálogo de contratos detalhado;
10. matriz de ownership por componente, dado, arquivo compartilhado e contrato;
11. mapa de colisão de arquivos, destacando hotspots e coordenador de mudança;
12. quatro objetivos globais e suas microtarefas;
13. grafo de dependências, caminho crítico e oportunidades de trabalho independente por mock;
14. estratégia de branches, sequência de commits e ordem de merges;
15. checkpoints de integração: contratos/esqueletos, primeira fatia ponta a ponta e integração final;
16. estratégia de testes unitários, integração, contrato, revisão, smoke test e aceitação no navegador;
17. observabilidade mínima para depurar integração: logs, IDs de correlação e erros visíveis;
18. configuração compartilhada: comandos, env vars sem segredos, fixtures, seeds e serviços locais;
19. riscos, spikes, decisões pendentes, owner, prazo e plano de contingência;
20. roteiro de integração, ensaio da demo e estratégia de recuperação;
21. quality gate com resultado `PLAN READY` ou `PLAN BLOCKED`;
22. changelog do plano.

Cada contrato deve registrar: ID e versão, estado, produtor e consumidor, direção/protocolo, precondições, schema exato ou tipos, exemplo válido, resposta, estados, erros, timeout, retry, idempotência, autenticação/autorização, persistência, compatibilidade, mock e localização, teste de contrato, observabilidade, owner e checkpoint de integração. Use `não aplicável` com justificativa em vez de omitir silenciosamente.

Cada microtarefa deve ter ID, responsável, objetivo observável, entradas, saída concreta, dependências, arquivos ou área provável, critérios de aceitação, testes, evidência esperada e estimativa curta.

## Plano individual

Crie `docs/plans/people/<nome-normalizado>.md` para cada participante com:

1. versão do plano geral de origem;
2. missão e resultado global da pessoa;
3. resumo do sistema, fluxo da demo e explicação de onde sua parte se encaixa;
4. fronteiras: o que possui, o que pode editar e o que não deve alterar sem coordenação;
5. componentes, dados e arquivos sob ownership, incluindo hotspots coordenados por outra pessoa;
6. contratos fornecidos e consumidos, usando os mesmos IDs e versões do plano geral, com exemplos necessários para implementação;
7. dependências recebidas, mocks/fixtures disponíveis, localização desses recursos e entregas que desbloqueia;
8. setup local: comandos, serviços, env vars sem valores secretos, seeds e verificações iniciais;
9. microtarefas ordenadas com os mesmos IDs do plano geral, contexto, decisão esperada, critérios e evidência;
10. sequência recomendada de branches e commits, evitando misturar contratos com implementação extensa;
11. testes unitários, integração, contrato, revisão e cenários no navegador;
12. handoff de cada entrega: artefato, consumidor, como validar e sinal de disponibilidade;
13. pontos e horários relativos de sincronização com as outras três pessoas;
14. checklist `ready to start`, `ready to hand off` e `ready to merge`;
15. riscos, hipóteses, dúvidas, stop conditions e plano alternativo;
16. contexto proibido de reinterpretar localmente: decisões reservadas ao plano geral.

O plano individual deve permitir que a pessoa comece, implemente, teste e faça handoff sem depender de explicação oral para qualquer decisão já conhecida. Ele não pode redefinir contratos. Em caso de divergência, o plano geral vence e a divergência bloqueia o merge até ser sincronizada.
