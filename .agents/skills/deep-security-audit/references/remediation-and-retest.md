# Remediação e reteste

## Planejamento

Agrupe por causa raiz e blast radius. Priorize contenção de `CRITICAL/HIGH`, depois correção estrutural e hardening. Para cada ação, defina owner, dependências, risco de regressão, rollout/fallback e teste.

Correções em autenticação, autorização, dados, migrations, secrets, pagamentos ou infraestrutura podem exigir change control e autorização externa. Não faça rotação, revogação, deploy ou alteração de permissão apenas porque o relatório recomendou.

## Implementação

Preserve compatibilidade e testes existentes. Adicione regressão que represente o abuso sem payload perigoso. Evite correções cosméticas que escondem sintoma e deixam source-to-sink intacto.

## Reteste

1. use commit/ambiente novo e registre diferença;
2. repita cenário original e confirme que falha de forma segura;
3. execute teste de regressão e fluxos legítimos adjacentes;
4. verifique logs/erros sem vazamento;
5. reavalie bypass alternativo e risco residual;
6. marque `VERIFIED FIXED`, `PARTIALLY FIXED`, `NOT FIXED` ou `ACCEPTED RISK` somente com evidência/decisão.

Risco aceito requer owner, justificativa, prazo/revisão e controle compensatório; o agente não aceita risco em nome do usuário.
