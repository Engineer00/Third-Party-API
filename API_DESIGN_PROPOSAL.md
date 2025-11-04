# Unified API Design Proposal for CrewAI-like Block/Trigger System

## Overview
This document proposes a user-friendly and effective API structure for a block-based workflow system similar to CrewAI, inspired by the best practices from Sim, Flowise, and Flojoy.

---

## Core Principles

1. **RESTful Design**: Clean, intuitive REST endpoints
2. **Type Safety**: Strong typing with Zod/TypeScript validation
3. **Consistent Responses**: Standardized response formats
4. **Error Handling**: Clear, actionable error messages
5. **Versioning**: API versioning for future compatibility
6. **Documentation**: OpenAPI/Swagger documentation

---

## Base URL Structure

```
/api/v1/
```

All endpoints are prefixed with `/api/v1/` for versioning.

---

## Standard Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "requestId": "uuid",
    "timestamp": "2025-01-01T00:00:00Z"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... },
    "requestId": "uuid"
  }
}
```

---

## 1. Workflows API

### 1.1 List Workflows
```http
GET /api/v1/workflows
Query Parameters:
  - workspaceId?: string (filter by workspace)
  - folderId?: string (filter by folder)
  - page?: number (default: 1)
  - limit?: number (default: 50)
  - search?: string (search by name/description)
  - tags?: string[] (filter by tags)

Response:
{
  "success": true,
  "data": {
    "workflows": [
      {
        "id": "uuid",
        "name": "My Workflow",
        "description": "Workflow description",
        "color": "#3972F6",
        "workspaceId": "uuid",
        "folderId": "uuid",
        "tags": ["ai", "automation"],
        "status": "draft" | "deployed" | "archived",
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-01-01T00:00:00Z",
        "lastExecutedAt": "2025-01-01T00:00:00Z",
        "executionCount": 42,
        "metadata": {
          "blockCount": 5,
          "triggerCount": 1
        }
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 100,
      "totalPages": 2
    }
  }
}
```

### 1.2 Get Workflow
```http
GET /api/v1/workflows/:id

Response:
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "My Workflow",
    "description": "Workflow description",
    "color": "#3972F6",
    "workspaceId": "uuid",
    "folderId": "uuid",
    "tags": ["ai", "automation"],
    "status": "draft",
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-01T00:00:00Z",
    "state": {
      "blocks": { ... },
      "edges": [ ... ],
      "loops": { ... },
      "parallels": { ... }
    },
    "metadata": {
      "version": "1.0.0",
      "lastSaved": 1234567890,
      "isDeployed": false
    }
  }
}
```

### 1.3 Create Workflow
```http
POST /api/v1/workflows
Content-Type: application/json

Request Body:
{
  "name": "My New Workflow",
  "description": "Workflow description",
  "color": "#3972F6",
  "workspaceId": "uuid",
  "folderId": "uuid",
  "tags": ["ai", "automation"],
  "templateId": "uuid" (optional - use template)
}

Response:
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "My New Workflow",
    ...
  }
}
```

### 1.4 Update Workflow
```http
PUT /api/v1/workflows/:id
Content-Type: application/json

Request Body:
{
  "name": "Updated Name",
  "description": "Updated description",
  "color": "#FF0000",
  "tags": ["updated", "tags"]
}

Response:
{
  "success": true,
  "data": { ... }
}
```

### 1.5 Update Workflow State
```http
PUT /api/v1/workflows/:id/state
Content-Type: application/json

Request Body:
{
  "blocks": {
    "block-1": {
      "id": "block-1",
      "type": "agent",
      "name": "Researcher Agent",
      "position": { "x": 100, "y": 100 },
      "subBlocks": {
        "role": {
          "id": "role",
          "type": "short-input",
          "value": "Senior Research Analyst"
        },
        "goal": {
          "id": "goal",
          "type": "long-input",
          "value": "Research and analyze topics"
        }
      },
      "outputs": {},
      "enabled": true,
      "data": {}
    }
  },
  "edges": [
    {
      "id": "edge-1",
      "source": "block-1",
      "target": "block-2",
      "sourceHandle": "output",
      "targetHandle": "input"
    }
  ],
  "loops": {},
  "parallels": {},
  "lastSaved": 1234567890,
  "isDeployed": false
}

Response:
{
  "success": true,
  "data": {
    "warnings": [],
    "savedAt": "2025-01-01T00:00:00Z"
  }
}
```

### 1.6 Delete Workflow
```http
DELETE /api/v1/workflows/:id

Response:
{
  "success": true,
  "data": {
    "deleted": true,
    "id": "uuid"
  }
}
```

### 1.7 Deploy Workflow
```http
POST /api/v1/workflows/:id/deploy

Response:
{
  "success": true,
  "data": {
    "deployed": true,
    "deployedAt": "2025-01-01T00:00:00Z",
    "webhookUrl": "https://api.example.com/webhooks/trigger/:path"
  }
}
```

### 1.8 Undeploy Workflow
```http
POST /api/v1/workflows/:id/undeploy

Response:
{
  "success": true,
  "data": {
    "deployed": false,
    "undeployedAt": "2025-01-01T00:00:00Z"
  }
}
```

---

## 2. Blocks API

### 2.1 List Available Blocks
```http
GET /api/v1/blocks
Query Parameters:
  - category?: "agents" | "tasks" | "tools" | "triggers" | "all"
  - search?: string

Response:
{
  "success": true,
  "data": {
    "blocks": [
      {
        "id": "agent",
        "name": "Agent",
        "category": "agents",
        "description": "AI agent with role, goal, and backstory",
        "icon": "agent-icon.svg",
        "version": "1.0.0",
        "inputs": [
          {
            "id": "role",
            "name": "Role",
            "type": "string",
            "required": true,
            "description": "Agent's role"
          },
          {
            "id": "goal",
            "name": "Goal",
            "type": "string",
            "required": true,
            "description": "Agent's goal"
          }
        ],
        "outputs": [
          {
            "id": "output",
            "name": "Output",
            "type": "agent",
            "description": "Agent instance"
          }
        ],
        "configurable": true,
        "tags": ["ai", "agent"]
      }
    ]
  }
}
```

### 2.2 Get Block Definition
```http
GET /api/v1/blocks/:id

Response:
{
  "success": true,
  "data": {
    "id": "agent",
    "name": "Agent",
    "category": "agents",
    ...
  }
}
```

### 2.3 Validate Block Configuration
```http
POST /api/v1/blocks/:id/validate
Content-Type: application/json

Request Body:
{
  "blockId": "block-1",
  "config": {
    "role": "Researcher",
    "goal": "Research topics",
    "backstory": "Expert researcher"
  }
}

Response:
{
  "success": true,
  "data": {
    "valid": true,
    "errors": [],
    "warnings": []
  }
}
```

---

## 3. Triggers API

### 3.1 List Available Triggers
```http
GET /api/v1/triggers

Response:
{
  "success": true,
  "data": {
    "triggers": [
      {
        "id": "webhook",
        "name": "Webhook Trigger",
        "provider": "generic",
        "description": "Trigger workflow via webhook",
        "type": "webhook",
        "icon": "webhook-icon.svg",
        "version": "1.0.0",
        "configFields": {
          "path": {
            "type": "string",
            "label": "Webhook Path",
            "required": true,
            "description": "Unique path for webhook"
          },
          "method": {
            "type": "select",
            "label": "HTTP Method",
            "options": ["POST", "GET", "PUT", "DELETE"],
            "defaultValue": "POST"
          }
        },
        "outputs": {
          "body": {
            "type": "object",
            "description": "Request body"
          },
          "headers": {
            "type": "object",
            "description": "Request headers"
          }
        },
        "requiresCredentials": false,
        "webhook": {
          "method": "POST"
        },
        "instructions": [
          "Configure webhook path",
          "Use the generated URL to trigger workflow"
        ]
      }
    ]
  }
}
```

### 3.2 Get Trigger Definition
```http
GET /api/v1/triggers/:id

Response:
{
  "success": true,
  "data": {
    "id": "webhook",
    ...
  }
}
```

### 3.3 Configure Trigger on Block
```http
POST /api/v1/workflows/:workflowId/blocks/:blockId/triggers
Content-Type: application/json

Request Body:
{
  "triggerId": "webhook",
  "config": {
    "path": "my-webhook-path",
    "method": "POST"
  }
}

Response:
{
  "success": true,
  "data": {
    "triggerId": "webhook",
    "triggerPath": "my-webhook-path",
    "webhookUrl": "https://api.example.com/webhooks/trigger/my-webhook-path",
    "config": {
      "path": "my-webhook-path",
      "method": "POST"
    }
  }
}
```

### 3.4 Update Trigger Configuration
```http
PUT /api/v1/workflows/:workflowId/blocks/:blockId/triggers/:triggerId
Content-Type: application/json

Request Body:
{
  "config": {
    "path": "updated-path",
    "method": "POST"
  }
}

Response:
{
  "success": true,
  "data": { ... }
}
```

### 3.5 Delete Trigger
```http
DELETE /api/v1/workflows/:workflowId/blocks/:blockId/triggers/:triggerId

Response:
{
  "success": true,
  "data": {
    "deleted": true
  }
}
```

---

## 4. Execution API

### 4.1 Execute Workflow
```http
POST /api/v1/workflows/:id/execute
Content-Type: application/json
Headers:
  - X-Execution-Mode: "sync" | "async" (default: "sync")
  - X-Stream-Response: "true" | "false" (default: "false")

Request Body:
{
  "input": {
    "message": "Hello, world!"
  },
  "stream": false,
  "selectedOutputs": ["block-1", "block-2"],
  "isSecureMode": false
}

Response (Sync):
{
  "success": true,
  "data": {
    "executionId": "uuid",
    "status": "completed",
    "output": {
      "block-1": {
        "type": "agent",
        "data": "..."
      }
    },
    "executionTime": 1234,
    "completedAt": "2025-01-01T00:00:00Z"
  }
}

Response (Async):
{
  "success": true,
  "data": {
    "executionId": "uuid",
    "status": "queued",
    "queuedAt": "2025-01-01T00:00:00Z"
  }
}
```

### 4.2 Get Execution Status
```http
GET /api/v1/executions/:executionId

Response:
{
  "success": true,
  "data": {
    "executionId": "uuid",
    "workflowId": "uuid",
    "status": "running" | "completed" | "failed" | "cancelled",
    "progress": 0.75,
    "output": { ... },
    "error": null,
    "startedAt": "2025-01-01T00:00:00Z",
    "completedAt": "2025-01-01T00:00:00Z",
    "executionTime": 1234
  }
}
```

### 4.3 Cancel Execution
```http
POST /api/v1/executions/:executionId/cancel

Response:
{
  "success": true,
  "data": {
    "executionId": "uuid",
    "status": "cancelled",
    "cancelledAt": "2025-01-01T00:00:00Z"
  }
}
```

### 4.4 List Executions
```http
GET /api/v1/executions
Query Parameters:
  - workflowId?: string
  - status?: "running" | "completed" | "failed" | "cancelled"
  - page?: number
  - limit?: number
  - startDate?: ISO8601
  - endDate?: ISO8601

Response:
{
  "success": true,
  "data": {
    "executions": [ ... ],
    "pagination": { ... }
  }
}
```

---

## 5. Webhooks API

### 5.1 Trigger Webhook
```http
POST /api/v1/webhooks/trigger/:path
Content-Type: application/json

Request Body:
{
  "message": "Hello from webhook",
  "data": { ... }
}

Response:
{
  "success": true,
  "data": {
    "executionId": "uuid",
    "status": "queued",
    "webhookPath": "my-webhook-path"
  }
}
```

### 5.2 List Webhooks
```http
GET /api/v1/webhooks
Query Parameters:
  - workflowId?: string

Response:
{
  "success": true,
  "data": {
    "webhooks": [
      {
        "id": "uuid",
        "workflowId": "uuid",
        "blockId": "uuid",
        "triggerId": "webhook",
        "path": "my-webhook-path",
        "webhookUrl": "https://api.example.com/webhooks/trigger/my-webhook-path",
        "isActive": true,
        "createdAt": "2025-01-01T00:00:00Z",
        "lastTriggeredAt": "2025-01-01T00:00:00Z",
        "triggerCount": 42
      }
    ]
  }
}
```

### 5.3 Get Webhook Details
```http
GET /api/v1/webhooks/:id

Response:
{
  "success": true,
  "data": {
    "id": "uuid",
    ...
  }
}
```

---

## 6. Connectors API (Third-Party Integrations)

### 6.1 List Connectors
```http
GET /api/v1/connectors
Query Parameters:
  - category?: string (filter by category)
  - provider?: string (filter by provider)
  - search?: string (search by name/description)

Response:
{
  "success": true,
  "data": {
    "connectors": [
      {
        "id": "google_calendar",
        "name": "Google Calendar",
        "provider": "google",
        "category": "productivity",
        "version": "1.0.0",
        "description": "Integrate with Google Calendar API",
        "icon": "📅",
        "authType": "oauth2",
        "baseUrl": "https://www.googleapis.com/calendar/v3",
        "endpoints": {
          "listEvents": {
            "path": "/calendars/{calendarId}/events",
            "method": "GET",
            "description": "List events from a calendar"
          },
          "createEvent": {
            "path": "/calendars/{calendarId}/events",
            "method": "POST",
            "description": "Create a new calendar event"
          }
        },
        "semanticRouting": {
          "enabled": true,
          "routeMapPath": "./tools/route-maps/google-calendar.json",
          "confidenceThreshold": 0.7
        },
        "toolWrapper": {
          "enabled": true,
          "crewName": "Google Calendar Agent"
        },
        "rateLimit": {
          "requests": 100,
          "window": 60
        },
        "setupInstructions": [
          "1. Go to Google Cloud Console",
          "2. Enable Google Calendar API",
          "3. Create OAuth 2.0 credentials"
        ]
      }
    ]
  }
}
```

### 6.2 Get Connector Details
```http
GET /api/v1/connectors/:id

Response:
{
  "success": true,
  "data": {
    "id": "google_calendar",
    "name": "Google Calendar",
    ...
    "endpoints": { ... },
    "semanticRouting": { ... },
    "toolWrapper": { ... }
  }
}
```

### 6.3 List Connector Endpoints
```http
GET /api/v1/connectors/:id/endpoints

Response:
{
  "success": true,
  "data": {
    "endpoints": {
      "listEvents": {
        "path": "/calendars/{calendarId}/events",
        "method": "GET",
        "parameters": [
          {
            "name": "calendarId",
            "type": "string",
            "location": "path",
            "required": true
          },
          {
            "name": "timeMin",
            "type": "date",
            "location": "query",
            "required": false
          }
        ],
        "responseSchema": { ... }
      }
    }
  }
}
```

### 6.4 Semantic Route Query
```http
POST /api/v1/connectors/route
Content-Type: application/json

Request Body:
{
  "query": "Schedule a meeting for tomorrow at 2pm",
  "category": "google" (optional)
}

Response:
{
  "success": true,
  "data": {
    "connector": {
      "id": "google_calendar",
      "name": "Google Calendar"
    },
    "confidence": 0.92,
    "route": "EVENT_MANAGEMENT_FLOW",
    "reasoning": "Query matches calendar-related utterances",
    "tool": "calendar_create"
  }
}
```

### 6.5 Test Connector
```http
POST /api/v1/connectors/:id/test
Content-Type: application/json

Request Body:
{
  "credentialId": "uuid",
  "endpoint": "listEvents",
  "params": {
    "calendarId": "primary"
  }
}

Response:
{
  "success": true,
  "data": {
    "connected": true,
    "response": { ... },
    "executionTime": 234
  }
}
```

---

## 7. Workspaces API

### 7.1 List Workspaces
```http
GET /api/v1/workspaces

Response:
{
  "success": true,
  "data": {
    "workspaces": [
      {
        "id": "uuid",
        "name": "My Workspace",
        "description": "Workspace description",
        "role": "owner" | "admin" | "member" | "viewer",
        "memberCount": 5,
        "workflowCount": 10,
        "createdAt": "2025-01-01T00:00:00Z"
      }
    ]
  }
}
```

### 6.2 Create Workspace
```http
POST /api/v1/workspaces
Content-Type: application/json

Request Body:
{
  "name": "New Workspace",
  "description": "Workspace description"
}

Response:
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "New Workspace",
    ...
  }
}
```

---

## 8. Templates API

### 8.1 List Templates
```http
GET /api/v1/templates
Query Parameters:
  - category?: string
  - search?: string

Response:
{
  "success": true,
  "data": {
    "templates": [
      {
        "id": "uuid",
        "name": "Research Agent Template",
        "description": "Template for research agents",
        "category": "agents",
        "preview": "template-preview.png",
        "workflow": {
          "blocks": { ... },
          "edges": [ ... ]
        },
        "tags": ["research", "agent"],
        "createdAt": "2025-01-01T00:00:00Z"
      }
    ]
  }
}
```

### 7.2 Create Workflow from Template
```http
POST /api/v1/templates/:id/workflows
Content-Type: application/json

Request Body:
{
  "name": "My Workflow",
  "workspaceId": "uuid",
  "folderId": "uuid"
}

Response:
{
  "success": true,
  "data": {
    "workflow": { ... }
  }
}
```

---

## 9. Validation API

### 9.1 Validate Workflow
```http
POST /api/v1/workflows/:id/validate

Response:
{
  "success": true,
  "data": {
    "valid": true,
    "errors": [],
    "warnings": [
      {
        "blockId": "block-1",
        "message": "Agent missing goal",
        "severity": "warning"
      }
    ],
    "suggestions": [
      {
        "blockId": "block-2",
        "suggestion": "Consider adding a tool to this agent"
      }
    ]
  }
}
```

---

## 10. Error Codes

### Standard Error Codes
- `UNAUTHORIZED` (401): Authentication required
- `FORBIDDEN` (403): Insufficient permissions
- `NOT_FOUND` (404): Resource not found
- `VALIDATION_ERROR` (400): Request validation failed
- `CONFLICT` (409): Resource conflict
- `RATE_LIMIT_EXCEEDED` (429): Too many requests
- `INTERNAL_ERROR` (500): Server error

### Workflow-Specific Errors
- `WORKFLOW_NOT_FOUND` (404)
- `WORKFLOW_NOT_DEPLOYED` (400)
- `BLOCK_NOT_FOUND` (404)
- `INVALID_WORKFLOW_STATE` (400)
- `EXECUTION_FAILED` (500)
- `TRIGGER_NOT_FOUND` (404)

---

## 11. WebSocket API (Real-time Updates)

### 11.1 Connection
```javascript
ws://api.example.com/ws/v1/workflows/:workflowId

// Subscribe to workflow updates
{
  "type": "subscribe",
  "channel": "workflow-updates"
}

// Receive updates
{
  "type": "workflow-updated",
  "data": {
    "blockId": "block-1",
    "update": { ... }
  }
}
```

### 10.2 Execution Updates
```javascript
// Subscribe to execution
{
  "type": "subscribe",
  "channel": "execution",
  "executionId": "uuid"
}

// Receive execution updates
{
  "type": "execution-update",
  "data": {
    "executionId": "uuid",
    "status": "running",
    "progress": 0.5,
    "currentBlock": "block-1"
  }
}
```

---

## 12. Best Practices

### 12.1 Request Headers
```
Authorization: Bearer <token>
Content-Type: application/json
X-Request-ID: <uuid> (optional, for tracking)
```

### 12.2 Pagination
Always use pagination for list endpoints:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 50, max: 100)

### 12.3 Filtering
Use query parameters for filtering:
- `search`: Text search
- `status`: Filter by status
- `tags`: Filter by tags
- Date ranges: `startDate`, `endDate`

### 12.4 Rate Limiting
- Standard: 100 requests/minute
- Burst: 200 requests/minute
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

### 12.5 Caching
- Use `ETag` and `If-None-Match` for conditional requests
- Cache-Control headers for cacheable resources

---

## 13. Implementation Recommendations

### 12.1 Technology Stack
- **Framework**: Next.js (App Router) or Express.js
- **Validation**: Zod for request/response validation
- **Database**: PostgreSQL with Drizzle ORM
- **Real-time**: Socket.io or WebSockets
- **Documentation**: OpenAPI/Swagger

### 12.2 File Structure
```
src/
├── api/
│   ├── v1/
│   │   ├── workflows/
│   │   ├── blocks/
│   │   ├── triggers/
│   │   ├── executions/
│   │   └── webhooks/
│   └── middleware/
│       ├── auth.ts
│       ├── validation.ts
│       └── error-handler.ts
├── lib/
│   ├── validation/
│   ├── execution/
│   └── webhooks/
└── types/
    └── api.ts
```

### 12.3 Key Features
1. **Type Safety**: Full TypeScript with Zod validation
2. **Error Handling**: Centralized error handling
3. **Logging**: Structured logging with request IDs
4. **Testing**: Comprehensive API tests
5. **Documentation**: Auto-generated OpenAPI docs

---

## 14. Comparison with Existing Platforms

### Sim
- ✅ Uses Next.js App Router (good for SSR)
- ✅ Strong validation with Zod
- ✅ Good error handling
- ✅ Webhook support
- ⚠️ Complex state management

### Flowise
- ✅ RESTful API design
- ✅ Clear separation of concerns
- ✅ Good permission system
- ⚠️ Less type safety
- ⚠️ No versioning

### Flojoy
- ✅ Clean architecture
- ✅ Good state management
- ⚠️ Desktop-focused (Electron)
- ⚠️ Limited API exposure

### Our Proposal
- ✅ Combines best practices
- ✅ Type-safe with Zod
- ✅ RESTful with versioning
- ✅ Comprehensive error handling
- ✅ Real-time support
- ✅ Better documentation
- ✅ More user-friendly responses

---

## Conclusion

This API design provides:
1. **User-Friendly**: Clear, intuitive endpoints
2. **Type-Safe**: Full validation with Zod
3. **Scalable**: Pagination, filtering, caching
4. **Reliable**: Comprehensive error handling
5. **Documented**: OpenAPI/Swagger support
6. **Real-time**: WebSocket support for live updates

The structure is inspired by all three platforms while improving upon their limitations and adding modern best practices.

---

## Related Documentation

- **Production System Design**: See `PRODUCTION_SYSTEM_DESIGN.md` for production-ready architecture
- **Third-Party API Structure**: See `THIRD_PARTY_API_STRUCTURE.md` for detailed connector patterns
- **System Architecture Diagrams**: See `SYSTEM_ARCHITECTURE_DIAGRAMS.md` for visual diagrams
- **Semantic Routing**: See `PRODUCTION_SYSTEM_DESIGN.md` for semantic routing implementation

