# Briefing da banca — Lumen

**Objetivo:** permitir que qualquer integrante explique, sem depender de buzzwords, o fluxo completo, os trade-offs e os limites atuais do Lumen.

**Mensagem de abertura (30 segundos):** Lumen monitora tentativas de pagamento sintéticas e responde à pergunta operacional: *há uma queda material de conversão, em qual população, desde quando e qual investigação humana deve vir primeiro?* O operador fornece fatos de transações; o sistema persiste, processa, calcula métricas e baseline, detecta anomalias, forma um Incident com evidências e, só depois, acrescenta memória ou uma sugestão humana. Não processamos pagamentos reais, PII, nem executamos ações financeiras.

> Fonte de verdade arquitetural: [system-plan.md](plans/system-plan.md). Histórico completo: [flight-log.md](flight-log.md). Este briefing descreve o estado de 2026-08-30 e não transforma evidência histórica em aceite atual.

## O sistema em uma explicação

```text
1..100 TransactionInputs sintéticos
  → batch persistido antes do 202
  → worker com lifecycle durável
  → outcome/evento canônico e classificação factual
  → agregação por janela + baseline anterior
  → detector estatístico + RCA determinístico
  → Incident persistido, impacto e evidências
  → memória de precedentes e sugestão opcional HUMAN_ONLY
```

- **Web (Next.js):** coleta fatos e mostra o que a API devolveu; não calcula taxa, causa, progresso ou confiança.
- **API/worker (FastAPI + DuckDB/Parquet):** é a autoridade de lifecycle, persistência, métricas, detecção, correlação e Incident.
- **Memória (Neo4j, opcional):** oferece contexto histórico confirmado; não resolve transação, não decide RCA e não bloqueia ingestão.
- **Agente/OpenAI (opcional):** trabalha depois do Incident persistido e só publica hipótese separada, com evidências; nunca muda a causa ou executa pagamento.

## As quatro decisões que mudaram o fluxo

### 1. `FL-20260829-TEAM-015` — entrada pública transaction-first

**Decisão:** o operador envia de 1 a 100 fatos de transação, ou gera samples revisáveis; não informa queda de approval, latência, causa, outcome ou efeitos de cenário.

**Por que fez diferença:** essa escolha muda o produto de um painel onde se "desenha" o incidente para um sistema que o descobre. Ela estabelece a cadeia demonstrável `input → persistência → processamento → métricas → diagnóstico`, impede que o frontend antecipe a resposta e torna a seed/harness um mecanismo de ensaio interno, não uma manipulação pública do resultado.

**Trade-off assumido:** um lote pequeno pode não produzir Incident. Isso é correto: a UI deve mostrar ausência de evidência ou `INCONCLUSIVE`, não forçar uma história para a demo.

**Prova que mostrar:** gerar/revisar/submeter um batch, acompanhar `PROCESSING` até o estado terminal e abrir o Log/Detail devolvido pela API.

**Frase para a banca:** “Nós tiramos a causa e a métrica da mão do usuário porque elas são exatamente aquilo que o produto precisa medir e explicar.”

### 2. `FL-20260830-TEAM-024` — lifecycle terminal atômico e correlação isolada

**Decisão:** o worker executa `canonical → analytics → Incident → link → record terminal` em uma transação DuckDB, isolada por `correlation_id`; falhas fazem rollback antes de registrar `UNKNOWN/PIPELINE_FAILED`.

**Por que fez diferença:** sem isso, a transação que dispara a anomalia poderia terminar sem link para o Incident, ou um erro poderia deixar fatos, links e estados divergentes. A atomicidade torna o detalhe auditável: o operador vê o resultado persistido e o vínculo causal correspondente, em vez de um progresso visual inventado pela UI.

**Trade-off assumido:** o MVP usa DuckDB, um worker in-process e uma réplica; o lock cobre mais trabalho e não é arquitetura para escala horizontal. É uma escolha consciente para a fatia demonstrável, com migração futura para fila/banco transacional caso o volume exija.

**Prova que mostrar:** `202` somente após persistência inicial, polling apenas enquanto há `PROCESSING`, e um terminal completo com outcome/classificação; explicar que um `UNKNOWN` é falha de pipeline, não uma recusa de pagamento.

**Frase para a banca:** “Preferimos consistência auditável num único fluxo a aparentar concorrência sem conseguir provar que o Incident pertence à transação certa.”

### 3. `FL-20260830-TEAM-025` — seis dimensões sem usar decline code como atalho causal

**Decisão:** merchant, provider, método, país e banco emissor formam rollups esparsos antes do resultado; o `normalized_decline_code` é um perfil de evidência do slice já anômalo. O RCA só afirma uma causa quando as evidências qualificadas sustentam a hipótese; do contrário retorna `INCONCLUSIVE`.

**Por que fez diferença:** o desafio pede granularidade real. Agrupar só por provider/país perderia o problema de um merchant ou emissor específico; colocar decline code como chave causal criaria circularidade, pois ele é observado depois da falha. A decisão faz o sistema diferenciar *sinal*, *evidência* e *causa*.

**Trade-off assumido:** slices raros ou ambíguos não recebem uma causa “bonita”. A perda de cobertura é deliberada para não aumentar confiança artificialmente.

**Prova que mostrar:** um Incident com escopo, baseline, métricas, evidências e alternativas; em um caso pouco sustentado, mostrar `INCONCLUSIVE` como resposta válida. Se houver dois problemas com fingerprints distintos, explicar que a correlação exige fingerprint completo, correlação e janela compatíveis.

**Frase para a banca:** “O código de recusa ajuda a explicar a assinatura do problema; ele não pode ser usado como prova circular da causa que estamos tentando descobrir.”

### 4. `FL-20260830-TEAM-029` — agente determinístico, grounded e estritamente humano

**Decisão:** o agente recebe um `EvidencePack` imutável depois do Incident; o padrão é template determinístico/offline. A hipótese é um contrato aditivo, exige ao menos duas fontes atuais de evidência e só pode sugerir categorias já produzidas pelo RCA. OpenAI, quando configurada, é opcional e pós-persistência.

**Por que fez diferença:** a parte “agente” melhora a investigação sem virar uma autoridade opaca. Uma falha do provedor de IA não desfaz o Incident, uma memória histórica não reescreve a causa atual e nenhuma sugestão pode retry, reroute, capture, refund ou alterar pagamento.

**Trade-off assumido:** a demo padrão é menos vistosa que uma narrativa livre de LLM e o caminho OpenAI no deploy precisa de prova própria. Em troca, o fluxo crítico é reproduzível e permanece seguro offline.

**Prova que mostrar:** separar visualmente causa do motor, memória histórica e hipótese do agente; mostrar estados `SUGGESTED`, `INSUFFICIENT_EVIDENCE` ou `UNAVAILABLE` sem perder o Incident já persistido.

**Frase para a banca:** “A IA explica e prioriza investigação; ela não cria a verdade operacional nem toma uma ação financeira.”

## Perguntas prováveis e respostas curtas

| Pergunta da banca | Resposta que devemos dar | Evidência / limite honesto |
| --- | --- | --- |
| Qual problema vocês resolvem? | Não é contar falhas isoladas: é identificar uma degradação material de conversão, seu recorte, início, impacto e a próxima investigação humana. | Fluxo e critérios do desafio em [README-submit.md](../README-submit.md). |
| Por que o usuário não configura a queda ou a causa? | Porque isso tornaria a demo uma simulação dirigida. Ele envia fatos; taxa, baseline, outcome e diagnóstico são outputs derivados. | `FL-...-015`; samples são revisáveis antes do submit. |
| Por que responder `202` e não esperar tudo? | O batch já está durável, mas processamento, agregação e diagnóstico são assíncronos. O log mostra lifecycle real e o browser só faz polling enquanto existe `PROCESSING`. | A UI não inventa percentual ou relógio. |
| O que impede dados parciais? | O worker usa transação única para o terminal e o vínculo do Incident; em falha, reverte e registra estado técnico explícito. | Uma réplica/lock é limitação assumida do MVP. |
| Como evitam falso positivo? | Observamos janelas fechadas, usamos baseline estritamente anterior e exigimos suporte mínimo; baixa amostra ou ambiguidade resulta em ausência de candidato ou `INCONCLUSIVE`. | A conversão usa pagamentos únicos; não confundir com approval por tentativa. |
| Como encontram a causa sem circularidade? | O RCA explora dimensões pré-resultado e usa o decline code como evidência posterior. A causa só é `SUPPORTED` quando o motor a sustenta. | `FL-...-025`; precedente e LLM não promovem causa. |
| E dois incidentes simultâneos? | Eles só compartilham episódio quando correlação, janela compatível e fingerprint completo do slice coincidem. | Há um defeito aberto de deduplicação entre métricas quando as janelas não se sobrepõem; não devemos alegar esse caso como plenamente aceito. |
| Por que DuckDB e não Kafka/Postgres? | Para o MVP, DuckDB/Parquet e um worker tornam a fatia completa reproduzível e auditável com menos infraestrutura. A fronteira é conhecida: uma réplica, sem escala horizontal. | Volume/restart em Railway ainda requer verificação atual. |
| Qual é o papel do Neo4j? | Memória de Incidents confirmados e réplica opcional de refusal codes. A autoridade para lookup e RCA continua no catálogo/DuckDB. | Falha de Neo4j não bloqueia ingestão. |
| Vocês usam OpenAI para detectar fraude ou agir? | Não. O agente recebe fatos já persistidos, gera hipótese separada e `HUMAN_ONLY`; não tem ferramenta nem permissão financeira. | Sem chave, há template determinístico; caminho OpenAI no deploy é `NOT RUN` nesta revisão. |
| Dados reais de cartão entram no sistema? | Não. O escopo é sintético/tokenizado; PAN, CVV e PII são proibidos. Dados reais exigiriam novo desenho de segurança, isolamento e retenção. | Não apresentar o MVP como pronto para processamento real. |
| O que não está validado hoje? | A suíte Python tem 245 passes e 2 falhas reproduzíveis: duplicação multi-métrica de Incident e seed sensível a opcionais omitidos versus `null`. Deploy público/Volume/restart/CORS e browser Vercel também não foram verificados nesta revisão. | Isso é dívida aberta, não um resultado escondido. |
| O que fariam a seguir? | Primeiro: normalizar opcionais antes da seed e reconciliar candidatos multi-métrica; depois executar os testes afetados e smoke real Railway/Vercel. Só então ampliar escala, fontes externas ou IA. | Corrigir antes de prometer novas features. |

## Divisão de respostas no time

| Pessoa | É a referência para | Resposta que deve conseguir assumir |
| --- | --- | --- |
| André | experiência web e contrato API → UI | A UI é consumidora live: coleta fatos, mostra lifecycle real, estados vazios/erro e não calcula diagnóstico. |
| Rogério | API, persistência, worker, integração e deploy | Por que `202`, atomicidade, idempotência, DuckDB/Volume e quais evidências de deploy ainda faltam. |
| Renato | dados sintéticos, outcome, detector e RCA | Como o baseline/detector usam eventos derivados, por que há `INCONCLUSIVE` e por que o resultado sintético precisa ser determinístico. |
| Altoé | memória, explicação e agente | Por que precedente não é causa, Neo4j é opcional, e a sugestão é grounded e `HUMAN_ONLY`. |

Todos devem conseguir responder as quatro decisões acima e repetir os limites abertos. Se uma pergunta sair da especialidade, a passagem correta é: “A arquitetura define a fronteira assim; vou passar para quem é owner do detalhe, sem extrapolar a evidência.”

## Roteiro de demonstração e trial by fire

1. Explicar em uma frase o problema e submeter/gerar um batch sintético revisável.
2. Mostrar `202`, lifecycle real no Log e o detalhe de uma transação; não prometer Incident para lote sem volume.
3. Mostrar um Incident sustentado: métrica observada versus baseline, recorte causal, evidências, impacto na mesma moeda e recomendação humana.
4. Mostrar explicitamente uma limitação: `INCONCLUSIVE`, ausência de precedente ou `UNAVAILABLE` do agente preserva o fluxo, não é mascarado.
5. Se a banca provocar simultaneidade, baixa amostra, memória indisponível ou falha de IA, apontar o fallback tipado. Não acionar os dois fluxos de backend com defeito aberto como prova de aceite.

## Estado de prontidão para a defesa

| Lente | Estado | O que sustenta a resposta |
| --- | --- | --- |
| Funciona ponta a ponta | `PARTIAL` | Caminho live e UI foram implementados, mas dois defeitos backend e verificações públicas de deploy continuam abertos. |
| Profundidade e julgamento | `READY` | As quatro decisões têm alternativas, trade-offs e fronteiras de autoridade explícitas. |
| Problema real | `READY` | O fluxo mede conversão, localização causal, impacto e investigação humana, em vez de uma falha isolada. |
| Originalidade | `PARTIAL` | A diferenciação é o encadeamento auditável e a separação entre fato, RCA, memória e IA; não alegar benchmark de superioridade não executado. |
| Experiência e clareza | `READY` | README, plano, diagramas, contratos e este roteiro permitem explicar o sistema sem contexto privado. |

**Status honesto:** o briefing está pronto para ensaio e defesa técnica; a aceitação final do backend permanece `CHANGES REQUIRED` até os dois defeitos conhecidos serem corrigidos e comprovados.
