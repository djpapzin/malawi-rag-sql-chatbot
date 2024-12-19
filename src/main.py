"""
Main FastAPI application for RAG SQL Chatbot
"""

import logging
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .llm_service import LLMService
from .db_service import DatabaseService
from .translation import TranslationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="RAG SQL Chatbot")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    llm_service = LLMService()
    db_service = DatabaseService()
    translation_service = TranslationService()
    logger.info("Successfully initialized all services")
except Exception as e:
    logger.error(f"Error initializing services: {str(e)}")
    raise

class QueryRequest(BaseModel):
    message: str
    language: str = "english"
    session_id: Optional[str] = None
    require_translation: bool = False
    include_language_suggestions: bool = True
    llm_config: Optional[Dict] = None

@app.post("/query")
async def process_query(request: QueryRequest):
    """
    Process a user query with LLM enhancement and SQL execution
    """
    try:
        logger.info(f"Processing query: {request.message} (Language: {request.language})")
        
        # Step 1: Process with LLM if enabled
        llm_response = None
        if request.llm_config and request.llm_config.get("enabled", False):
            llm_response = llm_service.process_query(
                query=request.message,
                chat_history=[],  # TODO: Implement chat history
                language=request.language,
                session_id=request.session_id
            )
            
            # Use enhanced query if available
            query_to_execute = llm_response.get("llm_processing", {}).get("enhanced_query", request.message)
        else:
            query_to_execute = request.message
            
        # Step 2: Execute SQL query
        db_response = await db_service.execute_query(query_to_execute)
        
        # Step 3: Format response
        response_text = db_response.get("response", "No results found")
        
        # Step 4: Translate if required
        if request.require_translation and request.language != "english":
            response_text = await translation_service.translate(
                text=response_text,
                target_language=request.language
            )
        
        # Step 5: Prepare final response
        response = {
            "response": response_text,
            "session_id": request.session_id,
            "language": request.language,
            "translated": request.require_translation,
        }
        
        # Add LLM processing results if available
        if llm_response and "llm_processing" in llm_response:
            response["llm_processing"] = llm_response["llm_processing"]
        
        # Add suggested questions if requested
        if request.include_language_suggestions:
            response["suggested_questions"] = (
                llm_response.get("llm_processing", {}).get("suggested_questions", [])
                if llm_response
                else []
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Check the health of all services
    """
    try:
        # Check LLM service
        llm_status = "ok" if llm_service else "error"
        
        # Check database
        db_status = "ok" if await db_service.check_connection() else "error"
        
        # Check translation service
        translation_status = "ok" if translation_service else "error"
        
        return {
            "status": "healthy",
            "services": {
                "llm": llm_status,
                "database": db_status,
                "translation": translation_status
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 