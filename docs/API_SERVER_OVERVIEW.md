# API Server Overview - How It Works

Complete explanation of the Google Suite API Server in plain English.

## What This API Server Is About

This is a REST API server that connects external tools like Sim or Flowise to Google Suite operations through CrewAI. Think of it as a smart translator that takes structured tool requests, converts them into natural language that AI agents can understand, and then executes Google Suite tasks intelligently.

## The Big Picture

The server acts as a bridge between two worlds:

1. **External Systems**: Tools like Sim/Flowise that send structured tool calls
2. **CrewAI Agents**: Intelligent AI agents that understand natural language and can use Google Suite tools

The server translates between these two worlds, making it possible for external systems to use Google Suite tools without needing to understand how CrewAI works.

## How It Works

### The Core Components

The server has three main parts:

1. **Tool Mapping System**: Maps 27 different tool IDs (like gmail_read, google_calendar_create) to specific CrewAI flow names (like EMAIL_MANAGEMENT_FLOW, EVENT_MANAGEMENT_FLOW)

2. **Query Converter**: Takes structured parameters and converts them into natural language queries that CrewAI agents can understand

3. **Flow Executor**: Runs the appropriate CrewAI flow with the right agents and tools to complete the task

## The Complete Request Flow

### Step 1: Server Startup

When the server starts up:

- Checks environment variables (OpenAI API key, Gmail credentials)
- Does NOT initialize CrewAI flows immediately (lazy loading for fast startup)
- Displays available tools and their status
- Server is ready in about 1-2 seconds

### Step 2: Receiving a Request

When a client (like Sim/Flowise) sends a request to the main endpoint:

**Example Request:**
```json
{
  "toolId": "gmail_read",
  "params": {
    "hours": 24,
    "unread_only": true,
    "maxResults": 10
  }
}
```

### Step 3: Validating the Request

The server checks:
- Does the toolId exist in the mapping?
- If not found, returns an error with available tools
- If valid, continues processing

### Step 4: Converting Parameters to Natural Language

This is where the magic happens. The server converts structured parameters into a natural language query:

**Example:**
- Input: toolId "gmail_read" with params {"hours": 24, "unread_only": true}
- Output: "Read unread emails from the last 24 hours, maximum 10 results"

The convert_params_to_user_query function handles all 27 tools, each with specific conversion logic.

### Step 5: Determining Which Crew to Use

The server looks up which CrewAI flow should handle this request:
- gmail_read maps to EMAIL_MANAGEMENT_FLOW
- google_calendar_create maps to EVENT_MANAGEMENT_FLOW
- google_drive_upload maps to DRIVE_MANAGEMENT_FLOW

### Step 6: Lazy Loading the CrewAI Flow

First request:
- The GoogleSuiteFlow is initialized (takes 10-30 seconds)
- This loads all the agents, tools, and semantic routers
- The flow is cached for future requests

Subsequent requests:
- Uses the cached flow (very fast)

### Step 7: Executing the CrewAI Flow

The server:
- Gets or creates the GoogleSuiteFlow instance
- Runs the flow with the natural language query
- Uses a thread pool executor to avoid blocking the async server
- Passes the query, crew name, and flow name to the flow

### Step 8: Processing the Result

The server:
- Parses the CrewAI result into a standard format
- Handles different result types (strings, objects, dictionaries)
- Formats it properly for the client

### Step 9: Returning the Response

The server returns a structured response:

**Response Format:**
```json
{
  "success": true,
  "output": {
    "data": "...",
    "status": "success",
    "message": "..."
  },
  "metadata": {
    "tool_id": "gmail_read",
    "crew_name": "EMAIL_MANAGEMENT_FLOW",
    "execution_time_seconds": 15.23,
    "timestamp": "2024-..."
  }
}
```

## Available Endpoints

The server provides three main endpoints:

1. **GET /health** - Health check endpoint to verify server is running
2. **GET /api/tools/google-suite/list** - Lists all 27 available tools
3. **POST /api/tools/google-suite/execute** - Main endpoint for executing tools

## Key Features

1. **Lazy Initialization**: Server starts fast, flows initialize on first request
2. **Caching**: Flow instances are cached using singleton pattern
3. **Async Execution**: Uses thread pool executors to run synchronous CrewAI code without blocking
4. **Error Handling**: Comprehensive error catching and reporting
5. **CORS Support**: Allows requests from Sim/Flowise frontend

## Performance Characteristics

- Server startup: 1-2 seconds
- First tool execution: 10-30 seconds (initializes flow)
- Subsequent executions: Fast (flow is cached)

## Flow Diagram

Here is a visual representation of how the API server processes requests:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT (Sim/Flowise)                          │
│                                                                   │
│  Sends POST request:                                            │
│  {                                                               │
│    "toolId": "gmail_read",                                      │
│    "params": {"hours": 24, "unread_only": true}                 │
│  }                                                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ HTTP POST
                           │ /api/tools/google-suite/execute
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API SERVER (api_server.py)                    │
│                                                                   │
│  Step 1: Validate Request                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Check if toolId exists in TOOL_TO_CREW_MAPPING          │   │
│  │ If not found → Return error with available tools         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  Step 2: Convert Parameters to Natural Language                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ convert_params_to_user_query()                          │   │
│  │ Input:  {"hours": 24, "unread_only": true}              │   │
│  │ Output: "Read unread emails from the last 24 hours..."   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  Step 3: Determine Crew Flow                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Lookup: toolId → Crew Name                               │   │
│  │ "gmail_read" → "EMAIL_MANAGEMENT_FLOW"                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  Step 4: Get or Create Flow (Lazy Loading)                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ get_google_suite_flow()                                  │   │
│  │ ├─ First time: Initialize GoogleSuiteFlow (10-30s)     │   │
│  │ │   - Load agents                                       │   │
│  │ │   - Load tools                                        │   │
│  │ │   - Initialize semantic routers                       │   │
│  │ │   - Cache flow instance                               │   │
│  │ └─ Subsequent: Use cached flow (fast)                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  Step 5: Execute Flow in Thread Pool                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ flow.kickoff(inputs={                                    │   │
│  │   "user_query": "Read unread emails...",                 │   │
│  │   "crew_name": "EMAIL_MANAGEMENT_FLOW",                  │   │
│  │   "flow_name": "EMAIL_MANAGEMENT_FLOW"                   │   │
│  │ })                                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  Step 6: Parse Result                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ parse_crewai_result()                                    │   │
│  │ Convert CrewAI result to standard format                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  Step 7: Format Response                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ {                                                       │   │
│  │   "success": true,                                     │   │
│  │   "output": {...},                                     │   │
│  │   "metadata": {...}                                    │   │
│  │ }                                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ HTTP Response
                           │ JSON
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT (Sim/Flowise)                          │
│                                                                   │
│  Receives response with:                                        │
│  - Success status                                               │
│  - Email data                                                   │
│  - Metadata (execution time, etc.)                             │
└─────────────────────────────────────────────────────────────────┘
```

### Detailed Component Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    CREWAI FLOW EXECUTION                         │
│                                                                   │
│  GoogleSuiteFlow.kickoff()                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                           │   │
│  │  Semantic Router                                         │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │ Analyzes natural language query                  │   │   │
│  │  │ Routes to appropriate agent                      │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                    │                                     │   │
│  │                    ▼                                     │   │
│  │  Email Management Agent                                 │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │ Receives: "Read unread emails..."                │   │   │
│  │  │ Decides: Use Gmail Read Tool                      │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                    │                                     │   │
│  │                    ▼                                     │   │
│  │  Gmail Read Tool                                        │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │ Connects to Gmail API                            │   │   │
│  │  │ Reads emails using SMTP credentials              │   │   │
│  │  │ Returns email data                                │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                    │                                     │   │
│  │                    ▼                                     │   │
│  │  Result: Email data in structured format             │   │
│  │                                                           │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Request Flow Summary

```
External System
    │
    │ POST /api/tools/google-suite/execute
    │ {
    │   "toolId": "gmail_read",
    │   "params": {...}
    │ }
    │
    ▼
┌──────────────────────────────────────┐
│  API Server (FastAPI)                │
│  ┌────────────────────────────────┐ │
│  │ 1. Validate toolId             │ │
│  │ 2. Convert params to query      │ │
│  │ 3. Get crew name from mapping   │ │
│  │ 4. Get/create flow (lazy)       │ │
│  │ 5. Execute flow in thread pool │ │
│  │ 6. Parse result                 │ │
│  │ 7. Format response              │ │
│  └────────────────────────────────┘ │
└──────────────┬───────────────────────┘
               │
               │ flow.kickoff()
               ▼
┌──────────────────────────────────────┐
│  CrewAI Flow                         │
│  ┌────────────────────────────────┐ │
│  │ Semantic Router                │ │
│  │   ↓                            │ │
│  │ Agent (Email Management)      │ │
│  │   ↓                            │ │
│  │ Tool (Gmail Read)             │ │
│  │   ↓                            │ │
│  │ Google API                     │ │
│  │   ↓                            │ │
│  │ Result                         │ │
│  └────────────────────────────────┘ │
└──────────────┬───────────────────────┘
               │
               │ Returns result
               ▼
┌──────────────────────────────────────┐
│  API Server                           │
│  Formats and returns JSON response    │
└──────────────┬───────────────────────┘
               │
               │ HTTP Response
               ▼
        External System
```

## Example Complete Flow

Here is a complete example of what happens when you send a request:

1. Client sends: {"toolId": "gmail_read", "params": {"hours": 24}}
2. Server validates: Tool exists
3. Server converts: "Read unread emails from the last 24 hours, maximum 10 results"
4. Server determines: Use EMAIL_MANAGEMENT_FLOW
5. Server initializes flow (first time only): 10-30 seconds
6. CrewAI executes: Agents read emails using Gmail tools
7. Server formats result: Standard JSON response
8. Server returns: Success with email data and metadata

## Requirements for Google Suite Tools

### Gmail Tools

**Required:**
- GMAIL_SMTP_EMAIL environment variable (your Gmail address)
- GMAIL_SMTP_PASSWORD environment variable (Gmail App Password, not regular password)

**How to get Gmail App Password:**
1. Go to Google Account settings
2. Enable 2-Step Verification
3. Generate an App Password for "Mail"
4. Use that 16-character password in GMAIL_SMTP_PASSWORD

**Available Tools:**
- gmail_send
- gmail_read
- gmail_search
- gmail_draft
- gmail_labels
- gmail_reply

### Google Calendar Tools

**Required:**
- service_account.json file in the project root directory
- OWNER_EMAIL environment variable (the email address of the calendar owner)

**How to set up service account:**
1. Go to Google Cloud Console
2. Create a new project or select existing one
3. Enable Google Calendar API
4. Create a Service Account
5. Download the service account JSON key file
6. Save it as service_account.json in the project root
7. Share your calendar with the service account email address

**Available Tools:**
- google_calendar_create
- google_calendar_list
- google_calendar_get
- google_calendar_update
- google_calendar_delete
- google_calendar_quick_add
- google_calendar_freebusy

### Google Drive Tools

**Required:**
- service_account.json file in the project root directory
- OWNER_EMAIL environment variable (the email address of the Drive owner)

**How to set up service account:**
1. Go to Google Cloud Console
2. Create a new project or select existing one
3. Enable Google Drive API
4. Create a Service Account
5. Download the service account JSON key file
6. Save it as service_account.json in the project root
7. Share any folders/files you want to access with the service account email address

**Note:** The service_account.json file location is checked in the google_suite/tools directory. You may need to place it in both the project root and the tools directory.

**Available Tools:**
- google_drive_upload
- google_drive_download
- google_drive_list
- google_drive_share
- google_drive_create_folder
- google_drive_move
- google_drive_delete

### Google Sheets Tools

**Status:** Defined in API but not fully implemented yet

**What would be required (when implemented):**
- service_account.json file
- OWNER_EMAIL environment variable
- Google Sheets API enabled in Google Cloud Console

**Planned Tools:**
- google_sheets_read
- google_sheets_write
- google_sheets_update
- google_sheets_append

### Google Docs Tools

**Status:** Defined in API but not fully implemented yet

**What would be required (when implemented):**
- service_account.json file
- OWNER_EMAIL environment variable
- Google Docs API enabled in Google Cloud Console

**Planned Tools:**
- google_docs_read
- google_docs_write
- google_docs_create

## Summary

This API server is a translation layer that:

- Receives structured tool requests from external systems
- Converts them into natural language queries
- Routes them to the appropriate CrewAI flow
- Executes them using intelligent AI agents
- Returns formatted results

It enables external systems like Sim/Flowise to use Google Suite tools through CrewAI without needing to understand the CrewAI implementation details. The server handles all the complexity of agent coordination, tool selection, and result formatting.

