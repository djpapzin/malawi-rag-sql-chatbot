import requests
import json
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API prefix from environment
API_PREFIX = os.getenv('API_PREFIX', '')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_query_endpoint():
    """Test the /query endpoint with various queries"""
    base_url = "http://127.0.0.1:8000"
    api_path = f"{API_PREFIX}/query"  # Include API prefix in path
    
    test_queries = [
        "How many education projects are there in Central Region?",
        "What is the total budget for all projects?",
        "List all projects in the Infrastructure sector",
        "Show me projects with completion percentage greater than 50%",
        "What is the average budget for projects in each district?",
    ]
    
    headers = {
        "Content-Type": "application/json"
    }
    
    for query in test_queries:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing query: {query}")
        logger.info('='*50)
        
        payload = {
            "message": query
        }
        
        try:
            url = f"{base_url}{api_path}"
            logger.info(f"Making request to: {url}")
            response = requests.post(
                url,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("Success!")
                logger.info("Natural Language Response:")
                logger.info(result.get("response", "No response"))
                logger.info("\nSQL Query:")
                if source := result.get("source"):
                    logger.info(source.get("sql", "No SQL query"))
                logger.info("\nMetadata:")
                if metadata := result.get("metadata"):
                    logger.info(f"Query ID: {metadata.get('query_id')}")
                    logger.info(f"Processing Time: {metadata.get('processing_time')}s")
                    logger.info(f"Timestamp: {metadata.get('timestamp')}")
            else:
                logger.error(f"Error! Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                
        except Exception as e:
            logger.error(f"Exception occurred: {str(e)}")
            continue

if __name__ == "__main__":
    logger.info("Testing API endpoints...")
    test_query_endpoint()