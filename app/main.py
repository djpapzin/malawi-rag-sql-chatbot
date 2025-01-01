from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from datetime import datetime
import uuid
from typing import Dict, Any, List
import logging
import importlib

# Import our custom modules
from .models import ChatQuery, ChatResponse, QueryMetadata, QuerySource
from .query_parser import QueryParser
from .response_generator import ResponseGenerator
from .sql_tracker import SQLTracker

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Force reload modules
importlib.reload(importlib.import_module('app.query_parser'))
importlib.reload(importlib.import_module('app.models'))

# Initialize FastAPI app
app = FastAPI(
    title="Malawi Projects Chatbot",
    description="A chatbot for querying Malawi infrastructure projects",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
sql_tracker = SQLTracker()
response_generator = ResponseGenerator(sql_tracker=sql_tracker)
query_parser = QueryParser()
logger.info("Initialized components")
logger.info(f"Using QueryParser from module: {QueryParser.__module__}")

@app.post("/query")
async def process_query(chat_query: ChatQuery) -> ChatResponse:
    """Process a chat query and return response with source information"""
    try:
        query_start = datetime.now()
        
        # Check if this is a "show more" request
        show_more_intents = ["show more", "more", "continue", "next", "show next", "display more"]
        is_show_more = any(intent in chat_query.message.lower() for intent in show_more_intents)
        
        # Parse the query
        logger.info(f"Parsing query: {chat_query.message}")
        sql_query = query_parser.parse_query(chat_query.message)
        logger.info(f"Generated SQL query: {sql_query}")
        
        # Generate response
        response_text, metadata = response_generator.generate_response(
            query=sql_query,
            page=chat_query.page,
            page_size=chat_query.page_size,
            is_show_more=is_show_more
        )
        
        # Get the executed SQL query from metadata
        executed_sql = metadata.get("sql", sql_query)
        logger.info(f"Executed SQL query: {executed_sql}")
        
        # Create response with both response and message fields
        response = ChatResponse(
            response=response_text,  # Main response text
            message=response_text,   # Same as response for compatibility
            metadata=QueryMetadata(
                query_time=str(datetime.now() - query_start),
                total_results=metadata["total_results"],
                current_page=metadata["current_page"],
                total_pages=metadata["total_pages"],
                has_more=metadata["has_more"]
            ),
            source=QuerySource(
                sql=executed_sql,  # Use the executed SQL query
                table="projects",
                filters=metadata.get("filters", {})  # Get filters from metadata
            )
        )
        
        logger.info(f"Returning response with SQL: {executed_sql}")
        return response
            
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        test_query = "SELECT 1"
        sql_tracker.execute_query(test_query)
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Service unhealthy: {str(e)}"
        )