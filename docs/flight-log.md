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

## André

<!-- ANDRE: faça append de novas entradas imediatamente antes da próxima seção. -->

_Nenhuma decisão registrada._

## Altoé

<!-- ALTOE: faça append de novas entradas imediatamente antes da próxima seção. -->

_Nenhuma decisão registrada._

## Rogério

<!-- ROGERIO: faça append de novas entradas imediatamente antes da próxima seção. -->

_Nenhuma decisão registrada._

## Renato

<!-- RENATO: faça append de novas entradas ao final desta seção. -->

_Nenhuma decisão registrada._

## Prontidão para a banca

_Preencher no modo `FINALIZE`._

| Lente | Estado | Evidência | Lacuna/ação |
| --- | --- | --- | --- |
| Funciona? | NOT READY | — | Ligar execução ponta a ponta e trial by fire |
| Profundidade e julgamento | PARTIAL | FL-20260829-TEAM-001 | Registrar decisões reais do sistema |
| Resolve o problema real | NOT READY | — | Ligar decisões ao enunciado e casos difíceis |
| Originalidade | NOT READY | — | Explicar o insight original como mecanismo |
| Experiência e clareza | PARTIAL | Este arquivo é legível no repo | Validar com leitor externo e demo |
