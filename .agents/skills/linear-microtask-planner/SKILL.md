---
name: linear-microtask-planner
description: Converte planos aprovados em issues detalhadas e sincronizadas no Linear, com responsáveis confirmados, hierarquia, dependências, preview e idempotência. Use ao preparar, criar, reorganizar ou sincronizar trabalho no Linear; não use para inventar arquitetura nem escreva no Linear sem confirmação explícita.
---

# Linear Microtask Planner

Use `docs/plans/system-plan.md` como fonte de verdade e `docs/plans/people/*.md` como contexto derivado. Escreva issues para alguém que não participou da reunião conseguir executar sem perguntar por contexto já conhecido.

## Fases

0. **Conectividade e descoberta:** siga [discovery-and-mapping.md](references/discovery-and-mapping.md). Confirme ferramentas, workspace, equipes, projetos, ciclos, usuários, labels e estados reais. Não invente IDs.
1. **Seleção do plano:** use caminho fornecido; senão procure primeiro o plano canônico e depois fallbacks documentados. Leia o arquivo inteiro e todos os planos individuais referenciados.
2. **Validação:** exija `PLAN READY`, owners explícitos, contratos e dependências. Ambiguidade de ownership ou arquitetura volta ao planner/guardian.
3. **Mapeamento de pessoas:** associe nome/e-mail a usuário real com as regras da referência. Match parcial ou apelido exige confirmação. Nunca atribua por aproximação.
4. **Decomposição:** uma issue por entregável verificável, um assignee, aproximadamente 20–60 minutos para o hackathon. Agrupe passos mecânicos menores que uma hora; divida tarefas que misturam contrato, implementação, validação ou múltiplos resultados.
5. **Descrição:** use exatamente a estrutura de [issue-schema.md](references/issue-schema.md), ajustando apenas se o plano exigir mais campos. Repita contexto e detalhes necessários; não obrigue o executor a caçar decisões em outro arquivo.
6. **Preview:** mostre destino, hierarquia, tabela de issues, contagem/carga por pessoa, caminho crítico, dependências, labels/estado, ambiguidades e perguntas abertas. Ofereça criar, ajustar ou cancelar.
7. **Confirmação:** não faça qualquer escrita antes de um `ok` explícito para o preview atual. Uma confirmação antiga não autoriza um preview materialmente alterado.
8. **Criação/sincronização:** siga [sync-protocol.md](references/sync-protocol.md). Crie containers/parents, depois issues, depois relações e backlinks. Pare em falha parcial e reporte estado exato.
9. **Verificação:** releia tudo que foi criado/alterado; confira quantidade, assignees, hierarquia, projeto/ciclo, estado, labels, relações, descrições e links.
10. **Fechamento:** atualize planos com identificadores/URLs, mostre resumo por pessoa e liste lacunas `⚠️ A definir com o time`.

## Hierarquia

Prefira um projeto existente do hackathon. Dentro dele, use um parent issue por objetivo global e microtarefas como sub-issues. Se o workspace não usar projetos, apresente a opção de um épico geral ou somente parents por objetivo; não crie projeto, épico, labels ou estados novos sem informar e obter confirmação.

## Invariantes

- Título imperativo, específico e sem nome da pessoa.
- Uma issue tem owner único e resultado binariamente verificável.
- Dependências existem como relações reais, não só texto.
- Use labels e estados existentes; derive prioridade do caminho crítico/risco.
- Não invente requisito, prazo, endpoint, arquivo ou decisão.
- Informação insuficiente vira `> ⚠️ A definir com o time: ...` e pode bloquear criação se mudar o resultado.
- Idioma segue as regras do projeto; identificadores de código permanecem em inglês.
- Reexecução atualiza em vez de duplicar e nunca apaga/cancela item sem autorização.
