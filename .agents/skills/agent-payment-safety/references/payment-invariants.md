# Invariantes de pagamentos

- Valor usa inteiro + moeda explícita.
- Operação mutável possui idempotency key e correlação ponta a ponta.
- Autorização é validada no backend no momento da execução.
- Estado terminal não regride por webhook atrasado.
- Eventos duplicados não duplicam efeito financeiro.
- Falha após envio ao provedor entra em estado reconciliável, não em retry cego.
- Segredos e dados sensíveis não aparecem em logs, prompts ou planos.
- Sandbox e produção são distinguíveis e impossíveis de misturar por padrão.
- Toda ação registra ator, política aplicada, horário e resultado.
- A demo possui caminho de recuperação caso o provedor externo falhe.
