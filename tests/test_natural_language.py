import pytest
import json
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
API_URL = "http://localhost:5000/api/rag-sql-chatbot/chat"
HEADERS = {"Content-Type": "application/json"}

def test_natural_language_response():
    """Test that responses include natural language explanations"""

    # Test cases with expected content/phrases
    test_cases = [
        {
            "description": "Basic district query",
            "query": "Which projects are in Dowa?",
            "expected_content": ["projects", "Dowa", "district"]
        },
        {
            "description": "Alternative district query format",
            "query": "Show me all projects in Dowa district",
            "expected_content": ["projects", "Dowa", "district"]
        },
        {
            "description": "Natural district query",
            "query": "I want to see projects in Dowa",
            "expected_content": ["projects", "Dowa", "district"]
        },
        {
            "description": "Question-based district query",
            "query": "What projects exist in Dowa?",
            "expected_content": ["projects", "Dowa", "district"]
        },
        {
            "description": "Direct district query",
            "query": "Projects located in Dowa",
            "expected_content": ["projects", "Dowa", "district"]
        },
        {
            "description": "Informal district query",
            "query": "Tell me about projects in Dowa",
            "expected_content": ["projects", "Dowa", "district"]
        },
        {
            "description": "Existence check district query",
            "query": "Are there any projects in Dowa?",
            "expected_content": ["projects", "Dowa", "district"]
        },
        {
            "description": "Sector query",
            "query": "Show me health sector projects",
            "expected_content": ["health", "sector", "projects"]
        },
        {
            "description": "Question-based sector query",
            "query": "What education projects are there?",
            "expected_content": ["education", "projects"]
        },
        {
            "description": "Direct sector query",
            "query": "List all water projects",
            "expected_content": ["water", "projects"]
        },
        {
            "description": "Informal sector query",
            "query": "Tell me about transport projects",
            "expected_content": ["transport", "projects"]
        },
        {
            "description": "Need-based sector query",
            "query": "I need information about agriculture projects",
            "expected_content": ["agriculture", "projects"]
        },
        {
            "description": "Combined district and sector query",
            "query": "Show me health projects in Dowa",
            "expected_content": ["health", "projects", "Dowa", "district"]
        },
        {
            "description": "Combined status and sector query",
            "query": "List completed education projects",
            "expected_content": ["completed", "education", "projects"]
        },
        {
            "description": "Combined status and sector question",
            "query": "What are the ongoing water projects?",
            "expected_content": ["ongoing", "water", "projects"]
        }
    ]

    results = []

    for test_case in test_cases:
        try:
            # Send request
            response = requests.post(
                API_URL,
                headers=HEADERS,
                json={"message": test_case["query"]}
            )

            # Check status code
            assert response.status_code == 200, f"Request failed with status {response.status_code}"

            # Parse response
            data = response.json()

            # Verify response structure
            assert "results" in data, "Response missing 'results' field"
            assert len(data["results"]) > 0, "No results returned"

            # Check for natural language content
            result = data["results"][0]
            assert isinstance(result, dict), "Result is not a dictionary"
            assert "message" in result, f"Response missing natural language message in result: {result}"

            # Check for expected content
            message = result.get("message", "").lower()
            missing_content = [
                word for word in test_case["expected_content"]
                if word.lower() not in message
            ]

            test_passed = len(missing_content) == 0

            # Record result
            results.append({
                "test_case": test_case["description"],
                "query": test_case["query"],
                "passed": test_passed,
                "missing_content": missing_content if not test_passed else [],
                "response": message[:200] + "..." if len(message) > 200 else message
            })

        except Exception as e:
            logger.error(f"Error testing {test_case['description']}: {str(e)}")
            results.append({
                "test_case": test_case["description"],
                "query": test_case["query"],
                "passed": False,
                "error": str(e)
            })

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_{timestamp}.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    # Check if all tests passed
    failed_tests = [r for r in results if not r["passed"]]
    if failed_tests:
        for test in failed_tests:
            print(f"\nFailed test: {test['test_case']}")
            print(f"Query: {test['query']}")
            if "error" in test:
                print(f"Error: {test['error']}")
            else:
                print(f"Missing content: {test['missing_content']}")
                print(f"Response: {test['response']}")
        pytest.fail(f"{len(failed_tests)} test(s) failed. See {results_file} for details.")

if __name__ == "__main__":
    test_natural_language_response()
