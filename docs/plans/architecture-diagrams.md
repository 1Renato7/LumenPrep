# Diagramas de arquitetura — Lumen 2.0

Fonte de verdade: `docs/plans/system-plan.md` v2.0.0.

## Fluxo do produto

```mermaid
flowchart TD
    A[Adicionar 1..100 transações<br/>ou gerar samples por quantidade + seed] --> B[Revisar linhas editáveis]
    B --> C[Submit batch]
    C --> D[Railway persiste antes do 202]
    D --> E[Worker processa cada transaction]
    E --> F[Log: PROCESSING<br/>stage + progress real]
    E --> G[Outcome: SUCCEEDED<br/>FAILED ou UNKNOWN]
    G --> H[Classificação e evidências]
    H --> I[Agregação e baseline automáticos]
    I --> J{Anomalia sustentada?}
    J -->|Não| K[Log permanece consultável<br/>sem inventar incidente]
    J -->|Sim| L[RCA + Incident]
    L --> M[Memória + explicação grounded]
    M --> N[Detalhe linka transaction,<br/>evidence, incident e precedent]
```

## Deploy Vercel + Railway

```mermaid
flowchart LR
    U[Browser] --> V[Next.js<br/>Vercel]
    V -->|HTTPS /v1<br/>CORS allowlist| R[FastAPI<br/>Railway public domain]
    R --> W[Worker<br/>Railway]
    W --> D[(DuckDB + Parquet<br/>Railway Volume)]
    R --> D
    W --> N[Neo4j<br/>incident memory]
    W --> O[OpenAI<br/>grounded explanation]
    X[Internal traffic/scenario harness] --> R
    D -. no public access .- V
    N -. no direct browser access .- V
```

## Lanes paralelas

```mermaid
flowchart TB
    C[CTR-TXN-001 + CTR-TXL-001 + CTR-API-001 v3 frozen]
    C --> A[André<br/>Next input + samples<br/>logs + detail]
    C --> R[Rogério<br/>batch API + worker<br/>Railway deploy]
    C --> T[Renato<br/>outcome adapter<br/>samples + background traffic]
    C --> G[Altoé<br/>transaction-to-incident trace<br/>grounded explanation]
    A --> I[Contract integration]
    R --> I
    T --> I
    G --> I
    I --> B[Browser acceptance<br/>Vercel → Railway]
```

## Autoridade dos dados

```mermaid
flowchart LR
    INPUT[TransactionInput<br/>user facts only] --> OUT[Deterministic outcome<br/>provider result + latency]
    OUT --> MET[Computed metrics<br/>rates + baseline]
    MET --> RCA[Detector/RCA<br/>cause status]
    RCA --> INC[Incident]
    INC --> RAG[Memory/RAG<br/>context + wording]
    RAG --> UI[UI presentation]
```

Cada etapa pode enriquecer a seguinte, mas nenhuma etapa posterior reescreve fatos anteriores. O navegador apresenta; não calcula outcome, taxa, causa ou confiança.
