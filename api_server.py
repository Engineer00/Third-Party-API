"""
FastAPI Backend Server for CrewAI Tool Wrapper Integration

This server bridges Sim/Flowise tool calls to CrewAI flows with semantic routing.
It provides a REST API that converts structured tool parameters into natural language
queries that CrewAI can process intelligently.

Port: 8002 (configurable via CREWAI_API_PORT env var)
"""

import os
import sys
import json
import traceback
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

# Add src to path to import umbrella_corp modules
project_root = Path(__file__).resolve().parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.umbrella_corp.flows.googlesuite_flow import GoogleSuiteFlow

load_dotenv()

# ============================================================================
# Tool ID to Crew Name Mapping (needed for lifespan)
# ============================================================================

TOOL_TO_CREW_MAPPING = {
    # Google Calendar Tools
    'google_calendar_create': 'EVENT_MANAGEMENT_FLOW',
    'google_calendar_list': 'EVENT_MANAGEMENT_FLOW',
    'google_calendar_get': 'EVENT_MANAGEMENT_FLOW',
    'google_calendar_update': 'EVENT_MANAGEMENT_FLOW',
    'google_calendar_delete': 'EVENT_MANAGEMENT_FLOW',
    'google_calendar_quick_add': 'EVENT_MANAGEMENT_FLOW',
    'google_calendar_freebusy': 'EVENT_MANAGEMENT_FLOW',
    
    # Gmail Tools
    'gmail_send': 'EMAIL_MANAGEMENT_FLOW',
    'gmail_read': 'EMAIL_MANAGEMENT_FLOW',
    'gmail_search': 'EMAIL_MANAGEMENT_FLOW',
    'gmail_draft': 'EMAIL_MANAGEMENT_FLOW',
    'gmail_labels': 'EMAIL_MANAGEMENT_FLOW',
    'gmail_reply': 'EMAIL_MANAGEMENT_FLOW',
    
    # Google Drive Tools
    'google_drive_upload': 'DRIVE_MANAGEMENT_FLOW',
    'google_drive_download': 'DRIVE_MANAGEMENT_FLOW',
    'google_drive_list': 'DRIVE_MANAGEMENT_FLOW',
    'google_drive_share': 'DRIVE_MANAGEMENT_FLOW',
    'google_drive_create_folder': 'DRIVE_MANAGEMENT_FLOW',
    'google_drive_move': 'DRIVE_MANAGEMENT_FLOW',
    'google_drive_delete': 'DRIVE_MANAGEMENT_FLOW',
    
    # Google Sheets Tools
    'google_sheets_read': 'SHEETS_MANAGEMENT_FLOW',
    'google_sheets_write': 'SHEETS_MANAGEMENT_FLOW',
    'google_sheets_update': 'SHEETS_MANAGEMENT_FLOW',
    'google_sheets_append': 'SHEETS_MANAGEMENT_FLOW',
    
    # Google Docs Tools
    'google_docs_read': 'DOCS_MANAGEMENT_FLOW',
    'google_docs_write': 'DOCS_MANAGEMENT_FLOW',
    'google_docs_create': 'DOCS_MANAGEMENT_FLOW',
}

# ============================================================================
# Lifespan Event Handler
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    print("\n" + "="*60)
    print("[START] CrewAI Tool Wrapper API Server")
    print("="*60)
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"OpenAI API Key: {'[OK] Set' if os.getenv('OPENAI_API_KEY') else '[ERROR] Missing'}")
    print(f"Gmail SMTP Email: {'[OK] Set' if os.getenv('GMAIL_SMTP_EMAIL') else '[ERROR] Missing'}")
    print(f"Available Tools: {len(TOOL_TO_CREW_MAPPING)}")
    print("[INFO] GoogleSuiteFlow will be initialized on first request (lazy loading)")
    print("="*60 + "\n")
    yield
    # Shutdown (if needed)
    pass

# ============================================================================
# FastAPI App Setup
# ============================================================================

app = FastAPI(
    title="CrewAI Tool Wrapper API",
    description="REST API for integrating CrewAI flows with Sim/Flowise blocks",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for Sim/Flowise frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Request/Response Models
# ============================================================================

class ToolExecuteRequest(BaseModel):
    """Request model for tool execution"""
    toolId: str = Field(..., description="Tool identifier (e.g., 'google_calendar_create')")
    params: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    userQuery: Optional[str] = Field(None, description="Optional natural language query (auto-generated if not provided)")


class ToolExecuteResponse(BaseModel):
    """Response model for tool execution"""
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    timestamp: str
    version: str


class ToolListResponse(BaseModel):
    """Response model for listing available tools"""
    tools: list[str]
    mappings: Dict[str, str]
    total: int

# TOOL_TO_CREW_MAPPING moved above (before lifespan definition)

# ============================================================================
# Flow Cache (Singleton Pattern)
# ============================================================================

_flow_cache: Dict[str, GoogleSuiteFlow] = {}

def get_google_suite_flow() -> GoogleSuiteFlow:
    """
    Get or create GoogleSuiteFlow instance (singleton)
    
    Follows the same pattern as router_flow.py:
    - Initializes with: GoogleSuiteFlow(name, api_key)
    - Matches the OFFICE_FLOWS pattern in router_flow.py
    """
    cache_key = 'google_suite'
    
    if cache_key not in _flow_cache:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment variables")
        
        # Follow umbrella_corp pattern: GoogleSuiteFlow("Google Suite Flow", OPENAI_API_KEY)
        # As seen in router_flow.py lines 189-191
        # NOTE: This initialization is slow because it:
        # 1. Initializes GoogleSuiteCrew (loads agents/tools)
        # 2. Initializes semantic routers (reads JSON files, creates OpenAI routers)
        # This is why we do lazy initialization - only create flow on first request
        print(f"[START] Initializing GoogleSuiteFlow (this may take 10-30 seconds)...")
        print(f"[INFO] Loading semantic routers and Google Suite Crew...")
        start_init_time = time.time()
        try:
            _flow_cache[cache_key] = GoogleSuiteFlow(
                name="Google Suite Flow",  # Matches router_flow.py pattern
                api_key=api_key
            )
            elapsed = time.time() - start_init_time
            print(f"[OK] GoogleSuiteFlow initialized successfully in {elapsed:.2f}s")
        except Exception as e:
            print(f"[ERROR] Failed to initialize GoogleSuiteFlow: {str(e)}")
            traceback.print_exc()
            raise ValueError(f"Flow initialization failed: {str(e)}")
    
    return _flow_cache[cache_key]

# ============================================================================
# Parameter to Query Conversion
# ============================================================================

def convert_params_to_user_query(tool_id: str, params: Dict[str, Any]) -> str:
    """Convert structured parameters to natural language query for CrewAI"""
    
    # Google Calendar
    if tool_id == 'google_calendar_create':
        summary = params.get('summary', 'event')
        start = params.get('start', {})
        end = params.get('end', {})
        start_time = start.get('dateTime', '') if isinstance(start, dict) else str(start)
        end_time = end.get('dateTime', '') if isinstance(end, dict) else str(end)
        description = params.get('description', '')
        attendees = params.get('attendees', [])
        
        query = f"Create calendar event: {summary}"
        if start_time:
            query += f" from {start_time}"
        if end_time:
            query += f" to {end_time}"
        if description:
            query += f" with description: {description}"
        if attendees:
            query += f" with attendees: {', '.join(attendees) if isinstance(attendees, list) else attendees}"
        return query
    
    elif tool_id == 'google_calendar_list':
        time_min = params.get('timeMin', 'now')
        time_max = params.get('timeMax', 'future')
        max_results = params.get('maxResults', 10)
        return f"List calendar events from {time_min} to {time_max}, maximum {max_results} results"
    
    elif tool_id == 'google_calendar_get':
        event_id = params.get('eventId', '')
        return f"Get calendar event with ID: {event_id}"
    
    elif tool_id == 'google_calendar_update':
        event_id = params.get('eventId', '')
        summary = params.get('summary', '')
        return f"Update calendar event {event_id} with title: {summary}"
    
    elif tool_id == 'google_calendar_delete':
        event_id = params.get('eventId', '')
        return f"Delete calendar event with ID: {event_id}"
    
    # Gmail
    elif tool_id == 'gmail_send':
        to = params.get('to', '')
        subject = params.get('subject', '')
        body = params.get('body', '')
        cc = params.get('cc')
        bcc = params.get('bcc')
        
        query = f"Send email to {to} with subject '{subject}'"
        if body:
            query += f" and body: {body[:100]}..." if len(body) > 100 else f" and body: {body}"
        if cc:
            query += f", CC: {cc}"
        if bcc:
            query += f", BCC: {bcc}"
        return query
    
    elif tool_id == 'gmail_read':
        hours = params.get('hours', 24)
        unread_only = params.get('unread_only', True)
        max_results = params.get('maxResults', 10)
        return f"Read {'unread' if unread_only else 'recent'} emails from the last {hours} hours, maximum {max_results} results"
    
    elif tool_id == 'gmail_search':
        query_param = params.get('query', '')
        return f"Search emails with query: {query_param}"
    
    elif tool_id == 'gmail_reply':
        original_from = params.get('original_from_email', '')
        original_subject = params.get('original_subject', '')
        reply_body = params.get('reply_body', '')
        return f"Reply to email from {original_from} with subject '{original_subject}' and reply: {reply_body[:100]}..."
    
    # Google Drive
    elif tool_id == 'google_drive_upload':
        file_name = params.get('fileName') or params.get('name', 'file')
        folder_id = params.get('folderId', '')
        if folder_id:
            return f"Upload file {file_name} to Google Drive folder {folder_id}"
        return f"Upload file {file_name} to Google Drive"
    
    elif tool_id == 'google_drive_list':
        folder_id = params.get('folderId', '')
        query = params.get('query', '')
        if query:
            return f"List files in Google Drive matching: {query}"
        if folder_id:
            return f"List files in Google Drive folder {folder_id}"
        return "List files in Google Drive"
    
    elif tool_id == 'google_drive_download':
        file_id = params.get('fileId', '')
        return f"Download file from Google Drive with ID: {file_id}"
    
    elif tool_id == 'google_drive_share':
        file_id = params.get('fileId', '')
        email = params.get('email', '')
        return f"Share Google Drive file {file_id} with {email}"
    
    elif tool_id == 'google_drive_create_folder':
        folder_name = params.get('name', 'New Folder')
        parent_id = params.get('parentId', '')
        if parent_id:
            return f"Create folder '{folder_name}' in Google Drive folder {parent_id}"
        return f"Create folder '{folder_name}' in Google Drive"
    
    # Google Sheets
    elif tool_id == 'google_sheets_read':
        spreadsheet_id = params.get('spreadsheetId', '')
        range_name = params.get('range', '')
        return f"Read data from Google Sheets {spreadsheet_id} range {range_name}"
    
    elif tool_id == 'google_sheets_write':
        spreadsheet_id = params.get('spreadsheetId', '')
        range_name = params.get('range', '')
        return f"Write data to Google Sheets {spreadsheet_id} range {range_name}"
    
    # Google Docs
    elif tool_id == 'google_docs_read':
        document_id = params.get('documentId', '')
        return f"Read Google Docs document {document_id}"
    
    elif tool_id == 'google_docs_create':
        title = params.get('title', 'New Document')
        return f"Create Google Docs document with title: {title}"
    
    # Default: use params as JSON string
    return f"Execute {tool_id} with parameters: {json.dumps(params, default=str)}"

# ============================================================================
# Result Parsing
# ============================================================================

def parse_crewai_result(result: Any) -> Dict[str, Any]:
    """Parse CrewAI flow result into Sim/Flowise compatible format"""
    
    if isinstance(result, str):
        return {
            'data': result,
            'status': 'success',
            'message': result
        }
    elif hasattr(result, 'response'):
        # GoogleSuiteFlowState object
        response_str = str(result.response) if result.response else str(result)
        return {
            'data': response_str,
            'status': 'success',
            'message': response_str
        }
    elif isinstance(result, dict):
        return result
    elif hasattr(result, '__dict__'):
        # Pydantic model or dataclass
        return {
            'data': result.__dict__ if hasattr(result, '__dict__') else str(result),
            'status': 'success',
            'message': str(result)
        }
    else:
        return {
            'data': str(result),
            'status': 'success',
            'message': str(result)
        }

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CrewAI Tool Wrapper API",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/tools/google-suite/list", response_model=ToolListResponse)
async def list_available_tools():
    """List all available Google Suite tools"""
    return {
        "tools": list(TOOL_TO_CREW_MAPPING.keys()),
        "mappings": TOOL_TO_CREW_MAPPING,
        "total": len(TOOL_TO_CREW_MAPPING)
    }

@app.post("/api/tools/google-suite/execute", response_model=ToolExecuteResponse)
async def execute_google_suite_tool(request: ToolExecuteRequest):
    """
    Execute Google Suite tool via CrewAI flow
    
    This endpoint receives tool execution requests from Sim/Flowise blocks
    and routes them to appropriate CrewAI flows with semantic routing.
    
    Flow:
    1. Receives structured parameters from Sim/Flowise block
    2. Converts parameters to natural language query
    3. Routes to appropriate CrewAI flow via semantic router
    4. Executes with CrewAI agent + tools
    5. Returns formatted response
    """
    start_time = datetime.utcnow()
    
    try:
        tool_id = request.toolId
        params = request.params
        
        print(f"\n{'='*60}")
        print(f"[TOOL] Tool Execution Request")
        print(f"{'='*60}")
        print(f"Tool ID: {tool_id}")
        print(f"Params: {json.dumps(params, indent=2, default=str)}")
        
        # Validate tool ID
        if tool_id not in TOOL_TO_CREW_MAPPING:
            error_msg = f"Unknown tool ID: {tool_id}. Available tools: {list(TOOL_TO_CREW_MAPPING.keys())}"
            print(f"[ERROR] {error_msg}")
            return ToolExecuteResponse(
                success=False,
                output=None,
                error=error_msg,
                metadata={"available_tools": list(TOOL_TO_CREW_MAPPING.keys())}
            )
        
        # Get user query (either provided or generated from params)
        user_query = request.userQuery
        if not user_query:
            user_query = convert_params_to_user_query(tool_id, params)
        
        print(f"User Query: {user_query}")
        
        # Get crew name from tool mapping
        crew_name = TOOL_TO_CREW_MAPPING.get(tool_id, 'GOOGLE_SUITE_FLOW')
        print(f"Crew Name: {crew_name}")
        
        # Get CrewAI Flow (following umbrella_corp pattern)
        # Lazy initialization - flow is created on first request to avoid slow startup
        print(f"[START] Getting GoogleSuiteFlow (lazy initialization)...")
        flow = get_google_suite_flow()
        
        # Execute flow (following umbrella_corp pattern from googlesuite_flow.py and router_flow.py)
        # Pattern matches: flow.kickoff(inputs={"user_query": ..., "crew_name": ..., "flow_name": ...})
        # As seen in router_flow.py line 102 and googlesuite_flow.py lines 88, 95
        # Note: kickoff() is synchronous, so we run it in a thread pool to avoid asyncio event loop conflicts
        print(f"[START] Executing CrewAI Flow...")
        
        # Run synchronous kickoff in thread pool to avoid asyncio conflicts
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=1)
        result = await loop.run_in_executor(
            executor,
            lambda: flow.kickoff(inputs={
                "user_query": user_query,
                "crew_name": crew_name,
                "flow_name": crew_name,  # Following router_flow.py pattern where flow_name = crew_name
            })
        )
        
        # Parse result
        parsed_result = parse_crewai_result(result)
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        print(f"[OK] Execution completed in {execution_time:.2f}s")
        print(f"Response: {parsed_result.get('message', 'N/A')[:200]}...")
        print(f"{'='*60}\n")
        
        return ToolExecuteResponse(
            success=True,
            output=parsed_result,
            metadata={
                "tool_id": tool_id,
                "crew_name": crew_name,
                "execution_time_seconds": execution_time,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except ValueError as e:
        error_msg = f"Configuration error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        traceback.print_exc()
        return ToolExecuteResponse(
            success=False,
            output=None,
            error=error_msg
        )
    except Exception as e:
        error_msg = f"Error executing tool {request.toolId}: {str(e)}"
        print(f"[ERROR] {error_msg}")
        traceback.print_exc()
        return ToolExecuteResponse(
            success=False,
            output=None,
            error=error_msg,
            metadata={"traceback": traceback.format_exc()}
        )

# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    print(f"[ERROR] Unhandled exception: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": f"Internal server error: {str(exc)}",
            "traceback": traceback.format_exc()
        }
    )

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("CREWAI_API_PORT", "8002"))
    host = os.getenv("CREWAI_API_HOST", "0.0.0.0")
    
    print(f"\n[START] Starting server on localhost:{port}")
    print(f"[INFO] API Documentation: http://localhost:{port}/docs")
    print(f"[INFO] Health Check: http://localhost:{port}/health")
    print(f"[INFO] List Tools: http://localhost:{port}/api/tools/google-suite/list\n")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        reload=os.getenv("ENVIRONMENT", "development") == "development"
    )

