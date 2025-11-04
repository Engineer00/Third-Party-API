# Third-Party API Integration Patterns

## Overview
This document analyzes how block-based workflow systems integrate with third-party APIs like Google, Slack, webhooks, and HTTP requests. These patterns are essential for building a comprehensive CrewAI-like system. Analysis is based on cloned repositories:

- **Sim**: [`repos/sim`](https://github.com/simstudioai/sim) - Trigger-based integration patterns
- **Flowise**: [`repos/Flowise`](https://github.com/FlowiseAI/Flowise) - Tool-based integration patterns
- **Flojoy**: [`repos/flojoy`](https://github.com/flojoy-ai/studio) - Block-based integration patterns
- **Flojoy Studiolab**: [`repos/flojoy-studiolab`](https://github.com/flojoy-ai/studiolab) - Alternative implementation
- **External References**: [OpenMetadata](https://open-metadata.org/) (connector discovery and management) and [ShaderFrog](https://shaderfrog.com/2/) (visual composition)

---

## 1. Integration Architecture Patterns

### 1.1 Trigger-Based Integration (Sim)
**Pattern**: Webhook and polling triggers for event-driven workflows

**Key Features**:
- Webhook triggers for real-time events
- Polling triggers for services without webhooks
- OAuth credential management
- Provider-specific authentication

**Example Triggers**:
- Slack webhook
- Gmail polling
- Generic webhook
- GitHub webhook
- Stripe webhook
- Microsoft Teams webhook

### 1.2 Tool-Based Integration (Flowise)
**Pattern**: HTTP request tools and service-specific nodes

**Key Features**:
- Generic HTTP request tools (GET, POST, PUT, DELETE)
- Service-specific tools (Google Calendar, Gmail, Slack)
- OAuth2 credential handling
- Schema-based request configuration

**Example Tools**:
- RequestsGet, RequestsPost, RequestsPut, RequestsDelete
- GoogleCalendar, GoogleDocs, GoogleDrive, GoogleSheets
- Gmail, MicrosoftOutlook, MicrosoftTeams
- Slack (via MCP)
- Jira, Stripe

### 1.3 Block-Based Integration (Flojoy)
**Pattern**: Custom blocks for specific integrations

**Key Features**:
- Manifest-based block definitions
- Python-based block execution
- Hardware and API integrations

---

## 2. Authentication Patterns

### 2.1 OAuth 2.0 Integration

**Sim Pattern**:
```typescript
interface TriggerConfig {
  requiresCredentials?: boolean
  credentialProvider?: string // 'google-email', 'microsoft', etc.
  configFields: {
    // OAuth fields
    [key: string]: TriggerConfigField
  }
}
```

**Flowise Pattern**:
```typescript
interface INode {
  credential: INodeParams
  // Node requires OAuth credential
}

// Example: Google Calendar
credential: {
  label: 'Connect Credential',
  name: 'credential',
  type: 'credential',
  credentialNames: ['googleCalendarOAuth2']
}
```

**Key Features**:
- Centralized credential management
- Token refresh handling
- Scope-based permissions
- Multiple credential providers

### 2.2 API Key Authentication

**Pattern**: Secret storage for API keys

```typescript
// Generic webhook with auth token
configFields: {
  token: {
    type: 'string',
    label: 'Authentication Token',
    isSecret: true,
    required: false
  },
  secretHeaderName: {
    type: 'string',
    label: 'Secret Header Name',
    placeholder: 'X-Secret-Key'
  }
}
```

### 2.3 Webhook Authentication

**Pattern**: Signature verification for webhooks

```typescript
// Slack webhook with signing secret
configFields: {
  signingSecret: {
    type: 'string',
    label: 'Signing Secret',
    isSecret: true,
    required: true
  }
}
```

---

## 3. HTTP Request Integration

### 3.1 Generic HTTP Request Tools (Flowise)

**GET Request**:
```typescript
class RequestsGet_Tools implements INode {
  inputs: [
    {
      label: 'URL',
      name: 'requestsGetUrl',
      type: 'string',
      acceptVariable: true
    },
    {
      label: 'Headers',
      name: 'requestsGetHeaders',
      type: 'string',
      placeholder: `{
    "Authorization": "Bearer <token>"
}`
    },
    {
      label: 'Query Params Schema',
      name: 'requestsGetQueryParamsSchema',
      type: 'code',
      description: 'Schema for LLM to understand query params'
    }
  ]
}
```

**POST Request**:
```typescript
class RequestsPost_Tools implements INode {
  inputs: [
    {
      label: 'URL',
      name: 'requestsPostUrl',
      type: 'string'
    },
    {
      label: 'Body',
      name: 'requestPostBody',
      type: 'string',
      placeholder: `{
    "name": "John Doe",
    "age": 30
}`
    },
    {
      label: 'Body Schema',
      name: 'requestsPostBodySchema',
      type: 'code',
      description: 'Schema for LLM to understand body params'
    }
  ]
}
```

**Key Features**:
- Support for GET, POST, PUT, DELETE
- Schema-based parameter configuration
- Variable substitution
- LLM-friendly descriptions
- Max output length limits

### 3.2 Webhook Trigger (Sim)

**Generic Webhook**:
```typescript
export const genericWebhookTrigger: TriggerConfig = {
  id: 'generic_webhook',
  name: 'Generic Webhook',
  provider: 'generic',
  description: 'Receive webhooks from any service or API',
  
  configFields: {
    requireAuth: {
      type: 'boolean',
      label: 'Require Authentication',
      defaultValue: false
    },
    token: {
      type: 'string',
      label: 'Authentication Token',
      isSecret: true
    },
    secretHeaderName: {
      type: 'string',
      label: 'Secret Header Name',
      placeholder: 'X-Secret-Key'
    }
  },
  
  webhook: {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  }
}
```

---

## 4. Service-Specific Integrations

### 4.1 Google Services

**Google Calendar (Flowise)**:
```typescript
class GoogleCalendar_Tools implements INode {
  credential: {
    credentialNames: ['googleCalendarOAuth2']
  },
  
  inputs: [
    {
      label: 'Type',
      name: 'calendarType',
      type: 'options',
      options: ['event', 'calendar', 'freebusy']
    },
    {
      label: 'Event Actions',
      name: 'eventActions',
      type: 'multiOptions',
      options: [
        'listEvents',
        'createEvent',
        'getEvent',
        'updateEvent',
        'deleteEvent',
        'quickAddEvent'
      ]
    }
  ]
}
```

**Gmail Polling (Sim)**:
```typescript
export const gmailPollingTrigger: TriggerConfig = {
  id: 'gmail_poller',
  name: 'Gmail Email Trigger',
  requiresCredentials: true,
  credentialProvider: 'google-email',
  
  configFields: {
    labelIds: {
      type: 'multiselect',
      label: 'Gmail Labels to Monitor',
      options: [] // Dynamically populated
    },
    searchQuery: {
      type: 'string',
      label: 'Gmail Search Query',
      placeholder: 'subject:report OR from:important@example.com'
    },
    markAsRead: {
      type: 'boolean',
      label: 'Mark as Read',
      defaultValue: false
    },
    includeAttachments: {
      type: 'boolean',
      label: 'Include Attachments',
      defaultValue: false
    }
  },
  
  outputs: {
    email: {
      id: { type: 'string' },
      subject: { type: 'string' },
      from: { type: 'string' },
      bodyText: { type: 'string' },
      attachments: { type: 'file[]' }
    }
  }
}
```

**Google Services Available**:
- Google Calendar
- Google Docs
- Google Drive
- Google Sheets
- Gmail (via polling or OAuth)

### 4.2 Slack Integration

**Slack Webhook (Sim)**:
```typescript
export const slackWebhookTrigger: TriggerConfig = {
  id: 'slack_webhook',
  name: 'Slack Webhook',
  provider: 'slack',
  
  configFields: {
    signingSecret: {
      type: 'string',
      label: 'Signing Secret',
      isSecret: true,
      required: true
    }
  },
  
  outputs: {
    event: {
      event_type: { type: 'string' },
      channel: { type: 'string' },
      channel_name: { type: 'string' },
      user: { type: 'string' },
      text: { type: 'string' },
      timestamp: { type: 'string' }
    }
  },
  
  instructions: [
    'Go to Slack Apps page',
    'Create app and get signing secret',
    'Configure OAuth scopes',
    'Set up event subscriptions',
    'Install app to workspace'
  ]
}
```

**Slack MCP (Flowise)**:
- Model Context Protocol integration
- Tool-based Slack operations
- OAuth2 authentication

### 4.3 Microsoft Services

**Microsoft Teams (Sim)**:
- Webhook trigger
- Chat subscription trigger
- OAuth authentication

**Microsoft Outlook (Flowise)**:
- Email operations
- Calendar integration
- OAuth2 authentication

### 4.4 Other Services

**GitHub**:
- Webhook trigger for repository events
- Signature verification
- Event filtering

**Stripe**:
- Webhook trigger for payment events
- Signature verification
- Event type filtering

**Jira**:
- Tool-based integration
- OAuth authentication
- Issue management operations

---

## 5. Credential Management

### 5.1 Credential Storage

**Pattern**: Centralized credential store

```typescript
interface Credential {
  id: string
  name: string
  type: 'oauth2' | 'api_key' | 'basic_auth'
  provider: string
  data: {
    // Encrypted credential data
    access_token?: string
    refresh_token?: string
    api_key?: string
    // ...
  }
  scopes?: string[]
  expiresAt?: Date
}
```

### 5.2 OAuth Flow

**Steps**:
1. User initiates OAuth connection
2. Redirect to provider's OAuth page
3. User authorizes application
4. Receive authorization code
5. Exchange code for access/refresh tokens
6. Store tokens securely
7. Refresh tokens when expired

### 5.3 Token Refresh

**Pattern**: Automatic token refresh

```typescript
// Flowise pattern
async function refreshOAuth2Token(
  credentialData: ICommonObject,
  nodeData: INodeData
): Promise<string> {
  // Check if token is expired
  // Refresh using refresh_token
  // Update stored credential
  // Return new access token
}
```

---

## 6. API Design Recommendations

### 6.1 Third-Party API Endpoints

```typescript
// API endpoints for third-party integrations

// 1. Credentials Management
POST   /api/v1/credentials
GET    /api/v1/credentials
GET    /api/v1/credentials/:id
PUT    /api/v1/credentials/:id
DELETE /api/v1/credentials/:id

// 2. OAuth Flow
GET    /api/v1/oauth/:provider/authorize
GET    /api/v1/oauth/:provider/callback
POST   /api/v1/oauth/:provider/refresh

// 3. HTTP Request Tool Configuration
POST   /api/v1/tools/http-request/validate
POST   /api/v1/tools/http-request/test

// 4. Webhook Management
GET    /api/v1/webhooks
POST   /api/v1/webhooks/:id/test
DELETE /api/v1/webhooks/:id
```

### 6.2 Credential Types

```typescript
interface CredentialType {
  id: string
  name: string
  provider: string
  authType: 'oauth2' | 'api_key' | 'basic_auth' | 'bearer_token'
  fields: CredentialField[]
  scopes?: string[]
  instructions: string[]
}

interface CredentialField {
  id: string
  label: string
  type: 'string' | 'password' | 'select'
  required: boolean
  isSecret: boolean
  placeholder?: string
  description?: string
  options?: string[]
}
```

### 6.3 HTTP Request Tool Schema

```typescript
interface HTTPRequestTool {
  id: string
  name: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  url: string
  headers?: Record<string, string>
  queryParams?: Record<string, string>
  body?: any
  bodySchema?: JSONSchema
  queryParamsSchema?: JSONSchema
  auth?: {
    type: 'none' | 'bearer' | 'basic' | 'oauth2'
    credentialId?: string
    header?: string
  }
  responseHandling?: {
    maxLength?: number
    parseJson?: boolean
    extractFields?: string[]
  }
}
```

---

## 7. Implementation Patterns

### 7.1 Trigger Configuration UI

**Sim Pattern**:
- Modal-based configuration
- Step-by-step instructions
- Sample payload display
- Credential selector
- Test webhook button

**Key Components**:
```typescript
interface TriggerConfigUI {
  triggerId: string
  configFields: Record<string, TriggerConfigField>
  instructions: string[]
  samplePayload: any
  onSave: (config: Record<string, any>) => Promise<void>
  onTest?: () => Promise<void>
}
```

### 7.2 HTTP Request Tool UI

**Flowise Pattern**:
- URL input with variable support
- Headers editor (JSON)
- Body editor (JSON)
- Schema editor (for LLM)
- Description field

**Key Components**:
```typescript
interface HTTPRequestToolUI {
  url: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE'
  headers?: Record<string, string>
  body?: any
  bodySchema?: JSONSchema
  queryParamsSchema?: JSONSchema
  onExecute: (config: HTTPRequestConfig) => Promise<Response>
}
```

### 7.3 Credential Connection UI

**Pattern**:
- Provider selector
- OAuth flow initiation
- Credential form
- Test connection button
- Scope selection (for OAuth)

```typescript
interface CredentialConnectionUI {
  provider: string
  credentialType: CredentialType
  onConnect: (config: CredentialConfig) => Promise<Credential>
  onTest: (credential: Credential) => Promise<boolean>
}
```

---

## 8. Recommended API Structure

### 8.1 Credentials API

```http
# List available credential types
GET /api/v1/credentials/types
Response: {
  "success": true,
  "data": {
    "types": [
      {
        "id": "google-oauth2",
        "name": "Google OAuth2",
        "provider": "google",
        "authType": "oauth2",
        "scopes": ["calendar", "gmail", "drive"],
        "fields": [...],
        "instructions": [...]
      }
    ]
  }
}

# Create credential
POST /api/v1/credentials
Body: {
  "typeId": "google-oauth2",
  "name": "My Google Account",
  "config": { ... }
}

# List user credentials
GET /api/v1/credentials
Response: {
  "success": true,
  "data": {
    "credentials": [
      {
        "id": "uuid",
        "name": "My Google Account",
        "type": "google-oauth2",
        "provider": "google",
        "status": "connected",
        "expiresAt": "2025-01-01T00:00:00Z"
      }
    ]
  }
}

# OAuth Authorization
GET /api/v1/oauth/:provider/authorize?credentialType=google-oauth2&redirectUri=...
# Redirects to provider OAuth page

# OAuth Callback
GET /api/v1/oauth/:provider/callback?code=...&state=...
# Exchanges code for tokens, creates credential

# Refresh OAuth Token
POST /api/v1/credentials/:id/refresh
Response: {
  "success": true,
  "data": {
    "expiresAt": "2025-01-01T00:00:00Z"
  }
}
```

### 8.2 HTTP Request Tools API

```http
# Validate HTTP request configuration
POST /api/v1/tools/http-request/validate
Body: {
  "method": "POST",
  "url": "https://api.example.com/users",
  "headers": { "Authorization": "Bearer token" },
  "body": { "name": "John" },
  "bodySchema": { ... }
}
Response: {
  "success": true,
  "data": {
    "valid": true,
    "errors": [],
    "warnings": []
  }
}

# Test HTTP request
POST /api/v1/tools/http-request/test
Body: {
  "method": "GET",
  "url": "https://api.example.com/users",
  "headers": { ... },
  "auth": {
    "type": "oauth2",
    "credentialId": "uuid"
  }
}
Response: {
  "success": true,
  "data": {
    "status": 200,
    "headers": { ... },
    "body": { ... },
    "executionTime": 123
  }
}
```

### 8.3 Webhook API

```http
# List webhooks
GET /api/v1/webhooks?workflowId=uuid
Response: {
  "success": true,
  "data": {
    "webhooks": [
      {
        "id": "uuid",
        "workflowId": "uuid",
        "blockId": "uuid",
        "triggerId": "slack_webhook",
        "path": "my-slack-webhook",
        "webhookUrl": "https://api.example.com/webhooks/trigger/my-slack-webhook",
        "isActive": true,
        "lastTriggeredAt": "2025-01-01T00:00:00Z",
        "triggerCount": 42
      }
    ]
  }
}

# Test webhook
POST /api/v1/webhooks/:id/test
Body: {
  "payload": { ... }
}
Response: {
  "success": true,
  "data": {
    "received": true,
    "executionId": "uuid"
  }
}
```

---

## 9. Best Practices

### 9.1 Security
1. **Secret Storage**: Encrypt all credentials at rest
2. **Token Refresh**: Automatic refresh before expiration
3. **Webhook Verification**: Verify signatures for all webhooks
4. **Rate Limiting**: Implement rate limits for API calls
5. **Scope Limitation**: Request minimum required OAuth scopes

### 9.2 Error Handling
1. **Retry Logic**: Exponential backoff for failed requests
2. **Error Messages**: Clear, actionable error messages
3. **Logging**: Log all API calls (without sensitive data)
4. **Monitoring**: Track API usage and failures

### 9.3 User Experience
1. **Clear Instructions**: Step-by-step setup guides
2. **Test Buttons**: Allow testing connections before saving
3. **Sample Data**: Show sample payloads/responses
4. **Status Indicators**: Show connection status clearly
5. **Error Recovery**: Help users fix connection issues

### 9.4 Developer Experience
1. **Type Safety**: Full TypeScript types
2. **Documentation**: Comprehensive API documentation
3. **SDK**: Client SDK for common languages
4. **Examples**: Code examples for common use cases
5. **Schema Validation**: Validate all configurations

---

## 10. Integration Checklist

### For Each Third-Party Service:

- [ ] **Credential Type Definition**
  - [ ] Define credential fields
  - [ ] Configure OAuth scopes (if applicable)
  - [ ] Create setup instructions

- [ ] **Trigger/Tool Implementation**
  - [ ] Define configuration fields
  - [ ] Implement authentication
  - [ ] Handle webhook verification (if applicable)
  - [ ] Define output schema

- [ ] **UI Components**
  - [ ] Credential connection UI
  - [ ] Configuration form
  - [ ] Test connection button
  - [ ] Status indicators

- [ ] **Documentation**
  - [ ] Setup guide
  - [ ] API reference
  - [ ] Example workflows
  - [ ] Troubleshooting guide

- [ ] **Testing**
  - [ ] Unit tests
  - [ ] Integration tests
  - [ ] Webhook testing
  - [ ] Error handling tests

---

## 11. Supported Integrations Summary

### Triggers (Event-Driven)
- **Generic Webhook**: Any HTTP webhook
- **Slack**: Messages, mentions, reactions
- **Gmail**: New emails (polling)
- **GitHub**: Repository events
- **Stripe**: Payment events
- **Microsoft Teams**: Messages, chat events
- **WhatsApp**: Messages via Business Platform
- **Telegram**: Bot messages
- **Webflow**: Form submissions, CMS changes
- **Airtable**: Record changes
- **Google Forms**: Form submissions

### Tools (Action-Based)
- **HTTP Requests**: GET, POST, PUT, DELETE
- **Google Services**: Calendar, Docs, Drive, Sheets, Gmail
- **Microsoft Services**: Outlook, Teams, Calendar
- **Slack**: Via MCP
- **Jira**: Issue management
- **Stripe**: Payment operations
- **Search APIs**: Google, Brave, Serper, Tavily
- **OpenAPI Toolkit**: Generic OpenAPI integration

### Credential Types
- **OAuth2**: Google, Microsoft, Slack, GitHub
- **API Key**: Generic API keys
- **Bearer Token**: Token-based auth
- **Basic Auth**: Username/password
- **Custom Headers**: Custom authentication

---

## Conclusion

The integration patterns from Sim, Flowise, and Flojoy provide a comprehensive blueprint for building third-party API support:

1. **Triggers**: Webhook and polling-based event triggers
2. **Tools**: HTTP request tools and service-specific integrations
3. **Credentials**: Centralized OAuth and API key management
4. **UI**: User-friendly configuration interfaces
5. **Security**: Proper authentication and secret management

Combining these patterns with the API design proposal creates a robust, user-friendly system for integrating with any third-party service.

---

## 12. Semantic Routing & Intelligent Tool Selection (umbrella_corp Pattern)

### 12.1 Semantic Routing Integration

**Pattern**: Use semantic-router library to intelligently route user queries to appropriate connectors/tools

```typescript
// lib/routing/semantic-router.ts
export class SemanticRouter {
  private router: SemanticRouter
  private routeMaps: Map<string, RouteMap>
  
  async route(query: string): Promise<RoutingResult> {
    const result = await this.router.route(query)
    return {
      connectorId: result.name,
      confidence: result.confidence || 0,
      reasoning: result.reasoning
    }
  }
}
```

### 12.2 Route Map Structure

```json
// tools/route-maps/google-suite.json
{
  "connector": "google_suite",
  "routes": [
    {
      "tool": "gmail_send",
      "name": "EMAIL_MANAGEMENT_FLOW",
      "utterances": [
        "email", "send", "inbox", "message", "reply", "forward"
      ]
    },
    {
      "tool": "calendar_create",
      "name": "EVENT_MANAGEMENT_FLOW",
      "utterances": [
        "meeting", "schedule", "calendar", "appointment", "event"
      ]
    }
  ]
}
```

### 12.3 Tool Wrapper Pattern (CrewAI-style)

**Pattern**: Wrap third-party APIs as CrewAI tools for intelligent agent execution

```typescript
// tools/tool-wrapper.ts
export class ToolWrapper {
  private crew: CrewAI.Crew
  private tools: CrewAI.Tool[]
  
  async execute(query: string, config: any): Promise<any> {
    // Create task from user query
    const task = new CrewAI.Task({
      description: query,
      agent: this.crew.agents[0]
    })
    
    // Execute crew
    return await this.crew.kickoff([task])
  }
}
```

### 12.4 Hierarchical Routing

**Pattern**: Two-level routing (flow-level → tool-level)

```typescript
// 1. Top-level: Route to flow (e.g., GOOGLE_SUITE)
const flowResult = await topLevelRouter.route(query)
// 2. Flow-level: Route to tool within flow (e.g., calendar_create)
const toolResult = await flowRouter.route(query)
```

---

## 13. UI Flow Patterns from OpenMetadata & ShaderFrog

### 13.1 Connector Discovery UI (OpenMetadata Pattern)

**Pattern**: Categorized connector browser with visual cards

**Key Features:**
- **100+ Connectors**: Organized by category (API, Database, Messaging, Dashboard, Pipeline, ML Model, Metadata, Search, Storage)
- **Visual Cards**: Each connector shows icon, name, description, category, status
- **Search & Filter**: Text search, category filters, sort by popularity
- **Quick Connect**: One-click connection initiation

**UI Components:**
```typescript
interface ConnectorBrowser {
  connectors: Connector[]
  searchQuery: string
  selectedCategory: string
  
  // Visual display
  viewMode: 'grid' | 'list'
  connectorCards: ConnectorCard[]
  
  // Actions
  onConnect: (connector: Connector) => void
  onViewDetails: (connector: Connector) => void
}
```

### 13.2 Setup Wizard Flow (OpenMetadata Pattern)

**Pattern**: Multi-step guided setup with validation

**Steps:**
1. Connector Selection
2. Configuration (endpoints, parameters)
3. Authentication (OAuth or credentials)
4. Test Connection
5. Metadata Ingestion (what to sync)
6. Schedule (sync frequency)
7. Review & Deploy

### 13.3 Visual Composition (ShaderFrog Pattern)

**Pattern**: Node-based visual editor with real-time preview

**Key Features:**
- **Drag-and-Drop**: Connectors from palette to canvas
- **Inline Parameters**: Controls directly on nodes (ShaderFrog-style)
- **Real-time Preview**: See API request/response as you configure
- **Visual Feedback**: Status indicators, connection validation

**UI Flow:**
```
Connector Palette → Drag to Canvas → Configure Parameters → 
Connect Nodes → Real-time Preview → Execute
```

### 13.4 Status & Monitoring Dashboard (OpenMetadata Pattern)

**Pattern**: Real-time health indicators and metrics

**Features:**
- Connection status (🟢 Connected, 🟡 Warning, 🔴 Error)
- Last sync time
- API call statistics
- Error rate monitoring
- Quick actions (test, re-authenticate, view logs)

---

## Related Documentation

- **Best Integration Approach**: See `BEST_API_INTEGRATION_APPROACH.md` for recommended approach and analysis
- **Production System Design**: See `PRODUCTION_SYSTEM_DESIGN.md` for production-ready implementation
- **Third-Party API Structure**: See `THIRD_PARTY_API_STRUCTURE.md` for complete connector structure
- **Integration Flow Explained**: See `THIRD_PARTY_API_INTEGRATION_FLOW_EXPLAINED.md` for detailed flow explanation
- **System Architecture Diagrams**: See `SYSTEM_ARCHITECTURE_DIAGRAMS.md` for visual flow diagrams
- **UI Flow Patterns**: See `OPENMETADATA_SHADERFROG_UI_PATTERNS.md` for detailed UI patterns from OpenMetadata and ShaderFrog
- **API Design Proposal**: See `API_DESIGN_PROPOSAL.md` for API endpoint specifications
- **Block/Trigger Patterns**: See `BLOCK_TRIGGER_PATTERNS_ANALYSIS.md` for UI patterns from Sim, Flowise, and Flojoy

