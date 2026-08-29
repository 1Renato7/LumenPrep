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

1. **Defina escopo e assurance target.** Registre commit, componentes, ambientes, dados, identidades, integrações, limitações, autorização e o que ficou fora.
2. **Planeje a cobertura:** siga [audit-procedure.md](references/audit-procedure.md). Crie matriz componente × ameaça × método × evidência; priorize blast radius e trust boundaries.
3. **Reconstrua o sistema.** Leia `AGENTS.md`, planos, contratos, manifests, configuração, entrypoints, rotas, schemas, migrations, CI/CD e caminhos reais.
4. **Modele ameaças.** Leia [threat-model.md](references/threat-model.md). Mapeie ativos, atores, trust boundaries, data flows, privilégios, abuse cases e controles esperados.
5. **Faça triagem automatizada segura.** Use scanners já disponíveis e apropriados para secrets, dependências, SAST, containers e IaC. Registre comando, versão, cobertura e falhas. Não use volume de alertas como profundidade.
6. **Revise manualmente por fluxo.** Rastreie entrada não confiável até ação/dado sensível, valide controle server-side e cubra [audit-checklist.md](references/audit-checklist.md).
7. **Valide em runtime quando possível.** Em local/sandbox autorizado, teste autenticação, autorização, isolamento, validação, erros e abuso de modo não destrutivo. Para interfaces, opere navegador e inspecione console/rede sem expor dados.
8. **Confirme achados.** Reproduza de forma mínima, elimine falso positivo e determine precondições, alcance, impacto, exploitability e confiança. Suspeita sem evidência permanece hipótese.
9. **Produza relatório.** Use [finding-format.md](references/finding-format.md) em `docs/security/security-audit.md`, com coverage matrix, threat model, achados, controles positivos, lacunas, risco residual e plano ordenado.
10. **Remedeie/reteste somente quando autorizado.** Siga [remediation-and-retest.md](references/remediation-and-retest.md); confirme cenário original e regressões, não apenas mudança textual.

## Profundidade adaptativa

Priorize caminhos de maior consequência: identidade, autorização, dados sensíveis, pagamentos, ferramentas de agentes, RAG, webhooks, uploads, execução de comandos, administração, multi-tenant e supply chain. Leia referências especializadas do projeto e acione skills de domínio somente quando realmente aplicáveis.

## Resultado

Classifique a auditoria como:

- `SECURITY REVIEWED`: o escopo planejado foi coberto e limitações estão registradas;
- `SECURITY REVIEWED WITH GAPS`: parte relevante não pôde ser validada;
- `SECURITY BLOCKED`: falta de acesso, execução ou contexto impede conclusão útil.

Essa classificação descreve a cobertura da auditoria, não certifica ausência de vulnerabilidades.
