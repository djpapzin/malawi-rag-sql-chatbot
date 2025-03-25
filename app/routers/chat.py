from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
import traceback
import os
import time
import sqlalchemy
import sqlite3

from app.database.langchain_sql import LangChainSQLIntegration
from app.core.config import settings
from app.models import ChatRequest  # Import shared ChatRequest model

# Initialize router
router = APIRouter(
    tags=["chat", "query"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

# Add special test endpoints
@router.get("/test-education", response_model=Dict[str, Any])
async def test_education_query():
    """Direct test endpoint for education sector query using GET"""
    try:
        # Connect directly to the database
        conn = sqlite3.connect('/home/dj/malawi-rag-sql-chatbot/malawi_projects1.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Execute the query directly
        query = """
            SELECT 
                PROJECTNAME, PROJECTCODE, PROJECTSECTOR, PROJECTSTATUS,
                DISTRICT, BUDGET, FISCALYEAR
            FROM proj_dashboard
            WHERE PROJECTSECTOR = 'Education'
            ORDER BY BUDGET DESC NULLS LAST
            LIMIT 10;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert to dictionaries
        projects = []
        for row in rows:
            project = {}
            for key in row.keys():
                project[key] = row[key]
            projects.append(project)
        
        # Format for display
        formatted_projects = []
        for project in projects:
            formatted_projects.append({
                "Name": project.get("PROJECTNAME", "Unknown"),
                "Code": project.get("PROJECTCODE", "Unknown"),
                "Sector": project.get("PROJECTSECTOR", "Unknown"),
                "Status": project.get("PROJECTSTATUS", "Unknown"),
                "District": project.get("DISTRICT", "Unknown"),
                "Budget": f"MWK {float(project.get('BUDGET', 0)):,.2f}" if project.get("BUDGET") else "Unknown",
                "Fiscal Year": project.get("FISCALYEAR", "Unknown"),
            })
        
        return {
            "response": f"Found {len(projects)} education sector projects.",
            "projects": formatted_projects,
            "metadata": {
                "total_results": len(projects),
                "query": query
            }
        }
    except Exception as e:
        logging.error(f"Error in test endpoint: {str(e)}")
        logging.error(traceback.format_exc())
        return {
            "response": f"Error: {str(e)}",
            "projects": [],
            "metadata": {}
        }
logger = logging.getLogger(__name__)

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

@router.post("/chat", response_model=Dict[str, Any])
@router.post("/query", response_model=Dict[str, Any])
async def handle_request(chat_request: ChatRequest, request: Request):
    """Handle both chat and query requests with direct SQL execution"""
    try:
        endpoint = request.url.path.split('/')[-1]
        logger.info(f"Received {endpoint} request: {chat_request}")
        sql_chain = LangChainSQLIntegration()
        
        try:
            # Generate the SQL query
            start_time = time.time()
            sql_query, query_type = await sql_chain.generate_sql_query(chat_request.message)
            logger.info(f"Generated SQL query: {sql_query}, type: {query_type}")
            
            # Execute the query directly
            query_results = await sql_chain.execute_query(sql_query)
            query_time = time.time() - start_time
            
            # Format response using the format_response method
            response = await sql_chain.format_response(
                query_results=query_results,
                sql_query=sql_query,
                query_time=query_time,
                user_query=chat_request.message,
                query_type=query_type
            )
            
            return response
            
        except Exception as query_err:
            logger.error(f"Error processing query: {str(query_err)}")
            logger.error(traceback.format_exc())
            # Fallback to basic response
            return {
                "response": f"I encountered an error while processing your query about {chat_request.message}. Please try again.",
                "metadata": {
                    "error": str(query_err),
                    "original_query": chat_request.message
                }
            }
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

async def process_request(chat_request: ChatRequest):
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

@router.options("/query")
async def query_options():
    """Handle OPTIONS requests for query endpoint"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )
