from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any
import logging
import traceback
import os
import time

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
async def chat(request: Request):
    """
    Chat endpoint for RAG SQL Chatbot
    """
    try:
        # Parse request body
        body = await request.json()
        
        # Check if message is in the request body
        if "message" not in body:
            return JSONResponse(
                status_code=400,
                content={"error": "Message field is required in the request body"}
            )
        
        user_message = body["message"]
        
        # Check if the message is empty
        if not user_message or user_message.strip() == "":
            return JSONResponse(
                status_code=400,
                content={"error": "Message cannot be empty"}
            )
        
        # Check if this is an aggregate query
        is_aggregate = _is_aggregate_query(user_message)
        
        # Process the message
        start_time = time.time()
        
        # Initialize the SQL chain
        sql_chain = LangChainSQLIntegration()
        
        # Run the query
        response = sql_chain.process_query(user_message)
        
        # Calculate query time
        query_time = time.time() - start_time
        
        # Add query time to response metadata
        if "metadata" in response:
            response["metadata"]["query_time"] = f"{query_time:.2f}s"
        
        # Return the response
        return JSONResponse(content=response)
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": f"An error occurred: {str(e)}"}
        )
