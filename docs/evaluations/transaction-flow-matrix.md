# Matriz de avaliação transaction-first — TASK-EVAL-001

- **Issue:** `LUM2-56`
- **Execução:** 2026-08-30
- **Modo:** desenvolvimento local, dados sintéticos e contextos determinísticos; não é holdout.
- **Comando:** `python -m pytest -q tests/test_transaction_flow_evaluation.py tests/test_background_traffic.py tests/test_transaction_worker.py tests/test_detection.py tests/test_rca_ranking.py`

| Caso | Seed / contexto | Resultado esperado | Resultado observado |
| --- | --- | --- | --- |
| Batch misto | IDs fixos `eval-0`, `eval-1`, `eval-unknown` | `SUCCEEDED`, `FAILED`, `UNKNOWN` após worker | PASS |
| Manual e background | seed `404`, mesmo `TransactionInput` e contexto | mesmo evento/outcome; input não contém outcome/status | PASS |
| Baixo volume | 11 tentativas, threshold 12 | nenhum `AnomalyCandidate`, nenhuma alternativa causal | PASS |
| Simultâneos / empate | provider e issuer com score/support iguais | `INCONCLUSIVE`, sem vencedor único | PASS |

## Métricas observadas

- Cobertura de estados terminais no batch misto: `3/3` (`SUCCEEDED`, `FAILED`, `UNKNOWN`).
- Equivalência de transporte no mesmo input/contexto: `1/1`.
- False candidates no caso de baixo volume: `0/1`.
- Preservação de `INCONCLUSIVE` no empate: `1/1`.
- `root_cause_accuracy`, `scope_exact_match`, `false_incidents`, `separation_rate` e `inconclusive_precision` estatísticos: **NOT RUN** nesta matriz; não há ground truth visível nem conjunto holdout. Eles pertencem à `LUM2-57`.

## Limitações e próximo gate

Os resultados provam invariantes de contrato e abstention no conjunto de desenvolvimento, não generalização estatística. A `LUM2-57` deve usar somente eventos/logs persistidos, abrir ground truth apenas depois da resposta e congelar thresholds antes do holdout final.
