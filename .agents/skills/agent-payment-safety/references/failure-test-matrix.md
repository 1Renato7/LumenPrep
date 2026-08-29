# Matriz de testes de falha financeira

| Cenário | Injeção | Invariante | Resultado esperado | Evidência |
| --- | --- | --- | --- | --- |
| double click | duas requests iguais | um efeito | mesma operação/idempotência | ledger/provider ref |
| concorrência | requests simultâneas | limite/saldo íntegro | uma transição válida | lock/version/test |
| timeout antes da resposta | abort/latência | sem retry cego | `UNKNOWN` + reconciliação | estado/log |
| provider recusou | erro definitivo | sem efeito | `FAILED_KNOWN` | resposta sanitizada |
| webhook duplicado | mesmo event ID | efeito único | segunda entrega no-op | dedupe record |
| webhook fora de ordem | evento antigo após terminal | terminal não regride | evento ignorado/auditado | state history |
| DB falha após provider | partial failure | reconciliável | `UNKNOWN/PENDING` + repair | runbook/test |
| assinatura inválida | payload adulterado | nenhuma transição | rejeição + alerta | status/log |
| agente fora do mandato | valor/beneficiário excedido | policy server-side | bloqueio antes do provider | policy result |
| currency/unidade errada | payload inválido | valor inequívoco | rejeição | validation test |
| retry legítimo | erro seguro | mesma intenção | política/idempotência | IDs correlatos |
| provider indisponível | fault injection | demo recuperável | fallback/estado claro | UI/log |

Acrescente refund, chargeback, split, recurring ou wallet conforme o produto. Execute em sandbox/dados sintéticos e valide banco, ledger, provider mock e estado visível.
