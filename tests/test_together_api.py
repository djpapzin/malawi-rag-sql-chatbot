import requests
import json
from datetime import datetime
import os

def test_query_endpoint():
    # Test setup
    url = "http://localhost:5000/query"
    test_cases = [
        {
            "name": "Basic SQL Query",
            "message": "How many records are in the dataset?",
            "expected_status": 200,
            "expected_type": "chat"
        },
        {
            "name": "Greeting Test",
            "message": "Hello, how are you?",
            "expected_status": 200,
            "expected_type": "chat"
        },
        {
            "name": "Invalid Query",
            "message": "What is the average age of people in the dataset?",
            "expected_status": 200,
            "expected_type": "chat"  # Should return chat explaining we don't have age data
        },
        {
            "name": "District Query",
            "message": "Show me all projects in Lilongwe",
            "expected_status": 200,
            "expected_type": "sql"
        },
        {
            "name": "Budget Query",
            "message": "What is the total budget for all projects?",
            "expected_status": 200,
            "expected_type": "sql"
        },
        {
            "name": "General Question",
            "message": "What kind of information can I ask about?",
            "expected_status": 200,
            "expected_type": "chat"
        }
    ]
    
    # Create results directory if it doesn't exist
    results_dir = "test_results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        
    # Generate timestamp for the results file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(results_dir, f"together_api_test_results_{timestamp}.md")
    
    with open(results_file, "w", encoding='utf-8') as f:
        # Write header
        f.write("# Together API Integration Test Results\n\n")
        f.write(f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Run tests
        for test_case in test_cases:
            f.write(f"## Test Case: {test_case['name']}\n\n")
            f.write(f"Input Message: `{test_case['message']}`\n\n")
            
            try:
                response = requests.post(url, json={"message": test_case['message']})
                
                f.write(f"Status Code: {response.status_code}\n\n")
                f.write("Response:\n```json\n")
                try:
                    formatted_response = json.dumps(response.json(), indent=2)
                    f.write(formatted_response)
                except:
                    f.write(str(response.text))
                f.write("\n```\n\n")
                
                # Test validation
                passed = True
                reasons = []
                
                # Check status code
                if response.status_code != test_case['expected_status']:
                    passed = False
                    reasons.append(f"Expected status {test_case['expected_status']}, got {response.status_code}")
                
                # Check response type
                try:
                    response_json = response.json()
                    if 'response' in response_json:
                        response_type = response_json['response'].get('query_type')
                        if response_type != test_case['expected_type']:
                            passed = False
                            reasons.append(f"Expected type {test_case['expected_type']}, got {response_type}")
                except:
                    passed = False
                    reasons.append("Could not parse response JSON")
                
                if passed:
                    f.write("[PASS] Test Passed\n\n")
                else:
                    f.write("[FAIL] Test Failed\n")
                    for reason in reasons:
                        f.write(f"- {reason}\n")
                    f.write("\n")
                    
            except Exception as e:
                f.write(f"[ERROR] {str(e)}\n\n")
            
            f.write("---\n\n")
            
        # Write summary
        f.write("# Test Summary\n\n")
        f.write(f"- Test file: `{os.path.basename(__file__)}`\n")
        f.write(f"- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- Server URL: {url}\n")
    
    print(f"Test results saved to: {results_file}")

if __name__ == "__main__":
    test_query_endpoint()
