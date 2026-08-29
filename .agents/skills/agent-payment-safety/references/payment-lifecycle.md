# Lifecycle de pagamento

Defina estados válidos para o domínio/provedor. Exemplo conceitual:

```text
DRAFT → PROPOSED → AUTHORIZED → SUBMITTING
SUBMITTING → PENDING_PROVIDER | SUCCEEDED | FAILED_KNOWN | UNKNOWN
PENDING_PROVIDER | UNKNOWN → SUCCEEDED | FAILED_KNOWN via reconciliação
```

Estados terminais não regridem por evento atrasado. Transições inválidas falham fechadas e deixam evidência.

Para cada transição, registre ator, precondição, autorização, side effect, persistência, idempotency key, provider reference, evento emitido, timeout, retry permitido, compensação e log/audit.

Separe:

- `FAILED_KNOWN`: provider confirmou ausência de efeito; retry pode usar política definida;
- `UNKNOWN`: request pode ter produzido efeito; consulte/reconcilie antes de repetir;
- `PENDING_PROVIDER`: efeito assíncrono aguardando evento/poll;
- `SUCCEEDED`: efeito confirmado e reconciliável.

Webhooks são sinais não ordenados e potencialmente duplicados. Valide assinatura/timestamp, deduplicate por event ID, busque estado autoritativo quando necessário e aplique transição idempotente.

Defina cancelamento/refund como operações próprias, com autorização, idempotência e ledger; não edite o passado para simular reversão.
