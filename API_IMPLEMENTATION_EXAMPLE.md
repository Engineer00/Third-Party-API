# API Implementation Example

This document provides practical TypeScript examples for implementing the proposed API structure.

---

## 1. Type Definitions

```typescript
// types/api.ts

export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: ApiError
  meta?: {
    requestId: string
    timestamp: string
  }
}

export interface ApiError {
  code: string
  message: string
  details?: Record<string, any>
  requestId: string
}

export interface PaginationParams {
  page?: number
  limit?: number
}

export interface PaginationMeta {
  page: number
  limit: number
  total: number
  totalPages: number
}

export interface Workflow {
  id: string
  name: string
  description?: string
  color: string
  workspaceId?: string
  folderId?: string
  tags: string[]
  status: 'draft' | 'deployed' | 'archived'
  createdAt: string
  updatedAt: string
  lastExecutedAt?: string
  executionCount: number
  metadata: {
    blockCount: number
    triggerCount: number
  }
}

export interface WorkflowState {
  blocks: Record<string, BlockState>
  edges: Edge[]
  loops?: Record<string, LoopState>
  parallels?: Record<string, ParallelState>
  lastSaved?: number
  isDeployed?: boolean
  deployedAt?: string
}

export interface BlockState {
  id: string
  type: string
  name: string
  position: { x: number; y: number }
  subBlocks: Record<string, SubBlockState>
  outputs: Record<string, any>
  enabled: boolean
  horizontalHandles?: boolean
  isWide?: boolean
  height?: number
  advancedMode?: boolean
  triggerMode?: boolean
  data?: BlockData
}

export interface SubBlockState {
  id: string
  type: string
  value: any
}

export interface BlockData {
  parentId?: string
  extent?: 'parent'
  width?: number
  height?: number
  collection?: any
  count?: number
  loopType?: 'for' | 'forEach' | 'while' | 'doWhile'
  whileCondition?: string
  parallelType?: 'collection' | 'count'
  type?: string
}

export interface Edge {
  id: string
  source: string
  target: string
  sourceHandle?: string
  targetHandle?: string
  type?: string
  animated?: boolean
  style?: Record<string, any>
  data?: Record<string, any>
}

export interface LoopState {
  id: string
  nodes: string[]
  iterations: number
  loopType: 'for' | 'forEach' | 'while' | 'doWhile'
  forEachItems?: any[] | Record<string, any> | string
  whileCondition?: string
}

export interface ParallelState {
  id: string
  nodes: string[]
  distribution?: any[] | Record<string, any> | string
  count?: number
  parallelType?: 'count' | 'collection'
}

export interface BlockDefinition {
  id: string
  name: string
  category: 'agents' | 'tasks' | 'tools' | 'triggers'
  description: string
  icon?: string
  version: string
  inputs: BlockInput[]
  outputs: BlockOutput[]
  configurable: boolean
  tags: string[]
}

export interface BlockInput {
  id: string
  name: string
  type: 'string' | 'number' | 'boolean' | 'object' | 'array' | 'files'
  required: boolean
  description?: string
  defaultValue?: any
}

export interface BlockOutput {
  id: string
  name: string
  type: string
  description?: string
}

export interface TriggerDefinition {
  id: string
  name: string
  provider: string
  description: string
  type: 'webhook' | 'schedule' | 'event' | 'manual'
  icon?: string
  version: string
  configFields: Record<string, TriggerConfigField>
  outputs: Record<string, TriggerOutput>
  requiresCredentials?: boolean
  webhook?: {
    method?: 'POST' | 'GET' | 'PUT' | 'DELETE'
    headers?: Record<string, string>
  }
  instructions: string[]
}

export interface TriggerConfigField {
  type: 'string' | 'boolean' | 'select' | 'number' | 'multiselect' | 'credential'
  label: string
  placeholder?: string
  options?: string[]
  defaultValue?: string | boolean | number | string[]
  description?: string
  required?: boolean
  isSecret?: boolean
  provider?: string
  requiredScopes?: string[]
}

export interface TriggerOutput {
  type?: string
  description?: string
  [key: string]: TriggerOutput | string | undefined
}

export interface Execution {
  executionId: string
  workflowId: string
  status: 'running' | 'completed' | 'failed' | 'cancelled'
  progress?: number
  output?: Record<string, any>
  error?: {
    message: string
    code: string
    details?: any
  }
  startedAt: string
  completedAt?: string
  executionTime?: number
}

export interface Webhook {
  id: string
  workflowId: string
  blockId: string
  triggerId: string
  path: string
  webhookUrl: string
  isActive: boolean
  createdAt: string
  lastTriggeredAt?: string
  triggerCount: number
}
```

---

## 2. Zod Schemas for Validation

```typescript
// lib/validation/schemas.ts
import { z } from 'zod'

export const PositionSchema = z.object({
  x: z.number(),
  y: z.number(),
})

export const SubBlockStateSchema = z.object({
  id: z.string(),
  type: z.string(),
  value: z.any(),
})

export const BlockDataSchema = z.object({
  parentId: z.string().optional(),
  extent: z.literal('parent').optional(),
  width: z.number().optional(),
  height: z.number().optional(),
  collection: z.unknown().optional(),
  count: z.number().optional(),
  loopType: z.enum(['for', 'forEach', 'while', 'doWhile']).optional(),
  whileCondition: z.string().optional(),
  parallelType: z.enum(['collection', 'count']).optional(),
  type: z.string().optional(),
})

export const BlockStateSchema = z.object({
  id: z.string(),
  type: z.string(),
  name: z.string(),
  position: PositionSchema,
  subBlocks: z.record(SubBlockStateSchema),
  outputs: z.record(z.any()),
  enabled: z.boolean(),
  horizontalHandles: z.boolean().optional(),
  isWide: z.boolean().optional(),
  height: z.number().optional(),
  advancedMode: z.boolean().optional(),
  triggerMode: z.boolean().optional(),
  data: BlockDataSchema.optional(),
})

export const EdgeSchema = z.object({
  id: z.string(),
  source: z.string(),
  target: z.string(),
  sourceHandle: z.string().optional(),
  targetHandle: z.string().optional(),
  type: z.string().optional(),
  animated: z.boolean().optional(),
  style: z.record(z.any()).optional(),
  data: z.record(z.any()).optional(),
})

export const LoopSchema = z.object({
  id: z.string(),
  nodes: z.array(z.string()),
  iterations: z.number(),
  loopType: z.enum(['for', 'forEach', 'while', 'doWhile']),
  forEachItems: z.union([z.array(z.any()), z.record(z.any()), z.string()]).optional(),
  whileCondition: z.string().optional(),
})

export const ParallelSchema = z.object({
  id: z.string(),
  nodes: z.array(z.string()),
  distribution: z.union([z.array(z.any()), z.record(z.any()), z.string()]).optional(),
  count: z.number().optional(),
  parallelType: z.enum(['count', 'collection']).optional(),
})

export const WorkflowStateSchema = z.object({
  blocks: z.record(BlockStateSchema),
  edges: z.array(EdgeSchema),
  loops: z.record(LoopSchema).optional(),
  parallels: z.record(ParallelSchema).optional(),
  lastSaved: z.number().optional(),
  isDeployed: z.boolean().optional(),
  deployedAt: z.coerce.date().optional(),
})

export const CreateWorkflowSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100),
  description: z.string().max(500).optional(),
  color: z.string().regex(/^#[0-9A-F]{6}$/i).default('#3972F6'),
  workspaceId: z.string().uuid().optional(),
  folderId: z.string().uuid().nullable().optional(),
  tags: z.array(z.string()).default([]),
  templateId: z.string().uuid().optional(),
})

export const UpdateWorkflowSchema = z.object({
  name: z.string().min(1).max(100).optional(),
  description: z.string().max(500).optional(),
  color: z.string().regex(/^#[0-9A-F]{6}$/i).optional(),
  tags: z.array(z.string()).optional(),
})

export const ExecuteWorkflowSchema = z.object({
  input: z.any().optional(),
  stream: z.boolean().default(false),
  selectedOutputs: z.array(z.string()).optional(),
  isSecureMode: z.boolean().default(false),
})
```

---

## 3. API Client Implementation

```typescript
// lib/api-client.ts

export class WorkflowApiClient {
  private baseUrl: string
  private apiKey?: string

  constructor(baseUrl: string, apiKey?: string) {
    this.baseUrl = baseUrl.replace(/\/$/, '')
    this.apiKey = apiKey
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(this.apiKey && { Authorization: `Bearer ${this.apiKey}` }),
      ...options.headers,
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error = await response.json()
      throw new ApiError(error.error.code, error.error.message, error.error)
    }

    return response.json()
  }

  // Workflows
  async listWorkflows(params?: {
    workspaceId?: string
    folderId?: string
    page?: number
    limit?: number
    search?: string
    tags?: string[]
  }): Promise<ApiResponse<{ workflows: Workflow[]; pagination: PaginationMeta }>> {
    const query = new URLSearchParams()
    if (params?.workspaceId) query.set('workspaceId', params.workspaceId)
    if (params?.folderId) query.set('folderId', params.folderId)
    if (params?.page) query.set('page', params.page.toString())
    if (params?.limit) query.set('limit', params.limit.toString())
    if (params?.search) query.set('search', params.search)
    if (params?.tags) params.tags.forEach(tag => query.append('tags', tag))

    return this.request(`/api/v1/workflows?${query}`)
  }

  async getWorkflow(id: string): Promise<ApiResponse<Workflow & { state: WorkflowState }>> {
    return this.request(`/api/v1/workflows/${id}`)
  }

  async createWorkflow(data: z.infer<typeof CreateWorkflowSchema>): Promise<ApiResponse<Workflow>> {
    return this.request('/api/v1/workflows', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateWorkflow(
    id: string,
    data: z.infer<typeof UpdateWorkflowSchema>
  ): Promise<ApiResponse<Workflow>> {
    return this.request(`/api/v1/workflows/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async updateWorkflowState(
    id: string,
    state: WorkflowState
  ): Promise<ApiResponse<{ warnings: string[]; savedAt: string }>> {
    return this.request(`/api/v1/workflows/${id}/state`, {
      method: 'PUT',
      body: JSON.stringify(state),
    })
  }

  async deleteWorkflow(id: string): Promise<ApiResponse<{ deleted: boolean; id: string }>> {
    return this.request(`/api/v1/workflows/${id}`, {
      method: 'DELETE',
    })
  }

  async deployWorkflow(
    id: string
  ): Promise<ApiResponse<{ deployed: boolean; deployedAt: string; webhookUrl?: string }>> {
    return this.request(`/api/v1/workflows/${id}/deploy`, {
      method: 'POST',
    })
  }

  async undeployWorkflow(
    id: string
  ): Promise<ApiResponse<{ deployed: boolean; undeployedAt: string }>> {
    return this.request(`/api/v1/workflows/${id}/undeploy`, {
      method: 'POST',
    })
  }

  // Blocks
  async listBlocks(params?: {
    category?: 'agents' | 'tasks' | 'tools' | 'triggers' | 'all'
    search?: string
  }): Promise<ApiResponse<{ blocks: BlockDefinition[] }>> {
    const query = new URLSearchParams()
    if (params?.category) query.set('category', params.category)
    if (params?.search) query.set('search', params.search)

    return this.request(`/api/v1/blocks?${query}`)
  }

  async getBlock(id: string): Promise<ApiResponse<BlockDefinition>> {
    return this.request(`/api/v1/blocks/${id}`)
  }

  // Triggers
  async listTriggers(): Promise<ApiResponse<{ triggers: TriggerDefinition[] }>> {
    return this.request('/api/v1/triggers')
  }

  async getTrigger(id: string): Promise<ApiResponse<TriggerDefinition>> {
    return this.request(`/api/v1/triggers/${id}`)
  }

  async configureTrigger(
    workflowId: string,
    blockId: string,
    triggerId: string,
    config: Record<string, any>
  ): Promise<ApiResponse<{
    triggerId: string
    triggerPath: string
    webhookUrl: string
    config: Record<string, any>
  }>> {
    return this.request(`/api/v1/workflows/${workflowId}/blocks/${blockId}/triggers`, {
      method: 'POST',
      body: JSON.stringify({ triggerId, config }),
    })
  }

  // Execution
  async executeWorkflow(
    id: string,
    options: {
      input?: any
      stream?: boolean
      selectedOutputs?: string[]
      isSecureMode?: boolean
      mode?: 'sync' | 'async'
    } = {}
  ): Promise<ApiResponse<Execution>> {
    const headers: HeadersInit = {}
    if (options.mode) headers['X-Execution-Mode'] = options.mode
    if (options.stream) headers['X-Stream-Response'] = 'true'

    return this.request(`/api/v1/workflows/${id}/execute`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        input: options.input,
        stream: options.stream,
        selectedOutputs: options.selectedOutputs,
        isSecureMode: options.isSecureMode,
      }),
    })
  }

  async getExecution(executionId: string): Promise<ApiResponse<Execution>> {
    return this.request(`/api/v1/executions/${executionId}`)
  }

  async cancelExecution(executionId: string): Promise<ApiResponse<{ executionId: string; status: string; cancelledAt: string }>> {
    return this.request(`/api/v1/executions/${executionId}/cancel`, {
      method: 'POST',
    })
  }

  // Webhooks
  async listWebhooks(params?: { workflowId?: string }): Promise<ApiResponse<{ webhooks: Webhook[] }>> {
    const query = new URLSearchParams()
    if (params?.workflowId) query.set('workflowId', params.workflowId)

    return this.request(`/api/v1/webhooks?${query}`)
  }

  async getWebhook(id: string): Promise<ApiResponse<Webhook>> {
    return this.request(`/api/v1/webhooks/${id}`)
  }
}

export class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public details?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}
```

---

## 4. Usage Example

```typescript
// Example usage
import { WorkflowApiClient } from './lib/api-client'

const client = new WorkflowApiClient('https://api.example.com', 'your-api-key')

// Create a workflow
const createResponse = await client.createWorkflow({
  name: 'My Research Workflow',
  description: 'Automated research workflow',
  color: '#3972F6',
  tags: ['research', 'ai'],
})

const workflowId = createResponse.data!.id

// Add blocks to workflow state
const workflowState = {
  blocks: {
    'agent-1': {
      id: 'agent-1',
      type: 'agent',
      name: 'Researcher',
      position: { x: 100, y: 100 },
      subBlocks: {
        role: {
          id: 'role',
          type: 'short-input',
          value: 'Senior Research Analyst',
        },
        goal: {
          id: 'goal',
          type: 'long-input',
          value: 'Research and analyze topics thoroughly',
        },
      },
      outputs: {},
      enabled: true,
    },
  },
  edges: [],
  lastSaved: Date.now(),
  isDeployed: false,
}

// Save workflow state
await client.updateWorkflowState(workflowId, workflowState)

// Configure a webhook trigger
await client.configureTrigger(workflowId, 'agent-1', 'webhook', {
  path: 'my-research-webhook',
  method: 'POST',
})

// Deploy workflow
const deployResponse = await client.deployWorkflow(workflowId)
console.log('Webhook URL:', deployResponse.data!.webhookUrl)

// Execute workflow
const executionResponse = await client.executeWorkflow(workflowId, {
  input: { topic: 'AI Research' },
  mode: 'sync',
})

console.log('Execution result:', executionResponse.data!.output)
```

---

## 5. Next.js Route Handler Example

```typescript
// app/api/v1/workflows/[id]/state/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { WorkflowStateSchema } from '@/lib/validation/schemas'
import { getSession } from '@/lib/auth'
import { saveWorkflowState } from '@/lib/workflows/db-helpers'

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const session = await getSession()
    if (!session?.user?.id) {
      return NextResponse.json(
        {
          success: false,
          error: {
            code: 'UNAUTHORIZED',
            message: 'Authentication required',
            requestId: crypto.randomUUID(),
          },
        },
        { status: 401 }
      )
    }

    const { id: workflowId } = await params
    const body = await request.json()

    // Validate request body
    const state = WorkflowStateSchema.parse(body)

    // Check permissions
    const hasAccess = await checkWorkflowAccess(workflowId, session.user.id)
    if (!hasAccess) {
      return NextResponse.json(
        {
          success: false,
          error: {
            code: 'FORBIDDEN',
            message: 'Insufficient permissions',
            requestId: crypto.randomUUID(),
          },
        },
        { status: 403 }
      )
    }

    // Save workflow state
    const result = await saveWorkflowState(workflowId, state)

    return NextResponse.json({
      success: true,
      data: {
        warnings: result.warnings || [],
        savedAt: new Date().toISOString(),
      },
      meta: {
        requestId: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
      },
    })
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          success: false,
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Invalid request body',
            details: error.errors,
            requestId: crypto.randomUUID(),
          },
        },
        { status: 400 }
      )
    }

    return NextResponse.json(
      {
        success: false,
        error: {
          code: 'INTERNAL_ERROR',
          message: 'An internal error occurred',
          requestId: crypto.randomUUID(),
        },
      },
      { status: 500 }
    )
  }
}
```

---

This implementation provides:
1. **Type Safety**: Full TypeScript types
2. **Validation**: Zod schemas for all inputs
3. **Error Handling**: Consistent error responses
4. **Client Library**: Easy-to-use API client
5. **Server Implementation**: Example route handlers

The API is designed to be intuitive, type-safe, and developer-friendly while maintaining the flexibility needed for complex workflows.

---

## 6. Connector API Client Implementation

```typescript
// lib/api-client.ts (Extended)

export class ConnectorApiClient {
  // List connectors
  async listConnectors(params?: {
    category?: string
    provider?: string
    search?: string
  }): Promise<ApiResponse<{ connectors: Connector[] }>> {
    const query = new URLSearchParams()
    if (params?.category) query.set('category', params.category)
    if (params?.provider) query.set('provider', params.provider)
    if (params?.search) query.set('search', params.search)

    return this.request(`/api/v1/connectors?${query}`)
  }

  // Get connector details
  async getConnector(id: string): Promise<ApiResponse<Connector>> {
    return this.request(`/api/v1/connectors/${id}`)
  }

  // Semantic route query
  async routeQuery(
    query: string,
    category?: string
  ): Promise<ApiResponse<ConnectorRoutingResult>> {
    return this.request('/api/v1/connectors/route', {
      method: 'POST',
      body: JSON.stringify({ query, category }),
    })
  }

  // Test connector
  async testConnector(
    connectorId: string,
    config: {
      credentialId?: string
      endpoint: string
      params: any
    }
  ): Promise<ApiResponse<ConnectorTestResult>> {
    return this.request(`/api/v1/connectors/${connectorId}/test`, {
      method: 'POST',
      body: JSON.stringify(config),
    })
  }
}

// Usage example
const client = new ConnectorApiClient('https://api.example.com', 'api-key')

// Route user query to appropriate connector
const routingResult = await client.routeQuery(
  'Schedule a meeting for tomorrow at 2pm'
)

if (routingResult.data && routingResult.data.confidence > 0.7) {
  const connector = routingResult.data.connector
  console.log(`Routing to: ${connector.name} (confidence: ${routingResult.data.confidence})`)
  
  // Execute with tool wrapper if enabled
  if (connector.toolWrapper?.enabled) {
    const result = await executeWithToolWrapper(
      connector,
      routingResult.data.query,
      {}
    )
  }
}
```

---

## 7. Semantic Router Implementation Example

```typescript
// lib/semantic-router.ts

import { SemanticRouter, Route } from 'semantic-router'
import { OpenAIEncoder } from 'semantic-router/encoders'

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
    
    // Convert route map to semantic router routes
    const routes = routeMap.routes.map(route => 
      new Route({
        name: `${connectorId}:${route.name}`,
        utterances: route.utterances
      })
    )
    
    this.router.addRoutes(routes)
  }
  
  async route(query: string): Promise<RoutingResult> {
    const result = await this.router.route(query)
    
    // Parse connector and tool from route name
    const [connectorId, routeName] = result.name.split(':')
    
    return {
      connectorId,
      routeName,
      confidence: result.confidence || 0,
      reasoning: result.reasoning
    }
  }
}
```

---

## Related Documentation

- **Production System Design**: See `PRODUCTION_SYSTEM_DESIGN.md` for complete semantic routing and tool wrapper implementation
- **Third-Party API Structure**: See `THIRD_PARTY_API_STRUCTURE.md` for connector structure and route map format
- **API Design Proposal**: See `API_DESIGN_PROPOSAL.md` for complete API endpoint specifications

