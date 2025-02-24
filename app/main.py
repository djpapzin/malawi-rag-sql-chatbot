from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import traceback
from datetime import datetime
from typing import Union
from .models import (
    ChatQuery,
    ChatResponse,
    GeneralQueryResponse,
    SpecificQueryResponse,
    DatabaseManager
)
from .database.langchain_sql import LangChainSQLIntegration
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from environment
PORT = int(os.getenv('PORT', '5000'))  # Changed default port to 5000
HOST = os.getenv('HOST', '0.0.0.0')
API_PREFIX = os.getenv('API_PREFIX', '')
CORS_ORIGINS = eval(os.getenv('CORS_ORIGINS', '["*"]'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Malawi Projects Chatbot",
    description="A chatbot for querying Malawi infrastructure projects",
    version="1.0.0"
)

# Initialize templates
templates = Jinja2Templates(directory="frontend/templates")

# Set up static files and templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = DatabaseManager()
sql_integration = LangChainSQLIntegration()
logger.info("Initialized components")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM proj_dashboard")
            count = cursor.fetchone()[0]
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "database": {
                    "status": "connected",
                    "row_count": count
                },
                "api": "running"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )

@app.post("/query")
async def process_query(query: ChatQuery) -> ChatResponse:
    """Process a chat query and return response with sources"""
    try:
        # Log incoming query
        logger.info(f"Processing query: {query.message}")
        
        # Get answer from SQL integration
        result = sql_integration.get_answer(query.message)
        
        # Return response in new format
        return ChatResponse(response=result)
        
    except Exception as e:
        # Log error
        logger.error(f"Error processing query: {str(e)}\nFull trace: {traceback.format_exc()}")
        
        # Raise HTTPException
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )