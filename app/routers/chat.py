from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any
import logging
import traceback
import os
import time
import sqlalchemy

from app.database.langchain_sql import LangChainSQLIntegration
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    message: str

def _is_aggregate_query(query: str) -> bool:
    """
    Determine if a query is likely an aggregate query
    """
    # List of keywords that suggest an aggregate query
    aggregate_keywords = [
        'count', 'how many', 'total', 'sum', 'average', 'avg', 
        'breakdown', 'group by', 'statistics', 'summary',
        'distribution', 'percentage', 'proportion', 'compare'
    ]
    
    # Check if any of the keywords are in the query
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in aggregate_keywords)

@router.post("/chat")
async def chat(chat_request: ChatRequest):
    """
    Chat endpoint for RAG SQL Chatbot
    """
    try:
        logger.info(f"Received chat request: {chat_request}")
        
        # Use LangChainSQLIntegration directly instead of QueryClassificationService
        sql_chain = LangChainSQLIntegration()
        response = await sql_chain.process_query(chat_request.message)
        
        return JSONResponse(
            content=response,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )
        
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f"Unexpected error: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Initialize SQL integration to test database connection
        sql_chain = LangChainSQLIntegration()
        
        return JSONResponse(
            content={
                "status": "healthy",
                "message": "RAG SQL Chatbot is running"
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e)
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )

@router.options("/health")
async def health_options():
    """Handle OPTIONS requests for health endpoint"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )
