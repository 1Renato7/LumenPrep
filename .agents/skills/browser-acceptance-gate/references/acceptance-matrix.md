# Matriz de aceitação

## Contexto

Registre tarefa/commit, data, ambiente/URL, viewport, conta/role sanitizada, dados/fixture, servidor/comando e dependências externas.

## Cenários

| ID | Critério | Precondição | Ações exatas | Esperado | Observado | Console | Rede | Evidência | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Estados: `PASS`, `FAIL`, `BLOCKED`, `NOT RUN`. Nunca converta `NOT RUN` em `PASS`.

Cobertura proporcional:

- fluxo principal e resultado final;
- loading, vazio, entrada inválida e falha de dependência;
- retry, ação repetida e prevenção de duplicação;
- navegação, back/forward e refresh/persistência;
- role sem permissão quando aplicável;
- desktop e mobile para interface responsiva;
- foco/teclado, labels e feedback básico;
- ausência de erro inesperado no console;
- status, timing e payload essenciais das requests afetadas.

## Falha

Para cada falha: ID, severidade, primeiro passo divergente, passos mínimos, evidência, request/erro correlato, frequência e suspeita sem apresentá-la como causa confirmada.

## Resultado

Informe critérios cobertos/não cobertos, bugs, limitações, processos deixados ativos e gate `PASS|PASS WITH LIMITATIONS|FAIL`.
