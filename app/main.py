"""Main Application Module

This module contains the main FastAPI application and route handlers.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import logging
from pathlib import Path
from .query_parser import QueryParser
from .response_formatter import ResponseFormatter
from .database.service import DatabaseService
from .core.config import settings
from .routers import chat, query
from .llm_classification.new_classifier import LLMClassifier
from .services.llm_service import LLMService
import ssl

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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Root path to serve index.html
@app.get("/")
async def read_root():
    return FileResponse("frontend/templates/index.html")

# Include routers
app.include_router(chat.router, prefix="/api/rag-sql-chatbot")
app.include_router(query.router, prefix="/api/rag-sql-chatbot")

# Initialize services
llm_service = LLMService()
query_parser = QueryParser(llm_service=llm_service)
response_formatter = ResponseFormatter()
db_service = DatabaseService()
classifier = LLMClassifier()

# Chat functionality moved to routers/chat.py

if __name__ == "__main__":
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(
        certfile="/etc/letsencrypt/live/dziwani.kwantu.support/fullchain.pem",
        keyfile="/etc/letsencrypt/live/dziwani.kwantu.support/privkey.pem"
    )
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000, ssl_keyfile="/etc/letsencrypt/live/dziwani.kwantu.support/privkey.pem", ssl_certfile="/etc/letsencrypt/live/dziwani.kwantu.support/fullchain.pem") 