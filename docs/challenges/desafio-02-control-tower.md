# Desafio 02 — The Control Tower

**Fonte:** <https://nextwave-hackathon-2026.vercel.app/challenges/file-02> · lida em 29/08/2026
**Competição:** 6 crews globais neste desafio (vs. 4 no 03)
**Uma frase:** detectar quedas de conversão em um stream de pagamentos ao vivo, **diagnosticar a causa raiz** cruzando 6 dimensões, explicar com evidência e dinheiro, priorizar incidentes simultâneos e recomendar ação — **sem executá-la**.

---

## 1. O que o desafio pede (checklist oficial)

| # | Requisito | Observação |
|---|---|---|
| 1 | Observar stream ao vivo e detectar quedas **que importam**, separando de ruído normal (hora do dia, fim de semana, variância) | falso positivo é falha explícita |
| 2 | Diagnosticar a **causa raiz** navegando `merchant × provider × method × country × issuing bank × decline code` até isolar onde está | o núcleo do desafio |
| 3 | Explicar com evidência: *what, where, since when, who is affected, quanto custa e por que o sistema acredita nisso* — em linguagem de operações | |
| 4 | Priorizar múltiplos incidentes simultâneos e **admitir honestamente quando a evidência é insuficiente** | |
| 5 | Recomendar ação para o humano, **sem executar** | "this challenge diagnoses, it doesn't remediate" |

**Pode incluir (opcional):** custo em dinheiro por incidente; comparação com histórico esperado; memória de incidentes passados.

**Trial by fire:** o júri injeta ao vivo um incidente nunca ensaiado — **uma nova combinação de dimensões**. O sistema tem que detectar e diagnosticar sozinho.

## 2. Demo exigida (o roteiro já vem pronto)

1. Stream mockado rodando normal → **o sistema não dispara em ruído**
2. Queda real injetada ao vivo → detectada em tempo razoável
3. Diagnóstico de causa raiz correto, **com a evidência visível**
4. Explicação legível + custo estimado + ação recomendada
5. **Dois incidentes simultâneos separados e priorizados corretamente**
6. Trial by fire passado

**Bônus:** (a) caso em que o sistema admite evidência insuficiente em vez de inventar; (b) reconhecer incidente repetido usando memória ("isso já aconteceu terça"); (c) explicação para dois públicos — operação (detalhe) e executivo (uma linha com o dinheiro).

## 3. Caso mínimo ficcional dado

PagoTotal, orquestrador com 3 merchants × 3 providers em MX/CO/BR. Momentos: operação normal → provider passa a recusar demais **só no Brasil** → ao mesmo tempo um banco emissor mexicano cai **para um único merchant** → júri injeta o dele. Transações, decline codes, dashboards e histórico **podem ser inventados**.

---

## 4. Mapa de dificuldade

### 🔴 Difícil de verdade (é aqui que se ganha ou perde)

- **Isolamento de causa raiz em 6 dimensões.** Explosão combinatória: não dá para varrer todos os cruzamentos ingenuamente nem para chutar "o provider". Precisa de um mecanismo real — análise de contribuição / drill-down hierárquico com significância estatística (família Adtributor/contribution analysis). **É exatamente aqui que mora a nota da lente 4 (Originality) e da lente 2 (Depth).**
- **Separar dois incidentes simultâneos.** Não é rodar o detector duas vezes: depois que o incidente A explica parte da queda, é preciso **recalcular o resíduo** e diagnosticar B no que sobrou. Sem isso, o sistema reporta o mesmo incidente duas vezes com nomes diferentes. É o item da demo em que a maioria dos times vai falhar.
- **Baseline sem falso positivo.** Distinguir queda real de sazonalidade e variância exige um modelo de comportamento esperado (por hora/dia-da-semana/dimensão) e um teste de significância — não um threshold fixo.
- **Sobreviver ao trial by fire.** Só sobrevive se a detecção for genuinamente estatística e genérica. Qualquer atalho hardcoded morre ao vivo.

### 🟡 Médio

- Priorização entre incidentes (precisa de uma função de severidade defensável: dinheiro × volume × confiança × duração — não "o maior número").
- Memória de incidentes (fingerprint do incidente + busca por similaridade no histórico). Conceitualmente simples, mas é trabalho.
- Explicação em dois níveis via LLM.

### 🟢 Fácil / barato

- **Gerador de stream de transações.** Nós controlamos os dados: volume, sazonalidade e injeção de incidente viram configuração. É a alavanca mais barata do desafio inteiro.
- **Console de injeção de incidentes** (formulário: escolher dimensões, taxa de recusa, duração, início). Barato de construir e **é o que desarma o trial by fire** — o júri injeta pela nossa UI, com formato que já conhecemos.
- Custo em dinheiro = aprovações perdidas × ticket médio. Aritmética trivial, retorno narrativo enorme.
- Dashboard: timeline + tabela de dimensões + trilha de drill-down. Nada exótico.

### ⚠️ Armadilhas

- **Deixar o LLM diagnosticar.** Mata a lente 2: em Q&A não há como defender "por que essa dimensão e não aquela". O diagnóstico tem que ser determinístico e auditável; **o LLM é só o narrador** da evidência já calculada.
- Alertar por threshold e chamar de detecção — o próprio enunciado condena isso ("alerts fire on everything or on nothing").
- Implementar remediação. O enunciado proíbe. Tempo gasto ali é tempo jogado fora.

---

## 5. Como atacar (fatia vertical primeiro, conforme conselho do júri)

**Hora 0–4 — esqueleto ponta a ponta feio:** gerador de stream → janela de agregação → detector de queda em **uma** dimensão → tela mostrando "conversão caiu". Roda de ponta a ponta.
**Hora 4–10 — o mecanismo:** drill-down multidimensional com significância + explain-away do resíduo (os dois incidentes). É o coração; recebe o maior investimento.
**Hora 10–16 — os casos feios:** evidência insuficiente, custo em dinheiro, priorização, console de injeção.
**Hora 16–20 — narrativa:** explicação em dois públicos, memória de incidentes, README + diagrama + decision log.
**Hora 20–24 — ensaio do trial by fire:** cada um do time injeta um incidente que os outros não conhecem. Repetir até não quebrar.

---

## 6. Leitura contra os critérios do júri

| Lente | Aderência | Comentário |
|---|---|---|
| 1. Does it work? | **Alta** | Sistema determinístico, sem latência de LLM no caminho crítico. Demo reprodutível, baixa variância ao vivo. |
| 2. Depth & judgment | **Muito alta** | Cada escolha (janela, teste estatístico, ordem de drill-down, função de severidade) é um trade-off real e defensável. Decision log escreve-se sozinho. |
| 3. Solves the real problem | **Alta**, se os "ugly cases" forem feitos | Os casos feios estão nomeados no enunciado: ruído, dois incidentes, evidência insuficiente. |
| 4. Originality | **Depende inteiramente do mecanismo** | Threshold + LLM = solução óbvia. Contribution analysis com explain-away = mecanismo que o júri provavelmente não viu. |
| 5. Experience & clarity | **Média** | Menor apelo visual. Compensa com a linha executiva do dinheiro e uma trilha de evidência legível. |

**Perfil de risco:** risco técnico concentrado em **algoritmo** (resolvível pensando), risco de demo **baixo**. Teto visual mais baixo, piso muito mais alto.
