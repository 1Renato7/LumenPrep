---
name: deep-security-audit
description: Executa uma auditoria defensiva profunda de segurança em código, arquitetura, configuração, dependências e fluxos em runtime. Use somente quando o usuário pedir explicitamente uma auditoria, revisão ou verificação de segurança; nunca acione implicitamente por uma tarefa comum de implementação, revisão ou merge.
---

# Deep Security Audit

Avalie segurança com profundidade proporcional ao risco e produza conclusões rastreáveis. Não declare que um sistema está absolutamente seguro; informe escopo, evidências, limitações e risco residual.

## Limites de operação

- Confirme o alvo e permaneça dentro do repositório, ambiente e serviços autorizados pelo usuário.
- Comece de forma read-only. Não corrija achados, altere infraestrutura, faça rotação de segredos ou modifique controles externos sem pedido explícito.
- Prefira testes locais, sandbox e dados sintéticos. Não execute exploração destrutiva, negação de serviço, persistência, evasão, exfiltração ou acesso a dados reais.
- Não imprima valores de segredos. Registre apenas localização, tipo, impacto e instrução de revogação/rotação.
- Não instale scanners ou envie código a serviços externos sem autorização.
- Trate resultados automatizados como sinais que precisam de confirmação manual.

## Fluxo obrigatório

1. **Defina escopo e assurance target.** Registre commit, componentes, ambientes, dados, identidades, integrações, limitações e o que ficou fora da auditoria.
2. **Reconstrua o sistema.** Leia `AGENTS.md`, planos, contratos, manifests, configuração, entrypoints, rotas, schemas, migrations, CI/CD e caminhos de execução relevantes.
3. **Modele ameaças.** Leia [threat-model.md](references/threat-model.md). Mapeie ativos, atores, trust boundaries, data flows, privilégios, abuse cases e controles esperados.
4. **Faça triagem automatizada segura.** Use scanners já disponíveis e apropriados para secrets, dependências, SAST, containers e IaC. Registre comando, versão, cobertura e falhas. Não use um scanner irrelevante apenas para aumentar volume.
5. **Revise manualmente por fluxo.** Rastreie entrada não confiável até ações sensíveis e valide controles em servidor. Cubra o checklist aplicável de [audit-checklist.md](references/audit-checklist.md).
6. **Valide em runtime quando possível.** Em ambiente local ou autorizado, teste autenticação, autorização, isolamento, validação, estados de erro e controles de abuso de modo não destrutivo. Para interfaces, use o navegador e inspecione console/rede sem expor dados.
7. **Confirme achados.** Elimine falso positivo, determine precondições, alcance, impacto, exploitability e confiança. Uma suspeita sem evidência deve permanecer hipótese.
8. **Produza relatório.** Use [finding-format.md](references/finding-format.md) em `docs/security/security-audit.md`. Inclua threat model, achados, pontos positivos, lacunas, risco residual e plano de remediação ordenado.
9. **Reteste quando solicitado ou após correções.** Verifique o cenário original, testes de regressão e efeitos colaterais. Não feche achado somente porque o código mudou.

## Profundidade adaptativa

Priorize caminhos de maior consequência: identidade, autorização, dados sensíveis, pagamentos, ferramentas de agentes, RAG, webhooks, uploads, execução de comandos, administração, multi-tenant e supply chain. Leia referências especializadas do projeto e acione skills de domínio somente quando realmente aplicáveis.

## Resultado

Classifique a auditoria como:

- `SECURITY REVIEWED`: o escopo planejado foi coberto e limitações estão registradas;
- `SECURITY REVIEWED WITH GAPS`: parte relevante não pôde ser validada;
- `SECURITY BLOCKED`: falta de acesso, execução ou contexto impede conclusão útil.

Essa classificação descreve a cobertura da auditoria, não certifica ausência de vulnerabilidades.
