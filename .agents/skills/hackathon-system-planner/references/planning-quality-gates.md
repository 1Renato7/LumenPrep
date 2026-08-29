# Quality gates do planejamento

## Gate 1 — problema e resultado

- usuário e necessidade estão explícitos;
- critério de vitória é observável;
- demo possui início, ação, resultado e fallback;
- fatos, hipóteses, decisões e não objetivos estão separados;
- restrições do evento foram incorporadas.

## Gate 2 — arquitetura e contratos

- todos os componentes, dados e integrações têm IDs e owners;
- cada fronteira possui contrato versionado;
- erros, estados, autenticação, retry, idempotência e observabilidade estão definidos quando aplicáveis;
- toda dependência paralela tem entrega antecipada ou mock testável;
- arquivos/configurações compartilhados têm coordenador.

## Gate 3 — decomposição

- cada objetivo global tem resultado próprio e owner primário;
- toda microtarefa produz artefato ou comportamento verificável;
- entradas, saídas, fora de escopo, contratos, critérios, testes e evidência estão preenchidos;
- dependências estão no grafo, não apenas em prosa;
- carga foi comparada por esforço, risco, caminho crítico e capacidade;
- existe folga para integração, correção e ensaio.

## Gate 4 — autonomia individual

Para cada participante, simule uma nova sessão sem memória da reunião. O plano individual precisa responder por que a parte existe, o que pode alterar, como preparar o ambiente, qual contrato consome, qual mock usar, qual é a primeira tarefa, como provar cada entrega, quem recebe o handoff e quando parar para sincronizar. Se depender de explicação oral já conhecida, falha.

## Gate 5 — consistência

- IDs, versões e schemas são idênticos no geral, produtor e consumidor;
- toda tarefa individual existe no geral e todo item do geral tem owner;
- nenhuma entrega tem dois owners primários;
- dependências são simétricas entre bloqueador e bloqueado;
- ordem de integração e checkpoints são iguais para todos.

## Gate 6 — execução e integração

- o primeiro bloco de cada pessoa é executável em paralelo;
- merges foram simulados com build/teste/smoke esperados;
- há checkpoints de contratos, fatia ponta a ponta e integração final;
- existe contingência para provider, atraso e contrato quebrado;
- a demo pode ser ensaiada com dados determinísticos.

Classifique `PLAN READY` somente quando todos os itens aplicáveis estiverem satisfeitos. Em `PLAN BLOCKED`, liste lacuna, impacto, decisão necessária, opções, owner e prazo limite.
