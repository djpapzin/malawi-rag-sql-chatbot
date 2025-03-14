"""
LLM Response Handler Module

This module handles the generation, formatting, and storage of LLM responses.
It implements the strategies outlined in the LLM Response Integration Plan.
"""

import json
import logging
import os
import time
import uuid
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResponseHandler:
    """
    Handles the generation, formatting, validation, and storage of LLM responses.
    """
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize the response handler.
        
        Args:
            storage_dir: Directory to store response logs. Defaults to app/logs.
        """
        self.storage_dir = storage_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        # Create logs directory if it doesn't exist
        Path(self.storage_dir).mkdir(parents=True, exist_ok=True)
        
        # Response type definitions
        self.response_types = {
            "greeting": "Friendly welcome responses",
            "help": "Information about system capabilities",
            "data": "Structured data responses from database queries",
            "error": "Error messages for failed queries",
            "other": "Fallback responses for unhandled queries"
        }
        
        # LLM configuration
        self.llm_config = {
            "temperature": 0.2,
            "max_tokens": 512,
            "presence_penalty": 0.5
        }
        
    def format_response(self, 
                        query_type: str, 
                        results: List[Dict[str, Any]], 
                        metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the response according to the standard structure.
        
        Args:
            query_type: Type of query (chat, sql, error)
            results: List of result objects
            metadata: Additional metadata about the query and response
            
        Returns:
            Formatted response dictionary
        """
        # Handle district queries
        if query_type == "district_query":
            # Extract district name from the query
            district_match = re.search(r'(?:in|at|from|of)(?: the)? ([a-zA-Z\s]+?) district', metadata.get("user_query", "").lower())
            if district_match:
                district_name = district_match.group(1).strip().title()
                if results:
                    formatted_results = [
                        {
                            "type": "text",
                            "message": f"Found {len(results)} projects in {district_name} district:",
                            "data": {}
                        }
                    ]
                    
                    # Add each project as a project_details result
                    for result in results:
                        project_data = {
                            "Name of project": result.get("PROJECTNAME", "N/A"),
                            "Fiscal year": result.get("FISCALYEAR", "N/A"),
                            "Location": f"{result.get('REGION', '')}, {result.get('DISTRICT', '')}, {result.get('TRADITIONALAUTHORITY', '')}".strip(", "),
                            "Budget": f"MWK {result.get('TOTALBUDGET', 0):,.2f}" if result.get('TOTALBUDGET') else "Not available",
                            "Status": result.get("PROJECTSTATUS", "N/A"),
                            "Contractor name": result.get("CONTRACTORNAME", "N/A"),
                            "Contract start date": result.get("SIGNINGDATE", "N/A"),
                            "Expenditure to date": f"MWK {result.get('TOTALEXPENDITURETODATE', 0):,.2f}" if result.get('TOTALEXPENDITURETODATE') else "Not available",
                            "Sector": result.get("PROJECTSECTOR", "N/A"),
                            "Source of funding": result.get("FUNDINGSOURCE", "N/A"),
                            "Project code": result.get("PROJECTCODE", "N/A"),
                            "Date of last Council monitoring visit": result.get("LASTVISIT", "N/A")
                        }
                        
                        formatted_results.append({
                            "type": "project_details",
                            "message": result.get("PROJECTNAME", "Unknown Project"),
                            "data": project_data
                        })
                    
                    return {
                        "results": formatted_results,
                        "metadata": {
                            "total_results": len(results),
                            "query_type": "district_query",
                            "filters_applied": {"district": district_name}
                        }
                    }
                else:
                    return {
                        "results": [{
                            "type": "text",
                            "message": f"No projects found in {district_name} district.",
                            "data": {}
                        }],
                        "metadata": {
                            "total_results": 0,
                            "query_type": "district_query",
                            "filters_applied": {"district": district_name}
                        }
                    }
        
        # Handle specific project queries
        elif query_type == "specific":
            if not results:
                return {
                    "results": [{
                        "type": "text",
                        "message": "No project found matching your query.",
                        "data": {}
                    }],
                    "metadata": {
                        "total_results": 0,
                        "query_type": "specific"
                    }
                }
                
            result = results[0]
            project_data = {
                "Name of project": result.get("PROJECTNAME", "N/A"),
                "Fiscal year": result.get("FISCALYEAR", "N/A"),
                "Location": f"{result.get('REGION', '')}, {result.get('DISTRICT', '')}, {result.get('TRADITIONALAUTHORITY', '')}".strip(", "),
                "Budget": f"MWK {result.get('TOTALBUDGET', 0):,.2f}" if result.get('TOTALBUDGET') else "Not available",
                "Status": result.get("PROJECTSTATUS", "N/A"),
                "Contractor name": result.get("CONTRACTORNAME", "N/A"),
                "Contract start date": result.get("SIGNINGDATE", "N/A"),
                "Expenditure to date": f"MWK {result.get('TOTALEXPENDITURETODATE', 0):,.2f}" if result.get('TOTALEXPENDITURETODATE') else "Not available",
                "Sector": result.get("PROJECTSECTOR", "N/A"),
                "Source of funding": result.get("FUNDINGSOURCE", "N/A"),
                "Project code": result.get("PROJECTCODE", "N/A"),
                "Date of last Council monitoring visit": result.get("LASTVISIT", "N/A")
            }
            
            # Create a descriptive summary
            summary = f"{project_data['Name of project']} is a {project_data['Sector']} project"
            if project_data['Location'] != "Not available":
                summary += f" in {project_data['Location']}"
            summary += f". The project is currently {project_data['Status']}"
            if project_data['Budget'] != "Not available":
                summary += f" with a budget of {project_data['Budget']}"
            summary += "."
            
            return {
                "results": [
                    {
                        "type": "text",
                        "message": summary,
                        "data": {}
                    },
                    {
                        "type": "project_details",
                        "message": "Project Details",
                        "data": project_data
                    }
                ],
                "metadata": {
                    "total_results": 1,
                    "query_type": "specific",
                    "project_name": project_data['Name of project'],
                    "project_sector": project_data['Sector']
                }
            }
        
        # Handle other query types
        return {
            "results": [{
                "type": "text",
                "message": str(results[0]) if results else "No results found.",
                "data": {}
            }],
            "metadata": metadata
        }
    
    def validate_response(self, response: Dict[str, Any]) -> bool:
        """
        Validate that the response meets the required format.
        
        Args:
            response: Response dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check basic structure
            if "response" not in response:
                logger.error("Response missing 'response' key")
                return False
                
            if "query_type" not in response["response"]:
                logger.error("Response missing 'query_type' key")
                return False
                
            if "results" not in response["response"]:
                logger.error("Response missing 'results' key")
                return False
                
            if "metadata" not in response["response"]:
                logger.error("Response missing 'metadata' key")
                return False
                
            # Check that results is a list
            if not isinstance(response["response"]["results"], list):
                logger.error("Response 'results' is not a list")
                return False
                
            # Check that each result has a type
            for result in response["response"]["results"]:
                if "type" not in result:
                    logger.error("Result missing 'type' key")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating response: {str(e)}")
            return False
    
    def store_response(self, 
                      query: str, 
                      response: Dict[str, Any],
                      session_id: str = None) -> str:
        """
        Store the response in a log file.
        
        Args:
            query: Original user query
            response: Formatted response dictionary
            session_id: Optional session ID for tracking conversations
            
        Returns:
            Path to the log file
        """
        try:
            # Generate filename based on current date
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(self.storage_dir, f"responses_{today}.jsonl")
            
            # Create log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "response_id": str(uuid.uuid4()),
                "session_id": session_id or "anonymous",
                "query": query,
                "response": response,
                "llm_metadata": {
                    "model": os.getenv("TOGETHER_AI_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K"),
                    "config": self.llm_config
                }
            }
            
            # Append to log file
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
            
            logger.info(f"Response stored in {log_file}")
            return log_file
        except Exception as e:
            logger.error(f"Error storing response: {str(e)}")
            return ""
    
    def get_prompt_template(self, prompt_type: str) -> str:
        """
        Get the prompt template for a specific response type.
        
        Args:
            prompt_type: Type of prompt (greeting, help, data, error)
            
        Returns:
            Prompt template string
        """
        templates = {
            "greeting": """You are a helpful assistant for a Malawi infrastructure projects database. The user has greeted you.
                        Respond warmly and suggest what kinds of questions they can ask about the projects.""",
            
            "help": """You are a helpful assistant for a Malawi infrastructure projects database. The user wants to know what information is available.
                    Explain what kinds of data we have about infrastructure projects in Malawi.""",
            
            "data": """You are a helpful assistant for a Malawi infrastructure projects database. The user has asked a specific question.
                    Based on the following data, provide a clear and concise answer to their question.
                    
                    Question: {question}
                    
                    Data: {data}
                    
                    SQL Query: {sql_query}
                    
                    Respond in a natural, conversational way. Include specific numbers and details from the data.""",
            
            "error": """You are a helpful assistant for a Malawi infrastructure projects database. The user's query could not be processed.
                      Explain the issue in a friendly way and suggest alternative questions they could ask.
                      
                      Error: {error}"""
        }
        
        return templates.get(prompt_type, templates["help"])
