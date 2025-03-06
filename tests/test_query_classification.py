import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "http://154.0.164.254:5000/api/rag-sql-chatbot/chat"

def test_query(query: str, chat_history: list = None) -> dict:
    """Test a single query and return the response"""
    try:
        payload = {
            "message": query,
            "language": "english",
            "page": 1,
            "page_size": 10
        }
        
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"\nQuery: {query}")
        logger.info(f"Response: {json.dumps(result, indent=2)}")
        
        return result
    except Exception as e:
        logger.error(f"Error testing query: {str(e)}")
        return None

def run_tests():
    """Run a series of test queries"""
    # Test unrelated queries
    logger.info("\n=== Testing Unrelated Queries ===")
    test_query("Hello, how are you?")
    test_query("What can you do?")
    test_query("Tell me about yourself")
    
    # Test general queries
    logger.info("\n=== Testing General Queries ===")
    test_query("Show me all projects in Lilongwe")
    test_query("List all health sector projects")
    test_query("What are the completed projects?")
    
    # Test specific queries
    logger.info("\n=== Testing Specific Queries ===")
    test_query("Tell me about the Lilongwe Water Project")
    test_query("What's the status of MW-HE-01?")
    
    # Test queries with multiple filters
    logger.info("\n=== Testing Queries with Multiple Filters ===")
    test_query("Show me completed health projects in Lilongwe")
    test_query("List all projects in Mzuzu with budget over 100 million")

if __name__ == "__main__":
    run_tests() 