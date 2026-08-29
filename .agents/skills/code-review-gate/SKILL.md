---
name: code-review-gate
description: Revisa o diff de uma tarefa antes da aceitação funcional, priorizando bugs, regressões, segurança, contratos quebrados e testes ausentes. Use quando uma implementação estiver pronta para revisão, antes de declarar conclusão ou enviar para integração; não use como formatter ou revisão puramente estética.
---

# Code Review Gate

Faça uma revisão orientada a risco e evidências.

1. Identifique escopo, critérios da microtarefa, branch-base e diff exato.
2. Leia o plano geral, o plano individual e os contratos relacionados quando existirem.
3. Inspecione chamadas e consumidores suficientes para avaliar comportamento, não apenas linhas alteradas.
4. Procure bugs funcionais, regressões, estados inválidos, concorrência, tratamento de erro, exposição de dados, quebra de contrato e cobertura ausente.
5. Execute ou recomende testes focados quando o achado depender de confirmação.
6. Relate achados por severidade, com arquivo/linha, cenário de falha e correção segura. Não liste preferências sem impacto.
7. Classifique o gate:
   - `PASS`: nenhum achado bloqueante;
   - `PASS WITH NOTES`: apenas riscos não bloqueantes;
   - `CHANGES REQUIRED`: existe falha que impede aceitação ou integração.

Depois de correções, revise o novo diff e os testes afetados. O gate não substitui `$browser-acceptance-gate` nem `$integration-contract-guardian`.
