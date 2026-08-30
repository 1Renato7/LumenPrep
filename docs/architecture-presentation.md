# Arquitetura de apresentação - LumenPrep

Este desenho é intencionalmente orientado ao fluxo operacional. Setas contínuas representam
processamento ou persistência; setas tracejadas representam consulta ou tráfego interno.

```mermaid
flowchart TB
    Operator([Operador]) --> Client

    subgraph Web["Experiência web - Next.js"]
        direction LR
        Input["Entrada<br/>transações e samples"] --> Client["Cliente API tipado<br/>HTTP JSON"] --> Observe["Logs, detalhe, incidentes<br/>e notificações"]
    end

    subgraph API["Fronteira pública - FastAPI"]
        direction LR
        TxAPI["Transaction API<br/>batch, catálogo e logs"]
        OpsAPI["Operação<br/>health, métricas e demo"]
        IncAPI["Incident API<br/>detalhe, review e sugestão"]
    end

    Client -->|batch, catálogo e logs| TxAPI
    Client -->|health, métricas e demo| OpsAPI
    Client -->|incidents, review e sugestão| IncAPI

    subgraph Core["Núcleo determinístico - fonte da verdade operacional"]
        direction LR
        Accept["1. Aceitar lote<br/>persistir PROCESSING"] --> Worker["2. Worker durável<br/>lease, retomada e progresso"] --> Outcome["3. Outcome e classificação<br/>catálogo de refusal codes"] --> Ingest["4. Ingestão<br/>normalizar, validar e deduplicar"] --> Detect["5. Métricas e detecção<br/>baseline, anomalia e RCA"] --> Incident["6. Incident persistido<br/>evidências, links e notificação"]
    end

    TxAPI -->|persiste antes do 202| Accept
    OpsAPI -. tráfego sintético .-> Ingest

    subgraph Context["Contexto pós-incidente - nunca altera fatos ou causa"]
        direction LR
        Explain["Explicação grounded<br/>detalhe por transação"]
        Agent["Agente opcional<br/>hipótese HUMAN_ONLY"]
        Review["Revisão humana<br/>decisão idempotente"]
        Memory["Memória de precedentes<br/>Neo4j opcional, fallback em memória"]
    end

    Incident -->|fatos e evidências| Explain
    Incident -->|fatos e evidências| Agent
    IncAPI -->|registra decisão| Review
    Review -->|somente APPROVED| Memory
    Explain -. consulta de precedente .-> Memory
    Agent -. consulta de precedente .-> Memory

    subgraph Data["DuckDB - estado operacional persistente"]
        direction LR
        TxData["Lotes e transações<br/>status e outcomes"]
        EventData["Eventos raw e canônicos<br/>tentativas e agregações"]
        IncData["Incidents, links<br/>notificações e reviews"]
        AssistData["Sugestões e catálogo<br/>de refusal codes"]
    end

    Accept --> TxData
    Worker --> TxData
    Ingest --> EventData
    Detect --> EventData
    Incident --> IncData
    IncAPI -. consulta .-> IncData
    Agent --> AssistData
    Outcome -. consulta catálogo .-> AssistData

    classDef ui fill:#eaf2ff,stroke:#2563eb,color:#172554,stroke-width:2px;
    classDef api fill:#eef2ff,stroke:#4f46e5,color:#312e81,stroke-width:2px;
    classDef core fill:#ecfdf5,stroke:#059669,color:#064e3b,stroke-width:2px;
    classDef data fill:#fff7ed,stroke:#d97706,color:#78350f,stroke-width:2px;
    classDef intel fill:#faf5ff,stroke:#9333ea,color:#581c87,stroke-width:2px;
    classDef human fill:#fff1f2,stroke:#e11d48,color:#881337,stroke-width:2px;
    class Operator,Input,Observe,Client ui;
    class TxAPI,IncAPI,OpsAPI api;
    class Accept,Worker,Outcome,Ingest,Detect,Incident core;
    class TxData,EventData,IncData,AssistData data;
    class Explain,Agent,Memory intel;
    class Review human;
```

## Leitura do diagrama

- A UI é consumidora da API: não consulta DuckDB ou Neo4j diretamente.
- O lote é gravado como `PROCESSING` antes da resposta `202`; o worker pode retomar o trabalho.
- DuckDB guarda os fatos operacionais. Explicação, agente e memória apenas enriquecem a leitura pós-incidente.
- Neo4j é opcional e recebe um precedente somente depois de uma revisão humana `APPROVED`.
