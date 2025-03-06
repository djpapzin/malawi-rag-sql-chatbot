"""Main Application Module

This module contains the main FastAPI application and route handlers.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List
import logging
from pathlib import Path
from .query_parser import QueryParser
from .response_formatter import ResponseFormatter
from .database.service import DatabaseService
from .core.config import settings
from .routers import chat
from .llm_classification.new_classifier import LLMClassifier

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
    filename=settings.LOG_FILE
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Root path to serve index.html
@app.get("/")
async def read_root():
    return FileResponse("frontend/templates/index.html")

# Include routers
app.include_router(chat.router, prefix="/api/rag-sql-chatbot")

# Initialize services
query_parser = QueryParser()
response_formatter = ResponseFormatter()
db_service = DatabaseService()
classifier = LLMClassifier()

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    language: str = "english"
    page: int = 1
    page_size: int = settings.DEFAULT_PAGE_SIZE
    context: Dict[str, Any] = None

@app.post("/api/rag-sql-chatbot/chat")
async def chat(request: ChatRequest) -> Dict[str, Any]:
    """Handle chat requests"""
    try:
        # Classify the query
        classification = await classifier.classify_query(request.message, request.context)
        
        # Handle unrelated queries directly
        if classification.query_type == "unrelated":
            return {
                "type": "unrelated",
                "message": "I can help you find information about infrastructure projects in Malawi. You can ask me about specific projects, projects in certain districts or sectors, or general questions about the projects.",
                "metadata": {
                    "query_time": None,
                    "total_results": 0
                }
            }
        
        # Parse the query for database access
        query_info = await query_parser.parse_query(request.message, classification)
        
        # Execute the query if needed
        results = []
        if query_info["query"]:
            results = await db_service.execute_query(query_info["query"])
        
        # Format the response
        response = response_formatter.format_response(
            query_type=classification.query_type,
            results=results,
            parameters=classification.parameters
        )
        
        # Add metadata
        response["metadata"] = {
            "query_time": query_info["metadata"]["timestamp"],
            "total_results": len(results),
            "current_page": request.page,
            "page_size": request.page_size,
            "sql_query": query_info["query"] if query_info["query"] else None,
            "confidence": classification.confidence
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error processing your request. Please try again."
        ) 