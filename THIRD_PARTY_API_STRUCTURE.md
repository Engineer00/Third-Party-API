# Third-Party API Integration Structure

## Overview

This document defines the complete structure for integrating third-party APIs into the production system, combining visual blocks, semantic routing, and intelligent tool selection.

---

## Table of Contents

1. [API Integration Architecture](#api-integration-architecture)
2. [Connector Structure](#connector-structure)
3. [Route Map Structure](#route-map-structure)
4. [Tool Wrapper Structure](#tool-wrapper-structure)
5. [Credential Structure](#credential-structure)
6. [API Client Structure](#api-client-structure)
7. [Error Handling Structure](#error-handling-structure)
8. [Rate Limiting Structure](#rate-limiting-structure)

---

## API Integration Architecture

### Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Integration Layer (Blocks)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Service-     │  │ Generic      │  │ OpenAPI      │ │
│  │ Specific     │  │ HTTP Tool    │  │ Integration  │ │
│  │ Blocks       │  │              │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
┌──────────────────────────▼──────────────────────────────┐
│           Connector Layer (Semantic Routing)            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Connector    │  │ Route Map    │  │ Tool Wrapper │ │
│  │ Registry     │  │ Manager      │  │ Manager      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
┌──────────────────────────▼──────────────────────────────┐
│              API Client Layer (Execution)               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ OAuth        │  │ HTTP Client  │  │ Webhook      │ │
│  │ Handler      │  │ (with Retry) │  │ Handler      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
┌──────────────────────────▼──────────────────────────────┐
│              External Services                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Google APIs  │  │ Slack API    │  │ GitHub API   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Connector Structure

### TypeScript Interface

```typescript
// tools/connectors/types.ts

export interface ConnectorConfig {
  // Basic Information
  id: string                    // Unique identifier (e.g., 'google_calendar')
  name: string                  // Display name (e.g., 'Google Calendar')
  provider: string              // Provider name (e.g., 'google')
  version: string               // Version (e.g., '1.0.0')
  description: string           // Description
  icon?: string                 // Icon URL or name
  category: ConnectorCategory   // Category
  
  // Authentication
  authType: AuthType            // 'oauth2' | 'api_key' | 'bearer' | 'basic'
  authConfig: AuthConfig        // Authentication configuration
  
  // API Configuration
  baseUrl: string               // Base API URL
  apiVersion?: string           // API version (e.g., 'v1')
  endpoints: Record<string, EndpointConfig>  // API endpoints
  
  // Semantic Routing
  semanticRouting?: SemanticRoutingConfig
  
  // Tool Wrapper
  toolWrapper?: ToolWrapperConfig
  
  // Production Features
  rateLimit?: RateLimitConfig
  retry?: RetryConfig
  circuitBreaker?: CircuitBreakerConfig
  cache?: CacheConfig
  
  // Documentation
  documentation?: string
  setupInstructions?: string[]
  examples?: ConnectorExample[]
  
  // Health Check
  healthCheck?: () => Promise<boolean>
}

export enum ConnectorCategory {
  COMMUNICATION = 'communication',    // Slack, Teams, Email
  PRODUCTIVITY = 'productivity',      // Google Workspace, Office 365
  DEVELOPMENT = 'development',        // GitHub, GitLab, Jira
  DATA = 'data',                      // Databases, Data stores
  AI_ML = 'ai_ml',                    // OpenAI, Anthropic
  MARKETING = 'marketing',            // HubSpot, Mailchimp
  PAYMENT = 'payment',                // Stripe, PayPal
  STORAGE = 'storage',                // S3, Dropbox
  CUSTOM = 'custom'                   // Custom APIs
}

export enum AuthType {
  OAUTH2 = 'oauth2',
  API_KEY = 'api_key',
  BEARER = 'bearer',
  BASIC = 'basic',
  CUSTOM = 'custom'
}

export interface AuthConfig {
  // OAuth2
  authorizationUrl?: string
  tokenUrl?: string
  clientId?: string
  clientSecret?: string
  scopes?: string[]
  redirectUri?: string
  
  // API Key
  apiKeyLocation?: 'header' | 'query' | 'body'
  apiKeyName?: string
  
  // Bearer Token
  tokenHeader?: string
  
  // Basic Auth
  usernameField?: string
  passwordField?: string
}

export interface EndpointConfig {
  path: string                    // Endpoint path (e.g., '/events')
  method: HttpMethod              // 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  description?: string
  parameters?: ParameterConfig[]
  requestBody?: RequestBodyConfig
  responseSchema?: JSONSchema
  examples?: EndpointExample[]
}

export interface ParameterConfig {
  name: string
  type: ParameterType
  location: 'path' | 'query' | 'header' | 'body'
  required?: boolean
  description?: string
  default?: any
  schema?: JSONSchema
}

export type ParameterType = 
  | 'string' 
  | 'number' 
  | 'boolean' 
  | 'array' 
  | 'object' 
  | 'date' 
  | 'file'

export interface RequestBodyConfig {
  contentType: 'json' | 'form' | 'multipart' | 'raw'
  schema: JSONSchema
  required?: boolean
}

export interface SemanticRoutingConfig {
  enabled: boolean
  routeMapPath?: string           // Path to route map JSON
  utterances?: string[]           // Keywords for semantic matching
  confidenceThreshold?: number    // Minimum confidence (default: 0.7)
  fallbackTool?: string           // Fallback tool if routing fails
}

export interface ToolWrapperConfig {
  enabled: boolean
  crewName?: string               // CrewAI crew name
  agentRole?: string              // Agent role description
  agentGoal?: string              // Agent goal
  agentBackstory?: string         // Agent backstory
  llmProvider?: string            // LLM provider (default: OpenAI)
  llmModel?: string               // LLM model (default: gpt-4)
}

export interface RateLimitConfig {
  requests: number                // Number of requests
  window: number                  // Time window in seconds
  strategy?: 'fixed' | 'sliding' // Rate limit strategy
}

export interface RetryConfig {
  enabled: boolean
  maxAttempts: number
  backoff: 'exponential' | 'linear' | 'fixed'
  initialDelay: number           // Milliseconds
  maxDelay?: number              // Maximum delay
  retryableErrors?: number[]     // HTTP status codes to retry
}

export interface CircuitBreakerConfig {
  enabled: boolean
  failureThreshold: number       // Failures before opening
  successThreshold?: number      // Successes before closing
  timeout: number                // Timeout in milliseconds
  resetTimeout: number           // Reset timeout in milliseconds
}

export interface CacheConfig {
  enabled: boolean
  ttl: number                    // Time to live in seconds
  keyGenerator?: (config: any) => string
  invalidateOn?: string[]        // Events that invalidate cache
}
```

### Example Connector: Google Calendar

```typescript
// tools/connectors/google/calendar.ts

export const GoogleCalendarConnector: ConnectorConfig = {
  id: 'google_calendar',
  name: 'Google Calendar',
  provider: 'google',
  version: '1.0.0',
  description: 'Integrate with Google Calendar API to manage events',
  icon: '📅',
  category: ConnectorCategory.PRODUCTIVITY,
  
  // OAuth2 Authentication
  authType: AuthType.OAUTH2,
  authConfig: {
    authorizationUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    tokenUrl: 'https://oauth2.googleapis.com/token',
    scopes: [
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/calendar.events'
    ],
    redirectUri: process.env.GOOGLE_REDIRECT_URI!
  },
  
  // API Configuration
  baseUrl: 'https://www.googleapis.com/calendar/v3',
  apiVersion: 'v3',
  
  endpoints: {
    listEvents: {
      path: '/calendars/{calendarId}/events',
      method: 'GET',
      description: 'List events from a calendar',
      parameters: [
        {
          name: 'calendarId',
          type: 'string',
          location: 'path',
          required: true,
          description: 'Calendar identifier'
        },
        {
          name: 'timeMin',
          type: 'date',
          location: 'query',
          required: false,
          description: 'Lower bound for event start time'
        },
        {
          name: 'timeMax',
          type: 'date',
          location: 'query',
          required: false,
          description: 'Upper bound for event end time'
        },
        {
          name: 'maxResults',
          type: 'number',
          location: 'query',
          required: false,
          default: 10,
          description: 'Maximum number of events to return'
        }
      ],
      responseSchema: {
        type: 'object',
        properties: {
          items: {
            type: 'array',
            items: { $ref: '#/definitions/Event' }
          }
        }
      }
    },
    
    createEvent: {
      path: '/calendars/{calendarId}/events',
      method: 'POST',
      description: 'Create a new calendar event',
      parameters: [
        {
          name: 'calendarId',
          type: 'string',
          location: 'path',
          required: true,
          default: 'primary'
        }
      ],
      requestBody: {
        contentType: 'json',
        schema: {
          type: 'object',
          required: ['summary', 'start', 'end'],
          properties: {
            summary: { type: 'string' },
            description: { type: 'string' },
            start: {
              type: 'object',
              properties: {
                dateTime: { type: 'string', format: 'date-time' },
                timeZone: { type: 'string' }
              }
            },
            end: {
              type: 'object',
              properties: {
                dateTime: { type: 'string', format: 'date-time' },
                timeZone: { type: 'string' }
              }
            }
          }
        }
      }
    },
    
    updateEvent: {
      path: '/calendars/{calendarId}/events/{eventId}',
      method: 'PUT',
      description: 'Update an existing calendar event'
    },
    
    deleteEvent: {
      path: '/calendars/{calendarId}/events/{eventId}',
      method: 'DELETE',
      description: 'Delete a calendar event'
    }
  },
  
  // Semantic Routing
  semanticRouting: {
    enabled: true,
    routeMapPath: './tools/route-maps/google-calendar.json',
    utterances: [
      'calendar', 'event', 'meeting', 'schedule', 'appointment',
      'book', 'reserve', 'create meeting', 'add event'
    ],
    confidenceThreshold: 0.7
  },
  
  // Tool Wrapper
  toolWrapper: {
    enabled: true,
    crewName: 'Google Calendar Agent',
    agentRole: 'Calendar Management Specialist',
    agentGoal: 'Help users manage their Google Calendar events efficiently',
    agentBackstory: 'You are an expert at managing calendar events and scheduling',
    llmProvider: 'openai',
    llmModel: 'gpt-4'
  },
  
  // Production Features
  rateLimit: {
    requests: 100,
    window: 60,
    strategy: 'sliding'
  },
  
  retry: {
    enabled: true,
    maxAttempts: 3,
    backoff: 'exponential',
    initialDelay: 1000,
    maxDelay: 10000,
    retryableErrors: [429, 500, 502, 503, 504]
  },
  
  circuitBreaker: {
    enabled: true,
    failureThreshold: 5,
    successThreshold: 2,
    timeout: 30000,
    resetTimeout: 60000
  },
  
  cache: {
    enabled: true,
    ttl: 300, // 5 minutes
    keyGenerator: (config) => `calendar:${config.calendarId}:${config.endpoint}`
  },
  
  // Documentation
  documentation: 'https://developers.google.com/calendar/api',
  setupInstructions: [
    '1. Go to Google Cloud Console',
    '2. Create a new project or select existing',
    '3. Enable Google Calendar API',
    '4. Create OAuth 2.0 credentials',
    '5. Add authorized redirect URI',
    '6. Copy Client ID and Client Secret',
    '7. Connect in the application'
  ],
  
  examples: [
    {
      name: 'List Today\'s Events',
      description: 'Get all events scheduled for today',
      config: {
        endpoint: 'listEvents',
        calendarId: 'primary',
        timeMin: '2025-01-01T00:00:00Z',
        timeMax: '2025-01-01T23:59:59Z'
      }
    }
  ],
  
  // Health Check
  healthCheck: async () => {
    // Verify API is accessible
    try {
      const response = await fetch('https://www.googleapis.com/calendar/v3/users/me/calendarList')
      return response.ok
    } catch {
      return false
    }
  }
}
```

---

## Route Map Structure

### JSON Schema

```typescript
// tools/route-maps/types.ts

export interface RouteMap {
  connector: string                    // Connector ID
  version: string                      // Route map version
  routes: RouteDefinition[]
  modifiers?: ModifierDefinition[]
}

export interface RouteDefinition {
  tool: string                         // Tool/endpoint name
  name: string                         // Route name (used in semantic router)
  flow?: string                        // Flow name (optional grouping)
  utterances: string[]                 // Keywords/phrases for matching
  modifierFunc?: string                // Modifier function name (optional)
  examples?: string[]                  // Example queries
  confidence?: number                  // Minimum confidence (optional)
}

export interface ModifierDefinition {
  name: string                         // Modifier function name
  type: 'codes' | 'custom'            // Modifier type
  data?: any                           // Modifier data (e.g., codes list)
  generator?: string                   // Code generator function
}
```

### Example Route Map: Google Suite

```json
// tools/route-maps/google-suite.json
{
  "connector": "google_suite",
  "version": "1.0.0",
  "routes": [
    {
      "tool": "gmail_send",
      "name": "EMAIL_MANAGEMENT_FLOW",
      "flow": "GOOGLE_SUITE",
      "utterances": [
        "email",
        "send",
        "inbox",
        "message",
        "reply",
        "forward",
        "gmail",
        "compose",
        "draft",
        "send email",
        "reply to email",
        "forward email"
      ],
      "examples": [
        "Send an email to john@example.com",
        "Reply to the latest email",
        "Forward this message to my team"
      ]
    },
    {
      "tool": "calendar_create",
      "name": "EVENT_MANAGEMENT_FLOW",
      "flow": "GOOGLE_SUITE",
      "utterances": [
        "meeting",
        "schedule",
        "calendar",
        "appointment",
        "event",
        "book",
        "reserve",
        "create meeting",
        "add event",
        "schedule meeting"
      ],
      "examples": [
        "Schedule a meeting for tomorrow at 2pm",
        "Create a calendar event",
        "Book an appointment"
      ]
    },
    {
      "tool": "drive_upload",
      "name": "DRIVE_MANAGEMENT_FLOW",
      "flow": "GOOGLE_SUITE",
      "utterances": [
        "file",
        "folder",
        "document",
        "share",
        "upload",
        "download",
        "google drive",
        "create folder",
        "move file"
      ],
      "examples": [
        "Upload a file to Google Drive",
        "Share a document with my team",
        "Create a new folder"
      ]
    }
  ],
  "modifiers": [
    {
      "name": "naics_codes",
      "type": "codes",
      "generator": "generateNaicsCodes"
    }
  ]
}
```

---

## Tool Wrapper Structure

### TypeScript Interface

```typescript
// tools/wrappers/types.ts

export interface ToolWrapper {
  connectorId: string
  connector: ConnectorConfig
  crew: CrewAI.Crew
  tools: CrewAI.Tool[]
  agent: CrewAI.Agent
}

export class ToolWrapperManager {
  private wrappers = new Map<string, ToolWrapper>()
  
  async createWrapper(
    connector: ConnectorConfig
  ): Promise<ToolWrapper> {
    if (!connector.toolWrapper?.enabled) {
      throw new Error('Tool wrapper not enabled for connector')
    }
    
    // Create tools from connector endpoints
    const tools = await this.createTools(connector)
    
    // Create agent
    const agent = new CrewAI.Agent({
      role: connector.toolWrapper.agentRole || `${connector.name} Agent`,
      goal: connector.toolWrapper.agentGoal || 
        `Execute ${connector.name} operations efficiently`,
      backstory: connector.toolWrapper.agentBackstory || 
        `You are an expert at using ${connector.name} API`,
      tools: tools,
      llm: this.getLLM(connector.toolWrapper),
      verbose: true
    })
    
    // Create crew
    const crew = new CrewAI.Crew({
      agents: [agent],
      tasks: [],
      process: CrewAI.Process.sequential
    })
    
    const wrapper: ToolWrapper = {
      connectorId: connector.id,
      connector,
      crew,
      tools,
      agent
    }
    
    this.wrappers.set(connector.id, wrapper)
    return wrapper
  }
  
  private async createTools(
    connector: ConnectorConfig
  ): Promise<CrewAI.Tool[]> {
    return Object.entries(connector.endpoints).map(([name, endpoint]) => {
      return new CrewAI.Tool({
        name: `${connector.id}_${name}`,
        description: endpoint.description || 
          `Call ${connector.name} ${name} endpoint`,
        func: async (params: any) => {
          return this.executeEndpoint(connector, name, params)
        }
      })
    })
  }
  
  private async executeEndpoint(
    connector: ConnectorConfig,
    endpointName: string,
    params: any
  ): Promise<any> {
    const endpoint = connector.endpoints[endpointName]
    const client = await this.getClient(connector)
    
    // Execute with production features
    return this.executeWithRetry(
      () => client.call(endpoint, params),
      connector.retry
    )
  }
}
```

---

## Credential Structure

### TypeScript Interface

```typescript
// lib/credentials/types.ts

export interface Credential {
  id: string
  userId: string
  workspaceId?: string
  type: string                    // Credential type (e.g., 'google-oauth2')
  provider: string                // Provider (e.g., 'google')
  status: CredentialStatus
  encryptedData: EncryptedCredentialData
  metadata: CredentialMetadata
  createdAt: Date
  updatedAt: Date
}

export enum CredentialStatus {
  ACTIVE = 'active',
  EXPIRED = 'expired',
  ERROR = 'error',
  REVOKED = 'revoked'
}

export interface EncryptedCredentialData {
  encrypted: Buffer
  keyId: string
  algorithm: string
  iv?: Buffer
}

export interface CredentialMetadata {
  scopes?: string[]               // OAuth scopes
  expiresAt?: Date               // Token expiration
  refreshToken?: string           // Encrypted refresh token
  lastUsedAt?: Date
  usageCount?: number
}

// OAuth2 Credential
export interface OAuth2CredentialData {
  accessToken: string
  refreshToken?: string
  expiresAt?: Date
  tokenType?: string
  scope?: string
}

// API Key Credential
export interface ApiKeyCredentialData {
  apiKey: string
  location: 'header' | 'query'
  headerName?: string
}

// Bearer Token Credential
export interface BearerTokenCredentialData {
  token: string
  headerName?: string
}
```

---

## API Client Structure

### TypeScript Interface

```typescript
// lib/api-client/types.ts

export interface APIClient {
  baseUrl: string
  auth: AuthMethod
  rateLimit?: RateLimiter
  retry?: RetryHandler
  circuitBreaker?: CircuitBreaker
  cache?: Cache
}

export interface AuthMethod {
  type: AuthType
  credentials: any
  getHeaders(): Promise<Record<string, string>>
  refresh?(): Promise<void>
}

export class HTTPAPIClient implements APIClient {
  constructor(
    public baseUrl: string,
    public auth: AuthMethod,
    public rateLimit?: RateLimiter,
    public retry?: RetryHandler,
    public circuitBreaker?: CircuitBreaker,
    public cache?: Cache
  ) {}
  
  async call(
    endpoint: EndpointConfig,
    params: any
  ): Promise<any> {
    // 1. Check circuit breaker
    if (this.circuitBreaker?.isOpen()) {
      throw new CircuitBreakerOpenError()
    }
    
    // 2. Check rate limit
    if (this.rateLimit) {
      await this.rateLimit.checkLimit()
    }
    
    // 3. Check cache
    if (this.cache) {
      const cached = await this.cache.get(endpoint.path, params)
      if (cached) return cached
    }
    
    // 4. Build request
    const url = this.buildUrl(endpoint, params)
    const headers = await this.auth.getHeaders()
    const body = this.buildBody(endpoint, params)
    
    // 5. Execute with retry
    const response = await this.executeWithRetry(
      () => fetch(url, {
        method: endpoint.method,
        headers,
        body
      })
    )
    
    // 6. Parse response
    const data = await response.json()
    
    // 7. Cache result
    if (this.cache && response.ok) {
      await this.cache.set(endpoint.path, params, data)
    }
    
    // 8. Update circuit breaker
    if (response.ok) {
      this.circuitBreaker?.recordSuccess()
    } else {
      this.circuitBreaker?.recordFailure()
    }
    
    return data
  }
}
```

---

## Error Handling Structure

### Error Types

```typescript
// lib/errors/types.ts

export class APIError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number,
    public details?: any
  ) {
    super(message)
    this.name = 'APIError'
  }
}

export class RateLimitError extends APIError {
  constructor(public retryAfter?: number) {
    super(
      'Rate limit exceeded',
      'RATE_LIMIT_EXCEEDED',
      429,
      { retryAfter }
    )
  }
}

export class CircuitBreakerOpenError extends APIError {
  constructor() {
    super(
      'Circuit breaker is open',
      'CIRCUIT_BREAKER_OPEN',
      503
    )
  }
}

export class AuthenticationError extends APIError {
  constructor(message: string = 'Authentication failed') {
    super(message, 'AUTHENTICATION_ERROR', 401)
  }
}

export class ValidationError extends APIError {
  constructor(message: string, details?: any) {
    super(message, 'VALIDATION_ERROR', 400, details)
  }
}
```

---

## Rate Limiting Structure

### Rate Limiter Implementation

```typescript
// lib/rate-limiting/types.ts

export interface RateLimiter {
  checkLimit(key: string, limit: number, window: number): Promise<boolean>
  getRemaining(key: string): Promise<number>
  getResetTime(key: string): Promise<Date>
}

export class RedisRateLimiter implements RateLimiter {
  constructor(private redis: Redis) {}
  
  async checkLimit(
    key: string,
    limit: number,
    window: number
  ): Promise<boolean> {
    const redisKey = `ratelimit:${key}`
    const now = Date.now()
    
    // Use sliding window log algorithm
    const pipeline = this.redis.pipeline()
    pipeline.zremrangebyscore(redisKey, 0, now - window * 1000)
    pipeline.zcard(redisKey)
    pipeline.zadd(redisKey, now, `${now}-${Math.random()}`)
    pipeline.expire(redisKey, window)
    
    const results = await pipeline.exec()
    const count = results[1][1] as number
    
    return count < limit
  }
}
```

---

## Summary

This structure provides:

1. **Standardized Connector Format**: Consistent structure for all API integrations
2. **Semantic Routing**: Intelligent tool selection based on user queries
3. **Tool Wrapping**: CrewAI-style tool wrapping for AI-powered execution
4. **Production Features**: Rate limiting, retry, circuit breakers, caching
5. **Type Safety**: Full TypeScript support with interfaces
6. **Extensibility**: Easy to add new connectors

---



