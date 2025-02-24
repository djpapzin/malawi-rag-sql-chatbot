import requests
import json
import logging
from dotenv import load_dotenv
import os
from datetime import datetime
from result_handler import ResultHandler
import time

# Load environment variables
load_dotenv()

# Get API prefix from environment
API_PREFIX = os.getenv('API_PREFIX', '')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_query_endpoint():
    """Test the /query endpoint with various queries"""
    base_url = "http://127.0.0.1:5000"
    api_path = "/query"
    
    test_queries = [
        "What is the total budget for infrastructure projects?",
        "Show me all infrastructure projects",
        "What is the total budget for all projects?",
    ]
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Initialize result handler
    result_handler = ResultHandler()
    
    for i, query in enumerate(test_queries):
        # Add delay between requests to avoid rate limiting
        if i > 0:
            logger.info("Waiting 2 seconds to avoid rate limiting...")
            time.sleep(2)
            
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing query: {query}")
        logger.info('='*50)
        
        payload = {
            "message": query
        }
        
        try:
            response = requests.post(
                f"{base_url}{api_path}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Log raw response
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Raw Response: {response.text}")
            
            if response.ok:
                data = response.json()
                logger.info("\nResponse Data:")
                logger.info(json.dumps(data, indent=2))
                
                # Save results
                result_handler.add_result(
                    query=query,
                    status_code=response.status_code,
                    response_data=data,
                    timestamp=datetime.now().isoformat()
                )
            else:
                logger.error(f"Error: {response.text}")
                result_handler.add_result(
                    query=query,
                    status_code=response.status_code,
                    response_data={"error": response.text},
                    timestamp=datetime.now().isoformat()
                )
                
        except Exception as e:
            logger.error(f"Exception: {str(e)}")
            result_handler.add_result(
                query=query,
                status_code=500,
                response_data={"error": str(e)},
                timestamp=datetime.now().isoformat()
            )
            
    # Save results to markdown
    result_handler.save_results("api_test_results.md")

if __name__ == "__main__":
    logger.info("Testing API endpoints...")
    test_query_endpoint()