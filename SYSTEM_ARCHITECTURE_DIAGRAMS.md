# System Architecture Diagrams (Mermaid Format)

## Overview

This document contains Mermaid-format diagrams for the complete system architecture, including third-party API integration flows. The architecture incorporates patterns from [OpenMetadata](https://open-metadata.org/) (connector management) and [ShaderFrog](https://shaderfrog.com/2/) (visual composition).

---

## Complete System Flow Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Flow Editor UI<br/>ReactFlow + Next.js]
        Panel[Block Panel<br/>Sidebar]
        Config[Trigger Config<br/>Modal]
    end
    
    subgraph "API Gateway"
        Gateway[Kong/Tyk API Gateway<br/>Rate Limiting<br/>Authentication]
    end
    
    subgraph "Application Layer"
        WorkflowSvc[Workflow Service]
        SemanticRouter[Semantic Router<br/>Intelligent Routing]
        ExecEngine[Execution Engine]
        
        BlockReg[Block Registry]
        TriggerReg[Trigger Registry]
        ToolReg[Tool Registry]
    end
    
    subgraph "Integration Layer"
        ConnMgr[Connector Manager]
        CredMgr[Credential Manager]
        WebhookHdl[Webhook Handler]
        OAuthHdl[OAuth Handler]
        CacheMgr[Cache Manager]
        RateLimiter[Rate Limiter]
    end
    
    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL<br/>Primary Database)]
        Redis[(Redis<br/>Cache & Queue)]
        Elasticsearch[(Elasticsearch<br/>Logs)]
    end
    
    subgraph "External Services"
        GoogleAPI[Google APIs]
        SlackAPI[Slack API]
        GitHubAPI[GitHub API]
        OtherAPIs[Other APIs]
    end
    
    UI --> Gateway
    Panel --> Gateway
    Config --> Gateway
    
    Gateway --> WorkflowSvc
    Gateway --> SemanticRouter
    
    WorkflowSvc --> ExecEngine
    SemanticRouter --> ExecEngine
    
    ExecEngine --> BlockReg
    ExecEngine --> TriggerReg
    ExecEngine --> ToolReg
    
    ExecEngine --> ConnMgr
    ExecEngine --> CredMgr
    ExecEngine --> WebhookHdl
    
    ConnMgr --> OAuthHdl
    ConnMgr --> CacheMgr
    ConnMgr --> RateLimiter
    
    CredMgr --> PostgreSQL
    WebhookHdl --> Redis
    CacheMgr --> Redis
    
    ConnMgr --> GoogleAPI
    ConnMgr --> SlackAPI
    ConnMgr --> GitHubAPI
    ConnMgr --> OtherAPIs
    
    WorkflowSvc --> PostgreSQL
    ExecEngine --> Redis
    ExecEngine --> PostgreSQL
    
    WebhookHdl --> Elasticsearch
    
    style UI fill:#e1f5ff
    style Gateway fill:#fff4e1
    style SemanticRouter fill:#f3e5f5
    style ExecEngine fill:#e8f5e9
    style ConnMgr fill:#fce4ec
    style PostgreSQL fill:#e3f2fd
    style Redis fill:#ffebee
```

## Third-Party API Integration Flow

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant SemanticRouter
    participant ConnectorMgr
    participant ToolWrapper
    participant CredentialMgr
    participant APIClient
    participant ExternalAPI
    
    User->>UI: Natural Language Query
    UI->>SemanticRouter: Route Query
    SemanticRouter->>SemanticRouter: Analyze Query<br/>(Check Route Maps)
    
    alt High Confidence Match
        SemanticRouter->>ConnectorMgr: Route to Connector
        ConnectorMgr->>ConnectorMgr: Load Connector Config
        
        alt Tool Wrapper Enabled
            ConnectorMgr->>ToolWrapper: Create CrewAI Tool
            ToolWrapper->>ToolWrapper: Wrap API Endpoints
            ToolWrapper->>ToolWrapper: Create Agent Crew
            ToolWrapper->>ToolWrapper: Execute with LLM
        else Direct Execution
            ConnectorMgr->>ConnectorMgr: Validate Config
        end
        
        ConnectorMgr->>CredentialMgr: Get Credentials
        CredentialMgr->>CredentialMgr: Check Token Expiry
        
        alt Token Expired
            CredentialMgr->>CredentialMgr: Refresh Token
        end
        
        CredentialMgr->>ConnectorMgr: Return Credentials
        
        ConnectorMgr->>ConnectorMgr: Check Rate Limit
        ConnectorMgr->>ConnectorMgr: Check Circuit Breaker
        
        alt Circuit Breaker Open
            ConnectorMgr->>UI: Error: Circuit Breaker Open
        else Rate Limit Exceeded
            ConnectorMgr->>UI: Error: Rate Limit Exceeded
        else Proceed
            ConnectorMgr->>APIClient: Execute Request
            APIClient->>ExternalAPI: HTTP Request
            ExternalAPI->>APIClient: Response
            
            alt Success
                APIClient->>ConnectorMgr: Success Response
                ConnectorMgr->>ConnectorMgr: Update Circuit Breaker
                ConnectorMgr->>ConnectorMgr: Cache Result
                ConnectorMgr->>UI: Return Result
            else Error
                APIClient->>ConnectorMgr: Error Response
                ConnectorMgr->>ConnectorMgr: Retry Logic
                ConnectorMgr->>ConnectorMgr: Update Circuit Breaker
                ConnectorMgr->>UI: Return Error
            end
        end
    else Low Confidence
        SemanticRouter->>UI: Fallback: Generic HTTP Tool
        UI->>ConnectorMgr: Use Generic HTTP Block
        ConnectorMgr->>APIClient: Execute Generic Request
        APIClient->>ExternalAPI: HTTP Request
        ExternalAPI->>APIClient: Response
        APIClient->>UI: Return Result
    end
```

## Block Execution Flow

```mermaid
flowchart TD
    Start([Workflow Triggered]) --> Validate{Validate Workflow}
    Validate -->|Invalid| Error1([Error: Invalid Workflow])
    Validate -->|Valid| LoadBlock[Load Block from Registry]
    
    LoadBlock --> CheckVersion{Block Version<br/>Compatible?}
    CheckVersion -->|No| Error2([Error: Version Mismatch])
    CheckVersion -->|Yes| ValidateConfig[Validate Block Config<br/>with Zod Schema]
    
    ValidateConfig -->|Invalid| Error3([Error: Invalid Config])
    ValidateConfig -->|Valid| CheckCircuit{Circuit Breaker<br/>Open?}
    
    CheckCircuit -->|Yes| Error4([Error: Circuit Breaker Open])
    CheckCircuit -->|No| CheckRateLimit{Rate Limit<br/>Exceeded?}
    
    CheckRateLimit -->|Yes| Error5([Error: Rate Limit Exceeded])
    CheckRateLimit -->|No| CheckCache{Cache Hit?}
    
    CheckCache -->|Yes| ReturnCache([Return Cached Result])
    CheckCache -->|No| CheckTimeout{Set Execution<br/>Timeout}
    
    CheckTimeout --> Execute[Execute Block]
    Execute --> CheckSuccess{Execution<br/>Success?}
    
    CheckSuccess -->|No| Retry{Retry<br/>Enabled?}
    Retry -->|Yes| CheckMaxRetries{Max Retries<br/>Reached?}
    CheckMaxRetries -->|No| Backoff[Wait with Backoff]
    Backoff --> Execute
    CheckMaxRetries -->|Yes| UpdateCircuitFailure[Update Circuit Breaker<br/>Record Failure]
    UpdateCircuitFailure --> Error6([Error: Execution Failed])
    
    CheckSuccess -->|Yes| UpdateCircuitSuccess[Update Circuit Breaker<br/>Record Success]
    UpdateCircuitSuccess --> CacheResult{Cacheable?}
    
    CacheResult -->|Yes| StoreCache[Store in Cache]
    StoreCache --> RecordMetrics[Record Metrics]
    CacheResult -->|No| RecordMetrics
    
    RecordMetrics --> ReturnResult([Return Result])
    
    style Start fill:#e8f5e9
    style ReturnResult fill:#e8f5e9
    style ReturnCache fill:#e8f5e9
    style Error1 fill:#ffebee
    style Error2 fill:#ffebee
    style Error3 fill:#ffebee
    style Error4 fill:#ffebee
    style Error5 fill:#ffebee
    style Error6 fill:#ffebee
```

## Trigger Activation Flow

```mermaid
flowchart TD
    Start([User Creates Trigger]) --> Validate{Validate Trigger<br/>Config}
    Validate -->|Invalid| Error1([Error: Invalid Config])
    Validate -->|Valid| CheckType{Trigger Type?}
    
    CheckType -->|Webhook| WebhookFlow[Webhook Flow]
    CheckType -->|Polling| PollingFlow[Polling Flow]
    CheckType -->|Schedule| ScheduleFlow[Schedule Flow]
    CheckType -->|Manual| ManualFlow[Manual Flow]
    
    subgraph WebhookFlow[Webhook Activation]
        WebhookFlow --> GeneratePath[Generate Webhook Path]
        GeneratePath --> StoreMapping[Store Path Mapping]
        StoreMapping --> VerifySig{Verify Signature<br/>Required?}
        VerifySig -->|Yes| HandleChallenge[Handle Challenge Response]
        VerifySig -->|No| Activate[Activate Webhook]
        HandleChallenge --> Activate
    end
    
    subgraph PollingFlow[Polling Activation]
        PollingFlow --> SetInterval[Set Polling Interval]
        SetInterval --> StartPoll[Start Polling Loop]
        StartPoll --> PollAPI[Poll External API]
        PollAPI --> ProcessItems{New Items?}
        ProcessItems -->|Yes| QueueExecution[Queue Workflow Execution]
        ProcessItems -->|No| Wait[Wait for Interval]
        QueueExecution --> Wait
        Wait --> PollAPI
    end
    
    subgraph ScheduleFlow[Schedule Activation]
        ScheduleFlow --> ParseCron[Parse Cron Expression]
        ParseCron --> ValidateCron{Valid Cron?}
        ValidateCron -->|No| Error2([Error: Invalid Cron])
        ValidateCron -->|Yes| ScheduleJob[Schedule Job in Queue]
        ScheduleJob --> Activate
    end
    
    subgraph ManualFlow[Manual Activation]
        ManualFlow --> CreateButton[Create Manual Trigger Button]
        CreateButton --> Activate
    end
    
    Activate --> StoreTrigger[Store Trigger in DB]
    StoreTrigger --> Monitor[Start Monitoring]
    Monitor --> Success([Trigger Activated])
    
    style Start fill:#e8f5e9
    style Success fill:#e8f5e9
    style Error1 fill:#ffebee
    style Error2 fill:#ffebee
```

## Semantic Routing Flow

```mermaid
flowchart TD
    Start([User Query Received]) --> EncodeQuery[Encode Query<br/>with OpenAI Embedding]
    EncodeQuery --> TopLevelRoute[Top-Level Router<br/>Route to Flow]
    
    TopLevelRoute --> CheckConfidence{Confidence<br/>Threshold?}
    CheckConfidence -->|Low < 0.7| Fallback[Fallback Routing]
    CheckConfidence -->|High >= 0.7| GetFlow[Get Flow Router]
    
    GetFlow --> FlowLevelRoute[Flow-Level Router<br/>Route to Tool]
    FlowLevelRoute --> CheckToolConfidence{Tool Confidence<br/>Threshold?}
    
    CheckToolConfidence -->|Low < 0.7| UseFlowDefault[Use Flow Default Tool]
    CheckToolConfidence -->|High >= 0.7| GetTool[Get Specific Tool]
    
    UseFlowDefault --> LoadTool[Load Tool Config]
    GetTool --> LoadTool
    
    LoadTool --> CheckWrapper{Tool Wrapper<br/>Enabled?}
    CheckWrapper -->|Yes| CreateWrapper[Create CrewAI Tool Wrapper]
    CheckWrapper -->|No| DirectExec[Direct Execution]
    
    CreateWrapper --> CreateAgent[Create Agent with Tools]
    CreateAgent --> ExecuteCrew[Execute Crew with Query]
    ExecuteCrew --> ParseResult[Parse Crew Result]
    
    DirectExec --> ExecuteTool[Execute Tool Directly]
    ExecuteTool --> ParseResult
    
    ParseResult --> ReturnResult([Return Result])
    
    Fallback --> GenericTool[Use Generic HTTP Tool]
    GenericTool --> ReturnResult
    
    style Start fill:#e8f5e9
    style ReturnResult fill:#e8f5e9
    style Fallback fill:#fff9c4
    style GenericTool fill:#fff9c4
```

## Credential Management Flow

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant CredentialMgr
    participant OAuthHandler
    participant Encryption
    participant Database
    participant ExternalProvider
    
    User->>UI: Initiate OAuth Connection
    UI->>CredentialMgr: Request OAuth URL
    CredentialMgr->>OAuthHandler: Generate OAuth URL
    OAuthHandler->>OAuthHandler: Create State Token
    OAuthHandler->>ExternalProvider: Redirect to OAuth
    ExternalProvider->>User: Show Authorization Page
    User->>ExternalProvider: Authorize Application
    ExternalProvider->>OAuthHandler: Return Authorization Code
    OAuthHandler->>ExternalProvider: Exchange Code for Tokens
    ExternalProvider->>OAuthHandler: Return Access & Refresh Tokens
    
    OAuthHandler->>CredentialMgr: Tokens Received
    CredentialMgr->>Encryption: Encrypt Credentials
    Encryption->>CredentialMgr: Encrypted Data
    CredentialMgr->>Database: Store Encrypted Credentials
    Database->>CredentialMgr: Credential ID
    CredentialMgr->>UI: Connection Successful
    
    Note over CredentialMgr,Database: Token Refresh Flow
    CredentialMgr->>CredentialMgr: Check Token Expiry
    CredentialMgr->>Database: Fetch Credential
    Database->>CredentialMgr: Encrypted Credential
    CredentialMgr->>Encryption: Decrypt Credential
    Encryption->>CredentialMgr: Decrypted Token
    
    alt Token Expired
        CredentialMgr->>ExternalProvider: Refresh Token
        ExternalProvider->>CredentialMgr: New Access Token
        CredentialMgr->>Encryption: Encrypt New Token
        Encryption->>CredentialMgr: Encrypted Data
        CredentialMgr->>Database: Update Credential
    end
```

## Workflow Execution Flow

```mermaid
flowchart TD
    Start([Workflow Execution Triggered]) --> LoadWorkflow[Load Workflow State]
    LoadWorkflow --> ValidateWorkflow{Workflow Valid?}
    ValidateWorkflow -->|No| Error1([Error: Invalid Workflow])
    ValidateWorkflow -->|Yes| FindTrigger[Find Trigger Block]
    
    FindTrigger --> ExecuteTrigger[Execute Trigger Block]
    ExecuteTrigger --> GetOutput[Get Trigger Output]
    GetOutput --> FindStartBlock[Find Start Block]
    
    FindStartBlock --> ExecutionLoop{More Blocks<br/>to Execute?}
    
    ExecutionLoop -->|Yes| GetNextBlock[Get Next Block]
    GetNextBlock --> ValidateInput{Input Valid?}
    ValidateInput -->|No| Error2([Error: Invalid Input])
    ValidateInput -->|Yes| ExecuteBlock[Execute Block]
    
    ExecuteBlock --> CheckSuccess{Execution<br/>Success?}
    CheckSuccess -->|No| HandleError[Handle Error]
    HandleError --> CheckRetry{Retry<br/>Enabled?}
    CheckRetry -->|Yes| RetryBlock[Retry Block]
    RetryBlock --> ExecuteBlock
    CheckRetry -->|No| Error3([Error: Block Failed])
    
    CheckSuccess -->|Yes| StoreOutput[Store Block Output]
    StoreOutput --> FindNextBlocks[Find Connected Blocks]
    FindNextBlocks --> ExecutionLoop
    
    ExecutionLoop -->|No| CollectResults[Collect All Results]
    CollectResults --> StoreExecution[Store Execution Log]
    StoreExecution --> Success([Workflow Completed])
    
    style Start fill:#e8f5e9
    style Success fill:#e8f5e9
    style Error1 fill:#ffebee
    style Error2 fill:#ffebee
    style Error3 fill:#ffebee
```

## System Component Interaction

```mermaid
graph LR
    subgraph "Client"
        Browser[Web Browser]
        Mobile[Mobile App]
    end
    
    subgraph "Load Balancer"
        LB[Load Balancer<br/>Nginx]
    end
    
    subgraph "API Gateway"
        Gateway[Kong/Tyk<br/>Rate Limiting<br/>Auth]
    end
    
    subgraph "Application Services"
        API1[API Instance 1]
        API2[API Instance 2]
        API3[API Instance 3]
    end
    
    subgraph "Background Services"
        Worker1[Worker 1]
        Worker2[Worker 2]
        Scheduler[Scheduler]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL<br/>Primary)]
        PG_REPLICA[(PostgreSQL<br/>Replica)]
        REDIS[(Redis<br/>Cache)]
        QUEUE[(Redis<br/>Queue)]
    end
    
    Browser --> LB
    Mobile --> LB
    LB --> Gateway
    Gateway --> API1
    Gateway --> API2
    Gateway --> API3
    
    API1 --> PG
    API2 --> PG
    API3 --> PG
    
    API1 --> REDIS
    API2 --> REDIS
    API3 --> REDIS
    
    API1 --> QUEUE
    API2 --> QUEUE
    API3 --> QUEUE
    
    QUEUE --> Worker1
    QUEUE --> Worker2
    
    Scheduler --> QUEUE
    
    PG --> PG_REPLICA
    
    style Browser fill:#e1f5ff
    style Gateway fill:#fff4e1
    style API1 fill:#e8f5e9
    style API2 fill:#e8f5e9
    style API3 fill:#e8f5e9
    style PG fill:#e3f2fd
    style REDIS fill:#ffebee
```

## Monitoring & Observability Flow

```mermaid
flowchart TD
    Start([System Operation]) --> Instrument[Instrumentation]
    
    Instrument --> Metrics[Metrics Collection]
    Instrument --> Traces[Distributed Tracing]
    Instrument --> Logs[Logging]
    
    Metrics --> Prometheus[Prometheus<br/>Time Series DB]
    Traces --> Jaeger[Jaeger<br/>Tracing Backend]
    Logs --> Elasticsearch[(Elasticsearch<br/>Log Storage)]
    
    Prometheus --> Grafana[Grafana<br/>Dashboards]
    Jaeger --> Grafana
    Elasticsearch --> Grafana
    
    Grafana --> AlertManager[Alert Manager]
    AlertManager --> Notifications[Notifications<br/>Email/Slack/PagerDuty]
    
    style Start fill:#e8f5e9
    style Prometheus fill:#e3f2fd
    style Grafana fill:#f3e5f5
    style AlertManager fill:#fff9c4
```

---

## How to Use These Diagrams

### For Draw.io

1. Open [draw.io](https://app.diagrams.net/)
2. Go to **File → Import From → Device**
3. Copy the Mermaid code
4. Draw.io doesn't natively support Mermaid, but you can:
   - Use [Mermaid Live Editor](https://mermaid.live/) to convert to SVG
   - Import the SVG into draw.io
   - Or manually recreate using draw.io shapes

### For Mermaid Live Editor

1. Go to [https://mermaid.live/](https://mermaid.live/)
2. Paste any diagram code
3. Export as PNG, SVG, or copy the link

### For Documentation

These diagrams can be embedded directly in Markdown files if your documentation platform supports Mermaid (GitHub, GitLab, many wikis).

### For Presentations

Export as PNG/SVG from Mermaid Live Editor and import into PowerPoint, Keynote, or Google Slides.

---

## UI Flow Components (OpenMetadata & ShaderFrog)

### Connector Browser (OpenMetadata Pattern)

The connector browser UI (inspired by OpenMetadata) appears in the Frontend Layer, providing:
- Visual connector discovery with categorized browsing
- Search and filter capabilities
- One-click connection initiation

### Visual Editor (ShaderFrog Pattern)

The flow editor UI incorporates ShaderFrog patterns:
- Inline parameter controls on nodes
- Real-time preview of API requests/responses
- Visual feedback during configuration
- Drag-and-drop connector placement

These UI components enhance the user experience for API integration workflows.

---

## Related Documentation

- **Production System Design**: See `PRODUCTION_SYSTEM_DESIGN.md` for complete architecture
- **Third-Party API Structure**: See `THIRD_PARTY_API_STRUCTURE.md` for connector structure
- **Integration Flow**: See `THIRD_PARTY_API_INTEGRATION_FLOW_EXPLAINED.md` for detailed flow explanation
- **UI Flow Patterns**: See `OPENMETADATA_SHADERFROG_UI_PATTERNS.md` for UI implementation patterns
- **Best Approach**: See `BEST_API_INTEGRATION_APPROACH.md` for recommended integration approach
- **Integration Patterns**: See `THIRD_PARTY_API_INTEGRATION_PATTERNS.md` for integration patterns

---

*All diagrams are optimized for production system architecture visualization. UI patterns inspired by OpenMetadata (connector management) and ShaderFrog (visual composition).*

