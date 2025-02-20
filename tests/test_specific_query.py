import requests
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_specific_queries():
    """Test specific project queries with expected results"""
    logger.info("Starting specific project query tests...")
    
    # Test cases with expected results
    test_cases = [
        {
            "query": "Tell me about 'Nachuma Market Shed phase 3'",
            "expected": {
                "response_contains": [
                    "Nachuma Market Shed phase 3",
                    "Project Code: a631987d",
                    "District: Zomba",
                    "Region: Southern Region"
                ],
                "sql_contains": [
                    "SELECT",
                    "FROM proj_dashboard",
                    "PROJECTNAME",
                    "WHERE ISLATEST = 1"
                ]
            }
        },
        {
            "query": "What is the status of 'Boma Bus Depot and Market Toilets'",
            "expected": {
                "response_contains": [
                    "Boma Bus Depot and Market Toilets"
                ],
                "sql_contains": [
                    "SELECT",
                    "FROM proj_dashboard",
                    "PROJECTNAME",
                    "WHERE ISLATEST = 1",
                    "LIKE"
                ]
            }
        },
        {
            "query": "Show details about project MW-CR-DO",
            "expected": {
                "sql_contains": [
                    "SELECT",
                    "FROM proj_dashboard",
                    "PROJECTCODE",
                    "WHERE ISLATEST = 1",
                    "MW-CR-DO"
                ]
            }
        }
    ]
    
    results = []
    for test_case in test_cases:
        try:
            logger.info(f"\nTesting query: {test_case['query']}")
            
            # Make request to API
            response = requests.post(
                "http://localhost:8001/query",
                json={"message": test_case['query']}
            )
            
            # Log response
            logger.info(f"Status Code: {response.status_code}")
            
            # Parse response
            actual_response = response.json()
            
            # Create test result
            test_result = {
                "query": test_case['query'],
                "expected": test_case['expected'],
                "actual": actual_response,
                "status_code": response.status_code,
                "passed": False,
                "errors": []
            }
            
            # Verify response
            if response.status_code == 200:
                # Check response content
                if "response_contains" in test_case['expected']:
                    response_text = actual_response.get("response", "")
                    for expected_text in test_case['expected']['response_contains']:
                        if expected_text not in response_text:
                            test_result['errors'].append(
                                f"Missing expected text in response: '{expected_text}'"
                            )
                
                # Check SQL query
                if "sql_contains" in test_case['expected']:
                    sql = actual_response.get("source", {}).get("sql", "")
                    for expected_sql in test_case['expected']['sql_contains']:
                        if expected_sql not in sql:
                            test_result['errors'].append(
                                f"Missing expected SQL component: '{expected_sql}'"
                            )
            else:
                test_result['errors'].append(f"Unexpected status code: {response.status_code}")
            
            # Set passed status
            test_result['passed'] = len(test_result['errors']) == 0
            results.append(test_result)
            
        except Exception as e:
            logger.error(f"Error testing query: {str(e)}")
            results.append({
                "query": test_case['query'],
                "error": str(e),
                "passed": False
            })
    
    # Generate test report
    logger.info("\n=== Test Results ===")
    for result in results:
        logger.info(f"\nQuery: {result['query']}")
        logger.info(f"Passed: {result['passed']}")
        if not result['passed']:
            logger.info("Errors:")
            for error in result.get('errors', []):
                logger.info(f"  - {error}")
        logger.info("\nExpected:")
        logger.info(json.dumps(result['expected'], indent=2))
        logger.info("\nActual Response:")
        if "response" in result['actual']:
            logger.info(result['actual']['response'])
        logger.info("\nActual SQL:")
        if "source" in result['actual']:
            logger.info(result['actual']['source']['sql'])
        logger.info("-" * 50)
    
    # Calculate overall success
    success = all(result['passed'] for result in results)
    return success

if __name__ == "__main__":
    try:
        success = test_specific_queries()
        logger.info(f"Tests {'succeeded' if success else 'failed'}")
        import sys
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test script failed: {str(e)}")
        import sys
        sys.exit(1)
