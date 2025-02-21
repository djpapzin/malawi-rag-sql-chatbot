from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
from datetime import datetime
import uuid
from typing import Dict, Any, List
import logging
import importlib
import re
from dotenv import load_dotenv
import os
import traceback
import time

# Load environment variables
load_dotenv()

# Get configuration from environment
PORT = int(os.getenv('PORT', '8000'))
HOST = os.getenv('HOST', '0.0.0.0')
API_PREFIX = os.getenv('API_PREFIX', '')
CORS_ORIGINS = eval(os.getenv('CORS_ORIGINS', '["*"]'))

# Import our custom modules
from .models import ChatQuery, ChatResponse, QueryMetadata, QuerySource
from .query_parser import QueryParser
from .response_generator import ResponseGenerator
from .sql_tracker import SQLTracker
from .database.langchain_sql import LangChainSQLIntegration

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
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
    openapi_url=None  # Disable default openapi
)

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

# Set up static files and templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Create a sub-application with the API prefix
api_app = FastAPI(
    title="Malawi Projects Chatbot API",
    description="A chatbot for querying Malawi infrastructure projects",
    version="1.0.0"
)

# Mount the API app with the prefix
app.mount(API_PREFIX, api_app)

# Add CORS middleware to both apps
for current_app in [app, api_app]:
    current_app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Initialize components
sql_tracker = SQLTracker()
response_generator = ResponseGenerator()
query_parser = QueryParser()
langchain_sql = LangChainSQLIntegration()
logger.info("Initialized components")
logger.info(f"Using QueryParser from module: {QueryParser.__module__}")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def root_health_check():
    """Root health check endpoint"""
    return await health_check()

@api_app.post("/query")
async def process_query(query: ChatQuery) -> ChatResponse:
    """Process a chat query and return response with sources"""
    try:
        # Log incoming query
        logger.info(f"Processing query: {query.message}")
        
        # Get current timestamp
        timestamp = datetime.now().isoformat()
        
        # Generate unique query ID
        query_id = str(uuid.uuid4())
        
        # Start timer
        start_time = time.time()
        
        # Get answer from SQL integration
        sql_integration = LangChainSQLIntegration()
        result = sql_integration.get_answer(query.message)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create response
        response = ChatResponse(
            response=result["response"],
            metadata=QueryMetadata(
                timestamp=timestamp,
                query_id=query_id,
                processing_time=processing_time
            ),
            source=QuerySource(
                sql=result["sql"],
                database="malawi_projects1.db"
            )
        )
        
        # Log success
        logger.info(f"Query processed successfully. Query ID: {query_id}")
        
        return response
        
    except Exception as e:
        # Log error
        logger.error(f"Error processing query: {str(e)}\nFull trace: {traceback.format_exc()}")
        
        # Raise HTTPException
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@api_app.get("/schema")
async def get_database_schema():
    """Get database schema information"""
    try:
        schema_info = langchain_sql.get_table_info()
        return {"schema": schema_info}
    except Exception as e:
        logger.error(f"Error getting schema: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting schema: {str(e)}"
        )

@api_app.post("/generate-sql")
async def generate_sql(query: ChatQuery):
    """Generate SQL query from natural language without executing it"""
    try:
        sql_query = langchain_sql.generate_sql_query(query.message)
        return {
            "sql_query": sql_query,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating SQL: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating SQL: {str(e)}"
        )

@api_app.get("/health")
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