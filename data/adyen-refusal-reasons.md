# Motivos de recusa (Adyen)

Base de pesquisa para respostas de autorização recusadas. Fonte: [Adyen — Refusal reasons](https://docs.adyen.com/development-resources/refusal-reasons/), consultada em 30/08/2026.

> **Uso seguro:** não exponha `refusalReason` ou detalhes da recusa ao shopper. Use-os internamente para diagnóstico, UX genérica e lógica de retentativa.

## Campos da resposta

Uma chamada pode retornar HTTP `200 OK` e ainda assim ter a autorização recusada. Nessa situação, use estes campos em conjunto:

| Campo | Função |
|---|---|
| `resultCode` | Categoria do resultado: `Refused`, `Error` ou `Cancelled`. |
| `refusalReason` | Explicação curta da recusa. |
| `refusalReasonCode` | Código numérico correspondente ao motivo. |

## Tabela de referência

| Código | `refusalReason` | Significado / ação sugerida |
|---:|---|---|
| 0 | (none) | Pode vir com `Authorised`; ignore o código, pois a transação foi bem-sucedida. |
| 2 | Refused | Transação recusada, sem detalhe específico. |
| 3 | Referral | Encaminhamento/referência ao emissor. |
| 4 | Acquirer Error | Erro no adquirente; a transação não foi concluída. |
| 5 | Blocked Card | Cartão bloqueado e inutilizável. |
| 6 | Expired Card | Cartão expirado. |
| 7 | Invalid Amount | Divergência ou valor inválido na transação. |
| 8 | Invalid Card Number | Número do cartão incorreto ou inválido. |
| 9 | Issuer Unavailable | Não foi possível contatar o banco emissor. |
| 10 | Not supported | Banco não suporta ou não permite este tipo de transação. |
| 11 | 3D Not Authenticated | 3D Secure não foi executado ou falhou. |
| 12 | Not enough balance | Saldo insuficiente para cobrir o pagamento. |
| 14 | Acquirer Fraud | Possível fraude identificada pelo adquirente. |
| 15 | Cancelled | Transação cancelada. |
| 16 | Shopper Cancelled | Shopper cancelou antes de concluir. |
| 17 | Invalid Pin | PIN incorreto ou inválido. |
| 18 | Pin tries exceeded | PIN incorreto informado mais de três vezes seguidas. |
| 19 | Pin validation not possible | Não foi possível validar o PIN. |
| 20 | FRAUD | Checagens de risco antes da autorização atingiram score de fraude >= 100. |
| 21 | Not Submitted | Transação não foi submetida corretamente para processamento. |
| 22 | FRAUD-CANCELLED | Checagens de risco antes e depois da autorização atingiram score de fraude >= 100. |
| 23 | Transaction Not Permitted | Operação não permitida para emissor/cartão, estabelecimento ou adquirente/terminal. |
| 24 | CVC Declined | CVC informado e inválido. |
| 25 | Restricted Card | Cartão restrito; inclui cartão inválido naquele país. |
| 26 | Revocation Of Auth | Shopper pediu a interrupção de cobranças recorrentes/assinatura. |
| 27 | Declined Non Generic | Recusa que não pode ser mapeada com confiança; distingue recusa genérica de uma específica. |
| 28 | Withdrawal amount exceeded | Valor excede o limite de saque permitido para o cartão. |
| 29 | Withdrawal count exceeded | Quantidade de saques excedeu o limite permitido. |
| 31 | Issuer Suspected Fraud | Emissor reportou suspeita de fraude. |
| 32 | AVS Declined | Dados de endereço fornecidos pelo shopper estão incorretos. |
| 33 | Card requires online pin | Banco exige que o shopper informe o PIN. |
| 34 | No checking account available on Card | Banco exige conta corrente vinculada para concluir a compra. |
| 35 | No savings account available on Card | Banco exige conta poupança vinculada para concluir a compra. |
| 36 | Mobile pin required | Banco exige um PIN mobile. |
| 37 | Contactless fallback | Shopper abandonou após o pagamento por aproximação pedir outro método de entrada (PIN ou tarja). |
| 38 | Authentication required | Emissor recusou a isenção de autenticação; repetir com 3D Secure. |
| 39 | RReq not received from DS | Emissor ou bandeira não comunicou o resultado via RReq. |
| 40 | Current AID is in Penalty Box | Rede de pagamento indisponível; repetir com outro meio de pagamento. |
| 41 | CVM Required Restart Payment | PIN ou assinatura exigidos; reiniciar a transação. |
| 42 | 3DS Authentication Error | Falha de 3DS na bandeira ou emissor; tentar novamente ou com outro meio. |
| 46 | Transaction blocked by Adyen to prevent excessive retry fees | Serviço da Adyen bloqueou a transação para evitar taxas de retentativas excessivas. |
| 50 | Token Revoked | Shopper desabilitou o token concedido ao estabelecimento para cobranças recorrentes. |

## Observações de implementação

- A tabela é aplicável a integrações de pagamentos online. Os motivos também são entregues pelo **Standard webhook**, sem assinatura adicional.
- Para testes, a Adyen permite acionar esses cenários pelos respectivos valores de `refusalReasonCode` no ambiente de teste.
- Use `resultCode` para a decisão de alto nível e `refusalReasonCode` para regras específicas, como solicitar 3DS no código `38` ou bloquear retentativas no código `46`.
