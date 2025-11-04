# Production-Level System Design: Blocks, Triggers & Third-Party API Integration

## Executive Summary

This document provides a **production-ready** system design for a visual workflow platform combining:
- **Visual Blocks & Triggers** (from [`repos/sim`](https://github.com/simstudioai/sim), [`repos/Flowise`](https://github.com/FlowiseAI/Flowise), [`repos/flojoy`](https://github.com/flojoy-ai/studio))
- **Semantic Routing & Intelligent Tool Selection** (from umbrella_corp)
- **Connector Management UI** (from [OpenMetadata](https://open-metadata.org/) - 100+ connectors)
- **Visual Composition Patterns** (from [ShaderFrog](https://shaderfrog.com/2/) - node-based editor)
- **Production-Grade Infrastructure** (scalability, reliability, monitoring)

## Source Repositories

This design incorporates best practices from the following cloned repositories:

- **Sim**: [`repos/sim`](https://github.com/simstudioai/sim) - Trigger system, webhook handling, OAuth integration
- **Flowise**: [`repos/Flowise`](https://github.com/FlowiseAI/Flowise) - HTTP request tools, OAuth2 credentials
- **Flojoy**: [`repos/flojoy`](https://github.com/flojoy-ai/studio) - Manifest-based blocks
- **Flojoy Studiolab**: [`repos/flojoy-studiolab`](https://github.com/flojoy-ai/studiolab) - Alternative implementation
- **FedRAMP Automation**: [`repos/fedramp-automation`](https://github.com/GSA/fedramp-automation) - Validation patterns

---

## Table of Contents

1. [Production Architecture Overview](#production-architecture-overview)
2. [Blocks System (Production-Ready)](#blocks-system-production-ready)
3. [Triggers System (Production-Ready)](#triggers-system-production-ready)
4. [Third-Party API Integration (Production-Ready)](#third-party-api-integration-production-ready)
5. [Semantic Routing & Intelligent Tool Selection](#semantic-routing--intelligent-tool-selection)
6. [Production Infrastructure](#production-infrastructure)
7. [Monitoring & Observability](#monitoring--observability)
8. [Security & Compliance](#security--compliance)
9. [Deployment Strategy](#deployment-strategy)

---

## Production Architecture Overview

### System Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    Presentation Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Flow Editor  │  │ Block Panel  │  │  Dashboard   │         │
│  │ (ReactFlow)  │  │ (Sidebar)    │  │  (Monitoring)│         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────▼──────────────────────────────────┐
│                    Application Layer                             │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              API Gateway (Kong/Tyk)                     │   │
│  │  - Rate Limiting  - Authentication  - Request Routing │   │
│  └────────────────────────────────────────────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Workflows    │  │ Semantic     │  │  Execution   │       │
│  │ Service      │  │ Router       │  │  Engine      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Blocks       │  │ Triggers     │  │  Tools        │       │
│  │ Registry     │  │ Registry     │  │  Registry     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────▼──────────────────────────────────┐
│                    Integration Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Connector    │  │ Credential   │  │  Webhook     │         │
│  │ Manager      │  │ Manager      │  │  Handler     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ OAuth        │  │ Rate Limit   │  │  Cache       │         │
│  │ Handler      │  │ Manager      │  │  Manager     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────▼──────────────────────────────────┐
│                    Data & Infrastructure Layer                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ PostgreSQL   │  │ Redis        │  │  Queue       │         │
│  │ (Primary DB) │  │ (Cache/State)│  │  (BullMQ)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ S3/MinIO     │  │ Elasticsearch│  │  Prometheus  │         │
│  │ (Storage)    │  │ (Logs)       │  │  (Metrics)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack (Production)

**Frontend:**
- Next.js 14+ (App Router)
- ReactFlow (visual editor)
- Zustand (state management)
- Tailwind CSS + shadcn/ui
- React Query (data fetching)

**Backend:**
- Node.js 20+ (or Bun for better performance)
- Express.js / Next.js API Routes
- TypeScript (strict mode)
- Zod (validation)

**Database:**
- PostgreSQL 15+ (primary database)
- Redis 7+ (caching, queues, sessions)
- Elasticsearch (logs, search)

**Infrastructure:**
- Docker + Kubernetes (or Docker Compose for smaller deployments)
- Nginx / Traefik (reverse proxy)
- Kong / Tyk (API gateway)
- Prometheus + Grafana (monitoring)
- Sentry (error tracking)

**Message Queue:**
- BullMQ (job queue)
- Redis Streams (event streaming)

**External Services:**
- AWS S3 / MinIO (file storage)
- Cloudflare (CDN, DDoS protection)

---

## Blocks System (Production-Ready)

### Block Registry Architecture

```typescript
// blocks/registry.ts
export interface ProductionBlockConfig extends BlockConfig {
  // Production metadata
  version: string
  deprecated?: boolean
  deprecationDate?: string
  migrationPath?: string
  
  // Performance
  executionTimeout?: number // milliseconds
  maxConcurrency?: number
  rateLimit?: {
    requests: number
    window: number // seconds
  }
  
  // Monitoring
  metrics?: {
    enabled: boolean
    trackExecutionTime: boolean
    trackErrorRate: boolean
  }
  
  // Caching
  cacheable?: boolean
  cacheTTL?: number // seconds
  cacheKey?: (config: BlockExecutionConfig) => string
  
  // Retry logic
  retry?: {
    enabled: boolean
    maxAttempts: number
    backoff: 'exponential' | 'linear' | 'fixed'
    initialDelay: number // milliseconds
  }
  
  // Circuit breaker
  circuitBreaker?: {
    enabled: boolean
    failureThreshold: number
    resetTimeout: number // milliseconds
  }
  
  // Validation
  schema: ZodSchema
  
  // Execution
  execute: (
    config: BlockExecutionConfig,
    context: ExecutionContext
  ) => Promise<BlockOutput>
  
  // Health check
  healthCheck?: () => Promise<boolean>
}

// Production block registry with versioning
export class ProductionBlockRegistry {
  private blocks = new Map<string, ProductionBlockConfig>()
  private versions = new Map<string, string[]>() // blockId -> versions[]
  
  register(block: ProductionBlockConfig): void {
    // Validate block
    this.validateBlock(block)
    
    // Store version history
    const versions = this.versions.get(block.id) || []
    versions.push(block.version)
    this.versions.set(block.id, versions.sort())
    
    // Store block
    this.blocks.set(`${block.id}@${block.version}`, block)
    
    // Register as latest if no version conflict
    if (!this.blocks.has(block.id)) {
      this.blocks.set(block.id, block)
    }
  }
  
  get(blockId: string, version?: string): ProductionBlockConfig | undefined {
    if (version) {
      return this.blocks.get(`${blockId}@${version}`)
    }
    return this.blocks.get(blockId)
  }
  
  private validateBlock(block: ProductionBlockConfig): void {
    // Validate schema
    if (!block.schema) {
      throw new Error(`Block ${block.id} must have a schema`)
    }
    
    // Validate execute function
    if (typeof block.execute !== 'function') {
      throw new Error(`Block ${block.id} must have an execute function`)
    }
  }
}
```

### Block Execution with Production Features

```typescript
// lib/execution/block-executor.ts
export class ProductionBlockExecutor {
  private circuitBreakers = new Map<string, CircuitBreaker>()
  private rateLimiters = new Map<string, RateLimiter>()
  private cache: Redis
  
  async execute(
    block: ProductionBlockConfig,
    config: BlockExecutionConfig,
    context: ExecutionContext
  ): Promise<BlockOutput> {
    const startTime = Date.now()
    const executionId = generateExecutionId()
    
    // 1. Validate input
    try {
      config = block.schema.parse(config)
    } catch (error) {
      throw new ValidationError(`Invalid block configuration: ${error.message}`)
    }
    
    // 2. Check circuit breaker
    if (block.circuitBreaker?.enabled) {
      const breaker = this.getCircuitBreaker(block.id)
      if (breaker.isOpen()) {
        throw new CircuitBreakerOpenError(`Circuit breaker open for ${block.id}`)
      }
    }
    
    // 3. Check rate limit
    if (block.rateLimit) {
      const limiter = this.getRateLimiter(block.id)
      const allowed = await limiter.checkLimit(
        context.userId || 'anonymous',
        block.rateLimit.requests,
        block.rateLimit.window
      )
      if (!allowed) {
        throw new RateLimitError(`Rate limit exceeded for ${block.id}`)
      }
    }
    
    // 4. Check cache
    if (block.cacheable && block.cacheKey) {
      const cacheKey = block.cacheKey(config)
      const cached = await this.cache.get(cacheKey)
      if (cached) {
        return JSON.parse(cached)
      }
    }
    
    // 5. Execute with timeout and retry
    try {
      const result = await this.executeWithRetry(
        block,
        config,
        context,
        executionId
      )
      
      // 6. Cache result
      if (block.cacheable && block.cacheKey) {
        const cacheKey = block.cacheKey(config)
        await this.cache.setex(
          cacheKey,
          block.cacheTTL || 3600,
          JSON.stringify(result)
        )
      }
      
      // 7. Record metrics
      const duration = Date.now() - startTime
      this.recordMetrics(block.id, 'success', duration)
      
      // 8. Update circuit breaker
      if (block.circuitBreaker?.enabled) {
        this.getCircuitBreaker(block.id).recordSuccess()
      }
      
      return result
      
    } catch (error) {
      // Record failure
      const duration = Date.now() - startTime
      this.recordMetrics(block.id, 'error', duration, error)
      
      // Update circuit breaker
      if (block.circuitBreaker?.enabled) {
        this.getCircuitBreaker(block.id).recordFailure()
      }
      
      throw error
    }
  }
  
  private async executeWithRetry(
    block: ProductionBlockConfig,
    config: BlockExecutionConfig,
    context: ExecutionContext,
    executionId: string
  ): Promise<BlockOutput> {
    const retryConfig = block.retry || {
      enabled: false,
      maxAttempts: 1,
      backoff: 'exponential',
      initialDelay: 1000
    }
    
    if (!retryConfig.enabled) {
      return this.executeWithTimeout(block, config, context)
    }
    
    let lastError: Error
    for (let attempt = 0; attempt < retryConfig.maxAttempts; attempt++) {
      try {
        return await this.executeWithTimeout(block, config, context)
      } catch (error) {
        lastError = error as Error
        
        // Don't retry on validation errors
        if (error instanceof ValidationError) {
          throw error
        }
        
        // Calculate delay
        const delay = this.calculateBackoff(
          attempt,
          retryConfig.backoff,
          retryConfig.initialDelay
        )
        
        await sleep(delay)
      }
    }
    
    throw lastError!
  }
  
  private async executeWithTimeout(
    block: ProductionBlockConfig,
    config: BlockExecutionConfig,
    context: ExecutionContext
  ): Promise<BlockOutput> {
    const timeout = block.executionTimeout || 30000 // 30s default
    
    return Promise.race([
      block.execute(config, context),
      new Promise<never>((_, reject) => {
        setTimeout(() => {
          reject(new TimeoutError(`Block execution timeout: ${block.id}`))
        }, timeout)
      })
    ])
  }
}
```

### Block Categories (Production Structure)

```typescript
// blocks/categories.ts
export enum BlockCategory {
  // Core
  TRIGGER = 'trigger',
  LOGIC = 'logic',
  DATA = 'data',
  
  // AI/ML
  AI_AGENT = 'ai_agent',
  LLM = 'llm',
  EMBEDDING = 'embedding',
  VECTOR_STORE = 'vector_store',
  
  // API Integration
  HTTP = 'http',
  OAUTH = 'oauth',
  WEBHOOK = 'webhook',
  
  // Third-Party Services
  GOOGLE = 'google',
  SLACK = 'slack',
  GITHUB = 'github',
  MICROSOFT = 'microsoft',
  
  // Data Processing
  TRANSFORM = 'transform',
  FILTER = 'filter',
  AGGREGATE = 'aggregate',
  
  // Workflow Control
  LOOP = 'loop',
  PARALLEL = 'parallel',
  CONDITION = 'condition',
  DELAY = 'delay'
}

// Block organization
export const BLOCK_CATEGORIES: Record<BlockCategory, BlockCategoryConfig> = {
  [BlockCategory.TRIGGER]: {
    name: 'Triggers',
    icon: '⚡',
    description: 'Start workflows with events',
    color: 'blue'
  },
  [BlockCategory.AI_AGENT]: {
    name: 'AI Agents',
    icon: '🤖',
    description: 'Intelligent agents powered by LLMs',
    color: 'purple'
  },
  // ... more categories
}
```

---

## Triggers System (Production-Ready)

### Trigger Registry Architecture

```typescript
// triggers/registry.ts
export interface ProductionTriggerConfig extends TriggerConfig {
  // Production metadata
  version: string
  deprecated?: boolean
  
  // Performance
  maxConcurrency?: number
  batchSize?: number // For polling triggers
  
  // Reliability
  retry?: {
    enabled: boolean
    maxAttempts: number
    backoff: 'exponential' | 'linear'
  }
  
  // Monitoring
  metrics?: {
    trackExecutionCount: boolean
    trackErrorRate: boolean
    trackLatency: boolean
  }
  
  // Webhook-specific
  webhook?: {
    method?: 'POST' | 'GET' | 'PUT' | 'DELETE'
    verifySignature: boolean
    signatureAlgorithm?: 'sha256' | 'sha1'
    challengeResponse?: boolean // For webhook verification
    headers?: Record<string, string>
    rateLimit?: {
      requests: number
      window: number
    }
  }
  
  // Polling-specific
  polling?: {
    interval: number // seconds
    maxItems?: number
    backoffMultiplier?: number // For rate limiting
  }
  
  // Schedule-specific
  schedule?: {
    cronExpression: string
    timezone?: string
    maxInstances?: number // Prevent overlapping executions
  }
  
  // Health check
  healthCheck?: () => Promise<boolean>
}

export class ProductionTriggerRegistry {
  private triggers = new Map<string, ProductionTriggerConfig>()
  private activeTriggers = new Map<string, ActiveTriggerInstance>()
  
  register(trigger: ProductionTriggerConfig): void {
    this.validateTrigger(trigger)
    this.triggers.set(trigger.id, trigger)
  }
  
  async activate(
    triggerId: string,
    workflowId: string,
    config: TriggerInstanceConfig
  ): Promise<ActiveTriggerInstance> {
    const trigger = this.triggers.get(triggerId)
    if (!trigger) {
      throw new Error(`Trigger not found: ${triggerId}`)
    }
    
    // Validate configuration
    this.validateTriggerConfig(trigger, config)
    
    // Create instance
    const instance = await this.createTriggerInstance(trigger, workflowId, config)
    
    // Start trigger based on type
    switch (trigger.type) {
      case 'webhook':
        await this.activateWebhook(instance)
        break
      case 'polling':
        await this.activatePolling(instance)
        break
      case 'schedule':
        await this.activateSchedule(instance)
        break
    }
    
    this.activeTriggers.set(instance.id, instance)
    return instance
  }
  
  private async activateWebhook(instance: ActiveTriggerInstance): Promise<void> {
    const trigger = instance.config
    
    // Create webhook endpoint
    const webhookPath = await this.createWebhookEndpoint(instance)
    
    // Store webhook mapping
    await this.storeWebhookMapping(webhookPath, instance.id)
    
    // If challenge response is required, handle it
    if (trigger.webhook?.challengeResponse) {
      await this.handleWebhookChallenge(instance)
    }
  }
  
  private async activatePolling(instance: ActiveTriggerInstance): Promise<void> {
    const trigger = instance.config
    const interval = trigger.polling!.interval * 1000
    
    // Start polling loop
    const poll = async () => {
      try {
        const items = await this.pollForItems(instance)
        if (items.length > 0) {
          await this.processPolledItems(instance, items)
        }
      } catch (error) {
        this.handlePollingError(instance, error)
      }
      
      // Schedule next poll
      setTimeout(poll, interval)
    }
    
    // Initial poll
    poll()
  }
  
  private async activateSchedule(instance: ActiveTriggerInstance): Promise<void> {
    const trigger = instance.config
    const cronExpression = trigger.schedule!.cronExpression
    
    // Schedule job using BullMQ
    await this.scheduleManager.addJob({
      id: instance.id,
      cron: cronExpression,
      timezone: trigger.schedule!.timezone,
      workflowId: instance.workflowId,
      config: instance.config
    })
  }
}
```

### Webhook Handler (Production)

```typescript
// lib/webhooks/webhook-handler.ts
export class ProductionWebhookHandler {
  private webhookStore: WebhookStore
  private signatureVerifier: SignatureVerifier
  
  async handleWebhook(
    path: string,
    request: Request
  ): Promise<Response> {
    const startTime = Date.now()
    const requestId = generateRequestId()
    
    try {
      // 1. Find webhook instance
      const instance = await this.webhookStore.findByPath(path)
      if (!instance) {
        return new Response('Not Found', { status: 404 })
      }
      
      const trigger = instance.config
      
      // 2. Handle challenge response (for webhook verification)
      if (request.method === 'GET' && trigger.webhook?.challengeResponse) {
        return this.handleChallenge(request, instance)
      }
      
      // 3. Verify signature
      if (trigger.webhook?.verifySignature) {
        const payload = await request.text()
        const signature = request.headers.get('X-Signature') || 
                         request.headers.get('X-Hub-Signature-256')
        
        const isValid = await this.signatureVerifier.verify(
          payload,
          signature!,
          instance.secret,
          trigger.webhook.signatureAlgorithm || 'sha256'
        )
        
        if (!isValid) {
          logger.warn(`[${requestId}] Invalid webhook signature`, {
            path,
            instanceId: instance.id
          })
          return new Response('Invalid Signature', { status: 401 })
        }
      }
      
      // 4. Check rate limit
      if (trigger.webhook?.rateLimit) {
        const allowed = await this.checkRateLimit(
          instance.id,
          trigger.webhook.rateLimit
        )
        if (!allowed) {
          return new Response('Rate Limit Exceeded', { 
            status: 429,
            headers: { 'Retry-After': trigger.webhook.rateLimit.window.toString() }
          })
        }
      }
      
      // 5. Parse payload
      const payload = await this.parsePayload(request, trigger)
      
      // 6. Queue workflow execution
      await this.queueWorkflowExecution(instance, payload)
      
      // 7. Return response
      return new Response('OK', { status: 200 })
      
    } catch (error) {
      logger.error(`[${requestId}] Webhook handling error`, {
        path,
        error: error instanceof Error ? error.message : String(error)
      })
      
      return new Response('Internal Server Error', { status: 500 })
    } finally {
      const duration = Date.now() - startTime
      this.recordMetrics('webhook', duration)
    }
  }
  
  private async queueWorkflowExecution(
    instance: ActiveTriggerInstance,
    payload: any
  ): Promise<void> {
    await this.workflowQueue.add('execute', {
      workflowId: instance.workflowId,
      triggerId: instance.id,
      payload,
      timestamp: new Date().toISOString()
    }, {
      attempts: 3,
      backoff: {
        type: 'exponential',
        delay: 2000
      }
    })
  }
}
```

---

## Third-Party API Integration (Production-Ready)

### Connector Architecture with Semantic Routing

```typescript
// tools/connector-manager.ts
export interface ProductionConnectorConfig extends ConnectorConfig {
  // Semantic routing
  semanticRouting?: {
    enabled: boolean
    routeMap?: string // Path to route map JSON
    utterances?: string[] // Keywords for semantic matching
    confidenceThreshold?: number // Minimum confidence for routing
  }
  
  // Tool wrapping (CrewAI-style)
  toolWrapper?: {
    enabled: boolean
    crewName?: string
    agentRole?: string
    agentGoal?: string
    agentBackstory?: string
  }
  
  // Production features
  version: string
  healthCheck: () => Promise<boolean>
  rateLimit: RateLimitConfig
  retry: RetryConfig
  circuitBreaker: CircuitBreakerConfig
}

export class ProductionConnectorManager {
  private connectors = new Map<string, ProductionConnectorConfig>()
  private semanticRouter: SemanticRouter
  private toolWrappers = new Map<string, ToolWrapper>()
  
  register(connector: ProductionConnectorConfig): void {
    // Validate connector
    this.validateConnector(connector)
    
    // Register semantic routing if enabled
    if (connector.semanticRouting?.enabled) {
      this.registerSemanticRoute(connector)
    }
    
    // Register tool wrapper if enabled
    if (connector.toolWrapper?.enabled) {
      this.registerToolWrapper(connector)
    }
    
    // Store connector
    this.connectors.set(connector.id, connector)
  }
  
  async routeToConnector(
    userQuery: string,
    context?: RoutingContext
  ): Promise<ConnectorRoutingResult> {
    // Use semantic router to find best connector
    const routingResult = await this.semanticRouter.route(userQuery)
    
    if (routingResult.confidence < 0.7) {
      // Low confidence - try fallback
      return this.fallbackRouting(userQuery, context)
    }
    
    const connectorId = routingResult.routeName
    const connector = this.connectors.get(connectorId)
    
    if (!connector) {
      throw new Error(`Connector not found: ${connectorId}`)
    }
    
    return {
      connector,
      confidence: routingResult.confidence,
      route: routingResult.routeName,
      reasoning: routingResult.reasoning
    }
  }
  
  async executeWithToolWrapper(
    connector: ProductionConnectorConfig,
    query: string,
    config: any
  ): Promise<any> {
    if (!connector.toolWrapper?.enabled) {
      // Direct execution
      return this.executeConnector(connector, config)
    }
    
    // Use tool wrapper (CrewAI-style)
    const wrapper = this.toolWrappers.get(connector.id)
    if (!wrapper) {
      throw new Error(`Tool wrapper not found for ${connector.id}`)
    }
    
    return wrapper.execute(query, config)
  }
}
```

### Tool Wrapper (CrewAI-style)

```typescript
// tools/tool-wrapper.ts
export class ToolWrapper {
  private crew: CrewAI.Crew
  private tools: CrewAI.Tool[]
  
  constructor(
    private connector: ProductionConnectorConfig,
    private llm: LLM
  ) {
    this.tools = this.createToolsFromConnector(connector)
    this.crew = this.createCrew()
  }
  
  private createToolsFromConnector(
    connector: ProductionConnectorConfig
  ): CrewAI.Tool[] {
    // Convert connector endpoints to CrewAI tools
    return Object.entries(connector.endpoints).map(([name, endpoint]) => {
      return new CrewAI.Tool({
        name: `${connector.id}_${name}`,
        description: endpoint.description || `Call ${connector.name} ${name} endpoint`,
        func: async (params: any) => {
          return this.executeEndpoint(connector, name, params)
        }
      })
    })
  }
  
  private createCrew(): CrewAI.Crew {
    const config = this.connector.toolWrapper!
    
    const agent = new CrewAI.Agent({
      role: config.agentRole || `${this.connector.name} Agent`,
      goal: config.agentGoal || `Execute ${this.connector.name} operations`,
      backstory: config.agentBackstory || 
        `You are an expert at using ${this.connector.name} API`,
      tools: this.tools,
      llm: this.llm,
      verbose: true
    })
    
    return new CrewAI.Crew({
      agents: [agent],
      tasks: []
    })
  }
  
  async execute(query: string, config?: any): Promise<any> {
    // Create task from user query
    const task = new CrewAI.Task({
      description: query,
      agent: this.crew.agents[0]
    })
    
    // Execute crew
    const result = await this.crew.kickoff([task])
    
    return result
  }
  
  private async executeEndpoint(
    connector: ProductionConnectorConfig,
    endpointName: string,
    params: any
  ): Promise<any> {
    const endpoint = connector.endpoints[endpointName]
    const client = this.getClient(connector)
    
    // Execute with production features
    return this.executeWithRetry(
      () => client.call(endpoint, params),
      connector.retry
    )
  }
}
```

### Semantic Router Integration

```typescript
// lib/routing/semantic-router.ts
export class ProductionSemanticRouter {
  private router: SemanticRouter
  private routeMaps: Map<string, RouteMap>
  
  constructor(apiKey: string) {
    const encoder = new OpenAIEncoder({ apiKey })
    this.router = new SemanticRouter({
      encoder,
      routes: [],
      autoSync: 'local'
    })
    this.routeMaps = new Map()
  }
  
  async loadRouteMap(connectorId: string, routeMapPath: string): Promise<void> {
    const routeMap = await this.loadRouteMapFromFile(routeMapPath)
    this.routeMaps.set(connectorId, routeMap)
    
    // Add routes to semantic router
    const routes = this.convertRouteMapToRoutes(routeMap)
    this.router.addRoutes(routes)
  }
  
  async route(query: string): Promise<RoutingResult> {
    const result = await this.router.route(query)
    
    return {
      routeName: result.name,
      confidence: result.confidence || 0,
      reasoning: result.reasoning,
      metadata: result.metadata
    }
  }
  
  private convertRouteMapToRoutes(routeMap: RouteMap): Route[] {
    return routeMap.routes.map(route => {
      return new Route({
        name: route.name,
        utterances: route.utterances,
        // Add modifiers if present
        ...(route.modifierFunc && {
          modifier: this.getModifier(route.modifierFunc)
        })
      })
    })
  }
}
```

### Route Map Structure (umbrella_corp pattern)

```json
// tools/route-maps/google-suite.json
{
  "connector": "google_suite",
  "routes": [
    {
      "tool": "gmail_send",
      "name": "EMAIL_MANAGEMENT_FLOW",
      "utterances": [
        "email",
        "send",
        "inbox",
        "message",
        "reply",
        "forward",
        "gmail",
        "compose"
      ],
      "modifierFunc": null
    },
    {
      "tool": "calendar_create",
      "name": "EVENT_MANAGEMENT_FLOW",
      "utterances": [
        "meeting",
        "schedule",
        "calendar",
        "appointment",
        "event",
        "book",
        "reserve"
      ],
      "modifierFunc": null
    },
    {
      "tool": "drive_upload",
      "name": "DRIVE_MANAGEMENT_FLOW",
      "utterances": [
        "file",
        "folder",
        "document",
        "share",
        "upload",
        "download",
        "google drive"
      ],
      "modifierFunc": null
    }
  ]
}
```

---

## UI Flows for API Integration (OpenMetadata & ShaderFrog Patterns)

### Connector Discovery UI (OpenMetadata Pattern)

**Inspired by**: [OpenMetadata's connector browser](https://open-metadata.org/) with 100+ connectors

**UI Flow Components:**

```typescript
// components/connectors/ConnectorBrowser.tsx
export interface ConnectorBrowserProps {
  connectors: Connector[]
  onConnect: (connector: Connector) => void
  onViewDetails: (connector: Connector) => void
}

export function ConnectorBrowser({ connectors, onConnect, onViewDetails }: ConnectorBrowserProps) {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState<string | null>(null)
  
  // Categories from OpenMetadata pattern
  const categories = [
    'API',
    'Database',
    'Messaging',
    'Dashboard',
    'Pipeline',
    'ML Model',
    'Metadata',
    'Search',
    'Storage'
  ]
  
  const filteredConnectors = useMemo(() => {
    return connectors.filter(connector => {
      const matchesSearch = connector.name.toLowerCase().includes(search.toLowerCase()) ||
                           connector.description?.toLowerCase().includes(search.toLowerCase())
      const matchesCategory = !category || connector.category === category
      return matchesSearch && matchesCategory
    })
  }, [connectors, search, category])
  
  return (
    <div className="connector-browser">
      {/* Search & Filters (OpenMetadata-style) */}
      <div className="browser-header">
        <SearchInput value={search} onChange={setSearch} />
        <CategoryFilter 
          categories={categories}
          selected={category}
          onChange={setCategory}
        />
        <SortSelector />
      </div>
      
      {/* Connector Grid */}
      <div className="connector-grid">
        {filteredConnectors.map(connector => (
          <ConnectorCard
            key={connector.id}
            connector={connector}
            onClick={() => onViewDetails(connector)}
            onConnect={() => onConnect(connector)}
          />
        ))}
      </div>
    </div>
  )
}
```

**Key Features:**
- **Categorized Browser**: 100+ connectors organized by category
- **Visual Cards**: Icons, descriptions, status badges, popularity metrics
- **Search & Filter**: Text search, category filters, sort by popularity
- **Quick Connect**: One-click connection initiation

### Setup Wizard Flow (OpenMetadata Pattern)

**Multi-step guided configuration:**

```typescript
// components/connectors/ConnectorSetupWizard.tsx
export function ConnectorSetupWizard({ connector }: { connector: Connector }) {
  const [step, setStep] = useState(0)
  const [config, setConfig] = useState<Partial<ConnectorConfig>>({})
  
  const steps = [
    {
      id: 'select-endpoint',
      title: 'Select Endpoint',
      component: EndpointSelector,
      validate: (config) => !!config.endpoint
    },
    {
      id: 'configure-parameters',
      title: 'Configure Parameters',
      component: ParameterConfig,
      validate: (config) => validateParameters(config)
    },
    {
      id: 'authenticate',
      title: 'Authentication',
      component: AuthenticationSetup,
      validate: (config) => !!config.credentials
    },
    {
      id: 'test-connection',
      title: 'Test Connection',
      component: ConnectionTest,
      validate: (config) => config.testResult?.success === true
    },
    {
      id: 'review-deploy',
      title: 'Review & Deploy',
      component: ReviewAndDeploy,
      validate: (config) => true
    }
  ]
  
  return (
    <Wizard>
      <WizardHeader steps={steps} currentStep={step} />
      <WizardContent>
        {steps[step].component({ config, setConfig, connector })}
      </WizardContent>
      <WizardFooter>
        <Button onClick={() => setStep(step - 1)} disabled={step === 0}>
          Back
        </Button>
        <Button 
          onClick={() => setStep(step + 1)} 
          disabled={!steps[step].validate(config)}
        >
          {step === steps.length - 1 ? 'Deploy' : 'Next'}
        </Button>
      </WizardFooter>
    </Wizard>
  )
}
```

### Visual Node Configuration (ShaderFrog Pattern)

**Inline parameter controls with real-time preview:**

```typescript
// components/editor/ConnectorNode.tsx
export function ConnectorNode({ node }: { node: Node }) {
  const [config, setConfig] = useState(node.data.config)
  const [preview, setPreview] = useState<APIPreview | null>(null)
  
  // Update preview on config change (ShaderFrog-style real-time updates)
  useEffect(() => {
    const request = buildRequest(config)
    setPreview({ request, response: null })
  }, [config])
  
  return (
    <div className="connector-node">
      {/* Node Header */}
      <div className="node-header">
        <Icon name={node.data.connector.icon} />
        <span>{node.data.connector.name}</span>
        <StatusIndicator status={node.data.status} />
      </div>
      
      {/* Inline Parameters (ShaderFrog-style) */}
      <div className="node-parameters">
        <ParameterControl
          label="Endpoint"
          type="select"
          value={config.endpoint}
          options={node.data.connector.endpoints.map(e => e.name)}
          onChange={(value) => {
            setConfig({ ...config, endpoint: value })
          }}
        />
        
        <ParameterControl
          label="Method"
          type="select"
          value={config.method}
          options={['GET', 'POST', 'PUT', 'DELETE']}
          onChange={(value) => {
            setConfig({ ...config, method: value })
          }}
        />
        
        <ParameterControl
          label="Headers"
          type="json-editor"
          value={config.headers || {}}
          onChange={(value) => {
            setConfig({ ...config, headers: value })
          }}
        />
      </div>
      
      {/* Real-time Preview (ShaderFrog-style) */}
      {preview && (
        <div className="node-preview">
          <PreviewPanel preview={preview} />
          <TestButton 
            onClick={async () => {
              const response = await testConnection(config)
              setPreview({ ...preview, response })
            }}
          />
        </div>
      )}
    </div>
  )
}
```

**Key Features:**
- **Inline Controls**: Parameters visible directly on nodes
- **Real-time Updates**: Changes reflect immediately in preview
- **Visual Preview**: See API request/response as you configure
- **Type-appropriate Controls**: Select, input, slider, toggle based on parameter type

### Status Dashboard (OpenMetadata Pattern)

**Real-time health indicators and metrics:**

```typescript
// components/connectors/ConnectorStatusDashboard.tsx
export function ConnectorStatusDashboard({ connectors }: Props) {
  return (
    <div className="status-dashboard">
      {connectors.map(connector => (
        <ConnectorStatusCard
          key={connector.id}
          connector={connector}
          status={getStatus(connector)}
          metrics={getMetrics(connector)}
          actions={[
            { label: 'Test', onClick: () => testConnection(connector.id) },
            { label: 'Re-authenticate', onClick: () => reauthenticate(connector.id) },
            { label: 'View Logs', onClick: () => viewLogs(connector.id) }
          ]}
        />
      ))}
    </div>
  )
}

function getStatus(connector: Connector): 'connected' | 'warning' | 'error' | 'disconnected' {
  if (!connector.credentials) return 'disconnected'
  if (connector.lastError) return 'error'
  if (connector.tokenExpiresSoon) return 'warning'
  if (connector.lastSync) return 'connected'
  return 'disconnected'
}

function getMetrics(connector: Connector) {
  return {
    lastSync: connector.lastSync,
    syncFrequency: connector.syncFrequency,
    apiCalls: {
      total: connector.metrics?.totalCalls || 0,
      successful: connector.metrics?.successfulCalls || 0,
      failed: connector.metrics?.failedCalls || 0,
      rateLimited: connector.metrics?.rateLimitedCalls || 0
    },
    errorRate: connector.metrics?.errorRate || 0
  }
}
```

**Visual Indicators:**
- 🟢 **Connected**: Green indicator, "Connected" text
- 🟡 **Warning**: Yellow indicator, "Token expires soon" text
- 🔴 **Error**: Red indicator, "Connection failed" text
- ⚪ **Not Configured**: Gray indicator, "Not configured" text

### Combined UI Flow for API Integration

**Best practices from both platforms:**

1. **Discovery** (OpenMetadata):
   - Browse connectors by category
   - Search and filter
   - View connector details
   - Quick connect

2. **Setup** (OpenMetadata):
   - Multi-step wizard
   - Step-by-step validation
   - Test connection
   - Review and deploy

3. **Configuration** (ShaderFrog):
   - Drag connector to canvas
   - Inline parameter controls
   - Real-time preview
   - Visual feedback

4. **Monitoring** (OpenMetadata):
   - Status dashboard
   - Health indicators
   - API metrics
   - Quick actions

---

## Semantic Routing & Intelligent Tool Selection

### Hierarchical Routing System

```typescript
// lib/routing/hierarchical-router.ts
export class HierarchicalRouter {
  private topLevelRouter: SemanticRouter // Routes to flows
  private flowRouters: Map<string, SemanticRouter> // Routes within flows
  
  async route(query: string): Promise<HierarchicalRoutingResult> {
    // 1. Top-level routing (which flow?)
    const topLevelResult = await this.topLevelRouter.route(query)
    
    if (topLevelResult.confidence < 0.7) {
      return {
        flow: null,
        tool: null,
        confidence: topLevelResult.confidence,
        reasoning: 'Low confidence in top-level routing'
      }
    }
    
    const flowName = topLevelResult.name
    
    // 2. Flow-level routing (which tool within flow?)
    const flowRouter = this.flowRouters.get(flowName)
    if (!flowRouter) {
      return {
        flow: flowName,
        tool: null,
        confidence: topLevelResult.confidence,
        reasoning: 'Flow router not found'
      }
    }
    
    const flowResult = await flowRouter.route(query)
    
    return {
      flow: flowName,
      tool: flowResult.name,
      confidence: Math.min(topLevelResult.confidence, flowResult.confidence || 0),
      reasoning: `${topLevelResult.reasoning}. ${flowResult.reasoning}`
    }
  }
}
```

### Integration with Blocks

```typescript
// blocks/semantic-block.ts
export const SemanticRouterBlock: ProductionBlockConfig = {
  id: 'semantic_router',
  name: 'Semantic Router',
  category: BlockCategory.AI_AGENT,
  version: '1.0.0',
  
  configFields: {
    query: {
      type: 'string',
      label: 'User Query',
      required: true
    },
    connectorCategory: {
      type: 'select',
      label: 'Connector Category',
      options: ['google', 'slack', 'github', 'all'],
      defaultValue: 'all'
    }
  },
  
  async execute(config: BlockExecutionConfig, context: ExecutionContext) {
    const router = context.services.semanticRouter
    const query = config.query
    
    // Route to appropriate connector
    const routingResult = await router.routeToConnector(query)
    
    if (!routingResult.connector) {
      return {
        success: false,
        error: 'No suitable connector found',
        confidence: routingResult.confidence
      }
    }
    
    // Execute with tool wrapper
    const connectorManager = context.services.connectorManager
    const result = await connectorManager.executeWithToolWrapper(
      routingResult.connector,
      query,
      config
    )
    
    return {
      success: true,
      connector: routingResult.connector.id,
      confidence: routingResult.confidence,
      result
    }
  }
}
```

---

## Production Infrastructure

### API Gateway Configuration

```yaml
# kong/kong.yml
_format_version: "3.0"

services:
  - name: workflow-api
    url: http://api:3000
    routes:
      - name: workflows
        paths:
          - /api/v1/workflows
        methods:
          - GET
          - POST
          - PUT
          - DELETE
        plugins:
          - name: rate-limiting
            config:
              minute: 100
              hour: 1000
          - name: cors
            config:
              origins:
                - "*"
              methods:
                - GET
                - POST
                - PUT
                - DELETE
          - name: request-id
          - name: correlation-id
          - name: prometheus
            config:
              per_consumer: true
```

### Database Schema (Production)

```sql
-- workflows
CREATE TABLE workflows (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  state JSONB NOT NULL,
  version INTEGER NOT NULL DEFAULT 1,
  status VARCHAR(50) NOT NULL DEFAULT 'draft',
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by UUID REFERENCES users(id),
  INDEX idx_workspace (workspace_id),
  INDEX idx_status (status),
  INDEX idx_created_at (created_at)
);

-- blocks
CREATE TABLE blocks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
  block_type VARCHAR(100) NOT NULL,
  config JSONB NOT NULL,
  position JSONB,
  version VARCHAR(50) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  INDEX idx_workflow (workflow_id),
  INDEX idx_block_type (block_type)
);

-- triggers
CREATE TABLE triggers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
  trigger_type VARCHAR(100) NOT NULL,
  config JSONB NOT NULL,
  webhook_path VARCHAR(255) UNIQUE,
  secret VARCHAR(255),
  status VARCHAR(50) NOT NULL DEFAULT 'active',
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  INDEX idx_workflow (workflow_id),
  INDEX idx_webhook_path (webhook_path),
  INDEX idx_status (status)
);

-- credentials
CREATE TABLE credentials (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
  type VARCHAR(100) NOT NULL,
  provider VARCHAR(100) NOT NULL,
  encrypted_data BYTEA NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'active',
  expires_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  INDEX idx_user (user_id),
  INDEX idx_workspace (workspace_id),
  INDEX idx_type (type),
  INDEX idx_status (status)
);

-- executions
CREATE TABLE executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_id UUID NOT NULL REFERENCES workflows(id),
  trigger_id UUID REFERENCES triggers(id),
  status VARCHAR(50) NOT NULL,
  input JSONB,
  output JSONB,
  error JSONB,
  started_at TIMESTAMP NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMP,
  duration_ms INTEGER,
  INDEX idx_workflow (workflow_id),
  INDEX idx_trigger (trigger_id),
  INDEX idx_status (status),
  INDEX idx_started_at (started_at)
);

-- execution_logs
CREATE TABLE execution_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  execution_id UUID NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
  block_id UUID,
  level VARCHAR(20) NOT NULL,
  message TEXT NOT NULL,
  metadata JSONB,
  timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
  INDEX idx_execution (execution_id),
  INDEX idx_timestamp (timestamp)
);
```

### Queue Configuration

```typescript
// lib/queue/queue-manager.ts
export class ProductionQueueManager {
  private workflowQueue: Queue
  private webhookQueue: Queue
  private emailQueue: Queue
  
  constructor(redis: Redis) {
    this.workflowQueue = new Queue('workflow-execution', {
      connection: redis,
      defaultJobOptions: {
        attempts: 3,
        backoff: {
          type: 'exponential',
          delay: 2000
        },
        removeOnComplete: {
          age: 24 * 3600, // 24 hours
          count: 1000
        },
        removeOnFail: {
          age: 7 * 24 * 3600 // 7 days
        }
      }
    })
    
    // Process workflow jobs
    this.workflowQueue.process('execute', 10, async (job) => {
      return this.executeWorkflow(job.data)
    })
  }
  
  async addWorkflowExecution(
    workflowId: string,
    input: any,
    priority: number = 0
  ): Promise<Job> {
    return this.workflowQueue.add(
      'execute',
      { workflowId, input },
      {
        priority,
        jobId: `workflow-${workflowId}-${Date.now()}`
      }
    )
  }
}
```

---

## Monitoring & Observability

### Metrics Collection

```typescript
// lib/monitoring/metrics.ts
export class ProductionMetrics {
  private prometheus: PrometheusClient
  
  // Block metrics
  recordBlockExecution(
    blockId: string,
    status: 'success' | 'error',
    duration: number
  ): void {
    this.prometheus.histogram.observe(
      'block_execution_duration_seconds',
      duration / 1000,
      { block_id: blockId, status }
    )
    
    this.prometheus.counter.inc(
      'block_executions_total',
      { block_id: blockId, status }
    )
  }
  
  // Workflow metrics
  recordWorkflowExecution(
    workflowId: string,
    status: 'success' | 'error',
    duration: number
  ): void {
    this.prometheus.histogram.observe(
      'workflow_execution_duration_seconds',
      duration / 1000,
      { workflow_id: workflowId, status }
    )
  }
  
  // API metrics
  recordAPICall(
    connectorId: string,
    endpoint: string,
    status: number,
    duration: number
  ): void {
    this.prometheus.histogram.observe(
      'api_call_duration_seconds',
      duration / 1000,
      { connector_id: connectorId, endpoint, status }
    )
  }
}
```

### Distributed Tracing

```typescript
// lib/tracing/tracer.ts
export class ProductionTracer {
  private tracer: Tracer
  
  startWorkflowTrace(workflowId: string): Span {
    return this.tracer.startSpan('workflow.execute', {
      tags: {
        'workflow.id': workflowId,
        'service.name': 'workflow-engine'
      }
    })
  }
  
  startBlockTrace(blockId: string, parentSpan: Span): Span {
    return this.tracer.startSpan('block.execute', {
      childOf: parentSpan,
      tags: {
        'block.id': blockId
      }
    })
  }
  
  startAPITrace(connectorId: string, endpoint: string, parentSpan: Span): Span {
    return this.tracer.startSpan('api.call', {
      childOf: parentSpan,
      tags: {
        'connector.id': connectorId,
        'api.endpoint': endpoint
      }
    })
  }
}
```

---

## Security & Compliance

### Credential Encryption

```typescript
// lib/security/encryption.ts
export class ProductionEncryption {
  private keyManager: KeyManager
  
  async encryptCredential(data: any): Promise<EncryptedCredential> {
    const keyId = await this.keyManager.getLatestKey()
    const encrypted = await this.keyManager.encrypt(
      JSON.stringify(data),
      keyId
    )
    
    return {
      encryptedData: encrypted,
      keyId,
      algorithm: 'AES-256-GCM'
    }
  }
  
  async decryptCredential(encrypted: EncryptedCredential): Promise<any> {
    const key = await this.keyManager.getKey(encrypted.keyId)
    const decrypted = await this.keyManager.decrypt(
      encrypted.encryptedData,
      key
    )
    
    return JSON.parse(decrypted)
  }
}
```

### Audit Logging

```typescript
// lib/audit/audit-logger.ts
export class AuditLogger {
  async log(
    event: AuditEvent,
    userId: string,
    metadata?: any
  ): Promise<void> {
    await this.auditStore.create({
      event,
      userId,
      timestamp: new Date(),
      metadata,
      ipAddress: metadata?.ipAddress,
      userAgent: metadata?.userAgent
    })
  }
}

// Audit events
export enum AuditEvent {
  WORKFLOW_CREATED = 'workflow.created',
  WORKFLOW_UPDATED = 'workflow.updated',
  WORKFLOW_DELETED = 'workflow.deleted',
  CREDENTIAL_CREATED = 'credential.created',
  CREDENTIAL_UPDATED = 'credential.updated',
  CREDENTIAL_DELETED = 'credential.deleted',
  WORKFLOW_EXECUTED = 'workflow.executed',
  WEBHOOK_RECEIVED = 'webhook.received'
}
```

---

## Deployment Strategy

### Docker Compose (Development/Staging)

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/workflows
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=workflows
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    volumes:
      - redis_data:/data
  
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  postgres_data:
  redis_data:
  grafana_data:
```

### Kubernetes (Production)

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: workflow-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: workflow-api
  template:
    metadata:
      labels:
        app: workflow-api
    spec:
      containers:
      - name: api
        image: workflow-api:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## Conclusion

This production-level system design provides:

1. **Scalable Architecture**: Horizontal scaling, caching, queues
2. **Reliability**: Circuit breakers, retries, health checks
3. **Observability**: Metrics, tracing, logging
4. **Security**: Encryption, audit logs, rate limiting
5. **Semantic Intelligence**: Intelligent routing and tool selection
6. **Production Infrastructure**: Kubernetes, monitoring, CI/CD

### Key Production Features

- **Semantic Routing**: Intelligent tool/connector selection based on user queries
- **Tool Wrapping**: CrewAI-style tool wrapping for better AI integration
- **Circuit Breakers**: Prevent cascading failures
- **Rate Limiting**: Protect APIs from abuse
- **Caching**: Reduce API calls and improve performance
- **Retry Logic**: Handle transient failures
- **Monitoring**: Comprehensive observability
- **Security**: Encrypted credentials, audit logs

---

## Next Steps

1. **Phase 1**: Implement core blocks and triggers
2. **Phase 2**: Add semantic routing
3. **Phase 3**: Implement tool wrapping
4. **Phase 4**: Add production infrastructure
5. **Phase 5**: Monitoring and observability
6. **Phase 6**: Security hardening
7. **Phase 7**: Performance optimization

---

## Related Documentation

- **Comprehensive System Design**: See `COMPREHENSIVE_SYSTEM_DESIGN.md` for complete system overview
- **Third-Party API Structure**: See `THIRD_PARTY_API_STRUCTURE.md` for connector structure and patterns
- **Integration Flow**: See `THIRD_PARTY_API_INTEGRATION_FLOW_EXPLAINED.md` for detailed flow explanation
- **UI Flow Patterns**: See `OPENMETADATA_SHADERFROG_UI_PATTERNS.md` for UI implementation patterns
- **Best Approach**: See `BEST_API_INTEGRATION_APPROACH.md` for recommended integration approach
- **Integration Patterns**: See `THIRD_PARTY_API_INTEGRATION_PATTERNS.md` for integration patterns
- **System Architecture Diagrams**: See `SYSTEM_ARCHITECTURE_DIAGRAMS.md` for visual diagrams
- **API Design**: See `API_DESIGN_PROPOSAL.md` for API endpoint specifications

---

*Production-ready system design combining visual blocks/triggers with semantic routing and intelligent tool selection. UI patterns inspired by OpenMetadata (connector management) and ShaderFrog (visual composition).*

