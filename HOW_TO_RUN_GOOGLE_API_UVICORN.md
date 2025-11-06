# How to Run Google Suite API with Uvicorn

Complete guide for running the Google Suite Tool Wrapper API server using **uvicorn only**.

## Quick Start

### Basic Command (Uvicorn Only)

```bash
uv run python -m uvicorn api_server:app --host 0.0.0.0 --port 8002 --reload
```

### Important: Use `python -m uvicorn`

**DO NOT use `uv run uvicorn` directly - it will fail!**

**This will fail:**
```bash
uv run uvicorn api_server:app --host 0.0.0.0 --port 8002
# Error: "Failed to canonicalize script path"
```

**Always use this:**
```bash
uv run python -m uvicorn api_server:app --host 0.0.0.0 --port 8002 --reload
```

## Uvicorn Commands

### Development Mode (Recommended)

```bash
uv run python -m uvicorn api_server:app \
    --host 0.0.0.0 \
    --port 8002 \
    --reload
```

**Features:**
- Auto-reload on file changes
- Perfect for development
- Server restarts automatically when code changes

### Production Mode (Single Worker)

```bash
uv run python -m uvicorn api_server:app \
    --host 0.0.0.0 \
    --port 8002 \
    --log-level info
```

### Production Mode (Multiple Workers)

```bash
uv run python -m uvicorn api_server:app \
    --host 0.0.0.0 \
    --port 8002 \
    --workers 4 \
    --log-level info \
    --timeout-keep-alive 5
```

**Note:** With multiple workers, each worker has its own instance of the flow cache. First request to each worker will initialize the flow separately.

## Server Details

- **Port**: 8002 (configurable via `CREWAI_API_PORT` environment variable)
- **Host**: 0.0.0.0 (all interfaces)
- **URL**: http://localhost:8002
- **Server**: Uvicorn

## Available Endpoints

### Health Check
```
GET http://localhost:8002/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "CrewAI Tool Wrapper API",
  "timestamp": "2024-...",
  "version": "1.0.0"
}
```

**Test:**
```powershell
Invoke-WebRequest -Uri http://localhost:8002/health
```

### List Available Tools
```
GET http://localhost:8002/api/tools/google-suite/list
```

**Response:**
```json
{
  "tools": [
    "google_calendar_create",
    "google_calendar_list",
    "gmail_send",
    "gmail_read",
    ...
  ],
  "mappings": {
    "google_calendar_create": "EVENT_MANAGEMENT_FLOW",
    "gmail_read": "EMAIL_MANAGEMENT_FLOW",
    ...
  },
  "total": 27
}
```

**Test:**
```powershell
Invoke-RestMethod -Uri http://localhost:8002/api/tools/google-suite/list
```

### Execute Tool
```
POST http://localhost:8002/api/tools/google-suite/execute
```

**Request Body:**
```json
{
  "toolId": "gmail_read",
  "params": {
    "hours": 24,
    "unread_only": true,
    "maxResults": 10
  },
  "userQuery": "read my unread emails from the last 24 hours"  // Optional
}
```

**Response:**
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
    "execution_time_seconds": 15.2,
    "timestamp": "2024-..."
  }
}
```

## API Documentation

Once the server is running, access interactive API documentation:

- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc

## Available Google Suite Tools (27 Total)

### Google Calendar Tools (7)
- `google_calendar_create` - Create calendar event
- `google_calendar_list` - List calendar events
- `google_calendar_get` - Get specific event
- `google_calendar_update` - Update event
- `google_calendar_delete` - Delete event
- `google_calendar_quick_add` - Quick add event
- `google_calendar_freebusy` - Check free/busy status

### Gmail Tools (6)
- `gmail_send` - Send email
- `gmail_read` - Read emails
- `gmail_search` - Search emails
- `gmail_draft` - Create draft
- `gmail_labels` - Manage labels
- `gmail_reply` - Reply to email

### Google Drive Tools (7)
- `google_drive_upload` - Upload file
- `google_drive_download` - Download file
- `google_drive_list` - List files
- `google_drive_share` - Share file
- `google_drive_create_folder` - Create folder
- `google_drive_move` - Move file/folder
- `google_drive_delete` - Delete file/folder

### Google Sheets Tools (4) - Defined but not fully implemented
- `google_sheets_read` - Read spreadsheet data
- `google_sheets_write` - Write to spreadsheet
- `google_sheets_update` - Update spreadsheet
- `google_sheets_append` - Append to spreadsheet

### Google Docs Tools (3) - Defined but not fully implemented
- `google_docs_read` - Read document
- `google_docs_write` - Write to document
- `google_docs_create` - Create document

## Environment Variables

Required in `.env` file:

```bash
# OpenAI API Key (Required)
OPENAI_API_KEY=sk-...

# Gmail SMTP (Required for Gmail tools)
GMAIL_SMTP_EMAIL=your-email@gmail.com
GMAIL_SMTP_PASSWORD=your-app-password

# Server Configuration (Optional)
CREWAI_API_PORT=8002
CREWAI_API_HOST=0.0.0.0
ENVIRONMENT=development  # or production

# Google Service Account (Required for Calendar/Drive tools)
# Place service_account.json in project root
```

**Note:** When using uvicorn with `--reload`, the reload flag takes precedence over `ENVIRONMENT` setting.

## Uvicorn Command Options

### Basic Options

| Option | Description | Example |
|--------|-------------|---------|
| `--host` | Host to bind to | `0.0.0.0` (all interfaces) or `127.0.0.1` (localhost only) |
| `--port` | Port number | `8002` |
| `--reload` | Auto-reload on file changes | Enable for development |
| `--workers` | Number of worker processes | `4` for production |
| `--log-level` | Logging level | `info`, `debug`, `warning`, `error` |

### Advanced Options

| Option | Description | Example |
|--------|-------------|---------|
| `--reload-dir` | Directory to watch for changes | `--reload-dir .` |
| `--reload-include` | Files to include in reload | `--reload-include "*.py"` |
| `--reload-exclude` | Files to exclude from reload | `--reload-exclude "*.pyc"` |
| `--access-log` | Enable access logging | `--access-log` |
| `--no-access-log` | Disable access logging | `--no-access-log` |
| `--timeout-keep-alive` | Keep-alive timeout | `--timeout-keep-alive 5` |

## Complete Command Examples

### Example 1: Development with Auto-Reload

```bash
uv run python -m uvicorn api_server:app \
    --host 0.0.0.0 \
    --port 8002 \
    --reload \
    --reload-dir . \
    --log-level info
```

### Example 2: Development with Debug Logging

```bash
uv run python -m uvicorn api_server:app \
    --host 0.0.0.0 \
    --port 8002 \
    --reload \
    --log-level debug
```

### Example 3: Production Single Worker

```bash
uv run python -m uvicorn api_server:app \
    --host 0.0.0.0 \
    --port 8002 \
    --log-level info \
    --no-access-log
```

### Example 4: Production Multi-Worker

```bash
uv run python -m uvicorn api_server:app \
    --host 0.0.0.0 \
    --port 8002 \
    --workers 4 \
    --log-level info \
    --timeout-keep-alive 5 \
    --no-access-log
```

### Example 5: Custom Port

```bash
uv run python -m uvicorn api_server:app \
    --host 0.0.0.0 \
    --port 9000 \
    --reload
```

### Example 6: Localhost Only (Development)

```bash
uv run python -m uvicorn api_server:app \
    --host 127.0.0.1 \
    --port 8002 \
    --reload
```

## PowerShell Script for Easy Startup

Create `start_with_uvicorn.ps1`:

```powershell
# Start API Server with Uvicorn
$port = if ($env:CREWAI_API_PORT) { $env:CREWAI_API_PORT } else { "8002" }
$host = if ($env:CREWAI_API_HOST) { $env:CREWAI_API_HOST } else { "0.0.0.0" }

Write-Host "=== Starting API Server with Uvicorn ===" -ForegroundColor Green
Write-Host "Port: $port" -ForegroundColor Cyan
Write-Host "Host: $host" -ForegroundColor Cyan
Write-Host "Auto-reload: Enabled" -ForegroundColor Yellow
Write-Host ""

uv run python -m uvicorn api_server:app `
    --host $host `
    --port $port `
    --reload
```

**Usage:**
```powershell
.\start_with_uvicorn.ps1
```

## Testing the API

### Test API Script: test_api_server.py

The project includes a comprehensive test script: `test_api_server.py`

**Location:** `test_api_server.py` (in project root)

**What it tests:**
- Health check endpoint
- List tools endpoint
- Gmail read tool execution
- Calendar list tool execution

**Note:** This is a test client application, not a server. It sends HTTP requests to test the API server. It does not need uvicorn or run as a server itself.

### Running the Automated Test Suite

Run the comprehensive test suite:
```bash
uv run python test_api_server.py
```

This automated test will:
1. **Wait for server** - Checks if server is running on port 8002 (waits up to 30 seconds)
2. **Health Check** - Tests `/health` endpoint
3. **List Tools** - Tests `/api/tools/google-suite/list` endpoint
4. **Gmail Read** - Tests Gmail read tool execution (first request may take 10-30s)
5. **Calendar List** - Tests Calendar list tool execution

**Expected Output:**
```
============================================================
API Server Test Suite
============================================================

[INFO] Waiting for server at http://localhost:8002...
[OK] Server is ready!

[TEST] Health Check...
[OK] Health check passed
   Status: healthy
   Service: CrewAI Tool Wrapper API

[TEST] List Tools...
[OK] List tools passed
   Total tools: 27
   Sample tools: ['google_calendar_create', 'google_calendar_list', ...]

[TEST] Execute Gmail Read Tool...
[OK] Execute tool passed
   Success: True
   Response: ...
   Execution time: 23.00s

[TEST] Execute Calendar List Tool...
[OK] Execute tool passed
   Success: True
   Response: ...

============================================================
Test Summary
============================================================
[OK] Health Check
[OK] List Tools
[OK] Gmail Read
[OK] Calendar List

Total: 4/4 tests passed
============================================================
```

**Test Script Features:**
- Automatically waits for server to be ready (up to 30 seconds)
- Tests all major endpoints
- Shows detailed results for each test
- Provides execution time information
- Handles errors gracefully
- Can be run anytime the server is running

### Manual Testing

#### Test 1: Health Check
```powershell
Invoke-WebRequest -Uri http://localhost:8002/health
```

#### Test 2: List Tools
```powershell
Invoke-RestMethod -Uri http://localhost:8002/api/tools/google-suite/list
```

#### Test 3: Execute Gmail Read Tool
```powershell
$body = @{
    toolId = "gmail_read"
    params = @{
        hours = 24
        unread_only = $true
        maxResults = 5
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8002/api/tools/google-suite/execute `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

#### Test 4: Execute Calendar List Tool
```powershell
$body = @{
    toolId = "google_calendar_list"
    params = @{
        timeMin = "now"
        maxResults = 5
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8002/api/tools/google-suite/execute `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### Testing via Browser/API Documentation

1. **Start the server:**
   ```bash
   uv run python -m uvicorn api_server:app --host 0.0.0.0 --port 8002 --reload
   ```

2. **Open API Documentation:**
   - Go to: http://localhost:8002/docs
   - Interactive Swagger UI with all endpoints

3. **Test Endpoints:**
   - Click on any endpoint (e.g., `/api/tools/google-suite/execute`)
   - Click "Try it out"
   - Enter request body (example below)
   - Click "Execute"
   - View response

**Example Request Body for Swagger UI:**
```json
{
  "toolId": "gmail_read",
  "params": {
    "hours": 24,
    "unread_only": true,
    "maxResults": 5
  }
}
```

## Examples

### Example 1: Read Gmail

```bash
curl -X POST http://localhost:8002/api/tools/google-suite/execute \
  -H "Content-Type: application/json" \
  -d '{
    "toolId": "gmail_read",
    "params": {
      "hours": 24,
      "unread_only": true,
      "maxResults": 5
    }
  }'
```

### Example 2: List Calendar Events

```bash
curl -X POST http://localhost:8002/api/tools/google-suite/execute \
  -H "Content-Type: application/json" \
  -d '{
    "toolId": "google_calendar_list",
    "params": {
      "timeMin": "now",
      "maxResults": 10
    }
  }'
```

### Example 3: Send Email

```bash
curl -X POST http://localhost:8002/api/tools/google-suite/execute \
  -H "Content-Type: application/json" \
  -d '{
    "toolId": "gmail_send",
    "params": {
      "to": "recipient@example.com",
      "subject": "Test Email",
      "body": "This is a test email"
    }
  }'
```

## Performance Notes

### Lazy Loading
The server uses **lazy initialization** for fast startup:

- **Server startup**: ~1-2 seconds (with uvicorn)
- **First tool execution**: 10-30 seconds (initializes GoogleSuiteFlow)
- **Subsequent requests**: Fast (flow is cached)

### First Request
When you execute a tool for the first time, you'll see:
```
[START] Initializing GoogleSuiteFlow (this may take 10-30 seconds)...
[INFO] Loading semantic routers and Google Suite Crew...
[OK] GoogleSuiteFlow initialized successfully in 15.23s
```

This is normal - the flow is being initialized. Subsequent requests will be fast.

## Troubleshooting

### Issue: "Failed to canonicalize script path"

**Problem:** Using `uv run uvicorn` directly instead of `python -m uvicorn`

**Solution:**
```bash
# Wrong
uv run uvicorn api_server:app --host 0.0.0.0 --port 8002

# Correct
uv run python -m uvicorn api_server:app --host 0.0.0.0 --port 8002
```

### Issue: Port Already in Use

```bash
# Check what's using the port
Get-NetTCPConnection -LocalPort 8002

# Use a different port
uv run python -m uvicorn api_server:app --host 0.0.0.0 --port 8003 --reload
```

### Issue: Server Won't Start

1. **Check dependencies:**
   ```bash
   uv sync
   ```

2. **Check environment variables:**
   - Ensure `.env` file exists
   - Verify `OPENAI_API_KEY` is set
   - Verify `GMAIL_SMTP_EMAIL` is set

3. **Check for syntax errors:**
   ```bash
   uv run python -m py_compile api_server.py
   ```

### Issue: Module Not Found

```bash
# Install dependencies
uv sync

# Or install uvicorn
uv pip install uvicorn
```

### Issue: Google Service Account Required

For Calendar and Drive tools, you need `service_account.json` in the project root.

## Production Deployment

For production, use multiple workers:

```bash
uv run python -m uvicorn api_server:app \
    --host 0.0.0.0 \
    --port 8002 \
    --workers 4 \
    --log-level info \
    --timeout-keep-alive 5 \
    --no-access-log
```

**Note:** With multiple workers, each worker has its own instance of the flow cache. First request to each worker will initialize the flow separately.

## Integration with Sim/Flowise

This API is designed to integrate with Sim/Flowise blocks:

1. **Tool Definition**: Each tool (e.g., `gmail_read`) is defined in Sim/Flowise
2. **API Call**: Sim/Flowise sends structured request to `/api/tools/google-suite/execute`
3. **Semantic Routing**: API converts parameters to natural language query
4. **CrewAI Execution**: CrewAI flow processes the query with appropriate tools
5. **Response**: Formatted result returned to Sim/Flowise

## Quick Reference

### Uvicorn Commands

| Scenario | Command |
|----------|---------|
| **Development** | `uv run python -m uvicorn api_server:app --host 0.0.0.0 --port 8002 --reload` |
| **Production (Single)** | `uv run python -m uvicorn api_server:app --host 0.0.0.0 --port 8002 --log-level info` |
| **Production (Multi-Worker)** | `uv run python -m uvicorn api_server:app --host 0.0.0.0 --port 8002 --workers 4 --log-level info` |
| **Localhost Only** | `uv run python -m uvicorn api_server:app --host 127.0.0.1 --port 8002 --reload` |
| **Custom Port** | `uv run python -m uvicorn api_server:app --host 0.0.0.0 --port 9000 --reload` |

### Testing Commands

| Command | Description |
|---------|-------------|
| `uv run python test_api_server.py` | Run automated test suite |
| `Invoke-WebRequest -Uri http://localhost:8002/health` | Health check (PowerShell) |
| `http://localhost:8002/docs` | Open API documentation |

### Access URLs

- **Health Check**: http://localhost:8002/health
- **API Documentation**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc
- **List Tools**: http://localhost:8002/api/tools/google-suite/list
- **Execute Tool**: http://localhost:8002/api/tools/google-suite/execute

## Summary

**Always use:**
```bash
uv run python -m uvicorn api_server:app --host 0.0.0.0 --port 8002 --reload
```

**Never use:**
```bash
uv run uvicorn api_server:app --host 0.0.0.0 --port 8002  # Will fail
```

The `python -m uvicorn` syntax is required when using `uv` as it properly resolves the module path.

**To test the API:**
```bash
uv run python test_api_server.py
```

---

**This guide focuses exclusively on running with uvicorn. The test script `test_api_server.py` is a client application that tests the API server.**

