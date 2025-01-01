import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_query_endpoint():
    """Test the /query endpoint with various queries"""
    base_url = "http://localhost:8001"
    
    test_queries = [
        "Show me all projects",
        "Show projects in Central Region",
        "Show education sector projects",
        "Show projects in progress",
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    for query in test_queries:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing query: {query}")
        logger.info('='*50)
        
        payload = {
            "message": query,
            "source_lang": "english",
            "page": 1,
            "page_size": 5
        }
        
        try:
            response = requests.post(
                f"{base_url}/query",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("Success!")
                logger.info(f"Response message: {result.get('message', '')}")
                logger.info(f"Response text: {result.get('response', '')}")
                
                # Log SQL query details
                source = result.get('source', {})
                sql = source.get('sql', '')
                logger.info(f"SQL Query: {sql}")
                logger.info(f"Source details: {json.dumps(source, indent=2)}")
                
                # Log metadata
                metadata = result.get('metadata', {})
                logger.info(f"Metadata: {json.dumps(metadata, indent=2)}")
            else:
                logger.error(f"Error {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")

def test_health_endpoint():
    """Test the /health endpoint"""
    try:
        response = requests.get("http://localhost:8001/health")
        if response.status_code == 200:
            logger.info("\nHealth check passed!")
            logger.info(json.dumps(response.json(), indent=2))
        else:
            logger.error(f"Health check failed: {response.status_code}")
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")

if __name__ == "__main__":
    logger.info("Testing API endpoints...")
    test_health_endpoint()
    test_query_endpoint() 