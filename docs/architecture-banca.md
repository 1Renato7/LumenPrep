# Arquitetura do código — LumenPrep

Este é o diagrama da arquitetura que existe no repositório. Ele mostra os módulos, as
fronteiras de processo e os caminhos de dados do produto; não é um desenho de requisitos
do desafio.

```mermaid
flowchart TB
    Browser["Navegador do operador"]

    subgraph Web["web/ — Next.js"]
        direction TB
        Routes["App Router<br/>/ · /transactions · /transactions/new<br/>/transactions/[id] · /incidents · /incidents/[id]"]
        UI["Componentes<br/>transaction-form · transaction-log<br/>transaction-detail · incidents · notifications"]
        Client["lib/api<br/>client-interface → client-runtime → parse/types"]
        Routes --> UI --> Client
    end

    subgraph API["main.py + app/api/ — FastAPI"]
        direction TB
        App["create_app()<br/>CORS + lifespan"]
        TransactionAPI["transactions.py<br/>/v1/transaction-catalog<br/>/v1/transaction-samples<br/>/v1/transaction-batches<br/>/v1/transactions"]
        IncidentAPI["incidents.py<br/>/v1/incidents · notification<br/>review · suggestion · transaction grounding"]
        SupportAPI["health.py · metrics.py<br/>refusal_codes.py"]
        EventAPI["events.py<br/>POST /transactions<br/>GET /transactions/health"]
        DemoAPI["demo.py<br/>cenários e tráfego sintético"]
        App --> TransactionAPI
        App --> IncidentAPI
        App --> SupportAPI
        App --> EventAPI
        App --> DemoAPI
    end

    Browser --> Web
    Client -->|"HTTP JSON"| API

    subgraph TransactionPath["Caminho de transação — app/worker + app/ingestion"]
        direction LR
        Batch["BatchRequest<br/>Idempotency-Key"] --> PersistTxn["Persistência inicial<br/>transaction_batches<br/>transaction_records = PROCESSING"]
        PersistTxn --> Background["FastAPI BackgroundTask<br/>run_batch_to_completion"]
        Background --> Lifecycle["transaction_worker.py<br/>lease, retomada e estágios<br/>RECEIVED → COMPLETE"]
        Lifecycle --> Outcome["simulation/transaction_outcomes.py<br/>outcome e classificação determinísticos"]
        Outcome --> Refusal["refusal_codes/<br/>catálogo versionado + resolução"]
        Refusal --> Canonical["ingestion/<br/>normalização · validação · dedupe<br/>ordenação e eventos canônicos"]
    end

    TransactionAPI --> Batch

    subgraph IncidentPath["Caminho de incidentes — app/aggregation + app/detection + app/rca"]
        direction LR
        Canonical --> Pipeline["incident_pipeline.py<br/>derive_incidents_for_correlation"]
        Pipeline --> Windows["aggregation/windows.py<br/>janelas fechadas e recortes"]
        Windows --> Detector["detection/detector.py<br/>baseline histórico + guardrails"]
        Detector --> RCA["rca/ranking.py + beam.py<br/>hipóteses e evidências"]
        RCA --> IncidentRepo["incidents/<br/>Incident, deduplicação e links"]
        IncidentRepo --> SuggestionJob["SuggestionJob<br/>somente após incident persistido"]
    end

    subgraph Data["Persistência local — DuckDB (app/ingestion/storage.py)"]
        direction TB
        Raw["raw_events<br/>append-only"]
        CanonicalDB["canonical_events<br/>canonical_attempts"]
        TxnDB["transaction_batches<br/>transaction_records"]
        IncidentDB["incident_records<br/>transaction_incident_links<br/>incident_notifications"]
        AgentDB["incident_suggestions<br/>incident_reviews<br/>refusal_code_catalog"]
    end

    PersistTxn --> TxnDB
    Canonical --> Raw
    Canonical --> CanonicalDB
    IncidentRepo --> IncidentDB
    SuggestionJob --> AgentDB
    Refusal --> AgentDB

    subgraph ReadPath["Leitura, explicação e memória"]
        direction LR
        IncidentAPI --> ReadRepo["DuckDBIncidentRepository<br/>consulta incidentes, links e notificações"]
        ReadRepo --> IncidentDB
        IncidentAPI --> Grounding["explanation/<br/>TransactionGrounding + GroundedExplainer"]
        Grounding --> ReadRepo
        SuggestionJob --> Agent["agent/<br/>evidence · retrieval · validation<br/>Template ou OpenAI Responses opcional"]
        Agent --> AgentDB
        IncidentAPI --> Agent
        IncidentAPI --> Review["POST /incidents/{id}/review<br/>decisão humana idempotente"]
        Review --> AgentDB
        Review --> Memory
        IncidentAPI --> Memory
    end

    IncidentAPI -->|"incidentes, detalhe, logs,<br/>notificações e sugestão"| Client

    subgraph Memory["Memória opcional — app/memory"]
        direction TB
        Fallback["InMemoryIncidentRepository<br/>fallback determinístico"]
        Neo["Neo4jIncidentRepository<br/>quando NEO4J_URI está configurada"]
        Promotion["promotion.py<br/>somente review APPROVED"]
        Fallback --> Promotion
        Neo --> Promotion
    end

    Agent --> Memory

    subgraph Stream["Canal de stream usado pela simulação — app/streaming"]
        direction LR
        Simulator["simulation/<br/>live_stream · background_traffic<br/>historical · scenarios"] --> Server["TransactionServer<br/>log em memória, append-only"]
        Server --> Listener["IngestionListenerWorker<br/>thread iniciada no lifespan"]
        Listener --> Canonical
    end

    EventAPI --> Server
    DemoAPI --> Simulator

    classDef ui fill:#dbeafe,stroke:#1d4ed8,color:#172554;
    classDef api fill:#e0e7ff,stroke:#4338ca,color:#312e81;
    classDef worker fill:#dcfce7,stroke:#15803d,color:#14532d;
    classDef data fill:#fef3c7,stroke:#b45309,color:#78350f;
    classDef optional fill:#f3e8ff,stroke:#7e22ce,color:#581c87;
    classDef stream fill:#cffafe,stroke:#0e7490,color:#164e63;

    class Browser,Routes,UI,Client ui;
    class App,TransactionAPI,IncidentAPI,SupportAPI,EventAPI,DemoAPI api;
    class Batch,PersistTxn,Background,Lifecycle,Outcome,Refusal,Canonical,Pipeline,Windows,Detector,RCA,IncidentRepo,SuggestionJob,ReadRepo,Grounding,Agent,Review worker;
    class Raw,CanonicalDB,TxnDB,IncidentDB,AgentDB data;
    class Fallback,Neo,Promotion optional;
    class Simulator,Server,Listener stream;
```

## Como ler o desenho

- **Interface:** o diretório `web/` é um cliente Next.js. Ele não lê DuckDB nem Neo4j;
  usa os clientes tipados em `web/lib/api/` para chamar o FastAPI.
- **API e lifecycle:** `main.py` inicia o FastAPI, reconcilia trabalho pendente e sobe o
  listener de stream. A API de batch persiste primeiro e responde `202`; o worker avança
  a transação de forma durável.
- **Dados:** DuckDB é a fonte operacional de transações, eventos canônicos, incidentes,
  notificações, sugestões, revisões e catálogo de códigos. Parquet é usado pelo benchmark,
  não como o repositório transacional do fluxo online.
- **Incidentes:** o worker transforma resultados em eventos canônicos, calcula agregações,
  detecta anomalias, executa o RCA e só então persiste e relaciona o incidente.
- **Memória e agente:** ambos são complementares. Neo4j só é usado se estiver configurado;
  sem ele há fallback em memória. O agente recebe evidência de um incidente já persistido e
  devolve uma sugestão, sem executar ações externas.
- **Demo:** com `DEMO_MODE=true`, os endpoints de leitura de incidentes usam fixtures em
  `contracts/fixtures/`; com o modo desligado, leem `DuckDBIncidentRepository`.

## Referências no código

- [Entrada da aplicação](../main.py)
- [Rotas da API](../app/api)
- [Worker transacional](../app/worker/transaction_worker.py)
- [Pipeline de incidentes](../app/worker/incident_pipeline.py)
- [Persistência DuckDB](../app/ingestion/storage.py)
- [Cliente web](../web/lib/api)
