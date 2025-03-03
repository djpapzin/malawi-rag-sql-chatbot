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
        # Get request body
        body = await request.json()
        message = body.get("message")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
            
        # Initialize services
        query_service = QueryClassificationService()
        
        # Classify query
        classification = await query_service.classify_query(message)
        
        # Generate SQL based on classification
        sql_query = query_service.generate_sql_from_classification(classification)
        
        # Execute query and format results
        results = []
        async with get_db_connection() as conn:
            # Execute query
            start_time = time.time()
            records = await conn.fetch(sql_query)
            query_time = f"{time.time() - start_time:.2f}s"
            
            if not records:
                if classification["type"] == "district_query":
                    district = classification["parameters"]["district"]
                    results.append({
                        "type": "text",
                        "message": f"No projects found in {district} district.",
                        "data": {}
                    })
                else:
                    results.append({
                        "type": "text",
                        "message": "No results found for your query.",
                        "data": {}
                    })
            else:
                if classification["type"] == "district_query":
                    district = classification["parameters"]["district"]
                    results.append({
                        "type": "text",
                        "message": f"Found {len(records)} projects in {district} district:",
                        "data": {}
                    })
                else:
                    results.append({
                        "type": "text",
                        "message": "Found projects matching your query:",
                        "data": {}
                    })
                
                # Format results
                for record in records:
                    results.append({
                        "type": "text",
                        "message": format_project_details(record),
                        "data": {}
                    })
        
        return JSONResponse(
            content={
                "results": results,
                "metadata": {
                    "total_results": len(records) if records else 0,
                    "query_time": query_time,
                    "sql_query": sql_query
                }
            },
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
