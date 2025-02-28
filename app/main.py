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
import os
from dotenv import load_dotenv
import time

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
API_PREFIX = os.getenv('API_PREFIX', '/api/rag-sql-chatbot')
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
origins = [
    "http://154.0.164.254:3000",     # Frontend development
    "http://154.0.164.254:5000",     # Backend development
    "https://dziwani.kwantu.support" # Production
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = DatabaseManager()
langchain_sql = LangChainSQLIntegration()
response_handler = ResponseHandler()
conversation_store = ConversationStore()
logger.info("Initialized components")

# Include routers
from app.routers import chat
app.include_router(chat.router, prefix=API_PREFIX)

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get(f"{API_PREFIX}/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Get connection and check row count
        with langchain_sql.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM proj_dashboard")
            row_count = cursor.fetchone()[0]
        
        return {
            "status": "healthy",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "components": {
                "database": {
                    "status": "connected",
                    "row_count": row_count
                },
                "api": "running"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.post(f"{API_PREFIX}/chat")
async def chat(request: ChatRequest) -> Dict[str, Any]:
    """Process a chat message and return a response."""
    try:
        # Process the query and return results directly
        # The process_query method now returns the exact format expected by tests
        return await langchain_sql.process_query(request.message)
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "results": [{
                "type": "error",
                "message": "I encountered an error processing your request. Please try again.",
                "data": {"error": str(e)}
            }],
            "metadata": {
                "total_results": 0,
                "query_time": "0.00s",
                "sql_query": "",
                "error": str(e)
            }
        }