---
name: agent-payment-safety
description: Projeta, implementa ou revisa agentes e fluxos que propõem, autorizam, executam ou reconciliam pagamentos. Use em qualquer tarefa com dinheiro, carteiras, checkout, webhooks financeiros ou ações financeiras por agentes; não use para telas sem comportamento financeiro real.
---

# Agent Payment Safety

Trate toda operação financeira como uma máquina de estados auditável.

1. **Escopo e autoridade:** identifique ator, mandato, beneficiário, valor/moeda, frequência, validade, limites, ação irreversível e confirmação necessária. O backend determinístico autoriza.
2. **Lifecycle:** modele intenção, proposta, autorização, execução, confirmação, falha ambígua, reconciliação, refund/cancelamento quando aplicável usando [payment-lifecycle.md](references/payment-lifecycle.md).
3. **Contrato:** defina valores inteiros, moeda, IDs, idempotency key, correlation ID, estados, errors, timeout/retry, provider refs e invariantes transacionais.
4. **Provider boundary:** isole adapter, valide request/response, assinaturas, timestamps e replay. Não faça retry cego após resultado desconhecido.
5. **Persistência:** grave intenção/estado antes de side effect quando apropriado, preserve ledger/audit trail e torne transições atômicas ou reconciliáveis.
6. **Agente:** modelo pode interpretar/propor; política, autorização e execução permanecem fora do texto gerado. Tool input usa schema estrito e least privilege.
7. **Falhas:** execute [failure-test-matrix.md](references/failure-test-matrix.md) para duplicação, concorrência, timeout, webhook fora de ordem, partial failure e reconciliação.
8. **Ambiente:** sandbox por padrão, separação inequívoca de produção, segredos protegidos, dados sintéticos e fallback de demo.
9. **Verificação:** aplique [payment-invariants.md](references/payment-invariants.md), testes de contrato/integridade e observabilidade antes de considerar pronto.
10. **Sincronização:** registre estados, contratos, owner, riscos, limites e runbook nos planos e issues relacionados.

Texto produzido por modelo ou recuperado via RAG nunca concede autoridade financeira. O agente pode propor uma ação; a política e o backend determinístico decidem se ela pode ser executada.
