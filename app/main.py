from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import traceback
from datetime import datetime
from typing import Union, Dict, Any
import asyncio
from app.models import (
    ChatRequest,
    ChatResponse,
    GeneralQueryResponse,
    SpecificQueryResponse,
    DatabaseManager
)
from app.database.langchain_sql import LangChainSQLIntegration
from app.llm.response_handler import ResponseHandler
from app.llm.conversation_store import ConversationStore
from app.session_manager import SessionManager
import os
from dotenv import load_dotenv
import time
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("malawi-rag-sql-chatbot.log")
    ]
)

logger = logging.getLogger(__name__)

# Get configuration from environment
PORT = int(os.getenv('PORT', '5000'))  # Changed default port to 5000
HOST = os.getenv('HOST', '0.0.0.0')
API_PREFIX = os.getenv('API_PREFIX', '/api')
CORS_ORIGINS = eval(os.getenv('CORS_ORIGINS', '["*"]'))

# Initialize FastAPI app
app = FastAPI(
    title="Malawi Projects Chatbot",
    description="A chatbot for querying Malawi infrastructure projects",
    version="1.0.0",
    openapi_url=f"{API_PREFIX}/openapi.json",
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc"
)

# Initialize templates
templates = Jinja2Templates(directory="frontend/templates")

# Set up static files and templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = DatabaseManager()
sql_chain = LangChainSQLIntegration()
response_handler = ResponseHandler()
conversation_store = ConversationStore()
session_manager = SessionManager()  # Initialize SessionManager
logger.info("Initialized components")

# Include routers with correct prefix for rag-sql-chatbot
from app.routers import chat
app.include_router(
    chat.router, 
    prefix=f"{API_PREFIX}/rag-sql-chatbot",
    tags=["chatbot"]
)

@app.get("/")
async def root(request: Request):
    """Serve the main frontend page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get(f"{API_PREFIX}/")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Welcome to Malawi Projects Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "health": f"{API_PREFIX}/health",
            "chat": f"{API_PREFIX}/rag-sql-chatbot/chat",
            "docs": f"{API_PREFIX}/docs"
        }
    }

# Add a simplified health endpoint at /api/health that doesn't require database connection
@app.get(f"{API_PREFIX}/health")
async def simplified_health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "message": "API is running"
    }

@app.post(f"{API_PREFIX}/rag-sql-chatbot/query")
async def rag_sql_chatbot_query(request: ChatRequest):
    """
    Process a natural language query about Malawi infrastructure projects using RAG and SQL.
    """
    try:
        logger.info(f"Received query: {request.message}")
        
        # Process the query
        response = await sql_chain.process_query(request.message)
        
        # Check if response has the expected structure
        if isinstance(response, dict):
            if "results" in response:
                # New response format
                return response
            elif "response" in response:
                # Old response format - convert to new format
                old_response = response["response"]
                
                # Extract results and metadata
                results = old_response.get("results", [])
                metadata = old_response.get("metadata", {})
                query_type = old_response.get("query_type", "general")
                
                # Format the results for the frontend
                formatted_results = []
                
                if results:
                    # Add a text result with summary
                    formatted_results.append({
                        "type": "text",
                        "message": f"Found {len(results)} projects matching your query.",
                        "data": {}
                    })
                    
                    # Add the data as a table
                    if results and len(results) > 0:
                        # Get headers from the first result
                        first_result = results[0]
                        headers = list(first_result.keys())
                        
                        formatted_results.append({
                            "type": "table",
                            "message": "Project Details",
                            "data": {
                                "headers": headers,
                                "rows": results
                            }
                        })
                else:
                    # No results found
                    formatted_results.append({
                        "type": "text",
                        "message": "No projects found matching your criteria.",
                        "data": {}
                    })
                
                # Return in the new format
                return {
                    "results": formatted_results,
                    "metadata": metadata
                }
        
        # Fallback for unexpected response format
        logger.warning(f"Unexpected response format: {response}")
        return {
            "results": [{
                "type": "text",
                "message": "I processed your query but received an unexpected response format.",
                "data": {}
            }],
            "metadata": {
                "total_results": 0,
                "query_time": "0.00s"
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "results": [{
                "type": "error",
                "message": f"An error occurred while processing your query: {str(e)}",
                "data": {}
            }],
            "metadata": {
                "total_results": 0,
                "query_time": "0.00s"
            }
        }

@app.post(f"{API_PREFIX}/rag-sql-chatbot/chat")
async def chat(request: ChatRequest) -> Dict[str, Any]:
    """Process a chat message and return a response."""
    try:
        logger.info(f"Processing chat request with message: {request.message}")
        
        # Check if this is a pagination request
        session_id = request.session_id
        is_pagination = False
        page = 1
        
        # Check for pagination commands
        pagination_commands = ["show more", "next page", "previous page", "page"]
        for cmd in pagination_commands:
            if cmd in request.message.lower():
                is_pagination = True
                break
        
        # Extract page number if specified
        if "page" in request.message.lower():
            page_match = re.search(r"page\s+(\d+)", request.message.lower())
            if page_match:
                try:
                    page = int(page_match.group(1))
                except ValueError:
                    pass
        
        # Handle pagination request
        if is_pagination and session_id:
            session = session_manager.get_session(session_id)
            if not session:
                return {
                    "results": [{
                        "type": "error",
                        "message": "Your session has expired. Please try your original query again.",
                        "data": {}
                    }],
                    "metadata": {"total_results": 0}
                }
            
            # Handle "next page" and "show more"
            if "next page" in request.message.lower() or "show more" in request.message.lower():
                page = session["current_page"] + 1
            
            # Handle "previous page"
            if "previous page" in request.message.lower():
                page = max(1, session["current_page"] - 1)
            
            # Get results for the requested page
            page_data = session_manager.get_page_results(session_id, page)
            if page_data:
                # Update current page in session
                session_manager.update_session(session_id, {"current_page": page})
                return page_data
            
            # If we need to fetch more data, fall through to regular query processing
            # but with pagination parameters
            request.message = session["original_query"]
        
        # Process the regular query
        response = await sql_chain.process_query(request.message)
        
        # For new queries (non-pagination), create a session and store results
        if not is_pagination and isinstance(response, dict) and "results" in response:
            # Extract results data
            results_data = []
            total_results = 0
            
            for item in response["results"]:
                if item.get("type") == "table" and "data" in item:
                    results_data.extend(item["data"].get("rows", []))
                    total_results = len(item["data"].get("rows", []))
            
            if results_data and total_results > 10:
                # Create new session
                new_session_id = session_manager.create_session(request.message)
                session_manager.store_results(
                    new_session_id,
                    results_data,
                    total_results,
                    response.get("metadata", {}).get("sql_query", "")
                )
                
                # Add pagination metadata
                response["pagination"] = {
                    "session_id": new_session_id,
                    "has_more": total_results > 10,
                    "has_previous": False,
                    "current_page": 1,
                    "total_pages": (total_results + 9) // 10,
                    "next_page_command": "show more",
                    "prev_page_command": "previous page"
                }
                
                # Limit initial response to 10 results
                for item in response["results"]:
                    if item.get("type") == "table" and "data" in item:
                        item["data"]["rows"] = item["data"]["rows"][:10]
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "results": [{
                "type": "error",
                "message": f"An error occurred while processing your query: {str(e)}",
                "data": {}
            }],
            "metadata": {
                "total_results": 0,
                "query_time": "0.00s"
            }
        }

# Mount the frontend static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)