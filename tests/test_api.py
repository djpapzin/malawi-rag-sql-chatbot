import requests
import json
from datetime import datetime
import os

BASE_URL = "http://localhost:5000"
TEST_RESULTS_DIR = "test_results"

def ensure_results_dir():
    """Create test results directory if it doesn't exist"""
    if not os.path.exists(TEST_RESULTS_DIR):
        os.makedirs(TEST_RESULTS_DIR)

def save_test_results(results):
    """Save test results to a markdown file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{TEST_RESULTS_DIR}/api_test_results_{timestamp}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# API Test Results\n\n")
        f.write(f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for test in results:
            f.write(f"## Test Case: {test['name']}\n")
            f.write(f"Query: {test['query']}\n\n")
            
            if test['success']:
                f.write("Test Passed\n\n")
            else:
                f.write("Test Failed\n\n")
            
            f.write("### Response\n")
            f.write("```json\n")
            f.write(json.dumps(test['response'], indent=2))
            f.write("\n```\n\n")
            
            if test.get('error'):
                f.write("### Error\n")
                f.write(f"```\n{test['error']}\n```\n\n")
            
            f.write("---\n\n")
    
    print(f"Results saved to {filename}")

def test_query(query, name):
    """Test a specific query and return the results"""
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={"message": query}
        )
        
        return {
            "name": name,
            "query": query,
            "success": response.status_code == 200,
            "response": response.json() if response.status_code == 200 else None,
            "error": response.text if response.status_code != 200 else None
        }
    except Exception as e:
        return {
            "name": name,
            "query": query,
            "success": False,
            "response": None,
            "error": str(e)
        }

def run_tests():
    """Run all test cases"""
    test_cases = [
        {
            "name": "Total Budget Query",
            "query": "What is the total budget for all projects?"
        },
        {
            "name": "District Projects Query",
            "query": "List all projects in Zomba district"
        },
        {
            "name": "Sector Projects Query",
            "query": "List all infrastructure projects"
        },
        {
            "name": "Status Based Query",
            "query": "List all projects with Active status"
        },
        {
            "name": "Budget Range Query",
            "query": "What projects have a budget over 5 million?"
        },
        {
            "name": "Completion Percentage Query",
            "query": "Show projects that are more than 75% complete"
        },
        {
            "name": "Combined Criteria Query",
            "query": "List infrastructure projects in Lilongwe that are Active"
        },
        {
            "name": "Date Based Query",
            "query": "List projects starting in 2023"
        },
        {
            "name": "Project Count Query",
            "query": "Count the number of projects in each district"
        },
        {
            "name": "Average Budget Query",
            "query": "Calculate the average project budget for each sector"
        }
    ]
    
    results = []
    for test_case in test_cases:
        print(f"Running test: {test_case['name']}")
        result = test_query(test_case['query'], test_case['name'])
        results.append(result)
        if not result['success']:
            print(f"[FAIL] Test failed: {test_case['name']}")
        else:
            print(f"[PASS] Test passed: {test_case['name']}")
    
    return results

if __name__ == "__main__":
    print("Starting API tests...")
    ensure_results_dir()
    results = run_tests()
    save_test_results(results)
    print("Testing completed!")