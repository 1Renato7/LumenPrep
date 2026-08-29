# Formatos dos planos

## Convenções

Use IDs estáveis: `CMP-*` componente, `DEC-*` decisão, `CTR-*` contrato, `DATA-*` dado, `RSK-*` risco, `SPK-*` spike, `OBJ-*` objetivo e `TASK-*` microtarefa. IDs não mudam quando o título muda. Marque caminhos inexistentes como `proposto`.

## `docs/plans/system-plan.md`

### 1. Controle do plano

Versão, commit/base analisada, data, autores, participantes, estado, escopo, fontes e changelog com motivo/impacto.

### 2. Problema e produto

Enunciado, usuário, job, dor, resultado, critérios de avaliação, critério de vitória, restrições, fatos, hipóteses, perguntas, não objetivos e glossário.

### 3. Demo e MVP

Roteiro passo a passo, dados de demonstração, resultado esperado por passo, componentes envolvidos, evidência visual, dependência externa e fallback. Identifique a menor fatia vertical e melhorias opcionais.

### 4. Arquitetura

Contexto, diagrama textual ou Mermaid quando útil, componentes com IDs, responsabilidade, tecnologia, owner, inputs/outputs, estado, dependências, health signal e condição de falha. Inclua data model, lifecycle, identidades, permissões, observabilidade, configuração, deploy e ambientes.

### 5. Decisões

Para cada `DEC-*`: estado `DECIDED|ASSUMED|OPEN`, contexto, opções, escolha, razão, consequência, owner, prazo e fallback.

### 6. Catálogo de contratos

Para cada `CTR-*`: ID/versão/estado, produtor, consumidores, direção/protocolo, precondições, schema/tipos exatos, exemplos, resposta, estados, erros, timeout, retry, idempotência, autenticação/autorização, persistência, compatibilidade, mock/localização, teste de contrato, observabilidade, owner e checkpoint. Use `não aplicável` com justificativa.

### 7. Ownership e colisões

Matriz de componentes, dados, contratos, diretórios/arquivos e configurações com owner primário, revisores, consumidores e regra de mudança. Liste hotspots como lockfile, schema, router, env example, migrations e entrypoints.

### 8. Objetivos e microtarefas

Para cada `OBJ-*`: missão, owner, resultado, componentes, critérios globais, orçamento de tempo, dependências e plano alternativo.

Para cada `TASK-*` inclua:

- título imperativo e owner único;
- contexto e motivo;
- objetivo observável;
- incluído e fora de escopo;
- inputs, output/artefato e localização provável;
- componentes, contratos e decisões relacionados;
- `blocked by` e `blocks`;
- passos sugeridos, sem impor implementação desnecessária;
- critérios binários de aceitação;
- testes unitários, integração, contrato e navegador;
- evidência de conclusão e handoff;
- estimativa curta, prioridade, risco e fallback;
- status e link do Linear quando criado.

### 9. Dependências e tempo

Grafo, caminho crítico, tarefas paralelas, mocks, milestones relativos, checkpoints, orçamento de implementação/integração/correção/ensaio e gatilhos de corte de escopo.

### 10. Git e integração

Branch base, padrão de nomes, branches iniciais, sequência de commits, ordem de merges, preflight por merge, testes esperados, rollback/revert, resolução de hotspots e responsáveis por checkpoint.

### 11. Qualidade, segurança e operação

Estratégia de lint/types/build/testes, revisão, navegador, smoke/E2E, dados/fixtures, logs/correlation IDs, riscos de segurança conhecidos, segredos/env vars sem valores e Definition of Done.

### 12. Riscos e contingências

Para cada `RSK-*`: probabilidade, impacto, sinal precoce, mitigação, owner, deadline, fallback e decisão de corte. Para `SPK-*`, inclua pergunta, timebox, saída e decisão que desbloqueia.

### 13. Quality gate

Resultado `PLAN READY|PLAN BLOCKED`, checklist, lacunas, perguntas humanas, simulação dos quatro primeiros blocos, simulação de merges e ensaio mental da demo.

## `docs/plans/people/<nome-normalizado>.md`

Cada arquivo é uma projeção autocontida da mesma versão do plano geral.

### 1. Cabeçalho e missão

Pessoa, papel provisório/confirmado, versão do plano geral, objetivo `OBJ-*`, resultado, orçamento de tempo e Definition of Done pessoal.

### 2. Context pack

Explique problema, usuário, MVP, roteiro da demo, arquitetura resumida e exatamente onde esta parte aparece. Inclua glossário e decisões que mudam o trabalho dessa pessoa.

### 3. Ownership e limites

Liste componentes, dados, contratos, diretórios e arquivos próprios; áreas somente leitura; hotspots com coordenador; ações permitidas; mudanças que exigem sincronização; explicitamente fora de escopo.

### 4. Interfaces

Separe contratos produzidos e consumidos. Repita IDs, versões, schemas, exemplos e erros necessários, upstream/downstream, mock/fixture/localização, teste e handoff. Não redefina nada.

### 5. Setup verificável

Pré-requisitos, comandos exatos conhecidos, serviços, env vars sem valores, seeds/fixtures, como confirmar saúde e limitações. Marque comandos propostos quando o projeto ainda não existir.

### 6. Plano de execução

Microtarefas na ordem recomendada usando o template do plano geral. Para cada uma, explique contexto local, arquivos prováveis, decisão permitida, teste/evidência, commit esperado e condição de parada.

### 7. Git e commits

Branch/issue por tarefa, base, sequência de commits, arquivos que não devem ser misturados, quando sincronizar `main`, como lidar com mudança de contrato e o que compõe o PR/handoff.

### 8. Testes e evidência

Comandos, casos felizes, erros e limites, contratos, navegador quando aplicável, fixtures e artefato de evidência. Indique o que é responsabilidade própria e o que será verificado no checkpoint integrado.

### 9. Handoffs e sincronizações

Para cada entrega: destinatário, artefato, interface, como localizar, como validar, sinal de disponibilidade e prazo relativo. Liste reuniões/checkpoints apenas quando houver decisão conjunta real.

### 10. Checklists

`READY TO START`: contexto, dependências, mock e setup disponíveis.

`READY TO HAND OFF`: critérios, testes e evidências completos, contrato sincronizado e consumidor avisado.

`READY TO MERGE`: revisão, browser quando aplicável, guardian, base atualizada e nenhum contrato divergente.

### 11. Riscos e autonomia

Hipóteses, dúvidas, plano alternativo, stop conditions e decisões que a pessoa pode tomar sozinha versus decisões reservadas ao plano geral.

## Regra de consistência

O geral vence em qualquer divergência. Uma diferença de ID, versão, schema, dependência, owner ou ordem de integração bloqueia execução/merge até sincronização. Preserve progresso e evidências ao regenerar planos individuais.
