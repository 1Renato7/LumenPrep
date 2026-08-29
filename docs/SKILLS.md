# Guia das skills do LumenPrep

Este documento explica como as skills se combinam. As instruções executáveis permanecem nos respectivos `SKILL.md`; este guia é a visão operacional para os participantes.

## Ativação

Skills automáticas possuem `allow_implicit_invocation: true` e descrições com gatilhos claros. O `AGENTS.md` também define a ordem obrigatória entre elas. A auditoria de segurança é a única skill explicit-only.

| Skill | Ativação | Quando usar | Entrega principal |
| --- | --- | --- | --- |
| `hackathon-system-planner` | Automática | Descoberta, arquitetura, MVP, divisão ou replanejamento | Plano geral e quatro planos individuais |
| `integration-contract-guardian` | Automática | Planejamento de fronteiras e antes de integração, merge, rebase ou PR | Mapa de contratos e parecer de prontidão |
| `linear-microtask-planner` | Automática | Decomposição e sincronização de trabalho no Linear | Parent issues, microtarefas e dependências |
| `code-review-gate` | Automática | Depois da implementação, antes de considerar a tarefa pronta | Achados priorizados e gate de revisão |
| `browser-acceptance-gate` | Automática | Depois da revisão, quando há comportamento observável | Matriz de cenários e evidência no navegador |
| `rag-quality-engineer` | Automática | RAG, embeddings, recuperação, grounding ou citações | Arquitetura e protocolo de avaliação RAG |
| `agent-payment-safety` | Automática | Agentes ou sistemas que lidam com dinheiro e pagamentos | Invariantes financeiros e testes de falha |
| `deep-security-audit` | Somente explícita | Auditoria profunda solicitada pelo usuário | Threat model, achados e plano de remediação |

## `hackathon-system-planner`

**Serve para:** transformar a leitura do problema e as ideias dos quatro participantes em uma arquitetura executável.

**Precisa receber:** enunciado, critérios do hackathon, tempo, stack, integrações possíveis, roteiro de demo, ideias do time e habilidades/preferências de André, Altoé, Rogério e Renato.

**Produz:**

- `docs/plans/system-plan.md` como fonte de verdade;
- `docs/plans/people/<participante>.md` para cada pessoa;
- componentes, decisões, ownership, riscos e microtarefas identificados;
- dependências, caminho crítico, branches e checkpoints.

Antes dos planos individuais, chama o guardian. Se houver fronteira ambígua, o plano recebe `PLAN BLOCKED`.

Exemplo: `Planeje o sistema completo a partir deste enunciado e destas quatro propostas.`

## `integration-contract-guardian`

**Serve para:** impedir que partes desenvolvidas em paralelo dependam de interpretações incompatíveis.

No modo de planejamento, define produtor, consumidor, schemas, estados, erros, autenticação, retry, idempotência, mocks, testes e ownership. Também simula o início do trabalho de cada pessoa e a sequência de merges.

No modo de integração, compara o diff real com os contratos planejados, reconstrói dependências upstream/downstream e procura conflitos semânticos que o Git não detecta.

**Resultados:** `PLAN READY`/`PLAN BLOCKED` no planejamento e `READY`/`READY WITH WARNINGS`/`BLOCKED` na integração.

Exemplo: `Analise se esta branch está pronta para integrar com main.`

## `linear-microtask-planner`

**Serve para:** converter o plano aprovado em trabalho pequeno, ordenado e rastreável.

Cria um parent issue por objetivo global e child issues de aproximadamente 20–60 minutos, cada uma com responsável, dependências reais, critérios, testes, evidência e IDs dos contratos envolvidos.

Preparar uma prévia pode acontecer automaticamente. Criar ou alterar itens no Linear exige pedido ou autorização explícita.

Exemplo: `Prepare as microtarefas no Linear para os quatro planos aprovados e mostre a prévia.`

## `code-review-gate`

**Serve para:** encontrar defeitos de implementação antes dos testes finais e do merge.

Prioriza bugs, regressões, estados inválidos, concorrência, tratamento de erros, exposição de dados, quebra de contratos e testes ausentes. Não se concentra em preferências estéticas cobertas por formatter ou lint.

**Resultados:** `PASS`, `PASS WITH NOTES` ou `CHANGES REQUIRED`.

Exemplo: `Revise o diff desta microtarefa antes de eu integrar.`

## `browser-acceptance-gate`

**Serve para:** provar que o comportamento criado funciona na aplicação real, e não apenas no código.

Executa o fluxo no navegador local, testa interação, loading, vazio, erro, navegação, persistência, desktop/mobile, console e rede. Não substitui testes unitários ou de API.

**Resultados:** `PASS`, `PASS WITH LIMITATIONS` ou `FAIL` com matriz de evidências.

Exemplo: `Valide no navegador local os critérios desta tarefa.`

## `rag-quality-engineer`

**Serve para:** evitar um RAG que funciona apenas na demo ou responde sem evidência.

Define corpus, parsing, chunking, metadados, permissões, baseline de recuperação, citações, fallback e avaliações. Mede recuperação e geração separadamente e trata documentos como dados não confiáveis.

Exemplo: `Projete o RAG e um conjunto pequeno de avaliações antes da implementação.`

## `agent-payment-safety`

**Serve para:** manter decisões financeiras determinísticas, auditáveis e resistentes a duplicação ou falhas parciais.

Impõe valores inteiros, moeda explícita, idempotência, autorização no backend, estados, ledger, reconciliação, validação de webhook, sandbox e confirmação humana quando necessária. Texto de modelo ou RAG nunca concede autoridade financeira.

Exemplo: `Revise o contrato do agente de pagamentos e seus estados de falha.`

## `deep-security-audit`

**Serve para:** executar uma auditoria defensiva profunda do sistema inteiro ou de um escopo definido.

**Ativação:** nunca automática. Deve ser mencionada explicitamente com `$deep-security-audit` ou solicitada de forma inequívoca como auditoria de segurança.

A auditoria cobre threat modeling, autenticação, autorização, tenants, entradas, injections, XSS, CSRF, SSRF, uploads, dados, secrets, criptografia, APIs, infraestrutura, CI/CD, supply chain, agentes, LLM, RAG, pagamentos, lógica de negócio, logs e resposta a incidentes conforme aplicabilidade.

Por padrão, é read-only e não destrutiva. Produz `docs/security/security-audit.md`, achados `SEC-*`, severidade, evidência sanitizada, correção recomendada e teste de regressão. Não certifica que o sistema está absolutamente seguro.

Exemplo: `Use $deep-security-audit para auditar o commit atual antes da apresentação.`

## Sequências recomendadas

### Planejamento inicial

```text
hackathon-system-planner
  → integration-contract-guardian (planejamento)
  → planos individuais
  → linear-microtask-planner
```

### Conclusão de uma microtarefa

```text
implementação
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
- Quando uma skill retornar bloqueio, resolva a causa; não contorne o gate removendo contexto.
