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
                content={
                    "results": [{
                        "type": "error",
                        "message": "Message field is required in the request body",
                        "data": {}
                    }],
                    "metadata": {
                        "total_results": 0,
                        "query_time": "0.00s",
                        "sql_query": ""
                    }
                },
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            )
        
        user_message = body["message"]
        
        # Check if the message is empty
        if not user_message or user_message.strip() == "":
            return JSONResponse(
                status_code=400,
                content={
                    "results": [{
                        "type": "error",
                        "message": "Message cannot be empty",
                        "data": {}
                    }],
                    "metadata": {
                        "total_results": 0,
                        "query_time": "0.00s",
                        "sql_query": ""
                    }
                },
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            )
        
        # Process the message
        start_time = time.time()
        
        # Initialize the SQL chain
        sql_chain = LangChainSQLIntegration()
        
        # Run the query and await the response
        response = await sql_chain.process_query(user_message)
        
        # Calculate query time
        query_time = time.time() - start_time
        
        # Ensure response has the correct structure
        if not isinstance(response, dict):
            response = {
                "results": [{
                    "type": "text",
                    "message": str(response),
                    "data": {}
                }],
                "metadata": {
                    "total_results": 1,
                    "query_time": f"{query_time:.2f}s",
                    "sql_query": ""
                }
            }
        elif "metadata" not in response:
            response["metadata"] = {
                "total_results": len(response.get("results", [])),
                "query_time": f"{query_time:.2f}s",
                "sql_query": ""
            }
        else:
            response["metadata"]["query_time"] = f"{query_time:.2f}s"
        
        # Return the response
        return JSONResponse(
            content=response,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "results": [{
                    "type": "error",
                    "message": str(e),
                    "data": {}
                }],
                "metadata": {
                    "total_results": 0,
                    "query_time": "0.00s",
                    "sql_query": ""
                }
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={"status": "healthy", "message": "RAG SQL Chatbot is running"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )
