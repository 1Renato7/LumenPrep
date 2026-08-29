# Quality gates do planejamento

## Gate 1 — problema e resultado

- usuário e necessidade estão explícitos;
- critério de vitória é observável;
- demo possui início, ação, resultado e fallback;
- a menor fatia ponta a ponta cabe nas primeiras horas e funciona antes de expansões;
- trial by fire e pelo menos um caso difícil do problema estão definidos;
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

## Gate 7 — julgamento e Flight Log

- toda decisão material `DECIDED` possui backlink `FL-*` e alternativas reais;
- nenhuma justificativa se limita a nomear framework, provider ou feature;
- fatos, testes, hipóteses e desconhecidos estão separados;
- os principais trade-offs registram ganho, perda, risco residual e gatilho de revisão;
- decisões se ligam a evidência de funcionamento, caso difícil ou plano explícito de validação;
- as cinco lentes da banca possuem evidência planejada sem multiplicar features superficialmente;
- a equipe consegue defender `por que`, `por que não`, `o que falha`, `como sabe` e `o que mudaria`.

Classifique `PLAN READY` somente quando todos os itens aplicáveis estiverem satisfeitos. Em `PLAN BLOCKED`, liste lacuna, impacto, decisão necessária, opções, owner e prazo limite.
