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
            "query": "Tell me about Mangochi Hospital Improvement Phase 9",
            "expected": {
                "response_contains": [
                    "Mangochi Hospital Improvement Phase 9",
                    "MWK 2,205,357.14",
                    "35.0% Complete",
                    "Mangochi"
                ],
                "sql_contains": [
                    "SELECT",
                    "FROM proj_dashboard",
                    "LOWER(projectname)",
                    "LIKE"
                ]
            }
        },
        {
            "query": "What is the status of Mangochi Bridge Rehabilitation Phase 27",
            "expected": {
                "response_contains": [
                    "Mangochi Bridge Rehabilitation Phase 27",
                    "MWK 5,616,071.43",
                    "100.0% Complete"
                ],
                "sql_contains": [
                    "SELECT",
                    "FROM proj_dashboard",
                    "LOWER(projectname)",
                    "LIKE"
                ]
            }
        },
        {
            "query": "Show details about Mangochi Irrigation Improvement Phase 44",
            "expected": {
                "response_contains": [
                    "Mangochi Irrigation Improvement Phase 44",
                    "MWK 9,026,785.71",
                    "55.0% Complete"
                ],
                "sql_contains": [
                    "SELECT",
                    "FROM proj_dashboard",
                    "LOWER(projectname)",
                    "LIKE"
                ]
            }
        }
    ]
    
    results = []
    with open('specific_test_results.txt', 'w') as f:
        f.write("=== Specific Query Test Results ===\n")
        f.write(f"Test Run Time: {datetime.now().isoformat()}\n\n")
        
        for test_case in test_cases:
            try:
                logger.info(f"\nTesting query: {test_case['query']}")
                f.write(f"\nTesting query: {test_case['query']}\n")
                
                # Make request to API
                response = requests.post(
                    "http://localhost:5000/query",
                    json={"message": test_case['query']}
                )
                
                # Log response
                logger.info(f"Status Code: {response.status_code}")
                f.write(f"Status Code: {response.status_code}\n")
                
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
                        # Convert response to string for easier searching
                        response_str = json.dumps(actual_response)
                        for expected_text in test_case['expected']['response_contains']:
                            if expected_text not in response_str:
                                test_result['errors'].append(
                                    f"Missing expected text in response: '{expected_text}'"
                                )
                    
                    # Check SQL query
                    if "sql_contains" in test_case['expected']:
                        sql = actual_response.get("response", {}).get("metadata", {}).get("sql_query", "")
                        for expected_sql in test_case['expected']['sql_contains']:
                            if expected_sql.lower() not in sql.lower():
                                test_result['errors'].append(
                                    f"Missing expected SQL component: '{expected_sql}'"
                                )
                else:
                    test_result['errors'].append(f"Unexpected status code: {response.status_code}")
                
                # Set passed status
                test_result['passed'] = len(test_result['errors']) == 0
                results.append(test_result)
                
                # Write results to file
                f.write("\nTest Result:\n")
                f.write(f"Passed: {test_result['passed']}\n")
                if not test_result['passed']:
                    f.write("Errors:\n")
                    for error in test_result['errors']:
                        f.write(f"  - {error}\n")
                
                f.write("\nExpected:\n")
                f.write(json.dumps(test_result['expected'], indent=2) + "\n")
                
                f.write("\nActual Response:\n")
                f.write(str(actual_response) + "\n")
                f.write("-" * 50 + "\n")
                
            except Exception as e:
                logger.error(f"Error testing query: {str(e)}")
                f.write(f"\nError testing query: {str(e)}\n")
                results.append({
                    "query": test_case['query'],
                    "error": str(e),
                    "passed": False
                })
        
        # Write summary
        success = all(result['passed'] for result in results)
        f.write("\n=== Test Summary ===\n")
        f.write(f"Total Tests: {len(results)}\n")
        f.write(f"Passed: {sum(1 for r in results if r['passed'])}\n")
        f.write(f"Failed: {sum(1 for r in results if not r['passed'])}\n")
        f.write(f"Overall Status: {'SUCCESS' if success else 'FAILED'}\n")
    
    logger.info("Test results have been written to specific_test_results.txt")
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
