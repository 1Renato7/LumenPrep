# Guia das skills do LumenPrep

Este documento explica como as skills se combinam. As instruções executáveis permanecem nos respectivos `SKILL.md`; este guia é a visão operacional para os participantes.

## Ativação

Skills automáticas possuem `allow_implicit_invocation: true` e descrições com gatilhos claros. O `AGENTS.md` também define a ordem obrigatória entre elas. A auditoria de segurança é a única skill explicit-only. O `flight-log-recorder` é transversal: pode ser acionado dentro de qualquer outra skill quando surgir uma decisão material.

| Skill | Ativação | Quando usar | Entrega principal |
| --- | --- | --- | --- |
| `flight-log-recorder` | Automática e transversal | Toda decisão material, alternativa rejeitada, risco aceito ou mudança de rota | Entrada fundamentada em `docs/flight-log.md` |
| `hackathon-system-planner` | Automática | Descoberta, arquitetura, MVP, divisão ou replanejamento | Plano geral e quatro planos individuais |
| `integration-contract-guardian` | Automática | Planejamento de fronteiras e antes de integração, merge, rebase ou PR | Mapa de contratos e parecer de prontidão |
| `linear-microtask-planner` | Automática | Decomposição e sincronização de trabalho no Linear | Parent issues, microtarefas e dependências |
| `code-review-gate` | Automática | Depois da implementação, antes de considerar a tarefa pronta | Achados priorizados e gate de revisão |
| `browser-acceptance-gate` | Automática | Depois da revisão, quando há comportamento observável | Matriz de cenários e evidência no navegador |
| `rag-quality-engineer` | Automática | RAG, embeddings, recuperação, grounding ou citações | Arquitetura e protocolo de avaliação RAG |
| `agent-payment-safety` | Automática | Agentes ou sistemas que lidam com dinheiro e pagamentos | Invariantes financeiros e testes de falha |
| `deep-security-audit` | Somente explícita | Auditoria profunda solicitada pelo usuário | Threat model, achados e plano de remediação |

## `flight-log-recorder`

**Serve para:** registrar o raciocínio real do time enquanto as decisões acontecem e preparar uma defesa técnica auditável para a banca.

Ativa automaticamente quando uma escolha muda produto, escopo, arquitetura, contrato, dados, RAG, pagamentos, segurança, UX, qualidade, operação, Git, integração, prazo ou demo; quando uma alternativa plausível é rejeitada; quando um risco é aceito; ou quando evidência obriga mudança de rota. Passos mecânicos e ideias ainda não escolhidas não geram entrada.

Cada entrada usa ID próprio, timestamp, owner, contexto, decisão, critérios, alternativas reais, fatos/testes/hipóteses, trade-offs aceitos, consequências, propagação, trial by fire, fallback e gatilhos de revisão. Decisões revertidas não somem: uma nova entrada substitui a anterior por vínculo explícito.

O único arquivo entregue é `docs/flight-log.md`. Para reduzir conflitos, há lanes de append para Team, André, Altoé, Rogério e Renato; o índice cronológico é consolidado apenas no fechamento. O log histórico não substitui o plano geral nem os contratos atuais.

No modo `FINALIZE`, a skill prepara síntese e prontidão segundo os critérios da banca: profundidade sobre dificuldade, funcionamento sobre promessa e julgamento sobre espetáculo, avaliados pelas lentes de funcionamento, profundidade, problema real, originalidade e experiência/clareza.

Exemplo: `Registre por que cortamos a segunda integração para aprofundar o fluxo ponta a ponta.`

## `hackathon-system-planner`

**Serve para:** transformar a leitura do problema e as ideias dos quatro participantes em uma arquitetura executável.

**Precisa receber:** enunciado, critérios do hackathon, tempo, stack, integrações possíveis, roteiro de demo, ideias do time e habilidades/preferências de André, Altoé, Rogério e Renato.

**Produz:**

- `docs/plans/system-plan.md` como fonte de verdade;
- `docs/plans/people/<participante>.md` para cada pessoa;
- componentes, decisões, ownership, riscos e microtarefas identificados;
- dependências, caminho crítico, branches e checkpoints.

Antes dos planos individuais, chama o guardian. Se houver fronteira ambígua, o plano recebe `PLAN BLOCKED`.

O planner possui protocolos separados para descoberta, formatos e quality gates. Os planos individuais incluem context pack, ownership/limites, contratos produzidos/consumidos, setup verificável, microtarefas completas, Git, testes, handoffs, stop conditions e checklists de início/entrega/merge.

Exemplo: `Planeje o sistema completo a partir deste enunciado e destas quatro propostas.`

## `integration-contract-guardian`

**Serve para:** impedir que partes desenvolvidas em paralelo dependam de interpretações incompatíveis.

No modo de planejamento, define produtor, consumidor, schemas, estados, erros, autenticação, retry, idempotência, mocks, testes e ownership. Também simula o início do trabalho de cada pessoa e a sequência de merges.

No modo de integração, compara o diff real com os contratos planejados, reconstrói dependências upstream/downstream e procura conflitos semânticos que o Git não detecta.

**Resultados:** `PLAN READY`/`PLAN BLOCKED` no planejamento e `READY`/`READY WITH WARNINGS`/`BLOCKED` na integração.

Exemplo: `Analise se esta branch está pronta para integrar com main.`

O guardian também possui modo `CHANGE CONTROL`, obrigatório quando um contrato já distribuído muda. Ele define compatibilidade, versionamento, migração, adapters, ordem, fallback e sincronização de todos os consumidores.

## `linear-microtask-planner`

**Serve para:** converter o plano aprovado em trabalho pequeno, ordenado e rastreável.

Executa descoberta real de teams/projetos/ciclos/usuários/labels/estados, confirma o mapeamento das pessoas, cria um parent issue por objetivo global e child issues de aproximadamente 20–60 minutos. Cada issue recebe contexto, incluído/fora de escopo, passos sugeridos, contratos, dependências reais, critérios, testes, evidência, handoff e Definition of Done.

Preparar uma prévia pode acontecer automaticamente. Criar ou alterar itens no Linear exige pedido ou autorização explícita. A criação ocorre em duas passagens, possui recuperação de falha parcial, backlinks nos planos e sincronização idempotente por `TASK-*`.

Exemplo: `Prepare as microtarefas no Linear para os quatro planos aprovados e mostre a prévia.`

## `code-review-gate`

**Serve para:** encontrar defeitos de implementação antes dos testes finais e do merge.

Prioriza bugs, regressões, estados inválidos, concorrência, tratamento de erros, exposição de dados, quebra de contratos e testes ausentes. Não se concentra em preferências estéticas cobertas por formatter ou lint.

A revisão reconstrói intenção, callers/consumers e estados, registra cobertura/limitações e usa achados `P0–P3` com cenário, evidência, impacto e correção segura.

**Resultados:** `PASS`, `PASS WITH NOTES` ou `CHANGES REQUIRED`.

Exemplo: `Revise o diff desta microtarefa antes de eu integrar.`

## `browser-acceptance-gate`

**Serve para:** provar que o comportamento criado funciona na aplicação real, e não apenas no código.

Executa o fluxo no navegador local, testa interação, loading, vazio, erro, navegação, persistência, desktop/mobile, console e rede. Não substitui testes unitários ou de API.

Cada critério vira cenário reproduzível com precondição, ações, esperado/observado, console, rede e evidência. Casos não executados ficam `NOT RUN`, nunca aprovação implícita.

**Resultados:** `PASS`, `PASS WITH LIMITATIONS` ou `FAIL` com matriz de evidências.

Exemplo: `Valide no navegador local os critérios desta tarefa.`

## `rag-quality-engineer`

**Serve para:** evitar um RAG que funciona apenas na demo ou responde sem evidência.

Define corpus, parsing, chunking, metadados, permissões, baseline de recuperação, citações, fallback e avaliações. Mede recuperação e geração separadamente e trata documentos como dados não confiáveis.

Também cobre lifecycle documental, versionamento de embeddings/índice, deleção, cache, observabilidade, regressão, custos, isolamento cross-tenant e runbook de falha.

Exemplo: `Projete o RAG e um conjunto pequeno de avaliações antes da implementação.`

## `agent-payment-safety`

**Serve para:** manter decisões financeiras determinísticas, auditáveis e resistentes a duplicação ou falhas parciais.

Impõe valores inteiros, moeda explícita, idempotência, autorização no backend, estados, ledger, reconciliação, validação de webhook, sandbox e confirmação humana quando necessária. Texto de modelo ou RAG nunca concede autoridade financeira.

Inclui máquina de estados, distinção entre falha conhecida e resultado desconhecido, provider boundary, transições auditáveis e matriz de testes para concorrência, duplicação, timeout, webhook, partial failure e indisponibilidade.

Exemplo: `Revise o contrato do agente de pagamentos e seus estados de falha.`

## `deep-security-audit`

**Serve para:** executar uma auditoria defensiva profunda do sistema inteiro ou de um escopo definido.

**Ativação:** nunca automática. Deve ser mencionada explicitamente com `$deep-security-audit` ou solicitada de forma inequívoca como auditoria de segurança.

A auditoria cobre threat modeling, autenticação, autorização, tenants, entradas, injections, XSS, CSRF, SSRF, uploads, dados, secrets, criptografia, APIs, infraestrutura, CI/CD, supply chain, agentes, LLM, RAG, pagamentos, lógica de negócio, logs e resposta a incidentes conforme aplicabilidade.

Por padrão, é read-only e não destrutiva. Produz `docs/security/security-audit.md`, achados `SEC-*`, severidade, evidência sanitizada, correção recomendada e teste de regressão. Não certifica que o sistema está absolutamente seguro.

A auditoria cria uma coverage matrix, define stop conditions, separa scanner de confirmação manual e só marca `VERIFIED FIXED` após repetir o cenário original e validar regressões.

Exemplo: `Use $deep-security-audit para auditar o commit atual antes da apresentação.`

## Sequências recomendadas

### Planejamento inicial

```text
hackathon-system-planner
  → flight-log-recorder (a cada DEC-* e trade-off)
  → integration-contract-guardian (planejamento)
  → planos individuais
  → linear-microtask-planner
```

### Conclusão de uma microtarefa

```text
implementação
  → flight-log-recorder (quando houver decisão material)
  → testes automatizados
  → code-review-gate
  → correções
  → browser-acceptance-gate, quando aplicável
  → integration-contract-guardian, quando pronta para integrar
```

### Auditoria solicitada

```text
pedido explícito
  → deep-security-audit
  → relatório de achados
  → autorização separada para correções
  → reteste dos achados corrigidos
```

## Boas práticas para a equipe

- Comece uma nova tarefa do Codex depois de atualizar skills ou `AGENTS.md`.
- Informe o ID da microtarefa do plano e do Linear ao pedir implementação.
- Não altere contrato apenas no plano individual ou no código.
- Integre contratos, tipos e mocks cedo.
- Não deixe revisão, navegador ou integração para os minutos finais.
- Não deixe o Flight Log para o final: registre a escolha antes que contexto, incerteza e alternativas se percam.
- Quando uma skill retornar bloqueio, resolva a causa; não contorne o gate removendo contexto.

## Referências profundas

| Skill | Referências principais |
| --- | --- |
| Flight Log | detecção, schema de entrada, colaboração/Git, fechamento para a banca |
| Planner | descoberta, formatos do plano, quality gates |
| Guardian | catálogo de contratos, checklist, protocolo de merge |
| Linear | descoberta/mapeamento, schema de issue, sincronização/idempotência |
| Review | checklist comportamental, formato de achados |
| Browser | protocolo de execução, matriz de aceitação |
| RAG | arquitetura, avaliação, operação/segurança |
| Payments | invariantes, lifecycle, matriz de falhas |
| Security | threat model, checklist, procedimento, achados, remediação/reteste |
