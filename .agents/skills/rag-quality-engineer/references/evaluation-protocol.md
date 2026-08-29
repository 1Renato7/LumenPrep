# Protocolo de avaliação RAG

## Dataset

Mantenha casos versionados com ID, pergunta, usuário/tenant, evidência esperada, fontes aceitáveis, resposta esperada ou condição de no-answer e categoria. Cubra perguntas fáceis, ambíguas, compostas, temporais, sem resposta, conflitantes, cross-tenant e adversariais.

Separe conjunto usado para desenvolvimento de um holdout pequeno. Não otimize somente para a demo.

## Retrieval

Meça presença da evidência correta em `k`, posição/rank, precisão dos candidatos, impacto dos filtros, no-result correto e isolamento. Registre query transformada, candidatos, scores e versão do índice de forma sanitizada.

## Geração

Avalie correção, completude, groundedness, fidelidade da citação, resposta a conflito, calibração e recusa/no-answer. Uma resposta plausível sem apoio é falha.

## Sistema

Meça latência por estágio, custo, tokens/contexto, taxa de erro/fallback, freshness, estabilidade e vazamento de permissão. Registre versões de corpus, embedding, retrieval config, prompt e modelo.

## Processo

1. Rode baseline e guarde resultados.
2. Agrupe falhas por parsing, chunking, metadata/filter, retrieval, ranking, assembly ou geração.
3. Faça uma mudança por hipótese quando possível.
4. Rode dataset completo e compare ganhos/regressões/custo.
5. Aceite mudança somente com melhora relevante e nenhuma regressão crítica.

Produza tabela por caso e resumo de métricas, falhas, limitações e decisão. Não esconda exemplos sem resposta ou falhas de permissão atrás de uma média.
