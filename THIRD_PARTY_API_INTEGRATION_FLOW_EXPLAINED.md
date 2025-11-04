# Third-Party API Integration Flow - Detailed Explanation

## Overview

This document provides a comprehensive explanation of the **Third-Party API Integration Flow** sequence diagram. This flow illustrates how user queries are intelligently routed to appropriate third-party APIs, executed with production-ready features, and results are returned to the user.

---

## Table of Contents

1. [Flow Summary](#flow-summary)
2. [Participants (Components)](#participants-components)
3. [Step-by-Step Flow Explanation](#step-by-step-flow-explanation)
4. [Decision Points & Alternative Paths](#decision-points--alternative-paths)
5. [Production Features](#production-features)
6. [Error Handling](#error-handling)
7. [Example Scenarios](#example-scenarios)

---

## Flow Summary

The integration flow follows this high-level pattern:

1. **User Input**: User submits a natural language query
2. **Semantic Routing**: System intelligently routes query to appropriate connector
3. **Connector Selection**: Load and configure the selected connector
4. **Tool Wrapping** (Optional): Wrap API as CrewAI tool for intelligent execution
5. **Authentication**: Retrieve and validate credentials
6. **Production Checks**: Rate limiting, circuit breaker, caching
7. **API Execution**: Execute request to external API
8. **Response Handling**: Process and return results

---

## Participants (Components)

### 1. **User**
- The end user who submits queries
- Can be a human or another system making API calls

### 2. **UI (User Interface)**
- Frontend application (React/Next.js)
- Receives user queries and displays results
- Handles user interactions

### 3. **SemanticRouter**
- Intelligent routing component using semantic-router library
- Analyzes natural language queries using embeddings
- Matches queries to appropriate connectors/tools based on route maps
- Returns confidence scores for matches

### 4. **ConnectorMgr (Connector Manager)**
- Manages all third-party API connectors
- Loads connector configurations
- Validates connector configs
- Handles execution orchestration
- Manages production features (rate limiting, circuit breaker, caching)

### 5. **ToolWrapper**
- Wraps third-party APIs as CrewAI tools
- Creates AI agents with API tools
- Executes queries using LLM-powered execution
- Enables natural language understanding of API capabilities

### 6. **CredentialMgr (Credential Manager)**
- Manages authentication credentials
- Stores encrypted credentials (OAuth tokens, API keys)
- Handles token refresh for OAuth
- Validates credential expiry

### 7. **APIClient (API Client)**
- HTTP client for making requests to external APIs
- Handles request/response formatting
- Implements retry logic
- Manages connection pooling

### 8. **ExternalAPI**
- Third-party service APIs (Google, Slack, GitHub, etc.)
- Receives HTTP requests
- Returns responses

---

## Step-by-Step Flow Explanation

### Phase 1: Query Initiation & Routing

#### Step 1: User Submits Query
```
User -> UI: Natural Language Query
```

**What Happens:**
- User types or submits a natural language query (e.g., "Schedule a meeting for tomorrow at 2pm")
- UI receives the query and prepares it for processing
- Query is sent to the backend for routing

**Example:**
- Query: "Schedule a meeting for tomorrow at 2pm"
- Query: "Send an email to john@example.com"
- Query: "List my calendar events"

#### Step 2: Semantic Routing
```
UI -> SemanticRouter: Route Query
SemanticRouter -> SemanticRouter: Analyze Query (Check Route Maps)
```

**What Happens:**
1. UI sends query to SemanticRouter
2. SemanticRouter uses OpenAI embeddings to convert query to vector
3. Compares query vector against route maps (predefined utterances)
4. Calculates confidence score for each route
5. Selects best matching route

**Route Maps Example:**
```json
{
  "routes": [
    {
      "name": "EVENT_MANAGEMENT_FLOW",
      "tool": "calendar_create",
      "utterances": [
        "meeting", "schedule", "calendar", "appointment", "event",
        "book", "reserve", "create meeting", "add event"
      ]
    },
    {
      "name": "EMAIL_MANAGEMENT_FLOW",
      "tool": "gmail_send",
      "utterances": [
        "email", "send", "inbox", "message", "reply", "forward"
      ]
    }
  ]
}
```

**Confidence Calculation:**
- High confidence (≥ 0.7): Strong match, proceed with specific connector
- Low confidence (< 0.7): Weak match, use generic HTTP tool

---

### Phase 2: Connector Selection & Configuration

#### Step 3: Route to Connector (High Confidence Path)
```
SemanticRouter -> ConnectorMgr: Route to Connector
ConnectorMgr -> ConnectorMgr: Load Connector Config
```

**What Happens:**
1. SemanticRouter identifies matching connector (e.g., `google_calendar`)
2. ConnectorMgr loads connector configuration from registry
3. Connector config includes:
   - Endpoints (API paths, methods, parameters)
   - Authentication requirements
   - Rate limits
   - Semantic routing config
   - Tool wrapper config

**Connector Config Example:**
```typescript
{
  id: 'google_calendar',
  name: 'Google Calendar',
  baseUrl: 'https://www.googleapis.com/calendar/v3',
  endpoints: {
    createEvent: {
      path: '/calendars/{calendarId}/events',
      method: 'POST'
    }
  },
  semanticRouting: {
    enabled: true,
    confidenceThreshold: 0.7
  },
  toolWrapper: {
    enabled: true,
    crewName: 'Google Calendar Agent'
  }
}
```

---

### Phase 3: Execution Path Selection

#### Step 4: Tool Wrapper vs Direct Execution

**Path A: Tool Wrapper Enabled**
```
ConnectorMgr -> ToolWrapper: Create CrewAI Tool
ToolWrapper -> ToolWrapper: Wrap API Endpoints
ToolWrapper -> ToolWrapper: Create Agent Crew
ToolWrapper -> ToolWrapper: Execute with LLM
```

**What Happens (AI-Powered Execution):**
1. **Create CrewAI Tool**: Convert API endpoints into CrewAI tools
   ```typescript
   const tool = new CrewAI.Tool({
     name: 'google_calendar_create_event',
     description: 'Create a calendar event in Google Calendar',
     func: async (params) => {
       return await executeCalendarAPI('createEvent', params)
     }
   })
   ```

2. **Wrap API Endpoints**: All connector endpoints become tools
   - `listEvents` → Tool
   - `createEvent` → Tool
   - `updateEvent` → Tool

3. **Create Agent Crew**: Create AI agent with tools
   ```typescript
   const agent = new CrewAI.Agent({
     role: 'Calendar Management Specialist',
     goal: 'Help users manage their Google Calendar events',
     tools: [calendarTools],
     llm: 'gpt-4'
   })
   ```

4. **Execute with LLM**: LLM interprets query and calls appropriate tools
   - Query: "Schedule a meeting for tomorrow at 2pm"
   - LLM understands: needs to create event
   - LLM extracts: date (tomorrow), time (2pm)
   - LLM calls: `createEvent` tool with extracted parameters

**Benefits:**
- Natural language understanding
- Automatic parameter extraction
- Intelligent tool selection
- Handles complex queries

**Path B: Direct Execution**
```
ConnectorMgr -> ConnectorMgr: Validate Config
```

**What Happens (Direct API Call):**
1. Validate connector configuration
2. Extract parameters from query (if structured)
3. Prepare API request directly
4. Skip LLM processing

**When Used:**
- Tool wrapper disabled
- Simple, structured queries
- Performance-critical scenarios

---

### Phase 4: Authentication

#### Step 5: Credential Retrieval
```
ConnectorMgr -> CredentialMgr: Get Credentials
CredentialMgr -> CredentialMgr: Check Token Expiry
```

**What Happens:**
1. ConnectorMgr requests credentials for connector
2. CredentialMgr retrieves encrypted credentials from database
3. Decrypts credentials
4. Checks if OAuth token is expired

**Token Expiry Check:**
```typescript
const expiresAt = credential.expiresAt
const now = new Date()
const bufferTime = 5 * 60 * 1000 // 5 minutes

if (expiresAt.getTime() - now.getTime() < bufferTime) {
  // Token expires soon or expired
}
```

#### Step 6: Token Refresh (If Needed)
```
alt Token Expired
    CredentialMgr -> CredentialMgr: Refresh Token
end
```

**What Happens:**
1. If token expired or expiring soon:
   - Use refresh token to get new access token
   - Update credential in database
   - Return new token

2. If token valid:
   - Return existing token

**Token Refresh Flow:**
```typescript
const response = await fetch('https://oauth2.googleapis.com/token', {
  method: 'POST',
  body: new URLSearchParams({
    client_id: config.clientId,
    client_secret: config.clientSecret,
    refresh_token: credential.refreshToken,
    grant_type: 'refresh_token'
  })
})

const newToken = await response.json()
// Update credential with new token
```

#### Step 7: Return Credentials
```
CredentialMgr -> ConnectorMgr: Return Credentials
```

**What Happens:**
- CredentialMgr returns valid credentials (access token, API key, etc.)
- ConnectorMgr uses credentials for API authentication

---

### Phase 5: Production Checks

#### Step 8: Rate Limiting Check
```
ConnectorMgr -> ConnectorMgr: Check Rate Limit
```

**What Happens:**
1. Check if request exceeds rate limit
2. Rate limit config example:
   ```typescript
   {
     requests: 100,  // 100 requests
     window: 60     // per 60 seconds
   }
   ```

3. Implementation:
   - Use Redis sliding window log algorithm
   - Track requests per connector/user
   - Block if limit exceeded

**Rate Limit Check:**
```typescript
const key = `ratelimit:${connectorId}:${userId}`
const allowed = await rateLimiter.checkLimit(key, 100, 60)

if (!allowed) {
  throw new RateLimitError('Rate limit exceeded')
}
```

#### Step 9: Circuit Breaker Check
```
ConnectorMgr -> ConnectorMgr: Check Circuit Breaker
```

**What Happens:**
1. Check circuit breaker state:
   - **Closed**: Normal operation, allow requests
   - **Open**: Too many failures, block requests temporarily
   - **Half-Open**: Testing if service recovered

2. Circuit Breaker Config:
   ```typescript
   {
     failureThreshold: 5,      // Open after 5 failures
     successThreshold: 2,      // Close after 2 successes
     timeout: 30000,            // 30s timeout
     resetTimeout: 60000        // Wait 60s before retry
   }
   ```

3. Implementation:
   - Track success/failure counts
   - Open circuit if failures exceed threshold
   - Automatically close after reset timeout

**Circuit Breaker Check:**
```typescript
const circuitBreaker = getCircuitBreaker(connectorId)

if (circuitBreaker.isOpen()) {
  throw new CircuitBreakerOpenError('Circuit breaker is open')
}
```

---

### Phase 6: Decision Point - Production Checks

#### Step 10: Error Paths (Circuit Breaker Open)
```
alt Circuit Breaker Open
    ConnectorMgr -> UI: Error: Circuit Breaker Open
```

**What Happens:**
- Circuit breaker is open (service is down/unstable)
- Return error immediately without calling API
- Prevents cascading failures

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "CIRCUIT_BREAKER_OPEN",
    "message": "Service temporarily unavailable",
    "retryAfter": 60
  }
}
```

#### Step 11: Error Paths (Rate Limit Exceeded)
```
else Rate Limit Exceeded
    ConnectorMgr -> UI: Error: Rate Limit Exceeded
```

**What Happens:**
- Rate limit exceeded
- Return error with retry-after information

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "retryAfter": 30
  }
}
```

---

### Phase 7: API Execution

#### Step 12: Execute Request (Success Path)
```
else Proceed
    ConnectorMgr -> APIClient: Execute Request
    APIClient -> ExternalAPI: HTTP Request
    ExternalAPI -> APIClient: Response
```

**What Happens:**
1. **ConnectorMgr** prepares request:
   - Build URL with path parameters
   - Add query parameters
   - Format request body
   - Add authentication headers

2. **APIClient** executes:
   ```typescript
   const response = await fetch(url, {
     method: 'POST',
     headers: {
       'Authorization': `Bearer ${accessToken}`,
       'Content-Type': 'application/json'
     },
     body: JSON.stringify(eventData)
   })
   ```

3. **ExternalAPI** processes and responds:
   - Validates request
   - Processes action
   - Returns result

**Example Request:**
```http
POST https://www.googleapis.com/calendar/v3/calendars/primary/events
Authorization: Bearer ya29.a0AfH6...
Content-Type: application/json

{
  "summary": "Team Meeting",
  "start": {
    "dateTime": "2025-01-02T14:00:00Z"
  },
  "end": {
    "dateTime": "2025-01-02T15:00:00Z"
  }
}
```

**Example Response:**
```json
{
  "id": "event123",
  "summary": "Team Meeting",
  "start": {
    "dateTime": "2025-01-02T14:00:00Z"
  },
  "end": {
    "dateTime": "2025-01-02T15:00:00Z"
  },
  "status": "confirmed"
}
```

---

### Phase 8: Response Handling

#### Step 13: Success Path
```
alt Success
    APIClient -> ConnectorMgr: Success Response
    ConnectorMgr -> ConnectorMgr: Update Circuit Breaker
    ConnectorMgr -> ConnectorMgr: Cache Result
    ConnectorMgr -> UI: Return Result
```

**What Happens:**
1. **Update Circuit Breaker**: Record success
   ```typescript
   circuitBreaker.recordSuccess()
   // If in half-open state and successThreshold reached, close circuit
   ```

2. **Cache Result**: Store response for future requests
   ```typescript
   const cacheKey = `connector:${connectorId}:${endpoint}:${paramsHash}`
   await redis.setex(cacheKey, 300, JSON.stringify(response))
   // Cache for 5 minutes (300 seconds)
   ```

3. **Return Result**: Send to UI
   ```json
   {
     "success": true,
     "data": {
       "eventId": "event123",
       "summary": "Team Meeting",
       "status": "confirmed"
     }
   }
   ```

#### Step 14: Error Path
```
else Error
    APIClient -> ConnectorMgr: Error Response
    ConnectorMgr -> ConnectorMgr: Retry Logic
    ConnectorMgr -> ConnectorMgr: Update Circuit Breaker
    ConnectorMgr -> UI: Return Error
```

**What Happens:**
1. **Retry Logic**: Attempt retry for transient errors
   ```typescript
   const retryableErrors = [429, 500, 502, 503, 504]
   
   if (retryableErrors.includes(response.status)) {
     // Exponential backoff
     const delay = Math.min(1000 * Math.pow(2, attempt), 10000)
     await sleep(delay)
     return await retryRequest()
   }
   ```

2. **Update Circuit Breaker**: Record failure
   ```typescript
   circuitBreaker.recordFailure()
   // If failures exceed threshold, open circuit
   ```

3. **Return Error**: Send error to UI
   ```json
   {
     "success": false,
     "error": {
       "code": "API_ERROR",
       "message": "Failed to create event",
       "statusCode": 500
     }
   }
   ```

---

### Phase 9: Fallback Path (Low Confidence)

#### Step 15: Generic HTTP Tool (Low Confidence)
```
else Low Confidence
    SemanticRouter -> UI: Fallback: Generic HTTP Tool
    UI -> ConnectorMgr: Use Generic HTTP Block
    ConnectorMgr -> APIClient: Execute Generic Request
    APIClient -> ExternalAPI: HTTP Request
    ExternalAPI -> APIClient: Response
    APIClient -> UI: Return Result
```

**What Happens:**
1. **Semantic Routing** returns low confidence (< 0.7)
2. **Fallback to Generic HTTP Tool**:
   - User provides API URL directly
   - Manual configuration
   - Generic HTTP request block

3. **Generic Request**:
   ```typescript
   {
     method: 'POST',
     url: 'https://api.example.com/endpoint',
     headers: {
       'Authorization': 'Bearer token'
     },
     body: {
       // User-provided body
     }
   }
   ```

**When Used:**
- Unsupported/unknown APIs
- Custom integrations
- Low confidence semantic matches
- Testing/debugging

---

## Decision Points & Alternative Paths

### Decision Point 1: High vs Low Confidence

**High Confidence (≥ 0.7):**
- ✅ Use specific connector
- ✅ Enable tool wrapper (if configured)
- ✅ Use optimized API calls

**Low Confidence (< 0.7):**
- ⚠️ Fallback to generic HTTP tool
- ⚠️ Manual configuration required
- ⚠️ No semantic routing benefits

### Decision Point 2: Tool Wrapper vs Direct Execution

**Tool Wrapper Enabled:**
- ✅ AI-powered execution
- ✅ Natural language understanding
- ✅ Automatic parameter extraction
- ⚠️ Higher latency (LLM processing)
- ⚠️ Higher cost (LLM API calls)

**Direct Execution:**
- ✅ Fast execution
- ✅ Lower cost
- ✅ Predictable behavior
- ⚠️ Requires structured input
- ⚠️ No natural language understanding

### Decision Point 3: Circuit Breaker State

**Closed (Normal):**
- ✅ Allow requests
- ✅ Track success/failure

**Open (Failing):**
- ❌ Block requests
- ❌ Return error immediately
- ✅ Prevents cascading failures

**Half-Open (Testing):**
- ⚠️ Allow limited requests
- ⚠️ Testing if service recovered
- ✅ Close if successful
- ❌ Reopen if failing

### Decision Point 4: Rate Limit Status

**Within Limit:**
- ✅ Allow request
- ✅ Track request count

**Exceeded:**
- ❌ Block request
- ❌ Return rate limit error
- ✅ Provide retry-after time

---

## Production Features

### 1. **Rate Limiting**
- **Purpose**: Prevent API abuse and stay within quotas
- **Implementation**: Redis-based sliding window
- **Config**: Per-connector limits
- **Response**: 429 status with retry-after header

### 2. **Circuit Breaker**
- **Purpose**: Prevent cascading failures
- **Implementation**: State machine (Closed → Open → Half-Open)
- **Config**: Failure threshold, reset timeout
- **Response**: 503 status with circuit breaker error

### 3. **Caching**
- **Purpose**: Reduce API calls, improve performance
- **Implementation**: Redis cache with TTL
- **Config**: Per-connector cache settings
- **Invalidation**: On data mutations

### 4. **Retry Logic**
- **Purpose**: Handle transient failures
- **Implementation**: Exponential backoff
- **Config**: Max attempts, backoff strategy
- **Retryable**: 429, 500, 502, 503, 504

### 5. **Token Refresh**
- **Purpose**: Maintain valid authentication
- **Implementation**: Automatic refresh before expiry
- **Config**: Buffer time (5 minutes)
- **Failure**: Return authentication error

---

## Error Handling

### Error Types

1. **Circuit Breaker Open**
   - Code: `CIRCUIT_BREAKER_OPEN`
   - Status: 503
   - Retry: After reset timeout

2. **Rate Limit Exceeded**
   - Code: `RATE_LIMIT_EXCEEDED`
   - Status: 429
   - Retry: After rate limit window

3. **Authentication Error**
   - Code: `AUTHENTICATION_ERROR`
   - Status: 401
   - Action: Re-authenticate

4. **API Error**
   - Code: `API_ERROR`
   - Status: 500, 502, 503, 504
   - Retry: With exponential backoff

5. **Validation Error**
   - Code: `VALIDATION_ERROR`
   - Status: 400
   - Action: Fix request parameters

---

## Example Scenarios

### Scenario 1: High Confidence with Tool Wrapper

**User Query:** "Schedule a meeting for tomorrow at 2pm with the team"

**Flow:**
1. SemanticRouter: Confidence 0.92 → `google_calendar` connector
2. ToolWrapper: Creates agent with calendar tools
3. LLM: Extracts date (tomorrow), time (2pm), attendees (team)
4. API Call: `createEvent` with extracted parameters
5. Result: Event created successfully

### Scenario 2: High Confidence with Direct Execution

**User Query:** "List my calendar events for today"

**Flow:**
1. SemanticRouter: Confidence 0.88 → `google_calendar` connector
2. Direct Execution: Validates config, extracts "today" date
3. API Call: `listEvents` with date filter
4. Result: List of events

### Scenario 3: Low Confidence Fallback

**User Query:** "Call my custom API at https://api.example.com/data"

**Flow:**
1. SemanticRouter: Confidence 0.35 → Low confidence
2. Fallback: Generic HTTP tool
3. User: Manually configures URL and parameters
4. API Call: Generic HTTP request
5. Result: API response

### Scenario 4: Circuit Breaker Open

**User Query:** "Create a calendar event"

**Flow:**
1. SemanticRouter: Routes to `google_calendar`
2. Circuit Breaker: Check → OPEN (service failing)
3. Error: Return immediately without API call
4. Result: Error message with retry time

---

## Summary

The Third-Party API Integration Flow provides:

1. **Intelligent Routing**: Semantic routing matches queries to appropriate connectors
2. **Flexible Execution**: Tool wrapper for AI-powered execution or direct execution for speed
3. **Secure Authentication**: Automatic token refresh and credential management
4. **Production Ready**: Rate limiting, circuit breakers, caching, retry logic
5. **Error Handling**: Comprehensive error handling with retry strategies
6. **Fallback Support**: Generic HTTP tool for unsupported APIs

This flow ensures reliable, secure, and efficient integration with third-party APIs while providing excellent user experience through intelligent routing and AI-powered execution.

---

## UI Flow Patterns (OpenMetadata & ShaderFrog)

### OpenMetadata Connector Discovery Flow

**Pattern**: Visual connector browser with categorized browsing

**UI Flow:**
1. **Landing**: Browse connectors by category or search
2. **Selection**: Click connector card to view details
3. **Details Modal**: See description, use cases, authentication requirements
4. **Connect**: Click "Connect" button to start setup wizard
5. **Setup Wizard**: Guided configuration through multiple steps
6. **Test**: Validate connection before deploying
7. **Deploy**: Activate connector and start syncing

### ShaderFrog Visual Composition Flow

**Pattern**: Node-based editor with inline parameter controls

**UI Flow:**
1. **Palette**: Browse connectors/blocks in categorized sidebar
2. **Drag**: Drag connector from palette to canvas
3. **Configure**: Adjust parameters directly on node (inline controls)
4. **Connect**: Drag from output to input to create data flow
5. **Preview**: See real-time preview of API request/response
6. **Execute**: Run workflow and see execution status per node

### Combined UI Flow for API Integration

**Best of Both Worlds:**
- OpenMetadata's connector discovery and setup wizard
- ShaderFrog's visual composition and inline controls
- Real-time preview and status indicators
- Visual feedback throughout the configuration process

---

## Related Documentation

- **Production System Design**: See `PRODUCTION_SYSTEM_DESIGN.md` for complete architecture
- **Third-Party API Structure**: See `THIRD_PARTY_API_STRUCTURE.md` for connector structure
- **System Architecture Diagrams**: See `SYSTEM_ARCHITECTURE_DIAGRAMS.md` for visual diagrams
- **API Integration Patterns**: See `THIRD_PARTY_API_INTEGRATION_PATTERNS.md` for integration patterns
- **UI Flow Patterns**: See `OPENMETADATA_SHADERFROG_UI_PATTERNS.md` for detailed UI patterns from OpenMetadata and ShaderFrog

