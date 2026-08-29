# Plano individual — Renato

## Missão

- **Plano geral:** 1.4.0
- **Objetivo:** `OBJ-RENATO-001`
- **Papel:** geração sintética, baselines, detector estatístico, RCA e avaliação causal.
- **Orçamento:** 13–14h de implementação; H15–H19 integração/validação.
- **Resultado:** máxima precisão top-1 no holdout de novas combinações, com falsos alertas baixos e `INCONCLUSIVE` calibrado.

## Context pack

O LLM não gera milhões de linhas e não diagnostica. O gerador vetorizado produz 90 dias reprodutíveis e publica transações continuamente no servidor; um listener da ingestão recebe os eventos do servidor. O ground truth fica separado. O detector recebe WindowMetrics e devolve candidatos. O RCA explora dimensões hierarquicamente e retorna evidências numéricas, sem narrativa.

Renato decide suficiência causal exclusivamente com dados atuais. O RCA deve conseguir sustentar uma combinação inédita sem consultar Neo4j; a memória posterior não participa do score nem do limiar de `INCONCLUSIVE`. Tanto o resultado suportado quanto o inconclusivo precisam carregar escopo, métricas, sinais e limitações suficientes para Altoé consultar precedentes.

O holdout deve privilegiar combinações nunca vistas, pois a capacidade principal do sistema é descobrir problemas novos; recorrência é avaliada separadamente por Altoé.

## Ownership e limites

- **Own:** `CMP-DATA-001`, `CMP-DET-001`, `CMP-RCA-001`; diretórios propostos `app/simulation/`, `app/detection/`, `app/diagnosis/`, `tests/evals/`.
- **Produz:** `CTR-SCN-001`, `CTR-EVT-001` publicado através de `CTR-STR-001`, `CTR-DET-001` e candidates para `CTR-INC-001`.
- **Consome:** `CTR-AGG-001`.
- **Hotspots:** não alterar canonical/incident schema; dependency changes passam por Rogério.
- **Fora de escopo:** texto LLM, Neo4j, frontend, antifraude real e RL.

## Interfaces

### CTR-SCN-001 v1 — produzido

Schema: `contracts/v1/scenario.schema.json`. Filtros aceitam qualquer dimensão conhecida; efeitos incluem approval multiplier, latency multiplier, timeout rate e decline distribution. `ground_truth` é persistido em caminho separado e nunca entra em payload de detecção.

### CTR-STR-001 v1 — publicado

Cada evento `CTR-EVT-001` é colocado no servidor de transações com um envelope monotônico (`sequence`, `published_at`, `payload`). O gerador não importa `app.ingestion`; o listener do owner Rogério lê pelo cursor e aplica a ingestão. O adapter local é o mock de desenvolvimento e deve poder ser trocado por servidor externo sem alterar o gerador.

### CTR-AGG-001 v1 — consumido

Campos: window, dimensions, attempt/payment counts, amount/currency, approval/payment conversion, p50/p95, timeout, declines, quality, revision e correlation.

### CTR-DET-001 v1 — produzido

```text
AnomalyCandidate {
  candidate_id:string; window:{start,end}; slice:map<string,string>;
  metric:"APPROVAL_RATE"|"LATENCY_P95"|"TIMEOUT_RATE";
  observed:float; expected:float; sample_size:int;
  effect_absolute:float; effect_relative:float;
  statistical_strength:float; lost_approvals:float;
  loss_coverage:float; temporal_consistency:float; data_quality:float;
  evidence_refs:string[]; detector_version:string
}
```

Nenhum texto causal livre. Sem evidência: zero candidates ou candidato marcado para `INCONCLUSIVE` pelo correlator.

## Plano de execução

### TASK-RENATO-001 — Gerar 90 dias determinísticos e publicar no servidor

- **Tempo:** H1–H3.
- **Ferramentas:** NumPy, seed fixa e `TransactionPublisher`/`CTR-STR-001`.
- **Distribuições:** merchant/provider/country/method/issuer/brand, sazonalidade hora/dia, approval condicional, latency lognormal/robusta e decline mapping.
- **Aceite:** mesmo seed produz a mesma sequência/payload; volume varia por hora, dia da semana e tendência; uma janela de baixa amostra é marcada no relatório; eventos chegam ao listener sem chamada direta à ingestão.
- **Teste:** distribuição, invariantes, referential integrity, baixa amostra, reprodução e publicação/consumo de contrato.

### TASK-RENATO-002 — Implementar scenario injector e stream

- **Tempo:** H3–H4.
- **Aceite:** nova combinação via JSON sem código; múltiplos efeitos simultâneos; ground truth isolado.
- **Teste:** provider BR e issuer MX simultâneos.

### TASK-RENATO-003 — Implementar baseline e detector

- **Tempo:** H3–H7.
- **Método:** 5m windows; weekday/time bucket; pooling; Beta-Binomial/Wilson para approval; p95/MAD para latency; min n e persistence.
- **Aceite:** normal não alerta; provider BR produz candidate; low volume não afirma causa.

### TASK-RENATO-004 — Implementar RCA hierárquico

- **Tempo:** H7–H10.
- **Método:** beam search depth <=3, contribuição para lost approvals, complexity penalty e dominance pruning.
- **Aceite:** exact scope no caso provider-country e merchant-issuer; não superespecializa quando provider global cai.

### TASK-RENATO-005 — Separação e casos difíceis em fixtures

- **Tempo:** H10–H12.
- **Casos:** simultaneous, latency-only, mix shift/Simpson, duplicates, unknown code, late data, recurrence signature e diffuse inconclusive.
- **Handoff:** candidates esperados para Rogério e signatures para Altoé, inclusive para casos `INCONCLUSIVE`, sem inserir causa histórica no score atual.

### TASK-RENATO-006 — Holdout e tuning por evidência

- **Tempo:** H12–H15.
- **Aceite:** reporta top-1 accuracy, scope exact match, false alerts e inconclusive; inclui causa nova suportada sem precedente; thresholds congelados antes do holdout final.
- **Regra:** não ajustar usando o caso secreto de trial by fire.

## Git e handoffs

- Branch sugerida: `feat/OBJ-RENATO-001-simulation-detection`.
- Entregar primeiro scenario/candidate fixtures, depois implementação.
- Commits: generator; injector; detector; RCA; evals.
- `READY TO MERGE`: seed reproducível, ground truth isolado, holdout report e contract tests.

## Riscos e autonomia

- Pode ajustar parâmetros estatísticos com dev evals; decisão material de threshold recebe Flight Log.
- Deve parar se precisão depender de hardcode do cenário ou do ground truth.
- Fallback: baseline pré-agregado; preservar 90 dias lógicos mesmo reduzindo raw row count.

## Sincronização Linear

- Parent: [LUM2-7](https://linear.app/lumenhack/issue/LUM2-7/entregar-dados-sinteticos-deteccao-e-rca).
- Microtarefas: `TASK-DATA-001`→`LUM2-43`, `TASK-DATA-002`→`LUM2-45`, `TASK-DATA-003`→`LUM2-46`, `TASK-DATA-004`→`LUM2-44`, `TASK-DATA-005`→`LUM2-47`, `TASK-DATA-006`→`LUM2-48`, `TASK-DATA-007`→`LUM2-49`, `TASK-DET-001`→`LUM2-50`, `TASK-DET-002`→`LUM2-51`, `TASK-DET-003`→`LUM2-52`, `TASK-DET-004`→`LUM2-53`, `TASK-RCA-001`→`LUM2-54`, `TASK-RCA-002`→`LUM2-55`, `TASK-EVAL-001`→`LUM2-56`, `TASK-EVAL-002`→`LUM2-57`.
- **Correção (2026-08-29):** o campo "ID estável" dentro de `LUM2-44/45/46` no Linear está rotacionado (cada um cita o ID errado dos três) — confiar no título real da issue e neste mapa, não no texto interno da issue. `LUM2-44` = "Gerar 90 dias com sazonalidade" (`TASK-DATA-004`); `LUM2-45` = "Gerar outcomes condicionais e retries" (`TASK-DATA-002`); `LUM2-46` = "Gerar latências e decline codes coerentes" (`TASK-DATA-003`).
- Fonte completa de dependências: `docs/plans/linear-preview.md`.
