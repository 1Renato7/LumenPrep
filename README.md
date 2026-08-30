# LumenPrep

Este repositório contém o sistema de trabalho do time para planejar, dividir, implementar, revisar e integrar o projeto do hackathon com Codex.

## Comece aqui

1. Abra o repositório como projeto no Codex.
2. Inicie uma nova tarefa para garantir que [AGENTS.md](AGENTS.md) seja carregado.
3. Durante a descoberta, forneça o enunciado, as ideias, as restrições, a stack e as habilidades dos quatro participantes.
4. Peça o plano geral. O Codex usará as skills de planejamento e integração antes de gerar os planos individuais.
5. Aprove o plano antes de criar as microtarefas no Linear.

As skills do projeto ficam em [`.agents/skills`](.agents/skills). Consulte [o guia completo das skills](docs/SKILLS.md) para saber quando cada uma é executada, o que recebe e o que entrega.

As decisões do time ficam no [Flight Log](docs/flight-log.md). Ele é atualizado automaticamente pelo Codex sempre que uma escolha material ou trade-off real acontece e permanece disponível para colaboração e defesa perante a banca.

As skills usam progressive disclosure: cada `SKILL.md` contém o fluxo central e carrega referências profundas somente quando necessárias. Isso mantém o contexto utilizável sem reduzir a precisão dos procedimentos.

## Ambiente Python

O runtime canônico do projeto é **Python 3.14.4**, indicado em `.python-version`, validado em `tests/test_environment.py` e fixado na imagem Docker de deploy. `pyproject.toml` declara a faixa de compatibilidade mínima das dependências; não substitui essa pinagem operacional. Quando o Python install manager não estiver disponível, inicialize o runtime local reproduzível (ignorado pelo Git) com:

```powershell
.\scripts\bootstrap-python.ps1
```

Não versione `.venv/`, `.python-runtime/`, artefatos de build ou caches. Após instalar essa versão, valide a base com:

```powershell
.\.python-runtime\python.exe -m unittest discover -s tests
```

## Fluxo principal

```text
Descoberta
  → registrar decisões e trade-offs no Flight Log durante todo o fluxo
  → plano geral
  → quality gate de integração
  → quatro planos individuais
  → microtarefas no Linear
  → implementação e testes
  → revisão de código
  → validação no navegador
  → validação de integração
  → merge
```

O plano geral em `docs/plans/system-plan.md` é a fonte de verdade arquitetural. Os planos em `docs/plans/people/` são projeções individuais e não podem redefinir contratos. A arquitetura 2.0 é transaction-first: Next.js na Vercel consome somente a API FastAPI no Railway; o runbook está em `docs/plans/deployment-vercel-railway.md`.

Um plano só é distribuído após `PLAN READY`. Os quality gates verificam problema, arquitetura, contratos, decomposição, autonomia individual, consistência entre os cinco planos, simulação de execução paralela, sequência de merges e ensaio da demo.

O planejamento prioriza uma fatia mínima ponta a ponta executável nas primeiras horas e usa o tempo restante para profundidade, casos difíceis e trial by fire. O número de features, integrações ou linhas de código não substitui evidência de funcionamento e julgamento técnico.

## Avaliador automatizado do case

O avaliador usa `OPENAI_API_KEY` somente para escolher probes permitidas e gerar um parecer conversacional. A decisão não é do modelo: verificações determinísticas tentam forçar causa sem evidência, vazamento cross-transaction, promoção de precedente, baixa amostra, ID de evidência falso e registro fora do schema público. Elas também reconstroem uma falha sintética a partir do input persistido e exigem que status, código, classificação, evidência, evento bruto e evento canônico coincidam. Se uma explicação foi inventada, não há evento de origem, o registro viola contrato, ou a mesma entrada muda ao cruzar o contrato público, o veredito não pode ser `PRONTA`.

Neste MVP o provider é sintético; portanto, a fonte autoritativa auditada é o adaptador determinístico do provider mais os eventos persistidos. Ao integrar um provider real, essa fonte deve ser substituída/adicionada pela resposta bruta do provider, sem deixar o LLM preenchê-la.

Com `OPENAI_API_KEY` configurada em `.env`, rode um único comando:

```powershell
& .\.venv\Scripts\python.exe .\scripts\run_case_evaluator.py --focus "verifique se algum erro ou diagnóstico foi inventado"
```

O resultado mostra as operações executadas e um veredito `PRONTA`, `PRONTA COM LIMITAÇÕES` ou `NÃO PRONTA`. Nunca versione a chave. Não é necessário subir a API em outro terminal.

## Regra de segurança

A auditoria profunda de segurança nunca é automática. Para executá-la, peça explicitamente:

```text
Use $deep-security-audit para auditar profundamente a segurança do sistema.
```

Por padrão, a auditoria diagnostica e documenta riscos sem corrigir código ou alterar infraestrutura.
