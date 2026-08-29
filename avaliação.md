# Avaliação — conformidade com os critérios do NextWave Hackathon 2026

**Fonte oficial:** <https://nextwave-hackathon-2026.vercel.app/judging> (+ `/challenges`, `/schedule`)
**Última verificação da fonte:** 29/08/2026
**Status do documento:** vivo — atualizado a cada checkpoint de integração
**Responsável pela manutenção:** (definir na abertura)

---

## 0. Como usar este arquivo

Este arquivo é o **delimitador de escopo** do time. Ele existe para responder, a qualquer momento do evento, três perguntas:

1. O que exatamente o júri avalia? (§1 e §2 — texto oficial, sem interpretação)
2. Estamos somando pontos ou desperdiçando tempo? (§3 e §4 — placar interno)
3. Por que decidimos assim? (§6 — log de decisões, que é **entregável obrigatório**)

**Ritual mínimo:** a cada checkpoint (§8), alguém abre este arquivo, atualiza o placar (§4), marca os entregáveis (§5) e registra as decisões novas (§6). Sem evidência real, não se marca nada como pronto — regra do `AGENTS.md`.

> ⚠️ **Aviso que vem do próprio júri.** Um dos itens explicitamente listados como *"o que não pontua"* é **"building for the rubric"** — times que perseguem as cinco lentes uma a uma acabam rasos nas cinco. Portanto: este documento é um **piso de conformidade e um detector de lacunas**, não um alvo a ser maximizado. Se o placar aqui e a profundidade do produto entrarem em conflito, **a profundidade do produto vence** e o placar é que está errado.

---

## 1. Não existe pontuação numérica oficial

**Isto é importante e precisa ficar claro para todo o time:** a página de avaliação **não publica pontos, percentuais nem pesos numéricos**. O que ela publica é:

- **cinco lentes**, declaradas como *"listadas aproximadamente em ordem de peso"* (`roughly in order of weight`);
- a ressalva explícita de que *"nenhuma delas sozinha decide um vencedor"* (`none of them alone decides a winner`);
- um processo de **ranking ordinal**: cada jurado classifica os projetos de forma independente e depois o painel delibera em conjunto.

Ou seja: **não somos pontuados, somos ordenados** — comparativamente, contra os outros times, por um painel que depois conversa entre si. Qualquer número neste documento (§3) é **instrumento interno de autoavaliação criado pelo time**, nunca a régua oficial. Não repetir esses números em slides, README ou pitch como se fossem do evento.

---

## 2. Critérios oficiais (texto-fonte)

### 2.1 Os três princípios

| # | Princípio | Texto oficial | O que significa na prática para nós |
|---|---|---|---|
| A | **Depth over difficulty** | *"Picking the hardest challenge earns nothing by itself. A modest scope solved deeply beats an ambitious scope solved superficially."* | Escolher o desafio mais difícil não dá ponto. Escopo pequeno resolvido a fundo > escopo grande resolvido raso. **Corta features, não profundidade.** |
| B | **Working beats promised** | *"We evaluate what runs in front of us, live, not what the slides say it will do."* | Só conta o que roda ao vivo. Slide que promete não vale nada. |
| C | **Judgment beats spectacle** | *"The technical defense weighs as much as the demo. A spectacular demo the team can't explain loses to a simpler demo defended with clear reasoning."* | **A defesa técnica pesa tanto quanto a demo.** Ninguém pode ter uma parte do sistema que não sabe explicar. |

### 2.2 As cinco lentes (ordem oficial de peso)

| Lente | Pergunta que o júri faz (texto oficial) | Tradução operacional |
|---|---|---|
| **1. Does it work?** | *"Does the system run end to end and pass the trial by fire — reacting correctly to what the judges change live, without the team touching anything?"* | O sistema roda ponta a ponta e sobrevive ao **trial by fire**: o jurado opera o sistema ao vivo, com entrada não ensaiada, e ele reage certo **sem ninguém do time tocar em nada**. |
| **2. Depth & judgment** | *"Is the architecture sound? Can the team explain every major decision, the alternatives they rejected and why? Does the decision log show real trade-offs?"* | Arquitetura sólida; o time explica **toda** decisão importante, as alternativas rejeitadas e o porquê; o **decision log mostra trade-offs reais** (não uma lista de tecnologias). |
| **3. Solves the real problem** | *"Does it hit the challenge's objective as written — including the ugly cases — rather than a generic product that happens to be nearby?"* | Atinge o objetivo do desafio **como está escrito**, incluindo os **casos feios**. Produto genérico que passa perto não conta. |
| **4. Originality** | *"Is there an idea here we haven't seen before — an approach, an insight, a mechanism — or is it the obvious solution executed adequately?"* | Existe uma abordagem, insight ou **mecanismo** que o júri não viu antes — ou é a solução óbvia bem executada? |
| **5. Experience & clarity** | *"Would the human on the other side actually use it? Is the pitch clear, the demo legible, the repo readable by someone who wasn't there?"* | Usabilidade real; pitch claro; demo legível; **repositório legível por quem não estava lá**. |

### 2.3 O que explicitamente NÃO pontua

- Número de features, slides, integrações ou linhas de código.
- Buzzwords — *"nomear um framework não é uma decisão de design; saber por que você o escolheu, sim."*
- Vídeo caprichado de algo que não roda ao vivo.
- **Perseguir a rubrica** (ver aviso em §0).

### 2.4 Conselho oficial do júri

> *"Get the thinnest possible version working end to end in the first hours. Then spend the rest of the 24h making it deep — handling the ugly cases, understanding your own trade-offs, and rehearsing the trial by fire. Teams that do this in the other order run out of time with a beautiful front and nothing behind it."*

**Consequência direta no nosso plano:** fatia vertical ponta a ponta **primeiro**, mesmo feia. Depois: casos feios, trade-offs e **ensaio do trial by fire**. Nunca o contrário.

### 2.5 Protocolo dos desafios

- **Escolher um** dos quatro desafios. A escolha é **final**.
- **Inventar livremente**: dados, fluxos, APIs, bancos, frameworks e protocolos são livres — *mas é preciso saber defender cada escolha*.
- **Trial by fire**: os jurados operam o sistema ao vivo, com entrada não ensaiada, na frente de todos.

### 2.6 Como a avaliação acontece

- **Domingo, 30/08** — pitches logo após o code freeze; campeões de cidade e vencedores globais anunciados no mesmo dia.
- **Formato por time:** pitch curto → demo ao vivo → trial by fire → Q&A técnico.
- **Painel:** jurados da Yuno e da Nauta. Todo projeto é visto pelo painel completo; jurados classificam de forma independente e depois deliberam juntos.
- **Entregáveis:** slides, demo, repositório GitHub público com README, diagrama de arquitetura, decision log. *"Missing deliverables are noticed."*

### 2.7 ⚠️ Divergência conhecida na fonte — resolver com a organização

As duas páginas oficiais informam durações diferentes para o pitch:

| Página | Texto |
|---|---|
| `/judging` | *"Each team: short pitch → live demo → trial by fire → technical Q&A — **10 minutes per team**. City champions give a 15-minute final pitch (10 presentation + 5 questions)."* |
| `/schedule` | Pitches — *"**7 minutes per team**"* |

**Decisão de risco do time:** ensaiar para **7 minutos** (o pior caso) e ter uma extensão opcional até 10. Um pitch que estoura o tempo perde a Q&A, que é onde a lente 2 é ganha. **Confirmar com a organização no dia.**

### 2.8 Relógio (por site)

| Site | T-ZERO (sáb 29/08) | Code freeze (dom 30/08) |
|---|---|---|
| São Paulo | 12:30 | 12:30 |
| Buenos Aires | 12:30 | 12:30 |
| Bogotá | 10:30 | 10:30 |
| Cidade do México | 09:30 | 09:30 |

Desafios anunciados 30 min antes do T-ZERO. Depois do freeze: pitches → campeões de cidade (T+27:00) → vencedores (T+29:00).

---

## 3. Instrumento interno de autoavaliação

> **Não oficial.** Criado pelo time para detectar lacunas. Os pesos abaixo são a nossa leitura da frase *"roughly in order of weight"*.

**Pesos internos:** L1 35% · L2 25% · L3 20% · L4 12% · L5 8%

**Escala por lente (0–5):**

| Nota | Significado |
|---|---|
| 0 | Não existe. |
| 1 | Existe no plano, não no código. |
| 2 | Existe no código, não roda ponta a ponta. |
| 3 | Roda no caminho feliz, ensaiado. |
| 4 | Roda com entrada não ensaiada; casos feios tratados. |
| 5 | Roda com entrada hostil, degrada com elegância e o time defende cada decisão sem hesitar. |

**Regras de leitura do placar:**

- **L1 ≤ 2 é estado de emergência.** Todo o time para o que está fazendo e volta para a fatia ponta a ponta. Nenhuma outra lente compensa L1 baixo.
- **Nenhuma lente pode ficar em 0** perto do freeze — o júri avisa que times que otimizam lente por lente ficam rasos em todas.
- Perto do freeze, **melhorar L1 de 3 → 4 vale mais que L4 de 3 → 5**.

---

## 4. Placar vivo

> Atualizar a cada checkpoint. Coluna **Evidência** só aceita fato verificável: commit, log de execução, gravação do ensaio, print. Sem evidência, a nota não sobe.

| Lente | Peso | Nota (0–5) | Evidência | Maior lacuna agora | Ação / dono |
|---|---|---|---|---|---|
| 1. Does it work? | 35% | — | — | — | — |
| 2. Depth & judgment | 25% | — | — | — | — |
| 3. Solves the real problem | 20% | — | — | — | — |
| 4. Originality | 12% | — | — | — | — |
| 5. Experience & clarity | 8% | — | — | — | — |

**Histórico de checkpoints**

| Quando | L1 | L2 | L3 | L4 | L5 | Decisão tomada no checkpoint |
|---|---|---|---|---|---|---|
| — | | | | | | |

---

## 5. Entregáveis obrigatórios

*"Missing deliverables are noticed."* — a ausência de qualquer item abaixo é notada pelo júri.

| # | Entregável | Onde vive | Dono | Status | Evidência |
|---|---|---|---|---|---|
| D1 | Apresentação (slides) | — | — | ☐ | — |
| D2 | Demo (ao vivo) | — | — | ☐ | — |
| D3 | Repositório GitHub **público** com README | — | — | ☐ | — |
| D4 | Diagrama de arquitetura | — | — | ☐ | — |
| D5 | **Decision log** — alternativas consideradas e por que escolhemos o que escolhemos | §6 deste arquivo | — | ☐ | — |

**Notas de conformidade:**

- **D3 — "público".** O repositório precisa estar público **antes do freeze**. Verificar também que o README é legível *"por alguém que não estava lá"* (lente 5): o que é, como rodar, como o sistema está desenhado.
- **D5 — o decision log é dois entregáveis em um.** É item obrigatório da lista **e** é a evidência direta da lente 2 (*"Does the decision log show real trade-offs?"*). Um log com "escolhemos X porque é rápido" não mostra trade-off e não pontua. Formato obrigatório em §6.
- **D2 — demo.** A página `/challenges` admite "live or video", mas `/judging` é inequívoca: *"A polished video of something that doesn't run live"* não pontua, e o trial by fire exige o sistema rodando. **Planejar demo ao vivo.** Vídeo só como plano B de rede/energia, nunca como entrega principal.

---

## 6. Decision log (entregável D5)

> **Regra:** toda decisão que alguém do time possa ser questionado sobre no Q&A entra aqui, **no momento em que é tomada** — não no domingo de manhã. Reconstruir trade-offs de memória produz exatamente o log raso que a lente 2 penaliza.
>
> **Formato obrigatório.** Uma decisão sem "alternativa rejeitada" e sem "o que perdemos" não é uma decisão documentada — é uma justificativa.

### Modelo

```
### DEC-000 — <título curto da decisão>
- **Data/hora:**
- **Contexto:** que problema forçou a decisão
- **Escolha:** o que decidimos
- **Alternativas rejeitadas:** A (por quê não), B (por quê não)
- **O que ganhamos:**
- **O que perdemos / dívida aceita:**
- **Como isso aparece no sistema:** arquivo, endpoint, contrato (ex.: CTR-API-001)
- **Quem defende no Q&A:**
- **Lente(s) afetada(s):** L1 / L2 / L3 / L4 / L5
```

### Decisões registradas

#### DEC-001 — Adotar este arquivo como delimitador de escopo e decision log do time
- **Data/hora:** 29/08/2026, antes do T-ZERO
- **Contexto:** o júri exige um decision log como entregável e avalia se ele mostra trade-offs reais. Sem um lugar único e acordado, cada pessoa registra decisões no seu próprio canal e o log só existiria no domingo, reconstruído de memória.
- **Escolha:** um único arquivo versionado na raiz do repositório, que reúne critérios oficiais, placar interno e decision log.
- **Alternativas rejeitadas:** (a) log só nos commits — não mostra alternativas rejeitadas nem trade-off, e o júri lê o log, não o histórico; (b) documento externo (Notion/Docs) — sai do repositório público, que é justamente um dos entregáveis; (c) issues do Linear — ferramenta interna, não entregável, e o júri não terá acesso.
- **O que ganhamos:** um só lugar para atualizar, versionado, público junto do código, e legível por quem não estava lá.
- **O que perdemos / dívida aceita:** exige disciplina de atualização durante o evento; se ninguém atualizar nos checkpoints, o arquivo vira ruído.
- **Como isso aparece no sistema:** `avaliação.md` na raiz do repositório.
- **Quem defende no Q&A:** (definir)
- **Lente(s) afetada(s):** L2, L5

<!-- Próximas decisões: DEC-002 em diante, sempre no formato acima. -->

---

## 7. Trial by fire — a lente de maior peso

O trial by fire é onde a lente 1 (35% do nosso peso interno) é ganha ou perdida. As condições estão declaradas na fonte oficial:

> *"Judges will operate your system live, with an unrehearsed input, in front of everyone. It must react correctly without the team touching anything."*

Três palavras carregam todo o risco: **operate** (é o jurado no teclado, não nós), **unrehearsed** (entrada que nunca vimos), **without the team touching anything** (nada de "deixa eu só rodar aqui").

### Checklist de sobrevivência

| # | Item | Status | Evidência |
|---|---|---|---|
| T1 | Alguém de fora do time consegue operar o sistema sem instrução verbal | ☐ | — |
| T2 | Entrada vazia / campo em branco não quebra | ☐ | — |
| T3 | Entrada absurda, longa ou fora de domínio degrada com mensagem clara — não com stack trace | ☐ | — |
| T4 | Entrada em outro idioma / com acentos / com emoji não quebra | ☐ | — |
| T5 | Dependência externa fora do ar tem fallback ou mensagem honesta (nunca tela branca) | ☐ | — |
| T6 | Sem passo manual escondido (seed, cache quente, terminal aberto, aba específica) | ☐ | — |
| T7 | Sistema roda a partir de estado limpo, do zero, sem intervenção | ☐ | — |
| T8 | Latência do caminho principal cabe no tempo do palco | ☐ | — |
| T9 | Nada depende do Wi-Fi do evento — ou há plano B testado | ☐ | — |
| T10 | Ensaiado ao menos **duas vezes**, com pessoa de fora do time no teclado, com entrada que ela inventou | ☐ | — |

**T10 é o item que mais times pulam e é o único que prova os outros nove.** Reservar bloco de tempo antes do freeze.

### Casos feios do desafio (lente 3)

O júri pede explicitamente *"including the ugly cases"*. Preencher assim que o desafio for anunciado — os casos feios do **enunciado**, não os genéricos:

| # | Caso feio | Comportamento esperado | Tratado? | Evidência |
|---|---|---|---|---|
| U1 | — | — | ☐ | — |

---

## 8. Checkpoints — quando este arquivo é revisado

Alinhado aos checkpoints de integração já exigidos pelo `AGENTS.md` (contratos/esqueletos → primeira fatia ponta a ponta → integração final).

| Checkpoint | Momento | O que se verifica aqui |
|---|---|---|
| CP0 | Logo após a escolha do desafio | Preencher §7 (casos feios). Registrar DEC da escolha do desafio e do recorte de escopo. |
| CP1 | Contratos e esqueletos congelados | Primeira passada no placar (§4). Marcar donos dos entregáveis (§5). |
| CP2 | **Primeira fatia ponta a ponta rodando** | **Portão duro: L1 ≥ 3.** Se não atingiu, cortar escopo — não adicionar. Registrar o corte como DEC. |
| CP3 | ~T+16h | Casos feios (§7) e decision log (§6) em dia. L1 deve estar em 4. |
| CP4 | Antes do freeze | Ensaio do trial by fire (T10). Todos os entregáveis (§5) marcados com evidência. Repositório **público**. |
| CP5 | Após o freeze, antes do pitch | Ensaio cronometrado (7 min, ver §2.7). Cada pessoa sabe qual DEC defende. |

---

## 9. Preparação do Q&A técnico

A defesa técnica pesa tanto quanto a demo (princípio C). O Q&A é curto e vem depois do trial by fire — não há tempo para procurar resposta.

| Área do sistema | Quem defende | Decisões que essa pessoa precisa saber explicar | Pronta? |
|---|---|---|---|
| — | — | DEC-xxx | ☐ |

**Perguntas que o time deve conseguir responder sem hesitar:**

1. Por que este recorte do problema e não o desafio inteiro? (princípio A)
2. Qual foi a alternativa mais séria que vocês rejeitaram, e o que ela teria dado de melhor?
3. O que quebra este sistema? Onde ele degrada primeiro?
4. Qual é a dívida técnica que vocês aceitaram de propósito?
5. O que aqui não é a solução óbvia? (lente 4)
6. O que vocês fariam com mais 24 horas?

> A resposta "não implementamos, mas sabíamos o trade-off e escolhemos priorizar X" **pontua**. A resposta "não deu tempo" não pontua. É a mesma informação com e sem julgamento.

---

## 10. Riscos abertos

| # | Risco | Impacto | Mitigação | Status |
|---|---|---|---|---|
| R1 | Duração do pitch divergente entre as páginas oficiais (7 vs 10 min) — §2.7 | Estourar o tempo e perder a Q&A, onde a lente 2 é ganha | Ensaiar para 7 min; confirmar com a organização no dia | Aberto |
| R2 | Repositório ainda não público no freeze | Entregável D3 ausente — *"missing deliverables are noticed"* | Item de CP4 | Aberto |
| R3 | Decision log escrito só no final | Log raso, sem trade-offs reais → derruba a lente 2 (25%) | Registrar no momento da decisão; verificado em CP3 | Aberto |
| R4 | Demo depender de passo manual do time | Falha direta no trial by fire → derruba a lente 1 (35%) | Itens T6, T7 e T10 | Aberto |

---

## Apêndice — rastreabilidade da fonte

Todo texto entre aspas neste documento foi extraído literalmente das páginas oficiais em 29/08/2026:

- `https://nextwave-hackathon-2026.vercel.app/judging` — princípios, cinco lentes, o que não pontua, formato do julgamento, entregáveis
- `https://nextwave-hackathon-2026.vercel.app/challenges` — protocolo (escolher um, inventar livremente, trial by fire), lista de entregáveis
- `https://nextwave-hackathon-2026.vercel.app/schedule` — horários por site, duração do pitch

**Se a organização atualizar qualquer uma dessas páginas durante o evento, este arquivo precisa ser reconferido.** Os desafios estavam `[ CLASSIFIED ]` no momento desta extração.
