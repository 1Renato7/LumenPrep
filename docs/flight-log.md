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

- Nenhum.

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

## André

<!-- ANDRE: faça append de novas entradas imediatamente antes da próxima seção. -->

_Nenhuma decisão registrada._

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

- Nenhum.

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

## Prontidão para a banca

_Preencher no modo `FINALIZE`._

| Lente | Estado | Evidência | Lacuna/ação |
| --- | --- | --- | --- |
| Funciona? | NOT READY | — | Ligar execução ponta a ponta e trial by fire |
| Profundidade e julgamento | PARTIAL | FL-20260829-TEAM-001 | Registrar decisões reais do sistema |
| Resolve o problema real | NOT READY | — | Ligar decisões ao enunciado e casos difíceis |
| Originalidade | NOT READY | — | Explicar o insight original como mecanismo |
| Experiência e clareza | PARTIAL | Este arquivo é legível no repo | Validar com leitor externo e demo |
