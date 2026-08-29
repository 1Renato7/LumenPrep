# Invariantes de pagamentos

- Valor usa inteiro na unidade mínima e moeda explícita; conversão/arredondamento é centralizado e testado.
- Toda intenção possui ID, idempotency key, correlation ID, ator e mandato.
- Autorização é validada no backend no momento da execução, não inferida do prompt/UI.
- Mesmo pedido repetido ou concorrente produz no máximo um efeito financeiro.
- Estado terminal não regride por webhook atrasado e transição inválida falha fechada.
- Eventos duplicados não duplicam ledger, saldo, notificação ou side effect.
- Falha após possível envio ao provider entra em estado reconciliável, nunca retry cego.
- Ledger é append-only ou mantém histórico auditável; refund/cancelamento são novos eventos.
- Provider reference e estado interno podem ser reconciliados por processo idempotente.
- Webhook valida assinatura, timestamp/replay, event ID e escopo antes de alterar estado.
- Limites de valor, moeda, beneficiário, frequência e validade são políticas determinísticas.
- Segredos e dados financeiros não aparecem em prompts, client bundles, logs ou planos.
- Sandbox e produção têm credenciais, endpoints, indicadores e dados impossíveis de confundir por padrão.
- Toda ação registra ator, política, input sanitizado, transição, horário, resultado e correlação.
- Timeout, rate limit, partial failure e provider outage possuem comportamento e UI explícitos.
- A demo possui mock/fallback determinístico sem fingir que uma transação real ocorreu.

Qualquer violação bloqueia o fluxo afetado até decisão consciente e registrada.
