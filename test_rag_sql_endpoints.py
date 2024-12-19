import requests
import json

# Configuration
BASE_URL = "http://localhost:8001"  # Local testing
LOCAL_URL = "http://localhost:8001"      # Local testing
FRONTEND_URL = "http://localhost:3000"  # Frontend URL
API_PREFIX = ""      # No API prefix for local testing

def test_endpoint(url, endpoint, payload=None, method="GET", expected_language=None):
    """Generic test function for endpoints"""
    full_url = f"{url}{API_PREFIX}{endpoint}"
    headers = {
        'Content-Type': 'application/json',
        'Origin': FRONTEND_URL,  # Simulate frontend request
        'Access-Control-Request-Method': 'POST'
    }
    
    try:
        if method == "GET":
            response = requests.get(full_url, headers=headers)
        elif method == "POST":
            response = requests.post(full_url, json=payload, headers=headers)
        
        print(f"\nTesting {full_url}")
        print(f"Headers: {json.dumps(headers, indent=2)}")
        print(f"Request Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        print(f"Status Code: {response.status_code}")
        print("Response Headers:")
        print(json.dumps(dict(response.headers), indent=2))
        print("Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing {endpoint}: {str(e)}")
        return False

def run_tests(base_url):
    """Run all endpoint tests"""
    print(f"\nTesting against: {base_url}")
    
    # Test health endpoint
    test_endpoint(base_url, "/health")
    
    # Test query with frontend-like request
    test_case = {
        "message": "Show me projects in Zomba district",
        "language": "en"
    }
    
    test_endpoint(base_url, "/query", test_case, "POST")

if __name__ == "__main__":
    print("=== Testing Frontend Communication ===")
    run_tests(LOCAL_URL)
