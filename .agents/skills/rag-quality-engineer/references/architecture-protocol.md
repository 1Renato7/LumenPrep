# Arquitetura RAG

## Corpus e lifecycle

Defina fontes, autoridade, licença/privacidade, owner, frequência, versionamento, deduplicação, atualização e deleção. Preserve lineage do documento original ao chunk e à citação.

## Ingestion e parsing

Registre formatos, parsers, falhas, OCR quando necessário, encoding, tabelas, títulos, listas e anexos. Quarantenar documento com parsing falho é melhor que indexar conteúdo corrompido silenciosamente.

## Chunking e metadados

Escolha limites por estrutura/semântica e avalie overlap, tamanho e perda de contexto. Cada chunk deve carregar source ID, localização, versão, timestamp, owner/tenant, permissions e campos necessários para filtros/citação.

## Indexação

Versione modelo de embedding, dimensão, normalização, índice e configuração. Garanta idempotência, reindexação, remoção e compatibilidade durante troca de versão. Não misture embeddings incompatíveis.

## Retrieval

Comece com baseline. Defina query normalization, filtros de autorização antes/depois conforme backend, top-k, score threshold e comportamento sem resultado. Busca híbrida/reranking requer métrica que mostre ganho.

## Context assembly e geração

Limite orçamento, deduplicate, preserve source boundaries e não misture instruções de documentos com instruções do sistema. Defina formato de citação, no-answer, conflito entre fontes e prioridade por autoridade/freshness.

## Contratos

Documente schemas para documento, chunk, query, resultado, citação, erro e trace de avaliação. Inclua latência, timeout, retry, cache, tenant e correlation ID.
