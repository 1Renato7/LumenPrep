# Procedimento da auditoria

## Scope statement

Registre objetivo, alvo, commit, ambiente, contas/roles de teste, dados permitidos, ações proibidas, janela, dependências externas, acesso disponível e critérios de parada. Alteração de escopo exige confirmação.

## Coverage matrix

| Componente/fluxo | Ativo | Trust boundary | Ameaça | Controle esperado | Método | Evidência | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- |

Estados: `COVERED`, `PARTIAL`, `NOT TESTED`, `NOT APPLICABLE`. Justifique os dois últimos.

## Ordem

1. inventário e arquitetura;
2. secrets/dependências/configuração;
3. identidade/autorização/tenancy;
4. entradas e ações sensíveis por data flow;
5. lógica de negócio e concorrência;
6. agentes/RAG/pagamentos conforme aplicabilidade;
7. runtime não destrutivo;
8. confirmação manual e relatório.

## Ferramentas

Use primeiro ferramentas já presentes e comandos oficiais. Para cada scanner, registre versão, configuração, caminhos incluídos/excluídos, exit code e limitações. Não instale nem envie código externamente sem autorização. Alertas automatizados precisam de inspeção do source-to-sink e contexto do controle.

## Evidência

Prefira arquivo/linha, configuração, teste local sanitizado, resposta/status, trace ou estado observável. Nunca guarde valor de secret, dado real desnecessário ou payload destrutivo. Mantenha hipóteses separadas de achados confirmados.

## Stop conditions

Pare e reporte quando o teste puder atingir produção, terceiros ou dados reais fora do escopo; exigir ação destrutiva; revelar segredo; causar custo/indisponibilidade; ou quando autorização/identidade do alvo estiver ambígua.
