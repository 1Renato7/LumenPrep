# Operação e segurança RAG

- aplique autorização na recuperação e valide isolamento cross-tenant;
- trate documentos, metadata e URLs como entrada não confiável;
- teste prompt injection direta/indireta, poisoning e exfiltração;
- nunca permita que evidência recuperada conceda autoridade para tools/pagamentos;
- sanitize logs e não armazene prompts/contextos sensíveis desnecessariamente;
- implemente deleção/reindexação e propagação de revogação;
- monitore ingest failures, index lag, no-answer, citation failure, latency e custo;
- versionar corpus, prompts, embeddings e configuração para reproduzir resultado;
- defina cache key/tenant/invalidation para evitar vazamento ou staleness;
- estabeleça fallback se vector store/model/provider falhar;
- limite loops, queries, tokens, retries e custo por usuário/execução;
- preserve dataset de avaliação e execute regressão antes de trocar componentes.

Registre runbook curto: como pausar ingestão, invalidar documento, reindexar, trocar provider, diagnosticar resposta e recuperar a demo.
