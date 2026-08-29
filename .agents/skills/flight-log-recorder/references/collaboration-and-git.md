# Colaboração e Git no Flight Log

## Objetivo

Manter um único `docs/flight-log.md`, legível pela banca e editável pelos quatro participantes, sem criar um hotspot de merge incontrolável.

## Lanes de append

O arquivo possui cinco regiões estáveis: `Team`, `André`, `Altoé`, `Rogério` e `Renato`.

- cada participante escreve somente na própria lane para decisões locais;
- decisões transversais entram em `Team` por um único recorder escolhido na conversa ou pelo integration coordinator;
- não mova entradas entre lanes durante implementação;
- cada lane possui sequência própria, evitando colisão de IDs;
- o índice cronológico no topo é mantido no fechamento, não por cada branch.

Essa estrutura reduz conflitos textuais, mas não elimina a obrigação de sincronizar a base antes de editar.

## Protocolo de escrita

1. Atualize a branch com a base conforme o protocolo Git do projeto.
2. Leia a entrada mais recente da sua lane e reserve o próximo número.
3. Procure por uma decisão equivalente com `rg 'FL-|<termo>' docs/flight-log.md` para evitar duplicata.
4. Faça append no final da lane apropriada; não reformate outras lanes.
5. Atualize fontes operacionais afetadas no mesmo commit ou em commit imediatamente ligado.
6. Prefira commit pequeno que inclua decisão e mudança relacionada. Não misture reorganização global do log.
7. Antes de integrar, confira que IDs são únicos e que nenhuma entrada desapareceu no diff.

## Decisão coletiva

Uma decisão é `Team` quando muda contrato compartilhado, MVP, arquitetura geral, risco transversal, sequência de integração, demo ou responsabilidade de outra pessoa. O recorder:

- confirma a frase da decisão e participantes;
- registra divergências relevantes sem atribuir consenso falso;
- cita o owner que tinha autoridade final;
- lista pessoas, contratos, planos e issues que precisam de propagação;
- avisa os afetados por meio do mecanismo de coordenação já escolhido pelo time.

## Conflitos de merge

Ao encontrar conflito no Flight Log:

1. preserve integralmente as duas entradas;
2. não escolha `ours` ou `theirs` para o arquivo inteiro;
3. restaure cada entrada na lane correta;
4. resolva IDs duplicados renumerando somente a entrada ainda não integrada e registre o ID final em seus backlinks;
5. mantenha a ordem de append dentro de cada lane;
6. execute a checagem de unicidade e releia o diff;
7. se duas entradas representam a mesma decisão, não apague uma silenciosamente: mantenha a canônica e adicione nota de consolidação com os IDs envolvidos.

O `$integration-contract-guardian` deve tratar remoção de entrada, ID duplicado, backlink quebrado ou decisão de contrato sem Flight Log como bloqueio de integração.

## Relação com fontes de verdade

- `docs/flight-log.md`: histórico de raciocínio e evidência.
- `docs/plans/system-plan.md`: estado arquitetural atual.
- `docs/plans/people/*.md`: projeções individuais atuais.
- Linear: estado operacional do trabalho.
- contratos, schemas e código: comportamento implementado.

Se houver divergência, não edite o passado para escondê-la. Atualize a fonte operacional, registre a decisão sucessora e sincronize os consumidores.

## Integridade e revisão

Antes de merge ou code freeze, confirme:

- nenhum ID duplicado;
- nenhuma entrada truncada ou removida sem explicação;
- timestamps, owner e status presentes;
- decisões `SUPERSEDED` possuem sucessora;
- decisões de contrato citam IDs e versões;
- links para branches/commits/testes foram preenchidos quando disponíveis;
- segredos e dados pessoais não aparecem;
- fatos e testes não foram superestimados.
