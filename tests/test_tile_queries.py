import requests
import json
from datetime import datetime
import logging
import os
from typing import Dict, Any
import time

# Set up logging with a more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Simplified format for cleaner output
)
logger = logging.getLogger(__name__)

# Test configuration
API_URL = "http://localhost:5000/api/rag-sql-chatbot/chat"
RESULTS_FILE = "tile_test_results.json"

def format_sql(sql: str) -> str:
    """Format SQL query for better readability"""
    # Basic SQL formatting
    sql = sql.replace("SELECT", "\nSELECT")
    sql = sql.replace("FROM", "\nFROM")
    sql = sql.replace("WHERE", "\nWHERE")
    sql = sql.replace("GROUP BY", "\nGROUP BY")
    sql = sql.replace("ORDER BY", "\nORDER BY")
    return sql

def format_response(response_data: Dict[str, Any]) -> str:
    """Format the response data for better readability"""
    if not response_data.get("response", {}).get("results"):
        return "No results found"
    
    formatted = []
    for result in response_data["response"]["results"]:
        if "total_budget" in result:
            # Handle total budget response
            formatted.append(f"Total Budget: {result['total_budget']['formatted']}")
        else:
            # Handle project details
            project_details = [
                f"Project: {result.get('project_name', 'N/A')}",
                f"Location: {result.get('location', {}).get('district', 'N/A')}",
                f"Budget: {result.get('total_budget', {}).get('formatted', 'N/A')}",
                f"Status: {result.get('status', 'N/A')}",
                f"Sector: {result.get('project_sector', 'N/A')}"
            ]
            formatted.append("\n".join(project_details))
    
    return "\n\n".join(formatted)

def test_tile_queries():
    """Test the example queries from the tiles"""
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # API endpoint
    api_url = "http://localhost:5000/api/rag-sql-chatbot/chat"
    results_file = "tile_test_results.json"

    # Test queries
    test_queries = [
        {
            "title": "Sector Query",
            "description": "Testing query for finding projects by sector and calculating total budget",
            "natural_language_query": "What is the total budget for infrastructure projects?"
        },
        {
            "title": "Location Query",
            "description": "Testing query for finding projects by location",
            "natural_language_query": "Show me all projects in Zomba district"
        },
        {
            "title": "Status Query",
            "description": "Testing query for finding completed projects",
            "natural_language_query": "List all completed projects"
        }
    ]

    # Run tests and save results
    results = []
    for query in test_queries:
        logger.info(f"\n{'='*80}\nTesting: {query['title']}\n{'='*80}\n")
        
        # Log the natural language query
        logger.info("Natural Language Query:")
        logger.info("-" * 50)
        logger.info(query["natural_language_query"])
        logger.info("\n")
        
        try:
            # Send request to API
            start_time = time.time()
            response = requests.post(api_url, json={"message": query["natural_language_query"]})
            response_time = time.time() - start_time
            
            # Log the generated SQL
            logger.info("Generated SQL:")
            logger.info("-" * 50)
            if response.status_code == 200:
                response_data = response.json()
                sql_query = response_data.get("response", {}).get("metadata", {}).get("sql_query", "Not available")
                logger.info(sql_query)
            else:
                logger.info("Not available")
            logger.info("\n")
            
            # Log the API response
            logger.info("API Response:")
            logger.info("-" * 50)
            if response.status_code == 200:
                results_data = response_data.get("response", {}).get("results", [])
                for result in results_data:
                    if "total_budget" in result:
                        logger.info(f"Total Budget: {result['total_budget'].get('formatted', 'N/A')}")
                    else:
                        logger.info(f"Project: {result.get('project_name', 'N/A')}")
                        logger.info(f"District: {result.get('location', {}).get('district', 'N/A')}")
                        logger.info(f"Sector: {result.get('project_sector', 'N/A')}")
                        logger.info(f"Status: {result.get('status', 'N/A')}")
                        logger.info(f"Budget: {result.get('total_budget', {}).get('formatted', 'N/A')}")
                        logger.info("-" * 30)
            else:
                error_msg = response.json().get("detail", "No results found")
                logger.info(error_msg)
            logger.info("\n")
            
            # Log response time and status code
            logger.info(f"Response Time: {response_time:.2f} seconds")
            logger.info(f"Status Code: {response.status_code}\n")
            
            # Save test result
            results.append({
                "title": query["title"],
                "description": query["description"],
                "natural_language_query": query["natural_language_query"],
                "sql_query": sql_query if response.status_code == 200 else "Not available",
                "status_code": response.status_code,
                "response_time": response_time,
                "response_data": response_data if response.status_code == 200 else {"detail": str(response.text)}
            })
            
        except Exception as e:
            logger.error(f"Error testing query: {str(e)}")
            results.append({
                "title": query["title"],
                "description": query["description"],
                "natural_language_query": query["natural_language_query"],
                "sql_query": "Not available",
                "status_code": 500,
                "response_time": time.time() - start_time,
                "response_data": {"detail": f"Error testing query: {str(e)}"}
            })
    
    # Save results to file
    with open(results_file, "w") as f:
        json.dump({
            "test_run_time": datetime.now().isoformat(),
            "results": results
        }, f, indent=2)
    
    logger.info(f"\nTest results saved to {results_file}\n")

if __name__ == "__main__":
    test_tile_queries() 