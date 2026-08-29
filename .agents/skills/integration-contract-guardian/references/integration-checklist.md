# Checklist de integração

## Planejamento

- Todos os componentes têm ID e owner.
- Toda fronteira tem contrato versionado, produtor, consumidor e checkpoint de integração.
- Schemas, exemplos, precondições, erros, estados, timeout, retry, autenticação e idempotência estão definidos ou justificados como não aplicáveis.
- Cada dependência possui entrega real ou mock/fixture localizado e testável.
- Componentes, dados e hotspots de arquivos têm owner; áreas compartilhadas têm coordenador e protocolo de mudança.
- O grafo não possui ciclo sem estratégia de quebra.
- Cada participante consegue iniciar seu primeiro bloco de trabalho com o contexto documentado.
- Todo passo do fluxo da demo aponta para componentes, contratos, responsáveis e evidências de teste.
- Toda hipótese crítica tem owner, prazo de validação e fallback.
- Não existe decisão crítica marcada como `OPEN` sem ação de resolução antes da implementação dependente.
- Toda decisão material `DECIDED`, especialmente a que congela contrato ou ownership, aponta para uma entrada `FL-*` com alternativas e trade-offs.
- A ordem de integração produz incrementos executáveis nos três checkpoints mínimos.
- A simulação de merges descreve build, testes de contrato, configuração e smoke test esperados em cada etapa.
- Todos os contratos necessários ao trabalho paralelo estão `FROZEN`, com mock e teste disponíveis.
- Alterações incompatíveis possuem versionamento, migração, ordem e fallback.
- O orçamento do evento reserva tempo para os checkpoints e recuperação.

Classifique como `PLAN READY` somente se todos os itens aplicáveis forem atendidos. Caso contrário, use `PLAN BLOCKED` e liste lacunas, impacto, owner da decisão e próxima ação.

## Integração de código

- Branch-base e diff foram identificados.
- Dirty state e alterações não relacionadas foram preservados.
- O contrato implementado corresponde ao ID e à versão registrados.
- Consumidores continuam compatíveis ou foram atualizados.
- Migrations têm ordem, rollback ou estratégia segura para o evento.
- Novas env vars estão documentadas sem valores secretos.
- Build, tipos e testes de contrato relevantes passaram.
- Não há código temporário, mock ou feature flag ativado por engano.
- O handoff prometido existe, está localizável e pode ser validado pelo consumidor.
- O fluxo integrado possui smoke test executado, ou limitação explicitamente bloqueante.
- O resultado pós-merge foi definido antes da ação e inclui estratégia de recuperação.
- O plano geral, planos individuais e Linear não divergem sobre tarefa, owner ou dependências.
- O Flight Log não perdeu entradas, não possui IDs duplicados e preserva decisões substituídas.
- Toda mudança material de contrato, resolução de conflito semântico ou warning aceito possui entrada `FL-*` e backlinks para os artefatos afetados.
- Conflitos em `docs/flight-log.md` foram resolvidos preservando ambas as entradas, sem aceitar o arquivo inteiro de apenas um lado.

## Classificação

- `READY`: sem bloqueios; evidências suficientes.
- `READY WITH WARNINGS`: integra, mas há risco não bloqueante claramente registrado.
- `BLOCKED`: contrato quebrado, consumidor incompatível, migration insegura, teste crítico falhando, evidência essencial ausente, decisão contratual material sem `FL-*` ou perda/duplicação não resolvida no Flight Log.

Sempre informe evidências executadas, achados, consumidores impactados e próxima ação.
