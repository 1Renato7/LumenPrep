# Formato do relatório e dos achados

## Sumário da auditoria

Registre commit, data, auditor, escopo, ambientes, métodos, ferramentas/versões, limitações e classificação de cobertura. Resuma arquitetura, trust boundaries, ativos críticos, achados por severidade, pontos positivos e risco residual.

## Severidade

- `CRITICAL`: comprometimento amplo ou impacto catastrófico plausível com precondições realistas.
- `HIGH`: impacto grave sobre confidencialidade, integridade, disponibilidade ou autoridade.
- `MEDIUM`: impacto relevante com alcance ou precondições limitantes.
- `LOW`: hardening ou exposição de baixo impacto comprovado.
- `INFO`: observação útil sem vulnerabilidade demonstrada.

Não derive severidade apenas do nome da categoria. Considere ativo, impacto, alcance, precondições, exploitability, controles existentes e confiança.

## Achado

Use um ID estável como `SEC-001` e inclua:

- título e severidade;
- estado e confiança;
- componente, arquivo/linha ou endpoint;
- ativo e trust boundary afetados;
- descrição e causa raiz;
- precondições e cenário de abuso;
- evidência mínima sanitizada;
- impacto técnico e de negócio;
- controles existentes;
- correção recomendada, owner e prioridade;
- teste de regressão e procedimento de reteste;
- referências relevantes;
- risco aceito ou residual, quando decidido pelo usuário.

Evite publicar payloads destrutivos, segredos ou instruções que aumentem risco sem necessidade defensiva. Um achado só fica `VERIFIED FIXED` após reteste do cenário original.
