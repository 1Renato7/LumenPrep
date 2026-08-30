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

### FL-20260829-ROGERIO-006 — Estender CTR-INC-001 v1 com hipóteses ordenadas sem mudar a causa atual

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

### FL-20260829-ROGERIO-007 — Priorizar impacto apenas dentro da mesma moeda sem FX implícito

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

### FL-20260829-ROGERIO-008 — Exigir fingerprint causal exato para separar incidentes simultâneos

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

## Prontidão para a banca

_Preencher no modo `FINALIZE`._

| Lente | Estado | Evidência | Lacuna/ação |
| --- | --- | --- | --- |
| Funciona? | NOT READY | — | Ligar execução ponta a ponta e trial by fire |
| Profundidade e julgamento | PARTIAL | FL-20260829-TEAM-001 | Registrar decisões reais do sistema |
| Resolve o problema real | NOT READY | — | Ligar decisões ao enunciado e casos difíceis |
| Originalidade | NOT READY | — | Explicar o insight original como mecanismo |
| Experiência e clareza | PARTIAL | Este arquivo é legível no repo | Validar com leitor externo e demo |
