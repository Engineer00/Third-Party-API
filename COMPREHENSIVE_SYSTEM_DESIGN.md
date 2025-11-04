# Comprehensive System Design: Blocks, Triggers, and Third-Party API Integration

## Executive Summary

This document provides a complete blueprint for building a CrewAI-like visual workflow system with blocks, triggers, and third-party API integrations. It synthesizes insights from Sim, Flowise, Flojoy, ShaderFrog, OpenMetadata, and industry best practices.

---

## Table of Contents

1. [What Does "Emulating These Repos" Mean?](#what-does-emulating-these-repos-mean)
2. [Complete System Architecture](#complete-system-architecture)
3. [Third-Party API Integration Structure](#third-party-api-integration-structure)
4. [Industry Best Practices](#industry-best-practices)
5. [Implementation Roadmap](#implementation-roadmap)
6. [Repository Summaries](#repository-summaries)
7. [Visual Patterns from ShaderFrog & OpenMetadata](#visual-patterns-from-shaderfrog--openmetadata)

---

### Key Components

#### 1. **Visual Flow Editor** (from Sim, Flowise, Flojoy)
- **ReactFlow-based**: Node-based visual programming interface
- **Drag-and-Drop**: Intuitive block placement and connection
- **Real-time Preview**: See workflow structure as you build
- **Connection Validation**: Type-safe block connections

#### 2. **Block System** (from Sim, Flowise, Flojoy)
- **Registry Pattern**: Centralized block definitions
- **Categorized Blocks**: Organize by function (AI, Data, APIs, etc.)
- **Configurable Properties**: Each block has configurable inputs/outputs
- **Sub-blocks**: Complex blocks with nested configuration

#### 3. **Trigger System** (from Sim)
- **Event-Driven**: Webhooks, polling, schedules
- **Provider-Specific**: Slack, Gmail, GitHub, etc.
- **OAuth Integration**: Secure credential management
- **Real-time Execution**: Trigger workflows automatically

#### 4. **Third-Party API Integration** (from Sim, Flowise, OpenMetadata)
- **Connector Pattern**: Standardized integration architecture
- **OAuth 2.0 Support**: Secure authentication
- **Generic HTTP Tools**: Flexible API integration
- **Service-Specific Blocks**: Optimized for popular services

#### 5. **State Management** (from Sim, Flojoy)
- **Zustand Stores**: Lightweight state management
- **Workflow Serialization**: Save/load workflows
- **Real-time Collaboration**: Multiple users editing

---

## Complete System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React + Next.js)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Flow Editor  │  │ Block Panel │  │ Trigger Config│       │
│  │ (ReactFlow)  │  │   (Sidebar)  │  │    (Modal)    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         │                 │                   │               │
│         └─────────────────┴───────────────────┘               │
│                            │                                   │
│                    ┌───────▼────────┐                         │
│                    │  State Store    │                         │
│                    │   (Zustand)     │                         │
│                    └───────┬────────┘                         │
└────────────────────────────┼──────────────────────────────────┘
                              │
┌─────────────────────────────┼──────────────────────────────────┐
│                      Backend API (Next.js/Express)             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Workflows    │  │   Blocks     │  │  Triggers     │       │
│  │   API        │  │   Registry   │  │  Registry     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         │                 │                   │               │
│         └─────────────────┴───────────────────┘               │
│                            │                                   │
│                    ┌───────▼────────┐                         │
│                    │  Execution     │                         │
│                    │   Engine       │                         │
│                    └───────┬────────┘                         │
│                            │                                   │
│  ┌─────────────────────────┼─────────────────────────┐       │
│  │                         │                         │       │
│  ┌──────────▼──────┐ ┌────▼──────┐ ┌──────▼──────┐ │       │
│  │  Credentials    │ │  Webhooks  │ │  Scheduler  │ │       │
│  │   Manager       │ │  Handler   │ │  Service    │ │       │
│  └─────────────────┘ └────────────┘ └─────────────┘ │       │
└─────────────────────────────┼──────────────────────────────────┘
                                │
┌───────────────────────────────┼──────────────────────────────────┐
│                      Database & Services                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ PostgreSQL   │  │   Redis      │  │  Queue        │         │
│  │ (Workflows)  │  │  (Cache)     │  │  (Jobs)       │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└──────────────────────────────────────────────────────────────────┘
```

### Folder Structure

```
project-root/
├── apps/
│   ├── web/                          # Next.js frontend
│   │   ├── app/
│   │   │   ├── api/                  # API routes
│   │   │   │   ├── v1/
│   │   │   │   │   ├── workflows/
│   │   │   │   │   ├── blocks/
│   │   │   │   │   ├── triggers/
│   │   │   │   │   ├── executions/
│   │   │   │   │   ├── credentials/
│   │   │   │   │   └── webhooks/
│   │   │   │   └── middleware/
│   │   │   ├── workspace/
│   │   │   │   └── [workspaceId]/
│   │   │   │       └── workflows/
│   │   │   │           └── [workflowId]/
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── blocks/               # Block UI components
│   │   │   │   ├── WorkflowBlock.tsx
│   │   │   │   ├── ConnectionBlocks.tsx
│   │   │   │   └── SubBlock.tsx
│   │   │   ├── edges/
│   │   │   │   └── WorkflowEdge.tsx
│   │   │   ├── panels/
│   │   │   │   ├── BlockConfigPanel.tsx
│   │   │   │   └── TriggerConfigModal.tsx
│   │   │   └── canvas/
│   │   │       └── FlowEditor.tsx
│   │   ├── blocks/                   # Block definitions
│   │   │   ├── registry.ts
│   │   │   ├── types.ts
│   │   │   ├── blocks/               # Individual block types
│   │   │   │   ├── agent/
│   │   │   │   ├── api/
│   │   │   │   ├── condition/
│   │   │   │   ├── http/
│   │   │   │   └── ...
│   │   │   └── utils.ts
│   │   ├── triggers/                  # Trigger definitions
│   │   │   ├── index.ts              # Trigger registry
│   │   │   ├── types.ts
│   │   │   ├── webhook/              # Webhook triggers
│   │   │   ├── polling/              # Polling triggers
│   │   │   └── schedule/             # Schedule triggers
│   │   ├── tools/                    # Tool definitions (3rd party APIs)
│   │   │   ├── registry.ts
│   │   │   ├── types.ts
│   │   │   ├── google/               # Google integrations
│   │   │   ├── slack/                # Slack integration
│   │   │   ├── http/                 # Generic HTTP tools
│   │   │   └── ...
│   │   ├── stores/                   # Zustand stores
│   │   │   ├── workflow.ts
│   │   │   ├── blocks.ts
│   │   │   ├── triggers.ts
│   │   │   └── execution.ts
│   │   ├── lib/
│   │   │   ├── validation/           # Zod schemas
│   │   │   ├── execution/            # Workflow execution
│   │   │   ├── webhooks/             # Webhook handling
│   │   │   └── oauth/                # OAuth flows
│   │   └── types/
│   │       └── api.ts
│   │
│   └── executor/                     # Workflow execution service
│       ├── handlers/                 # Block execution handlers
│       ├── routing/                  # Workflow routing logic
│       └── utils/
│
├── packages/
│   ├── db/                           # Database schema & migrations
│   │   ├── schema/
│   │   │   ├── workflows.ts
│   │   │   ├── blocks.ts
│   │   │   ├── triggers.ts
│   │   │   └── credentials.ts
│   │   └── migrations/
│   │
│   ├── shared/                       # Shared types & utilities
│   │   ├── types/
│   │   └── utils/
│   │
│   └── ui/                           # Shared UI components
│       └── components/
│
├── docker-compose.yml
├── package.json
├── turbo.json                        # Turborepo config
└── README.md
```

### Core Components

#### 1. **Block System**

```typescript
// blocks/types.ts
export interface BlockConfig {
  id: string
  name: string
  category: 'ai' | 'data' | 'api' | 'logic' | 'trigger' | 'tool'
  icon?: string
  description: string
  version: string
  
  // Block structure
  inputs: BlockInput[]
  outputs: BlockOutput[]
  
  // Configuration
  configFields: Record<string, BlockConfigField>
  
  // Execution
  execute: (config: BlockExecutionConfig) => Promise<BlockOutput>
  
  // UI
  component?: React.ComponentType<BlockComponentProps>
  
  // Metadata
  tags?: string[]
  documentation?: string
}

export interface BlockInput {
  id: string
  name: string
  type: 'string' | 'number' | 'boolean' | 'object' | 'array' | 'any'
  required?: boolean
  description?: string
  defaultValue?: any
}

export interface BlockOutput {
  id: string
  name: string
  type: 'string' | 'number' | 'boolean' | 'object' | 'array' | 'any'
  description?: string
}

// blocks/registry.ts
export const BLOCK_REGISTRY: Record<string, BlockConfig> = {
  agent: AgentBlock,
  api: ApiBlock,
  condition: ConditionBlock,
  http_request: HttpRequestBlock,
  slack_message: SlackMessageBlock,
  // ... more blocks
}
```

#### 2. **Trigger System**

```typescript
// triggers/types.ts
export interface TriggerConfig {
  id: string
  name: string
  provider: string
  description: string
  version: string
  icon?: string
  
  // Trigger type
  type: 'webhook' | 'polling' | 'schedule' | 'manual'
  
  // Configuration
  configFields: Record<string, TriggerConfigField>
  
  // Output schema
  outputs: Record<string, TriggerOutput>
  
  // Authentication
  requiresCredentials?: boolean
  credentialProvider?: string
  requiredScopes?: string[]
  
  // Webhook-specific
  webhook?: {
    method?: 'POST' | 'GET' | 'PUT' | 'DELETE'
    headers?: Record<string, string>
    verifySignature?: boolean
  }
  
  // Polling-specific
  polling?: {
    interval: number // seconds
    maxItems?: number
  }
  
  // Schedule-specific
  schedule?: {
    cronExpression: string
    timezone?: string
  }
  
  // Instructions for setup
  instructions: string[]
  samplePayload?: any
}

// triggers/index.ts
export const TRIGGER_REGISTRY: TriggerRegistry = {
  slack_webhook: slackWebhookTrigger,
  gmail_poller: gmailPollingTrigger,
  schedule: scheduleTrigger,
  generic_webhook: genericWebhookTrigger,
  // ... more triggers
}
```

#### 3. **Workflow Execution Engine**

```typescript
// lib/execution/workflow-executor.ts
export interface WorkflowExecutor {
  execute(workflow: WorkflowState, input?: any): Promise<ExecutionResult>
  
  // Execute single block
  executeBlock(
    block: BlockInstance,
    context: ExecutionContext
  ): Promise<BlockOutput>
  
  // Handle triggers
  handleTrigger(
    trigger: TriggerInstance,
    payload: any
  ): Promise<WorkflowExecution>
  
  // Route workflow execution
  routeExecution(
    workflow: WorkflowState,
    startBlockId: string
  ): Promise<ExecutionPath>
}
```

---

## Third-Party API Integration Structure

### Integration Architecture

Third-party API integration follows a **three-layer architecture**:

```
┌─────────────────────────────────────────────────────────┐
│                    Integration Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Connectors  │  │   Credentials│  │   Tools       │   │
│  │  (Registry)  │  │   Manager    │  │   (Blocks)    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────┐
│                    API Client Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  OAuth       │  │   HTTP       │  │   Webhooks   │   │
│  │  Handler     │  │   Client     │  │   Handler    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└───────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────┐
│                    External Services                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Google     │  │   Slack      │  │   GitHub     │   │
│  │   APIs       │  │   API        │  │   API        │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└───────────────────────────────────────────────────────────┘
```

### Connector Pattern (Inspired by OpenMetadata)

#### 1. **Connector Registry**

```typescript
// tools/registry.ts
export interface ConnectorConfig {
  id: string
  name: string
  provider: string
  version: string
  description: string
  icon?: string
  
  // Authentication
  authType: 'oauth2' | 'api_key' | 'bearer' | 'basic' | 'custom'
  authConfig: ConnectorAuthConfig
  
  // API endpoints
  baseUrl: string
  endpoints: Record<string, EndpointConfig>
  
  // Rate limiting
  rateLimit?: {
    requests: number
    period: number // seconds
  }
  
  // Error handling
  retryConfig?: RetryConfig
  
  // Documentation
  documentation?: string
  setupInstructions?: string[]
}

export interface EndpointConfig {
  path: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  parameters?: ParameterConfig[]
  requestBody?: RequestBodyConfig
  responseSchema?: JSONSchema
  description?: string
}

export const CONNECTOR_REGISTRY: Record<string, ConnectorConfig> = {
  google_calendar: googleCalendarConnector,
  slack: slackConnector,
  github: githubConnector,
  // ... more connectors
}
```

#### 2. **Credential Management**

```typescript
// lib/credentials/credential-manager.ts
export interface Credential {
  id: string
  name: string
  type: string
  provider: string
  status: 'connected' | 'expired' | 'error'
  
  // Encrypted credential data
  data: EncryptedCredentialData
  
  // OAuth-specific
  accessToken?: string
  refreshToken?: string
  expiresAt?: Date
  scopes?: string[]
  
  // Metadata
  createdAt: Date
  updatedAt: Date
}

export interface CredentialManager {
  // Create credential
  createCredential(
    type: string,
    config: CredentialConfig
  ): Promise<Credential>
  
  // OAuth flow
  initiateOAuth(
    provider: string,
    scopes: string[]
  ): Promise<OAuthUrl>
  
  handleOAuthCallback(
    provider: string,
    code: string,
    state: string
  ): Promise<Credential>
  
  // Refresh token
  refreshToken(credentialId: string): Promise<Credential>
  
  // Get credential
  getCredential(credentialId: string): Promise<Credential>
  
  // Validate credential
  validateCredential(credentialId: string): Promise<boolean>
}
```

#### 3. **Tool/Block Implementation**

```typescript
// tools/google/calendar.ts
export const GoogleCalendarTool: BlockConfig = {
  id: 'google_calendar',
  name: 'Google Calendar',
  category: 'api',
  provider: 'google',
  description: 'Interact with Google Calendar API',
  
  // Requires OAuth credential
  requiresCredential: true,
  credentialType: 'google-oauth2',
  requiredScopes: ['calendar.readonly', 'calendar.events'],
  
  // Configuration fields
  configFields: {
    action: {
      type: 'select',
      label: 'Action',
      options: [
        { value: 'list_events', label: 'List Events' },
        { value: 'create_event', label: 'Create Event' },
        { value: 'update_event', label: 'Update Event' },
        { value: 'delete_event', label: 'Delete Event' }
      ],
      required: true
    },
    calendarId: {
      type: 'string',
      label: 'Calendar ID',
      placeholder: 'primary',
      defaultValue: 'primary'
    },
    // ... more fields based on action
  },
  
  // Execution
  async execute(config: BlockExecutionConfig) {
    const credential = await getCredential(config.credentialId)
    const client = new GoogleCalendarClient(credential)
    
    switch (config.action) {
      case 'list_events':
        return await client.listEvents(config.calendarId, config.options)
      case 'create_event':
        return await client.createEvent(config.calendarId, config.event)
      // ... other actions
    }
  }
}
```

#### 4. **Generic HTTP Tool**

```typescript
// tools/http/request.ts
export const HttpRequestTool: BlockConfig = {
  id: 'http_request',
  name: 'HTTP Request',
  category: 'api',
  description: 'Make HTTP requests to any API',
  
  configFields: {
    method: {
      type: 'select',
      label: 'Method',
      options: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
      defaultValue: 'GET'
    },
    url: {
      type: 'string',
      label: 'URL',
      required: true,
      placeholder: 'https://api.example.com/endpoint'
    },
    headers: {
      type: 'json',
      label: 'Headers',
      placeholder: '{"Authorization": "Bearer token"}'
    },
    body: {
      type: 'json',
      label: 'Body',
      show: { method: ['POST', 'PUT', 'PATCH'] }
    },
    queryParams: {
      type: 'json',
      label: 'Query Parameters',
      placeholder: '{"key": "value"}'
    },
    // Schema for LLM understanding
    queryParamsSchema: {
      type: 'code',
      label: 'Query Params Schema',
      description: 'JSON Schema describing available query parameters',
      optional: true
    }
  },
  
  async execute(config: BlockExecutionConfig) {
    const response = await fetch(config.url, {
      method: config.method,
      headers: config.headers,
      body: config.body ? JSON.stringify(config.body) : undefined
    })
    
    return {
      status: response.status,
      headers: Object.fromEntries(response.headers.entries()),
      body: await response.json()
    }
  }
}
```

### Integration Patterns

#### Pattern 1: **Service-Specific Blocks** (Best for Popular Services)

**When to Use**: For services with complex APIs (Google, Slack, GitHub)

**Structure**:
```
tools/
├── google/
│   ├── calendar.ts
│   ├── gmail.ts
│   ├── drive.ts
│   └── sheets.ts
├── slack/
│   ├── message.ts
│   ├── channel.ts
│   └── webhook.ts
└── github/
    ├── issue.ts
    ├── pull_request.ts
    └── webhook.ts
```

**Benefits**:
- Optimized for specific service
- Better UX (service-specific fields)
- Type-safe API calls
- Service-specific error handling

#### Pattern 2: **Generic HTTP Tool** (Best for Any API)

**When to Use**: For services without dedicated blocks or custom APIs

**Structure**:
```
tools/
└── http/
    ├── request.ts        # Main HTTP request tool
    └── openapi.ts        # OpenAPI spec integration
```

**Benefits**:
- Works with any REST API
- No code changes needed for new APIs
- Flexible configuration
- LLM can understand API via schemas

#### Pattern 3: **OpenAPI Integration** (Best for API Discovery)

**When to Use**: When API provides OpenAPI spec

**Structure**:
```
tools/
└── openapi/
    ├── loader.ts         # Load OpenAPI spec
    ├── generator.ts      # Generate blocks from spec
    └── executor.ts       # Execute OpenAPI requests
```

**Benefits**:
- Auto-generate blocks from OpenAPI spec
- Always up-to-date with API
- Comprehensive API coverage
- Schema validation

### Authentication Patterns

#### 1. **OAuth 2.0** (Most Common)

```typescript
// lib/oauth/oauth-handler.ts
export class OAuthHandler {
  async initiateOAuth(
    provider: string,
    scopes: string[],
    redirectUri: string
  ): Promise<string> {
    const config = getOAuthConfig(provider)
    const state = generateState()
    
    const params = new URLSearchParams({
      client_id: config.clientId,
      redirect_uri: redirectUri,
      response_type: 'code',
      scope: scopes.join(' '),
      state: state,
      access_type: 'offline', // For refresh tokens
      prompt: 'consent'
    })
    
    return `${config.authorizationUrl}?${params.toString()}`
  }
  
  async handleCallback(
    provider: string,
    code: string,
    state: string
  ): Promise<OAuthTokens> {
    const config = getOAuthConfig(provider)
    
    const response = await fetch(config.tokenUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        client_id: config.clientId,
        client_secret: config.clientSecret,
        code: code,
        grant_type: 'authorization_code',
        redirect_uri: config.redirectUri
      })
    })
    
    const tokens = await response.json()
    
    return {
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      expiresAt: new Date(Date.now() + tokens.expires_in * 1000),
      scope: tokens.scope
    }
  }
  
  async refreshToken(
    provider: string,
    refreshToken: string
  ): Promise<OAuthTokens> {
    const config = getOAuthConfig(provider)
    
    const response = await fetch(config.tokenUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        client_id: config.clientId,
        client_secret: config.clientSecret,
        refresh_token: refreshToken,
        grant_type: 'refresh_token'
      })
    })
    
    return await response.json()
  }
}
```

#### 2. **API Key Authentication**

```typescript
// lib/credentials/api-key-handler.ts
export interface ApiKeyCredential {
  apiKey: string
  headerName?: string  // Default: 'X-API-Key' or 'Authorization'
  location?: 'header' | 'query'  // Default: 'header'
}

export function createApiKeyAuth(
  credential: ApiKeyCredential
): RequestHeaders {
  const headers: Record<string, string> = {}
  
  if (credential.location === 'query') {
    return { queryParams: { [credential.headerName || 'api_key']: credential.apiKey } }
  }
  
  // Header location
  if (credential.headerName === 'Authorization') {
    headers['Authorization'] = `Bearer ${credential.apiKey}`
  } else {
    headers[credential.headerName || 'X-API-Key'] = credential.apiKey
  }
  
  return { headers }
}
```

#### 3. **Webhook Signature Verification**

```typescript
// lib/webhooks/signature-verification.ts
export async function verifyWebhookSignature(
  payload: string,
  signature: string,
  secret: string,
  algorithm: 'sha256' | 'sha1' = 'sha256'
): Promise<boolean> {
  const hmac = crypto.createHmac(algorithm, secret)
  hmac.update(payload)
  const expectedSignature = hmac.digest('hex')
  
  // For some providers (e.g., Stripe), signature is in format 'sha256=...'
  const cleanSignature = signature.replace(/^sha256=/, '')
  
  return crypto.timingSafeEqual(
    Buffer.from(cleanSignature),
    Buffer.from(expectedSignature)
  )
}
```

### API Structure

#### RESTful API Design

```typescript
// API Endpoints Structure

// 1. Connectors API
GET    /api/v1/connectors                    // List all connectors
GET    /api/v1/connectors/:id                 // Get connector details
GET    /api/v1/connectors/:id/endpoints       // List connector endpoints

// 2. Credentials API
GET    /api/v1/credentials                    // List user credentials
POST   /api/v1/credentials                    // Create credential
GET    /api/v1/credentials/:id                // Get credential
PUT    /api/v1/credentials/:id                // Update credential
DELETE /api/v1/credentials/:id                // Delete credential
GET    /api/v1/credentials/types              // List credential types

// 3. OAuth API
GET    /api/v1/oauth/:provider/authorize       // Initiate OAuth
GET    /api/v1/oauth/:provider/callback       // OAuth callback
POST   /api/v1/oauth/:provider/refresh        // Refresh token
GET    /api/v1/oauth/:provider/test           // Test connection

// 4. Tools/Blocks API
GET    /api/v1/tools                          // List all tools
GET    /api/v1/tools/:id                      // Get tool details
GET    /api/v1/tools/:id/test                 // Test tool execution

// 5. Webhooks API
POST   /api/v1/webhooks/:path                 // Receive webhook
GET    /api/v1/webhooks                       // List webhooks
POST   /api/v1/webhooks                       // Create webhook
DELETE /api/v1/webhooks/:id                   // Delete webhook
```

---

## Industry Best Practices

### 1. **Security Best Practices**

#### Credential Storage
```typescript
// ✅ DO: Encrypt credentials at rest
import { encrypt, decrypt } from 'lib/encryption'

async function storeCredential(credential: Credential) {
  const encrypted = await encrypt(JSON.stringify(credential.data), {
    keyId: process.env.ENCRYPTION_KEY_ID
  })
  
  await db.credentials.create({
    data: {
      id: credential.id,
      encryptedData: encrypted,
      // Never store plaintext secrets
    }
  })
}

// ✅ DO: Use environment variables for secrets
const config = {
  oauth: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET
    }
  }
}

// ❌ DON'T: Store secrets in code
const badConfig = {
  apiKey: 'sk-1234567890'  // NEVER DO THIS
}
```

#### Token Refresh
```typescript
// ✅ DO: Automatic token refresh before expiration
async function getValidToken(credential: Credential): Promise<string> {
  const expiresIn = credential.expiresAt.getTime() - Date.now()
  const bufferTime = 5 * 60 * 1000 // 5 minutes
  
  if (expiresIn < bufferTime) {
    const refreshed = await refreshOAuthToken(credential.id)
    return refreshed.accessToken
  }
  
  return credential.accessToken
}
```

#### Webhook Security
```typescript
// ✅ DO: Verify webhook signatures
export async function handleWebhook(
  path: string,
  payload: string,
  signature: string
) {
  const webhook = await getWebhookByPath(path)
  
  if (!webhook) {
    throw new Error('Webhook not found')
  }
  
  // Verify signature
  const isValid = await verifyWebhookSignature(
    payload,
    signature,
    webhook.secret
  )
  
  if (!isValid) {
    throw new Error('Invalid webhook signature')
  }
  
  // Process webhook
  return await processWebhook(webhook, JSON.parse(payload))
}
```

### 2. **Error Handling Best Practices**

```typescript
// ✅ DO: Comprehensive error handling
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

export async function executeWithRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const maxRetries = options.maxRetries || 3
  const backoff = options.backoff || 'exponential'
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      if (attempt === maxRetries) {
        throw error
      }
      
      // Exponential backoff
      const delay = Math.min(1000 * Math.pow(2, attempt), 10000)
      await sleep(delay)
    }
  }
  
  throw new Error('Max retries exceeded')
}

// ✅ DO: Rate limiting
export class RateLimiter {
  private requests = new Map<string, number[]>()
  
  async checkLimit(
    key: string,
    limit: number,
    window: number
  ): Promise<boolean> {
    const now = Date.now()
    const requests = this.requests.get(key) || []
    
    // Remove old requests outside window
    const recentRequests = requests.filter(
      time => now - time < window * 1000
    )
    
    if (recentRequests.length >= limit) {
      return false
    }
    
    recentRequests.push(now)
    this.requests.set(key, recentRequests)
    return true
  }
}
```

### 3. **User Experience Best Practices**

#### Clear Configuration UI
```typescript
// ✅ DO: Provide clear setup instructions
export const GoogleCalendarConnector: ConnectorConfig = {
  setupInstructions: [
    '1. Go to Google Cloud Console',
    '2. Create a new project or select existing',
    '3. Enable Google Calendar API',
    '4. Create OAuth 2.0 credentials',
    '5. Add authorized redirect URI: https://your-app.com/oauth/google/callback',
    '6. Copy Client ID and Client Secret',
    '7. Click "Connect" below and authorize the application'
  ],
  
  // Test connection button
  testConnection: async (credential: Credential) => {
    try {
      const client = new GoogleCalendarClient(credential)
      await client.listCalendars()
      return { success: true, message: 'Connection successful' }
    } catch (error) {
      return { 
        success: false, 
        message: error.message,
        help: 'Check your credentials and permissions'
      }
    }
  }
}
```

#### Sample Data & Examples
```typescript
// ✅ DO: Provide sample payloads
export const SlackWebhookTrigger: TriggerConfig = {
  samplePayload: {
    type: 'event_callback',
    event: {
      type: 'message',
      text: 'Hello, world!',
      user: 'U1234567890',
      channel: 'C1234567890',
      ts: '1234567890.123456'
    }
  },
  
  outputs: {
    message: {
      type: 'string',
      description: 'Message text',
      path: 'event.text'
    },
    userId: {
      type: 'string',
      description: 'User ID',
      path: 'event.user'
    },
    channelId: {
      type: 'string',
      description: 'Channel ID',
      path: 'event.channel'
    }
  }
}
```

### 4. **Developer Experience Best Practices**

#### Type Safety
```typescript
// ✅ DO: Full TypeScript support
export interface BlockExecutionConfig {
  blockId: string
  config: Record<string, any>
  inputs: Record<string, any>
  credentialId?: string
  context: ExecutionContext
}

export interface BlockOutput {
  [key: string]: any
}

export type BlockExecutor = (
  config: BlockExecutionConfig
) => Promise<BlockOutput>

// ✅ DO: Zod validation
import { z } from 'zod'

export const GoogleCalendarConfigSchema = z.object({
  action: z.enum(['list_events', 'create_event', 'update_event', 'delete_event']),
  calendarId: z.string().default('primary'),
  eventId: z.string().optional(),
  event: z.object({
    summary: z.string(),
    start: z.object({ dateTime: z.string() }),
    end: z.object({ dateTime: z.string() })
  }).optional()
})

export function validateConfig(config: unknown) {
  return GoogleCalendarConfigSchema.parse(config)
}
```

#### Documentation
```typescript
// ✅ DO: Comprehensive documentation
/**
 * Google Calendar Tool
 * 
 * Interact with Google Calendar API to manage events.
 * 
 * @example
 * ```json
 * {
 *   "action": "create_event",
 *   "calendarId": "primary",
 *   "event": {
 *     "summary": "Meeting",
 *     "start": { "dateTime": "2025-01-01T10:00:00Z" },
 *     "end": { "dateTime": "2025-01-01T11:00:00Z" }
 *   }
 * }
 * ```
 * 
 * @requires OAuth credential with `calendar` scope
 * @see https://developers.google.com/calendar/api
 */
export const GoogleCalendarTool: BlockConfig = {
  // ...
}
```

### 5. **Scalability Best Practices**

#### Connection Pooling
```typescript
// ✅ DO: Use connection pooling for HTTP clients
import { Agent } from 'undici'

export const httpClient = new Agent({
  connections: 100,
  pipelining: 10
})

// ✅ DO: Cache credentials and API responses
import { Redis } from 'ioredis'

const redis = new Redis(process.env.REDIS_URL)

export async function getCachedCredential(
  credentialId: string
): Promise<Credential | null> {
  const cached = await redis.get(`credential:${credentialId}`)
  if (cached) {
    return JSON.parse(cached)
  }
  
  const credential = await db.credentials.findUnique({
    where: { id: credentialId }
  })
  
  if (credential) {
    await redis.setex(
      `credential:${credentialId}`,
      300, // 5 minutes
      JSON.stringify(credential)
    )
  }
  
  return credential
}
```

#### Queue-Based Execution
```typescript
// ✅ DO: Use queues for async operations
import { Queue } from 'bullmq'

export const workflowQueue = new Queue('workflow-execution', {
  connection: {
    host: process.env.REDIS_HOST,
    port: parseInt(process.env.REDIS_PORT || '6379')
  }
})

export async function queueWorkflowExecution(
  workflowId: string,
  input: any
) {
  await workflowQueue.add('execute', {
    workflowId,
    input
  }, {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 2000
    }
  })
}
```

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)

1. **Project Setup**
   - Initialize monorepo (Turborepo)
   - Set up Next.js app
   - Configure TypeScript, ESLint, Prettier
   - Set up database (PostgreSQL + Drizzle)

2. **Core Components**
   - ReactFlow integration
   - Basic block component
   - Block registry system
   - State management (Zustand)

3. **Basic Blocks**
   - Input block
   - Output block
   - Condition block
   - HTTP request block

### Phase 2: Trigger System (Weeks 5-8)

1. **Trigger Infrastructure**
   - Trigger registry
   - Webhook handler
   - Scheduler service
   - Polling service

2. **Basic Triggers**
   - Manual trigger
   - Schedule trigger
   - Generic webhook trigger

3. **Webhook Management**
   - Webhook creation
   - Webhook verification
   - Webhook routing

### Phase 3: Credential Management (Weeks 9-12)

1. **Credential System**
   - Credential storage (encrypted)
   - Credential API
   - Credential UI

2. **OAuth Integration**
   - OAuth flow handler
   - Token refresh
   - Provider configs (Google, Slack, etc.)

3. **API Key Management**
   - API key storage
   - API key UI

### Phase 4: Third-Party Integrations (Weeks 13-20)

1. **Connector Framework**
   - Connector registry
   - Connector loader
   - Connector executor

2. **Popular Integrations**
   - Google (Calendar, Gmail, Drive, Sheets)
   - Slack (Messages, Webhooks)
   - GitHub (Issues, PRs, Webhooks)
   - HTTP request tool (generic)

3. **Integration UI**
   - Connector browser
   - Setup wizard
   - Test connection

### Phase 5: Advanced Features (Weeks 21-28)

1. **Workflow Execution**
   - Execution engine
   - Error handling
   - Retry logic
   - Logging

2. **Advanced Blocks**
   - Loop block
   - Parallel block
   - Sub-workflow block

3. **Collaboration**
   - Real-time sync (Socket.io)
   - Version control
   - Permissions

### Phase 6: Polish & Optimization (Weeks 29-32)

1. **Performance**
   - Connection pooling
   - Caching
   - Rate limiting
   - Queue optimization

2. **Documentation**
   - API documentation
   - User guides
   - Developer guides

3. **Testing**
   - Unit tests
   - Integration tests
   - E2E tests

---

## Repository Summaries

### Sim (`simstudioai/sim`)

**Purpose**: Build and deploy AI agent workflows visually

**Tech Stack**:
- Next.js (App Router)
- Bun runtime
- PostgreSQL with pgvector
- ReactFlow for visual editor
- Zustand for state management
- Socket.io for real-time
- Trigger.dev for background jobs

**Key Features**:
- 80+ blocks (AI, data, API, logic)
- 15+ triggers (webhooks, polling, schedules)
- OAuth integration
- Knowledge bases
- Real-time collaboration

**Architecture Highlights**:
- Monorepo structure
- Block registry system
- Trigger registry system
- Comprehensive API structure
- Webhook handling

**Best Practices**:
- Type-safe with TypeScript + Zod
- Encrypted credential storage
- Webhook signature verification
- Rate limiting
- Comprehensive error handling

### Flowise (`FlowiseAI/Flowise`)

**Purpose**: Build AI agents visually with LangChain

**Tech Stack**:
- Express.js backend
- React frontend
- PostgreSQL database
- ReactFlow for visual editor
- Redux for state management

**Key Features**:
- 100+ node types
- LangChain integration
- Tool nodes (HTTP requests, service-specific)
- Credential management
- OAuth2 support

**Architecture Highlights**:
- Monorepo (server, ui, components)
- Node registry system
- Tool-based API integration
- Generic HTTP request tools
- Service-specific nodes

**Best Practices**:
- Modular node architecture
- Extensible tool system
- OAuth2 credential handling
- Async node loading

### Flojoy (`flojoy-ai/studio`)

**Purpose**: Test sequencer for hardware validation

**Tech Stack**:
- Electron desktop app
- React + TypeScript
- ReactFlow for visual editor
- Zustand for state management
- Python backend for block execution

**Key Features**:
- Visual block-based scripting
- Hardware integration
- Test sequencer
- Python block execution
- Manifest-based blocks

**Architecture Highlights**:
- Electron architecture
- Block manifest system
- Python execution engine
- Hardware abstraction

**Best Practices**:
- Manifest-driven blocks
- Type-safe block definitions
- Clean separation of concerns

### FedRAMP Automation (`GSA/fedramp-automation`)

**Purpose**: OSCAL validation and templates for FedRAMP compliance

**Not directly relevant** to blocks/triggers research, but provides:
- Validation framework patterns
- Schema validation
- Documentation generation

---

## Visual Patterns from ShaderFrog & OpenMetadata

### ShaderFrog Patterns

**Visual Node Composition**:
- Node-based visual programming
- Drag-and-drop interface
- Real-time preview
- Node categories and organization

**Applicable Patterns**:
1. **Node Categories**: Organize blocks by function (similar to ShaderFrog's shader types)
2. **Visual Composition**: Compose complex workflows from simple blocks
3. **Preview System**: Show workflow structure visually
4. **Community Marketplace**: Share and discover workflows/blocks

### OpenMetadata Patterns

**Connector Architecture**:
- 100+ data connectors
- Standardized connector pattern
- Metadata graph
- Unified API

**Applicable Patterns**:
1. **Connector Registry**: Centralized connector definitions
2. **Standardized Integration**: Consistent connector interface
3. **Metadata Management**: Track integration metadata
4. **API-First Design**: Extensible architecture

**Key Insights**:
- OpenMetadata's connector pattern is excellent for third-party API integration
- Standardized connector interface makes adding new integrations easy
- Metadata graph helps track relationships between integrations
- API-first design enables extensibility

---

## Conclusion

This comprehensive system design provides:

1. **Complete Architecture**: Full system structure from frontend to backend
2. **Third-Party API Integration**: Comprehensive patterns for API integration
3. **Industry Best Practices**: Security, error handling, UX, DX, scalability
4. **Implementation Roadmap**: Phased approach to building the system
5. **Repository Insights**: Learnings from Sim, Flowise, Flojoy
6. **Visual Patterns**: Insights from ShaderFrog and OpenMetadata

### Key Takeaways

1. **Emulate, Don't Copy**: Learn from their patterns, improve upon them
2. **Registry Pattern**: Central registries for blocks, triggers, connectors
3. **Type Safety**: Full TypeScript + Zod validation
4. **Security First**: Encrypt credentials, verify webhooks, refresh tokens
5. **User Experience**: Clear setup, test connections, sample data
6. **Scalability**: Connection pooling, caching, queues
7. **Extensibility**: Easy to add new blocks, triggers, connectors

### Next Steps

1. Start with Phase 1 (Foundation)
2. Build incrementally following the roadmap
3. Test each phase thoroughly
4. Iterate based on user feedback
5. Continuously improve based on best practices

---

## Related Documentation

This comprehensive design is complemented by additional detailed documentation:

- **Production System Design** (`PRODUCTION_SYSTEM_DESIGN.md`): Production-ready architecture with semantic routing, tool wrapping, circuit breakers, rate limiting, monitoring, and deployment strategies
- **Third-Party API Structure** (`THIRD_PARTY_API_STRUCTURE.md`): Complete structure for connectors, route maps, tool wrappers, credentials, and API clients
- **System Architecture Diagrams** (`SYSTEM_ARCHITECTURE_DIAGRAMS.md`): Mermaid diagrams for complete system flow, API integration, and all major components
- **API Design Proposal** (`API_DESIGN_PROPOSAL.md`): RESTful API endpoints and specifications
- **API Implementation Examples** (`API_IMPLEMENTATION_EXAMPLE.md`): TypeScript implementation examples with Zod validation
- **Block/Trigger Patterns** (`BLOCK_TRIGGER_PATTERNS_ANALYSIS.md`): Detailed analysis of UI patterns from Sim, Flowise, and Flojoy

---

## References

- **Sim**: https://github.com/simstudioai/sim
- **Flowise**: https://github.com/FlowiseAI/Flowise
- **Flojoy**: https://github.com/flojoy-ai/studio
- **umbrella_corp**: https://github.com/flojoy-ai/umbrella_corp (semantic routing patterns)
- **ShaderFrog**: https://shaderfrog.com/2/
- **OpenMetadata**: https://open-metadata.org/
- **ReactFlow**: https://reactflow.dev/
- **Zustand**: https://zustand-demo.pmnd.rs/
- **Zod**: https://zod.dev/
- **Semantic Router**: https://github.com/aurelio-labs/semantic-router

---


