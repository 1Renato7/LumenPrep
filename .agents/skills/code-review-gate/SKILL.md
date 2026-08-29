---
name: code-review-gate
description: Revisa o diff de uma tarefa antes da aceitação funcional, priorizando bugs, regressões, segurança, contratos quebrados e testes ausentes. Use quando uma implementação estiver pronta para revisão, antes de declarar conclusão ou enviar para integração; não use como formatter ou revisão puramente estética.
---

# Code Review Gate

Faça revisão orientada a risco, comportamento e evidência. Revisar não autoriza corrigir; implemente correções quando a tarefa incluir isso ou o usuário pedir.

1. **Escopo:** identifique microtarefa, critérios, plano/contratos, branch-base, merge-base, commits, diff e dirty state. Não inclua alterações alheias.
2. **Intenção:** reconstrua comportamento esperado, invariantes e consumidores. Leia código suficiente ao redor, callers, callees, tipos, testes e configurações.
3. **Análise:** use [review-checklist.md](references/review-checklist.md). Rastreie estados e caminhos de erro; não limite revisão às linhas vermelhas/verdes.
4. **Validação:** execute testes focados e checagens existentes quando necessários para confirmar um achado. Diferencie falha nova, preexistente e limitação ambiental.
5. **Achados:** use [finding-format.md](references/finding-format.md). Inclua somente problemas acionáveis com cenário concreto; evite estilo/lint sem impacto.
6. **Cobertura:** informe arquivos/fluxos analisados, testes executados, áreas fora do escopo e risco residual.
7. **Gate:** classifique:
   - `PASS`: nenhum achado bloqueante;
   - `PASS WITH NOTES`: apenas riscos não bloqueantes;
   - `CHANGES REQUIRED`: existe falha que impede aceitação ou integração.

Depois de correções, revise o novo diff, cenário original e testes afetados. Não feche achado só porque a linha mudou. O gate não substitui `$browser-acceptance-gate`, `$integration-contract-guardian` nem a auditoria explícita `$deep-security-audit`.
