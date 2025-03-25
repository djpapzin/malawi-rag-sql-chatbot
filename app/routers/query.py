from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
import time
import traceback

from app.database.langchain_sql import LangChainSQLIntegration
from app.models import ChatRequest

router = APIRouter(
    tags=["query"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

logger = logging.getLogger(__name__)

@router.post("/", response_model=Dict[str, Any])
@router.post("/query", response_model=Dict[str, Any])
async def handle_query(chat_request: ChatRequest):
    """Handle query requests with direct SQL execution"""
    try:
        logger.info(f"Received query request: {chat_request}")
        sql_chain = LangChainSQLIntegration()
        
        try:
            # Generate the SQL query
            start_time = time.time()
            sql_query, query_type = await sql_chain.generate_sql_query(chat_request.message)
            logger.info(f"Generated SQL query: {sql_query}, type: {query_type}")
            
            # Execute the query directly
            results = await sql_chain.execute_query(sql_query)
            query_time = time.time() - start_time
            
            # Format results manually
            formatted_projects = []
            for project in results[:10]:  # Limit to 10 projects for display
                try:
                    # Extract key fields with case-insensitive handling
                    project_data = {}
                    
                    # Helper function to get value with case-insensitive keys
                    def get_value(keys):
                        for key in keys:
                            if key in project and project[key] is not None:
                                return project[key]
                        return "Unknown"
                    
                    # Get basic project info - prioritize the uppercase keys as they match the DB schema
                    project_data["Name of project"] = get_value(["PROJECTNAME", "project_name", "projectname"])
                    project_data["Fiscal year"] = get_value(["FISCALYEAR", "fiscal_year", "fiscalyear"])
                    project_data["Location"] = get_value(["DISTRICT", "district", "location"])
                    
                    # Handle budget with formatting - prioritize the uppercase BUDGET field
                    budget = None
                    for key in ["BUDGET", "total_budget", "budget"]:
                        if key in project and project[key] is not None:
                            try:
                                budget = float(project[key])
                                break
                            except (ValueError, TypeError):
                                continue
                    project_data["Budget"] = f"MWK {budget:,.2f}" if budget is not None else "Unknown"
                    
                    # Get remaining fields - prioritize uppercase fields
                    project_data["Status"] = get_value(["PROJECTSTATUS", "status", "projectstatus"])
                    project_data["Sector"] = get_value(["PROJECTSECTOR", "project_sector", "projectsector"])
                    
                    # Add to formatted results
                    formatted_projects.append(project_data)
                except Exception as e:
                    logger.error(f"Error formatting project: {str(e)}")
            
            # Prepare metadata
            metadata = {
                "total_results": len(results),
                "query_time": f"{query_time:.2f}s",
                "sql_query": sql_query[1] if isinstance(sql_query, tuple) else sql_query,
                "original_query": chat_request.message,
                "query_type": query_type
            }
            
            # Create final response
            if formatted_projects:
                response_text = f"Found {len(results)} projects in the {query_type} sector." if query_type else f"Found {len(results)} projects matching your query."
                if len(results) > 10:
                    response_text += " Showing the first 10 results."
            else:
                response_text = "No projects found matching your query."
            
            return {
                "response": response_text,
                "projects": formatted_projects,
                "metadata": metadata
            }
            
        except Exception as query_err:
            logger.error(f"Error processing query: {str(query_err)}")
            # Fallback to basic response
            return {
                "response": f"I encountered an error while processing your query about {chat_request.message}. Please try again.",
                "metadata": {
                    "error": str(query_err),
                    "original_query": chat_request.message
                }
            }
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )
