import requests
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API configuration
API_URL = "http://localhost:5000/api/rag-sql-chatbot/chat"
HEADERS = {"Content-Type": "application/json"}

def test_query(query: str) -> dict:
    """Test a single query and return the results"""
    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={"message": query}
        )
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Request failed with status {response.status_code}"
            }
            
        data = response.json()
        return {
            "success": True,
            "response": data
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def check_response_content(response: dict, expected_params: list) -> tuple[bool, list]:
    """Check if the response contains the expected parameters"""
    if not response.get("results"):
        return False, expected_params
        
    # Check the first result's message
    message = response["results"][0].get("message", "").lower()
    
    # Check the data values if present
    data_values = []
    if len(response["results"]) > 1 and response["results"][1].get("type") == "list":
        data_values = [
            value.get("Location", "").lower() for value in 
            response["results"][1].get("data", {}).get("values", [])
        ]
    
    # Check for missing parameters
    missing_params = []
    for param in expected_params:
        param_lower = param.lower()
        if param_lower not in message and param_lower not in data_values:
            missing_params.append(param)
            
    return len(missing_params) == 0, missing_params

def main():
    # Test cases covering different query patterns
    test_cases = [
        # District queries
        {
            "description": "Basic district query",
            "query": "Which projects are in Dowa?",
            "expected_type": "district",
            "expected_params": ["Dowa"]
        },
        {
            "description": "Alternative district format",
            "query": "Show me all projects in Dowa district",
            "expected_type": "district",
            "expected_params": ["Dowa"]
        },
        {
            "description": "Natural district query",
            "query": "I want to see projects in Dowa",
            "expected_type": "district",
            "expected_params": ["Dowa"]
        },
        {
            "description": "Question-based district query",
            "query": "What projects exist in Dowa?",
            "expected_type": "district",
            "expected_params": ["Dowa"]
        },
        
        # Sector queries
        {
            "description": "Health sector query",
            "query": "Show me health sector projects",
            "expected_type": "sector",
            "expected_params": ["health"]
        },
        {
            "description": "Education sector query",
            "query": "What education projects are there?",
            "expected_type": "sector",
            "expected_params": ["education"]
        },
        {
            "description": "Water sector query",
            "query": "List all water projects",
            "expected_type": "sector",
            "expected_params": ["water"]
        },
        
        # Combined queries
        {
            "description": "District and sector combined",
            "query": "Show me health projects in Dowa",
            "expected_type": "combined",
            "expected_params": ["health", "Dowa"]
        },
        {
            "description": "Status and sector combined",
            "query": "List completed education projects",
            "expected_type": "combined",
            "expected_params": ["completed", "education"]
        },
        {
            "description": "Status and district combined",
            "query": "What are the ongoing projects in Dowa?",
            "expected_type": "combined",
            "expected_params": ["ongoing", "Dowa"]
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        logger.info(f"\nTesting: {test_case['description']}")
        logger.info(f"Query: {test_case['query']}")
        
        result = test_query(test_case["query"])
        
        if not result["success"]:
            logger.error(f"Test failed: {result['error']}")
            results.append({
                "test_case": test_case["description"],
                "query": test_case["query"],
                "success": False,
                "error": result["error"]
            })
            continue
            
        response = result["response"]
        
        # Check if response contains expected content
        success, missing_params = check_response_content(response, test_case["expected_params"])
        
        test_result = {
            "test_case": test_case["description"],
            "query": test_case["query"],
            "success": success,
            "response": response["results"][0].get("message", "") if response.get("results") else ""
        }
        
        if missing_params:
            test_result["missing_params"] = missing_params
            
        results.append(test_result)
        
        # Log the result
        if test_result["success"]:
            logger.info("✓ Test passed")
        else:
            logger.error(f"✗ Test failed - Missing parameters: {missing_params}")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"query_interpretation_results_{timestamp}.json"
    
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    passed_tests = sum(1 for r in results if r["success"])
    total_tests = len(results)
    
    print(f"\nTest Summary:")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"\nDetailed results saved to: {results_file}")

if __name__ == "__main__":
    main() 