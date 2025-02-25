import requests
import json
from datetime import datetime
import logging
import time
from typing import Dict, Any, List
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('query_tests.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
API_URL = "http://localhost:5000/query"
RESULTS_DIR = "test_results"
EXPECTED_FIELDS = {
    "general": ["project_name", "fiscal_year", "location", "total_budget", "status", "project_sector"],
    "specific": ["project_name", "fiscal_year", "location", "total_budget", "status", "project_sector", 
                 "contractor", "expenditure_to_date", "source_of_funding", "project_code", "last_monitoring_visit"]
}

class QueryTester:
    def __init__(self):
        self.test_queries = [
            {
                "title": "Infrastructure Budget Query",
                "description": "Get total budget for infrastructure projects",
                "query": "What is the total budget for infrastructure projects?",
                "expected_type": "general"
            },
            {
                "title": "Location-based Query",
                "description": "Get projects in Zomba district",
                "query": "Show me all projects in Zomba district",
                "expected_type": "general"
            },
            {
                "title": "Status-based Query",
                "description": "Get completed projects",
                "query": "List all completed projects",
                "expected_type": "general"
            }
        ]
        self.results = []
        os.makedirs(RESULTS_DIR, exist_ok=True)

    def validate_response_structure(self, response_data: Dict[str, Any], expected_type: str) -> List[str]:
        """Validate the structure of the API response."""
        errors = []
        try:
            if not isinstance(response_data, dict):
                return ["Response is not a dictionary"]
            
            if "response" not in response_data:
                errors.append("Missing 'response' key in response")
                return errors
            
            response = response_data["response"]
            if "results" not in response:
                errors.append("Missing 'results' key in response")
            
            if "metadata" not in response:
                errors.append("Missing 'metadata' key in response")
            
            # Check results structure
            if "results" in response:
                results = response["results"]
                if not isinstance(results, list):
                    errors.append("Results is not a list")
                elif results:
                    first_result = results[0]
                    for field in EXPECTED_FIELDS[expected_type]:
                        if field not in first_result:
                            errors.append(f"Missing expected field: {field}")
            
            # Check metadata structure
            if "metadata" in response:
                metadata = response["metadata"]
                expected_metadata_fields = ["total_results", "query_time", "sql_query"]
                for field in expected_metadata_fields:
                    if field not in metadata:
                        errors.append(f"Missing metadata field: {field}")
        
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        return errors

    def run_query_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single query test and return the results."""
        logger.info(f"\n{'='*80}\nTesting: {test_case['title']}\n{'='*80}")
        
        test_result = {
            "title": test_case["title"],
            "description": test_case["description"],
            "query": test_case["query"],
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "errors": [],
            "response_time": None,
            "response_data": None
        }

        try:
            # Send request and measure response time
            start_time = time.time()
            response = requests.post(API_URL, json={"message": test_case["query"]})
            test_result["response_time"] = time.time() - start_time

            # Log response time
            logger.info(f"Response Time: {test_result['response_time']:.2f} seconds")
            logger.info(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                response_data = response.json()
                test_result["response_data"] = response_data
                
                # Validate response structure
                validation_errors = self.validate_response_structure(
                    response_data, 
                    test_case["expected_type"]
                )
                
                if validation_errors:
                    test_result["errors"].extend(validation_errors)
                    logger.error("Validation Errors:")
                    for error in validation_errors:
                        logger.error(f"  - {error}")
                else:
                    test_result["success"] = True
                    logger.info("✓ Response validation successful")
                
                # Log the response data
                logger.info("\nResponse Data:")
                logger.info(json.dumps(response_data, indent=2))
            else:
                error_msg = f"Request failed with status code: {response.status_code}"
                test_result["errors"].append(error_msg)
                logger.error(error_msg)
                if response.text:
                    logger.error(f"Error response: {response.text}")

        except Exception as e:
            error_msg = f"Test execution error: {str(e)}"
            test_result["errors"].append(error_msg)
            logger.error(error_msg)

        return test_result

    def run_all_tests(self):
        """Run all test cases and save results."""
        logger.info(f"\nStarting test run at {datetime.now().isoformat()}")
        
        all_results = {
            "test_run_time": datetime.now().isoformat(),
            "total_tests": len(self.test_queries),
            "successful_tests": 0,
            "failed_tests": 0,
            "results": []
        }

        for test_case in self.test_queries:
            result = self.run_query_test(test_case)
            all_results["results"].append(result)
            
            if result["success"]:
                all_results["successful_tests"] += 1
            else:
                all_results["failed_tests"] += 1

        # Calculate success rate
        success_rate = (all_results["successful_tests"] / all_results["total_tests"]) * 100
        all_results["success_rate"] = f"{success_rate:.2f}%"

        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(RESULTS_DIR, f"query_test_results_{timestamp}.json")
        
        with open(results_file, "w") as f:
            json.dump(all_results, f, indent=2)
        
        logger.info(f"\nTest Results Summary:")
        logger.info(f"Total Tests: {all_results['total_tests']}")
        logger.info(f"Successful Tests: {all_results['successful_tests']}")
        logger.info(f"Failed Tests: {all_results['failed_tests']}")
        logger.info(f"Success Rate: {all_results['success_rate']}")
        logger.info(f"\nDetailed results saved to: {results_file}")

def main():
    """Main function to run the tests."""
    try:
        # Check if the API is available
        health_check = requests.get("http://localhost:5000/health")
        if health_check.status_code != 200:
            logger.error("API is not available. Please ensure the server is running.")
            return
        
        # Run the tests
        tester = QueryTester()
        tester.run_all_tests()
        
    except requests.exceptions.ConnectionError:
        logger.error("Could not connect to the API. Please ensure the server is running.")
    except Exception as e:
        logger.error(f"An error occurred while running tests: {str(e)}")

if __name__ == "__main__":
    main() 