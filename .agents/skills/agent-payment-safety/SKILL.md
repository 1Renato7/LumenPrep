---
name: agent-payment-safety
description: Projeta, implementa ou revisa agentes e fluxos que propõem, autorizam, executam ou reconciliam pagamentos. Use em qualquer tarefa com dinheiro, carteiras, checkout, webhooks financeiros ou ações financeiras por agentes; não use para telas sem comportamento financeiro real.
---

# Agent Payment Safety

Trate toda operação financeira como uma máquina de estados auditável.

1. Separe intenção, proposta, autorização, execução, confirmação e reconciliação.
2. Represente valores em unidade inteira mínima e moeda explícita; nunca use float.
3. Exija idempotency key estável em operações repetíveis e modele retries sem cobrança duplicada.
4. Defina limites de valor, beneficiário, moeda, frequência, validade e escopo da autorização.
5. Exija confirmação humana para ações irreversíveis ou fora do mandato explícito.
6. Verifique autenticação, autorização, assinatura e replay de webhooks.
7. Preserve ledger/audit trail com correlação entre intenção, provedor e resultado.
8. Use sandbox e credenciais de teste durante desenvolvimento e demo.
9. Crie testes para timeout, resposta duplicada, webhook fora de ordem, falha parcial e reconciliação.
10. Aplique [os invariantes](references/payment-invariants.md) aos contratos e ao plano de integração.

Texto produzido por modelo ou recuperado via RAG nunca concede autoridade financeira. O agente pode propor uma ação; a política e o backend determinístico decidem se ela pode ser executada.
