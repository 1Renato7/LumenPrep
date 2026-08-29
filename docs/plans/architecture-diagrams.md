# Diagramas de arquitetura — Lumen

Fonte de verdade: `docs/plans/system-plan.md` v1.3.1. Estes diagramas são projeções explicativas; em caso de divergência, o plano geral vence.

## 1. Fluxo completo para público geral

```mermaid
flowchart TD
    A[Pagamentos simulados chegam] --> B[Padronizar e guardar eventos]
    B --> C[Comparar o momento atual com o histórico normal]
    C --> D{Existe anomalia relevante?}
    D -->|Não| E[Continuar observando sem alertar]
    D -->|Sim| F[Investigar provider, país, método, banco, bandeira e recusa]
    F --> G{Há evidência atual suficiente?}
    G -->|Sim| H[Status atual: SUPPORTED<br/>causa sustentada por dados atuais]
    G -->|Não| I[Status atual: INCONCLUSIVE<br/>explicar alternativas e dados faltantes]
    H --> J[Formar Incident e calcular<br/>alcance + GMV em risco]
    I --> J
    J --> K[Consultar memória sempre<br/>por escopo, sinais e forma temporal]
    K --> L{Encontrou precedente<br/>humano semelhante?}
    L -->|Sim| M[Mostrar precedente, causa anterior,<br/>fatores iguais/diferentes e solução usada]
    L -->|Não| N[Marcar NO_PRECEDENT]
    K -. memória indisponível .-> O[Manter status atual<br/>e mostrar limitação]
    M --> P
    N --> P
    O --> P
    P{Combinar status atual<br/>com status da memória}
    P -->|SUPPORTED + MATCH| Q[Causa atual + recorrência<br/>validar e priorizar solução anterior]
    P -->|SUPPORTED + NO_PRECEDENT| R[Causa atual sustentada<br/>possível problema novo]
    P -->|INCONCLUSIVE + MATCH| S[Causa atual continua inconclusiva<br/>precedente orienta a investigação]
    P -->|INCONCLUSIVE + NO_PRECEDENT| T[Inconclusivo:<br/>sem causa sustentada e sem precedente]
    P -->|MEMORY_UNAVAILABLE| U[Preservar status atual<br/>e declarar memória indisponível]
    Q --> V[Dashboard: o que, onde, evidências,<br/>impacto, precedente e sugestão]
    R --> V
    S --> V
    T --> V
    U --> V
    V --> W[Humano decide; sistema não executa ação]
```

## 2. André — frontend, demo e pitch

```mermaid
flowchart LR
    A[Fixtures JSON<br/>CTR-INC / CTR-LLM] --> B[Streamlit<br/>Python]
    C[FastAPI + OpenAPI<br/>GET incidents/metrics] --> B
    D[POST demo inject<br/>scenario_id] --> B
    B --> E[Cards executivos<br/>GMV + alcance]
    B --> F[Drill-down operacional<br/>evidence_ids + confidence]
    B --> G[Matriz na UI<br/>SUPPORTED ou INCONCLUSIVE<br/>× match / no precedent / unavailable]
    E --> H[Browser Acceptance Gate<br/>desktop + projetor]
    F --> H
    G --> H
    H --> I[Pitch e demo de 5–7 min]
```

## 3. Gabriel Altoé — Neo4j, Graph RAG e explicação

```mermaid
flowchart TD
    A[Incident atual<br/>SUPPORTED ou INCONCLUSIVE<br/>CTR-INC-001] --> B[Neo4j Driver + Cypher<br/>prefilter por escopo e sinais]
    B --> C[Score estruturado<br/>escopo + declines + forma temporal]
    C --> D[Embedding opcional<br/>text-embedding-3-small]
    D --> E[SimilarIncidentResult v1.1<br/>memory_status tipado<br/>CTR-MEM-001]
    C --> E
    E --> F{Há match acima do threshold?}
    F -->|Sim| G[Precedente HUMAN_CONFIRMED<br/>fatores iguais e diferentes]
    F -->|Não| H[matches=[]<br/>NO_PRECEDENT]
    A --> I[Catálogo versionado<br/>de playbooks]
    G --> J[OpenAI Responses API<br/>gpt-5.6-terra + Structured Outputs]
    H --> J
    I --> J
    J --> K[Validador de evidence_ids<br/>+ precondições do playbook<br/>+ template determinístico]
    K --> L[ExplanationBundle<br/>precedente não altera causa atual<br/>sempre HUMAN_ONLY]
```

## 4. Rogério — ingestão, dados, contratos e API

```mermaid
flowchart LR
    A[Eventos do gerador<br/>CTR-EVT-001] --> B[Pydantic<br/>validação e normalização]
    B --> C[(Parquet raw<br/>imutável)]
    B --> D[Dedup + watermark<br/>terminal-state guard]
    B -. inválido .-> E[(Quarantine)]
    D --> F[(DuckDB canonical)]
    F --> G[DuckDB SQL<br/>janelas de 5 min]
    G --> H[WindowMetrics<br/>CTR-AGG-001]
    I[AnomalyCandidates<br/>de Renato] --> J[Python correlator<br/>separação de incidentes]
    J --> K[Impacto local<br/>lost approvals + GMV]
    K --> L[Incident<br/>CTR-INC-001]
    L --> M[FastAPI + OpenAPI<br/>dois eixos independentes:<br/>root_cause + memory status]
    N[Memória v1.1 com status tipado<br/>+ ExplanationBundle de Altoé] --> M
    M --> O[Streamlit<br/>de André]
```

## 5. Renato — geração, detecção e causa raiz

```mermaid
flowchart TD
    A[Scenario JSON + seed<br/>CTR-SCN-001] --> B[NumPy + Polars<br/>gerador vetorizado]
    B --> C[90 dias em Parquet<br/>+ stream acelerado]
    C --> D[WindowMetrics<br/>de DuckDB]
    D --> E[NumPy + SciPy<br/>baseline sazonal]
    E --> F[Approval<br/>Beta-Binomial / Wilson]
    E --> G[Latência e timeout<br/>p95 + MAD robusto]
    F --> H[AnomalyCandidate<br/>CTR-DET-001]
    G --> H
    H --> I[Python beam search<br/>dimensões até depth 3]
    I --> J[Score de RCA<br/>coverage + força + qualidade]
    J --> K{Evidência atual suficiente?}
    K -->|Sim| L[Incident SUPPORTED<br/>scope + métricas + evidências]
    K -->|Não| M[Incident INCONCLUSIVE<br/>scope + sinais + dados faltantes]
    L --> N[Handoff para memória<br/>sem usar histórico no score]
    M --> N
    N --> O[Holdout e evals<br/>ground truth isolado]
```
