from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from datetime import datetime
import uuid
from typing import Dict, Any, List
import logging
import importlib
import re

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
response_generator = ResponseGenerator()
query_parser = QueryParser()
logger.info("Initialized components")
logger.info(f"Using QueryParser from module: {QueryParser.__module__}")

@app.post("/query")
async def process_query(chat_query: ChatQuery) -> ChatResponse:
    """Process a chat query and return response with source information"""
    try:
        query_start = datetime.now()
        
        # Parse the query
        logger.info(f"Parsing query: {chat_query.message}")
        is_specific, project_identifier = query_parser.is_specific_project_query(chat_query.message)
        
        if is_specific:
            # Build SQL for specific project
            if re.match(r'MW-[A-Z]{2}-[A-Z0-9]{2}', project_identifier.upper()):
                sql_query = query_parser._build_specific_project_sql(project_code=project_identifier)
            else:
                sql_query = query_parser._build_specific_project_sql(project_name=project_identifier)
        else:
            sql_query = query_parser.parse_query(chat_query.message)
            
        logger.info(f"Generated SQL query: {sql_query}")
        
        # Execute query
        df, sources = sql_tracker.execute_query(sql_query)
        
        # Generate response
        response_text, metadata, source = response_generator.generate_response(
            df=df,
            sources=sources,
            is_specific_project=is_specific
        )
        
        # Create response
        response = ChatResponse(
            response=response_text,  # Main response text
            message=response_text,   # Same as response for compatibility
            metadata=QueryMetadata(
                query_time=str(datetime.now() - query_start),
                total_results=len(df),
                current_page=1,  # We'll implement pagination later
                total_pages=1,
                has_more=False
            ),
            source=source
        )
        
        logger.info(f"Returning response with {len(df)} results")
        return response
            
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        sql_tracker._connect()
        sql_tracker._disconnect()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "database": "connected",
                "api": "running"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )