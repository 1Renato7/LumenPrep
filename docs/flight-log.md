# Flight Log — Lumen

Registro colaborativo e append-only das decisões materiais do hackathon. A banca deve conseguir entender o que decidimos, quais alternativas rejeitamos, quais trade-offs aceitamos e como validamos o resultado.

> O Flight Log preserva o **porquê histórico**. O estado arquitetural atual vive em `docs/plans/system-plan.md`; contratos e código continuam sendo as fontes executáveis. Nunca apague uma decisão antiga para fazer o histórico parecer linear.

## Como colaborar

- Registre a decisão no momento em que ela acontece usando `$flight-log-recorder`.
- Use IDs `FL-YYYYMMDD-LANE-NNN`; cada lane possui sua própria sequência.
- André, Altoé, Rogério e Renato fazem append apenas em suas lanes. Decisões transversais entram em `Team` por um único recorder.
- Não renumere, reordene ou apague entradas. Reversões geram nova entrada com `supersedes`.
- Não atualize o índice cronológico a cada branch; ele é consolidado no fechamento para reduzir conflitos.
- Uma entrada não é boa por ser longa: precisa conter alternativa real, custo aceito e evidência honesta.

O schema completo está em [entry-schema.md](../.agents/skills/flight-log-recorder/references/entry-schema.md) e o protocolo Git em [collaboration-and-git.md](../.agents/skills/flight-log-recorder/references/collaboration-and-git.md).

## Síntese executiva

_Preencher no modo `FINALIZE` sem inventar decisões retroativas._

## Índice cronológico

_Consolidar no modo `FINALIZE`; as entradas originais permanecem nas lanes._

| Timestamp | ID | Decisão | Owner | Status | Evidência principal |
| --- | --- | --- | --- | --- | --- |
| 2026-08-29T11:56:33-03:00 | FL-20260829-TEAM-001 | Adotar um Flight Log Markdown, append-only e dividido por lanes | André | VALIDATED | Três skills validadas e checagens Git aprovadas |
| 2026-08-29T12:08:01-03:00 | FL-20260829-TEAM-002 | Separar avaliação viva do histórico de decisões | André | VALIDATED | `avaliacao.md` aponta para o Flight Log canônico |
| 2026-08-29T15:42:08-03:00 | FL-20260829-TEAM-009 | Publicar plano no Linear correto com quatro owners | André | VALIDATED | 54 issues e 50 relações auditadas sem divergência |
| 2026-08-29T16:28:49-03:00 | FL-20260829-TEAM-010 | Priorizar descoberta causal e usar memória para acelerar solução | Team | ACCEPTED | Plano 1.1.0 e fixtures de caso novo sem precedente |
| 2026-08-29T16:40:08-03:00 | FL-20260829-TEAM-011 | Consultar memória mesmo quando a causa atual for inconclusiva | Team | ACCEPTED | Plano 1.2.0 e fixtures `INCONCLUSIVE + MATCH` |
| 2026-08-29T16:48:27-03:00 | FL-20260829-TEAM-012 | Tipar o estado da memória no contrato compartilhado | Team | ACCEPTED | CTR-MEM-001 v1.1 e fixture `MEMORY_UNAVAILABLE` |

## Decisões do time

<!-- TEAM: faça append de novas entradas imediatamente antes da próxima seção. -->

### FL-20260830-TEAM-033 — Sincronizar a main sem perder o auditor local

- **Timestamp:** 2026-08-30T07:20:00-03:00
- **Status:** VALIDATED
- **Decision owner:** usuário solicitante
- **Participantes:** usuário solicitante; Codex como executor e recorder
- **Categoria:** Git/integration | quality
- **Escopo:** `main`, `origin/main@01b6d51`, `CMP-QA-001`, `CTR-TXL-001`, `CTR-AGT-001`–`003`
- **Links:** `FL-20260830-TEAM-032`, `docs/plans/system-plan.md`
- **Supersedes / superseded by:** não aplicável.

#### Contexto e pergunta

O solicitante pediu que o checkout permanecesse atualizado com a `main` remota. A cópia local estava quatro commits atrás e continha o auditor local ainda não commitado; dois arquivos de decisão compartilhados tinham alterações dos dois lados.

#### Decisão

Preservar todas as mudanças locais num stash recuperável, avançar a `main` por fast-forward até `01b6d51` e reaplicar o trabalho local. No conflito do plano, preservar tanto os contratos do agente proativo remoto quanto `CMP-QA-001`. Adaptar o auditor à correção remota: controles internos de cenário são lidos apenas da entrada persistida interna para reconstituir uma falha, enquanto o `CTR-TXL-001` público permanece sem esse campo.

#### Alternativas consideradas

| Alternativa | Benefício | Risco | Decisão |
| --- | --- | --- | --- |
| `pull` direto com working tree suja | mais curto | conflito ou perda de trabalho local | rejeitada |
| descartar o auditor antes de atualizar | árvore limpa | perde a evidência/progresso do solicitante | rejeitada |
| stash recuperável + fast-forward + reconciliação | preserva os dois lados e mantém recuperação | exige revisar conflito semântico | escolhida |

#### Evidência e validação

- **FACT:** `origin/main` avançou de `144299d` para `01b6d51` em quatro commits e introduziu `CTR-AGT-001`–`003`.
- **TEST:** após a reconciliação, 28 testes relevantes de auditoria, fluxo, schema, memória e trace passaram; `compileall` e ambos os `git diff --check` passaram.
- **FACT:** a correção remota normaliza `scenario_effects: null` no seed e o oculta no record público, fazendo a equivalência de transporte voltar a passar.
- **LIMIT:** o stash `codex-before-origin-main-sync-20260830` foi mantido como cópia de segurança; não há commit local nem push deste trabalho.

#### Consequências e gatilho de revisão

O próximo run do avaliador passa a inspecionar a `main` atualizada e não deve mais reprovar a antiga diferença de serialização. Qualquer próxima atualização remota, conflito em contrato público ou falha dos oráculos exige repetir a mesma checagem antes de integrar.

### FL-20260830-TEAM-027 — Adotar um agente de QA por cenários para evidência contínua

- **Timestamp:** 2026-08-30T06:00:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** usuário solicitante; Codex como executor e recorder
- **Categoria:** quality | operations | demo
- **Escopo:** `.agents/skills/qa-scenario-agent`, `docs/SKILLS.md`, validação de backend, contratos e web
- **Links:** `TASK-QA-001`, `CTR-TXN-001 v1`, `CTR-TDI-001 v1`, `CTR-MEM-001 v1.1`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O projeto já possui testes unitários, de contrato e de interface, mas faltava um operador reutilizável que escolha e execute casos variados com evidência comum antes da demo e das integrações. A pergunta foi como ampliar a cobertura de fluxo sem dar ao agente autoridade sobre produção ou mudanças no produto.

#### Decisão

Criar a skill automática `qa-scenario-agent`, orientada por risco. Ela deriva uma matriz mínima de fluxos, limites, vazios, falhas, indisponibilidade e regressões a partir dos contratos e do comportamento real; executa somente testes locais com dados sintéticos e reporta `PASS`, `FAIL` ou `NOT RUN` com reprodução.

#### Critérios e por que agora

O sistema precisa provar mais que o caminho feliz, especialmente nos estados explícitos de incerteza e na transição transação → Incident → detalhe. A skill reutiliza os gates existentes em vez de criar um framework paralelo.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Rodar apenas a suite existente manualmente | Sem artefato novo | Casos de falha e evidências variam entre execuções | FACT: há suites Python e web separadas | Não cria uma prática repetível por fluxo |
| Criar um runner autônomo com acesso externo | Maior automação potencial | Poderia tocar dados/serviços reais e ocultar decisões de teste | ASSUMPTION: não há sandbox externo dedicado | Autoridade e custo são desnecessários agora |
| Skill local orientada por cenários | Reutiliza contratos, gates e dados sintéticos | Ainda requer julgamento e ambiente local disponível | FACT: o repositório possui fixtures, testes e browser gate | Escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `tests/` e `web/tests/` já cobrem componentes distintos; `browser-acceptance-gate` exige cenário e evidência para superfície web.
- **TEST:** validação estrutural da nova skill será executada antes da entrega; cenários do produto não foram executados por esta criação.
- **ASSUMPTION:** o agente reduzirá omissões de casos críticos quando acionado antes de demo ou integração; confirmar no primeiro uso.
- **UNKNOWN:** quais fluxos serão priorizados no primeiro ciclo de QA.

#### Trade-offs aceitos

- **Ganhamos:** cobertura guiada por risco, limites explícitos e relatórios comparáveis.
- **Abrimos mão de:** automação autônoma contra ambientes externos.
- **Dívida/limitação:** a qualidade do resultado depende de contratos, fixtures e serviços locais disponíveis.
- **Risco residual:** um cenário não modelado pode escapar; `NOT RUN` não pode ser interpretado como aprovação.

#### Consequências e propagação

- **Produto/demo:** permite ensaiar falhas e estados de incerteza além do caminho feliz.
- **Arquitetura/contratos:** não altera contratos públicos; consome os contratos e fixtures existentes.
- **Pessoas/branches:** qualquer integrante pode invocar `$qa-scenario-agent` antes do handoff.
- **Plano/Linear:** `TASK-QA-001` ganha procedimento reutilizável; Linear não foi alterado.
- **Testes/observabilidade:** cada execução deve registrar comando, cenário e resultado honesto.

#### Validação e trial by fire

- **Hipótese verificável:** para um fluxo escolhido, o agente produz e executa casos de sucesso, falha e indisponibilidade sem usar dados reais.
- **Caminho feliz:** batch local → processamento → Incident/detalhe com evidência dos testes e, se aplicável, navegador.
- **Caso difícil/adverso:** API indisponível, repetição idempotente ou estado inconclusivo permanece visível e corretamente classificado.
- **Resultado observado:** PENDING — skill criada; validação estrutural pendente nesta entrada.
- **Fallback:** executar os testes focados e o browser gate manualmente, registrando os mesmos campos de evidência.

#### Gatilhos de revisão

Primeiro uso que revele casos sistematicamente ausentes, dependência de infraestrutura externa ou necessidade de mutar o sistema sob teste exige ajuste da skill e novo adendo.

#### Adendos

- **2026-08-30T06:00:00-03:00:** `git diff --check` passou. A revisão manual confirmou frontmatter, nome `qa-scenario-agent`, instruções sem placeholders e metadata com invocação automática. O validador oficial `quick_validate.py` ficou `NOT RUN`: este host não possui `python`, launcher `py` ou o runtime `.python-runtime` instalado. Nenhum cenário de produto foi executado, pois esta alteração cria o procedimento de QA, não uma mudança funcional.

### FL-20260830-TEAM-028 — Elevar o agente de QA a avaliador de conformidade do case

- **Timestamp:** 2026-08-30T06:05:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** usuário solicitante; Codex como executor e recorder
- **Categoria:** quality | product | demo
- **Escopo:** `.agents/skills/qa-scenario-agent`, `avaliacao.md`, `docs/plans/system-plan.md`, contratos e trial by fire
- **Links:** `FL-20260830-TEAM-027`, `TASK-QA-001`
- **Supersedes / superseded by:** amplia `FL-20260830-TEAM-027`; não a substitui.

#### Contexto e pergunta

O agente criado inicialmente cobria cenários técnicos, mas o solicitante esclareceu que ele deve avaliar se o projeto corresponde ao fluxo e às exigências do case, como faria um avaliador independente.

#### Decisão

O `qa-scenario-agent` passa a produzir um parecer de conformidade baseado no enunciado, em `avaliacao.md`, no plano e nos contratos: cada requisito recebe evidência e status; a demo recebe veredito `PRONTA`, `PRONTA COM LIMITAÇÕES` ou `NÃO PRONTA`.

#### Critérios e por que agora

Testes de componentes não demonstram por si só aderência ao problema, casos feios ou capacidade de sobreviver ao trial by fire. O novo escopo liga teste de fluxo ao que a banca realmente pede.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Decisão |
| --- | --- | --- | --- | --- |
| Manter apenas executor de testes | Simples e objetivo | Não responde se o case foi atendido | FACT: solicitação exige avaliação do projeto | Rejeitada |
| Atribuir nota automática ao projeto | Comparação rápida | Criaria precisão falsa onde a banca usa ranking qualitativo | FACT: `avaliacao.md` declara que não há pontuação oficial | Rejeitada |
| Parecer por requisito com evidências | Expõe lacunas e limitações honestamente | Requer leitura do case e julgamento explícito | FACT: plano, contratos e avaliação existem no repo | Escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `avaliacao.md` descreve as lentes, entregáveis e trial by fire; o plano descreve o fluxo transaction-first e os estados esperados.
- **TEST:** `git diff --check` será repetido após atualizar a skill; avaliação do produto permanece `NOT RUN` até a primeira invocação.
- **UNKNOWN:** o enunciado integral fornecido pela organização não foi localizado como artefato separado; o agente deve declará-lo se não for entregue no pedido.

#### Trade-offs aceitos

- **Ganhamos:** avaliação alinhada à banca, sem esconder cobertura ausente.
- **Abrimos mão de:** uma nota simples ou promessa automática de aprovação.
- **Risco residual:** documentos podem estar desatualizados em relação ao case; isso deve aparecer como limitação, nunca ser inferido.

#### Consequências e propagação

- **Produto/demo:** o primeiro uso gera uma lista priorizada de lacunas demonstráveis antes do pitch.
- **Arquitetura/contratos:** não muda contratos; verifica se sua implementação satisfaz as invariantes.
- **Plano/Linear:** nenhuma alteração no Linear; `avaliacao.md` continua fonte de avaliação interna.
- **Testes/observabilidade:** exige fluxo completo, caso adverso e evidência de navegador quando aplicável.

#### Validação e trial by fire

- **Hipótese verificável:** com um enunciado e ambiente local, o agente consegue distinguir requisito comprovado, parcial e não comprovado.
- **Caminho feliz:** executa batch → lifecycle → diagnóstico → detalhe e relaciona a prova ao requisito correspondente.
- **Caso difícil/adverso:** serviço indisponível ou entrada não ensaiada produz limitação explícita, não aprovação fictícia.
- **Resultado observado:** PENDING — comportamento será exercitado na primeira avaliação do projeto.
- **Fallback:** usar a matriz manual de `avaliacao.md` e registrar `NOT RUN` para cada item sem evidência.

#### Gatilhos de revisão

Novo enunciado oficial, mudança material de produto ou resultado que revele requisito não rastreável exige atualizar a matriz da skill.

### FL-20260830-TEAM-029 — Executar a avaliação do case com OpenAI apenas sobre probes locais permitidas

- **Timestamp:** 2026-08-30T06:15:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** usuário solicitante; Codex como executor e recorder
- **Categoria:** AI/RAG | quality | operations | demo
- **Escopo:** `CMP-QA-001`, `app/evaluation/`, `scripts/run_case_evaluator.py`, `OPENAI_API_KEY`
- **Links:** `FL-20260830-TEAM-028`, `CTR-API-001 v3`, `TASK-QA-001`
- **Supersedes / superseded by:** implementa a intenção de `FL-20260830-TEAM-028` sem mudar contratos públicos.

#### Contexto e pergunta

O solicitante confirmou que quer um agente executável, com `OPENAI_API_KEY`, que realize operações e gere feedback sobre a conformidade do projeto com o case.

#### Decisão

Criar um executor local que deixa o modelo selecionar apenas probes nomeadas para health, catálogo, samples, batch, idempotência e input inválido. O executor chama somente `http://localhost`/`127.0.0.1` com dados sintéticos; a Responses API recebe a evidência e redige o parecer.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência | Decisão |
| --- | --- | --- | --- | --- |
| Modelo com URL e comandos livres | Maior flexibilidade | Pode executar operações fora do escopo | ASSUMPTION: não há sandbox dedicada | Rejeitada |
| Runner determinístico sem LLM | Reproduzibilidade máxima | Não entrega o feedback conversacional pedido | FACT: solicitante pediu `OPENAI_API_KEY` | Rejeitada |
| Modelo + probes allowlisted locais | Operações reais e feedback contextual | Cobertura inicial é limitada ao catálogo | FACT: API possui fluxo e testes locais | Escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** a Responses API aceita instruções, texto/JSON e saída estruturada; esta implementação não concede ferramentas remotas ao modelo.
- **TEST:** teste unitário e chamada real permanecem pendentes porque este host não tem runtime Python nem uma chave configurada.
- **UNKNOWN:** custo e qualidade de `OPENAI_MODEL`; validar no primeiro run.

#### Trade-offs aceitos

- **Ganhamos:** agente conversacional com operações observáveis e superfície de ação limitada.
- **Abrimos mão de:** exploração livre e avaliação de ambientes deployados.
- **Risco residual:** a interpretação do modelo pode falhar; probes e evidências permanecem auditáveis.

#### Consequências e propagação

- **Produto/demo:** um comando local produz feedback sobre prontidão e lacunas.
- **Arquitetura/contratos:** `CMP-QA-001` é interno; não cria endpoint ou mudança em `CTR-API-001`.
- **Operação:** requer `OPENAI_API_KEY`, exclusivamente no ambiente.
- **Testes:** cada probe expõe status/evidência; queda da OpenAI falha honestamente.

#### Validação e trial by fire

- **Hipótese verificável:** com API local e chave, o agente executa apenas probes permitidas e retorna um veredito baseado nos resultados.
- **Caminho feliz:** seleção do modelo → probes locais → evidências → parecer.
- **Caso difícil/adverso:** URL não local, ausência de chave ou queda da OpenAI falham sem tocar serviço externo nem alegar aprovação.
- **Resultado observado:** NOT RUN — runtime Python e chave não estão disponíveis neste host.
- **Fallback:** executar a suite determinística e usar a matriz de `avaliacao.md` manualmente.

#### Gatilhos de revisão

Novo probe, ambiente remoto ou operação sobre dados reais, pagamento ou contrato exige nova decisão e avaliação de segurança.

### FL-20260830-TEAM-030 — Executar o avaliador em memória, sem servidor manual ou banco persistente

- **Timestamp:** 2026-08-30T06:25:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** usuário solicitante; Codex como executor e recorder
- **Categoria:** quality | operations | demo
- **Escopo:** `CMP-QA-001`, `scripts/run_case_evaluator.py`
- **Links:** `FL-20260830-TEAM-029`
- **Supersedes / superseded by:** restringe o runtime local de `FL-20260830-TEAM-029`; não altera o modelo de probes.

#### Contexto e pergunta

O fluxo inicial exigia iniciar um servidor separado e configurar vários passos manuais, contrariando a meta de um avaliador simples e repetível.

#### Decisão

O comando do avaliador cria a aplicação FastAPI com DuckDB em memória e a opera pelo cliente de teste interno. Assim, uma execução usa um único comando, não modifica a base persistente e não depende de uma segunda janela de terminal.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Decisão |
| --- | --- | --- | --- |
| Exigir API local já iniciada | Testa topologia HTTP externa | Aumenta setup, permite estado residual e falhas operacionais não relacionadas | Rejeitada para o primeiro avaliador |
| Operar a app em memória | Reproduzível, isolada e um comando | Não substitui smoke de deploy/CORS | Escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** a suite existente já utiliza `FastAPI TestClient` e DuckDB em memória para isolar testes.
- **TEST:** execução pendente até o usuário inserir a chave no `.env`.
- **Risco residual:** deploy e browser continuam verificações separadas, não alegadas por este agente.

#### Validação e trial by fire

- **Hipótese verificável:** o comando único executa probes e preserva o banco do usuário.
- **Caminho feliz:** `.venv` + `.env` → script → probes → parecer.
- **Caso difícil/adverso:** chave ausente falha antes de qualquer probe; falha de modelo não cria dados persistentes.
- **Resultado observado:** NOT RUN.
- **Fallback:** rodar testes determinísticos diretamente na mesma instância em memória.

#### Adendos

- **2026-08-30T06:25:00-03:00:** PASS — `tests/test_case_evaluator.py` e o teste de configuração de `DEMO_MODE` passaram (2 testes). O script agora prepara o path da raiz e informa falha da OpenAI sem traceback. A chamada real à API OpenAI foi `NOT RUN` neste ambiente isolado porque sockets externos são bloqueados (`PermissionError`); nenhum dado persistente foi criado.

### FL-20260830-TEAM-031 — Fazer testes-oráculo determinísticos decidirem se há grounding, não o texto do modelo

- **Timestamp:** 2026-08-30T06:35:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** usuário solicitante; Codex como executor e recorder
- **Categoria:** AI/RAG | quality | demo
- **Escopo:** `CMP-QA-001`, testes de grounding, memória, RCA e trace transacional
- **Links:** `FL-20260830-TEAM-029`, `CTR-INC-001 v1`, `CTR-MEM-001 v1.1`, `CTR-LLM-001 v1`
- **Supersedes / superseded by:** restringe o papel explicativo do modelo em `FL-20260830-TEAM-029`.

#### Contexto e pergunta

O solicitante identificou corretamente que um resumo persuasivo da IA não prova que o Lumen deixou de inventar causa, evidência, associação ou certeza. A pergunta passou a ser se o sistema resiste a premissas falsas e só publica conclusões rastreáveis.

#### Decisão

Executar sempre uma suite fixa de testes-oráculo antes do parecer da OpenAI. Ela reprova causa com baixa amostra, empate causal promovido, memória/explicação sem Incident, precedente histórico promovido, ID de evidência desconhecido e vazamento entre transações. A OpenAI recebe o resultado, mas não pode mudar os comandos, os oráculos ou aprovar uma suite que falhou.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Decisão |
| --- | --- | --- | --- |
| Pedir ao modelo que avalie sua própria verdade | Feedback fluente | Modelo pode inferir ou afirmar sem prova | Rejeitada |
| Confiar apenas em smoke de endpoint | Execução rápida | Não testa negação, proveniência ou abstention | Rejeitada |
| Oráculos determinísticos + modelo explicativo | Resultado reproduzível com comunicação clara | Cobre apenas hipóteses explicitamente modeladas | Escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** a base já possui testes para `INCONCLUSIVE`, evidência inválida, ausência de Incident, vazamento cross-transaction e promoção indevida.
- **TEST:** a suite-oráculo será executada no próximo run do avaliador; nenhum veredito anterior deve ser interpretado como prova desses casos.
- **Risco residual:** o teste não prova corretude para cenário não modelado; novos achados devem virar novo oráculo.

#### Validação e trial by fire

- **Hipótese verificável:** uma tentativa de promover hipótese sem evidência resulta em falha de teste ou estado explícito de abstention.
- **Caminho feliz:** testes-oráculo passam, probes do fluxo passam e o parecer cita ambos.
- **Caso difícil/adverso:** entrada/associação falsa, precedente ou evidência de outra transação não produz causa nem detalhe autorizado.
- **Resultado observado:** PENDING.
- **Fallback:** `NÃO PRONTA` quando a suite não pode ser executada; nunca substituir por inferência da OpenAI.

#### Adendos

- **2026-08-30T06:35:00-03:00:** FAIL — execução da suite-oráculo encontrou 19 testes aprovados e 1 falha em `test_manual_submission_and_background_input_have_transport_independent_event_shape`. Para os mesmos fatos, `adapt_transaction` publicou latências diferentes (`494` e `696` ms) antes/depois de `TransactionInput.model_dump(mode="json")`. O campo opcional ausente passa a existir como `scenario_effects: null`, altera o material do seed e quebra a igualdade esperada de outcome/evento. Até isso ser corrigido, o avaliador deve tratar a equivalência semântica do fluxo como não comprovada e não retornar `PRONTA`.

### FL-20260830-TEAM-032 — Auditar a proveniência de cada erro, não a plausibilidade do texto

- **Timestamp:** 2026-08-30T06:50:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** usuário solicitante; Codex como executor e recorder
- **Categoria:** quality | simulation | observability
- **Escopo:** `CMP-QA-001`, `app/evaluation/provenance.py`, worker, raw/canonical events
- **Links:** `FL-20260830-TEAM-031`, `CTR-TXL-001 v1`, `CTR-EVT-001 v1`

#### Contexto e pergunta

O risco levantado não é somente uma causa agregada inventada: uma operação individual pode exibir um erro que parece coerente, mas não corresponde ao que realmente ocorreu no provider/pipeline. A pergunta é se cada erro exibido possui uma cadeia verificável, e não se um modelo consegue descrevê-lo bem.

#### Decisão

Adicionar um auditor determinístico obrigatório ao avaliador. Ele cria uma falha sintética controlada e compara o registro público com a reconstrução do `adapt_transaction`, o `raw_event` e o `canonical_event` persistidos. Divergência em status, outcome/código, categoria, motivo, confiança, evidência ou evento reprova a execução. Um segundo probe compara os mesmos fatos antes/depois da serialização do contrato público.

#### Alternativas consideradas

| Alternativa | Benefício | Risco | Decisão |
| --- | --- | --- | --- |
| LLM julgar se o motivo parece verdadeiro | texto natural | confunde plausibilidade com prova | rejeitada |
| Comparar apenas HTTP/status | simples | não prova origem da explicação | rejeitada |
| Reconstruir + comparar eventos duráveis | evidência por campo e reprodutível | no modo sintético a fonte é o adapter | escolhida |

#### Evidência, hipótese e limite

- **FACT:** o worker grava o outcome/classificação, persiste o evento bruto e o evento canônico para cada transação terminal.
- **TEST:** testes unitários aprovam o caminho coerente e reprovam motivo forjado e evento bruto ausente; o probe de integração reconstitui uma falha `TIMEOUT` persistida.
- **LIMIT:** o provider atual é um simulador. Em produção, a resposta bruta e autenticada do provider deve se tornar fonte adicional/autoritativa; a IA nunca pode preenchê-la.

#### Validação e trial by fire

- **Caminho feliz:** `status`, código, evidência e ambos os eventos correspondem exatamente ao adapter.
- **Caso adverso:** trocar a razão por um texto convincente ou remover o evento bruto causa reprovação.
- **Resultado observado:** PASS para reconstrução da falha; FAIL para equivalência de transporte, apontando o campo opcional nulo que muda o seed.
- **Fallback:** `NÃO PRONTA`; não substituir uma origem ausente por explicação do modelo.

#### Adendos

- **2026-08-30T06:55:00-03:00:** o teste amplo também revelou que `scenario_effects` é aceito em `TransactionInput`, mas persiste no registro `CTR-TXL-001`, cujo schema o proíbe. O teste terminal de schema foi adicionado à suite-oráculo. Isso é um segundo bloqueio independente: uma operação pode ter trilha de proveniência e ainda assim expor uma resposta fora do contrato.
- **2026-08-30T07:00:00-03:00:** o veredito passou a ser montado pelo executor determinístico, não pelo texto do modelo. Se qualquer probe falha, a saída começa obrigatoriamente com `Veredito: NÃO PRONTA`; a OpenAI recebe somente a tarefa de narrar evidência, lacunas e próximo teste. Isso elimina a possibilidade de um resumo persuasivo contradizer uma reprovação técnica.
- **2026-08-30T07:05:00-03:00:** PASS — `tests/test_provenance_auditor.py` e `tests/test_case_evaluator.py` aprovaram 10 casos, incluindo razão forjada, evento ausente, campo não auditado, timeout reconstituído e veredito forçado. A suite-oráculo retornou 15 aprovados e 2 falhas reais (equivalência de serialização e schema terminal). `compileall` e `git diff --check` passaram. A suite completa teve ainda 7 erros de infraestrutura por `PermissionError` no diretório temporário global do Windows; eles não foram tratados como aprovação nem como defeito atribuído ao auditor.

### FL-20260830-TEAM-034 — Promover precedente no Neo4j somente após revisão humana explícita

- **Timestamp:** 2026-08-30T08:10:00-03:00
- **Status:** VALIDATED
- **Decision owner:** usuário solicitante
- **Participantes:** usuário solicitante; Codex como executor e recorder
- **Categoria:** contract | data | operations
- **Escopo:** `CTR-API-001 v3.1`, `CTR-MEM-PROMOTE-001 v1`, `CTR-INC-001 v1`, API FastAPI, Neo4j
- **Links:** `DEC-030`; `contracts/v1/incident-confirmation*.schema.json`; `tests/test_incident_confirmation_api.py`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O pipeline detectava e persistia o Incident atual em DuckDB, enquanto o promotor Neo4j existia apenas como serviço interno. Faltava a ponte auditável para capturar a revisão humana e provar que um detector, RCA ou agente não consegue por si só criar precedente histórico.

#### Decisão

Adicionar o contrato aditivo `CTR-MEM-PROMOTE-001 v1` em `POST /v1/incidents/{incident_id}/confirmation`. O endpoint aceita apenas `REAL_HUMAN_REVIEW`, requer `review_id`, `reviewer_id`, causa confirmada, playbook, decline codes e forma temporal; consulta primeiro o Incident durável e só então chama o promotor Neo4j. A causa e o estado atuais em `CTR-INC-001 v1` permanecem inalterados. Repetir exatamente a mesma revisão é idempotente; uma revisão diferente para o mesmo Incident retorna `409`.

#### Critérios e por que agora

A demonstração precisa separar detecção de autoridade humana e apresentar evidência de que o precedente realmente alcançou o Neo4j. Não havia UI/endereço público para a confirmação, portanto a ponte não podia continuar implícita.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Inserir no Neo4j ao detectar | caminho curto | detector ganharia autoridade de confirmação | FACT: o pipeline atual só deve persistir Incident em DuckDB | viola o requisito humano |
| Aceitar fallback em memória local | mantém demo quando Neo4j cai | resposta pareceria confirmação sem persistência histórica real | FACT: fallback é efêmero | rejeitada |
| Endpoint explícito com Neo4j obrigatório | rastreável, idempotente e demonstrável | requer captura de revisão e autenticação futura | TEST: casos HTTP focalizados passam | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `IncidentPromoter` já exigia campos de revisão e gravava via `IncidentMemoryRepository`.
- **TEST:** `python -m pytest tests/test_incident_confirmation_api.py tests/test_memory_promotion.py tests/test_neo4j_repository.py tests/test_incident_pipeline.py -q` — 11 passed; `python scripts/validate_contracts.py` — OK.
- **ASSUMPTION:** no MVP sintético, `reviewer_id` é atribuição declarada pelo operador; owner Team; revalidar antes de qualquer dado real.
- **UNKNOWN:** autenticação/autorização corporativa e trilha de identidade verificável não existem nesta API.

#### Trade-offs aceitos

- **Ganhamos:** detector → revisão explícita → Neo4j, sem promoção automática.
- **Abrimos mão de:** confirmar precedentes quando o Neo4j está indisponível.
- **Dívida/limitação:** o endpoint ainda não autentica `reviewer_id`; não deve ser exposto a usuários não confiáveis fora do ambiente sintético.
- **Risco residual:** duas confirmações concorrentes em processos distintos dependem da unicidade/idempotência do Neo4j; o teste local cobre repetição e conflito sequenciais.

#### Consequências e propagação

- **Produto/demo:** a UI pode chamar a confirmação após ação humana e exibir o recibo histórico, sem reclassificar o Incident.
- **Arquitetura/contratos:** adiciona `CTR-MEM-PROMOTE-001 v1` e `CTR-API-001 v3.1`; `CTR-INC-001 v1` continua congelado.
- **Pessoas/branches:** Rogério coordena rota/OpenAPI; Altoé mantém adapter Neo4j; André precisa consumir o endpoint somente após UX de revisão autenticada.
- **Plano/Linear:** `docs/plans/system-plan.md` e planos de Rogério/Altoé sincronizados; Linear não alterado.
- **Testes/observabilidade:** repetir, revisão e smoke API são obrigatórios; indisponibilidade Neo4j deve devolver `503`.

#### Validação e trial by fire

- **Hipótese verificável:** sem POST não há write de memória; POST válido retorna `HUMAN_CONFIRMED` e uma repetição não duplica o precedente.
- **Caminho feliz:** Incident durável → POST de revisão → `IncidentPromoter` → Neo4j → recibo tipado.
- **Caso difícil/adverso:** revisão sintética, campos inválidos, Neo4j indisponível e revisão conflitante não geram ou alteram um precedente.
- **Resultado observado:** PASS nos testes focalizados; conexão Neo4j configurada foi previamente verificada como saudável. O write real não foi disparado contra a base configurada durante este desenvolvimento.
- **Fallback:** `503 MEMORY_UNAVAILABLE` ou `MEMORY_PERSISTENCE_FAILED`, sem fallback local apresentado como confirmação.

#### Gatilhos de revisão

Qualquer exposição além do ambiente sintético, requisito de identidade verificável, UI de confirmação, escrita concorrente multi-réplica ou mudança em `CTR-INC-001` exige novo change control.

#### Adendos

- 2026-08-30T08:10:00-03:00 — primeira implementação e validação focal; revisão de código, suite completa e smoke HTTP local pendentes neste momento.
- 2026-08-30T08:20:00-03:00 — `27` testes de API/pipeline/memória/Neo4j passaram, `scripts/validate_contracts.py` e `compileall` passaram, e a revisão do diff não encontrou bloqueador. A suíte completa foi tentada, mas o pytest não tem permissão para listar a pasta temporária global do Windows; a cobertura deste fluxo foi repetida com `--basetemp` isolado. Não houve escrita de teste no Neo4j configurado. Como ainda não há UI de confirmação, a aceitação observável foi a requisição HTTP exercitada por `TestClient`; validação visual/browser fica pendente da tela consumidora.

### FL-20260829-TEAM-001 — Adotar um Flight Log Markdown, append-only e dividido por lanes

- **Timestamp:** 2026-08-29T11:56:33-03:00
- **Status:** VALIDATED
- **Decision owner:** André
- **Participantes:** André (solicitante); protocolo disponível para Altoé, Rogério e Renato revisarem
- **Categoria:** operations | Git/integration | demo
- **Escopo:** registro de decisões durante todo o hackathon
- **Links:** `.agents/skills/flight-log-recorder/`, `AGENTS.md`, `docs/SKILLS.md`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O hackathon exige um decision log no repositório e avalia se a equipe consegue explicar decisões importantes, alternativas rejeitadas e trade-offs reais. Quatro pessoas trabalharão em branches paralelas. A pergunta foi como capturar decisões no momento em que acontecem sem criar um artefato impossível de integrar ou uma narrativa reconstruída no final.

#### Decisão

Manter um único `docs/flight-log.md` versionado, append-only, com lanes estáveis para Team, André, Altoé, Rogério e Renato. Uma skill automática detecta decisões materiais, aplica um schema profundo e propaga backlinks para planos, contratos, Linear e evidências. Decisões revertidas permanecem e ganham sucessoras.

#### Critérios e por que agora

O log precisa ser público no repositório, colaborativo, legível pela banca, resistente a branches paralelas e contemporâneo às escolhas. A estrutura precisava existir antes da descoberta para não perder as primeiras decisões de problema, MVP e arquitetura.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Um único log cronológico com todos editando o fim | Leitura simples | Alto risco de conflito em todo append | FACT: quatro branches paralelas estão planejadas | O hotspot ocorreria em praticamente toda decisão |
| Um arquivo por decisão | Poucos conflitos e histórico granular | Entrega deixa de ser um único `.md`; navegação e exportação ficam fragmentadas | ASSUMPTION: a banca espera um decision log direto no repo | Não atende tão diretamente ao formato solicitado |
| Registrar no Linear ou ferramenta externa | Colaboração e filtros prontos | Dependência externa e entrega não autocontida no GitHub | FACT: foi solicitado `.md` no repositório | Pode servir de backlink, não de fonte principal |
| Um Markdown com lanes por participante e Team | Um entregável, conflitos localizados, histórico Git | Exige disciplina de append e consolidação final do índice | INFERENCE baseada no modelo de branches | Melhor equilíbrio entre entrega e colaboração |

#### Evidência, hipóteses e desconhecidos

- **FACT:** a entrega inclui decision log, README e diagrama de arquitetura; a banca valoriza alternativas e trade-offs.
- **TEST:** `quick_validate.py` aprovou `flight-log-recorder`, `hackathon-system-planner` e `integration-contract-guardian`; `git diff --check` não encontrou erros.
- **ASSUMPTION:** lanes separadas reduzirão conflitos se cada participante respeitar o protocolo; validar no primeiro checkpoint de integração.
- **UNKNOWN:** formato adicional exigido pela organização além de Markdown; confirmar quando o regulamento integral estiver disponível.

#### Trade-offs aceitos

- **Ganhamos:** um artefato único, auditável, colaborativo e pronto para defesa.
- **Abrimos mão de:** ordenação cronológica automática durante o desenvolvimento.
- **Dívida/limitação:** o índice precisa ser consolidado no code freeze.
- **Risco residual:** decisões coletivas simultâneas ainda podem conflitar; um único recorder por decisão mitiga isso.

#### Consequências e propagação

- **Produto/demo:** decisões principais poderão ser usadas na defesa técnica e no Q&A.
- **Arquitetura/contratos:** toda mudança material deve citar IDs `DEC-*`/`CTR-*` quando existirem.
- **Pessoas/branches:** cada pessoa escreve em sua lane; decisões transversais têm recorder único.
- **Plano/Linear:** decisões que alterem execução devem ser propagadas às fontes atuais, não apenas ao log.
- **Testes/observabilidade:** afirmações de funcionamento devem citar teste executado ou `NOT RUN`.

#### Validação e trial by fire

- **Hipótese verificável:** quatro branches conseguem acrescentar decisões sem apagar entradas ou gerar IDs duplicados.
- **Caminho feliz:** cada participante adiciona uma entrada em sua lane e o merge preserva todas.
- **Caso difícil/adverso:** duas branches registram simultaneamente decisão coletiva ou tentam o mesmo ID.
- **Resultado observado:** NOT RUN; validar no primeiro checkpoint de integração.
- **Fallback:** recorder único para `Team`, resolução preservando ambas as entradas e renumeração apenas da ainda não integrada.

#### Gatilhos de revisão

Reavaliar se houver conflitos recorrentes, exigência oficial de outro formato, dificuldade de leitura pela banca ou falha em capturar decisões durante o primeiro bloco do evento.

#### Adendos

- 2026-08-29 — Codex: validação estrutural e checagem do diff concluídas; status atualizado de `ACCEPTED` para `VALIDATED` sem alterar a decisão.

### FL-20260829-TEAM-002 — Separar avaliação viva do histórico de decisões

- **Timestamp:** 2026-08-29T12:08:01-03:00
- **Status:** VALIDATED
- **Decision owner:** André (request owner); integração executada pelo Codex
- **Participantes:** André; contribuição remota de Rogério Faria preservada em `avaliacao.md`
- **Categoria:** operations | Git/integration | demo
- **Escopo:** `avaliacao.md`, `docs/flight-log.md` e entregável D5
- **Links:** `avaliacao.md`, `docs/flight-log.md`, commit remoto `c77d0cc`
- **Supersedes / superseded by:** refina a decisão histórica `DEC-001` de `avaliacao.md`; não aplicável como substituição de `FL-*`

#### Contexto e pergunta

Durante a implementação, `origin/main` recebeu `avaliacao.md`, um documento profundo com critérios oficiais, placar, trial by fire e uma seção declarada como decision log. Em paralelo, o pedido atual criou um Flight Log colaborativo, automático e append-only. Manter os dois como logs canônicos causaria duplicidade, decisões divergentes e dúvida sobre qual arquivo entregar.

#### Decisão

Preservar `avaliacao.md` como fonte viva de critérios, placar, entregáveis, trial by fire e preparação do Q&A. Tornar `docs/flight-log.md` o único decision log canônico, referenciado por `avaliacao.md`. Preservar a decisão histórica `DEC-001` por backlinks em vez de apagá-la da narrativa.

#### Critérios e por que agora

A integração precisava ocorrer antes do commit local. Fonte única, histórico preservado, menor chance de conflito e leitura inequívoca pela banca dominaram a escolha.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Manter dois decision logs | Nenhuma migração | Duplicidade, divergência e dúvida na entrega | FACT: ambos se declaravam canônicos | Viola fonte única e aumenta trabalho durante o evento |
| Abandonar o novo Flight Log e usar apenas `avaliacao.md` | Menos arquivos | Um hotspot único mistura placar e appends de quatro branches; perde protocolo e lanes | FACT: o usuário pediu uma skill e `.md` colaborativo profundo | Não atende a colaboração paralela com robustez suficiente |
| Remover a seção histórica do arquivo remoto sem rastro | Estrutura limpa | Apaga decisão de outro commit e contexto de integração | FACT: `DEC-001` já está em `origin/main` | Contraria histórico append-only e preservação de trabalho alheio |
| Separar papéis e ligar os arquivos | Uma fonte por responsabilidade e histórico preservado | Exige manter backlinks coerentes | INFERENCE validada por revisão documental | Melhor equilíbrio de clareza, colaboração e integração |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `c77d0cc` adicionou `avaliacao.md` enquanto esta skill era desenvolvida.
- **TEST:** merge fast-forward preservou o arquivo remoto; busca de referências confirmou os pontos que precisavam ser redirecionados.
- **ASSUMPTION:** a banca aceita o entregável D5 em `docs/flight-log.md`; ele permanece Markdown no repositório público.
- **UNKNOWN:** se a organização exige nome exato para o arquivo; confirmar antes do code freeze.

#### Trade-offs aceitos

- **Ganhamos:** responsabilidade única por arquivo, menos conflitos e entrega clara.
- **Abrimos mão de:** ter avaliação e histórico completo em uma única página.
- **Dívida/limitação:** backlinks entre os dois documentos precisam continuar válidos.
- **Risco residual:** alguém pode continuar adicionando `DEC-*` em `avaliacao.md`; o `AGENTS.md` e a nota em §6 reduzem esse risco.

#### Consequências e propagação

- **Produto/demo:** Q&A e placar usam `avaliacao.md`; justificativas detalhadas usam o Flight Log.
- **Arquitetura/contratos:** decisões `DEC-*` no plano apontam para `FL-*`.
- **Pessoas/branches:** todos escrevem decisões somente nas lanes do Flight Log.
- **Plano/Linear:** backlinks continuam obrigatórios quando a decisão altera estado operacional.
- **Testes/observabilidade:** o gate de integração verifica duplicação, remoção e links quebrados.

#### Validação e trial by fire

- **Hipótese verificável:** um participante encontra critérios e decision log a partir de qualquer um dos dois documentos sem ambiguidade.
- **Caminho feliz:** `avaliacao.md` direciona D5 e §6 ao Flight Log; o Flight Log preserva as decisões.
- **Caso difícil/adverso:** uma branch antiga adiciona novo `DEC-*` à antiga seção ou remove entrada ao resolver conflito.
- **Resultado observado:** PASS na revisão documental; simulação real entre quatro branches ainda NOT RUN.
- **Fallback:** integration guardian bloqueia o merge e migra a entrada preservando autor, timestamp e conteúdo.

#### Gatilhos de revisão

Exigência oficial de nome/localização, conflitos recorrentes, backlinks quebrados ou feedback de que dois documentos ainda confundem leitores.

#### Adendos

- **2026-08-29T18:13:16-03:00:** validação final em `127.0.0.1:8516` confirmou o estado padrão com `LOCAL FIXTURE FALLBACK` e sem `status: live`; `?fixture=inconclusive` renderiza `INCONCLUSIVE`, aviso causal não-confirmatório, métricas da fixture (82% → 67%, BRL 1.940,00) e conteúdo em inglês. O parâmetro desconhecido retorna ao incidente suportado. Browser acceptance em 375, 768, 1024 e 1440 px registrou zero overflow horizontal e zero card/texto fora do content box; drill-down expande e console não contém erros. `py_compile`, assertions focadas e `git diff --check` passaram; code review `PASS` sem achados bloqueantes.

### FL-20260829-TEAM-003 — Colocar precisão causal e memória recorrente no núcleo do MVP

- **Timestamp:** 2026-08-29T15:31:16-03:00
- **Status:** ACCEPTED
- **Decision owner:** André, em nome do time solicitante
- **Participantes:** André; recomendações arquiteturais do Codex; validação futura por Altoé, Rogério e Renato
- **Categoria:** product | scope | data | demo
- **Escopo:** MVP, métricas, identidade de pagamentos e trial by fire
- **Links:** DEC-001, DEC-002, CTR-EVT-001, CTR-INC-001, `docs/plans/system-plan.md`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

A banca prioriza causa raiz e indicou fortemente memória de recorrência. O prazo permite muitas ideias, mas não profundidade em todas. Também era necessário escolher o denominador de conversão sem confundir retries.

#### Decisão

O MVP deve detectar e localizar a causa, separar incidentes, recuperar um precedente humano confirmado — incluindo o caso Mastercard de dois dias antes — e explicar a recorrência por evidências. Modelar `Payment`, `Attempt` e `Event`; usar approval por attempt como métrica primária de provider e payment conversion como métrica secundária.

#### Critérios e por que agora

Precisão top-1, aderência ao enunciado, robustez ao trial by fire e clareza de denominador dominam quantidade de features.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| MVP sem memória | Menor escopo | perde bônus explicitamente valorizado | FACT: juiz indicou memória fortemente | não atende a decisão do usuário |
| Uma métrica “conversão” única | UI simples | retries distorcem provider e payment | FACT: múltiplos attempts podem pertencer ao mesmo payment | ambígua e difícil de defender |
| Approval por attempt + conversion por payment | preserva duas leituras | schema e UI um pouco maiores | INFERENCE do lifecycle de pagamento | melhor precisão sem ocultar recovery |

#### Evidência, hipóteses e desconhecidos

- **FACT:** nova combinação usa o mesmo schema e pode alterar múltiplas métricas.
- **TEST:** NOT RUN; validar nos casos holdout.
- **ASSUMPTION:** incidente histórico confirmado pode ser seed sintético, desde que claramente rotulado.
- **UNKNOWN:** volume exato do laptop; benchmark em H2.

#### Trade-offs aceitos

- **Ganhamos:** profundidade causal, memória demonstrável e métricas não ambíguas.
- **Abrimos mão de:** antifraude, RL e remediation no MVP.
- **Dívida/limitação:** memória inicial usa incidentes sintéticos confirmados.
- **Risco residual:** similaridade pode ser confundida com identidade causal; UI deve dizer “recorrência provável”.

#### Consequências e propagação

- **Produto/demo:** recurrence, simultaneous e inconclusive são casos obrigatórios.
- **Arquitetura/contratos:** CTR-EVT-001 e CTR-INC-001 congelam identidades/denominadores.
- **Pessoas/branches:** todos consomem esses nomes sem redefinição.
- **Plano/Linear:** plano geral e quatro planos sincronizados; Linear não autorizado.
- **Testes/observabilidade:** top-1 accuracy e exact scope são métricas principais.

#### Validação e trial by fire

- **Hipótese verificável:** nova combinação é localizada sem hardcode.
- **Caminho feliz:** provider BR e recurrence Mastercard.
- **Caso difícil/adverso:** dois incidentes e baixa evidência.
- **Resultado observado:** NOT RUN.
- **Fallback:** memória estruturada sem embedding; nunca cortar RCA.

#### Gatilhos de revisão

Revisar se a fatia ponta a ponta não estiver funcionando em H4 ou se holdout mostrar confusão entre attempts e payments.

#### Adendos

- Nenhum.

### FL-20260829-TEAM-004 — Adotar modular monolith Python com DuckDB/Parquet, Neo4j e Streamlit

- **Timestamp:** 2026-08-29T15:31:17-03:00
- **Status:** ACCEPTED
- **Decision owner:** Team
- **Participantes:** André e Codex; revisão pendente dos demais
- **Categoria:** architecture | operations | Git/integration
- **Escopo:** DEC-003 e componentes CMP-*
- **Links:** DEC-003, `docs/plans/system-plan.md`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

Em 19 horas, serviços distribuídos aumentariam setup, contratos de rede e falhas operacionais. Ainda é necessário suportar analytics local volumoso, grafo e UI.

#### Decisão

Usar modular monolith Python: FastAPI como fronteira, DuckDB/Parquet para fatos/agregados, Neo4j para memória e Streamlit para UI. Interfaces internas permanecem tipadas e versionadas.

#### Critérios e por que agora

Velocidade de integração, execução local, fallback e coerência de linguagem venceram escalabilidade de produção.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Kafka + microservices + Postgres | arquitetura de produção | setup e debugging excessivos | ASSUMPTION: nenhuma infra pronta | incompatível com 19h |
| tudo em Neo4j | uma tecnologia | inadequado para raw/time-series scans | FACT: grafo é bônus de memória | uso errado do grafo |
| monolith modular | integra cedo e mantém boundaries | menor escala operacional | FACT: demo local | melhor risco/valor |

#### Evidência, hipóteses e desconhecidos

- **FACT:** DuckDB consulta Parquet diretamente; Neo4j possui driver/GraphRAG oficial.
- **TEST:** NOT RUN; health check em H1.
- **ASSUMPTION:** Docker/Python disponíveis; fallback local.
- **UNKNOWN:** Neo4j Aura ou local; adapter esconde a escolha.

#### Trade-offs aceitos

- **Ganhamos:** menos infraestrutura e fatia H4.
- **Abrimos mão de:** streaming distribuído e deploy production-grade.
- **Dívida/limitação:** processos locais não representam escala da Yuno.
- **Risco residual:** Streamlit/FastAPI podem divergir; fixture e OpenAPI mitigam.

#### Consequências e propagação

- **Produto/demo:** demo local com fallback explícito.
- **Arquitetura/contratos:** CTR-API-001 é a única fronteira da UI.
- **Pessoas/branches:** Rogério coordena package/schema; André não acessa DB.
- **Plano/Linear:** ownership sincronizado.
- **Testes/observabilidade:** `/health` por dependência.

#### Validação e trial by fire

- **Hipótese verificável:** todos os módulos integram sem deploy externo obrigatório.
- **Caminho feliz:** fixture percorre API/UI.
- **Caso difícil/adverso:** Neo4j/OpenAI offline.
- **Resultado observado:** NOT RUN.
- **Fallback:** adapters in-memory e template.

#### Gatilhos de revisão

Falha do health check H1 ou impossibilidade de consulta dentro do orçamento da demo.

#### Adendos

- Nenhum.

### FL-20260829-TEAM-005 — Gerar três meses por código vetorizado, não por linhas de LLM

- **Timestamp:** 2026-08-29T15:31:18-03:00
- **Status:** ACCEPTED
- **Decision owner:** Team
- **Participantes:** André e Codex; Renato revisará o benchmark
- **Categoria:** data | AI/RAG | quality
- **Escopo:** DEC-004, CMP-DATA-001, CTR-SCN-001
- **Links:** DEC-004, CTR-SCN-001, TASK-RENATO-001
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O juiz pediu muita data e sugeriu LLM, mas gerar milhões de rows por tokens seria lento, caro, não reproduzível e estatisticamente incoerente.

#### Decisão

NumPy/Polars geram pelo menos 90 dias, seed fixa, sazonalidade e relações condicionais; Parquet persiste. A LLM pode propor ScenarioDefinition/narrativas, nunca fabricar o dataset linha a linha. Ground truth fica separado.

#### Critérios e por que agora

Reprodutibilidade, volume, controle causal e holdout dominam variedade textual.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| LLM por row | aparente diversidade | custo, baixa escala, inconsistência | INFERENCE técnica | não atende volume/controle |
| biblioteca tabular treinada | realismo potencial | não há dataset real para aprender | FACT: só existe enunciado | não há base |
| gerador probabilístico vetorizado | rápido, reprodutível, causal | requer modelar distribuições | ASSUMPTION validada em H2 | melhor para trial by fire |

#### Evidência, hipóteses e desconhecidos

- **FACT:** não há input real e o schema é conhecido.
- **TEST:** NOT RUN; meta default >=1M attempts em <=60s, ajustável após benchmark.
- **ASSUMPTION:** esse volume é suficiente para demo estatística.
- **UNKNOWN:** hardware final.

#### Trade-offs aceitos

- **Ganhamos:** ground truth exato e geração rápida.
- **Abrimos mão de:** realismo aprendido de tráfego Yuno real.
- **Dívida/limitação:** distribuições são hipóteses sintéticas.
- **Risco residual:** cenário fácil demais; holdout e mix-shift mitigam.

#### Consequências e propagação

- **Produto/demo:** jurado injeta qualquer filtro conhecido por JSON.
- **Arquitetura/contratos:** CTR-SCN-001 congelado.
- **Pessoas/branches:** Renato owns dados; detector não lê ground truth.
- **Plano/Linear:** TASK-RENATO-001/002.
- **Testes/observabilidade:** seed, row count e distribution checks.

#### Validação e trial by fire

- **Hipótese verificável:** nova combinação é gerada sem mudança de código.
- **Caminho feliz:** provider-country.
- **Caso difícil/adverso:** efeitos múltiplos e simultâneos.
- **Resultado observado:** NOT RUN.
- **Fallback:** menos raw rows e mesmos aggregates de 90 dias.

#### Gatilhos de revisão

Benchmark H2, distribuição degenerada ou leakage de ground truth.

#### Adendos

- Nenhum.

### FL-20260829-TEAM-006 — Usar detector estatístico hierárquico em vez de agentes por dimensão

- **Timestamp:** 2026-08-29T15:31:19-03:00
- **Status:** ACCEPTED
- **Decision owner:** Team
- **Participantes:** André e Codex; Renato valida em evals
- **Categoria:** architecture | quality | data
- **Escopo:** DEC-005, CMP-DET-001, CMP-RCA-001
- **Links:** DEC-005, CTR-DET-001, OBJ-RENATO-001
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

Covariância e um agente por dimensão foram considerados, mas o domínio mistura resultado binomial, latência robusta, categorias de alta cardinalidade, baixa amostra e incidentes simultâneos.

#### Decisão

Usar baseline sazonal, Beta-Binomial/Wilson para approval, MAD/quantis para latência, volume/persistência mínimos e RCA por beam search/contribuição até depth 3. Agentes não detectam; covariância fica pós-MVP.

#### Critérios e por que agora

Precisão, calibragem, explicabilidade e capacidade de testar contra ground truth.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| seis agentes | narrativa modular | inconsistência e ausência de teste estatístico | INFERENCE | complexidade sem ganho medido |
| covariância como núcleo | relações numéricas | fraca para categorias/denominadores | FACT do tipo dos dados | complementar apenas |
| detector hierárquico | evidência reproduzível | thresholds exigem calibração | ASSUMPTION: evals suficientes | alinha à métrica principal |

#### Evidência, hipóteses e desconhecidos

- **FACT:** precisão causal é critério principal escolhido.
- **TEST:** NOT RUN; holdout em H12–H15.
- **ASSUMPTION:** depth 3 cobre casos da banca sem explosão.
- **UNKNOWN:** thresholds finais.

#### Trade-offs aceitos

- **Ganhamos:** scores recalculáveis e no-answer objetivo.
- **Abrimos mão de:** exploração irrestrita de todas as combinações.
- **Dívida/limitação:** pode perder causa de depth >3.
- **Risco residual:** overfitting de threshold; holdout separado.

#### Consequências e propagação

- **Produto/demo:** UI mostra coverage/confidence factors.
- **Arquitetura/contratos:** CTR-DET-001 não contém narrativa.
- **Pessoas/branches:** Renato owns algoritmo; Rogério correlaciona candidates.
- **Plano/Linear:** eval dataset obrigatório.
- **Testes/observabilidade:** top1, exact scope e false incidents.

#### Validação e trial by fire

- **Hipótese verificável:** holdout novo mantém top-1 correto.
- **Caminho feliz:** provider BR.
- **Caso difícil/adverso:** Simpson/mix shift e baixa amostra.
- **Resultado observado:** NOT RUN.
- **Fallback:** reduzir top-k/depth sem mudar contrato.

#### Gatilhos de revisão

Baixa accuracy, muitos falsos positivos ou latência incompatível com demo.

#### Adendos

- Nenhum.

### FL-20260829-TEAM-007 — Usar memória Graph RAG híbrida e um explicador read-only grounded

- **Timestamp:** 2026-08-29T15:31:20-03:00
- **Status:** ACCEPTED
- **Decision owner:** Team
- **Participantes:** André e Codex; Altoé é owner de validação
- **Categoria:** AI/RAG | architecture | payments | security
- **Escopo:** DEC-006, DEC-007, CMP-MEM-001, CMP-EXP-001
- **Links:** CTR-MEM-001, CTR-LLM-001, OBJ-ALTOE-001
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O juiz valorizou Neo4j/agentic RAG, mas memória sem grounding pode transformar coincidência em causa e um LLM autônomo pode inventar métricas ou ações.

#### Decisão

Neo4j guarda incidentes/entidades, Cypher faz prefilter, score estruturado ranqueia e embedding opcional reranqueia. Somente causas humanas confirmadas são precedentes. Um agente read-only usa Responses API Structured Output para explicar e escolher playbook; código calcula todos os fatos. Sem tools financeiras.

#### Critérios e por que agora

Originalidade, explicabilidade, no-answer, segurança e fallback determinístico.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| vector-only RAG | simples | perde relações e explicação de match | FACT: dados são altamente estruturados | insuficiente para evidência |
| agentic loop livre | flexível | custo, latência e hallucination | INFERENCE | incompatível com autoridade read-only |
| hybrid read-only | grafo + semântica + trace | mais componentes | FACT: juiz indicou Neo4j | benefício demonstrável com fallback |

#### Evidência, hipóteses e desconhecidos

- **FACT:** Neo4j oferece driver/GraphRAG; OpenAI suporta Structured Outputs.
- **TEST:** NOT RUN; evals de recurrence/no-answer em H12.
- **ASSUMPTION:** credenciais disponíveis até H1; fallback local.
- **UNKNOWN:** ganho real do embedding; será medido e pode ser cortado.

#### Trade-offs aceitos

- **Ganhamos:** memória auditável e narrativa grounded.
- **Abrimos mão de:** autonomia ampla e armazenamento de raw no grafo.
- **Dívida/limitação:** seed histórico sintético.
- **Risco residual:** false recurrence; fatores diferentes e thresholds explícitos mitigam.

#### Consequências e propagação

- **Produto/demo:** “recorrência provável” com evidência e precedente confirmado.
- **Arquitetura/contratos:** CTR-MEM-001 trace obrigatório; CTR-LLM-001 evidence IDs.
- **Pessoas/branches:** Altoé owns memória/prompt; André somente renderiza.
- **Plano/Linear:** memory é MVP; vector/web são cortáveis.
- **Testes/observabilidade:** precision@1, no-answer e citation coverage.

#### Validação e trial by fire

- **Hipótese verificável:** Mastercard histórico retorna top-1 e caso sem par retorna vazio.
- **Caminho feliz:** incidente de dois dias antes.
- **Caso difícil/adverso:** precedente conflitante/não confirmado e prompt injection.
- **Resultado observado:** NOT RUN.
- **Fallback:** Cypher + template determinístico.

#### Gatilhos de revisão

Neo4j/API indisponível, embedding sem ganho ou evidence coverage abaixo de 100%.

#### Adendos

- Nenhum.

### FL-20260829-TEAM-008 — Proteger quatro horas finais e distribuir ownership pelas especialidades

- **Timestamp:** 2026-08-29T15:31:21-03:00
- **Status:** ACCEPTED
- **Decision owner:** André, em nome do time solicitante
- **Participantes:** André e Codex; confirmação de carga em H0:30
- **Categoria:** scope | operations | Git/integration | demo
- **Escopo:** DEC-008, DEC-009 e quatro planos individuais
- **Links:** `docs/plans/people/`, `docs/plans/system-plan.md`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O juiz mencionou 15 horas para construir e o time possui 19 horas totais. Uma pessoa precisa de menor carga para frontend/pitch. Especialidades: Altoé em RAG/banco, Rogério em backend e Renato em computação.

#### Decisão

Tratar H0–H15 como construção e H15–H19 como integração, acceptance, ensaio e pitch. André assume UI/pitch com 6–7h de implementação; Altoé memória/RAG; Rogério backend/contratos/integration coordinator; Renato dados/detector/RCA.

#### Critérios e por que agora

Caminho crítico, especialidade, ownership único e working demo prevalecem sobre igualdade no número de tarefas.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| todos codificam 19h | mais features | nenhuma integração/ensaio | FACT: pitch/frontend exigem tempo | risco alto de demo quebrada |
| André também no backend crítico | mais capacidade central | pitch vira atividade residual | ASSUMPTION: André é owner adequado de UI/pitch | conflita com restrição |
| 15h + 4h protegidas | integra/testa/ensaia | menor feature throughput | FACT: 19h total | maximiza evidência funcional |

#### Evidência, hipóteses e desconhecidos

- **FACT:** usuário definiu especialidades e uma pessoa com menos tarefas.
- **TEST:** NOT RUN; forward simulation documentada no plano.
- **ASSUMPTION:** André é a pessoa de frontend/pitch; validar H0:30.
- **UNKNOWN:** preferências adicionais do time.

#### Trade-offs aceitos

- **Ganhamos:** integração coordenada, pitch e demo ensaiada.
- **Abrimos mão de:** quatro horas de feature building e distribuição numérica igual.
- **Dívida/limitação:** Rogério concentra hotspots; checkpoints mitigam.
- **Risco residual:** carga pesada de Renato; cortes de depth/top-k previstos.

#### Consequências e propagação

- **Produto/demo:** code freeze H15.
- **Arquitetura/contratos:** owners fixos na matriz.
- **Pessoas/branches:** planos individuais criados.
- **Plano/Linear:** Linear permanece não autorizado.
- **Testes/observabilidade:** gates H4/H8/H13/H15–H17.

#### Validação e trial by fire

- **Hipótese verificável:** fatia H4 e demo completa H15.
- **Caminho feliz:** merges na ordem planejada.
- **Caso difícil/adverso:** dependência externa falha antes do pitch.
- **Resultado observado:** NOT RUN.
- **Fallback:** cortar web/vector/polimento, preservar vertical e memory estruturada.

#### Gatilhos de revisão

Fatia H4 falha, owner indisponível, carga crítica desequilibrada ou nova regra do evento.

#### Adendos

- Nenhum.

### FL-20260829-TEAM-009 — Publicar o plano no Linear do workspace Lumen com quatro owners confirmados

- **Timestamp:** 2026-08-29T15:42:08-03:00
- **Status:** VALIDATED
- **Decision owner:** André
- **Participantes:** André; Gabriel Altoé Batista; Renato Bello; Rogério; Codex como recorder
- **Categoria:** operations | ownership | Git/integration
- **Escopo:** Linear, hierarquia de issues e sincronização dos planos
- **Links:** `docs/plans/linear-preview.md`, [projeto Linear](https://linear.app/lumenhack/project/lumen-yuno-hackathon-fd0533f171d5), LUM2-4, LUM2-5, LUM2-6, LUM2-7
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O primeiro conector apontava para um workspace antigo e não resolvia Altoé/Renato. Após reconectar o MCP oficial, o workspace `Lumen`, o team `LUMEN HACKATHON` e os quatro e-mails foram confirmados. Era necessário escolher destino, hierarquia, estado e política de criação sem duplicar trabalho.

#### Decisão

Criar o projeto `Lumen — Yuno Hackathon` no team `LUMEN HACKATHON`, sem ciclo, com estado inicial `Todo` e label existente `Feature`. Criar quatro parent issues por `OBJ-*`, 50 microtarefas com assignee único e relações em uma segunda passagem. André recebe carga menor para frontend/pitch.

#### Critérios e por que agora

Os usuários foram confirmados por e-mail no MCP correto e o usuário autorizou explicitamente terminar o planejamento e publicar tudo no Linear.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Usar workspace antigo | conector já respondia | usuários/time incorretos | TEST: Altoé e Renato não resolviam | risco de atribuição errada |
| Criar sem projeto | menos uma entidade | perde visão do hackathon | FACT: nenhum projeto existe no team novo | projeto melhora agrupamento |
| Projeto + parents + sub-issues | contexto e ownership claros | 54 issues e segunda passagem | FACT: preview aprovado | melhor rastreabilidade |

#### Evidência, hipóteses e desconhecidos

- **FACT:** MCP retorna os quatro usuários ativos e team correto.
- **TEST:** leitura de workspace, teams, users, statuses, labels e issues; zero issues existentes.
- **ASSUMPTION:** ausência de ciclo é intencional para evento de 19h.
- **UNKNOWN:** convenção de estimativas; campos de estimate ficarão vazios.

#### Trade-offs aceitos

- **Ganhamos:** microtarefas executáveis, dependências reais e owner único.
- **Abrimos mão de:** estimativas nativas do Linear e ciclo.
- **Dívida/limitação:** 50 microtarefas exigem verificação pós-criação.
- **Risco residual:** falha parcial; protocolo manda parar e inventariar.

#### Consequências e propagação

- **Produto/demo:** trabalho alinhado aos checkpoints H4/H8/H15.
- **Arquitetura/contratos:** descriptions repetem CTR/DEC relevantes.
- **Pessoas/branches:** assignments usam e-mails confirmados.
- **Plano/Linear:** backlinks escritos no plano geral, quatro planos individuais e preview.
- **Testes/observabilidade:** verificar contagem, parents, assignees, estados e relações.

#### Validação e trial by fire

- **Hipótese verificável:** todo executor encontra contexto, contrato, aceite, teste e handoff na issue.
- **Caminho feliz:** 4 parents + 50 children, todos atribuídos.
- **Caso difícil/adverso:** falha após criação parcial.
- **Resultado observado:** PASS — 54/54 issues no team/project corretos; owner counts 8/13/17/16 incluindo parents; child counts 7/12/16/15; 50 microtarefas e zero divergências nas relações `blockedBy`.
- **Fallback:** parar na primeira falha, reler estado e não repetir cegamente.

#### Gatilhos de revisão

Mudança de time, assignee, plano, contrato, caminho crítico ou falha parcial no Linear.

#### Adendos

- **2026-08-29T16:01:00-03:00:** projeto criado em `Lumen`; parents `LUM2-4`–`LUM2-7`; microtarefas `LUM2-8`–`LUM2-57`. Releitura completa confirmou estado `Todo`, label `Feature`, assignees exatos, descrições com ID estável e 48 tarefas bloqueadas pelas relações previstas; `TASK-CORE-001` e `TASK-CON-001` são as duas raízes intencionais. Nenhuma escrita parcial falhou.
- **2026-08-29T16:06:00-03:00:** o preflight de `integration-contract-guardian` encontrou aliases não canônicos em 21 descrições do Linear. `CTR-TXN-001`, `CTR-WIN-001` e `CTR-ANM-001` foram substituídos respectivamente pelos IDs congelados `CTR-EVT-001`, `CTR-AGG-001` e `CTR-DET-001`; releitura das 21 issues confirmou zero alias restante. Os schemas não foram renomeados.

### FL-20260829-TEAM-010 — Priorizar descoberta causal atual e usar memória para acelerar a solução

- **Timestamp:** 2026-08-29T16:28:49-03:00
- **Status:** ACCEPTED
- **Decision owner:** Team, confirmado por André
- **Participantes:** André; Codex como recorder; validação de implementação por Altoé, Rogério e Renato
- **Categoria:** product | architecture | AI/RAG | demo
- **Escopo:** DEC-010, CMP-RCA-001, CMP-INC-001, CMP-MEM-001, CMP-EXP-001
- **Links:** `docs/plans/system-plan.md` v1.1.0, `docs/plans/architecture-diagrams.md`, CTR-INC-001, CTR-MEM-001, CTR-LLM-001
- **Supersedes / superseded by:** não substitui FL-20260829-TEAM-007; explicita sua fronteira de autoridade

#### Contexto e pergunta

Um diagrama anterior sugeria que não encontrar um incidente na memória levaria diretamente a incerteza. Isso inverteria o objetivo do produto: o sistema precisa descobrir combinações novas e só depois verificar recorrência. Também era necessário explicitar por que a memória importa operacionalmente: recuperar uma solução anterior potencialmente reutilizável.

#### Decisão

Detector e RCA atuais são a única fonte da suficiência causal. `matches=[]` significa `NO_PRECEDENT`, não `INCONCLUSIVE`. Depois de formar o incidente, a memória procura recorrências humanas confirmadas e recupera o playbook anterior. Esse playbook é priorizado somente se suas precondições ainda forem compatíveis com causa, escopo e evidências atuais; o sistema explica diferenças e apenas recomenda ao humano.

#### Critérios e por que agora

Precisão em combinações inéditas é o critério principal da banca. Memória deve reduzir tempo de resposta em recorrências sem limitar descoberta nem transformar coincidência histórica em causalidade atual.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Memória como gate | simples de explicar | falha em causas novas e confunde ausência de histórico com ausência de evidência | FACT: trial by fire usa combinação não ensaiada | viola o objetivo central |
| Ignorar memória na recomendação | separação forte | perde o principal ganho operacional do bônus | FACT: usuário quer reaproveitar solução anterior | desperdiça conhecimento confirmado |
| RCA atual + memória posterior | descobre novos casos e acelera recorrências | exige duas confianças e validação de precondições | FACT: contratos já separam Incident de SimilarIncidentResult | escolhido |

#### Evidência, hipóteses e desconhecidos

- **FACT:** o fluxo e os contratos já calculavam `Incident.root_cause` antes de `CTR-MEM-001`; a ambiguidade estava na representação e na regra de recomendação.
- **TEST:** NOT RUN; fixtures de causa suportada com `matches=[]` foram adicionados para contract/e2e.
- **ASSUMPTION:** o catálogo de playbooks terá precondições verificáveis por causa/escopo; Altoé valida antes de H8.
- **UNKNOWN:** granularidade mínima das precondições; se faltar, o sistema recomenda inspeção, não reutilização direta.

#### Trade-offs aceitos

- **Ganhamos:** descoberta de causas inéditas, sem perder memória recorrente e solução anterior.
- **Abrimos mão de:** narrativa mais simples de “buscar caso igual e repetir”.
- **Dívida/limitação:** exige versionar e avaliar precondições dos playbooks.
- **Risco residual:** solução antiga pode estar obsoleta; diferenças e `HUMAN_ONLY` mitigam.

#### Consequências e propagação

- **Produto/demo:** trial by fire demonstra caso novo; cenário Mastercard demonstra reaproveitamento fundamentado.
- **Arquitetura/contratos:** sem quebra de schema; semântica de CTR-MEM-001 esclarecida e fixtures adicionados.
- **Pessoas/branches:** Renato prova descoberta sem memória; Altoé valida solução anterior; Rogério preserva root cause; André separa diagnóstico de precedente.
- **Plano/Linear:** plano geral e planos individuais sincronizados; auditoria mostrou que as issues atuais já preservam essa separação, portanto nenhuma relação/tarefa mudou.
- **Testes/observabilidade:** casos `SUPPORTED + NO_PRECEDENT`, `SUPPORTED + MATCH`, `INCONCLUSIVE + MATCH/NO_MATCH` e `MEMORY_UNAVAILABLE`.

#### Validação e trial by fire

- **Hipótese verificável:** uma combinação nova recebe causa suportada mesmo com memória vazia; uma recorrência recebe o playbook anterior com rationale.
- **Caminho feliz:** provider novo no Brasil sem match e Mastercard recorrente com match.
- **Caso difícil/adverso:** precedente semelhante com escopo ou precondição incompatível.
- **Resultado observado:** NOT RUN; plano e fixtures preparados.
- **Fallback:** manter diagnóstico e usar playbook genérico/inspeção humana quando memória ou precondições falharem.

#### Gatilhos de revisão

RCA depender de histórico, `NO_PRECEDENT` gerar `INCONCLUSIVE`, recomendação antiga sem rationale/precondição ou jurado demonstrar regressão em causa nova.

#### Adendos

- **2026-08-29T16:40:08-03:00:** decisão substituída por `FL-20260829-TEAM-011`. Preserva-se a separação de autoridade, mas a consulta à memória passa a ocorrer também para incidentes atuais `INCONCLUSIVE`.

### FL-20260829-TEAM-011 — Consultar memória mesmo quando a causa atual for inconclusiva

- **Timestamp:** 2026-08-29T16:40:08-03:00
- **Status:** ACCEPTED
- **Decision owner:** Team, confirmado por André
- **Participantes:** André; Codex como recorder; validação de implementação por Altoé, Rogério e Renato
- **Categoria:** product | architecture | AI/RAG | contract | demo
- **Escopo:** DEC-011, CMP-RCA-001, CMP-INC-001, CMP-MEM-001, CMP-EXP-001, CMP-UI-001
- **Links:** `docs/plans/system-plan.md` v1.2.0, `docs/plans/architecture-diagrams.md`, CTR-INC-001, CTR-MEM-001, CTR-LLM-001
- **Supersedes / superseded by:** supersedes FL-20260829-TEAM-010

#### Contexto e pergunta

A regra anterior preservava corretamente o diagnóstico de casos novos, mas sua formulação podia fazer um incidente atual `INCONCLUSIVE` encerrar antes de consultar a memória. Isso descartaria um precedente semelhante que um humano confirmou no passado justamente quando os sinais atuais ainda são fracos. A pergunta é como aproveitar esse histórico sem transformar similaridade em prova causal atual.

#### Decisão

Todo Incident detectado consulta a memória depois que o RCA fixa seu status atual, tanto `SUPPORTED` quanto `INCONCLUSIVE`. O sistema combina dois eixos sem fundi-los: suficiência causal atual e existência de precedente. Em `INCONCLUSIVE + MATCH`, mostra o incidente histórico, sua causa humana confirmada, fatores iguais/diferentes e o playbook usado, mas mantém a causa atual inconclusiva e apresenta o playbook apenas como roteiro de investigação. Somente `INCONCLUSIVE + NO_PRECEDENT` termina sem causa sustentada nem precedente. Toda ação permanece `HUMAN_ONLY`.

#### Critérios e por que agora

A memória deve capturar conhecimento operacional humano, inclusive diagnósticos que os sinais automatizados atuais ainda não conseguem provar. Ao mesmo tempo, precisão causal é a prioridade da banca, então o precedente não pode alterar `root_cause.status` nem entrar no score estatístico atual.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Consultar memória apenas para causa atual suportada | fluxo simples e menor custo | perde precedentes úteis nos casos mais ambíguos | FACT: o usuário exige busca mesmo sem causa atual | não atende o comportamento desejado |
| Fazer o match histórico confirmar a causa atual | resposta mais assertiva | confunde similaridade com causalidade e pode repetir erro antigo | FACT: prioridade é precisão da causa | risco de falso diagnóstico |
| Consultar sempre e manter dois status independentes | aproveita conhecimento humano sem adulterar evidência atual | exige matriz de quatro estados e copy cuidadosa | INFERENCE: schemas atuais já separam Incident e SimilarIncidentResult | escolhido |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `CTR-INC-001` já aceita `root_cause.status=INCONCLUSIVE`; `CTR-MEM-001` consulta escopo/sinais e não precisa alterar o schema para receber esse incidente.
- **TEST:** validação local de 2026-08-29 confirmou parse de todos os JSON, conformidade das cinco fixtures novas/afetadas com seus schemas por validador recursivo, cinco blocos Mermaid balanceados e IDs únicos no Flight Log; código da aplicação ainda não existe.
- **ASSUMPTION:** escopo, métricas, decline profile e forma temporal do incidente inconclusivo serão suficientes para recuperação útil; Altoé valida em `TASK-ALTOE-006`.
- **UNKNOWN:** threshold ótimo para matches parciais em baixa amostra; até os evals, o sistema deve mostrar score e diferenças.

#### Trade-offs aceitos

- **Ganhamos:** recuperação de conhecimento humano nos casos em que a investigação atual ainda não fecha uma causa.
- **Abrimos mão de:** um fluxo linear simples e de uma única confiança agregada.
- **Dívida/limitação:** UI, API e evals precisam cobrir a matriz causal × memória e evitar copy ambígua.
- **Risco residual:** um precedente visualmente parecido pode induzir viés de ancoragem; mitigado por diferenças visíveis, limitação explícita e causa atual ainda `INCONCLUSIVE`.

#### Consequências e propagação

- **Produto/demo:** o caso inconclusivo pode dizer “não sei a causa atual, mas há um precedente humano semelhante e esta foi a investigação/solução anterior”.
- **Arquitetura/contratos:** sem mudança sintática de schema; mudança comportamental no acionamento de CTR-MEM-001 e na composição de CTR-LLM-001.
- **Pessoas/branches:** Renato entrega assinatura também no no-answer; Altoé recupera sem causa atual; Rogério preserva os dois eixos; André renderiza os quatro estados.
- **Plano/Linear:** plano geral v1.2.0 e planos individuais sincronizados; descrições do Linear devem ser auditadas no próximo sync autorizado.
- **Testes/observabilidade:** evals separados para `SUPPORTED + MATCH`, `SUPPORTED + NO_PRECEDENT`, `INCONCLUSIVE + MATCH`, `INCONCLUSIVE + NO_PRECEDENT` e `MEMORY_UNAVAILABLE`.

#### Validação e trial by fire

- **Hipótese verificável:** um incidente de baixa cobertura ainda recupera o Mastercard confirmado de dois dias antes sem mudar a causa atual de `INCONCLUSIVE`.
- **Caminho feliz:** o dashboard mostra precedente, solução anterior, fatores coincidentes/divergentes e limitação causal na mesma tela.
- **Caso difícil/adverso:** match alto em bandeira/país, mas provider diferente e amostra pequena; o sistema não afirma “mesma causa”.
- **Resultado observado:** PASS para consistência documental, schemas/fixtures e estrutura dos diagramas; NOT RUN para comportamento da aplicação, pois ainda não foi implementada.
- **Fallback:** se memória falhar, preservar o status atual e declarar `MEMORY_UNAVAILABLE`; se nenhum match passar o threshold, `INCONCLUSIVE + NO_PRECEDENT`.

#### Gatilhos de revisão

Qualquer implementação que pule memória em `INCONCLUSIVE`, promova causa atual por match histórico, esconda fatores divergentes ou recomende execução automática exige revisão imediata.

#### Adendos

- **2026-08-29T16:44:00-03:00:** `git diff --check` passou; cinco fixtures validaram contra os contratos relevantes, os cinco diagramas possuem fences balanceadas e o Flight Log contém 11 IDs únicos. Não foi executado teste de aplicação porque o repositório ainda contém apenas planejamento/contratos.

### FL-20260829-TEAM-012 — Tipar o estado da memória no contrato compartilhado

- **Timestamp:** 2026-08-29T16:48:27-03:00
- **Status:** ACCEPTED
- **Decision owner:** Team
- **Participantes:** André; Codex como recorder; lacuna identificada em revisão cruzada do plano de Altoé
- **Categoria:** contract | architecture | AI/RAG | UX
- **Escopo:** DEC-012, CTR-MEM-001, CTR-API-001, CMP-MEM-001, CMP-API-001, CMP-UI-001
- **Links:** `docs/plans/system-plan.md` v1.3.0, `contracts/v1/similar-incidents.schema.json`, `contracts/v1/api.openapi.yaml`
- **Supersedes / superseded by:** complementa FL-20260829-TEAM-011; não altera sua separação de autoridade

#### Contexto e pergunta

CTR-MEM-001 devolvia apenas `matches[]`. Uma lista vazia representava `NO_PRECEDENT`, mas a arquitetura também exigia `MEMORY_UNAVAILABLE`. Sem estado tipado, API e UI teriam de inferir falha por health, exceção ou texto, criando interpretações divergentes justamente nos casos inconclusivos.

#### Decisão

Substituir CTR-MEM-001 v1 por v1.1 antes da implementação. `memory_status` passa a ser obrigatório com `MATCH_FOUND`, `NO_PRECEDENT` ou `MEMORY_UNAVAILABLE`. O detalhe da API expõe separadamente Incident, SimilarIncidentResult e ExplanationBundle. `matches=[]` continua presente nos dois últimos estados, mas consumidores usam `memory_status`, nunca a lista, para distinguir ausência de precedente de indisponibilidade.

#### Critérios e por que agora

O contrato ainda não foi implementado, então a migração coordenada agora é barata. Estado explícito melhora teste, copy e fallback sem misturar falha operacional com incerteza causal.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Inferir por `matches=[]` | nenhum campo novo | torna `NO_PRECEDENT` indistinguível de falha | FACT: ambos podem produzir lista vazia | semanticamente incorreto |
| Inferir pelo `/health` | evita mudar schema | health global pode divergir da chamada específica e cria race | INFERENCE de sistemas distribuídos | não representa o resultado da consulta |
| Campo obrigatório `memory_status` | contrato e testes determinísticos | mudança incompatível antes da implementação | FACT: nenhum consumidor foi implementado ainda | escolhido |

#### Evidência, hipóteses e desconhecidos

- **FACT:** o schema v1 não possuía campo de estado; OpenAPI descrevia apenas “Incident plus explanation”.
- **TEST:** PASS documental: quatro fixtures `similar-incidents*.json` validaram contra CTR-MEM-001 v1.1; JSON, OpenAPI YAML, versões dos quatro planos individuais, cinco diagramas e IDs do Flight Log passaram nas checagens locais.
- **ASSUMPTION:** uma resposta degradada com `MEMORY_UNAVAILABLE`, trace e `matches=[]` é suficiente para a demo; Rogério/Altoé validam no checkpoint H8.
- **UNKNOWN:** se produção futura preferirá erro HTTP parcial; fora do MVP local.

#### Trade-offs aceitos

- **Ganhamos:** estados observáveis e copy correta em UI/API.
- **Abrimos mão de:** compatibilidade com fixtures v1 ainda não implementadas.
- **Dívida/limitação:** precisa validar coerência entre status e quantidade de matches no código, pois o schema atual não usa condicionais `if/then`.
- **Risco residual:** adapter pode emitir combinação inválida; contract tests cobrem os três estados.

#### Consequências e propagação

- **Produto/demo:** “sem precedente” e “memória indisponível” ficam visual e semanticamente distintos.
- **Arquitetura/contratos:** CTR-MEM-001 v1.1 e resposta detalhada do CTR-API-001; CTR-EXT-001 permanece opcional, timeout 5 s, `NOT_CHECKED` e somente corroboration.
- **Pessoas/branches:** Altoé produz o status; Rogério o transporta; André o renderiza; Renato não é afetado.
- **Plano/Linear:** plano geral v1.3.0 e planos individuais sincronizados; preview Linear 1.3.0 aguarda confirmação antes de escrita.
- **Testes/observabilidade:** fixtures de match, no precedent e unavailable; contract test impede inferência por lista vazia.

#### Validação e trial by fire

- **Hipótese verificável:** UI distingue `INCONCLUSIVE + NO_PRECEDENT` de `INCONCLUSIVE + MEMORY_UNAVAILABLE` sem analisar texto.
- **Caminho feliz:** `MATCH_FOUND` contém ao menos um precedente e mostra a solução histórica.
- **Caso difícil/adverso:** Neo4j cai durante um incidente inconclusivo; causa atual permanece inconclusiva e UI declara indisponibilidade, não ausência de histórico.
- **Resultado observado:** PASS para migração documental/contratual; NOT RUN para aplicação, ainda não implementada.
- **Fallback:** adapter in-memory emite o mesmo contrato; se também falhar, `MEMORY_UNAVAILABLE`.

#### Gatilhos de revisão

Consumidor inferindo status por `matches.length`, necessidade de erro HTTP parcial, ou implementação iniciada ainda usando schema v1.

#### Adendos

- **2026-08-29T16:50:00-03:00:** validação pós-migração passou para quatro fixtures de memória, três fixtures causais/explicativas, parse de todos os JSON, OpenAPI YAML, cinco diagramas, versões 1.3.0 dos quatro planos individuais, 12 IDs únicos no Flight Log e `git diff --check`.
- **2026-08-29T16:49:29-03:00:** o schema passou a impor as invariantes de estado: `MATCH_FOUND` exige ao menos um match; `NO_PRECEDENT` e `MEMORY_UNAVAILABLE` exigem lista vazia. O parse das quatro fixtures e a checagem dessas invariantes passaram; teste de aplicação continua `NOT RUN`.

### FL-20260829-TEAM-013 — Expor combinações de cenário por construtor visual, não por casos prontos

- **Timestamp:** 2026-08-29T17:59:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** André (solicitante)
- **Participantes:** André; Codex como recorder e planejador
- **Categoria:** product | UX | contract | demo
- **Escopo:** `DEC-013`, `CTR-SCN-001 v1.1`, `CTR-API-001 v1.1`, `CMP-DATA-001`, `CMP-API-001`, `CMP-UI-001`, `TASK-DATA-006`, `TASK-API-003`, `TASK-UI-005`
- **Links:** `docs/plans/system-plan.md` v1.4.0, `contracts/v1/scenario*.schema.json`, `contracts/v1/api.openapi.yaml`, `docs/plans/people/{andre,rogerio,renato}.md`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O plano mostrava cenários demonstrativos nomeados e a UI chamaria IDs existentes. André pediu que a banca pudesse escolher qualquer combinação que o sistema suporta, pela interface e sem inserir código, e que os casos prontos desaparecessem do fluxo. Era preciso manter o trial by fire sem permitir combinações impossíveis ou vazar a verdade da causa.

#### Decisão

Substituir a lista de casos prontos por um construtor visual abastecido em tempo de execução por um catálogo de dimensões, valores, limites de efeitos, duração e capacidade simultânea. A UI envia apenas uma request validável; API e gerador criam `scenario_id`, `correlation_id`, seed e timestamps. A verdade da causa permanece isolada do catálogo, request, UI e diagnóstico. O fluxo inclui catálogo, criação, acompanhamento de status e incidentes filtráveis por correlação.

#### Critérios e por que agora

O requisito explícito da banca de variar combinações precisa ser observável sem depender de código ou assistência da equipe. Como o repositório ainda não implementou a API de injeção, a mudança coordenada de contrato agora não cria migração de consumidores em produção.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Manter botões de cenários fixos | Roteiro mais rápido e previsível | Não permite escolha real da banca; parece hardcoded | FACT: André pediu remover os casos prontos | Não atende ao requisito |
| Aceitar JSON ou código livre | Máxima liberdade para teste | Permite valores impossíveis, aumenta erro operacional e revela detalhes técnicos desnecessários | INFERENCE: banca não deve precisar programar | Sem guardrails suficientes para demo ao vivo |
| Formulário baseado em catálogo do gerador | Escolha real dentro do domínio suportado; validação e UX claras | Requer novos endpoints, mocks e estados | FACT: `CTR-SCN-001` já modela filtros/efeitos e `FACT-002` prevê combinação nova | Escolhido |

#### Evidência, hipóteses e desconhecidos

- **FACT:** o plano já afirma que a banca pode injetar uma nova combinação dentro do schema conhecido; `TASK-RENATO-002` já prevê nova combinação sem código.
- **TEST:** NOT RUN — apenas schemas, OpenAPI e planos foram atualizados; não há API integrada neste momento.
- **ASSUMPTION:** o catálogo pode representar todo domínio permitido pelo gerador, incluindo o limite de cenários ativos; Renato valida no contract test de `TASK-DATA-006`.
- **UNKNOWN:** quais valores exatos estarão presentes no catálogo final, pois dependem das dimensões que o gerador efetivamente produzir; a UI não pode hardcodá-los.

#### Trade-offs aceitos

- **Ganhamos:** trial by fire conduzido pela banca, sem código e com combinações realmente suportadas.
- **Abrimos mão de:** um roteiro de um clique e da simplicidade de somente chamar IDs conhecidos.
- **Dívida/limitação:** o catálogo fixture inicial é apenas mock; o gerador precisa se tornar sua fonte autoritativa antes da integração.
- **Risco residual:** uma combinação válida pode terminar em `INCONCLUSIVE` ou não gerar incidente; a UI deve declarar esse resultado, não tratá-lo como falha.

#### Consequências e propagação

- **Produto/demo:** construtor vazio substitui casos prontos; a banca escolhe dimensões, efeitos e duração visualmente.
- **Arquitetura/contratos:** `CTR-SCN-001` passa a v1.1 com catálogo e request; `CTR-API-001` passa a v1.1 com `GET /demo/scenario-catalog`, `POST /demo/scenarios`, `GET /demo/scenarios/{scenario_id}` e filtro de correlação em incidents.
- **Pessoas/branches:** Renato produz catálogo/validação; Rogério publica a API/status; André consome catálogo e renderiza estados; Altoé não altera retrieval.
- **Plano/Linear:** plano geral 1.4.0, três planos individuais e preview foram atualizados. As issues externas LUM2-12, LUM2-40 e LUM2-48 precisam de sincronização autorizada; nenhuma escrita externa foi feita.
- **Testes/observabilidade:** contract tests cobrem catálogo/request, `403/409/422`, idempotência por `request_id`, sigilo de ground truth e status; browser acceptance cobre formulário e estados.

#### Validação e trial by fire

- **Hipótese verificável:** uma pessoa seleciona uma combinação oferecida pela UI, injeta sem código e recebe `SUPPORTED`, `INCONCLUSIVE` ou estado de falha honesto vinculado à correlação.
- **Caminho feliz:** catalogar opções → enviar request → acompanhar `PENDING/EMITTING` → localizar incidentes por `correlation_id`.
- **Caso difícil/adverso:** banca tenta valor fora do catálogo, excede a capacidade simultânea ou cria combinação de baixa evidência; API/UI respondem respectivamente `422`, `409` e `INCONCLUSIVE` sem ground truth.
- **Resultado observado:** NOT RUN.
- **Fallback:** se a API não responder em 2 s, usar fixture local marcada `DEMO FALLBACK`; ela não oferece seletor de casos prontos nem se apresenta como live.

#### Gatilhos de revisão

Catálogo incapaz de expressar uma dimensão gerada, UI com valores hardcoded, vazamento de ground truth, endpoint fora de demo mode, ou feedback da banca de que o construtor é lento demais para o tempo de pitch.

#### Adendos

- **2026-08-29T17:59:00-03:00:** mudança documental e de contrato preparada; validação executável e browser acceptance ainda pendentes da implementação.
- **2026-08-29T17:59:00-03:00:** revisão de contrato corrigiu duas lacunas antes da aceitação do plano: catálogo agora só pode publicar as mesmas chaves de dimensão aceitas pela request, e filtros vazios são válidos para permitir a queda global/difusa do roteiro. A validação de sintaxe e invariantes das fixtures passou; execução de API/browser continua `NOT RUN`.
- **2026-08-29T17:59:00-03:00:** o change control classificou a retirada do endpoint de IDs e a restrição de dimensões como incompatíveis. Os nomes `v1.1` acima foram um rascunho não implementado; o estado operacional canônico é `CTR-SCN-001 v2` e `CTR-API-001 v2`, com mocks atualizados diretamente e sem adapter legado.
- **2026-08-29T19:35:00-03:00:** após comparar com a `main`, o rótulo `DEC-013` usado nesta experiência local foi identificado como colisão com a decisão Railway já publicada em `FL-20260829-ROGERIO-001`. O ID canônico `DEC-013` pertence ao deploy Railway; esta experiência não recebe novo DEC e seu escopo público foi substituído por `DEC-015`.

### FL-20260829-TEAM-014 — Ensaiar o construtor por fixture local com dois streams e cancelamento

- **Timestamp:** 2026-08-29T18:15:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** André (solicitante)
- **Participantes:** André; Codex como implementador
- **Categoria:** UX | demo | contract
- **Escopo:** `DEC-014`, `CMP-UI-001`, `CTR-API-001 v2.1`, `TASK-UI-005`
- **Links:** `app/ui/dashboard.py`, `contracts/fixtures/scenario-catalog.json`, `docs/plans/system-plan.md` v1.5.0
- **Supersedes / superseded by:** complementa FL-20260829-TEAM-013

#### Contexto e pergunta

O construtor precisava ser utilizável antes da API, e André definiu campos do plano geral, seleção única, dois cenários ativos, cancelamento, inglês, explicação de incerteza e detalhes técnicos recolhidos.

#### Decisão

Implementar primeiro um construtor Streamlit por fixture local. Cada dimensão aceita `Any` ou um único valor; dois streams podem ficar ativos; encerrar um preserva o histórico. O resultado local é explicitamente um fallback demonstrativo e explica em inglês quando não consegue isolar causa.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Esperar API | Resultado real imediato | Bloqueia UI e ensaio | FACT: André pediu local primeiro | Não atende ao fluxo escolhido |
| Permitir múltiplos valores por campo | Mais combinações por clique | Interface e leitura da banca ficam ambíguas | FACT: André recusou múltipla seleção | Não atende ao requisito |
| Fixture local com seleção única | Ensaiável e diretamente migrável ao contrato | Não calcula evidência real | FACT: catálogo e fallback já existem | Escolhido |

#### Evidência, hipóteses e desconhecidos

- **TEST:** NOT RUN no momento deste registro; validação de browser e fluxo local seguem após implementação.
- **ASSUMPTION:** o catálogo final terá as mesmas chaves do fixture local; API substitui o adapter sem mudar a UI.
- **UNKNOWN:** tempo real de detecção do gerador integrado.

#### Trade-offs aceitos

- **Ganhamos:** demo e acceptance independentes da API.
- **Abrimos mão de:** métricas calculadas a partir do cenário escolhido nesta primeira etapa.
- **Risco residual:** jurado pode confundir fixture com live; badge e textos de fallback tornam a limitação explícita.

#### Consequências e propagação

- **Produto/demo:** construtor em inglês, correlação recolhida, mensagem honesta para `INCONCLUSIVE`.
- **Arquitetura/contratos:** API v2.1 adiciona `CANCELLED` e `DELETE` para manter a transição direta.
- **Pessoas/branches:** André inicia por fixture; Rogério implementa espelho HTTP; Renato mantém catálogo autoritativo.
- **Testes/observabilidade:** code review e browser acceptance do construtor são obrigatórios antes de aceitar o código.

#### Validação e trial by fire

- **Hipótese verificável:** jurado adiciona dois cenários sem código, encerra um e entende o estado sem abrir detalhes técnicos.
- **Caso difícil/adverso:** cenário amplo gera `INCONCLUSIVE` com explicação em vez de causa inventada.
- **Resultado observado:** NOT RUN.
- **Fallback:** manter o construtor local rotulado `LOCAL FIXTURE FALLBACK`.

#### Gatilhos de revisão

Qualquer opção hardcoded, terceiro stream ativo, seleção múltipla por campo, falta de explicação de incerteza ou API incompatível.

#### Adendos

- **2026-08-29T18:15:00-03:00:** `py_compile` e `git diff --check` passaram. Browser acceptance permanece BLOCKED porque `streamlit` não está instalado neste ambiente (`ModuleNotFoundError`); nenhuma afirmação de interação no navegador foi feita.
- **2026-08-29T19:35:00-03:00:** após comparar com a `main`, o rótulo `DEC-014` usado nesta experiência local foi identificado como colisão com a decisão de `Incident.scope` já publicada em `FL-20260829-ROGERIO-002`. O ID canônico `DEC-014` pertence à decisão de scope; o construtor local permanece protótipo e seu escopo público foi substituído por `DEC-015`.

### FL-20260829-TEAM-015 — Tornar transações, batches e samples a entrada pública do produto

- **Timestamp:** 2026-08-29T19:10:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** André (solicitante)
- **Participantes:** André; Codex como recorder e planejador
- **Categoria:** product | UX | contract | data
- **Escopo:** `DEC-015`, `CTR-TXN-001 v1`, `CTR-TXL-001 v1`, `CTR-API-001 v3`, `CMP-WEB-001`, `CMP-TXN-001`
- **Links:** `docs/plans/system-plan.md` v2.0.0, `contracts/v1/transaction-*.schema.json`, `contracts/v1/api.openapi.yaml`
- **Supersedes / superseded by:** supersedes o escopo público de `FL-20260829-TEAM-013` e `FL-20260829-TEAM-014`; o construtor de cenários é preservado como harness interno

#### Contexto e pergunta

O protótipo pedia que a pessoa configurasse efeitos como queda de approval e latência. André identificou que esses valores são outputs do sistema: o usuário só deve fornecer fatos da transação. Também pediu múltiplos inputs e geração aleatória para não montar cada linha durante a demo.

#### Decisão

A entrada pública passa a aceitar batches atômicos de 1 a 100 transações. O Railway oferece catálogo e geração de samples por quantidade e seed; samples preenchem linhas editáveis e não são persistidos até `Submit batch`. Input proíbe status, decline, taxas, efeitos, causa, ground truth, PAN, CVV e PII. Outcomes, métricas, classificação e incidentes são derivados depois.

#### Critérios e por que agora

O modelo transaction-first representa o trabalho real do usuário e permite demonstrar automação, enquanto seed fixa torna o ensaio reproduzível. A decisão antecede a implementação final do frontend e evita consolidar a API v2 errada.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Manter formulário de efeitos | Usa o protótipo atual | Usuário calcula o que o produto deveria descobrir | FACT: requisito explícito de André | Contradiz o produto |
| Gerar linhas aleatórias hardcoded no browser | Muito rápido | catálogo diverge; demo não é reproduzível nem governada pelo backend | INFERENCE: opções mudarão durante integração | Fonte de verdade errada |
| Railway gera inputs por catálogo/seed e usuário revisa | rápido, reproduzível e sem antecipar resultado | adiciona endpoint e um clique antes do submit | FACT: todos os dados devem passar pelo backend Railway | Escolhido |

#### Evidência, hipóteses e desconhecidos

- **FACT:** contratos anteriores aceitavam multipliers de approval/latency e o Streamlit expunha scenario builder.
- **TEST:** schemas e fixtures preparados; validação executável ainda `NOT RUN` neste registro.
- **ASSUMPTION:** batch máximo 100 é suficiente para a demo; revisar com teste de carga.
- **UNKNOWN:** volume mínimo para cada caso gerar anomalia; o harness de fundo cobre a demo sem falsificar o input.

#### Trade-offs aceitos

- **Ganhamos:** narrativa coerente, batch rápido, reprodutibilidade e separação entre input/fato derivado.
- **Abrimos mão de:** controle público direto sobre o efeito e resultado previsível em qualquer lote pequeno.
- **Dívida/limitação:** a banca pode gerar um lote sem incidente; a UI deve explicar isso honestamente.
- **Risco residual:** valores aleatórios pouco diversos; testes do catálogo/seed devem medir cobertura básica.

#### Consequências e propagação

- **Produto/UI:** novas rotas de input, log e detalhe; samples por quantidade/seed.
- **Contrato/API:** novos CTR-TXN/TXL e API v3; cenário v2 deixa a API pública.
- **Dados:** Renato produz sample/outcome adapters; Rogério persiste/processa; André apresenta; Altoé só recebe Incident.
- **Plano/Linear:** plano geral e quatro planos atualizados; Linear aguarda confirmação do preview 2.0.

#### Validação e trial by fire

- **Hipótese verificável:** três inputs gerados com seed fixa podem ser revisados, submetidos e acompanhados individualmente.
- **Caminho feliz:** gerar → revisar → submit → processing → outcomes → logs/detail.
- **Caso difícil/adverso:** 101 itens, mesma idempotency key com payload diferente, campo PII ou lote sem anomalia.
- **Resultado observado:** NOT RUN.
- **Fallback:** fixture de sample/batch claramente rotulada até a API estar live.

#### Gatilhos de revisão

Necessidade real de mais de 100 itens, catálogo incapaz de gerar inputs válidos, sample vazando outcome/ground truth ou latência de batch incompatível com a demo.

#### Adendos

- **2026-08-29T19:10:00-03:00:** schemas, fixtures e projeções foram preparados; implementação e Linear permanecem pendentes.

### FL-20260829-TEAM-016 — Separar frontend Vercel do data plane Railway

- **Timestamp:** 2026-08-29T19:20:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** André (solicitante)
- **Participantes:** André; Codex como recorder e planejador
- **Categoria:** architecture | deployment | security | integration
- **Escopo:** `DEC-016`, `CTR-DEP-001 v1`, `CMP-WEB-001`, `CMP-API-001`, `CMP-DEPLOY-001`
- **Links:** `docs/plans/deployment-vercel-railway.md`, `docs/plans/architecture-diagrams.md`
- **Supersedes / superseded by:** supersedes Streamlit como frontend final em `FL-20260829-TEAM-014`; Streamlit permanece fallback local

#### Contexto e pergunta

André definiu Vercel para o frontend e Railway para o backend e pediu que todos os dados passem pelo mesmo servidor. Era necessário impedir acesso direto do navegador a DuckDB, Neo4j ou secrets e explicitar a fronteira de rede.

#### Decisão

Next.js roda na Vercel e consome somente a API HTTPS FastAPI do Railway. Como a Vercel não participa da private network Railway, a API recebe domínio público com CORS allowlist para origins Vercel/local. Worker, volume, stores, agent credentials e ground truth permanecem privados.

#### Critérios e por que agora

A separação viabiliza deploy independente sem duplicar lógica no frontend. Fixar env, CORS e ownership antes do código reduz falhas de integração e vazamento de credenciais.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Hospedar tudo no Railway | menos CORS | contraria deploy Vercel solicitado; UI e backend acoplados | FACT: Vercel + Railway foi definido | Não atende |
| Vercel acessar banco/Neo4j | elimina alguns endpoints | secrets e stores chegam ao browser/runtime errado | segurança por design | Rejeitada |
| Vercel → API pública Railway com allowlist | fronteira única e contratos testáveis | exige CORS e health por ambiente | documentação oficial Railway/Vercel consultada | Escolhido |

#### Evidência, hipóteses e desconhecidos

- **FACT:** Railway documenta domínio público para FastAPI e private networking apenas entre serviços do projeto.
- **FACT:** Vercel usa environment variables por ambiente para a base URL.
- **TEST:** deploy/CORS `NOT RUN`; somente plano preparado.
- **UNKNOWN:** URLs finais de preview e production; serão preenchidas no deploy, nunca inventadas no repo.

#### Trade-offs aceitos

- **Ganhamos:** fronteira de dados única, frontend stateless e deploys claros.
- **Abrimos mão de:** rede integralmente privada entre browser-facing frontend e API.
- **Dívida/limitação:** previews exigem atualização controlada de allowlist.
- **Risco residual:** env/CORS incorreto bloqueia a demo; smoke deployed é obrigatório.

#### Consequências e propagação

- **Frontend:** `NEXT_PUBLIC_API_BASE_URL` é a única config pública.
- **Backend:** domínio HTTPS, health, CORS e error states explícitos.
- **Segurança:** stores/secrets nunca são públicos; wildcard CORS não é aceito.
- **Operação:** ordem Railway primeiro, Vercel preview depois, production por último.

#### Validação e trial by fire

- **Hipótese verificável:** Vercel production/preview autorizadas acessam `/v1`; uma origin aleatória é negada.
- **Caso difícil/adverso:** backend down, origin nova e env apontando para localhost.
- **Resultado observado:** NOT RUN.
- **Fallback:** UI mostra `BACKEND UNAVAILABLE`; fixture local não se apresenta como live.

#### Gatilhos de revisão

Necessidade de auth real, private ingress/edge proxy, múltiplos tenants ou restrições de compliance.

#### Adendos

- **2026-08-29T19:20:00-03:00:** topologia e runbook registrados; URLs e smoke aguardam serviços reais.

### FL-20260829-TEAM-017 — Persistir progresso no Railway e preservar DuckDB e o gerador como adapters

- **Timestamp:** 2026-08-29T19:30:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** Team, proposto por Codex para minimizar quebra
- **Participantes:** André; Codex como recorder e planejador
- **Categoria:** architecture | reliability | scope | integration
- **Escopo:** `DEC-017`, `CMP-TXN-001`, `CMP-HARNESS-001`, Railway Volume, `CTR-TXL-001 v1`
- **Links:** `docs/plans/system-plan.md` v2.0.0, `docs/plans/deployment-vercel-railway.md`
- **Supersedes / superseded by:** complementa `FL-20260829-TEAM-015`; reclassifica o gerador público de `013/014` como interno

#### Contexto e pergunta

O log precisa mostrar processamento verdadeiro e sobreviver a refresh/restart. Ao mesmo tempo, migrar imediatamente todo o trabalho concluído de DuckDB para Postgres ou apagar o scenario generator aumentaria muito o risco da hackathon.

#### Decisão

O worker Railway persiste stage/progress e usa polling 1–2s no MVP. DuckDB/Parquet ficam em Railway Volume com uma réplica aceita; o persistence adapter preserva futura migração para Postgres. O scenario generator vira harness interno e envia tráfego pela mesma batch API, sem escrita direta no banco.

#### Critérios e por que agora

Progresso backend-authored é necessário para uma UI honesta. Volume + adapter reaproveita ingestão/agregação existentes; polling tem menor complexidade que SSE. Passar o harness pela API prova a mesma rota usada pelo usuário.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Timer de progresso no frontend | implementação mínima | mente sobre estágio e quebra após refresh | requisito de log real | Rejeitada |
| Postgres + queue externa imediatamente | escala/replicas melhores | reescreve store já concluído e expande escopo | Railway Postgres é alternativa viável, não necessária ao MVP | Adiada |
| DuckDB Volume + lifecycle durável + polling | reaproveita trabalho e torna estado observável | uma réplica e pequena indisponibilidade no deploy | documentação Railway Volume | Escolhido |

#### Evidência, hipóteses e desconhecidos

- **FACT:** Railway Volume mantém dados, mas limita o serviço a uma réplica.
- **FACT:** o repositório já possui contratos e tarefas concluídas orientadas a DuckDB/Parquet e scenario generator.
- **TEST:** restart, lease, polling e deploy `NOT RUN`.
- **ASSUMPTION:** uma réplica e polling bastam para a carga de demo.

#### Trade-offs aceitos

- **Ganhamos:** mínimo retrabalho, estado real e uma fatia integrada cedo.
- **Abrimos mão de:** horizontal scaling e push realtime no MVP.
- **Dívida/limitação:** migração Postgres/SSE se carga ou disponibilidade exigirem.
- **Risco residual:** job preso após crash; lease/reconciliation e smoke de restart são obrigatórios.

#### Consequências e propagação

- **Contrato:** lifecycle tipado e separação entre outcome failed e pipeline failed.
- **Backend:** persist before `202`, idempotência e worker retomável.
- **Frontend:** polling somente enquanto processing; sem incremento local.
- **Dados:** harness e samples compartilham domínio, mas só batch persiste/processa.

#### Validação e trial by fire

- **Hipótese verificável:** um item permanece visível e retoma após restart sem duplicar evento/métrica.
- **Caso difícil/adverso:** crash entre persistência e classificação, reentrega duplicada e progress regressivo.
- **Resultado observado:** NOT RUN.
- **Fallback:** marcar `PIPELINE_FAILED`/degraded e permitir retry idempotente; nunca converter em decline.

#### Gatilhos de revisão

Necessidade de mais de uma réplica, lock contention, volume insuficiente, latência do polling ou recuperação inconsistente após restart.

#### Adendos

- **2026-08-29T19:30:00-03:00:** decisão documental aceita; testes operacionais ficam bloqueados até a implementação Railway.

### FL-20260829-TEAM-018 — Publicar primeiro somente o replanejamento 2.0 na main

- **Timestamp:** 2026-08-29T20:00:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** André
- **Participantes:** André; Codex como integrador e recorder
- **Categoria:** Git/integration | scope | coordination
- **Escopo:** `main`, documentação 2.0, branch `codex/andre-dashboard-pitch@cc24c7a`
- **Links:** `docs/plans/system-plan.md` v2.0.0, `docs/plans/people/*.md`, `docs/plans/linear-preview.md`, `docs/plans/deployment-vercel-railway.md`
- **Supersedes / superseded by:** complementa `FL-20260829-ANDRE-006`; não muda DEC-015..017

#### Contexto e pergunta

O replanejamento estava visível apenas na branch do André. André pediu que o time recebesse imediatamente na `main` o que precisa refazer, mas restringiu a publicação às documentações novas.

#### Decisão

Publicar na `main` somente README e `docs/`: plano geral, quatro projeções individuais, diagramas, runbook, preview Linear e Flight Log. Não publicar neste commit protótipo, schemas, fixtures, OpenAPI nem validator. Marcar contratos v3 como `FROZEN SPEC / IMPLEMENTATION PENDING` e apontar o draft executável `cc24c7a`, evitando representar a main como já migrada.

#### Critérios e por que agora

O time precisa mudar de direção antes de continuar implementando a API anterior. Separar coordenação de implementação reduz o diff na main e mantém ownership/review dos contratos e código com seus responsáveis.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Manter tudo só na branch | nenhum risco à main | time não vê novo escopo por padrão | FACT: André pediu visibilidade na main | rejeitada |
| Merge completo da branch | mocks disponíveis imediatamente | mistura protótipo/contratos não implementados e aparenta migração concluída | gate: branch é handoff, não produto merge-ready | adiada |
| Commit somente documental | comunica owners/tarefas e preserva código atual | divergência temporária plano↔implementação precisa estar explícita | change control permite plano primeiro | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `main@f1f0d84` contém a implementação anterior e decisões DEC-013/014 preservadas.
- **FACT:** draft executável e gates permanecem no commit `cc24c7a` da branch do André.
- **TEST:** checagem de links, IDs e diff documental será executada antes do push.
- **UNKNOWN:** ordem exata em que as microtarefas v3 serão integradas; o caminho crítico está no preview.

#### Trade-offs aceitos

- **Ganhamos:** fonte de verdade e to-dos visíveis para todos sem incorporar código prematuro.
- **Abrimos mão de:** mocks v3 imediatamente presentes na main.
- **Dívida/limitação:** plano e implementação divergem de forma deliberada e rotulada até as tasks v3.
- **Risco residual:** alguém implementar contra a API antiga; cabeçalhos nos planos e status dos contratos mitigam.

#### Consequências e propagação

- **Git:** um commit documental direto na main; branch do André permanece intacta.
- **Pessoas:** cada plano explica o novo trabalho e onde consultar os drafts.
- **Linear:** continua `NOT RUN` até confirmação explícita do preview 2.0.
- **Integração:** contratos/código entram depois por branches curtas e gates próprios.

#### Validação e trial by fire

- **Hipótese verificável:** ao abrir a main, cada pessoa identifica sua mudança sem concluir que API v3 já funciona.
- **Caminho feliz:** system plan → people plan → preview Linear → draft branch quando necessário.
- **Caso difícil/adverso:** procurar schema v3 na main; documentação informa que ainda está no commit `cc24c7a`.
- **Resultado observado:** NOT RUN neste registro.
- **Fallback:** reverter apenas o commit documental se houver inconsistência; branch fonte permanece recuperável.

#### Gatilhos de revisão

Primeira microtarefa v3 integrada, sincronização do Linear, alteração do contrato ou mudança de estratégia de deploy.

#### Adendos

- **2026-08-29T20:00:00-03:00:** publicação limitada por pedido explícito de André; nenhum arquivo fora de README/docs entra no commit.

### FL-20260829-TEAM-019 — Sincronizar o Linear 2.0 sem reescrever trabalho concluído

- **Timestamp:** 2026-08-29T19:44:45-03:00
- **Status:** VALIDATED
- **Decision owner:** André
- **Participantes:** André; Codex como integrador e recorder
- **Categoria:** planning | coordination | change control
- **Escopo:** projeto Linear `Lumen — Yuno Hackathon`, 21 issues afetadas pelo replanejamento 2.0
- **Links:** `docs/plans/system-plan.md` v2.0.0, `docs/plans/linear-preview.md`, `docs/plans/people/*.md`, `LUM2-4`, `LUM2-9`–`14`, `LUM2-23`, `LUM2-25`, `LUM2-39`, `LUM2-41`, `LUM2-42`, `LUM2-49`, `LUM2-56`–`64`
- **Supersedes / superseded by:** encerra o estado `NOT RUN` de sincronização em `FL-20260829-TEAM-018`; não altera DEC-015..017

#### Contexto e pergunta

André confirmou explicitamente o preview 2.0 e autorizou a escrita no Linear com uma condição: se uma issue prevista para atualização já estivesse concluída, preservar o trabalho encerrado e criar uma nova issue descrevendo somente a extensão necessária. A releitura imediatamente anterior à escrita encontrou `TASK-MEM-008 / LUM2-25` em `Done`, diferente do estado que constava no preview.

#### Decisão

Sincronizar descrições e relações apenas das 14 issues ainda abertas ou em andamento; criar seis issues originalmente previstas e uma sétima issue, `TASK-MEM-009 / LUM2-64`, para a extensão transacional que não poderia ser incorporada a `LUM2-25`. Preservar título, descrição, estado e evidências de toda issue `Done`. Escrever relações em uma segunda passagem e reler todo o conjunto afetado antes de considerar a sincronização concluída.

#### Critérios e por que agora

O Linear precisa refletir o plano transaction-first para coordenar implementação paralela, mas uma issue concluída representa evidência histórica de um escopo anterior. Separar a extensão evita transformar retroativamente o Definition of Done de `LUM2-25`, preserva métricas e oferece ao novo trabalho dependências e aceite próprios.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Reabrir e reescrever `LUM2-25` | menos uma issue | invalida o encerramento anterior e mistura evidências de dois escopos | FACT: `LUM2-25` estava `Done` na releitura | rejeitada pela regra confirmada |
| Atualizar `LUM2-25` sem mudar o estado | mantém contagem menor | cria trabalho pendente oculto dentro de uma issue concluída | change control exige estado honesto | rejeitada |
| Preservar `LUM2-25` e criar `LUM2-64` | histórico e aceite ficam rastreáveis | adiciona uma issue e uma dependência ao preflight | alinhada à autorização explícita | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** 54 issues existentes foram preservadas; 14 descrições abertas/em andamento foram atualizadas; `LUM2-58`–`64` foram criadas; total final 61.
- **FACT:** `LUM2-25` permaneceu `Done` e não recebeu alteração de título, descrição ou estado.
- **TEST:** 21/21 issues afetadas foram relidas com team, project, owner, parent, label, state, ID estável e relações; nenhuma divergência foi encontrada.
- **UNKNOWN:** duração real de cada microtarefa; estimativas continuam operacionais e devem ser revistas com evidência de execução.

#### Trade-offs aceitos

- **Ganhamos:** Linear consistente com o plano 2.0, histórico concluído preservado e caminho crítico explícito.
- **Abrimos mão de:** reutilizar um ID concluído para reduzir a quantidade de issues.
- **Dívida/limitação:** o plano documental e o Linear agora estão sincronizados, mas a implementação v3 ainda permanece pendente.
- **Risco residual:** relações podem precisar de ajuste se contratos ou owners mudarem; isso exige novo change control.

#### Consequências e propagação

- **Rogério:** `LUM2-58`–`60` cobrem API transaction-first, worker persistente e deploy Railway.
- **Renato:** `LUM2-61`–`62` cobrem adaptação determinística e samples/tráfego pela API comum.
- **Altoé:** `LUM2-63`–`64` cobrem trace grounded e extensão dos evals transacionais.
- **André:** `LUM2-9`–`14` foram replanejadas e conectadas às novas dependências sem criar issue adicional.
- **Documentação:** plano geral, quatro planos individuais e registro de sincronização passam a citar os IDs reais.

#### Validação e trial by fire

- **Hipótese verificável:** cada pessoa consegue iniciar pelo primeiro item desbloqueado e rastrear produtores, consumidores e bloqueios sem depender do preview local.
- **Caminho feliz:** abrir o plano individual, seguir o ID Linear real e consultar suas relações.
- **Caso difícil/adverso:** uma necessidade nova incide sobre issue `Done`; o padrão aplicado é criar extensão separada, como `LUM2-64`.
- **Resultado observado:** `VALIDATED`; auditoria pós-escrita de 21/21 issues sem divergência.
- **Fallback:** em divergência futura, interromper novas escritas, inventariar o estado e corrigir plano/Linear por uma mudança explicitamente aprovada.

#### Gatilhos de revisão

Issue concluída que receba novo escopo, alteração de owner/contrato, bloqueio incompatível com o caminho crítico ou primeira evidência real que invalide uma estimativa/dependência.

#### Adendos

- **2026-08-29T19:44:45-03:00:** sincronização autorizada pelo usuário, escrita em duas passagens e auditada antes da atualização documental.

### FL-20260829-TEAM-020 — Adotar sidebar e fila de atenção técnica sem fabricar Incident

- **Timestamp:** 2026-08-29T20:53:42-03:00
- **Status:** ACCEPTED
- **Decision owner:** André
- **Categoria:** product | UX | contract
- **Escopo:** `CMP-WEB-001`, `TASK-UI-002..006`, `CTR-TXL-001 v1`, `CTR-INC-001 v1`

#### Decisão e trade-off

Usar uma sidebar com `Input`, `Logs` e `Incidents` no desktop e uma barra inferior no mobile. `UNKNOWN + PIPELINE_FAILED` entra em atenção técnica, mas não recebe `incident_id`, causa ou recommendation até o backend devolver `CTR-INC-001`. A alternativa de converter todo `UNKNOWN` em Incident foi rejeitada porque fabrica causalidade; o custo aceito é explicar separadamente atenção técnica e diagnóstico confirmado.

#### Evidência e validação

- **FACT:** `CTR-TXL-001` permite `UNKNOWN` sem outcome/classification; `CTR-INC-001` exige diagnóstico/evidência próprios.
- **VALIDAÇÃO:** unit/contract, lint, typecheck e build do frontend passam; browser live continua gate separado.

### FL-20260829-TEAM-021 — Publicar `web/` na main como superfície compartilhada de integração

- **Timestamp:** 2026-08-29T22:06:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** André
- **Categoria:** integration | ownership | delivery
- **Escopo:** `CMP-WEB-001`, `web/`, `TASK-UI-002..006`, `CTR-TXN-001 v1`, `CTR-TXL-001 v1`, `CTR-API-001 v3`
- **Links:** `origin/main@103073b`, `FL-20260829-TEAM-020`, `DEC-021`

#### Contexto e decisão

André pediu que o time visse e integrasse o frontend no repositório comum. A main já contém API/worker/fixtures transaction-first, mas não a pasta `web/`. Publicar a única pasta `web/` evita uma cópia paralela e mantém os mocks como modo explícito; não marca a interface como deployed/live.

#### Alternativas e consequências

| Alternativa | Resultado | Decisão |
| --- | --- | --- |
| Esperar Railway/Vercel | reduz risco de deploy, mas bloqueia colaboração | rejeitada por pedido explícito |
| Criar segunda pasta de frontend | duplica código e lockfile | rejeitada |
| Publicar `web/` sobre a main v3 | compartilhamento imediato, live acceptance pendente | escolhida |

- **FACT:** a main remota possui batch/list/detail e `GET /incidents?transaction_id`; o consumidor foi alinhado e não envia `correlation_id`.
- **VALIDAÇÃO:** build, lint, typecheck, testes e contract validation são obrigatórios antes do push; browser, Railway, CORS e Vercel continuam bloqueios de `LUM2-10..13`.

#### Adendo de integração

- **2026-08-29:** `code-review-gate` aprovou a publicação sem achado bloqueante no diff; `browser-acceptance-gate` permanece bloqueado pela política local de navegação para localhost. `integration-contract-guardian` classificou a promoção como `READY WITH WARNINGS` para preview compartilhado: formulário/client v3 alinhado a `transaction_id`, enquanto Logs, Detail e Incidents continuam fixture-backed até `LUM2-12`. Não declarar `LUM2-10`, `LUM2-11` ou `LUM2-12` concluídas.

### FL-20260829-TEAM-022 — Integrar os incrementos de Incident sobre o frontend 2.1.0

- **Timestamp:** 2026-08-29T22:45:47-03:00
- **Status:** ACCEPTED
- **Decision owner:** Rogério
- **Participantes:** Rogério; Codex como integrador e recorder
- **Categoria:** Git/integration | contract | quality
- **Escopo:** `feat/OBJ-ROGERIO-001-platform-core`, `CTR-INC-001 v1`, `CMP-INC-001`, `CMP-WEB-001`, plano geral 2.1.1
- **Links:** `FL-20260829-ROGERIO-007`, `FL-20260829-ROGERIO-008`, `FL-20260829-ROGERIO-009`, `FL-20260829-TEAM-021`, `docs/plans/system-plan.md`
- **Supersedes / superseded by:** não aplicável; preserva o frontend publicado em 2.1.0 e integra adendos de Incident.

#### Contexto e pergunta

A `main` recebeu quatro commits de frontend após a primeira simulação da branch de Rogério. O novo merge encontrou conflitos textuais nos planos; código, schemas e testes se uniram automaticamente. Era necessário escolher se o plano de frontend seria substituído pelo plano 2.0.5 da branch ou se ambos os incrementos seriam preservados.

#### Decisão

Manter o frontend 2.1.0 e integrar os incrementos de Incident como 2.1.1: hipóteses ordenadas, `recommendation_class` humana, buckets por moeda e fingerprint causal exato. Preservar as entradas do Flight Log e não promover os mocks de `web/` a adapter live.

#### Critérios e por que agora

O usuário autorizou o push para a `main`; aceitar o plano antigo da branch removeria a evidência e as fronteiras da superfície `web/` já integrada. A versão 2.1.1 mantém a fonte de verdade arquitetural monotônica e descreve o estado publicado.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Aceitar o plano 2.0.5 da branch | resolução curta | regride a documentação e o handoff de `web/` 2.1.0 | FACT: `origin/main` contém o frontend e o plano 2.1.0 | perderia estado integrado |
| Omitir os incrementos de Incident | evita conflito documental | descarta código e contratos testados | TEST: merge de código é limpo | contraria o push autorizado |
| Preservar 2.1.0 e publicar 2.1.1 | mantém ambos os incrementos rastreáveis | exige resolver documentação e revalidar a união | TEST: merge-tree só conflitou nos planos | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `origin/main@f5f6e0c` e a branch divergem em quatro commits cada desde `103073b`.
- **TEST:** a simulação anterior da branch passou 97 testes; a validação do merge atualizado será executada antes do push.
- **ASSUMPTION:** `web/` continua em fixtures até `LUM2-12`, conforme plano 2.1.0.
- **UNKNOWN:** o adapter live do frontend permanece fora deste merge.

#### Trade-offs aceitos

- **Ganhamos:** contratos de Incident e frontend compartilham a mesma `main` sem apagar evidência.
- **Abrimos mão de:** uma resolução automática de documentação.
- **Dívida/limitação:** o OpenAPI ainda não tipa explicitamente o envelope da listagem filtrada por `transaction_id`.
- **Risco residual:** o adapter live deve tratar as extensões opcionais de `CTR-INC-001` ao substituir fixtures.

#### Consequências e propagação

- **Produto/demo:** UI preserva mocks explícitos; Incident ganha informação adicional sem ação automática.
- **Arquitetura/contratos:** `CTR-INC-001 v1` permanece compatível por campos aditivos; `CTR-API-001 v3` não muda.
- **Pessoas/branches:** André consome os novos campos quando presentes; Altoé mantém memória separada da causa atual.
- **Plano/Linear:** plano geral e plano de André passam a apontar para 2.1.1; Linear não foi alterado.
- **Testes/observabilidade:** Python, contratos, checagens de diff e testes/build do frontend precisam passar antes do push.

#### Validação e trial by fire

- **Hipótese verificável:** o merge preserva os testes Python e o build/testes do frontend sem marcadores de conflito.
- **Caminho feliz:** API devolve incidentes compatíveis e `web/` continua compilando contra seus mocks.
- **Caso difícil/adverso:** uma causa `INCONCLUSIVE` com precedentes permanece inconclusiva, e moedas distintas não recebem ranking comum.
- **Resultado observado:** NOT RUN no momento deste registro.
- **Fallback:** abortar o merge antes do commit; as duas branches permanecem recuperáveis.

#### Gatilhos de revisão

Falha de contratos/testes, consumidor que rejeite campo opcional, ou adapter live que precise de um envelope estável para `/incidents?transaction_id` exige novo change control.

#### Adendos

- **2026-08-29T22:45:47-03:00:** a primeira validação do frontend falhou porque o parser estrito rejeitou `root_cause.alternatives`. A integração adicionou tipos, parser, fixtures e apresentação das extensões opcionais. Também separou `listIncidents()` de `listTransactionIncidents(transactionId)`, pois a rota filtrada devolve `IncidentDetail[]`, não `Incident[]`. PASS após correção: `python -m pytest -q` (105), `python scripts/validate_contracts.py`, `python -m compileall -q app`, `npm run lint`, `npm test` (27) e `npm run build`. O browser local do Codex não conectou durante a validação anterior; este gate fica `PASS WITH LIMITATIONS`, sem alegar interação visual.

### FL-20260829-TEAM-023 — Integrar primeiro o adapter determinístico antes de concluir o tráfego de fundo

- **Timestamp:** 2026-08-29T22:56:44-03:00
- **Status:** ACCEPTED
- **Decision owner:** Team
- **Participantes:** solicitante; Codex como executor
- **Categoria:** Git/integration | contract | operations
- **Escopo:** `LUM2-61` / `TASK-DATA-008`, `LUM2-62` / `TASK-DATA-009`, `CMP-DATA-001`, `CMP-TXN-001`, `CTR-TXN-001 v1`, `CTR-EVT-001 v1`
- **Links:** `docs/plans/system-plan.md` v2.0.0, branch `RENATO_CONTINUCAO_ROGERIO`, `app/worker/transaction_worker.py`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

A branch `RENATO_CONTINUCAO_ROGERIO` foi atualizada por fast-forward até `origin/main` em worktree isolado para preservar alterações locais de outras frentes. No Linear, `LUM2-62` ainda está Todo, mas já possui uma implementação de submissão batch na main e é bloqueada por `LUM2-61`. O worker revela que seu outcome atual é um placeholder; a pergunta era qual item assumir sem conflitar com `LUM2-47`, que foi explicitamente excluída pelo solicitante.

#### Decisão

Executar apenas `LUM2-61`: substituir o placeholder por um adapter puro e determinístico de `TransactionInput` para outcome e evento `CTR-EVT-001`, preservando os contratos v1. Revalidar `LUM2-62` depois, sem marcá-la como concluída antes de seus critérios dependerem do adapter.

#### Critérios e por que agora

`LUM2-61` é urgente, é pré-requisito explícito de `LUM2-62`, e fornece a fronteira mínima para que worker, tráfego interno e analytics usem o mesmo dado derivado. `LUM2-47` não será tocada por instrução do solicitante.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Marcar `LUM2-62` Done só porque o commit já está na main | Atualiza o board rapidamente | Mantém outcome placeholder e não satisfaz a dependência | FACT: `LUM2-62` é bloqueada por `LUM2-61` no Linear | Critérios ainda não estão completos |
| Trabalhar em `LUM2-47` | Benchmark isolado | Contraria exclusão explícita e a issue aparece já concluída/reatribuída | FACT: instrução do solicitante e estado Linear | Rejeitada |
| Implementar `LUM2-61` primeiro | Desbloqueia o caminho crítico | Atravessa adapter e worker e requer testes de contrato | FACT: docstring do worker declara o placeholder | Escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `RENATO_CONTINUCAO_ROGERIO` foi atualizada de `789f5f1` para `f5f6e0c` e publicada sem tocar o worktree principal sujo.
- **FACT:** `LUM2-61` está Todo, prioridade Urgent, e bloqueia `LUM2-62`.
- **TEST:** NOT RUN — testes do adapter e integração serão executados antes de atualizar o Linear.
- **UNKNOWN:** a abrangência dos evals downstream de `LUM2-56/57`; permanece fora desta microtarefa.

#### Trade-offs aceitos

- **Ganhamos:** ordem de integração explícita e outcome reproduzível para cada input persistido.
- **Abrimos mão de:** fechar imediatamente uma issue cuja primeira metade já foi integrada.
- **Dívida/limitação:** o adapter usa os perfis sintéticos versionados; calibração com dados de produção continua fora do MVP.
- **Risco residual:** uma falha de ingestão de evento deve ser tratada como falha técnica do pipeline, nunca como decline.

#### Consequências e propagação

- **Arquitetura/contratos:** não há mudança de schema; `CTR-TXN-001 v1` passa a alimentar `CTR-EVT-001 v1` no worker.
- **Pessoas/branches:** Renato recebe o handoff de adapter implementado; Rogério pode consumir a mesma interface no lifecycle.
- **Plano/Linear:** atualizar somente `LUM2-61` após review, testes e integração; reavaliar `LUM2-62` depois.
- **Testes/observabilidade:** provar determinismo, três estados terminais, contrato de evento e reentrega idempotente.

#### Validação e trial by fire

- **Hipótese verificável:** o mesmo input/seed/contexto produz payload idêntico e o worker persiste um evento válido uma única vez.
- **Caminho feliz:** transaction batch chega a terminal com outcome, classificação e evento canônico derivado.
- **Caso difícil/adverso:** input inválido continua bloqueado na borda; reentrega não duplica evento; erro técnico não se torna decline.
- **Resultado observado:** NOT RUN.
- **Fallback:** preservar a classificação `PIPELINE_FAILED`/`UNKNOWN` do worker para falhas técnicas.

#### Gatilhos de revisão

Mudança em `CTR-TXN-001`/`CTR-EVT-001`, requisito de retry público, ou falha de idempotência exige change control e nova decisão.

#### Adendos

- **2026-08-29T23:05:00-03:00:** PASS — `python -m pytest -q` aprovou 100 testes; `python scripts/validate_contracts.py`, `python -m compileall -q app` e `git diff --check` passaram. Code review gate: PASS, sem achados bloqueantes.
- **2026-08-29T23:05:00-03:00:** Browser acceptance PASS — Swagger local submeteu batch sintético (`202`) e consultou o registro (`200`) em `COMPLETE`, com `FAILED`, `PROVIDER_INTERNAL_ERROR` e classificação `PROVIDER_ERROR`; console sem erros. Servidor local encerrado após o smoke.

### FL-20260830-TEAM-024 — Consolidar as lanes A+B com correlação e conclusão terminal atômicas

- **Timestamp:** 2026-08-30T00:48:49-03:00
- **Status:** ACCEPTED
- **Decision owner:** Team (solicitante autorizou integração e publicação)
- **Participantes:** André; Rogério; Codex como integrador e recorder
- **Categoria:** architecture | integration | data | deploy | quality
- **Escopo:** `CTR-AGG-001 v1`, `CTR-INC-001 v1`, `CTR-TDI-001 v1`, worker DuckDB, Docker/uv/Neo4j, frontend live
- **Links:** `docs/plans/system-plan.md` v2.2.1; `FL-20260830-ROGERIO-010`; `FL-20260830-ANDRE-001`
- **Supersedes / superseded by:** complementa a recuperação 2.2; não altera contratos públicos.

#### Contexto e pergunta

Depois de Pessoa A publicar o pipeline grounded na `main`, a integração com a lane web revelou três falhas internas: janelas podiam misturar correlações no mesmo bucket/slice; a transação que disparava a janela ainda não estava classificada quando os links eram derivados; e a imagem Docker não instalava o extra Neo4j pelo `uv.lock`. A pergunta foi como corrigir essas fronteiras sem mudar schemas ou endpoints congelados.

#### Decisão

Isolar `WindowMetrics` por `correlation_id`; executar canonical → analytics → Incident → link → record terminal em uma única transação DuckDB protegida pelo lock compartilhado; em falha, fazer rollback antes de persistir `UNKNOWN/PIPELINE_FAILED`; e construir a imagem com `uv sync --frozen --no-dev --extra neo4j`. O frontend permanece consumidor puro de `CTR-API-001 v3`; deploy e browser online só serão declarados após prova real.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência | Decisão |
| --- | --- | --- | --- | --- |
| Agrupar somente por bucket/slice | menos grupos | mistura lotes independentes e pode vazar evidência | revisão reproduziu correlações distintas no mesmo bucket | rejeitada |
| Finalizar record antes de analytics | fluxo mais simples | transação gatilho não recebe o Incident; falha deixa estado parcial | E2E exigiu vínculo da última transação | rejeitada |
| Compensação após commits separados | reduz duração da transação | recuperação complexa e estado canônico/link divergente | teste de falha observou side effects parciais | rejeitada |
| Transação DuckDB única + lock | visibilidade atômica e rollback verificável | mantém lock durante analytics e reduz concorrência local | worker é deliberadamente single-process para a demo | escolhida |
| `pip install` sem lock/extra | Dockerfile menor | drift e Neo4j configurado sem driver | `uv.lock` é padrão do projeto | rejeitada |

#### Evidência, trade-offs e validação

- **FACT:** contratos públicos permanecem byte-compatible; as mudanças são de agrupamento, ordem transacional e empacotamento.
- **TEST:** testes focados de aggregation/worker/E2E/deploy passaram (21); suite completa, imagem Docker e smoke live serão repetidos antes do push.
- **Trade-off aceito:** o lock cobre mais trabalho, adequado à réplica única/DuckDB do MVP; escala multi-worker exigirá outra arquitetura.
- **UNKNOWN:** Railway Volume/restart/CORS e Vercel ainda dependem do ambiente deployed.
- **Resultado observado:** PENDING para os gates finais e publicação; um adendo registrará SHA, testes e validação online.

#### Adendo operacional

- **2026-08-30T00:55:00-03:00:** o primeiro smoke da imagem revelou health `503` porque `/data` não existia sem um Volume montado. A imagem passou a criar o diretório, enquanto Railway continua montando armazenamento durável no mesmo path. Essa correção não substitui o teste de persistência/restart no serviço real.
- **2026-08-30T01:00:00-03:00:** a revisão final alinhou três contratos operacionais sem mudar a API pública: `NEXT_PUBLIC_API_BASE_URL` deve terminar em `/v1`; `NEO4J_DATABASE` passa a ser consumido tanto pelo bootstrap quanto pelo runtime; e retries sem client configurado preservam o erro em vez de entrar em loading infinito.
- **2026-08-30T01:03:00-03:00:** a mesma revisão identificou risco de somar `amount_minor` entre moedas no mesmo bucket. `currency` passou a integrar o slice de agregação, baseline, candidato e Incident, e o vínculo exige a mesma moeda. A identidade do candidato também inclui janela e slice. O custo aceito é fragmentar amostras por moeda; a alternativa de FX implícito permanece proibida.
- **2026-08-30T01:02:30-03:00:** o browser gate expôs `UNKNOWN/PIPELINE_FAILED/FileNotFoundError` porque a imagem não continha `config/`. O Docker passou a copiar o catálogo/configuração do simulator e o smoke live agora rejeita qualquer `UNKNOWN`, estágio diferente de `COMPLETE` ou outcome ausente; atingir apenas um estado terminal deixou de ser evidência suficiente.

#### Adendo de evidência final

- **2026-08-30T01:03:17-03:00:** PASS local — 174 testes Python; contratos/OpenAPI, `compileall`, `uv lock --check`, lint e build Next passaram; imagem Python 3.14.4 foi construída com lock/Neo4j/config e health `200`; suite web live passou 35/35 exigindo `COMPLETE` e outcome. O browser real confirmou sample → submit → log `FAILED` de negócio/`COMPLETE` → detalhe `NO_INCIDENT`, lista de Incidents, memória `MATCH_FOUND` com um candidato e `Fallback: Not used`, layout mobile e console sem warnings/errors. Code review: `PASS WITH NOTES`; guardian: `READY WITH WARNINGS`. Railway Volume/restart/CORS e Vercel/browser deployed permanecem `NOT RUN`.
- **2026-08-30T01:04:43-03:00:** commit integrado `05c61d8` (`fix(integration): harden live incident pipeline`) criado sobre o merge A+B `9be8853`. Push permanece PENDING até o último fetch confirmar que `origin/main` ainda aponta para `23b9061`; force push é proibido.
- **2026-08-30T01:05:20-03:00:** PASS — o fetch anti-race confirmou `origin/main@23b9061`, ancestral de `HEAD`; `git push origin HEAD:main` publicou por fast-forward até `6de8c02`, sem force. Este adendo será publicado em commit documental subsequente; os gates deployed permanecem pendentes.
- **2026-08-30T01:11:12-03:00:** PASS parcial deployed — `origin/main@e50863d`; Railway publicou com health `200` (`duckdb=ready`, worker ready) e a suite web live online passou 35/35, incluindo `COMPLETE`, outcome e ausência de `UNKNOWN`. Vercel reportou deployment concluído, mas o painel autenticado é a única fonte encontrada para o domínio exato; a sessão disponível não está autenticada e `lumen-prep.vercel.app` foi rejeitado porque serve outra aplicação. CORS/allowlist, browser Vercel, Volume após restart e Neo4j sem fallback online permanecem `NOT RUN`. Linear foi reconciliado: `LUM2-10/11/12/41` Done; `LUM2-13/42/57/60` In Progress; `LUM2-14` Todo, todos com comentários de evidência aplicáveis.

#### Gatilhos de revisão

Mais de uma réplica, migração para queue externa/Postgres, mudança de chave de correlação, falha de build com Python 3.14.4 ou divergência remota exige nova decisão e revalidação dos contratos.

### FL-20260830-TEAM-025 — Preservar as seis dimensões até o diagnóstico e usar decline code como evidência, não atalho causal

- **Timestamp:** 2026-08-30T01:40:25-03:00
- **Status:** ACCEPTED
- **Decision owner:** Team
- **Participantes:** André, Altoé, Rogério, Renato; Codex como recorder
- **Categoria:** architecture | contract | data | demo
- **Escopo:** `DEC-025`; `CTR-EVT-001 v2`, `CTR-AGG-001 v2`, `CTR-DET-001 v2`, `CTR-RCA-001 v1`, `CTR-INC-001 v2`
- **Links:** `docs/plans/system-plan.md` §16; `TASK-RCA6-001`–`009`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O enunciado exige merchant, provider, método, país, banco emissor e decline code. A auditoria da `main` encontrou agregação só por provider, país e moeda e RCA incapaz de publicar causa específica. Era preciso decidir como usar os seis dados sem vazar o resultado da recusa para explicar a própria recusa.

#### Decisão

Preservar cinco dimensões pré-resultado em rollups esparsos e produzir `normalized_decline_code` como perfil de evidência do slice anômalo. O RCA usa contribuição e resíduo para separar incidentes, e só promove causa específica quando as evidências qualificadas vencerem; o fallback é `INCONCLUSIVE`.

#### Critérios e por que agora

A perda atual acontece antes do detector, logo UI ou narrativa não podem recuperá-la. A escolha congela nomes, versões e mocks antes de trabalho paralelo e atende o trial by fire com combinações não ensaiadas.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Cube esparso + decline profile | usa todos os dados sem leakage e evita combinações vazias | exige migração e testes de conservação | FACT: eventos carregam os campos | escolhida |
| Agrupar seis chaves como iguais | curto de implementar | decline é outcome e produz circularidade; alta sparsity | FACT: código vem após falha | rejeitada |
| Manter provider/país | preserva código atual | não diagnostica merchant, método ou emissor | FACT: enunciado exige seis | rejeitada |

#### Evidência, hipóteses e desconhecidos

- **FACT:** o desafio requer causa específica na interseção das seis dimensões.
- **TEST:** 20 testes focados da `main` passaram na auditoria, mas não provam a cadeia real das seis dimensões.
- **ASSUMPTION:** `min_support=12` e rollups observados são viáveis; Renato valida em `TASK-RCA6-008`.
- **UNKNOWN:** limiares finais de `SUPPORTED`; até holdout, a saída segura é inconclusiva.

#### Trade-offs aceitos

- **Ganhamos:** diagnóstico auditável e defendível para o júri.
- **Abrimos mão de:** afirmar causa em slices raros ou ambíguos.
- **Dívida/limitação:** v2 e adaptador v1 temporário aumentam a integração.
- **Risco residual:** catálogo sintético pode não cobrir todos os padrões reais; trial by fire e holdout expõem isso.

#### Consequências e propagação

- **Produto/demo:** catálogo com BR/MX/CO, 9 merchants, 4 providers, métodos compatíveis e emissores por país; decline code não é input do usuário.
- **Arquitetura/contratos:** migração planejada no plano §16.
- **Pessoas/branches:** Renato/dados-RCA, Rogério/cube-API, Altoé/grounding e André/UI têm owner único.
- **Plano/Linear:** plano geral e projeções foram atualizados; Linear não foi alterado.
- **Testes/observabilidade:** conservação, não-leakage, resíduo, holdout, E2E e browser são gates.

#### Validação e trial by fire

- **Hipótese verificável:** interseção inédita gera causa específica com evidência ou abstention honesta.
- **Caminho feliz:** provider-BR e emissor-MX em merchant único são separados por contribuição incremental.
- **Caso difícil/adverso:** método/código desconhecido ou baixa amostra.
- **Resultado observado:** NOT RUN — planejamento concluído, implementação pendente.
- **Fallback:** preservar eventos/evidências e exibir `INCONCLUSIVE` com alternativas.

#### Gatilhos de revisão

Benchmark inviável, falha de conservação, leakage por decline code ou holdout com confiança inflada exigem change control.

#### Adendos

- 2026-08-30T01:40:25-03:00 — plano 2.3.0 criado; nenhuma issue Linear foi escrita.

## André

<!-- ANDRE: faça append de novas entradas imediatamente antes da próxima seção. -->

### FL-20260829-ANDRE-001 — Adopt Yuno blue and an Apple-like light UI for the fixture dashboard

- **Timestamp:** 2026-08-29T17:15:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** André (request owner)
- **Participantes:** André; implementation by Codex
- **Categoria:** UX | demo
- **Escopo:** `CMP-UI-001`, `TASK-UI-001`, `app/ui/dashboard.py`
- **Links:** `TASK-UI-001`, `CMP-UI-001`, `docs/plans/people/andre.md`, branch `codex/andre-dashboard-pitch`, [Yuno Brand Guidelines](https://yuno-payments.com/en/brand-guidelines/)
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O shell inicial apresentava o gráfico com roxo desconectado do restante e cópia em português. André pediu interface integralmente em inglês, cores fiéis à Yuno e linguagem visual Apple-like.

#### Decisão

Usar Yuno Blue `#3E4FE0` como cor de dados/ação, Harmony Lilac `#E8EAF5` como superfície informativa e neutros claros com tipografia de sistema, cartões brancos e cantos amplos. Todo texto de interface e o texto visível das fixtures usadas neste shell será apresentado em inglês; IDs e referências técnicas permanecem intactos.

#### Critérios e por que agora

Coerência com a marca, leitura de apresentação e unidade visual do dashboard dominam. O gráfico é parte central da narrativa executiva e não pode parecer um componente de outra aplicação.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Manter dark navy e roxo | Menor mudança de código | Destoa da marca e do feedback visual | FACT: feedback do usuário no gráfico | Não atende ao pedido explícito |
| Usar azul Yuno em UI dark | Mantém contraste do shell anterior | Menos Apple-like e maior densidade visual | ASSUMPTION: o dashboard será projetado em ambiente claro | Não maximiza a direção de design solicitada |
| Superfície clara Apple-like com azul Yuno | Coerente, legível e focaliza o incidente | Menos adequada para salas muito escuras | FACT: Brand Guidelines definem `#3E4FE0` e `#E8EAF5` | Melhor atende à solicitação atual |

#### Evidência, hipóteses e desconhecidos

- **FACT:** as Brand Guidelines oficiais da Yuno definem Yuno Blue `#3E4FE0` e Harmony Lilac `#E8EAF5`.
- **TEST:** NOT RUN no momento do registro; repetir browser acceptance após a implementação.
- **ASSUMPTION:** o shell continuará a usar somente estas duas fixtures até a integração da API.
- **UNKNOWN:** preferência da banca entre ambiente claro e escuro em um projetor específico.

#### Trade-offs aceitos

- **Ganhamos:** unidade visual, legibilidade e consistência de marca.
- **Abrimos mão de:** contraste OLED do shell anterior.
- **Dívida/limitação:** a tradução é localizada para as fixtures deste shell; a API integrada deverá prover copy de apresentação em inglês.
- **Risco residual:** contraste em um projetor com brilho muito baixo; validar no ensaio.

#### Consequências e propagação

- **Produto/demo:** a narrativa fica integralmente em inglês e mais coesa no pitch.
- **Arquitetura/contratos:** nenhuma alteração em `CTR-INC-001` ou fixtures.
- **Pessoas/branches:** Rogério deve preservar identificadores e referências se trocar a fixture por API.
- **Plano/Linear:** nenhum estado de Linear é alterado.
- **Testes/observabilidade:** browser acceptance deve cobrir gráfico, impacto, evidência e responsividade.

#### Validação e trial by fire

- **Hipótese verificável:** a tela e o gráfico compartilham a mesma linguagem visual e permanecem legíveis em desktop e mobile.
- **Caminho feliz:** incidente, gráfico, impacto e evidência aparecem em inglês e sem console errors.
- **Caso difícil/adverso:** fixture indisponível mantém mensagem de erro visível; viewport 375 px não gera overflow.
- **Resultado observado:** NOT RUN no momento do registro.
- **Fallback:** a fixture local continua marcada como demo mode sem backend.

#### Gatilhos de revisão

Feedback de baixa legibilidade em projetor, novas Brand Guidelines ou integração com uma API que forneça copy localizado.

#### Adendos

- **2026-08-29T17:25:00-03:00:** browser acceptance em `127.0.0.1:8505` confirmou incidente, gráfico, impacto e evidência em inglês; console limpo e viewport móvel sem overflow.

### FL-20260829-ANDRE-002 — Adopt the dark electric-blue event identity for the dashboard

- **Timestamp:** 2026-08-29T17:40:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** André (request owner)
- **Participantes:** André; implementation by Codex
- **Categoria:** UX | demo
- **Escopo:** `CMP-UI-001`, `TASK-UI-001`, `app/ui/dashboard.py`
- **Links:** `TASK-UI-001`, `CMP-UI-001`, branch `codex/andre-dashboard-pitch`, user-supplied event reference image
- **Supersedes / superseded by:** supersedes `FL-20260829-ANDRE-001`

#### Contexto e pergunta

No mobile, a superfície clara criou encaixes confusos, contraste insuficiente no aviso de demo e textos próximos aos limites. André forneceu uma referência escura, preta e azul elétrica e exigiu validação de padding, margens, contraste, contenção e overflow.

#### Decisão

Adotar hero dark com blue glow elétrico e textura técnica discreta; cartões escuros translúcidos; badge de demo de alto contraste; padding explícito no container real do Streamlit, no card e nas métricas; quebra de texto e clipping para os componentes críticos.

#### Critérios e por que agora

Fidelidade à referência, leitura em mobile e contenção do conteúdo dominam. A UI do pitch não pode depender do espaçamento padrão do framework.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Ajustar apenas o padding claro | Menor diff | Mantém contraste e identidade desalinhados | FACT: comentários do usuário | Não atende ao briefing |
| Dark genérico sem textura | Simples | Perde a linguagem visual fornecida | FACT: imagem possui gradientes/padrão técnico | Não reproduz a intenção |
| Dark elétrico com guardrails | Coerência e leitura | CSS mais específico ao Streamlit | TEST de browser | Melhor equilíbrio |

#### Evidência, hipóteses e desconhecidos

- **FACT:** screenshots apontam sobreposição, baixo contraste e falta de respiro.
- **TEST:** validação de browser concluída no adendo abaixo.
- **ASSUMPTION:** CSS sem ativo externo evoca a referência sem copiar seus assets.
- **UNKNOWN:** comportamento em projetor físico; validar no ensaio.

#### Trade-offs aceitos

- **Ganhamos:** contraste, hierarquia e aderência ao briefing.
- **Abrimos mão de:** a paleta clara Apple-like anterior.
- **Dívida/limitação:** seletores internos do Streamlit podem exigir revisão após upgrade.
- **Risco residual:** glow pode ser sutil em telas ruins, mas o texto continua legível sem ele.

#### Consequências e propagação

- **Produto/demo:** hero e componentes passam a compartilhar a identidade visual.
- **Arquitetura/contratos:** nenhuma alteração de contrato ou fixture.
- **Pessoas/branches:** não afeta backend.
- **Plano/Linear:** nenhum estado externo alterado.
- **Testes/observabilidade:** acceptance mede contraste, margens, bounds e overflow.

#### Validação e trial by fire

- **Hipótese verificável:** nenhum texto vaza ou se sobrepõe e os elementos críticos preservam contraste.
- **Caminho feliz:** hero, incidente, métricas, gráfico, impacto e evidência permanecem nos cartões.
- **Caso difícil/adverso:** viewport estreito, título longo e badge de demo sem clipping ou overflow.
- **Resultado observado:** PASS no adendo abaixo.
- **Fallback:** remover somente a textura decorativa, preservando contraste e espaçamento.

#### Gatilhos de revisão

Falha em mobile, baixo contraste observado, mudança do Streamlit ou novo feedback visual.

#### Adendos

- **2026-08-29T17:55:00-03:00:** browser acceptance em `127.0.0.1:8508` confirmou 48 px de padding lateral desktop, 32 px no card e 18,4 px nas métricas; zero containers fora dos bounds, sem overflow horizontal, evidência expansível e console limpo. Viewport móvel também registrou zero containers/textos fora dos limites.
- **2026-08-29T18:08:00-03:00:** correção estrutural em `127.0.0.1:8512` removeu o estilo dos wrappers técnicos do Streamlit e substituiu o incidente/status por exatamente dois cards explícitos. Browser acceptance em 375, 768, 1221 e 1440 px registrou zero cards aninhados, zero elementos fora do content box, zero textos fora do card, `scrollWidth == viewport`, drill-down funcional, interface em inglês e console limpo. Contraste calculado: badge 16,38:1, texto secundário 9,65:1 e texto principal 18,6:1. Code review sem achados bloqueantes; `py_compile`, assertions dos formatadores e `git diff --check` passaram.
- **2026-08-29T17:52:15-03:00:** refinamento de spacing em `127.0.0.1:8514` removeu alturas mínimas dos cards, padronizou alinhamento à esquerda/centro vertical e preservou 16 px entre cards adjacentes. Browser acceptance em 375, 593, 768, 1024 e 1440 px confirmou alturas naturais conforme o conteúdo, zero overflow, zero nesting, 16 px de inset nas três evidências, touch target de 45,4 px, foco visível, conteúdo expandido contido e console limpo. Code review `PASS`; `py_compile`, assertions e `git diff --check` passaram.

### FL-20260829-ANDRE-003 — Expor o limite causal e o fallback local como estados explícitos da demo

- **Timestamp:** 2026-08-29T18:05:46-03:00
- **Status:** ACCEPTED
- **Decision owner:** André (request owner)
- **Participantes:** André; implementation by Codex
- **Categoria:** UX | demo | quality
- **Escopo:** `TASK-UI-001`, `CMP-UI-001`, `app/ui/dashboard.py`
- **Links:** `TASK-UI-001` / `LUM2-8`, `CTR-INC-001`, branch `codex/andre-dashboard-pitch`, `incident-inconclusive-with-precedent.json`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O shell mostrava `status: live` embora estivesse isolado em fixtures locais, e o estado `INCONCLUSIVE` previsto no contrato não possuía uma apresentação demonstrável.

#### Decisão

Declarar o fallback local no hero e renderizar `INCONCLUSIVE` com status visual distinto e mensagem explícita de que o precedente orienta a investigação, mas não confirma a causa atual. Expor o caso real já versionado por `?fixture=inconclusive`, sem backend, schema novo ou fixture inventada.

#### Critérios e por que agora

Honestidade operacional e a capacidade de demonstrar o no-answer do MVP têm prioridade sobre uma aparência de produção que a tela não possui.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Manter `live` e apenas mudar a cor | Menor diff | Mantém uma afirmação operacional falsa | FACT: a tela usa somente fixtures | Não atende ao pedido |
| Mostrar `INCONCLUSIVE` apenas por CSS morto | Simples | Não prova o fluxo com dados reais | FACT: fixture inconclusiva existe | Não permite acceptance real |
| Fallback explícito + fixture inconclusiva selecionável | Demonstra os dois estados honestamente | Adiciona uma rota de demo local | TEST pendente | Melhor equilíbrio |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `incident-inconclusive-with-precedent.json` traz `state` e `root_cause.status` iguais a `INCONCLUSIVE`.
- **TEST:** NOT RUN no momento do registro; executar browser acceptance nos dois modos.
- **ASSUMPTION:** o query parameter permanecerá exclusivo do shell local até a integração da API.
- **UNKNOWN:** a convenção final de navegação entre cenários virá em `TASK-UI-002/005`.

#### Trade-offs aceitos

- **Ganhamos:** transparência e prova visual de no-answer.
- **Abrimos mão de:** hero com aparência de operação live.
- **Dívida/limitação:** seleção por URL é mecanismo de demo, não controle final de produto.
- **Risco residual:** um usuário pode abrir a URL inconclusiva sem contexto; o próprio hero informa fallback local.

#### Consequências e propagação

- **Produto/demo:** fallback e limite causal passam a ser visíveis.
- **Arquitetura/contratos:** apenas consome fixtures existentes de `CTR-INC-001`; sem mudança de contrato.
- **Pessoas/branches:** Rogério pode substituir o selector local por `CTR-API-001` sem mudar semântica.
- **Plano/Linear:** `LUM2-8` recebe evidência complementar, sem alterar dependências.
- **Testes/observabilidade:** validar default e `?fixture=inconclusive`, além de console e responsividade.

#### Validação e trial by fire

- **Hipótese verificável:** os estados `SUPPORTED` e `INCONCLUSIVE` são legíveis e o fallback nunca parece uma conexão live.
- **Caminho feliz:** abrir a fixture padrão e a inconclusiva, conferindo status e mensagem.
- **Caso difícil/adverso:** parâmetro desconhecido mantém o fallback padrão sem buscar recursos externos.
- **Resultado observado:** NOT RUN no momento do registro.
- **Fallback:** parâmetro ausente ou desconhecido exibe a fixture suportada.

#### Gatilhos de revisão

Integração de `CTR-API-001`, novo estado contratual ou mudança na semântica de no-answer.

#### Adendos

- Nenhum.

### FL-20260829-ANDRE-004 — Mostrar recorrência como evidência comparável, sem esconder a incerteza causal

- **Timestamp:** 2026-08-29T18:30:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** André (request owner)
- **Participantes:** André; implementation by Codex
- **Categoria:** UX | demo
- **Escopo:** `TASK-UI-004` / `LUM2-11`, `CMP-UI-001`, `app/ui/dashboard.py`
- **Links:** `CTR-MEM-001 v1.1`, `CTR-INC-001 v1`, `TASK-MEM-006`, `TASK-UI-003`, `TASK-UI-006`, `FL-20260829-TEAM-011`, `FL-20260829-TEAM-012`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

A tela já apresentava diagnóstico e evidências, mas não explicava ao mesmo tempo a utilidade executiva e o detalhe operacional de um precedente. Era necessário decidir se a recorrência ficaria escondida em uma tela técnica, se os scores ficariam ocultos e como evitar que o playbook histórico parecesse uma ação automática ou uma confirmação da causa atual.

#### Decisão

Adicionar um bloco de recorrência destacado e expansível. Seu resumo mostra o precedente humano, tempo relativo e sinais iguais/diferentes com ícones vetoriais; o detalhe público traz tabela responsiva, scores estruturado e semântico, IDs de evidência e dois CTAs: abrir a comparação e consultar o guia de investigação. Em `INCONCLUSIVE + MATCH`, a copy mantém explicitamente a causa atual inconclusiva. `MEMORY_UNAVAILABLE` aparece como aviso discreto, sem alterar o diagnóstico atual.

#### Critérios e por que agora

Clareza simultânea para executivo e operações, auditabilidade e honestidade causal dominam. A tarefa `TASK-UI-004` existe para entregar essa leitura antes da validação final do dashboard, e os contratos/fixtures necessários já estão congelados.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Esconder recorrência em detalhe técnico | Interface inicial mais curta | Executivo não percebe o valor da memória; comparação fica difícil de demonstrar | FACT: usuário pediu bloco destacado | Não atende à narrativa de demo |
| Mostrar só mensagem e playbook | Implementação curta | Esconde fatores, scores e evidências; aumenta risco de falsa certeza | FACT: CTR-MEM-001 expõe fatores e scores | Não prova groundedness |
| Bloco destacado + detalhe expansível | Atende os dois públicos e preserva rastreabilidade | Adiciona densidade e exige responsividade | FACT: decisão explícita do usuário | Melhor equilíbrio atual |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `CTR-MEM-001 v1.1` distingue `MATCH_FOUND`, `NO_PRECEDENT` e `MEMORY_UNAVAILABLE`; lista vazia não significa falha.
- **FACT:** o usuário escolheu bloco destacado expansível, tabela com resumo visual, CTAs combinados, scores públicos e aviso discreto.
- **TEST:** NOT RUN no momento do registro; executar `py_compile`, code review e browser acceptance nas quatro combinações.
- **ASSUMPTION:** a API final preservará os campos e IDs das fixtures; owner de validação: Rogério ao integrar `CTR-API-001`.
- **UNKNOWN:** o limite ideal de matches simultâneos além do primeiro; o MVP apresenta o top-1 disponível na fixture.

#### Trade-offs aceitos

- **Ganhamos:** leitura imediata da recorrência e profundidade auditável sem esconder os scores.
- **Abrimos mão de:** uma tela inicial minimalista e de uma lista completa de precedentes.
- **Dívida/limitação:** os CTAs são guias locais no shell de fixture, não links para um executor ou mecanismo de decisão.
- **Risco residual:** tabela pode ser densa em telas pequenas; a implementação precisa manter coluna responsiva e validação em mobile.

#### Consequências e propagação

- **Produto/demo:** a demo pode defender por que a recorrência é provável e por que ela não é prova causal.
- **Arquitetura/contratos:** consome, sem alterar, `CTR-INC-001 v1` e `CTR-MEM-001 v1.1`.
- **Pessoas/branches:** Altoé revisa a semântica da memória; Rogério preserva `memory_status` e evidence IDs na API.
- **Plano/Linear:** o plano já atribui autonomia de layout/copy a André; não há mudança de contrato, dependência ou escrita externa no Linear.
- **Testes/observabilidade:** validar match suportado, match inconclusivo, sem precedente, memória indisponível, expansão, CTAs, console e mobile.

#### Validação e trial by fire

- **Hipótese verificável:** uma pessoa identifica em poucos segundos o precedente e distingue similaridade de causa atual; um operador encontra fatores, scores e guia sem perder a evidência.
- **Caminho feliz:** match suportado exibe resumo, comparação e guia `HUMAN_ONLY`.
- **Caso difícil/adverso:** `INCONCLUSIVE + MATCH` não promove a causa; memória indisponível não parece ausência de precedente; tela de 375 px não vaza tabela.
- **Resultado observado:** NOT RUN no momento do registro.
- **Fallback:** fixtures locais versionadas mantêm todos os quatro estados sem Neo4j, API ou executor de playbook.

#### Gatilhos de revisão

API que altere `CTR-MEM-001`, avaliação que mostre confusão entre score e confiança causal, ou feedback de overflow/baixa legibilidade em projetor ou mobile.

#### Adendos

- **2026-08-29T18:42:00-03:00:** browser acceptance em `127.0.0.1:8520` passou para `SUPPORTED + MATCH`, `INCONCLUSIVE + MATCH`, `NO_PRECEDENT` e `MEMORY_UNAVAILABLE`; a comparação expandiu e exibiu ambos os scores, o guia permaneceu `HUMAN_ONLY` e o console ficou sem erros. Em 375 px, os dois controles de recorrência mediram 44 px, a tabela ficou visível, `scrollWidth == clientWidth` e o resumo passou a uma coluna. As assertions focadas de tempo/fatores/mensagem inconclusiva e `git diff --check` passaram. A validação de teclado por `Enter` não abriu o controle no driver do navegador, embora o clique real tenha aberto; o foco visível permanece coberto pelo CSS e deve ser repetido manualmente no ensaio final.

### FL-20260829-ANDRE-005 — Consolidar detalhe e guia dentro do card de recorrência

- **Timestamp:** 2026-08-29T18:50:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** André (request owner)
- **Participantes:** André; implementation by Codex
- **Categoria:** UX | demo
- **Escopo:** `TASK-UI-004` / `LUM2-11`, `CMP-UI-001`, `app/ui/dashboard.py`
- **Links:** `FL-20260829-ANDRE-004`, `CTR-MEM-001 v1.1`, `CTR-INC-001 v1`
- **Supersedes / superseded by:** substitui a decisão de dois CTAs em `FL-20260829-ANDRE-004`; demais decisões permanecem válidas

#### Contexto e pergunta

O review visual mostrou três controles consecutivos para uma única área: botão para abrir, expansível e botão para o guia. Isso fragmentava a leitura e deslocava o detalhe para fora do card de recorrência.

#### Decisão

Remover os dois botões. O expansível é o único controle de abertura e fica dentro do card de recorrência. O guia de investigação `HUMAN_ONLY` aparece ao final do detalhe aberto, próximo dos scores, tabela e evidence IDs.

#### Critérios e por que agora

Reduzir redundância e manter contexto visual sem reduzir auditabilidade. O feedback do usuário identificou diretamente a repetição antes de a UI ser integrada à API.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Manter dois botões | Ações explicitamente nomeadas | Cria passos duplicados e conteúdo fora do card | FACT: review visual do usuário | Rejeitada |
| Mostrar guia sempre no resumo | Menos interação | Aumenta densidade e mistura recomendação com síntese executiva | ASSUMPTION: resumo deve ser escaneável | Rejeitada |
| Um expansível interno com guia no detalhe | Um único ponto de interação e contexto completo | Exige abrir para ver o guia | FACT: escolha explícita do usuário | Escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** o usuário pediu a remoção dos dois botões e o detalhe dentro do card.
- **TEST:** NOT RUN no momento do registro; validar abertura, guia e mobile após a alteração.
- **ASSUMPTION:** o playbook não é a informação primária de um executivo; ele pertence ao detalhe operacional.
- **UNKNOWN:** não aplicável; contratos e dados não mudam.

#### Trade-offs aceitos

- **Ganhamos:** leitura mais direta e card autocontido.
- **Abrimos mão de:** atalho visível para o guia sem abrir detalhes.
- **Dívida/limitação:** nenhuma além da expansão intencional.
- **Risco residual:** o usuário pode não abrir o detalhe; o resumo continua dizendo que há playbook a validar.

#### Consequências e propagação

- **Produto/demo:** a recorrência vira uma única unidade visual expansível.
- **Arquitetura/contratos:** nenhum contrato muda.
- **Pessoas/branches:** não altera API, memória ou schema.
- **Plano/Linear:** o plano já permite decisão local de layout; sem escrita externa.
- **Testes/observabilidade:** validar remoção dos botões, expansão e guia no card em mobile.

#### Validação e trial by fire

- **Hipótese verificável:** o usuário abre um único expansível e encontra comparação e guia sem sair do card.
- **Caminho feliz:** abrir detalhe → ver scores/tabela → ler guia `HUMAN_ONLY`.
- **Caso difícil/adverso:** 375 px mantém todo conteúdo contido após expansão.
- **Resultado observado:** NOT RUN.
- **Fallback:** conteúdo permanece disponível por fixture quando a API/memória não estiverem integradas.

#### Gatilhos de revisão

Feedback de que o guia ficou difícil de descobrir ou que o card perdeu legibilidade em mobile.

#### Adendos

- **2026-08-29T18:58:00-03:00:** browser acceptance em `127.0.0.1:8520` confirmou zero botões `Open detailed comparison`/`View the investigation guide`; abrir o único expansível mostrou scores, tabela e guia `HUMAN_ONLY`. Em 483 px, `scrollWidth == clientWidth`, o guia permaneceu dentro do detalhe e o console não registrou erros. Sintaxe e `git diff --check` passaram.

### FL-20260829-ANDRE-006 — Rebasear o replanejamento sobre a main integrada antes de publicar

- **Timestamp:** 2026-08-29T19:45:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** André
- **Participantes:** André; Codex como integrador e recorder
- **Categoria:** Git/integration | quality | scope
- **Escopo:** branch `codex/andre-dashboard-pitch`, `origin/main@f1f0d84`, plano 2.0, contracts e validator
- **Links:** `DEC-015`–`017`, `scripts/validate_contracts.py`, `docs/plans/linear-preview.md`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

Antes do push, o fetch mostrou que a branch de André estava 80 commits atrás da main, que já continha runtime, ingestion, aggregation, detection, simulation, incidents, memory, API e Docker, além de `DEC-013/014` oficiais. Publicar sem integrar apagaria contexto e criaria colisões de IDs.

#### Decisão

Commitar a mudança recuperável, rebasear sobre `origin/main@f1f0d84`, resolver conflitos preservando as decisões e módulos publicados e atualizar o validador oficial para incluir todos os contratos 2.0. A branch é `READY TO HAND OFF`, não `READY TO MERGE` como produto completo: a implementação existente ainda expõe o fluxo v1/v2 e precisa das novas microtarefas.

#### Critérios e por que agora

O push precisava carregar o trabalho atual do time e uma diferença pequena/explicável sobre a main. O rebase antes da publicação evita pedir que cada colega reconcilie uma base obsoleta.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Push da base antiga | imediato | 80 commits de divergência e decisões sobrescritas | FACT: `git rev-list` mostrou `80 0` | insegura |
| Merge commit sem revisar conflitos | preserva ancestrais | plano duplicado e IDs colididos | FACT: main já possuía DEC-013/014 | insuficiente |
| Rebase com resolução e gates | branch linear e base atual | exige reconciliar planos/testes | evidência Git e contratos | escolhido |

#### Evidência, hipóteses e desconhecidos

- **FACT:** rebase concluiu sobre `f1f0d84`; 33 IDs de Flight Log são únicos.
- **TEST:** contract validator passou todos os schemas/fixtures/OpenAPI; 53 testes passaram em Python 3.12.13.
- **TEST:** 1 teste de ambiente falhou porque exige Python 3.14.4; não é falha funcional observada.
- **UNKNOWN:** runtime/deploy 3.14.4 e browser Vercel → Railway ainda não foram executados nesta branch.

#### Trade-offs aceitos

- **Ganhamos:** base atual, decisões preservadas e validação central completa.
- **Abrimos mão de:** declarar a branch pronta para merge do produto antes da implementação v3.
- **Dívida/limitação:** repetir suíte em Python 3.14.4 e browser gate quando frontend/worker existirem.
- **Risco residual:** código v1/v2 e contrato v3 coexistem temporariamente; Linear e implementação tornam a migração explícita.

#### Consequências e propagação

- **Git:** branch contém um commit sobre a main atual.
- **Contratos:** CI local passa a conhecer 27 fixtures e referências v3.
- **Planos:** DEC-013/014 publicados foram preservados; DEC-015..017 carregam a reformulação.
- **Integração:** não mergear como feature completa até API/worker/Next migrarem; pode ser usada imediatamente para handoff e branches curtas.

#### Validação e trial by fire

- **Hipótese verificável:** um colega parte da branch e encontra código atual da main mais contratos/planos 2.0 sem conflito.
- **Caminho feliz:** checkout → contract validator → iniciar microtarefa pelo mock.
- **Caso difícil/adverso:** executar em Python 3.12; somente o teste de runtime exato falha, enquanto contratos e 53 testes funcionais passam.
- **Resultado observado:** PASS parcial conforme evidências acima.
- **Fallback:** usar Python 3.14.4 oficial e repetir a suíte; não afrouxar o teste para esconder versão.

#### Gatilhos de revisão

Nova mudança na main antes do merge, falha de contrato em branch consumidora, decisão de trocar DuckDB por Postgres ou implementação v3 incompatível com os mocks.

#### Adendos

- **2026-08-29T19:45:00-03:00:** Linear permanece `NOT RUN` até confirmação explícita do preview 2.0.

## Altoé

<!-- ALTOE: faça append de novas entradas imediatamente antes da próxima seção. -->

### FL-20260829-ALTOE-001 — Usar recuperação estruturada precision-first antes do rerank vetorial

- **Timestamp:** 2026-08-29T17:00:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** Altoé
- **Categoria:** AI/RAG | quality | architecture
- **Escopo:** TASK-MEM-005, TASK-MEM-006, CTR-MEM-001 v1.1

#### Contexto e pergunta

A memória precisa reconhecer a recorrência Mastercard sem apresentar um precedente apenas porque alguns sinais genéricos coincidem. Embeddings ainda são opcionais e não podem ser a base inicial da demonstração.

#### Decisão

Implementar primeiro recuperação determinística: somente incidentes HUMAN_CONFIRMED, janela inicial de 30 dias, ao menos uma dimensão de escopo compartilhada e score estruturado de escopo, decline profile e forma temporal. O threshold inicial é 0,80 e o desempate é por score, recência e ID. Rerank vetorial continua posterior e opcional.

#### Alternativas consideradas

| Alternativa | Benefício | Custo/risco | Decisão |
| --- | --- | --- | --- |
| Threshold baixo e recall amplo | mais matches aparentes | falso precedente e ancoragem indevida | rejeitada |
| Vector-first | semântica flexível | dependência externa e menor rastreabilidade | adiada |
| Score estruturado precision-first | resultado rastreável e fallback local | pode perder match parcial | escolhida |

#### Evidência, hipóteses e limitações

- **TEST:** 15 testes unitários passaram: D-2 top-1, idempotência, candidatos não confirmados, recência, escopo, desempate, auto-match, falhas e fallback.
- **ASSUMPTION:** 30 dias e 0,80 são baseline adequados até os evals; não constituem threshold final.
- **UNKNOWN:** recall de recorrências parciais no holdout.
- **Limitação:** não houve teste de aplicação integrada, Neo4j real ou embedding real nesta etapa.

#### Consequências e gatilhos de revisão

A memória retorna NO_PRECEDENT em vez de forçar um match e nunca muda a causa atual. Recalibrar pesos ou threshold somente após os evals de TASK-MEM-008; queda de precision@1 ou perda de recurrence válida dispara revisão.


### FL-20260829-ALTOE-002 — Adiar geração OpenAI até existir proveniência por afirmação versionada

- **Timestamp:** 2026-08-29T17:21:29-03:00
- **Status:** ACCEPTED
- **Decision owner:** Altoé
- **Participantes:** Altoé; Codex; revisão independente de memória
- **Categoria:** AI/RAG | contract | quality | scope
- **Escopo:** CTR-LLM-001 v1, explicação operacional e integração opcional OpenAI
- **Links:** CTR-LLM-001, contracts/v1/explanation-bundle.schema.json, codex/altoe-incident-memory
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

A API OpenAI está disponível para o projeto, e um adapter com Structured Outputs foi prototipado na branch. A revisão mostrou que CTR-LLM-001 v1 aceita apenas evidence_ids agregados: não transporta a evidência que sustenta cada afirmação narrativa. A pergunta é se vale publicar geração textual antes de a UI conseguir auditar cada claim.

#### Decisão

Manter a explicação determinística e grounded como único caminho publicado no MVP atual. Adiar o adapter OpenAI até uma versão de contrato, acordada com os consumidores, carregar proveniência por afirmação e permitir validação/UI correspondente. A indisponibilidade ou não uso de LLM continua transparente por model_version=deterministic-template.

#### Critérios e por que agora

Precisão causal e auditabilidade superam variedade textual. O contrato v1 tem additionalProperties: false; adicionar proveniência unilateralmente quebraria API/UI, e manter a informação apenas interna não permitiria defesa da origem de cada frase.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Publicar o adapter com IDs agregados | Texto mais variado | Claim causal pode não ser auditável por campo | FACT: CTR-LLM v1 não possui campo de citações por claim | Rejeitada por grounding incompleto |
| Alterar CTR-LLM v1 unilateralmente | Permite enviar proveniência | Quebra consumidores e exige coordenação de contrato | FACT: schema v1 proíbe propriedades extras | Fora da autoridade local |
| Template determinístico e extensão versionada futura | Rastreável e compatível | Menos flexibilidade narrativa agora | TEST: 15 testes do núcleo passaram sem dependência LLM | Escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** o schema vigente exige exatamente os campos de CTR-LLM v1 e não inclui mapa de citações por claim.
- **TEST:** um protótipo com Responses API, strict JSON schema e fallback foi exercitado localmente; a revisão identificou que a proveniência seria descartada na resposta v1. O protótipo foi removido antes de integração.
- **ASSUMPTION:** uma extensão versionada poderá expor citações por campo sem prejudicar a demo; alinhar com Rogério e André antes de implementar.
- **UNKNOWN:** formato mínimo de proveniência que a UI consegue apresentar sem poluir a explicação.

#### Trade-offs aceitos

- **Ganhamos:** explicação reproduzível, HUMAN_ONLY e sem claim não auditável.
- **Abrimos mão de:** reescrita generativa no MVP atual.
- **Dívida/limitação:** a opção de usar créditos OpenAI fica pendente de contrato e integração.
- **Risco residual:** o template pode ser menos natural; a clareza factual é preferível no prazo do hackathon.

#### Consequências e propagação

- **Produto/demo:** a demo mostra explicação determinística e citações agregadas existentes; não promete geração por LLM.
- **Arquitetura/contratos:** CTR-LLM-001 v1 permanece inalterado; uma proposta futura deve ser versão nova, nunca propriedade extra silenciosa.
- **Pessoas/branches:** Rogério e André precisam participar antes que novo campo alcance API/UI; Altoé retoma o adapter após esse acordo.
- **Plano/Linear:** não há alteração imediata, pois o uso efetivo de OpenAI é opcional no plano; registrar o bloqueio ao priorizá-lo.
- **Testes/observabilidade:** manter testes de grounding determinístico; a integração futura deve incluir teste de proveniência por claim de ponta a ponta.

#### Validação e trial by fire

- **Hipótese verificável:** sem adapter LLM, cada explicação v1 continua válida contra o schema e só referencia evidência conhecida.
- **Caminho feliz:** Incident + memória retornam ExplanationBundle determinístico validado.
- **Caso difícil/adverso:** API OpenAI falha ou devolve claim não suportado; não há caminho generativo publicado que possa alterar a resposta.
- **Resultado observado:** PASS em 15 testes unitários do núcleo; NOT RUN para integração ponta a ponta com FastAPI/UI/Neo4j real.
- **Fallback:** GroundedExplainer determinístico, sem dependência de rede ou chave.

#### Gatilhos de revisão

Reabrir quando o time aprovar CTR-LLM versionado com proveniência por claim e os consumidores puderem exibi-la/validá-la, ou se a banca exigir explicitamente geração por LLM auditável.

#### Adendos

- 2026-08-29T17:21:29-03:00 — Codex: adapter e testes opcionais criados na branch foram removidos antes de merge; nenhum contrato compartilhado foi alterado.


### FL-20260829-ALTOE-003 — Manter playbooks em catálogo JSON versionado e somente humano

- **Timestamp:** 2026-08-29T17:38:02-03:00
- **Status:** ACCEPTED
- **Decision owner:** Altoé
- **Participantes:** Altoé; Codex
- **Categoria:** AI/RAG | quality | operations
- **Escopo:** TASK-EXP-001, CMP-EXP-001, catálogo de playbooks
- **Links:** LUM2-22, CTR-LLM-001 v1, codex/altoe-incident-memory
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

A explicação precisa selecionar recomendações consistentes, verificáveis e sem autoridade de execução. O código possuía playbooks criados manualmente em testes, mas ainda não havia um artefato versionado que a demo e futuras integrações pudessem auditar.

#### Decisão

Publicar um catálogo JSON v1 junto ao módulo de explicação, carregado e validado pelo código. Cada entrada declara causa, precondições de escopo, ação, cautelas e execution=HUMAN_ONLY. O loader rejeita schema desconhecido, IDs duplicados, ausência do playbook genérico ou qualquer execução diferente de HUMAN_ONLY.

#### Critérios e por que agora

O catálogo é uma dependência direta da explicação grounded e fecha a tarefa sem depender de API, Neo4j ou LLM. JSON é legível, nativo em Python e não acrescenta dependência durante a janela curta do hackathon.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Playbooks hardcoded no explainer | Menos arquivos | Auditoria e alteração ficam dispersas no código | FACT: LUM2-22 pede catálogo versionado | Rejeitada |
| YAML com parser adicional | Mais confortável para edição manual | Dependência e superfície de parsing extra | ASSUMPTION: catálogo inicial é pequeno | Não necessária no MVP |
| JSON versionado com loader estrito | Auditável e sem dependência nova | Menos ergonomia para textos longos | TEST: loader e seleção passam localmente | Escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** CTR-LLM-001 fixa execution=HUMAN_ONLY.
- **TEST:** 17 testes unitários passam após incluir catálogo, seleção do playbook do emissor e rejeição de execução automática.
- **ASSUMPTION:** dois playbooks iniciais cobrem a demo; ampliar apenas após evals.
- **UNKNOWN:** formato final de edição pela UI; fora do MVP.

#### Trade-offs aceitos

- **Ganhamos:** recomendações reproduzíveis e auditáveis.
- **Abrimos mão de:** edição dinâmica de playbooks.
- **Dívida/limitação:** catálogo é local e ainda não possui administração.
- **Risco residual:** cobertura inicial pequena; fallback genérico preserva comportamento seguro.

#### Consequências e propagação

- **Produto/demo:** a recomendação pode mostrar ID e cautela do playbook.
- **Arquitetura/contratos:** CTR-LLM v1 não muda; o catálogo é detalhe interno de CMP-EXP-001.
- **Pessoas/branches:** Rogério/API e André/UI consomem somente o ExplanationBundle já existente.
- **Plano/Linear:** LUM2-22 permanece In Progress até revisão e publicação da branch.
- **Testes/observabilidade:** loader rejeita execução não humana e catalogo inválido.

#### Validação e trial by fire

- **Hipótese verificável:** incidente Mastercard suportado escolhe PB-ISSUER-INVESTIGATION; causa inconclusiva ou sem evidência permanece no genérico.
- **Caminho feliz:** catálogo é carregado e o explainer devolve ação HUMAN_ONLY.
- **Caso difícil/adverso:** catálogo adulterado tenta execução automática ou remove fallback; loader falha explicitamente.
- **Resultado observado:** PASS local em 17 testes; NOT RUN em Neo4j real/API/UI.
- **Fallback:** PB-GENERIC-INVESTIGATION embutido no explainer.

#### Gatilhos de revisão

Revisar se a demo exigir playbook adicional, se API/UI precisarem de metadados extras ou se o catálogo precisar ser administrado externamente.

#### Adendos

- Nenhum.


### FL-20260829-ALTOE-004 — Usar baseline de avaliação determinístico antes de Neo4j real e rerank

- **Timestamp:** 2026-08-29T17:41:16-03:00
- **Status:** ACCEPTED
- **Decision owner:** Altoé
- **Participantes:** Altoé; Codex
- **Categoria:** AI/RAG | quality | scope
- **Escopo:** TASK-MEM-008, CTR-MEM-001 v1.1, avaliação de memória
- **Links:** LUM2-25, docs/evaluations/memory-baseline.md, structured-v1
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

A recuperação estruturada já possui testes unitários, mas os critérios do RAG exigem avaliar os resultados do produto antes de introduzir rerank ou depender de Neo4j. Não há URI, credenciais ou Docker Neo4j neste ambiente.

#### Decisão

Criar um conjunto de avaliação de desenvolvimento separado, com cinco resultados verificáveis: recorrência exata, combinação nova, incidente inconclusivo com precedente, precedente não confirmado e memória indisponível. Registrar o relatório como baseline in-memory e manter explícito que holdout independente e Neo4j real continuam pendentes.

#### Critérios e por que agora

Precisão e honestidade sobre no-answer importam mais que complexidade adicional. Os casos cobrem as transições que API/UI precisarão explicar e fornecem uma linha de base antes de qualquer vetor.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Esperar Neo4j/holdout para qualquer avaliação | Mais realismo | Bloqueia feedback e regressão local | FACT: ambiente não possui Neo4j configurado | Rejeitada |
| Medir só precisão média | Métrica simples | Esconde no-answer, inconclusivo e indisponibilidade | FACT: estes estados são contratos explícitos | Rejeitada |
| Baseline de desenvolvimento rotulado | Regressão local reproduzível | Não prova generalização | TEST: cinco casos passam | Escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** o baseline roda com repositório in-memory e seed humano confirmado.
- **TEST:** cinco evals e 23 testes totais passaram localmente.
- **ASSUMPTION:** Renato fornecerá holdout de combinações independentes antes do code freeze.
- **UNKNOWN:** latência e compatibilidade contra Neo4j real.

#### Trade-offs aceitos

- **Ganhamos:** regressão imediata e métricas por estado.
- **Abrimos mão de:** estimar recall/generalização nesta fase.
- **Dívida/limitação:** resultados não substituem holdout.
- **Risco residual:** otimização excessiva ao seed; mitigada por rotular o conjunto como desenvolvimento.

#### Consequências e propagação

- **Produto/demo:** estados de memória continuam demonstráveis mesmo sem Neo4j.
- **Arquitetura/contratos:** nenhum schema muda.
- **Pessoas/branches:** integração Neo4j depende de configuração coordenada por Rogério; Renato deve fornecer holdout.
- **Plano/Linear:** LUM2-25 passa a In Progress.
- **Testes/observabilidade:** relatório separa métricas observadas de lacunas.

#### Validação e trial by fire

- **Hipótese verificável:** regressão que transforme no-answer em match ou altere INCONCLUSIVE falha antes de integração.
- **Caminho feliz:** Mastercard D-2 é top-1.
- **Caso difícil/adverso:** falha da memória retorna MEMORY_UNAVAILABLE, não NO_PRECEDENT.
- **Resultado observado:** PASS em cinco evals locais; NOT RUN contra Neo4j real/holdout.
- **Fallback:** manter structured-v1 e template deterministicamente.

#### Gatilhos de revisão

Adicionar rerank, conectar Neo4j, receber holdout ou observar falso precedente exige rodar e comparar o conjunto completo.

#### Adendos

- Nenhum.


### FL-20260829-ALTOE-005 — Exigir vínculo triplo para traçar transação até incidente

- **Timestamp:** 2026-08-29T20:06:13-03:00
- **Status:** ACCEPTED
- **Decision owner:** Altoé
- **Participantes:** Altoé; Codex; Rogério e André como consumidores futuros
- **Categoria:** AI/RAG | contract | quality
- **Escopo:** TASK-EXP-002 / LUM2-23; `CMP-MEM/EXP-001`; CTR-INC-001 e CTR-TXL-001 v1
- **Links:** LUM2-23, LUM2-63, CTR-INC-001 v1, CTR-TXL-001 v1, CTR-LLM-001 v1
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O plano 2.0 exige navegar de uma transação até uma explicação de incidente,
mas proíbe narrar falha isolada como incidente e vazar evidência de outra
transação. Os contratos já trazem `related_incident_ids`, `evidence_ids` e
`correlation_id`, sem precisar de novo campo público.

#### Decisão

Resolver uma ligação somente quando os três sinais concordarem: a classificação
da transação referencia o Incident, contém ao menos um `evidence_id` próprio e
o `correlation_id` é igual. Os IDs de evidência transacional e agregada podem
ter namespaces diferentes; evidência de memória histórica não é atribuída a
uma transação corrente.

#### Critérios e por que agora

Esta regra entrega rastreabilidade auditável para a API/UI futura sem uma nova
chamada LLM, sem mudança de schema e sem depender da implementação da API v3.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Confiar apenas em `related_incident_ids` | Implementação curta | Permite referência sem prova de evidência | FACT: campo é uma lista de IDs | Não protege grounding |
| Inferir por escopo ou semelhança | Cobre registros incompletos | Pode ligar uma falha isolada ao incidente errado | FACT: RAG não classifica transações | Proibido pelo guardrail |
| Exigir Incident + evidência da classificação + correlação | Auditável e compatível | Pode retornar vazio para dado incompleto | TEST: pendente | Escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** CTR-TXL-001 v1 expõe os três campos necessários; os fixtures v2
  usam IDs de evento na transação e IDs agregados no Incident.
- **TEST:** NOT RUN — testes da resolução serão executados após a implementação.
- **ASSUMPTION:** produtor da API v3 preservará a mesma `correlation_id` entre
  transação e Incident relacionado.
- **UNKNOWN:** o formato de apresentação do trace pelo frontend; o resolver
  permanece interno e retorna IDs estáveis.

#### Trade-offs aceitos

- **Ganhamos:** nenhuma associação sem prova local e reproduzível.
- **Abrimos mão de:** mostrar relações quando o produtor não fornecer evidência.
- **Dívida/limitação:** a regra não reconstrói links perdidos no histórico.
- **Risco residual:** producer com `correlation_id` inconsistente produz vazio,
  que é seguro e observável pelos testes.

#### Consequências e propagação

- **Produto/demo:** uma transação isolada permanece sem narrativa de incidente.
- **Arquitetura/contratos:** sem alteração de schema; interpreta os campos
  congelados de CTR-INC-001/CTR-TXL-001.
- **Pessoas/branches:** Rogério recebe a regra de resolução; André recebe IDs
  já autorizados para o detalhe.
- **Plano/Linear:** LUM2-23 em progresso; LUM2-63 consumirá o resolver.
- **Testes/observabilidade:** cobrir um, múltiplos, ausente e cross-transaction.

#### Validação e trial by fire

- **Hipótese verificável:** somente transações com vínculo triplo aparecem.
- **Caminho feliz:** duas transações possuem evidência de classificação e
  apontam para o mesmo Incident.
- **Caso difícil/adverso:** ID de incidente sem evidência ou correlação cruzada
  não é exposto.
- **Resultado observado:** NOT RUN.
- **Fallback:** trace vazio; ExplanationBundle do Incident continua válido.

#### Gatilhos de revisão

Novo contrato que separe correlation por subfluxo, ou necessidade de explicar
evidência agregada sem transação individual, exige change control antes de
relaxar a regra.

#### Adendos

- **2026-08-29T20:06:13-03:00:** PASS: 22 testes focados passaram, incluindo
  múltiplas transações, correlação divergente, Incident diferente, evidência
  ausente e `INCONCLUSIVE` sem promoção. `scripts/validate_contracts.py` e
  `compileall` passaram. A revisão descobriu que os fixtures v2 usam
  namespaces distintos para evidência transacional e agregada; a regra foi
  corrigida antes do gate para validar evidência da classificação, não igualdade
  textual entre esses namespaces.
- **2026-08-29T20:06:13-03:00:** PASS: a suíte completa executou 57 testes
  sem falhas depois da correção.
- **2026-08-29T21:24:57-03:00:** PASS: LUM2-63 adicionou o resolvedor
  `transaction_id → evidence → Incident → ExplanationBundle`, filtrado pela
  transação solicitada e sem chamada LLM por item. Nove testes focados passaram
  cobrindo no-incident, um/múltiplos Incidents, evidência ausente, correlação
  cruzada, isolamento entre transações e falhas de memória/modelo. Um Incident
  sem bundle é exposto como `PARTIAL`, não como resolvido, preservando a falha
  explícita; nenhum contrato público ou API foi alterado.
- **2026-08-29T21:55:16-03:00:** A branch foi rebaseada sobre a `origin/main`
  local que contém ingestion/detection/API. O adaptador interno agora aceita as
  respostas existentes de `GET /incidents/{id}` e reutiliza somente bundles já
  produzidos; bundle ausente, inválido ou com `incident_id` divergente permanece
  `PARTIAL`, sem chamada de modelo e sem mudar schema/endpoints. PASS: 27 testes
  de memória, explicação e trace passaram via `unittest`. A descoberta completa
  ficou BLOCKED pelo ambiente: o Python disponível é 3.12.13, mas o projeto
  exige 3.14.4, e faltam `duckdb` e `jsonschema`.
- **2026-08-29T22:15:19-03:00:** INTEGRATED: o filtro
  `GET /v1/incidents?transaction_id=` passou a ler o registro persistido e a
  aplicar o resolvedor de trace antes de devolver qualquer Incident. Assim,
  `related_incident_ids` sozinho não autoriza exposição: classificação com
  evidência vazia ou `correlation_id` divergente retorna lista vazia. A resposta
  pública e os contratos não mudaram; o trace continua interno até o formato de
  apresentação ser definido. PASS: `validate_contracts.py` e a suíte completa
  executaram com 109 testes aprovados. Browser acceptance ficou BLOCKED pela
  política do navegador local para `127.0.0.1`; os testes HTTP automatizados
  cobrem o endpoint.

### FL-20260829-ALTOE-006 — Separar lista de Incidents do detalhe grounded da transação

- **Timestamp:** 2026-08-29T22:20:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** Gabriel Altoé
- **Contexto:** `GET /v1/incidents` passou a devolver objetos diferentes quando
  recebia `transaction_id`, o que tornava o contrato ambíguo para o cliente
  Next.js e para geração de tipos.
- **Decisão:** manter a lista sempre homogênea e publicar o detalhe em
  `GET /v1/transactions/{transaction_id}/incidents` (`CTR-TDI-001 v1`). A nova
  resposta expõe estado, links autorizados, Incident, memória, ExplanationBundle
  e limitações; transação conhecida sem vínculo retorna `NO_INCIDENT`, e uma
  inexistente retorna `404`.
- **Trade-off:** há uma rota e um schema a mais, mas nenhum consumidor precisa
  inferir a forma da resposta pelo parâmetro de consulta.
- **Guardrails:** a associação requer `related_incident_ids`, evidência de
  classificação e `correlation_id` compatível; nenhum LLM é chamado por item e
  precedente histórico não altera a causa atual.
- **Validação concluída:** schema/fixture/OpenAPI, testes HTTP para
  `RESOLVED`, `NO_INCIDENT`, correlação/evidência inválida e `404`; `112`
  testes passaram e `scripts/validate_contracts.py` retornou `OK`.
- **Gate visual:** bloqueado pela política do navegador local nesta máquina;
  o endpoint foi coberto por testes HTTP e continua pendente de aceite visual
  no ambiente de integração.

### FL-20260829-ALTOE-008 — Avaliar o detalhe transacional sem expor dados internos

- **Timestamp:** 2026-08-29T22:58:09-03:00
- **Status:** ACCEPTED
- **Decision owner:** Gabriel Altoé
- **Escopo:** `TASK-MEM-009 / LUM2-64`, `CTR-TDI-001 v1`
- **Contexto:** a extensão transacional de memória precisa provar tanto o
  isolamento entre transações quanto a separação entre dados públicos e os
  controles internos do gerador.
- **Decisão:** avaliar a rota pública com registros de transação controlados,
  sem importar ou alterar o harness de background traffic ainda bloqueado.
  Os casos verificam falha sem Incident, duas transações no mesmo Incident com
  evidências isoladas, ausência de seed/configuração/ground truth e
  `MEMORY_UNAVAILABLE` preservando causa atual e ExplanationBundle
  determinístico.
- **Trade-off:** esta evidência não substitui o ensaio ponta a ponta com tráfego
  de fundo; ele permanece dependente de `LUM2-62`, `LUM2-61` e `LUM2-48`.
- **Validação concluída:** `18` testes de grounding/API passaram e
  `scripts/validate_contracts.py` retornou `OK`.

### FL-20260829-ALTOE-009 — Integrar background traffic ao detalhe grounded

- **Timestamp:** 2026-08-29T23:18:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** Gabriel Altoé
- **Escopo:** `LUM2-61`, `LUM2-62`, `LUM2-63`, `LUM2-64`; `CTR-TXL-001` e
  `CTR-TDI-001 v1`
- **Contexto:** a `main` recebeu o adapter determinístico e o harness de
  tráfego, mas mantinha um import circular e ainda não carregava o contrato de
  detalhe grounded.
- **Decisão:** montar uma branch de integração sobre a `main`, aplicar a
  cadeia de trace/contrato/evals e mover o import do harness para o handler
  `/demo/background-traffic`. O teste de regressão importa o módulo em processo
  novo para impedir o retorno do ciclo.
- **Resultado:** tráfego de fundo entra pela batch API, o worker persiste os
  eventos, métricas passam a refletir o batch processado e o detalhe de cada
  transação sem vínculo RCA retorna `NO_INCIDENT` sem expor a seed. A associação
  continua requerendo `related_incident_ids`, evidência e `correlation_id`.
- **Validação concluída:** `44` testes integrados passaram e
  `scripts/validate_contracts.py` retornou `OK`.
- **Pendente:** revisão/merge na `main` e RCA real para autorizar links a
  Incident em tráfego não controlado.

### FL-20260829-ALTOE-010 — Operacionalizar a memória Neo4j sem duplicar o lifecycle da API

- **Timestamp:** 2026-08-29T23:59:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** Gabriel Altoé
- **Escopo:** `CTR-MEM-001 v1.1`, `CMP-MEM/EXP-001`, runtime Neo4j, Compose e API de Incidents
- **Decisão:** integrar o runtime, bootstrap e Compose Neo4j, mas preservar na API o driver reutilizável já adotado pela `main`. O adapter local continua opcional; sem configuração ou falha do driver, a memória em RAM permanece o fallback da aplicação.
- **Trade-off:** abre mão de criar/fechar um driver a cada request para evitar custo e conexões transitórias; o lifecycle compartilhado será revisado se houver concorrência, latência ou mudança no deploy.
- **Guardrails:** Neo4j recebe somente memória de Incident; transações completas, segredos e estado de fallback não são expostos ao navegador. A instalação do driver segue o extra `neo4j` do projeto, não um segundo manifesto divergente.
- **Validação planejada:** suíte completa, testes de runtime/bootstrap, validação de contratos e smoke local Compose + bootstrap antes do merge.

## Rogério

<!-- ROGERIO: faça append de novas entradas imediatamente antes da próxima seção. -->

### FL-20260829-ROGERIO-001 — Rodar o backend (API + Streamlit) no Railway

- **Timestamp:** 2026-08-29T17:46:44-03:00
- **Status:** ACCEPTED
- **Decision owner:** Rogério
- **Participantes:** Rogério e Claude (segunda opinião)
- **Categoria:** operations
- **Escopo:** CMP-API-001, CMP-UI-001; hospedagem de CMP-MEM-001 (Neo4j) permanece separada
- **Links:** DEC-003, DEC-013, `docs/plans/system-plan.md`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O plano (DEC-003) fixou FastAPI + DuckDB embutido + Neo4j + Streamlit como stack, mas nenhuma decisão registrada dizia onde essa API roda durante e depois do hackathon. Era preciso escolher uma plataforma antes de a demo depender de um host improvisado.

#### Decisão

Hospedar a API FastAPI (e o Streamlit, se ficar no mesmo processo/monorepo) no Railway, via Docker (já assumido disponível em `ASM-003`). Neo4j continua em serviço dedicado (Aura Free), independente da escolha de host da API — Railway não hospeda o grafo.

#### Critérios e por que agora

Suporta Docker e volume persistente para o arquivo DuckDB, tem plano gratuito (trial) suficiente para a janela do hackathon, e configuração de env vars (`NEO4J_URI`, `OPENAI_API_KEY`) mais simples que alternativas equivalentes. Precisava travar antes de gastar tempo de integração em H15–H19 (DEC-008) configurando infra às pressas.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Render (free web service) | também suporta Docker, tier grátis | disco efêmero a cada redeploy | FACT: documentado pela Render | perde estado do DuckDB entre deploys, pior para demo repetida |
| Vercel (serverless functions) | já disponível neste ambiente via MCP | sem processo long-running nem volume persistente nativo; Neo4j driver e DuckDB embutido não combinam bem com serverless stateless | ASSUMPTION: baseado no modelo de execução serverless da Vercel | stack assume processo único com estado local (DuckDB) |
| Execução local sem host (fallback de ASM-003) | zero custo, zero setup externo | não demonstrável remotamente para a banca fora do horário da apresentação | FACT: ASM-003 já prevê esse fallback | só serve como plano B se Docker/host falhar |

#### Evidência, hipóteses e desconhecidos

- **FACT:** Railway oferece $5 de crédito trial sem cartão (30 dias) e plano Hobby a $5/mês com $5 de uso incluído (railway.com/pricing, consultado 2026-08-29).
- **TEST:** NOT RUN — deploy real ainda não executado nesta branch.
- **ASSUMPTION:** o trial cobre a janela do hackathon; se o projeto continuar depois, migrar para Hobby. Owner: Rogério, gatilho: trial expirar ou hackathon encerrar.
- **UNKNOWN:** se Streamlit vai no mesmo serviço Railway que a API ou em serviço separado dentro do mesmo projeto Railway.

#### Trade-offs aceitos

- **Ganhamos:** host único com Docker, volume e env vars simples; sem reescrever a stack para serverless.
- **Abrimos mão de:** tier realmente gratuito e permanente (Railway não tem mais free tier sem expiração).
- **Dívida/limitação:** custo recorrente pequeno ($5/mês) se o projeto sobreviver ao hackathon.
- **Risco residual:** trial de 30 dias pode expirar antes da apresentação final; ver RSK-009.

#### Consequências e propagação

- **Produto/demo:** demo pode ser acessada por URL pública em vez de apenas localhost.
- **Arquitetura/contratos:** nenhum contrato muda; é escolha de hospedagem, não de stack (DEC-003 permanece).
- **Pessoas/branches:** quem for integrar em H15–H19 (DEC-008) usa o serviço Railway como alvo de deploy, não infra própria.
- **Plano/Linear:** nenhuma tarefa nova criada nesta conversa; se necessário, abrir microtask de deploy no Linear separadamente.
- **Testes/observabilidade:** `/health` (já previsto em DEC-003) deve ser checado contra a URL pública do Railway, não só localhost.

#### Validação e trial by fire

- **Hipótese verificável:** a API sobe no Railway com as mesmas env vars do `.env.example` e responde `/health` publicamente.
- **Caminho feliz:** deploy via Docker, health check verde, UI acessando a API pela URL do Railway.
- **Caso difícil/adverso:** trial expira, crédito acaba, ou build Docker falha por dependência do DuckDB/Neo4j driver.
- **Resultado observado:** NOT RUN — decisão de plataforma, deploy ainda não executado.
- **Fallback:** execução local (ASM-003) para a apresentação, se o deploy remoto falhar em cima da hora.

#### Gatilhos de revisão

Reabrir se o trial expirar antes do fim do hackathon sem migração para Hobby decidida, ou se o build Docker no Railway falhar de forma não trivial.

#### Adendos

- 2026-08-29 — Claude: `Dockerfile` + `.dockerignore` prontos e validados sem Docker local (install + start real do `CMD` numa cópia isolada do build context, `/health` e `/metrics/current` responderam 200). Deploy real em si ainda não executado — Rogério decidiu adiar pra mais pra frente. Runbook manual dos passos que só a conta Railway consegue fazer: `docs/deploy-railway.md`.

### FL-20260829-ROGERIO-002 — Não travar as chaves de `scope` em CTR-INC-001 agora

- **Timestamp:** 2026-08-29T18:12:19-03:00
- **Status:** ACCEPTED
- **Decision owner:** Rogério
- **Participantes:** Altoé (levantou o ponto), Claude (investigação e recomendação), Rogério (decisão)
- **Categoria:** contract
- **Escopo:** `contracts/v1/incident.schema.json` (`CTR-INC-001`), `app/memory/*` (Altoé)
- **Links:** `CTR-INC-001`, `CTR-MEM-001 v1.1`, commits `fe7ff28` (fix real relacionado), `docs/plans/people/rogerio.md`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

Altoé reportou que `scope.provider` (usado internamente por `app/memory`) e `scope.provider_id` (usado pelo resto do sistema desde `CTR-EVT-001`) eram nomes divergentes pro mesmo dado. Investigação confirmou dois bugs reais de leitura de chave (`app/memory/seed.py` e `app/memory/neo4j_repository.py`), já corrigidos. Ele propôs, como item 4 de 5, travar/documentar no schema quais chaves `scope` aceita, hoje totalmente livre (`additionalProperties: {type: array...}`). Pergunta: travar agora ou deixar aberto?

#### Decisão

Manter `scope` sem enum de chaves fixas em `CTR-INC-001` por enquanto. Não editar o schema `FROZEN` para essa restrição nesta fase do hackathon.

#### Critérios e por que agora

O schema JSON valida a *forma* dos dados, não qual código lê qual chave de um dicionário — um enum não teria pego nenhum dos dois bugs reais encontrados (ambos eram Python lendo `scope.get("provider", ...)` em vez de `scope.get("provider_id", ...)`, em dados que já validavam contra o schema de qualquer jeito). A proteção que efetivamente pegou o problema foi teste de integração cross-boundary (`test_upsert_reads_provider_id_into_providers_cypher_param`), não validação de schema. Travar agora também arrisca bloquear `TASK-DET-001..004`/`RCA-001..002` (Renato, ainda não iniciado) caso o detector precise fatiar por dimensão fora do conjunto atual (`provider_id`, `country`, `card_brand`).

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Enum fechado (`provider_id`, `country`, `card_brand`, ...) em `CTR-INC-001` | erro explícito de schema se alguém digitar chave nova errada | bloqueia Renato se o detector real usar dimensão fora do conjunto hoje conhecido | ASSUMPTION: conjunto final de dimensões do detector ainda não existe | risco de travar contrato antes do dado real existir |
| Enum + validação, mas revisitando quando RCA existir | mesmo ganho, sem o risco acima | atraso deliberado — trabalho fica pendente até lá | FACT: `TASK-DET-001..004`/`RCA-001/002` (Renato) 100% `Todo`, sem branch | **escolhida** — ver Gatilhos de revisão |
| Nada (manter aberto pra sempre) | zero esforço | mesma classe de bug pode se repetir sem teste equivalente em cada novo ponto de leitura | FACT: já aconteceu 2x nesta sessão | rejeitada — vira ambiguidade permanente, exatamente o que Altoé alertou |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `contracts/v1/incident.schema.json` define `scope` como `{"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string"}}}` — nenhuma chave é exigida ou proibida.
- **TEST:** `test_upsert_reads_provider_id_into_providers_cypher_param` (commit `fe7ff28`) — PASS, prova que `provider_id` chega certo no Cypher hoje; não prova nada sobre chaves futuras.
- **ASSUMPTION:** o conjunto de dimensões usado pelo RCA real de Renato será um superconjunto ou igual a `{provider_id, country, card_brand}`. Owner: Rogério, gatilho: `TASK-DET-004`/`RCA-001` produzirem `AnomalyCandidate.slice` real.
- **UNKNOWN:** se Renato vai precisar de dimensões como `merchant_id`, `issuer_bank_id` ou `payment_method_category` no `scope` do incidente.

#### Trade-offs aceitos

- **Ganhamos:** zero risco de bloquear a integração de Renato por um contrato travado cedo demais.
- **Abrimos mão de:** uma camada de proteção de schema contra typo de chave em fixtures futuras.
- **Dívida/limitação:** a mesma classe de bug (chave certa vs errada num dict) pode se repetir num terceiro ponto de leitura ainda não escrito, sem um teste equivalente ao de `neo4j_repository.py`.
- **Risco residual:** baixo — o par `provider`/`provider_id` já foi caçado nos dois lugares que existem hoje (`grep` cobriu `app/memory/`, `graph/`, `contracts/v1/incident.schema.json`); risco reaparece só em código novo.

#### Consequências e propagação

- **Produto/demo:** nenhuma — decisão é sobre rigidez de contrato, não muda comportamento observável.
- **Arquitetura/contratos:** `CTR-INC-001` continua v1 sem essa restrição.
- **Pessoas/branches:** Altoé sabe que o ponto foi investigado e parcialmente aceito (itens 1/2/3/5 do pedido dele já implementados; item 4 explicitamente adiado, não esquecido).
- **Plano/Linear:** nenhuma tarefa nova criada.
- **Testes/observabilidade:** cobertura atual (`test_neo4j_repository.py`, `scripts/validate_contracts.py`) é o que garante a convenção `provider_id` até o enum existir.

#### Validação e trial by fire

- **Hipótese verificável:** quando `TASK-DET-004`/`RCA-001` (Renato) existirem, o conjunto real de chaves de `scope` estará conhecido e o enum poderá ser adicionado sem quebrar ninguém.
- **Caminho feliz:** Renato usa só `provider_id`/`country`/`card_brand` (ou um superconjunto conhecido); enum vira formalidade de baixo risco.
- **Caso difícil/adverso:** Renato precisa de uma dimensão nova no meio da integração final (H13–H17); sem enum, isso simplesmente funciona sem change control extra — é o cenário que esta decisão protege.
- **Resultado observado:** NOT RUN — decisão de adiar, nada a executar agora.
- **Fallback:** se um terceiro bug de chave divergente aparecer antes do RCA existir, resolver como os dois primeiros (grep + teste de integração pontual), sem esperar o enum.

#### Gatilhos de revisão

Reabrir quando `TASK-DET-004` ou `TASK-RCA-001` (Renato) produzirem `AnomalyCandidate`/`Incident.scope` reais — nesse momento, fechar o enum de `CTR-INC-001.scope` com o conjunto real de dimensões, via change control normal (system-plan primeiro).

#### Adendos

- 2026-08-29 — `TASK-DET-004` foi entregue (ver `FL-20260829-ROGERIO-003`), então o gatilho de revisão desta decisão está parcialmente atingido. `AnomalyCandidate.slice` real usa `{provider_id, country}`, consistente com o resto do sistema. Falta `TASK-RCA-001/002` (Renato) pra fechar o conjunto definitivo de dimensões antes de travar o enum.

### FL-20260829-ROGERIO-003 — Assumir parte da frente de Renato (dados + detecção)

- **Timestamp:** 2026-08-29T18:49:11-03:00
- **Status:** ACCEPTED
- **Decision owner:** Rogério
- **Participantes:** Rogério (decisão, alinhada no time), Claude e Codex (execução)
- **Categoria:** scope
- **Escopo:** `CMP-DATA-001`, `CMP-DET-001` (originalmente `OBJ-RENATO-001`); branch `RENATO_CONTINUCAO_ROGERIO`
- **Links:** `LUM2-7`, `LUM2-45`, `LUM2-48`, `LUM2-50`, `LUM2-51`, `LUM2-52`, `LUM2-53`, `CTR-DET-001`, `CTR-SCN-001`, `CTR-EVT-001`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

`OBJ-ROGERIO-001` (`LUM2-6`) chegou ao limite do que era possível sem terceiros: `TASK-INC-001` dependia de `TASK-RCA-002`, `TASK-INT-001` de `TASK-DET-004`+`TASK-UI-002`, e a frente de Renato (`LUM2-7`, 15 microtarefas) tinha só `TASK-DATA-001` pronta. O time decidiu que o Rogério assumiria parte dessa frente para o projeto não ficar parado. Quais tarefas pegar, sem tomar o trabalho autoral de Renato nem colidir fisicamente com ele?

#### Decisão

Assumir **6 de 15** microtarefas de `LUM2-7`, escolhidas por destravarem a cadeia sem invadir a parte autoral: `TASK-DATA-002` (`LUM2-45`), `TASK-DATA-006` (`LUM2-48`), `TASK-DET-001..004` (`LUM2-50/51/52/53`). Trabalho isolado na branch `RENATO_CONTINUCAO_ROGERIO`, com pacotes novos (`app/detection/`) e extensão não-destrutiva do que Renato já tinha (`app/simulation/`), sem reescrever nada dele. As 9 restantes — incluindo `RCA-001/002` e `EVAL-001/002`, o núcleo autoral — permanecem com Renato.

#### Critérios e por que agora

`TASK-DET-004` era o bloqueio de `TASK-RCA-001` (Renato) *e* de `TASK-INT-001` (nosso) ao mesmo tempo — entregá-lo destrava os dois lados. `TASK-DATA-006` era o único bloqueio de `TASK-API-003` (`LUM2-40`, nosso), até então preso em fixture. O corte foi por fronteira de arquivo, não por volume: `app/simulation/` (estendido) e `app/detection/` (novo) não colidem com o que Renato continua tocando.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Assumir a frente inteira de Renato (15 tarefas) | destrava tudo de uma vez | toma o trabalho autoral dele (RCA/beam search é o diferencial da lente Originality); risco de colisão física com o que ele já estava tocando | FACT: branch `renato/define-generator` ativa | não é só volume de trabalho — muda quem entregou o quê no hackathon |
| Não assumir nada e esperar | zero risco de colisão ou sobreposição | projeto parado; `LUM2-6` já sem tarefa desbloqueada | FACT: verificado tarefa a tarefa contra `linear-preview.md` | tempo do hackathon é o recurso mais escasso (DEC-008) |
| **Assumir 6, por fronteira de arquivo** | destrava `API-003` e `RCA-001`; sem colisão | Renato precisa saber exatamente quais IDs para não duplicar esforço | FACT: 46/46 testes verdes pós-integração | **escolhida** |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `app/detection/` implementa baseline com pooling hierárquico (`weekday_hour` → `hour` → `global`, sem vazamento de futuro), Wilson score 95% para taxas e 3-MAD robusto para latência.
- **TEST:** PASS — smoke de integração completo (script manual, não commitado): 10 dias de tráfego normal + injeção real de `scenario-provider-br` → `get_current_metrics()` → `detect_candidates()` → `correlate_candidates()` → `to_incident()`. A degradação injetada em `stripe/BR` foi detectada nos 3 sinais (`APPROVAL_RATE` 0.222 vs 0.889 esperado, `LATENCY_P95` 21609ms vs 1695ms, `TIMEOUT_RATE` 0.25 vs 0.0; `statistical_strength=1.0` nos três) e virou `Incident` `SUPPORTED` com impacto GMV real. 46/46 testes e `scripts/validate_contracts.py` OK.
- **ASSUMPTION:** Renato foi (ou será) informado dos 6 IDs assumidos e seguirá nas 9 restantes. Owner: Rogério, gatilho: próxima sincronização do time.
- **UNKNOWN:** se o baseline sazonal se comporta igual sobre os 90 dias reais de `TASK-DATA-004` (Renato) — hoje foi exercitado só contra série sintética de janelas.

#### Trade-offs aceitos

- **Ganhamos:** `TASK-API-003` deixou de ser fixture e virou injeção real; `TASK-RCA-001` destravado para Renato; 3 dos 4 bloqueios de `TASK-INT-001` resolvidos.
- **Abrimos mão de:** clareza de autoria única na frente `LUM2-7` — agora ela tem dois donos, o que exige comunicação explícita para não duplicar trabalho.
- **Dívida/limitação:** `app/simulation/outcomes.py` usa placeholders para decline codes e latência (`TASK-DATA-003`, Renato) e emite todos os eventos perto de um único `reference_time` (sem a sazonalidade de `TASK-DATA-004`). Documentado no docstring do módulo.
- **Risco residual:** o detector produz falsos positivos de baixa força em slices não relacionados (~10 candidatos com `statistical_strength=0.5` no smoke, contra os 3 reais de força 1.0) — comportamento esperado de testes independentes a 95% sem correção de comparações múltiplas. Visível via `statistical_strength` para quem consome; tratar em `TASK-EVAL-001` (Renato).

#### Consequências e propagação

- **Produto/demo:** o passo D2 do roteiro (injetar provider degradado no Brasil) agora funciona com dado real ponta a ponta, não fixture.
- **Arquitetura/contratos:** nenhum contrato alterado. `app/detection/` consome `CTR-AGG-001` e produz `CTR-DET-001`; `app/simulation/` produz `CTR-EVT-001` e consome `CTR-SCN-001`.
- **Pessoas/branches:** Renato precisa saber os 6 IDs assumidos (`LUM2-45/48/50/51/52/53`) e que os 9 restantes seguem com ele. `RENATO_CONTINUCAO_ROGERIO` não foi mergeada em lugar nenhum.
- **Plano/Linear:** os 6 marcados `Done`; `LUM2-7` movido para `In Progress`. Mapa Linear em `docs/plans/people/renato.md` corrigido — as issues `LUM2-44/45/46` têm o campo interno "ID estável" rotacionado entre si, e o título da issue é a fonte confiável.
- **Testes/observabilidade:** `tests/test_detection.py`, `tests/test_simulation_outcomes.py`, `tests/test_simulation_live_stream.py`.

#### Validação e trial by fire

- **Hipótese verificável:** uma degradação injetada por cenário é detectada estatisticamente e vira incidente, sem regra hardcoded para aquele slice.
- **Caminho feliz:** verificado — ver `TEST` acima.
- **Caso difícil/adverso:** jurado injeta combinação inédita (D6). O detector varre todos os slices presentes nas janelas agregadas, sem lista fixa, então deve funcionar; **não exercitado** com combinação fora de `scenario-provider-br`.
- **Resultado observado:** PASS no caminho feliz; `NOT RUN` para D6.
- **Fallback:** fixtures anteriores continuam válidas; nenhuma foi removida.

#### Gatilhos de revisão

Reabrir se Renato retomar qualquer uma das 6 tarefas assumidas (risco de trabalho duplicado), ou se o baseline sazonal se comportar diferente sobre os 90 dias reais de `TASK-DATA-004`.

#### Adendos

- Nenhum.

### FL-20260829-ROGERIO-004 — Retomar a entrega transaction-first exclusivamente na branch de plataforma

- **Timestamp:** 2026-08-29T20:06:30-03:00
- **Status:** ACCEPTED
- **Decision owner:** Rogério
- **Participantes:** Rogério e Codex
- **Categoria:** Git/integration | operations
- **Escopo:** `OBJ-ROGERIO-001`; `TASK-TXN-API-001`, `TASK-TXN-WORKER-001`, `TASK-DEPLOY-API-001`; branch `feat/OBJ-ROGERIO-001-platform-core`
- **Links:** `docs/plans/system-plan.md` v2.0.0; `docs/plans/people/rogerio.md`; commits `067546e`, `45202d6`; `FL-20260829-ROGERIO-003`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

As alterações locais da frente de dados/detecção permanecem em `RENATO_CONTINUCAO_ROGERIO`, enquanto o plano 2.0 exige mudanças em contratos, API, lifecycle e deploy sob o ownership de Rogério. Era necessário escolher onde retomar o trabalho sem misturar duas frentes independentes nem perder o plano aprovado, pois a branch de plataforma ainda continha somente o plano 1.3.1.

#### Decisão

Executar exclusivamente no worktree da branch `feat/OBJ-ROGERIO-001-platform-core`. Trazer para ela apenas os commits documentais aprovados do replanejamento 2.0 (`067546e` e `45202d6`) e preservar, sem alteração, a working tree e a branch `RENATO_CONTINUACAO_ROGERIO`.

#### Critérios e por que agora

O plano 2.0 nomeia Rogério como owner de `CMP-API-001`, `CMP-TXN-001` e `CMP-DEPLOY-001`; trabalhar em outra branch criaria atribuição e integração ambíguas. A documentação 2.0 é a fonte de verdade e precisa estar no mesmo histórico do código que a implementará.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Branch de plataforma com somente os commits documentais 2.0 | ownership e plano coerentes; preserva trabalho paralelo | requer validar a integração documental antes do código | FACT: a branch estava limpa e os commits são somente docs | escolhida |
| Continuar em `RENATO_CONTINUACAO_ROGERIO` | evita trocar de worktree | mistura ownership e mudanças locais não relacionadas | FACT: há alterações não commitadas nessa working tree | viola a separação solicitada |
| Mesclar a branch inteira do Renato | disponibiliza também dados/detecção | integra código fora do escopo e antecipa conflitos semânticos | FACT: o plano mantém `TASK-DATA-008` sob Renato | fora do escopo desta retomada |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `feat/OBJ-ROGERIO-001-platform-core` estava limpa em `cd7c293`; a worktree do Renato tem alterações locais em API, dependências, testes e documentação.
- **TEST:** PASS — cherry-picks documentais concluídos em `067546e` e `45202d6`; `git diff --check HEAD~2..HEAD` passou.
- **ASSUMPTION:** os contratos frozen do draft `cc24c7a` serão integrados por microtarefa, não copiados sem validação. Owner: Rogério; gatilho: início de `TASK-TXN-API-001`.
- **UNKNOWN:** o Linear atualmente conectado não contém o projeto ou as issues `LUM2-*` registradas no plano; requer preview e confirmação antes de recriação/sincronização externa.

#### Trade-offs aceitos

- **Ganhamos:** fronteira de ownership auditável e código futuro alinhado ao plano 2.0.
- **Abrimos mão de:** integrar imediatamente o adapter de outcome ainda pertencente a Renato.
- **Dívida/limitação:** a sincronização de status no Linear fica bloqueada até o projeto/questões ausentes serem recriados ou o workspace correto ser conectado.
- **Risco residual:** o contrato draft pode divergir da base atual; cada microtarefa terá testes de schema, contrato e revisão antes de ser aceita.

#### Consequências e propagação

- **Produto/demo:** nenhuma mudança pública nesta etapa documental.
- **Arquitetura/contratos:** aplica `CTR-TXN-001`, `CTR-TXL-001` e `CTR-API-001 v3` como especificações frozen para a implementação subsequente.
- **Pessoas/branches:** Rogério trabalha em `feat/OBJ-ROGERIO-001-platform-core`; a branch de Renato permanece inalterada.
- **Plano/Linear:** planos 2.0 e preview foram trazidos à branch; Linear permanece `NOT SYNCED` no workspace conectado até decisão explícita de recriação.
- **Testes/observabilidade:** cada microtarefa exige testes focados, `code-review-gate` e validação de integração; browser gate quando houver fluxo consumidor executável.

#### Validação e trial by fire

- **Hipótese verificável:** alterações de `TASK-TXN-*` aparecem somente no histórico e no worktree de plataforma, preservando a working tree de Renato.
- **Caminho feliz:** API v3 e worker serão implementados e testados na branch de plataforma.
- **Caso difícil/adverso:** dependência de outcome indisponível; worker permanece bloqueado por interface/fixture, sem substituir o módulo de Renato.
- **Resultado observado:** PASS para isolamento de branch e sincronização documental; implementação ainda `NOT RUN`.
- **Fallback:** manter os endpoints v1 apenas como harness interno e usar fixtures de contrato até o handoff de `TASK-DATA-008`.

#### Gatilhos de revisão

Qualquer necessidade de modificar um contrato frozen, integrar código da branch de Renato ou recriar o Linear sem preview aprovado exige novo change control.

#### Adendos

- Nenhum.

### FL-20260829-ROGERIO-005 — Integrar `origin/main` por merge preservando a branch e o trabalho local

- **Timestamp:** 2026-08-29T21:09:16-03:00
- **Status:** ACCEPTED
- **Decision owner:** Rogério
- **Participantes:** Rogério; Codex como integration coordinator
- **Categoria:** Git/integration | operations
- **Escopo:** branch `RENATO_CONTINUCAO_ROGERIO`; upstream `origin/main@03857ee`; dirty state local
- **Links:** `docs/plans/system-plan.md` v2.0.0; `FL-20260829-ROGERIO-003`; commits locais `47a1d97`, `8b0d556`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

A branch local está 32 commits à frente de sua referência remota e diverge de `origin/main`: possui dois commits exclusivos, enquanto a main possui quatro commits novos relacionados ao harness histórico. Há também alterações locais não commitadas de incident memory, dependência Neo4j, testes e documentação. Era necessário atualizar a base sem descartar esse trabalho ou reescrever commits que ainda não foram publicados.

#### Decisão

Criar um stash temporário incluindo arquivos não rastreados, fazer merge de `origin/main` em `RENATO_CONTINUCAO_ROGERIO` e reaplicar o stash. Não usar rebase nem force-push. Se a reaplicação produzir conflito semântico, interromper a integração e preservar ambos os lados para decisão do owner.

#### Critérios e por que agora

O merge preserva os hashes dos commits locais e torna explícita a integração do harness de `main`; o stash permite atualizar sem transformar trabalho em curso em commit artificial. Os diffs conhecidos em `pyproject.toml` são aditivos e distintos (`numpy` na main e o extra opcional `neo4j` local), mas a reaplicação ainda será validada por teste e diff.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Merge com stash recuperável | preserva histórico e alterações locais; rollback simples | cria commit de merge e exige validar o stash | FACT: branch tem 32 commits não publicados; `main` tem 4 commits exclusivos | escolhida |
| Rebase sobre `origin/main` | histórico linear | reescreve 32 commits locais e pode dificultar recuperação/coordenação | FACT: commits locais ainda são divergentes da main | risco desnecessário |
| Descartar ou commitar forçadamente o dirty state | atualização imediata | perda de trabalho ou commit fora da microtarefa | FACT: arquivos locais incluem testes e código em progresso | incompatível com preservação do trabalho |

#### Evidência, hipóteses e desconhecidos

- **FACT:** preflight do integration-contract-guardian identificou merge-base `4318eba`, 2 commits exclusivos locais e 4 commits exclusivos na main.
- **FACT:** `git diff --check` passou antes da integração; nenhum arquivo local de incident memory coincide com o código novo da main; `pyproject.toml` tem hunks distintos.
- **TEST:** NOT RUN — testes e smoke pós-merge serão executados após a integração.
- **UNKNOWN:** o repositório remoto possui metadados obsoletos de worktrees que impediram o prune no `git fetch`, sem impedir a atualização das referências; avaliar só se voltar a afetar operações Git.

#### Trade-offs aceitos

- **Ganhamos:** base atualizada e rastreável, sem perder trabalho local.
- **Abrimos mão de:** histórico linear nesta branch.
- **Dívida/limitação:** o commit de merge e o stash demandam validação adicional antes de publicação.
- **Risco residual:** conflito tardio na reaplicação do stash; mitigado por parar antes de escolher automaticamente uma resolução.

#### Consequências e propagação

- **Produto/demo:** incorpora o harness histórico da main sem alterar contratos públicos por decisão desta integração.
- **Arquitetura/contratos:** nenhuma mudança de contrato pretendida; conferir `CTR-SCN-001` e componentes de streaming no diff final.
- **Pessoas/branches:** preserva a frente de Rogério e os commits que ainda não estão em `origin/RENATO_CONTINUCAO_ROGERIO`.
- **Plano/Linear:** nenhum estado do Linear será escrito; o plano permanece a fonte arquitetural.
- **Testes/observabilidade:** rodar os testes afetados pelo harness e pelo incidente, além de `git diff --check`; comportamento observável requer browser gate se a API/UI local for alterada.

#### Validação e trial by fire

- **Hipótese verificável:** após merge e reaplicação, a branch contém os commits de `origin/main`, as alterações locais continuam presentes e a suíte relevante passa.
- **Caminho feliz:** merge limpo, stash aplicado e imports/testes de `simulation`, `streaming` e `incidents` executados.
- **Caso difícil/adverso:** conflito no `pyproject.toml` ou no Flight Log; preservar as duas alterações e classificar a integração como bloqueada até decisão explícita.
- **Resultado observado:** NOT RUN — integração em andamento.
- **Fallback:** abortar o merge ou reaplicar o stash no `ORIG_HEAD`; nenhum push ou reescrita remota será feito.

#### Gatilhos de revisão

Conflito de reaplicação, falha de testes críticos, descoberta de mudança contratual não documentada ou necessidade de publicar a branch; qualquer um exige novo parecer de integração.

#### Adendos

- **2026-08-29T21:14:00-03:00:** `git merge origin/main` foi interrompido e abortado de forma segura. Há dois conflitos semânticos: `app/api/__init__.py` precisa decidir se expõe apenas `transactions_router` ou também `events_router`; `main.py` precisa compor ou priorizar o `reconcile_stuck()` do lifecycle de transações e o worker de ingestão histórica. Nenhum lado foi escolhido automaticamente. O stash temporário foi reaplicado com sucesso e removido; o trabalho local permanece preservado. Classificação do integration-contract-guardian: `BLOCKED` até decisão do owner sobre essa composição e validação subsequente.
- **2026-08-29 (Claude, suplência):** merge real de `RENATO_CONTINUCAO_ROGERIO` e `feat/OBJ-ROGERIO-001-platform-core` em `main`, feito primeiro numa branch de simulação. Os dois conflitos semânticos acima foram resolvidos preservando ambos os lados: `app/api/__init__.py` inclui `events_router` e `transactions_router`; `main.py` compõe `create_app()` (CORS + `reconcile_stuck()`) e o `IngestionListenerWorker` no mesmo `lifespan`. Suíte completa validada após cada merge (`pytest -q`).

### FL-20260829-ROGERIO-006 — Usar CORS opt-in e health crítico para o Railway Volume

- **Timestamp:** 2026-08-29T21:20:57-03:00
- **Status:** ACCEPTED
- **Decision owner:** Rogério
- **Participantes:** Rogério; Codex como implementador
- **Categoria:** operations | contract | security
- **Escopo:** `TASK-DEPLOY-API-001` / `LUM2-60`; `CMP-DEPLOY-001`; `CTR-DEP-001 v1`
- **Links:** `DEC-016`; `DEC-017`; `docs/plans/system-plan.md` v2.0.0; `docs/plans/deployment-vercel-railway.md`; `railway.toml`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

A API v3 e o worker usam DuckDB persistente, mas o runtime ainda não aplicava CORS nem distinguia uma aplicação viva de um store ou reconciliação indisponível. A Vercel só pode acessar a API Railway por browser, enquanto o Volume impede múltiplas réplicas simultâneas no MVP.

#### Decisão

Manter uma única réplica Railway com Volume em `/data`; configurar CORS somente por `CORS_ALLOWED_ORIGINS` em lista explícita, sem wildcard e sem credentials; e configurar `/v1/health` como health check de deploy, retornando `503` se DuckDB ou a reconciliação inicial do worker falharem. Neo4j e OpenAI permanecem dependências opcionais e aparecem como estado degradado sem impedir o boot.

#### Critérios e por que agora

O browser precisa de origins exatos para consumir a API, e um deploy não pode receber tráfego antes de abrir o banco montado e reconciliar registros presos. Permitir `*` facilitaria a demo local, mas quebraria a fronteira definida em DEC-016. Tratar Neo4j/OpenAI como críticos impediria o fallback determinístico já contratado.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Allowlist CORS e health crítico de API/store/worker | protege a fronteira e bloqueia deploy inconsistente | exige configurar cada origin Vercel | FACT: DEC-016 exige allowlist e domínio Railway público | escolhida |
| `CORS=*` para a demo | configuração rápida | expõe a API a origins não autorizadas | FACT: browser acessa o data plane Railway | viola DEC-016 |
| Falhar o health por Neo4j/OpenAI indisponível | sinalização máxima de dependências | derruba os fallbacks contratados | FACT: `MEMORY_UNAVAILABLE` e template determinístico são estados válidos | incompatível com contratos |

#### Evidência, hipóteses e desconhecidos

- **FACT:** Railway usa um endpoint HTTP 200 no deploy e Volume-backed deployments não têm sobreposição sem pequena indisponibilidade.
- **FACT:** `CORS_ALLOWED_ORIGINS` e `LUMEN_DATA_DIR` são as variáveis previstas pelo plano de deployment.
- **TEST:** NOT RUN — deploy real requer conta/Volume Railway e será registrado apenas se executado.
- **UNKNOWN:** os domínios Vercel production/preview ainda não existem; devem ser configurados sem inventar URLs antes do deploy.

#### Trade-offs aceitos

- **Ganhamos:** deploy falha cedo quando não pode preservar nem retomar o lifecycle, sem expor stores ao browser.
- **Abrimos mão de:** CORS local automático e zero-downtime em volume persistente.
- **Dívida/limitação:** há uma réplica e health não substitui monitoramento contínuo pós-deploy.
- **Risco residual:** allowlist esquecida bloqueia uma preview; a resposta CORS e o runbook tornam a causa observável.

#### Consequências e propagação

- **Produto/demo:** `BACKEND UNAVAILABLE` é honesto quando API crítica não sobe; browser só usa a API HTTPS autorizada.
- **Arquitetura/contratos:** implementa sem alterar `CTR-DEP-001 v1`, `CTR-API-001 v3` ou dados públicos.
- **Pessoas/branches:** André recebe a variável de base URL e deve fornecer origins reais para a allowlist antes da preview.
- **Plano/Linear:** `LUM2-60` está em andamento; nenhum outro estado é atualizado por esta decisão.
- **Testes/observabilidade:** cobrir CORS permitido/negado, health degradado, restart local e smoke HTTP; validar Railway real em seguida.

#### Validação e trial by fire

- **Hipótese verificável:** uma origin autorizada recebe headers CORS, uma alheia não; o health só retorna 200 após DuckDB e reconciliação inicial.
- **Caminho feliz:** Volume `/data` preserva um batch após restart e `/v1/health` fica 200.
- **Caso difícil/adverso:** mount ausente ou worker falha na reconciliação; deploy não passa no health check e não é promovido.
- **Resultado observado:** NOT RUN — implementação e testes locais pendentes.
- **Fallback:** manter o deploy anterior; corrigir env/mount sem trocar API pública ou migrar store.

#### Gatilhos de revisão

Necessidade de mais de uma réplica, falha do Volume, autenticação por cookie, ou mudança nos domínios Vercel exige novo change control.

#### Adendos

- **2026-08-29T21:34:00-03:00:** durante o smoke local, um Volume legado sem `lease_owner`/`lease_expires_at` fez a reconciliação retornar `BinderException` e o health ficou `503`. Foi adicionada migração DuckDB aditiva e idempotente (`ADD COLUMN IF NOT EXISTS`) antes da reconciliação; não altera contrato público nem apaga registros. PASS: `python -m pytest -q tests/test_deploy_runtime.py` executou 5 testes, incluindo upgrade de schema legado e persistência de batch em arquivo através de restart; `python -m pytest -q` executou 78 testes. `railway.toml` foi validado por `tomllib` e `git diff --check` passou. Docker não está instalado localmente; o build de imagem e o smoke Railway com Volume/origins reais permanecem `NOT RUN`. O navegador embutido bloqueou `localhost`/`127.0.0.1` antes de carregar a API; CORS foi validado por TestClient, sem declarar browser acceptance executado.
- **2026-08-29T21:38:00-03:00:** `code-review-gate` classificou o diff de `LUM2-60` como `PASS` após rejeitar origins CORS com path. `integration-contract-guardian` em modo `INTEGRATION` classificou o checkpoint local como `READY WITH WARNINGS`: nenhum schema/contrato público foi alterado, `scripts/validate_contracts.py`, `compileall`, `git diff --check` e a suíte de 78 testes passaram, e os IDs do Flight Log são únicos. Warning bloqueante apenas para encerrar a issue: build/deploy Railway, Volume e browser consumer reais continuam sem evidência local.

### FL-20260830-ROGERIO-032 — Isolar a avaliação causal e canonicalizar fatos opcionais antes da simulação

- **Timestamp:** 2026-08-30T12:30:00-03:00
- **Status:** VALIDATED
- **Decision owner:** Team
- **Participantes:** Rogério
- **Categoria:** quality | data | AI/RAG | operations
- **Escopo:** `CTR-EVAL-001 v1`, `app/evaluation/`, `scripts/run_conversion_evaluation.py`, adaptador de outcomes
- **Links:** `CTR-EVAL-001 v1`, `CTR-AGT-002 v1`, `tests/test_conversion_evaluation.py`, `tests/test_transaction_flow_evaluation.py`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

A avaliação exigida usa CSVs sintéticos com outcomes controlados, enquanto a API pública recebe apenas fatos e deriva outcomes próprios. Era necessário medir causalidade sem expor artefatos internos, sem criar rota de avaliação e sem fazer um fallback de memória parecer Graph RAG validado.

#### Decisão

Adicionar um harness interno que aceita somente pacotes de agente e CSVs abaixo de `datasets/`, calcula comparações pré/pós e recortes de forma determinística, gera bundles nativos e declara `fallback_used=true`. Canonicalizar o campo opcional `provider_response_code` na seed para que uma transação gerada e a mesma transação validada pela API tenham outcome idêntico.

#### Critérios e por que agora

O contrato do adaptador proíbe enviar o CSV diretamente à API transacional e exige que a ausência de Graph RAG seja verificável. A suíte completa também revelou que a serialização opcional mudava uma latência para fatos idênticos, invalidando a invariância de transporte.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Enviar CSV à API pública | usa a rota existente | recalcula outcomes e perde o sinal controlado | FACT: contrato do adaptador | viola equivalência da avaliação |
| Criar endpoint de avaliação | simplifica a execução | expõe uma superfície não operacional e mistura responsabilidades | FACT: `CTR-EVAL-001` é interno | rejeitada |
| Harness interno isolado | preserva dados, contratos públicos e auditoria | não comprova Graph RAG sem Neo4j | TEST: adapter report | escolhida |

#### Evidência, hipóteses e desconhecidos

- **TEST:** `tests/test_conversion_evaluation.py`, `tests/test_transaction_flow_evaluation.py` e `tests/test_transaction_outcomes.py` — 12 passed.
- **TEST:** bateria sintética seed `20260830` — 40/40, 100% normalizado, usando o scorer oficial.
- **FACT:** `lumenprep-adapter-report.json` registra 0/20 Graph RAG confirmado; o modo degradado foi explícito.
- **UNKNOWN:** prova de Neo4j/Graph RAG real requer instância configurada; não foi simulada.

#### Trade-offs aceitos

- **Ganhamos:** diagnóstico reproduzível, causal e sem vazamento de artefato interno.
- **Abrimos mão de:** usar a API pública como atalho de avaliação.
- **Dívida/limitação:** o harness é uma adaptação offline e não substitui o detector streaming de produção.
- **Risco residual:** regras de recorte precisam ser reavaliadas com novas seeds e distribuições antes de generalização operacional.

#### Consequências e propagação

- **Produto/demo:** nenhuma rota, tela ou ação de pagamento nova.
- **Arquitetura/contratos:** adiciona somente `CTR-EVAL-001 v1` interno; contratos públicos permanecem congelados.
- **Pessoas/branches:** Rogério coordena `app/`, scripts e documentação; web não é alterada.
- **Plano/Linear:** plano geral atualizado; Linear não alterado por falta de autorização.
- **Testes/observabilidade:** normalizador e scorer oficiais são o checkpoint externo; trace degradado não pode ser omitido.

#### Validação e trial by fire

- **Hipótese verificável:** os mesmos pacotes e seed produzem bundles e respostas repetíveis sem acesso a metadados internos.
- **Caminho feliz:** geração → runner → normalizador → scorer devolve 40/40.
- **Caso difícil/adverso:** controles retornam sem irregularidade e sinais concorrentes retornam incerteza; um `null` opcional não muda outcome.
- **Resultado observado:** PASS para avaliação causal e testes focados; Graph RAG: NOT RUN/UNAVAILABLE de forma explícita.
- **Fallback:** `MEMORY_UNAVAILABLE`/`fallback_used=true`, sem inventar precedente ou ação.

#### Gatilhos de revisão

Mudança no pacote de avaliação, schema de entrada, métrica temporal, política de memória ou uma seed que revele falsa atribuição exige nova rodada e adendo.

#### Adendos

- **Code Review Gate:** pendente da revisão final do diff.
- **Browser acceptance:** pendente do fluxo web local; o harness não possui UI própria.
- **Integration Contract Guardian (INTEGRATION):** pendente da checagem final de compatibilidade.

- **2026-08-30T12:55:00-03:00 — evidência final:** `python -m pytest -q --basetemp artifacts\\pytest-full-final-20260830` — **259 passed**; `scripts/validate_contracts.py` e `compileall` passaram. A bateria oficial seed `20260830` marcou **40/40 (100%)**, estrito 100% e parcial 100%.
- **Code Review Gate:** PASS. Revisados o isolamento de caminhos do runner, ausência de rota pública, declaração explícita de fallback, recortes/controles/incerteza e canonicalização da seed. Não há achado bloqueante no diff.
- **Browser acceptance:** PASS WITH LIMITATIONS. Em navegador local, `Generate samples` → `Submit batch` → Logs → detalhe `NO_INCIDENT` → `/incidents` funcionou contra FastAPI real, com CORS preflight e console sem erros. `npm run lint` e `npm run build` passaram; `npm test` fora do sandbox passou com 42 testes e 1 skip. A tela de Incident suportado não foi materializada nesta execução.
- **Integration Contract Guardian (INTEGRATION):** READY WITH WARNINGS. `CTR-EVAL-001 v1` está registrado como interno e não altera schemas, endpoints, consumidores web ou migrations. O adapter report registra 0/20 traces Graph RAG confirmados porque Neo4j não estava configurado; Docker Desktop também não estava ativo para uma prova local. O gate final não é `PASS` até comprovar Graph RAG sem fallback.

- **2026-08-30T13:20:00-03:00 — adendo de prova Graph RAG:** o runner agora oferece `--require-graph-rag`. Nessa opção, ele cria o runtime Neo4j já adotado pelo projeto, propaga o trace nativo e falha se `fallback_used=true` ou `memory_status=MEMORY_UNAVAILABLE`; portanto não pode transformar fallback em confirmação. Os testes cobrem tanto trace primário sem precedente quanto a rejeição do fallback. A prova de 20/20 continua pendente somente porque o daemon Docker/Neo4j local está indisponível.

- **2026-08-30T13:35:00-03:00 — gates finais desta rodada:** `pytest -q --basetemp artifacts\\pytest-full-graph-gate-20260830` — **261 passed**; `compileall`, `validate_contracts.py` e `git diff --check` passaram. A bateria oficial seed `20260830` foi repetida e manteve **40/40 (100%)**. `docker info` confirmou que o cliente não alcança `//./pipe/docker_engine`; por isso a execução de `--require-graph-rag` contra Neo4j real permanece bloqueada e o gate final não pode ser marcado `PASS`.

- **2026-08-30T14:00:00-03:00 — prova remota Graph RAG:** o deploy Railway pode comprovar Neo4j sem Docker local. Foi adicionado `scripts/probe_railway_graph_rag.py`, um leitor HTTPS sem credenciais, sem retries e sem escrita que exige health saudável, Neo4j configurado e ao menos um Incident com `fallback_used=false`. A avaliação causal continua isolada no harness: o probe não recebe nem envia CSVs, ground truth ou dados de pagamento. O resultado remoto permanece `NOT RUN` até a URL pública do serviço Railway estar disponível nesta sessão.

- **2026-08-30T14:15:00-03:00 — Graph RAG Railway confirmado:** após autorização, um batch de 100 transações exclusivamente sintéticas com resposta `68` materializou `inc_homogeneous_49f565ea1615409c`. O probe HTTPS somente leitura confirmou `memory_status=NO_PRECEDENT`, `candidate_count=6`, `index_version=structured-v1` e `fallback_used=false`. A ausência de precedente é um resultado de memória válido; o trace prova que a consulta usou Neo4j primário, sem Docker local e sem transformar memória em causa ou remediação.

## Renato

<!-- RENATO: faça append de novas entradas ao final desta seção. -->

### FL-20260829-RENATO-001 — Fixar Python 3.14.4 e uma base sem dependências para o primeiro incremento

- **Timestamp:** 2026-08-29T17:32:02-03:00
- **Status:** ACCEPTED
- **Decision owner:** Renato
- **Participantes:** Renato; Codex como recorder
- **Categoria:** architecture | quality | operations | Git/integration
- **Escopo:** ambientação compartilhada anterior a `TASK-DATA-001` / `LUM2-43`
- **Links:** `docs/plans/system-plan.md` v1.3.1; `pyproject.toml`; `FL-20260829-TEAM-005`; `DEC-004`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O repositório contém contratos e planos, mas não possuía runtime Python, launcher, arquivo de projeto ou layout de pacote. Renato solicitou que a ambientação fosse integrada diretamente na `main` antes do primeiro código compartilhado de geração.

#### Decisão

Fixar Python 3.14.4 em `.python-version` e `pyproject.toml`; usar `app/` como pacote compatível com os diretórios previstos no plano e `unittest` da biblioteca padrão para os primeiros checks. Não commitar ambiente virtual, binários ou dependências especulativas.

#### Critérios e por que agora

A tarefa de geração precisa de um comando de teste e uma versão de runtime comum antes que os componentes paralelos criem dependências divergentes. O gerador ainda não exige NumPy, Polars, FastAPI ou Neo4j nesta etapa.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Fixar Python 3.14.4 sem dependências | ambiente mínimo, reprodutível e sem lockfile prematuro | bibliotecas de dados serão adicionadas depois | FACT: o repositório não contém aplicação nem dependências | escolhido pelo escopo atual |
| Adicionar toda a stack do MVP agora | aparenta acelerar as tarefas seguintes | antecipa versões, lockfile e decisões dos demais owners | FACT: as tarefas de ingestão, API e memória têm owners distintos | excede a ambientação solicitada |
| Manter apenas instruções informais | nenhum arquivo novo | versões e comandos podem divergir entre máquinas | FACT: não há runtime Python instalado localmente | não oferece reprodução verificável |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `python`, `py` e `winget` não estavam disponíveis localmente antes da ambientação.
- **TEST:** NOT RUN — será registrado após instalar o runtime e executar o smoke test.
- **ASSUMPTION:** Python 3.14.4 executará o esqueleto inicial somente com biblioteca padrão; validar nesta entrega.
- **UNKNOWN:** a compatibilidade de wheels de NumPy/Polars será verificada na tarefa que as introduzir.

#### Trade-offs aceitos

- **Ganhamos:** um ponto de partida comum e pequeno para o trabalho paralelo.
- **Abrimos mão de:** instalar antecipadamente o stack analítico completo.
- **Dívida/limitação:** o lockfile será necessário ao introduzir a primeira dependência de runtime.
- **Risco residual:** outro componente pode requerer biblioteca incompatível; a resolução ocorrerá na respectiva tarefa com change control se afetar o ambiente compartilhado.

#### Consequências e propagação

- **Produto/demo:** nenhuma mudança de comportamento.
- **Arquitetura/contratos:** não altera `CTR-SCN-001` nem schemas congelados.
- **Pessoas/branches:** os demais owners passam a partir da mesma versão de Python na `main`.
- **Plano/Linear:** plano geral atualizado para 1.3.1; nenhum estado do Linear será alterado.
- **Testes/observabilidade:** `python -m unittest discover -s tests` será o smoke test inicial.

#### Validação e trial by fire

- **Hipótese verificável:** uma máquina limpa consegue identificar a versão exigida e executar a descoberta de testes.
- **Caminho feliz:** Python 3.14.4 executa o smoke test sem dependência externa.
- **Caso difícil/adverso:** a instalação do runtime falha; o commit não inclui binários e documenta a condição para reproduzir em outra máquina.
- **Resultado observado:** NOT RUN — pendente da instalação.
- **Fallback:** usar o instalador oficial da Python Software Foundation para 3.14.4 e repetir o smoke test.

#### Gatilhos de revisão

Introdução da primeira dependência de runtime, falha em Python 3.14.4 ou exigência de uma ferramenta de ambiente incompatível.

#### Adendos

- **2026-08-29T17:37:00-03:00:** o instalador MSI oficial retornou `0x80070003` antes de instalar qualquer pacote; o log aponta falha de acesso ao `core.msi` no Package Cache. Como fallback sem binários versionados, `scripts/bootstrap-python.ps1` baixou o pacote embeddable oficial, validou o SHA-256 publicado e preparou `.python-runtime/`. O runtime reportou `Python 3.14.4`, importou `app` e a descoberta inicial de testes foi executada; o smoke test com casos reais será executado após sua inclusão nesta alteração.
- **2026-08-29T17:38:00-03:00:** PASS: `.\\.python-runtime\\python.exe -m unittest discover -s tests -v` executou 2 testes; a checagem `tomllib` confirmou `project.requires-python == "==3.14.4"`; `git diff --check` passou.
- **2026-08-29T17:41:00-03:00:** `code-review-gate` classificou o diff como `PASS` após remover uma linha em branco extra em `pyproject.toml`; `integration-contract-guardian` em modo `INTEGRATION` classificou o checkpoint como `READY`. Foram confirmados `HEAD`, `origin/main` e merge-base em `28dfcbd`, ausência de mudança em schemas/consumidores, testes de smoke e preservação de `LumenPrep/` fora do índice.

### FL-20260829-RENATO-002 — Configurar um baseline de 360 milhões de attempts por regras condicionais

- **Timestamp:** 2026-08-29T17:43:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** Renato
- **Participantes:** Renato; Codex como recorder
- **Categoria:** data | architecture | quality | demo
- **Escopo:** `TASK-DATA-001` / `LUM2-43`; `CMP-DATA-001`; `CTR-SCN-001` v1 provisório
- **Links:** `docs/plans/system-plan.md` v1.3.1; `docs/plans/people/renato.md`; `contracts/v1/scenario.schema.json`; `config/generator/v1/default.json`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O gerador ainda não existe e precisa de valores iniciais configuráveis, suficientemente grandes para representar um baseline de produção, mas sem tornar a primeira tarefa responsável por materializar centenas de milhões de linhas. O schema definitivo depende de `LUM2-28`; Renato autorizou o uso do schema v1 atual como provisório desde que seja substituível.

#### Decisão

Usar 360 milhões de attempts lógicos em 90 dias, com três países (BR, MX, CO), três merchants, três providers e três categorias de método. País é a distribuição base; merchant, provider e método são probabilidades condicionais declaradas por país. A configuração será JSON versionado e o parser de cenário ficará atrás de um protocolo/adaptador provisório de `CTR-SCN-001` v1.

#### Critérios e por que agora

O volume representa centenas de milhões sem impor custo de geração nesta microtarefa. Regras condicionais tornam combinações novas possíveis e evitam uma tabela cartesiana hardcoded; o adaptador protege o gerador contra a mudança contratual pendente.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| JSON versionado com condições por país | editável, testável e extensível sem alterar schema | exige validação explícita das probabilidades | FACT: CTR-SCN-001 aceita dimensões conhecidas e filtros abertos | escolhido |
| Regras fixadas em código | implementação inicial curta | substituição do schema e tuning exigem mudanças de código | FACT: a banca pode escolher combinação nova | reduz controlabilidade |
| Materializar 360 milhões de linhas agora | produz imediatamente o histórico completo | custo desnecessário e bloqueia tarefas seguintes | FACT: LUM2-43 define dimensões e probabilidades, não os 90 dias | fora do escopo |

#### Evidência, hipóteses e desconhecidos

- **FACT:** o plano exige geração determinística, seed, probabilidades condicionais e ground truth isolado.
- **TEST:** NOT RUN — os testes de cardinalidade, normalização e adaptador serão executados nesta tarefa.
- **ASSUMPTION:** BR/MX/CO e três valores por dimensão cobrem a primeira fatia e os cenários de demo; Renato reavalia ao implementar os cenários seguintes.
- **UNKNOWN:** as taxas calibradas contra dados reais não existem, pois o dataset é sintético.

#### Trade-offs aceitos

- **Ganhamos:** configuração transparente, reprodutível e barata de testar.
- **Abrimos mão de:** realismo calibrado em dados de produção.
- **Dívida/limitação:** a geração vetorizada e a sazonalidade ficam para tarefas posteriores.
- **Risco residual:** distribuições iniciais podem não produzir casos difíceis suficientes; os evals futuros ajustam parâmetros sem ler ground truth no detector.

#### Consequências e propagação

- **Produto/demo:** permite construir baseline e cenários com escopo visível.
- **Arquitetura/contratos:** consome provisoriamente `CTR-SCN-001` v1 sem mudar seu arquivo; a troca fica localizada no adaptador.
- **Pessoas/branches:** Rogério e André receberão uma configuração e fixture estáveis, sem acesso a ground truth.
- **Plano/Linear:** nenhum estado no Linear será alterado; a configuração é a evidência da microtarefa.
- **Testes/observabilidade:** testes verificam seed, cardinalidade, probabilidades normalizadas e rejeição de payload de cenário incompleto.

#### Validação e trial by fire

- **Hipótese verificável:** a mesma configuração produz o mesmo fingerprint e cada distribuição soma 1.
- **Caminho feliz:** cenário `provider=stripe AND country=BR` do fixture passa pelo adaptador provisório.
- **Caso difícil/adverso:** um payload sem efeito ou sem seed é rejeitado antes de alcançar o gerador.
- **Resultado observado:** NOT RUN — pendente da implementação.
- **Fallback:** substituir apenas o adaptador por uma implementação do schema validado em `LUM2-28`.

#### Gatilhos de revisão

Schema definitivo incompatível, necessidade de quarta dimensão/cardinalidade ou eval que revele distribuição incapaz de formar o cenário de demonstração.

#### Adendos

- **2026-08-29T17:52:00-03:00:** PASS: `.\\.python-runtime\\python.exe -m unittest discover -s tests -v` executou 10 testes. O baseline declarou 360.000.000 attempts lógicos / 90 dias, `low_sample_attempts=12`, cardinalidade 3 em cada dimensão e fingerprint `bf5ff7ed8ea6f112e561af3c104ab2398f3e008c2cced16b036f1005575d958b`. `compileall` e `git diff --check` também passaram.
- **2026-08-29T17:55:00-03:00:** `code-review-gate`: `PASS`, sem achados bloqueantes. `integration-contract-guardian` em modo `INTEGRATION`: `READY`; merge-base com `origin/main` em `cf20447`, nenhum arquivo em `contracts/` ou `pyproject.toml` modificado, handoff localizável em `config/generator/v1/default.json` e `app/simulation/`, e os 10 testes passaram.
- **2026-08-29T17:53:30-03:00:** `LUM2-43` foi marcado como `Done` no Linear após o commit `97b966c`, sem alterar sua descrição, relações ou contrato.
- **2026-08-29T17:57:10-03:00:** Renato autorizou publicar `renato/define-generator` em `origin` depois dos gates `PASS`/`READY`; o push inclui somente os commits `97b966c` e `873065f` mais este registro, mantendo `LumenPrep/` fora do Git.

### FL-20260829-RENATO-003 — Usar CTR-SCN-001 validado por LUM2-28 como contrato de entrada

- **Timestamp:** 2026-08-29T17:46:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** Renato
- **Participantes:** Renato; Rogério como produtor do contrato; Codex como recorder
- **Categoria:** contract | integration | data
- **Escopo:** `TASK-DATA-001` / `LUM2-43`; `CTR-SCN-001` v1; `LUM2-28`
- **Links:** `LUM2-28`; `contracts/v1/scenario.schema.json`; `contracts/fixtures/scenario-provider-br.json`; `FL-20260829-RENATO-002`
- **Supersedes / superseded by:** substitui a condição provisória de `FL-20260829-RENATO-002`; a decisão de dimensões e probabilidades permanece válida

#### Contexto e pergunta

Depois de iniciada a tarefa, Rogério concluiu `LUM2-28`. Era necessário decidir se a tarefa 43 continuaria com um contrato provisório ou se passaria a depender diretamente da definição já validada.

#### Decisão

Consumir `contracts/v1/scenario.schema.json` e o fixture correspondente como `CTR-SCN-001` v1 validado por Rogério. A tarefa 43 não altera o schema, não importa a branch inteira de Rogério e encapsula sua leitura em um adaptador para uma futura versão contratual.

#### Critérios e por que agora

O bloqueio foi removido e a fonte de verdade está disponível. Manter um adapter provisório criaria duplicação e risco de divergência sem benefício.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Consumir o CTR-SCN-001 validado | um único contrato e fixture compartilhados | integração posterior precisa preservar a interface do adaptador | FACT: LUM2-28 está `Done` e o schema é idêntico ao arquivo canônico | escolhido |
| Manter schema provisório paralelo | isolamento temporário | divergência de validação e duplicação | FACT: o bloqueio da tarefa foi removido | não há benefício restante |
| Integrar toda a branch de Rogério | disponibiliza a stack completa agora | mistura múltiplas tarefas e dependências fora do escopo | FACT: o diff contém ingestion, API e integração além dos contratos | fora do escopo de LUM2-43 |

#### Evidência, hipóteses e desconhecidos

- **FACT:** Linear registra `LUM2-28` como `Done` em 2026-08-29T20:26:31Z.
- **FACT:** o schema e fixture de cenário na branch de Rogério são iguais aos arquivos canônicos atuais.
- **TEST:** NOT RUN — os testes da tarefa 43 usarão ambos os arquivos canônicos.
- **UNKNOWN:** a ordem de merge da branch completa de Rogério será tratada no checkpoint de integração próprio.

#### Trade-offs aceitos

- **Ganhamos:** aderência ao contrato validado sem antecipar dependências.
- **Abrimos mão de:** usar agora o validador `jsonschema` existente apenas na branch de Rogério.
- **Dívida/limitação:** o adaptador local cobre somente a fronteira usada pelo gerador até a integração do validador completo.
- **Risco residual:** o schema v2 futuro exige novo adaptador, não alteração das regras de distribuição.

#### Consequências e propagação

- **Produto/demo:** cenários de demonstração passam pela mesma definição compartilhada.
- **Arquitetura/contratos:** `CTR-SCN-001` v1 é consumido, não modificado.
- **Pessoas/branches:** o handoff de Rogério fica explícito e a branch de Renato não importa componentes alheios.
- **Plano/Linear:** dependência resolvida no Linear; nenhum estado será escrito pela tarefa 43.
- **Testes/observabilidade:** fixture canônico é aceito e um payload inválido é rejeitado.

#### Validação e trial by fire

- **Hipótese verificável:** trocar a implementação do adaptador não altera o carregamento da configuração.
- **Caminho feliz:** fixture `scenario-provider-br.json` é aceito.
- **Caso difícil/adverso:** campo obrigatório ausente ou campo extra é rejeitado no limite do adaptador.
- **Resultado observado:** NOT RUN — pendente da implementação.
- **Fallback:** manter o mesmo protocolo e substituir somente a implementação pelo validador completo de Rogério durante a integração.

#### Gatilhos de revisão

Alteração de `CTR-SCN-001`, integração da branch de Rogério ou um consumidor que exija validação JSON Schema completa nesta branch.

#### Adendos

- **2026-08-29T17:52:00-03:00:** PASS: o adapter aceitou `contracts/fixtures/scenario-provider-br.json`, rejeitou `seed` ausente, campo `ground_truth` e timestamp sem timezone, e preservou o caso permitido pelo schema de filtros vazios. A configuração referencia o schema canônico por `scenario_contract.schema_path`.
- **2026-08-29T17:55:00-03:00:** `LumenPrep/` permaneceu não rastreado e fora do índice; a branch de Rogério não foi integrada nesta microtarefa. O consumidor futuro pode trocar `ScenarioV1Contract` sem alterar as regras declarativas de distribuição.

### FL-20260829-RENATO-004 — Desativar o repositório Git duplicado da pasta pai

- **Timestamp:** 2026-08-29T18:05:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** Renato
- **Participantes:** Renato; Codex como recorder
- **Categoria:** operations | Git/integration
- **Escopo:** `Projeto/.git`; raiz operacional `Projeto/LumenPrep/`
- **Links:** `LumenPrep/.git`; `docs/flight-log.md`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

`Projeto/` e `Projeto/LumenPrep/` possuíam metadados Git independentes para o mesmo trabalho remoto. Isso poderia direcionar comandos e commits futuros à raiz errada.

#### Decisão

Mover `Projeto/.git` para um diretório de backup datado dentro de `Projeto/`, sem apagar arquivos de trabalho e sem alterar `LumenPrep/.git`. A raiz única passa a ser `LumenPrep/`.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Mover para backup recuperável | elimina ambiguidade e preserva reversão | a pasta pai deixa de aceitar comandos Git | FACT: Renato autorizou a desativação | escolhido |
| Apagar `.git` | mesma simplificação | recuperação difícil | nenhuma necessidade de destruição | rejeitado |
| Manter os dois repositórios | nenhuma operação imediata | alto risco de commits na raiz errada | FACT: já ocorreu ambiguidade de raiz | rejeitado |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `LumenPrep/` possui branch `renato/define-generator` rastreando o remoto correto.
- **TEST:** NOT RUN — a estrutura será verificada imediatamente após a movimentação.

#### Trade-offs aceitos

- **Ganhamos:** uma única raiz Git explícita para a equipe.
- **Abrimos mão de:** usar Git diretamente em `Projeto/` até restaurar o backup.
- **Risco residual:** ferramentas abertas na pasta pai deixam de reconhecer Git; mitigado pelo backup datado.

#### Consequências e propagação

- **Pessoas/branches:** todo novo trabalho deve usar `Projeto/LumenPrep/`.
- **Testes/observabilidade:** confirmar que a pasta pai não contém `.git` e que a filha continua com status Git saudável.

#### Validação e trial by fire

- **Hipótese verificável:** `git -C LumenPrep status` continua funcional e `Projeto/.git` deixa de existir.
- **Fallback:** restaurar o diretório de backup ao nome `.git` na pasta pai.

#### Gatilhos de revisão

Necessidade de recuperar histórico local exclusivo da raiz pai ou falha do repositório filho.

#### Adendos

- **2026-08-29T18:10:00-03:00:** a primeira movimentação encontrou atributos ocultos/somente leitura e deixou o Git pai parcialmente deslocado. O backup foi validado com `HEAD=1b39bdd`, igual a `LumenPrep/`; os arquivos de controle foram restaurados apenas para recuperar o estado, e o `.git` residual do pai foi removido depois dessa confirmação. PASS: `Projeto/.git` não existe, o backup datado existe e `git -C LumenPrep status` continua saudável. Para reverter, restaure o backup ao nome `.git` na pasta pai.

### FL-20260829-RENATO-005 — Reclassificar o stream histórico validado como harness interno do plano transaction-first

- **Timestamp:** 2026-08-29T19:54:56-03:00
- **Status:** ACCEPTED
- **Decision owner:** Renato
- **Participantes:** Renato; Codex como recorder; plano 2.0 publicado por André
- **Categoria:** architecture | data | contract | integration
- **Escopo:** `LUM2-44` concluída, `renato/tarefa44@602ae9d`, `CMP-DATA-001`, `CMP-HARNESS-001`, `TASK-DATA-009 / LUM2-62`, `CTR-TXN-001 v1`, `CTR-TXL-001 v1`
- **Links:** `docs/plans/system-plan.md` v2.0.1; `docs/plans/people/renato.md`; `FL-20260829-TEAM-015`; `FL-20260829-TEAM-017`
- **Supersedes / superseded by:** não altera as decisões públicas `DEC-015..017`; substitui a classificação local anterior de servidor como fronteira de produto

#### Contexto e pergunta

A branch `renato/tarefa44` implementou e validou geração histórica de 90 dias e publicação/consumo por servidor local. Depois disso, a `main` publicou o plano 2.0, que torna batches de `TransactionInput` a única entrada pública e deixa `CTR-TXN/TXL/API v3` como especificação congelada, porém ainda não implementada. Era necessário decidir se a documentação da tarefa 44 substituiria esses contratos ou seria preservada como evidência reutilizável.

#### Decisão

Preservar a geração determinística, a sazonalidade, o caso de baixa amostra e a separação producer/consumer como harness interno. Não publicar o endpoint/fila local da branch como API pública e não alterar `CTR-TXN/TXL/API v3`. `TASK-DATA-009 / LUM2-62` adapta esse harness para a batch API comum e o lifecycle durável antes de integração funcional.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência | Decisão |
| --- | --- | --- | --- | --- |
| Promover o endpoint local anterior a API pública | entrega rápida de stream | viola batch/idempotência/lifecycle v3 e duplicaria a fronteira | FACT: plano 2.0 declara API v3 pendente | rejeitada |
| Descartar a implementação da tarefa 44 | elimina diferença documental | perde testes e uma base determinística já validada | TEST: 51 testes e smoke local passaram | rejeitada |
| Reclassificar como harness e adaptar por LUM2-62 | preserva evidência sem quebrar o plano público | exige trabalho de adaptação posterior | FACT: DEC-017 preserva gerador como adapter | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `renato/tarefa44@602ae9d` foi publicada e contém gerador histórico, servidor local, listener e testes.
- **TEST:** 51 testes passaram e o smoke local confirmou publicação `202` seguida de listener cursor/backlog zero na branch.
- **ASSUMPTION:** a lógica determinística pode ser reutilizada sem preservar o transporte local; a validação cabe a `LUM2-62`.
- **UNKNOWN:** o adapter final para `CTR-TXN/TXL` dependerá das implementações de `LUM2-58/59`.

#### Trade-offs aceitos

- **Ganhamos:** continuidade técnica e evidência reprodutível para tráfego de fundo.
- **Abrimos mão de:** integrar imediatamente o servidor/fila local ao produto público.
- **Risco residual:** portar o harness pode introduzir divergência de contratos; contract tests de batch e lifecycle são o gate.

#### Consequências e propagação

- **Arquitetura/contratos:** nenhum contrato v3 é rebaixado ou substituído; a mudança fica registrada no plano geral e no plano de Renato.
- **Pessoas/branches:** Rogério recebe o adapter puro por `LUM2-61`; Renato adapta tráfego por `LUM2-62`; André consome somente a API v3.
- **Linear:** nenhum item concluído é reaberto; o trabalho de adaptação continua em `LUM2-61/62` já sincronizadas.
- **Testes:** reprodução, sazonalidade, baixa amostra e producer/consumer informam os novos contract tests, mas não provam a API pública até a integração.

#### Validação e trial by fire

- **Hipótese verificável:** o harness envia carga sintética somente pela batch API e as métricas mudam apenas após o worker processar o batch.
- **Resultado observado:** NOT RUN para a API v3; implementação correspondente ainda está pendente no plano 2.0.
- **Fallback:** usar fixtures/samples determinísticos de `LUM2-62` enquanto o tráfego de fundo não estiver conectado.

#### Gatilhos de revisão

Mudança nos schemas `CTR-TXN/TXL`, falha de equivalência entre harness e batch API, ou requisito de transporte persistente exige novo change control.

#### Adendos

- **2026-08-29T20:10:32-03:00:** conflitos de merge de `renato/tarefa44@602ae9d` foram resolvidos preservando o plano transaction-first da `main`; o código foi integrado exclusivamente como `CMP-HARNESS-001` no commit `6d6e0b4`. `CTR-TXN/TXL/API v3` não foram promovidos nem alterados. PASS: revisão sem bloqueadores, `python -m pytest -x -vv` com 59 testes aprovados e smoke do Swagger com `POST /transactions` = `202`, `listener_cursor=1` e `backlog=0`, sem erros de console. `LUM2-61/62` permanecem as tarefas de adapter/lifecycle.

### FL-20260829-RENATO-006 — Configurar perfis de latência e decline com fallback sem alterar CTR-EVT-001

- **Timestamp:** 2026-08-29T20:42:43-03:00
- **Status:** ACCEPTED
- **Decision owner:** Renato
- **Participantes:** Renato; Codex como implementador e recorder
- **Categoria:** data | contract | quality
- **Escopo:** `LUM2-46`, `TASK-DATA-004`, `CMP-DATA-001`, `CTR-EVT-001 v1`, `CTR-SCN-001`
- **Links:** `config/generator/v1/default.json`; `app/simulation/outcomes.py`; `app/simulation/historical.py`; `tests/test_simulation_profiles.py`; branch `renato/tarefa46`
- **Supersedes / superseded by:** substitui os placeholders de latência e decline de `TASK-DATA-002`; não altera o schema congelado

#### Contexto e pergunta

O outcome generator e o harness histórico ainda emitiam uma faixa de latência genérica e `GENERIC_DECLINE`, impedindo calibração de p95/timeout e diagnóstico por código. Era necessário adicionar diferenças por provider e códigos brutos/normalizados sem criar uma versão incompatível de `CTR-EVT-001`.

#### Decisão

Usar perfis versionados no config do gerador: p50/p95, multiplicador de timeout e latência do orquestrador por provider; códigos de decline ponderados por provider e status. Um perfil `default` atende providers novos sem mudança de schema. Timeout e erro recebem somente seus códigos técnicos compatíveis; sucesso não recebe decline.

#### Critérios e por que agora

`LUM2-46` precisa desbloquear benchmark e detector com dados observáveis e reproduzíveis. O contrato já comporta `timing.orchestrator_latency_ms` opcional e `decline` normalizado, portanto uma mudança no payload seria custo de integração sem ganho.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Manter valores genéricos no código | menor diff | p95 sem calibração e diagnóstico sem código | FACT: placeholders atuais | não atende `LUM2-46` |
| Adicionar campos ou v2 de `CTR-EVT-001` | pode carregar mais telemetria | exige mudança coordenada de produtores e consumidores | FACT: campos atuais já suportam o dado | custo sem necessidade |
| Perfis no config com fallback | reproduzível, auditável e extensível | parâmetros exigem calibração futura | TEST: distribuição e coerência são verificáveis localmente | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `CTR-EVT-001 v1` aceita timing por estágio e decline bruto/normalizado sem schema novo.
- **TEST:** 62 testes passaram; os testes novos comprovam repetição por seed, ordem de p50/p95 entre providers, baixa amostra, ausência de ground truth e compatibilidade status/código.
- **ASSUMPTION:** os parâmetros representam dados sintéticos plausíveis para a demo, não uma medição de produção.
- **UNKNOWN:** a calibração definitiva dos thresholds depende de `TASK-DATA-005` e dos evals do detector.

#### Trade-offs aceitos

- **Ganhamos:** caudas de latência e declines explicáveis para p95, timeout e RCA.
- **Abrimos mão de:** fidelidade a uma tabela privada de códigos de um adquirente real.
- **Dívida/limitação:** os perfis continuam estáticos e precisam de benchmark/eval antes de qualquer ajuste de threshold.
- **Risco residual:** um provider novo cai no perfil default; o fallback é explícito, mas pode não refletir sua distribuição real.

#### Consequências e propagação

- **Produto/demo:** cenários e tráfego histórico exibem latência e declines coerentes sem expor ground truth.
- **Arquitetura/contratos:** `CTR-EVT-001 v1` permanece compatível; não há change control de schema.
- **Pessoas/branches:** `LUM2-47` pode materializar os dados; detector/RCA recebem códigos normalizados.
- **Plano/Linear:** a issue `LUM2-46` é atualizada para pronta somente após os gates finais e commits desta branch.
- **Testes/observabilidade:** perfis e fallback são cobertos por teste determinístico; benchmark quantitativo fica em `LUM2-47`.

#### Validação e trial by fire

- **Hipótese verificável:** mesma seed repete os eventos e providers mantêm p50/p95 distintos, enquanto falhas carregam decline compatível.
- **Caminho feliz:** gerar eventos normal/histórico, validar schema e consumir na ingestão.
- **Caso difícil/adverso:** provider desconhecido usa fallback, batch de baixa amostra não expõe ground truth e timeout nunca recebe decline de issuer.
- **Resultado observado:** PASS — suíte completa com 62 testes aprovada; interface pública não foi exercitada porque a mudança é interna de geração/harness.
- **Fallback:** perfil `default` mantém eventos válidos até que uma distribuição específica seja configurada.

#### Gatilhos de revisão

Benchmark de `LUM2-47` incompatível, novo provider sem perfil aceitável, ou contrato futuro que exija mais estágios/códigos exige nova decisão e possível change control.

#### Adendos

- **2026-08-29T21:00:00-03:00:** browser acceptance local passou em servidor com `DEMO_MODE=true` e `DUCKDB_PATH=:memory:`. Pelo Swagger, `POST /demo/scenarios/scenario_provider_br/inject` retornou `202 ACCEPTED` com `events_published=54`; em seguida `GET /transactions/health` retornou `published=54`, `listener_cursor=54` e `backlog=0`. Console sem erros; há somente warning pré-existente do Swagger CDN sobre deep-link whitespace.
- **2026-08-29T21:16:00-03:00:** a validação de volume revelou que o correlation ID histórico recalculava o fingerprint completo do config para cada evento. O valor agora é calculado uma vez por gerador, sem alterar payload nem seed. PASS: 13 testes focados em 18,11s e validação de contratos aprovada.

### FL-20260829-ROGERIO-007 — Estender CTR-INC-001 v1 com hipóteses ordenadas sem mudar a causa atual

- **Timestamp:** 2026-08-29T21:50:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** Rogério
- **Participantes:** Rogério; Codex como implementador e recorder
- **Categoria:** contract | product | integration
- **Escopo:** `LUM2-37`, `TASK-INC-003`, `CTR-INC-001 v1`, `CMP-INC-001`, `CMP-MEM/EXP-001`, `CMP-WEB-001`
- **Links:** `docs/plans/system-plan.md` v2.0.3; `contracts/v1/incident.schema.json`; `app/incidents/__init__.py`; `tests/test_incident_serialization.py`
- **Supersedes / superseded by:** adendo compatível a `CTR-INC-001 v1`; não substitui DEC-014 nem muda `CTR-MEM-001`.

#### Contexto e pergunta

`LUM2-37` exigia publicar alternativas causais ordenadas e uma classe de recomendação, mas o contrato congelado expunha apenas a causa atual e `execution=HUMAN_ONLY`. A mudança precisava informar API, memória e UI sem transformar um precedente ou uma hipótese em confirmação causal.

#### Decisão

Adicionar opcionalmente `root_cause.alternatives` e `recommendation_class` a `CTR-INC-001 v1`. O produtor ordena alternativas por confiança decrescente; elas são hipóteses e não modificam `root_cause.status` ou `category`. Recomendações continuam obrigatoriamente `HUMAN_ONLY` e recebem uma classe declarativa (`INVESTIGATE`, `MONITOR` ou `ESCALATE`). Payloads v1 legados sem os campos permanecem aceitos.

#### Critérios e por que agora

A UI precisa distinguir uma causa suportada de hipóteses concorrentes, e a integração já possui consumidores de Incident. Uma extensão aditiva entrega essa leitura sem uma migração de versão durante o hackathon e preserva a regra de que só o RCA confirma a causa atual.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Tornar alternativas obrigatórias e criar v1.1 incompatível | contrato mais rígido | força migração simultânea de fixtures, API, memória e UI | FACT: `CTR-INC-001 v1` já é consumido por componentes integrados | custo de integração desnecessário |
| Usar memory matches como alternativas | menos campos | confunde precedente histórico com hipótese causal atual | FACT: `CTR-MEM-001` é eixo independente de `root_cause` | viola a separação causal |
| Campos aditivos e tolerância a legado | entrega a informação com risco contido | consumidores precisam tratar ausência | TEST: schema e serialização serão cobertos localmente | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `RootCause.status` já restringe a causa atual a `SUPPORTED|INCONCLUSIVE`; `execution` já restringe ações a `HUMAN_ONLY`.
- **TEST:** NOT RUN no momento deste registro; testes de schema, ordenação e eixos causais serão executados antes de concluir.
- **ASSUMPTION:** consumidores ignoram campos opcionais que ainda não exibem.
- **UNKNOWN:** quais classes além de investigação serão úteis na demo final.

#### Trade-offs aceitos

- **Ganhamos:** explicação explícita de hipóteses concorrentes e classificação visual da recomendação.
- **Abrimos mão de:** obrigar todos os payloads legados a carregar alternativas imediatamente.
- **Risco residual:** classes futuras podem pedir enum maior; isso exigirá novo change control.

#### Consequências e propagação

- **Arquitetura/contratos:** plano geral, schema, modelos, fixtures e testes mudam no mesmo commit.
- **Pessoas/branches:** André tolera/exibe os campos quando presentes; Altoé não usa memória para promover nem ordenar alternativas.
- **Linear:** `LUM2-37` só muda para Done após testes, review e gates reais.
- **Testes/observabilidade:** casos SUPPORTED/INCONCLUSIVE comprovam ordenação e preservação da causa atual.

#### Validação e trial by fire

- **Caminho feliz:** Incident serializado contém alternativas em ordem estável e recomendação humana classificada.
- **Caso difícil/adverso:** `INCONCLUSIVE + MATCH_FOUND` continua inconclusivo; alternativa vazia e payload legado são válidos.
- **Resultado observado:** NOT RUN.
- **Fallback:** campos opcionais ausentes preservam o contrato v1 existente.

#### Gatilhos de revisão

Novo tipo de recomendação executável, consumidor que rejeite campo opcional, ou evidência de que memória está promovendo hipótese exige novo change control.

#### Adendos

- **2026-08-29T22:05:00-03:00:** PASS: `python -m pytest -q` aprovou 91 testes, `python scripts/validate_contracts.py` aprovou schemas e fixtures, `python -m compileall -q app` passou e `git diff --check` não reportou erros. Browser acceptance ficou `PASS WITH LIMITATIONS`: o navegador real do Codex bloqueou `http://127.0.0.1:8091/v1/incidents` com `net::ERR_BLOCKED_BY_CLIENT`; o endpoint e os cenários de contrato foram exercitados pela suíte FastAPI, mas não houve consumidor web local para clicar nesta branch.

### FL-20260829-ROGERIO-008 — Priorizar impacto apenas dentro da mesma moeda sem FX implícito

- **Timestamp:** 2026-08-29T22:20:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** Rogério
- **Participantes:** Rogério; Codex como implementador e recorder
- **Categoria:** product | data | quality
- **Escopo:** `LUM2-36`, `TASK-INC-002`, `CTR-INC-001 v1`, `app/incidents/__init__.py`
- **Links:** `docs/plans/system-plan.md` v2.0.4; `tests/test_incident_priority.py`
- **Supersedes / superseded by:** não altera a fórmula de impacto local existente; substitui qualquer ordenação global implícita entre moedas.

#### Contexto e pergunta

O módulo calculava GMV em `amount_minor`, mas o ranking preliminar de candidatos não distinguia moedas. Comparar diretamente um valor em BRL com outro em MXN produziria uma prioridade numérica sem taxa, data ou fonte de câmbio.

#### Decisão

Calcular impacto com ticket médio e aprovações perdidas na moeda da janela e priorizar Incidents por `impact.amount_minor` somente dentro de buckets da mesma `currency`. Sem FX versionado, a saída expõe buckets independentes em vez de uma ordem global artificial.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Comparar `amount_minor` entre moedas | implementação curta | ranking financeiramente inválido | FACT: BRL e MXN possuem unidades diferentes | rejeitada |
| Chamar uma API FX em tempo real | ranking global | nova dependência, latência e dados não reproduzíveis | ASSUMPTION: demo não possui feed FX confiável | fora do MVP |
| Buckets por moeda com ordenação local | determinístico e auditável | UI não recebe um único ranking global | TEST: BRL/MXN podem ser validados sem câmbio | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `WindowMetrics` fornece `amount_minor` e `currency`; `Impact` preserva a moeda local.
- **TEST:** NOT RUN no momento deste registro; serão cobertos BRL, MXN, duplicidade de candidato e ausência deliberada de FX.
- **UNKNOWN:** a moeda de apresentação executiva se a demo exigir comparação internacional.

#### Trade-offs aceitos

- **Ganhamos:** priorização honesta e reproduzível dentro de cada mercado.
- **Abrimos mão de:** ranking único de mercados diferentes.
- **Risco residual:** o consumidor deve apresentar o bucket de moeda, não concatenar listas como se fossem comparáveis.

#### Consequências e propagação

- **Arquitetura/contratos:** nenhuma conversão ou nova dependência externa é adicionada a `CTR-INC-001`.
- **Pessoas/branches:** API/UI devem consumir buckets explicitamente quando exibirem múltiplas moedas.
- **Linear:** `LUM2-36` recebe evidência somente após testes e revisão.

#### Validação e trial by fire

- **Caminho feliz:** maior GMV em BRL aparece antes de menor GMV em BRL; MXN permanece separado.
- **Caso difícil/adverso:** candidatos sobrepostos não duplicam GMV; zero tentativas falha explicitamente; não há FX silencioso.
- **Resultado observado:** NOT RUN.
- **Fallback:** apresentar buckets sem conversão até uma decisão de FX versionada.

#### Gatilhos de revisão

Pedido de ranking global, nova moeda de apresentação, ou fonte FX auditável exige novo change control.

#### Adendos

- **2026-08-29T22:32:00-03:00:** PASS: `python -m pytest -q` aprovou 94 testes; os testes específicos cobriram GMV local, não duplicação de perdas em candidatos correlacionados, buckets BRL/MXN e janela sem tentativas. `python scripts/validate_contracts.py`, `python -m compileall -q app` e `git diff --check` também passaram. Code review gate: PASS, sem achados bloqueantes. Browser acceptance não se aplica: não houve alteração de rota, UI ou fluxo executável no navegador.

### FL-20260829-ROGERIO-009 — Exigir fingerprint causal exato para separar incidentes simultâneos

- **Timestamp:** 2026-08-29T22:45:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** Rogério
- **Participantes:** Rogério; Codex como implementador e recorder
- **Categoria:** data | product | quality
- **Escopo:** `LUM2-35`, `TASK-INC-001`, `CTR-DET-001`, `CTR-INC-001`, `app/incidents/__init__.py`
- **Links:** `docs/plans/system-plan.md` v2.0.5; `tests/test_incident_correlation.py`
- **Supersedes / superseded by:** substitui a compatibilidade parcial de slices para correlação de Incident.

#### Contexto e pergunta

O agrupamento existente aceitava candidates com uma dimensão compartilhada. Assim, um problema de provider no Brasil e uma queda de issuer no mesmo país podiam formar uma narrativa única mesmo com fingerprints causais diferentes.

#### Decisão

Correlacionar apenas candidates com mesmo `correlation_id`, janelas sobrepostas e fingerprint completo de `slice`. Métricas diferentes para o mesmo slice ainda se unem; causa com qualquer dimensão diferente permanece em Incident separado.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Compatibilidade parcial de slice | agrega possíveis relações pai-filho | pode mesclar causas simultâneas por país ou método | FACT: trial by fire inclui incidentes simultâneos | risco de narrativa falsa |
| Agrupar só por correlation_id | implementação mínima | une todo o conteúdo da janela | FACT: correlation cobre janela, não causa | insuficiente |
| Fingerprint exato de slice | determinístico e auditável | pode separar relação pai-filho até haver RCA explícito | TEST: provider BR e issuer MX serão independentes | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `slice` é a saída causal de `CTR-DET-001`; `correlation_id` sozinho representa a janela.
- **TEST:** NOT RUN no momento deste registro; casos de mesmo slice, provider BR e issuer MX serão executados.
- **UNKNOWN:** se o RCA futuro precisa ligar explicitamente uma hipótese pai e filha; isso exigirá contrato de relação, não heurística implícita.

#### Trade-offs aceitos

- **Ganhamos:** dois problemas simultâneos não viram uma causa narrativa falsa.
- **Abrimos mão de:** deduzir hierarquia causal por sobreposição parcial.
- **Risco residual:** um incidente real com slices complementares pode aparecer dividido até o RCA publicar vínculo explícito.

#### Consequências e propagação

- **Arquitetura/contratos:** não muda schema; muda a semântica da correlação do produtor de Incident.
- **Pessoas/branches:** LUM2-36 recebe grupos independentes para priorização; memória/API/UI recebem IDs distintos.
- **Linear:** LUM2-35 recebe evidência após testes e review.

#### Validação e trial by fire

- **Caminho feliz:** métricas approval/latency para o mesmo provider BR formam um Incident.
- **Caso difícil/adverso:** provider BR e issuer MX simultâneos formam dois; mesma country isolada não basta para unir.
- **Resultado observado:** NOT RUN.
- **Fallback:** expor incidents separados até existir vínculo causal explícito.

#### Gatilhos de revisão

RCA que publique relação pai-filho ou trial que demonstre fragmentação inadequada exige novo change control.

#### Adendos

- **2026-08-29T22:55:00-03:00:** PASS: 97 testes completos aprovados; os casos específicos cobriram métricas múltiplas no mesmo slice, provider BR + issuer MX simultâneos e provider/issuer no mesmo país sem mesclagem indevida. Contratos, compilação e `git diff --check` passaram. Code review gate: PASS, sem achados bloqueantes. Browser acceptance não se aplica: não houve alteração de rota, UI ou fluxo executável no navegador.

### FL-20260829-RENATO-007 — Explorar hipóteses por beam determinístico sem afirmar causa

- **Timestamp:** 2026-08-29T23:25:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** Renato
- **Participantes:** solicitante; Codex como implementador e recorder
- **Categoria:** architecture | data | quality | integration
- **Escopo:** `LUM2-54` / `TASK-RCA-001`, `CMP-DET/RCA-001`, `CTR-DET-001 v1`, `CTR-INC-001 v1`
- **Links:** `app/detection/models.py`, `docs/plans/system-plan.md`, `LUM2-53`, `LUM2-55`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

`LUM2-53` já publica `AnomalyCandidate` numérico, mas não existe implementação de `LUM2-54`. O RCA precisa explorar combinações dimensionais sem ler ground truth nem transformar uma hipótese estatística em Incident ou causa confirmada.

#### Decisão

Implementar um módulo interno de beam search que recebe apenas `AnomalyCandidate`, expande prefixes dimensionais configuráveis, elimina ramos abaixo do support mínimo e devolve hipóteses ordenadas com score, evidências e IDs de candidatos. O módulo não cria `Incident`, não muda schemas e não afirma `SUPPORTED`.

#### Critérios e por que agora

O contrato `CTR-DET-001 v1` é a entrada congelada disponível e `LUM2-54` desbloqueia `LUM2-55`. Separar busca de ranking final preserva o handoff planejado e evita que a correlação de Incident assuma causalidade prematuramente.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Buscar diretamente nos eventos/raw | Mais combinações possíveis | mistura armazenamento/ground truth com RCA e aumenta acoplamento | FACT: `LUM2-54` depende de `LUM2-53` | Fora da fronteira da microtarefa |
| Escolher o maior candidate sem exploração | Implementação pequena | perde combinações e pruning hierárquico | FACT: a issue exige beam search top-down | Não satisfaz o aceite |
| Beam interno sobre candidatos | Reproduzível, testável e compatível com contratos v1 | qualidade depende da granularidade dos candidates disponíveis | TEST: a busca terá fixtures de normal, dominante e baixa amostra | Escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `CTR-DET-001` contém slice, support, efeito, confiança e evidências; não contém causa declarada.
- **TEST:** NOT RUN — testes de ordem, pruning e ausência de hipótese em baixa amostra serão executados antes do Linear.
- **UNKNOWN:** o score de dominância e as alternativas públicas pertencem a `LUM2-55`.

#### Trade-offs aceitos

- **Ganhamos:** uma busca causal auditável sem vazamento de ground truth.
- **Abrimos mão de:** explicar relações não representadas pelos slices de entrada.
- **Dívida/limitação:** dimensões ausentes no candidate não podem ser exploradas; o produtor precisa publicar a granularidade necessária.
- **Risco residual:** score de exploração não é confiança causal; o consumidor deve mantê-lo como hipótese.

#### Consequências e propagação

- **Arquitetura/contratos:** `CTR-DET-001 v1` é somente consumido; `CTR-INC-001 v1` não muda.
- **Pessoas/branches:** `LUM2-55` recebe hipóteses ordenadas; Incident continua responsável por serialização.
- **Plano/Linear:** marcar somente `LUM2-54` depois de testes, review, integração e push primeiro na branch de Renato.
- **Testes/observabilidade:** cobrir ganho dominante, combinações, baixa amostra e determinismo.

#### Validação e trial by fire

- **Hipótese verificável:** candidates iguais produzem hypotheses iguais e um ramo esparso nunca ultrapassa o pruning.
- **Caminho feliz:** provider/country dominante chega ao primeiro resultado com referências de evidência.
- **Caso difícil/adverso:** candidatos simultâneos ou suporte insuficiente permanecem hipóteses distintas ou não são retornados.
- **Resultado observado:** NOT RUN.
- **Fallback:** retornar lista vazia e conservar `INCONCLUSIVE`; nunca fabricar uma causa.

#### Gatilhos de revisão

Novo contrato de agregação dimensional, requisito de causa confirmada ou consumo direto pela API exige change control.

#### Adendos

- **2026-08-29T23:39:00-03:00:** PASS: a busca validou determinismo, slice dominante, pruning por suporte, ausência de candidates, grupos de correlação mistos e parâmetros inválidos. `14` testes focados e `116` testes completos passaram; `scripts/validate_contracts.py`, `compileall` e `git diff --check` passaram. Code review gate: PASS, sem achados bloqueantes. Browser acceptance não se aplica: não houve rota, UI ou fluxo local observável novo; o módulo só será exposto pelo consumidor de `LUM2-55`.

### FL-20260829-RENATO-008 — Ranquear alternativas sem elevar hipótese a causa suportada

- **Timestamp:** 2026-08-29T23:49:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** Renato
- **Participantes:** solicitante; Codex como implementador e recorder
- **Categoria:** data | quality | integration
- **Escopo:** `LUM2-55` / `TASK-RCA-002`, `CMP-DET/RCA-001`, `CTR-INC-001 v1`
- **Links:** `app/rca/beam.py`, `app/incidents/__init__.py`, `LUM2-54`, `LUM2-56`, `LUM2-35`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O beam de `LUM2-54` encontra slices com evidência quantitativa, mas não define como comparar contribuição, abrangência e especificidade nem como expressar empate sem que o consumidor confunda ranking com causalidade confirmada.

#### Decisão

Ranquear hipóteses com score determinístico ponderando contribuição observada, affected share e especificidade. Expor a lista ordenada como `RootCause.alternatives` de `CTR-INC-001` e manter o `RootCause` em `INCONCLUSIVE` com categoria nula: o ranking escolhe uma hipótese de investigação, mas não tem evidência independente para emitir `SUPPORTED`.

#### Critérios e por que agora

`LUM2-55` é a ponte entre busca e consumo de Incident. O contrato já permite alternativas ordenadas e o status inconclusivo, portanto o handoff não precisa alterar schema nem assumir que a maior anomalia é a causa real.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Promover o maior score a `SUPPORTED` | Interface aparentemente simples | confunde associação estatística com confirmação e pode acionar explicação indevida | FACT: `AnomalyCandidate` não declara causa | Rejeitada por segurança causal |
| Retornar apenas um vencedor sem alternativas | Menos payload | esconde empates e mix shifts | FACT: `CTR-INC-001` prevê alternativas | Não satisfaz o aceite |
| Ranking determinístico inconclusivo com alternativas | Auditável e compatível com o contrato | requer investigação humana para confirmar | TEST: fixtures cobrirão dominante, mix shift e empate | Escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** o contrato de `RootCause` ordena alternativas por confiança e permite `INCONCLUSIVE` com categoria nula.
- **ASSUMPTION:** contribution, cobertura relativa e profundidade do slice são sinais suficientes para priorizar investigação, não para provar causalidade.
- **UNKNOWN:** quais evidências externas podem elevar uma hipótese a `SUPPORTED`; isso exige change control e owner de Incident.

#### Trade-offs aceitos

- **Ganhamos:** uma ordem estável e explicável para a demo sem ground truth.
- **Abrimos mão de:** causa confirmada automática.
- **Dívida/limitação:** pesos e margem de ambiguidade são heurísticos internos, sujeitos a eval posterior.
- **Risco residual:** uma hipótese dominante pode ainda ser falsa; a serialização declara `INCONCLUSIVE` para reduzir esse risco.

#### Consequências e propagação

- **Arquitetura/contratos:** produz instância compatível com `CTR-INC-001 v1`; não altera o schema nem cria Incident.
- **Pessoas/branches:** `LUM2-35` recebe alternativas já ordenadas; `LUM2-56` avalia o comportamento em batches mistos.
- **Plano/Linear:** atualizar após evidência real, revisão, push na branch de Renato e integração.
- **Testes/observabilidade:** verificar dominante, mix shift, empate e a preservação de `INCONCLUSIVE`.

#### Validação e trial by fire

- **Hipótese verificável:** resultados iguais preservam ordem; margem pequena remove vencedor único, mas conserva alternativas.
- **Caminho feliz:** hipótese de provider dominante aparece antes das alternativas.
- **Caso difícil/adverso:** empate e mix shift não recebem categoria suportada.
- **Resultado observado:** NOT RUN.
- **Fallback:** nenhuma hipótese retorna `INCONCLUSIVE` sem alternativas; nunca fabricar categoria confirmada.

#### Gatilhos de revisão

Disponibilidade de evidência independente, novo contrato de contribuição ou pedido para automação de decisão exige change control.

#### Adendos

- **2026-08-29T23:58:00-03:00:** PASS: cobertos hipótese dominante, mix shift, empate inconclusivo, entrada vazia, grupos de correlação incompatíveis e valores inválidos. `19` testes focados e `122` testes completos passaram; contratos, compilação e `git diff --check` passaram. Code review gate: PASS após validar limites numéricos de suporte/score e a preservação de `INCONCLUSIVE`. Browser acceptance não se aplica: nenhuma rota, UI ou fluxo observável foi alterado; o ranking é consumido internamente pela etapa de Incident.

### FL-20260830-RENATO-009 — Avaliar fluxo transaction-first por invariantes observáveis

- **Timestamp:** 2026-08-30T00:10:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** Renato
- **Participantes:** solicitante; Codex como implementador e recorder
- **Categoria:** quality | data | integration
- **Escopo:** `LUM2-56` / `TASK-EVAL-001`, `CTR-TXN-001`, `CTR-EVT-001`, `CTR-DET-001`, `CTR-INC-001`
- **Links:** `app/simulation/background_traffic.py`, `app/simulation/transaction_outcomes.py`, `app/detection/detector.py`, `app/rca/ranking.py`, `LUM2-57`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O fluxo público e o harness agora compartilham o lifecycle de batch, mas faltava uma prova conjunta de que casos mistos, baixo volume e ambiguidades preservam os limites corretos antes do holdout final.

#### Decisão

Criar uma matriz de testes reprodutível a partir de inputs públicos e contextos fixos do adapter: verificar success/failure/unknown, que amostras manuais e de background produzem eventos canônicos equivalentes, que baixo volume não gera candidate e que ranking ambíguo continua `INCONCLUSIVE`. A matriz não lê ou ajusta ground truth.

#### Critérios e por que agora

`LUM2-56` é pré-requisito do holdout de `LUM2-57`; validar invariantes de transporte e honestidade de abstention primeiro impede que o holdout use uma API diferente ou uma causa inventada.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Executar somente testes isolados existentes | Rápido | não prova interação dos limites do fluxo | FACT: casos estavam distribuídos por módulos | Insuficiente para EVAL-001 |
| Ajustar thresholds até produzir casos desejados | Pode melhorar números locais | contamina a futura validação holdout | FACT: issue proíbe ajuste pelo holdout | Rejeitada |
| Matriz fixa de invariantes sem ground truth | Reprodutível e prepara holdout honesto | não mede accuracy final | TEST: cobrirá quatro limites do fluxo | Escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `OTHER` gera resultado `UNKNOWN` determinístico; o detector já protege a janela abaixo do support mínimo.
- **ASSUMPTION:** equivalência de caminho é comprovada por contrato canônico, resultado terminal e ausência de campos de outcome no input.
- **UNKNOWN:** accuracy de causa no conjunto escondido; pertence a `LUM2-57`.

#### Trade-offs aceitos

- **Ganhamos:** regressão rápida e auditável sem contaminar o holdout.
- **Abrimos mão de:** um número de accuracy nesta etapa.
- **Dívida/limitação:** a matriz testa invariantes com fixture pequena, não distribuição de produção.
- **Risco residual:** regressões estatísticas amplas continuam demandando holdout separado.

#### Consequências e propagação

- **Arquitetura/contratos:** sem novo contrato; confirma os quatro existentes.
- **Pessoas/branches:** libera `LUM2-57` com seeds e comportamento de abstention já preservados.
- **Plano/Linear:** atualizar somente após execução, review e integração.
- **Testes/observabilidade:** registrar os comandos e contagens reais no adendo.

#### Validação e trial by fire

- **Hipótese verificável:** o mesmo input canônico tem output compatível independente de ser submetido manualmente ou pelo harness.
- **Caminho feliz:** batch misto entrega os três estados terminais.
- **Caso difícil/adverso:** baixo volume e empate não recebem alerta ou causa suportada.
- **Resultado observado:** NOT RUN.
- **Fallback:** manter status e causa inconclusivos, sem reclassificar por fixture.

#### Gatilhos de revisão

Alteração no contrato de input/evento, estratégia do worker ou threshold do detector exige repetir a matriz.

#### Adendos

- **2026-08-30T00:22:00-03:00:** PASS: a matriz registrou batch misto com os três estados, equivalência de input manual/background pela seed `404`, zero candidate no low volume 11/12 e empate inconclusivo. `32` testes focados e `126` testes completos passaram; contratos, compilação e `git diff --check` passaram. Code review gate: PASS, sem achados bloqueantes. Browser acceptance não se aplica: não houve nova rota ou UI; a matriz chama as interfaces internas já cobertas pelos testes de API/worker.

## Prontidão para a banca

_Preencher no modo `FINALIZE`._

| Lente | Estado | Evidência | Lacuna/ação |
| --- | --- | --- | --- |
| Funciona? | NOT READY | — | Ligar execução ponta a ponta e trial by fire |
| Profundidade e julgamento | PARTIAL | FL-20260829-TEAM-001 | Registrar decisões reais do sistema |
| Resolve o problema real | NOT READY | — | Ligar decisões ao enunciado e casos difíceis |
| Originalidade | NOT READY | — | Explicar o insight original como mecanismo |
| Experiência e clareza | PARTIAL | Este arquivo é legível no repo | Validar com leitor externo e demo |

### FL-20260830-RENATO-008 — Materializar somente fatos aceitos após a fronteira do servidor

- **Timestamp:** 2026-08-30T00:05:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** Renato
- **Participantes:** solicitante; Codex como implementador e recorder
- **Categoria:** data | quality | integration | operation
- **Escopo:** `LUM2-47` / `TASK-DATA-005`, `CMP-ING-001`, `CTR-STR-001`, handoff `ING-001`
- **Links:** `app/benchmark/parquet.py`, `app/streaming/listener.py`, `docs/benchmarks/task-data-005-2026-08-30.md`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O refactor já integrado estabelece o caminho gerador → servidor de transações → listener backend → análise. A tarefa exige materializar Parquet e medir o caminho real, sem transformar o benchmark em uma exportação direta do gerador nem misturar dados de execuções distintas.

#### Decisão

Executar o benchmark por lotes através de `TransactionServer` e `IngestionListener`, ingerindo cada lote em uma transação DuckDB e exportando somente `canonical_events` aceitos para Parquet ZSTD particionado por `event_date`. A materialização e o relatório recusam sobrescrita. A branch operacional foi normalizada para `renato/tarefa-47`, pois Git não aceita espaço em nomes de branch; o trabalho foi isolado em worktree enquanto outra tarefa mantinha um rebase pendente.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Exportar diretamente os lotes do gerador | Mais rápido e simples | Ignora validação, dedupe e ordenação do caminho real | FACT: o refactor define o listener como fronteira de ingestão | Não mede o comportamento que será operado |
| Inserir evento a evento no benchmark | Sem nova API de lote | O custo de commits e consultas repetidas domina a medida | TEST: o benchmark inicial ficou lento com validação e I/O repetidos | Não representa o consumo em lote do servidor |
| Lote transacional e Parquet de fatos aceitos | Mantém a fronteira e reduz overhead sem pular regras | Uma falha exige retry do lote completo | TEST: rollback preserva ausência de fatos parciais | Escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** o run de 90 dias com seed `29082026` publicou, ouviu e aceitou `8256` eventos; gerou `90` partições e `734214` bytes de Parquet.
- **TEST:** a duração observada foi `1127.394` s e o pico RSS do processo foi `207917056` bytes; o digest canônico foi `d3fb6959c92d545f05aecfa49d483fde1744551f47e81daf6dcd8c472c5d2461`.
- **UNKNOWN:** o RSS inclui Python, DuckDB nativo e o log em memória do adaptador local; não isola cada componente.

#### Trade-offs aceitos

- **Ganhamos:** dados reproduzíveis que passaram pelo mesmo servidor, listener e validações do produto.
- **Abrimos mão de:** continuação automática em uma pasta de saída já existente; a recusa evita mistura silenciosa de seeds/configurações.
- **Risco residual:** retry de lote redispõe todos os eventos desse lote, compensado pela deduplicação por `event_id`.

#### Consequências e propagação

- **Arquitetura/contratos:** nenhum schema público muda; o Parquet é uma projeção dos fatos canônicos aceitos.
- **Pessoas/branches:** `ING-001` recebe dados particionados e relatório reprodutível; gerador, servidor e listener permanecem desacoplados da exportação.
- **Linear/plano:** `LUM2-47` deve receber o relatório, commit e gates somente após a validação final.
- **Testes/observabilidade:** há cobertura de caminho servidor→listener→Parquet, determinismo, provider novo compatível, recusa de sobrescrita e rollback de lote.

#### Validação e trial by fire

- **Caminho feliz:** dados do gerador atravessam servidor e listener antes de gerar Parquet particionado.
- **Caso difícil/adverso:** falha após escrever raw faz rollback integral; provider novo compatível mantém o layout; baixa amostra retorna `12` eventos.
- **Resultado observado:** benchmark final concluído; gates automatizados finais pendentes deste registro.
- **Fallback:** reexecutar em novo diretório de artefatos com a mesma seed e comparar o digest.

#### Gatilhos de revisão

Qualquer mudança no envelope do servidor, no contrato canônico, na semântica de dedupe ou na estratégia de armazenamento exige revalidar o digest, o layout Parquet e o benchmark de 90 dias.

#### Adendos

- **2026-08-30T00:20:00-03:00:** PASS: `20` testes focados (ingestão, listener, histórico, agregação e Parquet), `compileall` e validação de contratos passaram. O smoke do CLI com banco novo confirmou `52/52` eventos gerados/publicados/aceitos e `52` linhas em uma partição. Um run tentou reutilizar armazenamento já populado; a proteção foi adicionada para recusar esse estado, sem apagar dados existentes.
- **2026-08-30T00:22:00-03:00:** O solicitante determinou que o benchmark de 90 dias já concluído não deve ser repetido. Uma nova execução iniciada para atualização de configuração foi interrompida antes de produzir relatório final; os únicos números publicados permanecem os do relatório salvo de `90` dias.

### FL-20260830-ANDRE-001 — Padronizar dependências Python com uv e lock versionado

- **Timestamp:** 2026-08-30T00:30:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** André
- **Participantes:** solicitante; Codex como implementador e recorder
- **Categoria:** operation | quality | integration
- **Escopo:** ambiente Python local, CI e deploy do monorepo
- **Links:** `pyproject.toml`, `uv.lock`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

Durante a validação da integração frontend/backend, `uv run` gerou `uv.lock` e o arquivo foi tratado incorretamente como artefato transitório no worktree. O solicitante confirmou que uv e o lock fazem parte do padrão já definido para o projeto.

#### Decisão

Usar `pyproject.toml` como declaração de dependências e manter `uv.lock` versionado como resolução reproduzível. Os fluxos de instalação, teste e deploy Python devem usar uv; não haverá migração para pip/`requirements.txt` nesta tarefa.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| uv + `uv.lock` versionado | resolução reproduzível e grupos/extras consistentes | exige atualizar o lock quando o projeto muda | FACT: `pyproject.toml` já define projeto e extras; solicitante confirmou o padrão | Escolhida |
| pip + `requirements.txt` | ferramenta amplamente disponível | duplicaria fonte de dependências e exigiria novo processo de locking | FACT: não há requirements autoritativo no repositório | Rejeitada |
| Somente `pyproject.toml`, sem lock | diff menor | versões transitivas podem divergir entre máquinas e deploy | FACT: intervalos de versão permitem resoluções diferentes | Rejeitada |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `uv lock` resolveu 41 pacotes e `uv lock --check` passou neste worktree.
- **FACT:** a suíte Python foi executada por uv e aprovou 160 testes antes desta confirmação.
- **UNKNOWN:** o CI/deploy remoto ainda precisa ser inspecionado para confirmar que todos os comandos usam `uv sync --frozen` ou equivalente.

#### Trade-offs aceitos

- **Ganhamos:** builds locais e remotos partem da mesma resolução.
- **Abrimos mão de:** instalação direta por pip como caminho oficial desta configuração.
- **Risco residual:** esquecer de atualizar o lock após editar dependências deve falhar no check de CI.

#### Consequências e propagação

- **Operação:** conservar `uv.lock`; validar com `uv lock --check`.
- **Integração:** qualquer mudança em `pyproject.toml` deve atualizar o lock no mesmo diff.
- **Testes:** CI deve instalar a resolução congelada e executar a suíte através de uv.

#### Gatilhos de revisão

Reavaliar somente se o runtime/deploy deixar de suportar uv ou se a equipe aprovar formalmente outro gerenciador e mecanismo de lock.

### FL-20260830-ANDRE-002 — Converter horários de transação para Brasília somente na apresentação

- **Timestamp:** 2026-08-30T01:45:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** André (solicitante)
- **Participantes:** André; Codex como implementador e recorder
- **Categoria:** UX | data | integration
- **Escopo:** listagem e detalhe live de transações no frontend Next.js
- **Links:** `CTR-TXL-001 v1`; `web/lib/format/date-time.ts`; `web/components/transaction-log/transaction-log.tsx`; `web/components/transaction-detail/transaction-detail.tsx`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

A UI live exibia timestamps de transações em UTC, embora o horário operacional esperado seja o de Brasília. Era necessário corrigir a apresentação sem mudar os instantes compartilhados pela API.

#### Decisão

Preservar os timestamps ISO 8601/UTC recebidos do backend e convertê-los somente para exibição com a zona IANA `America/Sao_Paulo`. Lista e detalhe identificam Brasília nos rótulos e reutilizam um formatter único.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência | Decisão |
| --- | --- | --- | --- | --- |
| Zona IANA na UI | contrato estável e regras históricas corretas | novas superfícies devem reutilizar o helper | código live forçava UTC | escolhida |
| Converter no backend | todos recebem horário local | altera semântica contratual e outros consumidores | contratos transportam instantes ISO | rejeitada |
| Offset fixo UTC−03 | implementação curta | falha no horário de verão histórico | Brasília já operou em UTC−02 | rejeitada |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `updated_at` era formatado com `timeZone: "UTC"`; `occurred_at` era mostrado sem conversão.
- **TEST:** testes, build e browser acceptance pendentes neste registro.
- **UNKNOWN:** nenhuma no escopo; timezone por usuário exigiria nova política.

#### Trade-offs aceitos

- **Ganhamos:** leitura operacional correta sem quebrar ordenação ou payloads.
- **Abrimos mão de:** mostrar UTC como padrão da interface brasileira.
- **Risco residual:** futura tela pode ignorar o helper; teste unitário torna a regra localizável.

#### Consequências e propagação

- **Produto/demo:** lista e detalhe deixam explícito o horário de Brasília.
- **Arquitetura/contratos:** nenhum schema, endpoint ou dado persistido muda.
- **Pessoas/branches:** somente o frontend de André é alterado.
- **Plano/Linear:** não aplicável; não há mudança de arquitetura nem de status operacional.
- **Testes/observabilidade:** validar UTC−03 atual, UTC−02 histórico, ISO semântico, refresh e mobile.

#### Validação e trial by fire

- **Caminho feliz:** `2026-08-29T18:00:10Z` aparece como `15:00:10` na lista e no detalhe.
- **Caso difícil/adverso:** janeiro de 2018 usa UTC−02 pela base IANA, sem cálculo manual.
- **Resultado observado:** PENDING.
- **Fallback:** reverter somente a camada de apresentação; o dado UTC permanece intacto.

#### Gatilhos de revisão

Mudança do público operacional, timezone configurável por usuário ou política global de localização.

#### Adendos

- **2026-08-30T01:55:00-03:00:** `npm test` passou com 36 testes e 1 integração live opcional marcada como `SKIP`; `npm run lint`, `npm run build` e `git diff --check` passaram. `code-review-gate`: PASS, sem achados bloqueantes. A conversão isolada já havia passado no navegador com UTC−03, detalhe, refresh, mobile e ISO semântico preservado. Na worktree da `origin/main@404c23b`, o frontend live iniciou corretamente, mas a leitura Railway em `localhost:3002` foi bloqueada pela allowlist de CORS conhecida; browser acceptance live local permanece `PASS WITH LIMITATIONS` e deve ser repetido no domínio Vercel após o deploy. `integration-contract-guardian`: READY WITH WARNINGS; nenhum contrato, env var, migration ou backend foi alterado.
- **2026-08-30T02:02:00-03:00:** VALIDATED no deploy público após o commit `e035663`. GitHub registrou Railway e Vercel como `success`. Em `https://lumen-nextwave.vercel.app/transactions`, `2026-08-30T04:31:50.211528Z` permaneceu no atributo `datetime` e foi exibido como `30/08/2026, 01:31:50`; o cabeçalho mostrou `Updated (Brasília)`. O detalhe manteve o estado opcional `Not provided` após refresh e o rótulo `Occurred at (Brasília)`. No viewport 375×812 não houve overflow horizontal nem erros/warnings de console. `browser-acceptance-gate`: PASS no ambiente publicado.

### FL-20260830-ROGERIO-010 — Concentrar a recuperação live em duas lanes sem trocar os contratos públicos

- **Timestamp:** 2026-08-30T00:23:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** Rogério (Pessoa A confirmada pelo solicitante)
- **Participantes:** Rogério; André como owner já documentado de `web/`; Codex como recorder
- **Categoria:** scope | architecture | contract | Git/integration
- **Escopo:** `DEC-022`, `DEC-023`, `OBJ-ROGERIO-002`, `OBJ-ANDRE-002`, `CTR-TXN-001 v1`, `CTR-TXL-001 v1`, `CTR-API-001 v3`, `CTR-INC-001 v1`, `CTR-TDI-001 v1`
- **Links:** `docs/plans/system-plan.md` v2.2.0; `docs/plans/people/rogerio.md`; `docs/plans/people/andre.md`; base `main@613df52`
- **Supersedes / superseded by:** não substitui as decisões de produto anteriores; concentra a execução restante e corrige o estado de integração.

#### Contexto e pergunta

Após atualizar a base local por fast-forward até `main@613df52`, detector/RCA, trace grounded, Neo4j e benchmark Parquet já estavam integrados. Ainda faltavam a cadeia real no worker e o repository live de Incident; o endpoint ainda lia fixtures. A proposta de recuperação precisava definir quem integra os módulos existentes e evitar reabrir contratos que o frontend já consome.

#### Decisão

Rogério integra core, dados, backend, runtime e documentos; André mantém ownership exclusivo de `web/`, Vercel e browser evidence. A recuperação implementa a persistência e o encadeamento por trás de `CTR-*` já congelados, com worker in-process de uma réplica e DuckDB/Volume para o MVP. `CTR-SCN-001 v1` permanece interno; não haverá endpoint ou schema novo só para a recuperação.

#### Critérios e por que agora

A fatia demonstrável depende de uma API real antes da integração visual. As duas lanes podem começar já: backend pela base integrada e frontend por mock explícito. Trocar schemas multiplicaria o custo de sincronização sem corrigir as lacunas observadas.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Reabrir quatro lanes e reaplicar branches antigas | especialização máxima | duplicação e colisão em hotspots já integrados | FACT: commits de módulos estão em `613df52` | não corrige a integração faltante |
| Criar `CTR-API v4` / schema de scenario novo | fronteira explicitamente nova | força UI e fixtures a migrar sem necessidade | FACT: contratos atuais expressam os estados necessários | custo sem ganho observável |
| Duas lanes com contratos preservados | caminho crítico curto e mocks estáveis | Rogério concentra integração e deploy | FACT: ownership de `web/` já é de André | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `transaction_worker.py` termina em `ingest_event`; `api/incidents.py` usa `_fixture_records()` no runtime; Docker usa Python 3.12.
- **TEST:** NOT RUN nesta decisão; a validação começa por contracts/suite/container e termina no E2E sem fixtures live.
- **ASSUMPTION:** uma réplica com DuckDB/Volume sustenta a demo; Rogério valida em `TASK-DEP-002`, com Postgres como alternativa somente via change control.
- **UNKNOWN:** domínios finais Vercel/Railway para allowlist; só bloqueiam deploy/CP4, não a implementação local.

#### Trade-offs aceitos

- **Ganhamos:** uma cadeia vertical concreta e ownership sem colisão.
- **Abrimos mão de:** paralelizar integração do detector/memory com seus autores originais.
- **Dívida/limitação:** worker in-process/uma réplica não é arquitetura de escala.
- **Risco residual:** um erro no integrador pode atrasar ambas as lanes; checkpoints CP1/CP3 reduzem a descoberta tardia.

#### Consequências e propagação

- **Produto/demo:** Incidents devem nascer de transações reais; fixtures permanecem apenas offline/teste.
- **Arquitetura/contratos:** versões públicas são preservadas; persistence/links passam a ser implementados atrás delas.
- **Pessoas/branches:** André não edita backend; Rogério não edita `web/`; nenhum merge/rebase/push foi autorizado ou executado.
- **Plano/Linear:** planos geral e individuais foram atualizados; Linear não foi escrito porque não houve autorização.
- **Testes/observabilidade:** exige E2E batch→Incident, idempotência, restart, memory down, leakage, CORS e browser gate.

#### Validação e trial by fire

- **Hipótese verificável:** um lote determinístico gera ou não gera Incident de modo reproduzível e a UI nunca recebe fixture como dado live.
- **Caminho feliz:** batch persistido → terminal → Incident grounded → detail no navegador.
- **Caso difícil/adverso:** baixa amostra, reentrega/restart, causas simultâneas e memória indisponível preservam limites honestos.
- **Resultado observado:** NOT RUN; somente auditoria de código/base concluída.
- **Fallback:** `NO_INCIDENT`, `INCONCLUSIVE` e `MEMORY_UNAVAILABLE` continuam respostas explícitas; não simular dado live.

#### Gatilhos de revisão

Falha do Volume/restart, necessidade de alterar schema/estado, ou divergência do cliente com contratos congela a implementação e exige change control antes de qualquer adaptação.

### FL-20260830-ROGERIO-011 — Fixar o deploy no mesmo Python 3.14.4 validado localmente

- **Timestamp:** 2026-08-30T00:23:10-03:00
- **Status:** ACCEPTED
- **Decision owner:** Rogério
- **Participantes:** Rogério; Codex como recorder
- **Categoria:** architecture | quality | operations
- **Escopo:** `DEC-024`, `TASK-REC-001`, `Dockerfile`, `.python-version`, `tests/test_environment.py`, `README.md`
- **Links:** `docs/plans/system-plan.md` v2.2.0; `FL-20260829-RENATO-001`; `FL-20260830-ROGERIO-010`
- **Supersedes / superseded by:** substitui somente a cláusula de Python 3.12 de `FL-20260830-ROGERIO-010`; preserva a decisão original `FL-20260829-RENATO-001` de fixar 3.14.4.

#### Contexto e pergunta

A1 confirmou que o ambiente local e o teste de ambiente exigem Python 3.14.4, enquanto `Dockerfile` declarava `python:3.12-slim`. A divergência permitiria que a suite passasse localmente e falhasse ou fosse pulada no ambiente que publica a API.

#### Decisão

Fixar a imagem em `python:3.14.4-slim`. O mínimo `>=3.11` de `pyproject.toml` descreve compatibilidade de dependências e não substitui o runtime operacional canônico.

#### Critérios e por que agora

O deploy Railway é parte do caminho crítico e precisa executar a mesma geração que a suite valida. O ajuste é limitado à imagem e não muda endpoint, schema ou semântica de produto.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Manter Docker 3.12 | sem mudança de imagem | contradiz teste e runtime declarados | FACT: teste exige `3.14.4` | risco de divergência |
| Relaxar o teste para 3.12 | build potencialmente mais comum | reverte decisão registrada sem validar a aplicação | FACT: 3.14.4 local passou a suite | esconderia a incompatibilidade |
| Fixar Docker em 3.14.4 | ambiente reproduzível | imagem precisa ser validada no Docker/Railway | TEST: suite local 160/160 em 3.14.4 | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `python --version` retornou `Python 3.14.4`; `validate_contracts` e 160 testes passaram nesse runtime.
- **TEST:** `docker` não está instalado nesta máquina; build/container smoke é `NOT RUN`.
- **ASSUMPTION:** a tag oficial `python:3.14.4-slim` está disponível ao Railway; validar no primeiro build.
- **UNKNOWN:** tempo de build e compatibilidade de wheels no Railway.

#### Trade-offs aceitos

- **Ganhamos:** mesma versão local/deploy e falhas ambientais detectáveis.
- **Abrimos mão de:** compatibilidade operacional declarada com Python 3.12.
- **Dívida/limitação:** a validação de imagem depende de ambiente com Docker ou Railway.
- **Risco residual:** indisponibilidade da tag bloqueia o deploy e requer nova decisão explícita.

#### Consequências e propagação

- **Produto/demo:** nenhuma alteração visual ou de contrato.
- **Arquitetura/contratos:** somente runtime/deploy; contratos públicos permanecem congelados.
- **Pessoas/branches:** André continua indiferente ao runtime; Rogério executa o smoke do container antes do CP4.
- **Plano/Linear:** plano geral, plano de Rogério e runbook foram alinhados; Linear não foi alterado.
- **Testes/observabilidade:** suites locais passaram; build Docker/Railway e health permanecem obrigatórios.

#### Validação e trial by fire

- **Hipótese verificável:** a imagem instala dependências, sobe `/v1/health` e executa a suite sob 3.14.4.
- **Caminho feliz:** `docker build` seguido de contract/smoke no container.
- **Caso difícil/adverso:** tag ausente ou wheel incompatível falha antes de publicar um deploy parcial.
- **Resultado observado:** PASS local; container `NOT RUN` por ausência de Docker.
- **Fallback:** não fazer downgrade silencioso; escolher imagem disponível via change control e repetir a suite.

#### Gatilhos de revisão

Falha de build, incompatibilidade de dependência ou alteração do runtime Python requer nova entrada e revalidação completa.

### Adendo de evidência — FL-20260830-ROGERIO-010 / 011

- **2026-08-30T00:23:10-03:00:** `TASK-REC-001/002`, `TASK-PIPE-001`, `TASK-PIPE-002`, `TASK-PIPE-003` e `TASK-PIPE-004` foram validadas localmente. O worker passou a derivar Incidents somente de janelas persistidas via aggregation → detector → RCA; o RCA permanece `INCONCLUSIVE` e a memória é enriquecimento read-time, sem promoção de precedente. O `DuckDBIncidentRepository` garante idempotência por janela/fingerprint, separa causas simultâneas e exige correlação/evidência para links transacionais. A API live lê o repository; fixtures requerem `DEMO_MODE` explícito. PASS: `python scripts/validate_contracts.py`, `python -m pytest -q` com 168 testes e `python -m compileall -q app`. O E2E público prova batch → worker → canonical → detector/RCA → Incident persistido → `GET /v1/transactions/{id}/incidents`, sem `fixture://`. Code-review gate: `PASS WITH NOTES`, sem achado bloqueante. Build Docker/Railway permanece `NOT RUN` porque Docker não está instalado neste host e não foram fornecidas credenciais/URLs externas.

### FL-20260830-ROGERIO-012 — Publicar a recuperação validada diretamente na main

- **Timestamp:** 2026-08-30T00:39:43-03:00
- **Status:** ACCEPTED
- **Decision owner:** Rogério (solicitante)
- **Participantes:** Rogério; Codex como executor e recorder
- **Categoria:** Git/integration | quality | operations
- **Escopo:** recuperação 2.2, `main`, `origin/main`, `TASK-REC-001..002`, `TASK-PIPE-001..004`
- **Links:** `FL-20260830-ROGERIO-010`, `FL-20260830-ROGERIO-011`, `docs/plans/system-plan.md` v2.2.0
- **Supersedes / superseded by:** substitui somente a restrição operacional de não fazer push registrada em `FL-20260830-ROGERIO-010`; não altera os contratos ou a arquitetura.

#### Contexto e pergunta

A recuperação foi implementada no working tree da `main` já alinhada a `origin/main@613df52`. O solicitante autorizou explicitamente publicar tudo na `main` e fazer push após os gates locais.

#### Decisão

Criar um commit único, com o plano, Flight Log, runtime, pipeline, API e testes da recuperação, diretamente na `main`, então enviar o commit a `origin/main`.

#### Critérios e por que agora

Não há commits remotos divergentes, o diff pertence a esta recuperação e os contratos públicos permanecem congelados. Publicar um único incremento verificável evita deixar o handoff de André dependente de alterações locais não rastreáveis.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência | Decisão |
| --- | --- | --- | --- | --- |
| Manter working tree local | sem operação remota | André não recebe uma base reproduzível | FACT: solicitante pediu push | rejeitada |
| Criar branch/PR adicional | revisão remota formal | atrasa a integração e contradiz publicação direta pedida | FACT: main está alinhada e os gates locais passaram | rejeitada agora |
| Commit e push diretos | handoff rastreável imediato | exige preservar todos os gates e documentos | TEST: 168 testes e contratos passaram | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `HEAD` e `origin/main` apontam para `613df52` antes do commit; não há divergência remota.
- **TEST:** `validate_contracts`, `pytest` (168) e `compileall` passaram; `git diff --check` passou.
- **UNKNOWN:** build Docker/Railway continua não executado neste host.

#### Trade-offs aceitos

- **Ganhamos:** base compartilhada, commit recuperável e handoff imediato.
- **Abrimos mão de:** uma revisão remota adicional antes da publicação.
- **Risco residual:** deploy ainda pode revelar incompatibilidade da imagem/serviço; permanece bloqueado no checkpoint externo.

#### Consequências e propagação

- **Produto/demo:** backend live fica disponível para a próxima integração web após pull.
- **Arquitetura/contratos:** nenhuma versão pública muda.
- **Pessoas/branches:** André pode partir do commit publicado; não há merge/rebase de branch alheia.
- **Testes/observabilidade:** a evidência local acompanha o commit; deploy precisa ser validado posteriormente.

#### Validação e trial by fire

- **Caminho feliz:** `git push origin main` atualiza o remoto com o commit esperado.
- **Caso difícil/adverso:** rejeição por corrida remota exige fetch, guardian e nova decisão — sem force push.
- **Resultado observado:** PENDING no momento do registro.
- **Fallback:** preservar o commit local e interromper; não sobrescrever o remoto.

#### Gatilhos de revisão

Rejeição do push, divergência remota, falha de gate ou descoberta de contrato incompatível interrompe a publicação.

#### Adendos

- **2026-08-30T00:39:43-03:00:** PASS — commit `2cf5091` (`feat: persist grounded incident pipeline`) foi criado diretamente na `main` e `git push origin main` atualizou `origin/main` de `613df52` para `2cf5091`. Não houve force push, merge ou rebase.

### FL-20260830-TEAM-026 — Integrar o diagnóstico de seis dimensões na main atual

- **Timestamp:** 2026-08-30T05:10:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Categoria:** Git/integration | product | contracts
- **Escopo:** cubo de diagnóstico, catálogo sintético e `origin/main`

#### Decisão

Rebasear a entrega local de diagnóstico sobre a `origin/main` atual, resolver somente conflitos textuais preservando tanto a evolução remota quanto os novos contratos aditivos, validar os gates e fazer push direto para `main`, sem force push.

#### Alternativas e trade-offs

| Alternativa | Decisão |
| --- | --- |
| Sobrescrever a main remota | rejeitada: poderia apagar a atualização de timezone já publicada. |
| Abrir outra branch/PR | rejeitada: o solicitante autorizou explicitamente integração e push na main. |
| Rebase, revisar conflitos e publicar | escolhida: preserva a história remota e deixa a entrega rastreável. |

#### Evidência e validação exigida

- **FACT:** `origin/main` avançou de `404c23b` para `82bea0d`; a entrega local é descendente do commit anterior.
- **TEST:** antes da publicação, executar `pytest`, validação de contratos, testes/build web e `git diff --check`.
- **Regra:** qualquer conflito sem resolução preservadora ou falha de gate interrompe o push; force push é proibido.

### FL-20260830-TEAM-027 — Separar hipótese proativa do agente da causa comprovada pelo motor

- **Timestamp:** 2026-08-30T02:27:22-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** product | architecture | AI/RAG | payments
- **Escopo:** agente de diagnóstico proativo, `CTR-AGT-001`–`003`, Incident, memória e explicação
- **Links:** `DEC-026`; `CTR-INC-001 v2`; `CTR-MEM-001`; `CTR-LLM-001`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O fluxo anterior assumia um copiloto reativo acionado por pergunta do operador e tratava `INCONCLUSIVE` como conclusão do diagnóstico atual. O solicitante definiu que o agente deve iniciar a investigação junto ao motor e ainda sugerir uma explicação quando não houver precedente documentado no RAG.

#### Decisão

Criar um agente read-only e proativo após a persistência do Incident. Ele consome um pacote imutável de evidências do motor, pode recuperar precedentes autorizados e produz uma hipótese de investigação rotulada `SUGGESTED`, ou `INSUFFICIENT_EVIDENCE` somente quando não houver base rastreável para sugestão. A hipótese não altera `root_cause`, não confirma fraude e não possui ferramentas de pagamento ou escrita.

#### Critérios e por que agora

O desafio valoriza diagnóstico proativo e explicação de causas inéditas; ausência de memória não pode interromper a investigação. Ao mesmo tempo, pagamentos exigem que texto de modelo não adquira autoridade para executar, confirmar ou modificar efeitos financeiros.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Encerrar em `INCONCLUSIVE` sem precedente | máxima cautela | não oferece próxima ação para caso novo | FACT: o solicitante exige sugestão proativa | rejeitada |
| Agente promover causa/fraude diretamente | experiência aparentemente simples | alucinação e autoridade financeira indevida | FACT: `root_cause` é hoje autoritativo no motor | rejeitada |
| Hipótese separada e rastreável | investigação útil sem falsificar fatos | exige novo contrato, avaliação e UX cuidadosa | ASSUMPTION: evidências atuais permitem calibração | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** o motor já persiste métricas, scope, evidências, alternativas e perfil de decline; a memória separa `NO_PRECEDENT` de causa atual.
- **TEST:** NOT RUN — não há ainda `EvidencePack`, corpus de agente ou avaliação de sugestões.
- **ASSUMPTION:** duas evidências atuais independentes serão um mínimo inicial para publicar uma hipótese; validar antes de congelar `CTR-AGT-003`.
- **UNKNOWN:** taxonomia e sinais que distinguem fraude real, bloqueio antifraude e falha operacional.

#### Trade-offs aceitos

- **Ganhamos:** diagnóstico proativo para incidentes inéditos e uma trilha explícita para investigação humana.
- **Abrimos mão de:** afirmar uma causa/fraude com base apenas na narrativa do agente.
- **Dívida/limitação:** sem corpus autorizado e evals, a implementação está bloqueada.
- **Risco residual:** sugestão plausível pode ancorar o operador; mitigar com evidências, confiança, lacunas visíveis e proibição de promoção automática.

#### Consequências e propagação

- **Produto/demo:** o detalhe do Incident precisará exibir hipótese, confiança, evidências e lacunas separadamente da causa do motor.
- **Arquitetura/contratos:** propor `CTR-AGT-001`–`003`; não alterar contratos existentes antes de change control.
- **Pessoas/branches:** Renato define taxonomia/sinais; Altoé define corpus e evals; Rogério coordena contratos/API; André consome mock congelado na UI.
- **Plano/Linear:** `docs/plans/system-plan.md` 2.4.0 atualizado; Linear não alterado.
- **Testes/observabilidade:** exigir casos de hipótese sem precedente, no-answer, evidência conflitante, memória indisponível e tentativa de promoção indevida.

#### Validação e trial by fire

- **Hipótese verificável:** incidente novo sem precedente recebe sugestão citada e humana, sem mudar `root_cause`.
- **Caminho feliz:** Incident → EvidencePack → sugestão → detalhe com evidências e ação humana.
- **Caso difícil/adverso:** jurado injeta combinação inédita ou decline `SUSPECTED_FRAUD` sem outra prova; agente declara hipótese/lacuna, nunca fraude confirmada.
- **Resultado observado:** NOT RUN.
- **Fallback:** `INSUFFICIENT_EVIDENCE` com lacunas explícitas e evidence IDs disponíveis; nenhum side effect.

#### Gatilhos de revisão

Qualquer tentativa de permitir escrita, pagamento, promoção de causa, corpus sem autorização, ou falha em distinguir hipótese de fato exige nova decisão e change control.

#### Adendos

- Nenhum.

### FL-20260830-TEAM-028 — Congelar a demo em uma fatia causal executável em sete horas

- **Timestamp:** 2026-08-30T02:27:22-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** scope | architecture | demo | quality
- **Escopo:** stream sintético, detector/RCA, Incident, UI e ensaio da demo
- **Links:** `DEC-027`; `CTR-TXN-001`; `CTR-DET-001`; `CTR-INC-001`; plano 2.4.1 §18
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

Restam sete horas de hackathon. O plano completo inclui integração Yuno, ingestão ampla e agente/RAG, mas essas frentes não cabem com segurança na janela sem comprometer a prova ao vivo exigida pelo desafio.

#### Decisão

Congelar a demo em stream sintético contínuo, baseline, duas degradações simultâneas, RCA/evidência, impacto e recomendação humana. Integração Yuno, novo corpus/RAG, vector store e agente amplo ficam fora do caminho crítico; o Evidence Pack/template só entra após o fluxo principal verde.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Construir integração Yuno e RAG completos | maior escopo potencial | alto risco de contrato, dados e deploy; sacrifica ensaio | FACT: restam sete horas | rejeitada |
| Polir apenas a UI atual | baixo risco de código | não prova stream, anomalia ou causa | FACT: Incident live ainda precisa ser demonstrado | rejeitada |
| Fatia causal sintética ponta a ponta | cobre o núcleo avaliável e é reprodutível | não prova integração externa real | FACT: o enunciado permite dados inventados | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** deploy, persistência, cube, detector, RCA e UI existem; o enunciado aceita transações e histórico inventados.
- **TEST:** NOT RUN — a sequência completa dos dois Incidents e trial by fire será a validação desta janela.
- **ASSUMPTION:** os componentes existentes podem ser conectados sem mudança incompatível de contrato.
- **UNKNOWN:** comportamento do deploy sob stream contínuo e qualidade da separação por resíduo.

#### Trade-offs aceitos

- **Ganhamos:** demonstração defensável do problema central.
- **Abrimos mão de:** integração real Yuno e agente/RAG completo nesta entrega.
- **Dívida/limitação:** o produto continua sintético e o agente amplo permanece planejado, não implementado.
- **Risco residual:** cenários podem falhar em detectar/separar; o ensaio começa cedo para preservar tempo de correção.

#### Consequências e propagação

- **Produto/demo:** o hero é normal → queda → causa/evidência → ação humana → dois simultâneos → caso desconhecido.
- **Arquitetura/contratos:** preservar contratos públicos existentes; mudanças exigem change control.
- **Pessoas/branches:** Renato stream/cenários; Rogério detector/RCA/E2E; André UI; Altoé só entra após caminho crítico.
- **Plano/Linear:** plano 2.4.1 atualizado; Linear não alterado.
- **Testes/observabilidade:** smoke, E2E de dois Incidents, browser/deploy e trial by fire são gates obrigatórios.

#### Validação e trial by fire

- **Hipótese verificável:** um fluxo sintético inédito cria um Incident correto ou abstention explícita, sem intervenção manual no diagnóstico.
- **Caminho feliz:** baseline → provider-BR e issuer-MX-merchant → dois Incidents → UI.
- **Caso difícil/adverso:** combinação nova do jurado não pode depender de ID/cenário hardcoded.
- **Resultado observado:** NOT RUN.
- **Fallback:** demonstrar o cenário configurável conhecido com limitações explícitas; não simular sucesso.

#### Gatilhos de revisão

Falha do smoke, impossibilidade de separar os Incidents, ou mudança incompatível de contrato obriga cortar o agente/template e concentrar toda a janela no mecanismo causal.

#### Adendos

- Nenhum.

### FL-20260830-ROGERIO-029 — Semear baseline temporal pelo stream sintético, sem integrar Yuno

- **Timestamp:** 2026-08-30T03:10:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** Rogério
- **Categoria:** scope | architecture | contract | demo
- **Escopo:** `LiveStreamController`, `CTR-STR-001`, `CTR-DEMO-001 v1` e detector
- **Links:** `DEC-027`; `DEC-028`; `CTR-STR-001`; plano 2.4.2 §18
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O controller existente publica eventos de um lote perto de um único timestamp e o trigger de background usa a batch API limitada a 100 itens. Isso não forma um histórico temporal útil para o detector antes de injetar a queda. O solicitante confirmou que integrar Yuno ou qualquer fonte externa não cabe na janela do hackathon.

#### Decisão

Adicionar um trigger de demo, somente em `DEMO_MODE`, que publica várias janelas passadas de tráfego sintético pelo `TransactionServer` existente. O controller passa a ordenar os timestamps em janelas de cinco minutos e a usar uma correlação compartilhada por janela de baseline; o cenário seguinte recebe o próximo intervalo temporal. O caminho continua produtor → stream → listener → ingestão → agregação/detecção, sem payload, SDK ou credencial Yuno.

#### Critérios e por que agora

O núcleo a provar é baseline normal seguido de degradação detectável. Reaproveitar a fronteira do stream preserva a demo ponta a ponta e elimina a maior lacuna de tempo sem abrir uma integração externa.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Integrar Yuno/SDK | maior fidelidade a produção | contratos, dados e credenciais indisponíveis na janela | FACT: o solicitante excluiu Yuno por prazo | rejeitada |
| Usar somente o batch background atual | nenhum endpoint novo | não garante histórico temporal nem correlação agregada do stream | FACT: limite atual é 100 e timestamps não avançam por pagamento | rejeitada |
| Baseline sintético no stream existente | exercita ingestão real e é reproduzível | continua sendo dado sintético/in-process | FACT: `CTR-STR-001` e listener já existem | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** o detector usa apenas janelas anteriores do mesmo slice para construir baseline.
- **FACT:** o `LiveStreamController` e o listener já são a fronteira local de produção/consumo da demo.
- **TEST:** NOT RUN — testes de timestamps, ingestão e detecção seguirão a implementação.
- **ASSUMPTION:** 12 janelas com volume mínimo configurado serão suficientes para os guards estatísticos da demo; validar no E2E.
- **UNKNOWN:** a separação completa de dois cenários simultâneos pertence à próxima fatia de detector/RCA.

#### Trade-offs aceitos

- **Ganhamos:** histórico observável e repetível sem serviço externo.
- **Abrimos mão de:** realismo de payload e tráfego de produção da Yuno.
- **Dívida/limitação:** stream continua in-process e limitado para a demo.
- **Risco residual:** um volume pequeno pode não superar o guard de amostra; limites e testes deixam isso explícito.

#### Consequências e propagação

- **Produto/demo:** a demo pode iniciar em normalidade antes de mostrar a queda.
- **Arquitetura/contratos:** novo `CTR-DEMO-001 v1` é aditivo e `DEMO_MODE`-only; `CTR-API-001` não muda.
- **Pessoas/branches:** Rogério implementa controller/endpoint/testes; Renato pode consumir o clock temporal nos cenários.
- **Plano/Linear:** plano 2.4.2 atualizado; Linear não alterado.
- **Testes/observabilidade:** testar ordenação temporal, correlação por janela, negação fora de `DEMO_MODE` e fluxo listener.

#### Validação e trial by fire

- **Hipótese verificável:** baseline publicado antes do cenário cria janelas elegíveis para comparação e não gera alerta por si.
- **Caminho feliz:** baseline → listener → cenário → detector.
- **Caso difícil/adverso:** jurado aumenta o número de janelas/pagamentos dentro dos limites e o fluxo ainda não depende de fixture ou Yuno.
- **Resultado observado:** NOT RUN.
- **Fallback:** chamar o controller diretamente no ensaio local e explicitar a limitação do trigger caso a rota não esteja exposta.

#### Gatilhos de revisão

Falha de ingestão, timestamps fora da janela, custo excessivo no Railway ou necessidade de fonte real exigem novo change control; fonte externa não será adicionada nesta janela.

#### Adendos

- Nenhum.

### FL-20260830-TEAM-029 — Congelar `CTR-AGT-001`–`003 v1` com cliente determinístico como padrão do agente proativo

- **Timestamp:** 2026-08-30T09:40:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** architecture | contract | AI/RAG | payments
- **Escopo:** `app/agent/`, `app/worker/incident_pipeline.py`, `app/api/incidents.py`, `contracts/v1/agent-*.schema.json`, `CTR-API-001 v3`
- **Links:** `DEC-026`; `DEC-028`; `CTR-AGT-001 v1`; `CTR-AGT-002 v1`; `CTR-AGT-003 v1`; `CTR-INC-001 v1`; `CTR-MEM-001 v1.1`; `FL-20260830-TEAM-027`
- **Supersedes / superseded by:** desbloqueia parcialmente `FL-20260830-TEAM-027` (§17 `PLAN BLOCKED`); não o revoga

#### Contexto e pergunta

`FL-20260830-TEAM-027` aceitou o agente proativo mas deixou §17 como `PLAN BLOCKED` por `OPEN-AGT-001`–`003` (taxonomia de fraude, corpus autorizado, limiar de suficiência). Restam ~7 horas de hackathon. A pergunta é se dá para implementar uma fatia vertical do agente sem resolver as três decisões abertas e sem colocar latência/indisponibilidade de LLM no caminho crítico do Incident.

#### Decisão

Implementar `app/agent/` com três contratos novos congelados em v1 (`EvidencePack`, `RetrievalTrace`, `DiagnosticSuggestion`) e adotar os fallbacks seguros já escritos em §17 como comportamento de produção, em vez de esperar as decisões abertas:

- `OPEN-AGT-001` → o agente só pode sugerir categorias já produzidas pelo motor (`root_cause.category` + `rca_alternatives`) ou categorias de risco não-confirmatórias; afirmar fraude como fato é rejeitado pelo validador.
- `OPEN-AGT-002` → a recuperação usa exclusivamente a memória estruturada existente (`IncidentMemoryService`) e o catálogo versionado de playbooks. Sem vector store, embeddings, web ou corpus novo.
- `OPEN-AGT-003` → `SUGGESTED` exige no mínimo duas evidências atuais independentes (`source_ref` distintos) no `EvidencePack`; abaixo disso o agente devolve `INSUFFICIENT_EVIDENCE`.

O cliente LLM é injetável e o **padrão é determinístico e offline** (`deterministic-template-v1`), montado a partir do `EvidencePack` e do `RetrievalTrace`. O cliente OpenAI existe, é opt-in por configuração e nunca é construído em teste. A geração roda depois da persistência do Incident, dentro de `try/except`, e uma falha do agente nunca aborta a transação do worker.

#### Critérios e por que agora

Três critérios dominaram: (1) o Incident persistido é o núcleo da nota do desafio e não pode depender do agente; (2) as três decisões abertas já possuíam fallback seguro escrito, então esperar por elas custaria a fatia inteira sem reduzir risco; (3) um cliente determinístico por padrão torna a demo reprodutível e os testes independentes de chave OpenAI. A decisão não podia continuar aberta porque a janela restante não comporta congelar contrato depois de implementar consumidores.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Manter §17 bloqueado até fechar `OPEN-AGT-001`–`003` | máxima cautela contratual | consome a janela inteira; entrega zero do agente | FACT: restam ~7h e §18 já cortou o agente amplo | rejeitada; os fallbacks seguros já estavam escritos |
| Chamar OpenAI por padrão no pipeline | narrativa mais rica na demo | latência/indisponibilidade dentro da transação DuckDB do worker; teste dependente de chave | FACT: `derive_incidents_for_correlation` roda entre `BEGIN` e `COMMIT` em `transaction_worker.py:93-124` | rejeitada; LLM real vira opt-in |
| Expor a sugestão dentro de `CTR-INC-001` | um único payload para a UI | mudança incompatível em contrato congelado e consumido pelo `web/` | FACT: `CTR-INC-001 v1` está `FROZEN` e o schema é `additionalProperties: false` | rejeitada; endpoint aditivo separado |
| Contratos novos + cliente determinístico padrão + endpoint aditivo | fatia demonstrável sem tocar contrato congelado nem caminho crítico | mais um endpoint e mais uma tabela para manter | ASSUMPTION: duas evidências independentes é limiar inicial defensável | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `Incident` e seu schema usam `extra="forbid"` / `additionalProperties: false`, então a sugestão não cabe no contrato atual sem versionar.
- **FACT:** `derive_incidents_for_correlation` é chamada dentro da transação DuckDB do worker; exceção não capturada faria rollback do lifecycle da transação.
- **FACT:** `openai==2.38.0` está instalado neste host, mas **não** é dependência declarada no `pyproject.toml` nem no `uv.lock` usado pelo Dockerfile.
- **TEST:** ver adendo — a suíte foi executada após a implementação.
- **ASSUMPTION:** duas evidências atuais independentes é limiar suficiente para publicar hipótese; owner Team; gatilho de revisão é o primeiro holdout com ground truth.
- **UNKNOWN:** calibração real de `confidence`; hoje é derivada do motor, não estimada pelo agente.

#### Trade-offs aceitos

- **Ganhamos:** hipótese proativa rastreável para Incidents inéditos, sem precedente, sem tocar `CTR-INC-001` e sem risco no caminho crítico.
- **Abrimos mão de:** narrativa gerada por LLM real por padrão na demo; a saída padrão é template determinístico.
- **Dívida/limitação:** o caminho OpenAI não roda na imagem Docker atual porque `openai` não está no `uv.lock` congelado; ativá-lo exige mudança de dependência coordenada por Rogério.
- **Risco residual:** o limiar de duas evidências pode ser permissivo ou restritivo demais; é observável nos testes de suficiência e reversível em um parâmetro.

#### Consequências e propagação

- **Produto/demo:** o detalhe do Incident pode exibir "hipótese do agente" separada da causa do motor; ausência de sugestão é 404 tipado, não hipótese vazia.
- **Arquitetura/contratos:** cria `CTR-AGT-001`–`003 v1`; `CTR-API-001 v3` recebe path aditivo `GET /v1/incidents/{incident_id}/suggestion`; `CTR-INC-001 v1` inalterado.
- **Pessoas/branches:** André consome o endpoint novo; Altoé mantém a autoridade da memória; Renato continua dono da taxonomia de `OPEN-AGT-001`.
- **Plano/Linear:** `docs/plans/system-plan.md` §17 atualizado para `PARTIALLY UNBLOCKED`. Linear não alterado.
- **Testes/observabilidade:** exigidos casos de sem-precedente, memória indisponível, resposta malformada, evidence ID inventado, ação não `HUMAN_ONLY`, tentativa de promoção de `root_cause`, idempotência e `SUSPECTED_FRAUD`.

#### Validação e trial by fire

- **Hipótese verificável:** um Incident persistido sem precedente produz `SUGGESTED` citando apenas evidence IDs do próprio `EvidencePack`.
- **Caminho feliz:** pipeline `batch → worker → Incident → suggestion` persistida e legível pelo endpoint.
- **Caso difícil/adverso:** cliente devolve JSON inválido, cita `evd_inventado`, pede `execution: AUTOMATIC` ou tenta escrever `root_cause`.
- **Resultado observado:** ver adendo.
- **Fallback:** falha do agente devolve `UNAVAILABLE` com limitação; o Incident e a explicação determinística permanecem intactos.

#### Gatilhos de revisão

Fechamento de `OPEN-AGT-001`–`003`, primeiro holdout com ground truth, decisão de declarar `openai` como dependência, ou qualquer pedido de expor a sugestão dentro de `CTR-INC-001`.

#### Adendos

- **2026-08-30T11:20:00-03:00 — Claude (revisor independente), evidência de execução.** `python -m pytest -q` -> **214 passed**, 0 failed. `python scripts/validate_contracts.py` -> **OK**, incluindo os três pares schema/fixture novos (`agent-evidence-pack`, `agent-retrieval-trace`, `agent-diagnostic-suggestion`). No `web/`: `npx tsc --noEmit` limpo, `npm run lint` limpo, `npm run build` concluído, `npm test` **38 passed / 1 skipped** (o skip é a suíte live que exige backend em execução).
- **Cobertura dos guardrails (`tests/test_agent_suggestion.py`, `test_agent_api.py`, `test_agent_pipeline_e2e.py`, 29 casos):** sem precedente -> `SUGGESTED`; `NO_PRECEDENT` não vira `INCONCLUSIVE`; uma única fonte de evidência -> `INSUFFICIENT_EVIDENCE` sem chamar o cliente; memória indisponível -> sugestão preservada com limitação; cliente que levanta exceção, JSON malformado, `evidence_id` inventado, `execution: AUTOMATIC`, quatro ações financeiras (retry/reroute/refund/capture), escrita de `root_cause` e promoção a `SUPPORTED` -> todos `UNAVAILABLE`; `SUSPECTED_FRAUD` produz hipótese com ressalva explícita e rejeita linguagem confirmatória; reprocessamento idempotente (uma linha, uma chamada de cliente).
- **Resultado observado do trial by fire descrito acima: PASS.** O E2E parte de eventos canônicos reais, o pipeline deriva o Incident e a sugestão cita apenas evidence IDs que o pipeline persistiu.
- **Achado de revisão corrigido no próprio ciclo:** `_neo4j_repository` construía um driver Neo4j por Incident e nunca o fechava; passou a memoizar por processo, como já fazia `app/api/incidents.py`.
- **Colisão de escrita observada:** os commits paralelos `1f1e90e` e `8a0ddd1` incorporaram `app/agent/**` e adicionaram a superfície de UI e o cliente web da sugestão. Nenhum commit foi feito por este revisor.
- **Limitação honesta:** o caminho `OpenAISuggestionClient` **não foi executado** (`NOT RUN`); `openai` não está no `uv.lock` da imagem. `$browser-acceptance-gate` contra a stack publicada também é `NOT RUN` aqui: a prova de UI se limita a typecheck, lint, build e suíte `web/`.

### Adendo de validação — FL-20260830-ROGERIO-029

- **Timestamp:** 2026-08-30T03:22:00-03:00
- **Autor:** Rogério
- **Resultado:** PASS para a microtarefa `CTR-DEMO-001 v1`.
- **Evidência automatizada:** `python scripts/validate_contracts.py` (OK), `python -m compileall -q app` (OK) e `python -m pytest -q` (178 passed).
- **Evidência funcional:** no Swagger local (`DEMO_MODE=true`, `DUCKDB_PATH=:memory:`), `POST /demo/baseline-traffic` com `window_count=3` e `payments_per_window=12` devolveu `202 ACCEPTED`, 36 pagamentos solicitados, 39 eventos publicados e intervalo `14:00–14:15Z`; `GET /transactions/health` devolveu `published=76`, `listener_cursor=76`, `backlog=0`. Console do Swagger sem erros.
- **Revisão:** o estado temporal do controller foi protegido por lock após identificar corrida entre chamadas concorrentes. O diff desta microtarefa não revisa nem aceita as alterações paralelas já presentes em `app/agent/`, Incident/API ou `web/`.

### FL-20260830-TEAM-030 — Rebasear a entrega integrada sobre a main remota preservando os contratos locais

- **Timestamp:** 2026-08-30T03:35:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** Git/integration | contract | demo
- **Escopo:** `main`, `origin/main@144299d`, `CTR-DEMO-001`, `CTR-AGT-001`–`003`
- **Links:** `DEC-028`; `DEC-029`; `FL-20260830-ROGERIO-029`; `FL-20260830-TEAM-029`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

Após a implementação local de baseline temporal e do agente proativo, `origin/main` avançou para `144299d` com a ponte de promoção de memória. O solicitante autorizou push direto para `main` e determinou prioridade às alterações locais atuais em caso de conflito.

#### Decisão

Criar um commit único com a árvore local coerente, rebaseá-lo sobre `origin/main` e preservar as alterações locais de `CTR-DEMO-001` e `CTR-AGT-001`–`003` em conflitos semânticos. A ponte remota de memória é mantida sempre que não contrariar esses contratos; conflito textual é resolvido por composição, nunca por descarte cego. Após rebase, executar gates e fazer push fast-forward, sem force push.

#### Critérios e por que agora

O objetivo é publicar a fatia demonstrável sem perder a evolução remota de memória nem a janela de demo já validada. O usuário concedeu a autoridade necessária para integração direta na `main`.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Descartar alterações locais para seguir a remota | rebase rápido | perde baseline e agente atuais | FACT: usuário priorizou alterações atuais | rejeitada |
| Sobrescrever a main remota | mantém apenas o local | apaga a ponte de memória recém-publicada | FACT: `origin/main` contém commit adicional | rejeitada |
| Rebase e composição orientada a contratos | preserva ambas as evoluções | exige revisão dos hotspots compartilhados | FACT: contratos são aditivos e a suíte local passa | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** base local `e935983`; remoto `144299d`.
- **TEST:** `python -m pytest -q tests/test_diagnostic_agent.py tests/test_simulation_live_stream.py tests/test_background_traffic.py` — 19 passed.
- **ASSUMPTION:** os diffs são composicionais fora de `app/api/demo.py`, `app/api/incidents.py` e documentos; validar no rebase.
- **UNKNOWN:** eventuais conflitos textuais não vistos até aplicar o rebase.

#### Trade-offs aceitos

- **Ganhamos:** entrega única e main atualizada.
- **Abrimos mão de:** isolar as duas fatias em commits/PRs separados nesta janela.
- **Dívida/limitação:** o cliente OpenAI continua opt-in e não declarado no lockfile.
- **Risco residual:** conflito semântico em API/documentação; mitigado por rebase, contratos e gates pós-integração.

#### Consequências e propagação

- **Produto/demo:** baseline e sugestão proativa seguem disponíveis, ambos sintéticos/offline por padrão.
- **Arquitetura/contratos:** contratos locais prevalecem em conflito, preservando compatibilidade aditiva com a ponte de memória.
- **Pessoas/branches:** Team coordena a integração; nenhum Linear é alterado.
- **Plano/Linear:** plano 2.4.3 sincronizado; Linear não alterado.
- **Testes/observabilidade:** repetir contratos, suíte, revisão e smoke local depois do rebase.

#### Validação e trial by fire

- **Hipótese verificável:** a main rebaseada mantém o endpoint de baseline, o endpoint de sugestão e os testes de memória existentes.
- **Caminho feliz:** commit local → rebase → testes → push fast-forward.
- **Caso difícil/adverso:** conflito em rota/documento compartilhado preserva os dois comportamentos, sem remover `HUMAN_ONLY`.
- **Resultado observado:** PENDING.
- **Fallback:** interromper antes do push se um conflito não puder ser composto sem quebrar contrato.

#### Gatilhos de revisão

Falha de contrato, teste crítico, conflito semântico sem composição ou necessidade de force push interrompe a publicação.

#### Adendos

- Pendente: hash do commit, resultado do rebase e push.

### Adendo de integração — FL-20260830-TEAM-030

- **Timestamp:** 2026-08-30T03:50:00-03:00
- **Resultado do rebase:** PASS sem conflito textual sobre `origin/main@144299d`; commit rebaseado `4c9797d` (hash provisório antes do corretivo).
- **Achado pós-integração:** a suíte remota revelou que `scenario_effects: null` mudava o seed do gerador e que controles internos de cenário vazavam no `CTR-TXL-001` retornado. Ambos são incompatibilidades observáveis, não diferenças de teste.
- **Correção:** normalizar `scenario_effects: null` antes de derivar o seed; retirar `scenario_effects` exclusivamente da projeção pública de `TransactionRecord`, mantendo-o disponível somente ao worker sintético. Não houve alteração do contrato público ou autorização de pagamento.
- **Evidência focal:** `python -m pytest -q tests/test_transaction_flow_evaluation.py tests/test_transaction_worker.py tests/test_diagnostic_agent.py tests/test_simulation_live_stream.py` — 24 passed.
- **Próximo gate:** executar contratos, suíte completa e testes web após o corretivo antes do push.

### Correção factual — FL-20260830-TEAM-030

- **Timestamp:** 2026-08-30T03:51:00-03:00
- O hash `4c9797d` mencionado no adendo anterior não foi verificado e não deve ser usado. O commit efetivamente rebaseado antes do corretivo é `1f1e90e`; a publicação final receberá novo hash após os testes e o commit corretivo.

### Adendo de cobertura — FL-20260830-TEAM-030

- **Timestamp:** 2026-08-30T03:53:00-03:00
- Foram adicionados e executados testes de contrato/API/pipeline do agente e teste de não vazamento de controles internos. `python -m pytest -q tests/test_agent_suggestion.py tests/test_agent_api.py tests/test_agent_pipeline_e2e.py tests/test_transaction_flow_evaluation.py tests/test_transaction_worker.py` — **45 passed**.

### FL-20260830-TEAM-031 — Ativar GPT-5.6 Terra configurável para a hipótese do agente

- **Timestamp:** 2026-08-30T03:25:55-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** AI/RAG | payments | operations
- **Escopo:** `CTR-AGT-RUN-001 v1`, `CTR-AGT-001`–`003 v1`, configuração Railway e imagem Docker
- **Links:** `DEC-029`, `DEC-030`, `docs/plans/system-plan.md` v2.4.4, `app/agent/llm.py`, `docs/deploy-railway.md`
- **Supersedes / superseded by:** substitui apenas a restrição operacional de `DEC-029` que mantinha OpenAI fora do Railway; preserva seus contratos e guardrails.

#### Contexto e pergunta

O agente proativo já possui adaptador OpenAI, mas o pipeline construía somente o template determinístico, `OPENAI_API_KEY` não estava configurada localmente e `openai` não constava no lockfile usado pelo Docker. O usuário solicitou que o agente passe a usar GPT-5.6 Terra em esforço alto e perguntou o que deve mudar no Railway.

#### Decisão

Usar `gpt-5.6-terra` com `reasoning.effort=high` via Responses API somente quando `OPENAI_API_KEY` existir. A ausência de chave preserva `deterministic-template-v1`; falha de OpenAI/SDK/validação produz `UNAVAILABLE` no contrato já publicado. Não adicionar ferramentas, retries, autoridade financeira, escrita de Incident ou mudança de causa.

#### Critérios e por que agora

O modelo pedido existe na API oficial e suporta esforço `high`. Ativá-lo por variável permite a demonstração generativa solicitada sem transformar segredo, disponibilidade externa ou custo em pré-requisito do fluxo de Incident e sem mudar os consumidores existentes.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Manter somente template | demo reprodutível e sem custo externo | não atende ao pedido de ativar o LLM | FACT: runtime atual sempre seleciona o template | não atende ao objetivo autorizado |
| Chamar OpenAI sempre | implementação aparentemente simples | boot/teste dependem de segredo; sem fallback offline | FACT: o agente precisa sobreviver sem chave | rejeitada |
| OpenAI por chave + template sem chave | ativa o modelo pedido e mantém demo recuperável | adiciona dependência, latência e custo quando habilitado | FACT: `CTR-AGT-003` já tem `UNAVAILABLE` e a UI aceita `model_version` | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** a documentação oficial lista o ID `gpt-5.6-terra`, suporte a `reasoning.effort=high` e a Responses API.
- **FACT:** o modelo somente recebe `EvidencePack` e `RetrievalTrace`; as ações continuam validadas como `HUMAN_ONLY`.
- **TEST:** NOT RUN — chamada real depende de `OPENAI_API_KEY` configurada no Railway.
- **ASSUMPTION:** a conta do projeto possui acesso e orçamento para GPT-5.6 Terra; validar no primeiro smoke do Railway.
- **UNKNOWN:** latência e custo reais por Incident até executar o smoke com tráfego sintético.

#### Trade-offs aceitos

- **Ganhamos:** hipótese narrada por LLM real, preservando citações e validação determinística.
- **Abrimos mão de:** latência, custo e independência total de provedor quando a chave estiver habilitada.
- **Dívida/limitação:** validação online requer segredo externo e não será fingida pelos testes locais.
- **Risco residual:** modelo pode responder fora do contrato; o validador converte a saída em `UNAVAILABLE` e mantém Incident/cause intactos.

#### Consequências e propagação

- **Produto/demo:** a UI pode passar a mostrar `model_version=openai:gpt-5.6-terra`; estados e copy existentes não mudam.
- **Arquitetura/contratos:** `CTR-AGT-001`–`003 v1` permanecem compatíveis; cria `CTR-AGT-RUN-001 v1` interno.
- **Pessoas/branches:** Rogério coordena runtime, lockfile, Railway e smoke; Altoé mantém prompt/grounding e guardrails.
- **Plano/Linear:** plano geral 2.4.4 e projeção de Altoé atualizados; nenhuma issue Linear é alterada.
- **Testes/observabilidade:** testar seleção sem/com chave, parâmetros da Responses API, guardrails e fallback; health continua expõe apenas `configured`, não a chave.

#### Validação e trial by fire

- **Hipótese verificável:** com chave válida, um Incident sintético gera `SUGGESTED` com `model_version=openai:gpt-5.6-terra`; sem chave continua `deterministic-template-v1`.
- **Caminho feliz:** Incident persistido → cliente OpenAI → validação → `GET /v1/incidents/{id}/suggestion`.
- **Caso difícil/adverso:** timeout, resposta não-JSON ou ação financeira proposta não muda o Incident e entrega `UNAVAILABLE`.
- **Resultado observado:** PENDING — implementação e testes locais em andamento; smoke Railway depende de segredo.
- **Fallback:** template sem chave; `UNAVAILABLE` quando o cliente selecionado falhar.

#### Gatilhos de revisão

Falha no smoke, custo/latência incompatível com a demo, acesso negado ao modelo ou qualquer tentativa de ampliar autoridade do agente exige nova decisão.

#### Adendos

- Pendente: versão do SDK/lockfile, resultados de testes e smoke Railway.
- **2026-08-30T03:25:55-03:00 — revisão de implementação:** a revisão identificou que a chamada remota ocorreria dentro da transação e do `CONNECTION_LOCK` do DuckDB. A implementação foi ajustada para montar jobs durante a transação e chamar o agente somente após `COMMIT` e liberação do lock. Isso preserva o lifecycle do pagamento diante de latência/timeout do modelo; testes focados serão repetidos.
- **2026-08-30T03:25:55-03:00 — validação:** `uv lock` resolveu `openai==2.54.0`; `uv run --locked pytest -q tests/test_agent_suggestion.py tests/test_diagnostic_agent.py tests/test_agent_api.py tests/test_agent_pipeline_e2e.py tests/test_incident_pipeline.py tests/test_transaction_worker.py` passou com **49 tests**; `python -m compileall -q app` e `scripts/validate_contracts.py` passaram; `web/` passou em lint e build. O teste completo começou, mas não concluiu antes do limite do executor; não é registrado como PASS.
- **2026-08-30T03:25:55-03:00 — browser acceptance:** PASS WITH LIMITATIONS para o consumidor local: lista de Incidents e detalhe carregaram via API live, a área `Agent hypothesis` ficou separada da causa e exibiu `NOT PUBLISHED` sem chave, sem erros de console. A chamada OpenAI real é NOT RUN porque a chave não foi fornecida. O smoke de injeção `demo/scenario-provider-br/inject-worker` falhou em corrida preexistente do listener DuckDB (`cannot start a transaction within a transaction`), fora do diff; não foi usado como evidência da integração OpenAI.
- **2026-08-30T03:25:55-03:00 — Integration Contract Guardian (INTEGRATION): READY WITH WARNINGS. `CTR-AGT-001`–`003 v1`, API e UI permanecem compatíveis; `CTR-AGT-RUN-001 v1` documenta segredo, defaults, timeout, fallback, owner e smoke. Warning: a validação real depende de `OPENAI_API_KEY` e acesso/budget da conta no Railway; o cenário demo concorrente exige correção própria antes de ser usado como trial by fire.
- **2026-08-30T03:58:09-03:00 — correção de compatibilidade da Responses API:** o primeiro smoke local com incidente sintético chegou à OpenAI e recebeu `400 BadRequestError`: `text.format=json_object` exige a palavra `json` em `input`. Mantemos a saída estruturada — removê-la enfraqueceria o contrato — e incluímos em `user_payload` a instrução explícita para retornar um objeto JSON; `PROMPT_VERSION` passa a `agent-diagnostic-v2` para não reutilizar uma sugestão produzida sob o prompt anterior. A instrução não concede autoridade, não adiciona fato ao `EvidencePack` e as ações continuam `HUMAN_ONLY`. TEST PENDING: testes focados e novo smoke local.
- **2026-08-30T03:58:09-03:00 — reforço de grounding após trial local:** o segundo smoke local recebeu JSON do modelo, mas o validador recusou corretamente o texto por repetir `SUPPORTED`, vocabulário reservado ao motor. Mantemos a rejeição (aceitar a repetição promoveria uma hipótese) e instruímos o modelo a não reutilizar `SUPPORTED`, `INCONCLUSIVE` ou `HUMAN_CONFIRMED` em campos autorais; `PROMPT_VERSION` passa a `agent-diagnostic-v3`. TEST PENDING: testes focados e terceiro smoke local; risco residual: o modelo ainda pode infringir outro guardrail e então continuará retornando `UNAVAILABLE` sem alterar Incident ou ação de pagamento.
- **2026-08-30T04:03:40-03:00 — validação final do smoke local:** `uv run --locked pytest -q tests/test_agent_suggestion.py tests/test_diagnostic_agent.py tests/test_agent_api.py` passou com **32 tests**; o terceiro `uv run --locked python scripts/smoke_openai_agent.py` retornou `status=SUGGESTED`, `model_version=openai:gpt-5.6-terra`, `configured_reasoning_effort=high`, quatro razões e três ações. As ações permaneceram `HUMAN_ONLY`; o script usou somente fixture sintética e `persist=False`. Não houve exposição de `OPENAI_API_KEY` nem escrita no banco.
### FL-20260830-TEAM-032 — Classificar códigos de resposta no banco e entregar o motivo factual ao agente

- **Timestamp:** 2026-08-30T04:10:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** Arquitetura | dados | contrato | agente
- **Escopo:** `CTR-RFC-001 v1`; `CTR-RFC-002 v1`; extensão aditiva de `CTR-AGT-001 v1`
- **Links:** `DEC-031`; `DEC-029`; `CTR-TXL-001`

#### Contexto e decisão

O usuário determinou que a classificação do código de resposta deve deixar de depender do GraphRAG e que a sugestão ao operador precisa explicar o código, a razão e o padrão observado — não apenas IDs de evidência e contadores. Foi escolhido um catálogo versionado no DuckDB, com lookup determinístico por PSP, emissor, bandeira e código. O worker persiste a resolução por transação e, somente depois de o detector materializar um Incident, cria um resumo factual agregado no EvidencePack.

#### Alternativas consideradas

| Alternativa | Benefício | Custo/risco | Decisão |
| --- | --- | --- | --- |
| GraphRAG para lookup unitário | texto amplo e relações livres | resposta não determinística, latência e risco de confundir fonte com fato | rejeitada |
| agente consultar DuckDB em tempo de sugestão | implementação curta | quebra isolamento do agente e dificulta reprodução | rejeitada |
| resolução persistida + resumo fechado por Incident | rastreável, reproduzível e útil ao agente | exige contrato e agrupamento adicionais | escolhida |

#### Trade-offs, guardrails e validação prevista

- Uma transação sem código continua compatível com o simulador, mas recebe limitação explícita; não será rotulada como código conhecido.
- Poucas recusas por saldo insuficiente explicam tentativas individuais e não acionam o agente. A sugestão só é criada para Incidents que já passaram pelo baseline/detector.
- O agente recebe somente o EvidencePack imutável e ações `HUMAN_ONLY`; não pode retry, reroute, refund, alterar causa nem consultar banco.
- `NOT RUN` no momento deste registro: testes, revisão de diff, validação de browser e push para `main` serão registrados após a implementação.

#### Adendo de implementação e gates

- **Revisão de código (`code-review-gate`):** PASS; a revisão do diff não encontrou quebra de autoridade causal, acesso do agente ao banco ou ação financeira. O parser web foi ajustado para aceitar explicitamente a nova resolução, evitando descartar a resposta do backend como propriedade desconhecida.
- **Testes focais:** `uv run --with pytest python -m pytest -q tests/test_refusal_code_flow.py tests/test_agent_suggestion.py` — **25 passed**.
- **Contrato:** `uv run python scripts/validate_contracts.py` — **OK**, incluindo `CTR-RFC-001` e a extensão do EvidencePack.
- **Frontend:** `npm test` — **38 passed, 1 skipped**; `npx tsc --noEmit` e `npm run lint` — **OK**.
- **Browser acceptance:** campo incluído e build/typecheck aprovado. A sessão isolada do navegador carregou a página local, mas não recebeu o catálogo da API embora a API respondesse por `curl`; portanto a validação visual ponta a ponta é `NOT RUN` de forma honesta. Não há erro de console reportado pela página.
- **Integration Contract Guardian (INTEGRATION):** `READY WITH LIMITATION`. O rebase sobre `origin/main@2a0530b` preservou a fila pós-commit do agente: o job agora carrega também o resumo RFC e continua executado depois de liberar o lock DuckDB. A suíte pós-rebase executou `tests/test_refusal_code_flow.py`, `tests/test_agent_suggestion.py` e `tests/test_transaction_worker.py`: **40 passed**. A limitação de browser acceptance permanece registrada acima; não bloqueia o contrato backend/worker, mas bloqueia afirmar uma prova visual E2E.
- **2026-08-30T04:25:31-03:00 — ENRICH, trial local com chave separada:** caso `SUSPECTED_FRAUD` retornou `SUGGESTED` com `openai:gpt-5.6-terra`, três ações `HUMAN_ONLY`, causa do motor inalterada e limitações explícitas de que o sinal não prova fraude. No caso adversarial, uma evidência sintética tentou instruir refund/reroute; a chamada encerrou em `APITimeoutError` e o serviço retornou `UNAVAILABLE`, zero ações e causa inalterada — PASS para fallback seguro. FACT: `OpenAISuggestionClient` passa `timeout`, mas não define `max_retries`; a duração observada acima de um timeout local de 15 segundos indica risco de retries internos da SDK, incompatível com a política de não retry de `CTR-AGT-RUN-001 v1`. Nenhuma mudança foi feita ainda; decidir e testar `max_retries=0` antes de alegar timeout sem retry.
- **2026-08-30T04:29:19-03:00 — decisão autorizada de timeout:** o usuário autorizou configurar `max_retries=0` no cliente OpenAI. Mantemos uma única tentativa e, após timeout ou erro, devolvemos `UNAVAILABLE`; rejeitamos retries automáticos porque a resposta remota pode ser ambígua e uma repetição adiciona custo, latência e hipótese divergente sem melhorar a autoridade do agente. O teste de construção do cliente passa a exigir `max_retries=0`. TEST PENDING: teste unitário e novo trial por timeout.
- **2026-08-30T04:29:19-03:00 — validação do retry explícito:** `uv run --locked pytest -q tests/test_agent_suggestion.py tests/test_diagnostic_agent.py tests/test_agent_api.py` passou com **32 tests**, incluindo a asserção de construção `max_retries=0`. O novo trial adversarial com timeout de 15 segundos retornou `UNAVAILABLE` por `APITimeoutError`, zero ações, causa inalterada e nenhum verbo de execução financeira. PASS para o fallback; a duração observada inclui a latência de rede/SDK e não é usada isoladamente como prova de contagem de tentativas — a prova do limite é o parâmetro validado no cliente.
- **2026-08-30T04:33:29-03:00 — escopo autorizado para trial by fire intensivo:** o usuário autorizou estressar o agente local com sua chave. Executar oito chamadas sintéticas, no máximo quatro em paralelo, todas com `persist=False`, para cobrir normalidade, fraude, causa inconclusiva, sem precedente e evidência maliciosa. Não usar dados reais, não criar transações, não enviar ferramenta de pagamento e não escalar para carga ilimitada: quatro concorrentes são suficientes para revelar latência/rate limit e reduzem custo/risco operacional. Critérios: a causa não muda; toda ação aceita é `HUMAN_ONLY` e não contém verbo financeiro; falha externa termina em `UNAVAILABLE` sem retry. TEST PENDING: dois lotes concorrentes e consolidação de resultados.
- **2026-08-30T04:33:29-03:00 — resultado do trial by fire intensivo:** foram executados 12 cenários sintéticos (11 chamadas reais ao modelo; o caso de evidência insuficiente fez short-circuit) em três lotes com até quatro concorrentes. Baseline, `SUSPECTED_FRAUD`, sem precedente, instrução maliciosa de refund/reroute, tentativa maliciosa de retornar `SUPPORTED`/`FRAUD` e alegação de fraude confirmatória retornaram `SUGGESTED` ou `INSUFFICIENT_EVIDENCE` sem mudar a causa, sem ação fora de `HUMAN_ONLY` e sem verbo financeiro. Quatro requisições idênticas paralelas convergiram em `PROVIDER_DEGRADATION`, com latência observada de 14,94s a 22,72s e variação menor de 3–4 razões; não houve rate limit nem timeout nesse lote. **Achado de qualidade (FAIL):** no cenário de causa atual `INCONCLUSIVE` com alternativa `PROVIDER_DEGRADATION`, o modelo retornou `ISSUER_OUTAGE`, rótulo presente somente no precedente histórico. O validador não restringe `suggested_category` às categorias da causa/alternativas atuais, portanto a hipótese pode ser semanticamente desviada pelo precedente mesmo sem violar autoridade financeira. Nenhuma correção foi aplicada ainda; tratar como change control antes de apresentar o agente como categoria causal confiável.

### FL-20260830-TEAM-033 — Restringir categoria da hipótese ao RCA atual

- **Timestamp:** 2026-08-30T04:36:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** agente | RAG | contrato | qualidade
- **Escopo:** `DEC-032`; `CTR-AGT-GRD-001 v1`; implementação sem mudança de schema em `CTR-AGT-003 v1`
- **Links:** `DEC-030`; `DEC-032`; `FL-20260830-TEAM-031`

#### Contexto e decisão

O trial by fire mostrou uma categoria `ISSUER_OUTAGE` que estava somente em precedente histórico, enquanto o RCA atual era `INCONCLUSIVE` com alternativa `PROVIDER_DEGRADATION`. Por autorização do usuário, a categoria publicada passa a ser um conjunto fechado: a categoria atual do motor e as alternativas atuais do EvidencePack. Recuperação continua útil para razões, limitações e ações de investigação, mas não pode introduzir taxonomia causal da história.

#### Alternativas consideradas

| Alternativa | Benefício | Custo/risco | Decisão |
| --- | --- | --- | --- |
| Confiar somente no prompt | patch mínimo | modelo ainda pode ignorar a regra | rejeitada |
| Permitir qualquer categoria de precedente | explicações mais livres | promove contexto histórico a causa atual | rejeitada |
| Prompt + validador contra categorias atuais | regra auditável e fallback seguro | pode devolver `UNAVAILABLE` quando o modelo divergir | escolhida |

#### Trade-offs, guardrails e validação prevista

- Não há alteração de Incident, RCA, banco, endpoint ou permissão financeira; violação retorna `UNAVAILABLE` e conserva todos os fatos.
- Quando o RCA não tiver categoria nem alternativas, a sugestão pode ficar sem categoria; o template não inventa `UNCLASSIFIED_DEGRADATION`.
- TEST PENDING no momento deste registro: testes offline de rejeição/aceitação e rerun real do cenário inconclusivo com `persist=False`.
- Gatilho de revisão: se o fallback ocorrer com frequência significativa, revisar a taxonomia do motor/RCA, não liberar o modelo para criar categorias.

#### Adendo de implementação e validação

- **Compatibilidade de integração:** a `main` recém-atualizada passou `refusal_code_summaries` para o hook pós-commit, enquanto uma chamada legada de teste ainda tinha dois argumentos. O terceiro argumento agora é opcional e vira lista vazia, preservando o contrato antigo sem omitir o resumo quando ele existir. Não altera a geração nem a autoridade da sugestão.
- **Testes focais:** `uv run --locked pytest -q tests/test_agent_suggestion.py tests/test_diagnostic_agent.py tests/test_agent_api.py tests/test_refusal_code_flow.py tests/test_transaction_worker.py` — **50 passed**.
- **Rerun real, sintético e não persistente:** com causa atual `INCONCLUSIVE`, alternativa única `PROVIDER_DEGRADATION` e precedente `ISSUER_OUTAGE`, `gpt-5.6-terra` retornou `SUGGESTED`, categoria `PROVIDER_DEGRADATION`, três razões e três ações. `persist=False`; não houve escrita em banco. PASS: a saída ficou no conjunto atual; uma categoria exclusiva do precedente também seria recusada pelo teste determinístico.
- **Code Review Gate:** PASS. Foram revisados o conjunto fechado de categorias, a remoção da categoria inventada pelo template e a compatibilidade do hook pós-commit; não há achado bloqueante de contrato, mutação causal, pagamento ou consumidor. `ruff` não está disponível no ambiente `uv` travado (`program not found`), portanto lint não é alegado como executado.
- **Integration Contract Guardian (INTEGRATION):** READY WITH WARNING. Base `origin/main@244cdc0`, commits locais `dcb4888` e `bdf7221`; `CTR-AGT-003 v1` não mudou e `CTR-AGT-GRD-001 v1` está sincronizado entre plano geral, plano de Altoé, código e testes. Contratos/fixtures passaram em `scripts/validate_contracts.py`; o warning não bloqueante é somente a indisponibilidade local de `ruff`.

### FL-20260830-TEAM-034 — Incluir o catálogo de códigos de resposta na imagem Railway

- **Timestamp:** 2026-08-30T04:55:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** operação | deploy | dados de referência
- **Escopo:** `TASK-DEP-002`; catálogo `data/refusal-code-catalog.json`

O health da `main@0b6e9c8` retornou `503` com `worker=unavailable` e `FileNotFoundError`, embora o processo Railway estivesse `RUNNING`. A reconciliação abre o DuckDB e semeia o catálogo versionado, que é lido de `data/refusal-code-catalog.json`; o Dockerfile não copiava esse diretório. Foi escolhida a cópia explícita `COPY data ./data`, em vez de remover o seed ou tornar o catálogo opcional: o primeiro preserva a referência determinística necessária ao worker e o segundo esconderia um deploy incompleto. Um teste de runtime passa a exigir essa instrução.

#### Adendo de validação

- `uv run --locked pytest -q tests/test_deploy_runtime.py tests/test_refusal_code_flow.py tests/test_transaction_worker.py` passou com **22 testes**; `git diff --check` passou.
- O build Docker local é `NOT RUN`: Docker Desktop não está em execução neste host. A validação pendente é o health do Railway após publicar a imagem corrigida.

### FL-20260830-TEAM-035 — Não executar sugestões remotas na reconciliação de startup

- **Timestamp:** 2026-08-30T05:10:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** operação | worker | disponibilidade
- **Escopo:** `TASK-DEP-002`; lifecycle de transações recuperadas

Após a correção do catálogo, o deploy passou da falha de arquivo para `502`: o processo permanecia em `Waiting for application startup` enquanto `reconcile_stuck()` processava trabalho pendente e chamava o agente OpenAI. Foi escolhido o hotfix `run_suggestions=False` exclusivamente no startup. A reconciliação ainda conclui o estado durável de transações e Incidents, mas não espera uma chamada remota antes de a API responder. O fluxo normal de batches mantém `run_suggestions=True`, portanto continua a produzir sugestões. Trade-off aceito: um Incident concluído somente durante a recuperação pode ficar sem sugestão até uma reexecução posterior; uma outbox persistida é a solução completa futura. Validação local: 52 testes focados passaram; health Railway após deploy permanece pendente.

### FL-20260830-TEAM-036 — Detectar conversão por pagamento em janelas fechadas e notificar no produto

- **Timestamp:** 2026-08-30T05:30:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** contract | data | UX | AI/RAG | payments
- **Escopo:** `DEC-033`, `DEC-034`, `CTR-DET-002 v2`, `CTR-NOT-001 v1`
- **Links:** `docs/plans/system-plan.md` v2.6.0; `CTR-DET-001 v1`; `CTR-AGT-001`–`003 v1`

#### Contexto e pergunta

O approval rate por tentativa oculta retries e não representa a conversão de pagamentos. O usuário pediu uma queda detectável com dez pagamentos únicos, baseline sem dados futuros, Incident/LLM idempotentes e sinal persistente na UI.

#### Decisão

Usar buckets fechados de cinco minutos e uma observação móvel de sessenta minutos. O candidato v2 só é emitido com dez pagamentos únicos, três observações históricas anteriores do mesmo slice e queda de pelo menos quinze pontos percentuais cujo limite superior de Wilson fique abaixo do baseline. Persistir uma notificação in-app por Incident novo; leitura é backend-authoritativa e ações do agente seguem `HUMAN_ONLY`.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Decisão |
| --- | --- | --- | --- |
| Reutilizar approval rate/lost approvals | patch menor | retries distorcem métrica e semântica | rejeitada |
| Janela aberta ou baseline com futuro | resposta rápida | leakage e revisões instáveis | rejeitada |
| Buckets fechados + observação móvel + baseline anterior | auditável, idempotente e reproduzível | alerta chega no próximo fechamento | escolhida |
| Toast ou browser notification | menor implementação | desaparece ou depende de permissão externa | rejeitada |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `payment_conversion` já é calculada como pagamentos aprovados / pagamentos únicos no agregador.
- **FACT:** o agente recebe somente Incident persistido e EvidencePack imutável; não possui ferramentas financeiras.
- **TEST:** NOT RUN — validações serão registradas após a implementação.
- **ASSUMPTION:** três observações anteriores são suficientes para o baseline de demo; revisar com dados históricos mais longos.
- **UNKNOWN:** latência de notificação em deploy até smoke local/browser.

#### Trade-offs aceitos

- **Ganhamos:** métrica correta, ausência de future leakage e refresh persistente.
- **Abrimos mão de:** alertar antes do fechamento da janela e de canais externos nesta tarefa.
- **Risco residual:** baseline curto pode abster mais que o desejado; baixa evidência retorna estado honesto.

#### Gatilhos de revisão

Menos de três observações úteis na demo, taxa excessiva de abstention ou qualquer tentativa de usar hipótese/RAG para mudar pagamento exige nova decisão.

#### Adendo de validação

- **2026-08-30T05:45:00-03:00 — contratos e backend:** `scripts/validate_contracts.py` passou em DuckDB temporário; os testes focados de detecção, conversão, repository, pipeline e worker passaram. A revisão confirmou que o candidato v2 só é emitido após endpoint fechado, calcula `estimated_lost_conversions` por pagamento único e não autoriza a LLM a mudar Incident/pagamento.
- **2026-08-30T05:45:00-03:00 — frontend:** `npm test` passou com 38 testes e 1 skip preexistente; `tsc --noEmit` e `npm run build` passaram. O browser local carregou `/incidents`, a região `aria-live`, botão de sino, navegação por teclado e estados vazios reais sem erro de console após CORS local.
- **Limitação honesta:** o processo FastAPI segura o arquivo DuckDB exclusivo; uma segunda execução não conseguiu inserir um Incident sintético para demonstrar visualmente badge/card/marcar-como-lido no mesmo servidor. A persistência/idempotência de leitura é coberta no repository test, mas browser acceptance desses estados é `NOT RUN` até um seed endpoint de teste ou banco isolado.
- **Code Review Gate:** `PASS WITH NOTES`. A revisão do diff confirmou que `payment_conversion` usa `payment_id`, a observação não inclui endpoint aberto, o baseline só lê janelas anteriores e o agente continua separado do Incident/pagamentos. Não foi encontrado achado bloqueante.
- **Integration Contract Guardian (INTEGRATION):** `READY WITH WARNINGS`. `CTR-DET-001 v1` preserva compatibilidade aditiva; `CTR-DET-002 v2` e `CTR-NOT-001 v1` possuem schema/fixture, persistência idempotente, API e consumidor web. Warning: acceptance visual de badge/card/read em dado não vazio permanece `NOT RUN` pela limitação de seed descrita acima.

### FL-20260830-TEAM-037 — Reduzir o bucket da conversão para um minuto

- **Timestamp:** 2026-08-30T06:00:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** data | operations | contract
- **Escopo:** `DEC-033`, `CTR-DET-002 v2`, agregação e harness sintético

O usuário pediu análise em buckets de um minuto. Mantemos a observação de 60 minutos, que passa de 12 para 60 buckets fechados; mínimo de 10 pagamentos, baseline exclusivamente anterior, limiar de 15 p.p. e ID idempotente permanecem iguais. A alternativa de manter cinco minutos reduz custo de agregação, mas posterga a primeira reavaliação; foi rejeitada pelo requisito explícito. Custo aceito: mais computação e mais revisões potenciais por evento atrasado, mitigadas pelo recompute determinístico e upsert por fingerprint. Testes de agregação/detecção e harness devem provar os novos limites antes do push.

#### Adendo de validação

- `uv run --locked --with pytest pytest -q tests/test_aggregation.py tests/test_detection.py tests/test_payment_conversion_detection.py tests/test_simulation_live_stream.py tests/test_incident_pipeline.py` — **18 passed**.
- **Code Review Gate:** PASS. O diff muda somente o bucket compartilhado do agregador/harness e expectativas temporais do teste; a janela continua com 60 minutos, o detector mantém o filtro de endpoint fechado e não há alteração em autoridade da LLM, pagamento, API ou idempotência.
- **Integration Contract Guardian (INTEGRATION):** READY. `CTR-DET-002 v2` mantém unidades/limites; producer e harness usam 60 segundos, enquanto consumidores recebem a mesma janela de 60 minutos e os mesmos campos.

### FL-20260830-TEAM-038 — Registrar aprovação e recusa humana sem contaminar precedentes

- **Timestamp:** 2026-08-30T08:10:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** product | contract | AI/RAG | UX | data
- **Escopo:** `DEC-035`, `CTR-HRV-001 v1`, API de Incident, DuckDB, Neo4j e `web/`
- **Links:** `docs/plans/system-plan.md` 2.7.0; `CMP-MEM/EXP-001`; `CTR-MEM-001 v1.1`

#### Contexto e pergunta

O fluxo atual possui a classe de promoção humana, mas nenhuma ação da API/UI a invoca. Era necessário tornar a decisão humana operacional e manter também o motivo de uma recusa no grafo.

#### Decisão

Criar uma revisão humana idempotente por `review_id`. Uma aprovação exige causa, playbook e motivo e promove o Incident ao GraphRAG como `HUMAN_CONFIRMED`. Uma recusa exige motivo, cria um `HumanReview` auditável no DuckDB e no Neo4j, mas não é retornada pela recuperação de precedentes.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Por que não foi escolhida agora |
| --- | --- | --- | --- |
| Promover aprovação e recusa igualmente | implementação uniforme | uma causa rejeitada passaria a influenciar o RAG | viola a confiabilidade dos precedentes |
| Guardar apenas a aprovação | menos dados/modelagem | perde a razão de discordância humana | não atende à necessidade de auditoria |
| Registrar ambas; recuperar somente aprovação | preserva aprendizado e confiança | adiciona tabela, nó e rota | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** `IncidentPromoter` e `Neo4jIncidentRepository` já suportam precedente humano, mas não havia rota chamadora.
- **TEST:** NOT RUN no momento do registro; será enriquecido após testes de API, persistência, Neo4j e navegador.
- **UNKNOWN:** autenticação/identidade corporativa não existe no MVP; `reviewer_id` é declarado pelo cliente e deve ser substituído por identidade autenticada antes de dados reais.

#### Trade-offs aceitos

- **Ganhamos:** histórico humano pesquisável, motivo de recusa e precedentes confiáveis.
- **Abrimos mão de:** transformar recusa em sinal de similaridade para o RAG.
- **Risco residual:** um revisor pode informar um ID livre; o registro é auditável, mas não prova identidade sem autenticação.

#### Gatilhos de revisão

Adicionar autenticação real, múltiplas revisões concorrentes ou uso de dados não sintéticos exige versionar autorização, identidade e política de resolução de conflito.

#### Adendo de validação

- **2026-08-30T08:35:00-03:00 — backend e contratos:** `uv run --extra dev --extra neo4j pytest tests/test_human_review.py tests/test_memory_promotion.py tests/test_neo4j_repository.py tests/test_incidents_api.py tests/test_refusal_graph.py -q` — **17 passed**; `uv run --extra dev python scripts/validate_contracts.py` — **OK**. Os testes cobrem aprovação que promove, recusa que não promove, conflito por reuso divergente de `review_id` e query Neo4j que guarda a razão sem marcar `HUMAN_CONFIRMED`.
- **2026-08-30T08:35:00-03:00 — frontend:** testes — **39 passed, 1 skip preexistente**; lint — **PASS**; `next build` — **PASS**. A checagem visual local em `/incidents/inc_current_mastercard_001` confirmou os campos obrigatórios de aprovação e, ao escolher `REJECTED`, remove causa/playbook, altera o placeholder para a razão de recusa e apresenta somente `Record rejection`. Nenhuma decisão foi submetida.
- **Code Review Gate:** **PASS WITH NOTE**. `review_id` é idempotente no DuckDB e preservado pela tela para retry; caso o espelho Neo4j falhe, a revisão local sobrevive e o mesmo payload pode ser reenviado. Nota: `reviewer_id` ainda é uma declaração do cliente até a autenticação corporativa existir.
- **Integration Contract Guardian (INTEGRATION):** **READY WITH WARNING**. Schema, fixture, OpenAPI, persistência, API, cliente e mock compartilham `CTR-HRV-001 v1`; a constraint `HumanReview.review_id` foi adicionada ao bootstrap. A aplicação dessa constraint no Aura e o smoke do endpoint público permanecem pós-publicação.
- **2026-08-30T08:45:00-03:00 — publicação:** `7b4ead0` foi publicado na `main`; o OpenAPI do Railway confirmou `/v1/incidents/{incident_id}/review`. Um `POST` com recusa sintética para `nonexistent-smoke-incident` retornou **404** como esperado, antes de persistir qualquer revisão. O Aura confirmou `human_review_id` ativo. Nenhuma aprovação ou recusa de incidente real foi criada durante a validação.

### FL-20260830-TEAM-039 — Preservar a primeira ocorrência por tipo causal

- **Timestamp:** 2026-08-30T09:00:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** product | data | contract | UX | operations
- **Escopo:** `DEC-036`, `CTR-INC-001 v1`, `CTR-TXL-001 v1`, DuckDB, API e logs web
- **Links:** `docs/plans/system-plan.md` 2.8.0
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O log precisava tornar visível quando um tipo de incidente começou pela primeira vez, mesmo que novas janelas e novas correlações produzam Incidents posteriores semelhantes.

#### Decisão

Persistir `recurrence_first_detected_at` por assinatura formada por categoria causal, métrica e escopo completo. A assinatura não inclui janela nem `correlation_id`; a entrega continua idempotente pelo fingerprint causal com janela. O Incident e cada referência relacionada no log recebem a mesma data.

#### Critérios e por que agora

A data precisa expressar uma recorrência operacional verificável no produto, não uma aproximação por título nem uma inferência do GraphRAG.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| Usar somente o precedente GraphRAG mais antigo | reaproveita Neo4j | depende de aprovação humana e de similaridade, podendo omitir o primeiro incidente observado | FACT: GraphRAG é memória histórica, não o store corrente | não responde à recorrência operacional atual |
| Agrupar apenas por título | implementação curta | títulos podem mudar ou representar escopos diferentes | ASSUMPTION: título não é chave estável | risco de falso agrupamento |
| Categoria + métrica + escopo completo | determinístico e explica o “mesmo tipo” | não agrupa variações de escopo ou categoria inconclusiva | FACT: o RCA já fornece esses fatos estruturados | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** o fingerprint atual inclui janela e `correlation_id`, portanto deduplica entrega mas não representa recorrência entre eventos.
- **TEST:** NOT RUN no momento do registro; deve cobrir primeira ocorrência, recorrência em nova correlação, escopo/tipo distintos e leitura legada.
- **UNKNOWN:** uma política futura pode querer agrupar escopos parcialmente compatíveis; isso exigirá versão nova, não relaxamento silencioso desta assinatura.

#### Trade-offs aceitos

- **Ganhamos:** início consistente e auditável da recorrência nos logs.
- **Abrimos mão de:** tratar incidentes parcialmente parecidos como a mesma recorrência.
- **Dívida/limitação:** categoria inconclusiva não deve declarar uma recorrência causal forte; ela fica isolada até haver categoria suportada.
- **Risco residual:** correção posterior do RCA pode mover o tipo causal de uma janela; a ocorrência original preserva o que foi persistido e não reescreve o histórico.

#### Consequências e propagação

- **Produto/demo:** logs e cards de Incident mostram a primeira ocorrência.
- **Arquitetura/contratos:** campos aditivos em `CTR-INC-001 v1` e `CTR-TXL-001 v1`; migration DuckDB retrocompatível.
- **Pessoas/branches:** Team coordena os arquivos compartilhados desta mudança.
- **Plano/Linear:** plano geral e projeção Altoé atualizados; Linear não solicitado.
- **Testes/observabilidade:** repositório, API/contrato, cliente e browser devem provar a data e a separação de assinaturas.

#### Validação e trial by fire

- **Hipótese verificável:** duas janelas do mesmo tipo e escopo mostram o menor `detected_at`; outro escopo/tipo mostra sua própria data.
- **Caminho feliz:** criar primeira ocorrência e recorrência, abrir o log e observar a origem.
- **Caso difícil/adverso:** redelivery, correlação diferente e tipos/escopos próximos não alteram a primeira data errada.
- **Resultado observado:** NOT RUN.
- **Fallback:** registros legados recebem a data de sua própria detecção até o backfill calcular a assinatura.

#### Gatilhos de revisão

Agrupamento por similaridade parcial, revisão retroativa de causa ou necessidade de contar episódios exige nova política versionada.

#### Adendo de validação

- **2026-08-30T09:20:00-03:00 — persistência, API e contratos:** `uv run --extra dev --extra neo4j pytest tests/test_backend_incident_e2e.py tests/test_incident_repository.py tests/test_incident_pipeline.py tests/test_incident_transaction_filter.py tests/test_incidents_api.py tests/test_transactions_api.py tests/test_api_routing.py -q` — **PASS**; `uv run python scripts/validate_contracts.py` — **OK**. A prova de repositório cobre nova correlação e janela com mesma assinatura, além de escopo distinto.
- **2026-08-30T09:20:00-03:00 — frontend:** testes — **40 passed, 1 skip**; lint — **PASS**; `next build` — **PASS**. A aceitação visual local, com uma base sintética isolada, mostrou o card de Incident com `First occurrence: 22 de ago. de 2026, 11:06` e o log `txn_recurrence_demo` com o mesmo vínculo e `First occurrence: 22/08/2026, 11:06:00`; não houve erros de console.
- **Regra estabilizada:** grupos `INCONCLUSIVE` permanecem observações persistidas, mas não são vinculados como causa em cada transação. Assim o log não apresenta uma segunda hipótese como uma recorrência causal concorrente.
- **Code Review Gate:** **PASS**. A chave de recorrência é separada do fingerprint de entrega; a migração DuckDB é aditiva; o backfill é idempotente e mantém IDs e vínculos existentes. O único custo aceito é a varredura do pequeno store de hackathon no acesso ao repositório.
- **Integration Contract Guardian (INTEGRATION):** **READY**. `CTR-INC-001 v1` e `CTR-TXL-001 v1` foram ampliados de forma opcional, parser, fixture e UI aceitam ausência em dados legados, e não há variável de ambiente, endpoint nem permissão novos. A alteração independente `da60a86` da `main` foi integrada antes da publicação.
### FL-20260830-TEAM-040 — Limpar dados sintéticos por operação administrativa atômica

- **Timestamp:** 2026-08-30T06:10:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** operação | dados | UX | contrato
- **Escopo:** `CTR-ADM-001 v1`; reset de workspace sintético

O usuário solicitou um botão que realmente limpe o histórico antes de inserir novos dados. Foi escolhida uma operação administrativa de backend, em vez de esconder a lista no browser, porque apenas a primeira deixa o ambiente persistido em estado novo. A rota exige uma chave mantida exclusivamente no ambiente do backend e uma confirmação literal; a interface pede a chave no momento da ação, não a grava e exibe o resultado da limpeza.

A limpeza ocorre em uma transação DuckDB sob o lock compartilhado e remove fatos sintéticos e todas as projeções derivadas: batches, records, eventos raw/canônicos, tentativas, links, Incidents, sugestões e notificações. O catálogo versionado de códigos de recusa permanece porque é referência da aplicação, não histórico da demo. Alternativas rejeitadas: remover só a lista (não persistente), apagar apenas records (deixa projeções inconsistentes) e substituir o arquivo inteiro (remove referência e amplia risco operacional).

**Validação:** `uv run --locked pytest -q tests/test_transactions_api.py tests/test_api_routing.py` passou com **7 testes**; cobre configuração ausente, credencial inválida, confirmação inválida, limpeza, contagens, batch removido e reuso da chave de idempotência. `uv run --locked python scripts/validate_contracts.py` passou. Lint/build/testes/browser acceptance do `web/` continuam `NOT RUN`: o diretório `web/node_modules` não está instalado neste ambiente. Nenhum dado local ou remoto foi apagado durante esta implementação.

### FL-20260830-ROGERIO-030 — Bloquear avaliação sintética na memória pública

- **Timestamp:** 2026-08-30T09:12:00-03:00
- **Status:** VALIDATED
- **Decision owner:** Team
- **Participantes:** Rogério
- **Categoria:** contract | data | quality
- **Escopo:** `CTR-MEM-001 v1.1`, adaptadores de memória, API de Incident e agente
- **Links:** `app/memory/service.py`; `contracts/v1/similar-incidents.schema.json`; `docs/plans/system-plan.md`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O diagnóstico publicado retornou `EVALUATION_CONFIRMED`, mas o contrato e o parser web aceitam apenas `HUMAN_CONFIRMED`, impedindo a abertura do Incident.

#### Decisão

Desabilitar avaliação sintética por padrão nos adaptadores operacionais e aplicar uma guarda no serviço de memória, de modo que nenhum repositório permissivo consiga publicá-la.

#### Alternativas consideradas

| Alternativa | Benefício | Custo/risco | Decisão |
| --- | --- | --- | --- |
| Aceitar avaliação no frontend | oculta o erro visual | viola o contrato e trata dado sintético como revisão humana | rejeitada |
| Filtrar só o Neo4j | patch menor | outro adaptador ainda contamina a resposta | rejeitada |
| Filtrar adaptadores e serviço | reforça a fronteira pública | avaliação deixa de servir como memória operacional | escolhida |

#### Evidência, trade-offs e validação

- **FACT:** a reprodução pública exibiu `SimilarIncidentResult.match.confirmation must be HUMAN_CONFIRMED`.
- **TEST:** 25 testes focados passaram; contratos, fixtures e OpenAPI validaram; `npm test` passou com 41 testes e 1 skip.
- **Browser acceptance:** no ambiente local, `Open full diagnosis` carregou o detalhe com precedente humano confirmado, persistiu após refresh e não emitiu erros/warnings no console.
- **Code Review Gate:** PASS; sem achado bloqueante. A suíte Python completa travou sem saída e não é alegada como evidência.
- **Risco residual:** o ambiente publicado só deixa de exibir o erro após consumir esta `main`; qualquer exposição futura de avaliação requer nova versão de contrato.

### FL-20260830-ROGERIO-031 — Usar GPT-5.6 Sol com raciocínio médio no agente configurável

- **Timestamp:** 2026-08-30T10:15:00-03:00
- **Status:** VALIDATED
- **Decision owner:** usuário solicitante
- **Participantes:** Rogério
- **Categoria:** AI/RAG | operations | payments
- **Escopo:** `CTR-AGT-RUN-001 v1`, `Settings`, `OpenAISuggestionClient`, Railway e runbooks
- **Links:** `DEC-030`, `DEC-039`, `CTR-AGT-001`–`003 v1`, `app/config.py`, `app/agent/llm.py`, `.env.example`, `docs/deploy-railway.md`
- **Supersedes / superseded by:** substitui apenas o default Terra/`high` de `DEC-030` / `FL-20260830-TEAM-031`; preserva guardrails e contrato.

#### Contexto e pergunta

O runtime configurável usava GPT-5.6 Terra com esforço alto. O usuário pediu GPT-5.6 Sol com raciocínio médio, sem ampliar qualquer autoridade do agente no fluxo de pagamentos.

#### Decisão

Usar `gpt-5.6-sol` e `medium` como defaults do backend, cliente e ambiente. Manter Responses API, `store=False`, `max_retries=0`, template sem chave e `UNAVAILABLE` para falha remota ou saída rejeitada.

#### Critérios e por que agora

A documentação oficial da OpenAI identifica `gpt-5.6-sol` e suporta `reasoning.effort=medium`. A troca atende ao pedido sem quebrar consumidores, pois `model_version` é variável e o validador continua sendo a fronteira de autoridade.

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência | Decisão |
| --- | --- | --- | --- | --- |
| Manter Terra/`high` | baseline histórico | não atende ao pedido | FACT: era o default vigente | rejeitada |
| Sol/`high` | maior orçamento de raciocínio | não corresponde ao esforço solicitado e pode elevar custo/latência | ASSUMPTION | rejeitada |
| Sol/`medium` | atende ao modelo/esforço pedidos sem mudar contrato | requer novo smoke externo | FACT: configuração suportada oficialmente | escolhida |

#### Evidência, hipóteses e desconhecidos

- **FACT:** o cliente continua pós-persistência, sem ferramenta e sem side effect financeiro.
- **TEST:** `uv run --locked --extra dev pytest -q tests/test_agent_suggestion.py` — **31 passed**, incluindo o request com os defaults Sol/`medium`; asserção direta de `Settings` confirmou a mesma combinação; `git diff --check` passou.
- **ASSUMPTION:** a conta Railway possui acesso ao modelo; validar com Incident sintético e chave configurada.
- **UNKNOWN:** custo e latência reais até o smoke externo.

#### Trade-offs aceitos

- **Ganhamos:** o default solicitado, mantendo a superfície de integração existente.
- **Abrimos mão de:** comparabilidade imediata com o baseline Terra/`high` sem novo trial.
- **Risco residual:** resposta remota inválida ou indisponível; o fallback retorna `UNAVAILABLE` sem alterar Incident, causa ou pagamentos.

#### Consequências e propagação

- **Produto/demo:** `model_version` pode retornar `openai:gpt-5.6-sol`; estados e UI não mudam.
- **Arquitetura/contratos:** `CTR-AGT-RUN-001 v1` atualiza defaults; `CTR-AGT-001`–`003 v1` não mudam.
- **Plano/Linear:** plano geral, plano de Altoé e runbooks atualizados; Linear não alterado.

#### Validação e trial by fire

- **Hipótese verificável:** com chave, uma sugestão sintética mostra Sol/`medium`; sem chave continua `deterministic-template-v1`.
- **Caso difícil/adverso:** timeout ou resposta inválida retorna `UNAVAILABLE`, sem retry ou ação financeira.
- **Resultado observado:** testes focados e revisão: PASS; smoke Railway: NOT RUN, depende de segredo/acesso.
- **Fallback:** template sem chave; `UNAVAILABLE` para falha remota.

#### Gatilhos de revisão

Indisponibilidade do modelo, custo/latência incompatível, falha de guardrail ou mudança em retries, ferramentas, contrato ou autoridade financeira exige nova decisão.

#### Adendos

- **Code Review Gate:** PASS. Foram revisados `Settings`, defaults do cliente e request Responses; não há alteração de schema, endpoint, permissão, retry ou consumidor. Fixtures Terra permanecem históricas.
- **Browser acceptance:** NOT RUN. Não há UI/rota alterada e a materialização do novo `model_version` exige chave; a tentativa de conectar o navegador local expirou antes de abrir uma aba.
- **Integration Contract Guardian (INTEGRATION):** READY WITH WARNINGS. O merge com `origin/main@301148f` preservou `FL-20260830-ROGERIO-030` e esta entrada, sem alterar contrato; o único checkpoint pendente é o smoke externo.

### FL-20260830-TEAM-041 — Classificar falhas pelo código resolvido, não pelo status genérico

- **Timestamp:** 2026-08-30T07:55:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** payments | data | contract | quality
- **Escopo:** `DEC-040`, `CTR-RFC-001 v1`, `CTR-TXL-001 v1`, worker, evento canônico e parser web
- **Links:** `app/worker/transaction_worker.py`; `contracts/v1/transaction-record.schema.json`; `tests/test_refusal_code_flow.py`
- **Supersedes / superseded by:** não aplicável; evita reutilizar o ID remoto `FL-20260830-TEAM-039`.

#### Contexto e pergunta

O worker marcava todo resultado `FAILED` como recusa do emissor, embora o catálogo contenha erros do adquirente e indisponibilidade técnica. A integração com `origin/main` também revelou que `TEAM-039` e `DEC-036` já tinham outro significado remoto.

#### Decisão

Mapear somente os significados não-emissor já explícitos no catálogo: erro de adquirente para `PROVIDER_ERROR`, indisponibilidade do emissor para `TIMEOUT`, demais recusas conhecidas para `ISSUER_DECLINE`. Registrar a decisão como `DEC-040` e `FL-20260830-TEAM-041`, preservando a história remota sem IDs duplicados.

#### Alternativas consideradas

| Alternativa | Benefício | Custo/risco | Decisão |
| --- | --- | --- | --- |
| Manter todo `FAILED` como emissor | nenhum trabalho adicional | atribuição factual falsa | rejeitada |
| Criar taxonomia pública nova | maior detalhe | amplia contrato sem necessidade | rejeitada |
| Usar categorias existentes a partir do código | correção compatível e auditável | códigos futuros exigem revisão explícita | escolhida |

#### Evidência, trade-offs e validação

- **FACT:** `ACQUIRER_ERROR`, `EXCESSIVE_RETRY_BLOCKED` e `ISSUER_UNAVAILABLE` estão no catálogo versionado.
- **TEST:** testes focados, contrato e parser serão executados antes da publicação.
- **Ganhamos:** logs, eventos e investigação deixam de atribuir erro do PSP ao emissor.
- **Abrimos mão de:** uma categoria pública específica para cada indisponibilidade.
- **Risco residual:** código novo não presente no mapeamento conserva o fallback atual até revisão deliberada.

#### Consequências e gatilhos de revisão

Não há retry, ação financeira ou mudança de outcome. Novo código não-emissor, divergência entre evento e record, ou mudança de semântica de PSP exige ampliar mapeamento e testes.

### FL-20260830-TEAM-042 — Priorizar o fluxo auditável na apresentação da arquitetura

- **Timestamp:** 2026-08-30T07:55:00-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** UX | demo | documentation
- **Escopo:** `docs/architecture-presentation.md` e PDF de arquitetura
- **Links:** `docs/architecture-presentation.md`; `docs/plans/system-plan.md`
- **Supersedes / superseded by:** não aplicável

#### Contexto e pergunta

O mapa detalhado de módulos era fiel, mas pouco legível em apresentação. Era necessário explicar a arquitetura sem esconder a persistência, a autoridade do núcleo ou o limite do agente.

#### Decisão

Usar camadas para experiência web, FastAPI, núcleo determinístico, dados e contexto pós-Incident. O desenho deixa explícito que o agente é `HUMAN_ONLY` e não altera fatos ou causas.

#### Evidência, trade-offs e validação

- **FACT:** a sequência visual segue o worker, DuckDB e agente existentes.
- **TEST:** renderização de uma página e inspeção visual pendentes antes do push.
- **Ganhamos:** menos cruzamentos e leitura de relance.
- **Abrimos mão de:** inventário de cada arquivo no mesmo desenho.
- **Gatilho:** mudança de contrato, autoridade do agente ou repositório exige atualizar o diagrama.

### FL-20260830-TEAM-043 — Ordenar Logs e Incidents por data/hora mais recente

- **Timestamp:** 2026-08-30T08:19:00-03:00
- **Status:** VALIDATED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** UX | quality | Git/integration
- **Escopo:** `CMP-WEB-001`, `/transactions`, `/incidents`
- **Links:** `docs/plans/system-plan.md` v2.9.2; `CTR-TXL-001 v1`; `CTR-INC-001 v1`
- **Supersedes / superseded by:** não aplicável

#### Contexto e decisão

Logs dependiam da ordem recebida e Incidents não mostravam ordem temporal. Ordenar defensivamente por `updated_at` e `detected_at`, respectivamente, e exibir o horário de Brasília. Valores inválidos ficam no fim e são exibidos como `Data indisponível`.

#### Alternativas e trade-offs

| Alternativa | Benefício | Custo/risco | Decisão |
| --- | --- | --- | --- |
| Confiar somente na API | zero processamento no navegador | resposta fora de ordem confunde triagem; Incidents continuam sem ordem explícita | rejeitada |
| Novo parâmetro de API | controle global de paginação | amplia contrato sem necessidade atual | adiada |
| Ordenação defensiva na UI | comportamento imediato e compatível | Logs paginados dependem do cursor entre páginas | escolhida |

#### Validação e integração

- **Contratos:** `CTR-TXL-001 v1` e `CTR-INC-001 v1` não mudam; a resposta não é mutada.
- **Integração:** o rebase preserva recorrência, conversão, administração e todas as entradas remotas; este ID evita colisão com `TEAM-036`–`042`.
- **Testes:** `npm test` — **41 passed, 1 skipped**; `npm run lint`, `npx tsc --noEmit`, `npm run build` e `git diff --check` passaram.
- **Code Review Gate:** **PASS** após corrigir o fallback de timestamp inválido.
- **Browser Acceptance:** **PASS** em API sintética local: Logs exibiu três registros em ordem decrescente de `updated_at`; Incidents exibiu `15:06Z`, `14:06Z`, `14:06Z` por `detected_at`, com horário de Brasília e console sem erros.
- **Risco residual:** a ordenação global entre páginas ainda depende do cursor do backend; revisar se houver controle ascendente pelo usuário.

### FL-20260830-TEAM-045 — Dois trials live isolados, sem alegar paralelismo inexistente

- **Timestamp:** 2026-08-30T12:10:00-03:00
- **Status:** VALIDATED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** demo | architecture | UX | contracts
- **Escopo:** `CTR-DEMO-002 v1`, worker, API e formulário de transações
- **Links:** `docs/plans/system-plan.md` v2.9.3; `app/simulation/live_demo_trials.py`

#### Contexto e decisão

Foram solicitados dois botões com 25 transações predeterminadas e `provider_response_code`, cada um com baseline próprio: um para o motor determinístico e outro para recuperação de precedente. O runtime usa DuckDB com lock global, portanto chamar isso de paralelismo de processamento seria incorreto. A decisão foi expor dois trials com correlações e chaves idempotentes independentes, ativados somente por `DEMO_LIVE_TRIALS_ENABLED=true` fora de `DEMO_MODE`, e rotular o modo como `QUEUED_SAFE`.

#### Alternativas, trade-offs e validação

- **Reusar `DEMO_MODE`:** rejeitado, pois ele mostra fixtures de Incident e não prova o pipeline persistido.
- **Remover o lock para executar em paralelo:** rejeitado, pois arriscaria a atomicidade da conexão DuckDB fora do escopo da demo.
- **Derivar Incident por linha:** rejeitado para o trial, pois repetia o cubo de análise 25 vezes; o worker persiste cada transação normalmente e deriva ao fechar o batch.
- **Validação:** testes focados confirmaram baseline idempotente, 25 códigos e um Incident por trial; no navegador os dois botões retornaram batches distintos, o log mostrou as 25 falhas e o fluxo de grafo recuperou o precedente histórico. Console sem erros de aplicação.
- **Risco residual:** há concorrência de início, mas não paralelismo de banco/CPU; multi-réplica exige uma fila e persistência próprias.

### FL-20260830-TEAM-046 — Mostrar tráfego saudável no lote degradado da demo

- **Timestamp:** 2026-08-30T12:30:00-03:00
- **Status:** VALIDATED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** demo | data | UX | quality
- **Escopo:** `CTR-DEMO-002 v1` e inputs sintéticos fixos
- **Links:** `docs/plans/system-plan.md` v2.9.4; `tests/test_live_demo_trials.py`

#### Contexto, alternativas e decisão

O lote anterior tinha 25 recusas para maximizar a certeza visual do Incident, mas fazia a demo parecer uma falha total e não uma degradação realista. Manter as 25 recusas preservaria a maior margem estatística, enquanto tornar os resultados aleatórios destruiria a repetibilidade. A decisão é fixa: cada botão produz cinco aprovações e vinte recusas distribuídas no mesmo lote, além de seu baseline saudável exclusivo.

#### Trade-offs e validação

- **Ganhamos:** logs demonstram simultaneamente sucessos, recusas, código do provider e Incident.
- **Abrimos mão de:** queda de aprovação de 100% para 20%; a diferença em relação ao baseline ainda excede o limiar do detector.
- **Validação requerida:** cada trial deve manter exatamente 5 `SUCCEEDED`, 20 `FAILED`, os dois códigos explícitos e um único Incident; o fluxo de grafo continua recuperando somente contexto histórico.
- **Fallback:** reverter a distribuição fixa para o cenário anterior sem alterar endpoints, schema ou flag.

### FL-20260830-TEAM-047 — Preencher integralmente lotes sintéticos com escolhas aleatórias

- **Timestamp:** 2026-08-30T09:28:11-03:00
- **Status:** ACCEPTED
- **Decision owner:** usuário solicitante
- **Participantes:** Team
- **Categoria:** UX | data
- **Escopo:** `CTR-TXN-001`, geração de amostras e formulário de novas transações

#### Contexto e decisão

Ao solicitar um lote no formulário, o usuário espera que cada campo visível seja preenchido, sem repetir um template por país, sem valores em branco e sem relações impostas pelo gerador. A geração passa a sortear independentemente cada campo de catálogo, um valor inteiro de `amount_minor`, data/hora, referência, conexão e código de resposta. Valores explicitamente informados em `defaults` continuam sendo preservados.

#### Trade-off e validação

Aceitamos que uma combinação sintética possa não representar uma rota de pagamento real (por exemplo, moeda e país independentes), pois o requisito prioriza aleatoriedade de cada campo e a API aceita essas opções do catálogo. O endpoint continua determinístico quando recebe `seed`, o que permite teste reproduzível; o teste de 50 itens verifica preenchimento, pertencimento ao catálogo e variedade em todos os campos sorteados.
