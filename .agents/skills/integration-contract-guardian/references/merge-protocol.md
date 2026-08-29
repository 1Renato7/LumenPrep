# Protocolo de integração e merge

## Preflight

1. Confirme autorização para a ação externa pretendida.
2. Registre branch base, branch fonte, merge-base, commits e dirty state.
3. Atualize visão do remoto sem sobrescrever trabalho local.
4. Leia tarefa, plano individual, contratos, handoffs e critérios.
5. Liste arquivos tocados, hotspots e alterações de configuração/dependência/migration.

## Análise

- compare diff com escopo e contratos;
- mapeie alterações upstream/downstream;
- verifique imports/exports, schemas, APIs, events, env vars e feature flags;
- procure conflito semântico, duplicação, implementação paralela e mudança silenciosa;
- confirme que mocks temporários não permanecem ativos;
- confira compatibilidade e ordem de migrations;
- confirme handoff localizável e documentado.

## Verificação

Execute os comandos oficiais aplicáveis: formatter/lint, types, build, unit, integration, contract e smoke. Para comportamento visível, exija o gate de navegador concluído. Registre comandos, resultado e limitações; não transforme teste não executado em sucesso.

## Parecer antes do merge

- `READY`: contrato e evidências completos;
- `READY WITH WARNINGS`: risco não bloqueante com owner e follow-up;
- `BLOCKED`: contrato divergente, base incompatível, teste crítico falhando, migration insegura, handoff ausente ou evidência insuficiente.

## Execução e pós-merge

Quando autorizado, integre na ordem planejada. Se houver conflito, resolva pela fonte de verdade e pelos owners; não escolha automaticamente um lado em arquivos compartilhados. Após merge, execute build/testes/smoke do checkpoint e confira estado do repositório.

Se a validação pós-merge falhar, pare novos merges, preserve evidências e proponha correção ou revert seguro. Não reescreva histórico remoto compartilhado sem pedido explícito.
