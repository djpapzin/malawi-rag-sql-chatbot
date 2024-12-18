import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:8003"

def test_query(message: str):
    """Test a specific query"""
    url = f"{BASE_URL}/query"
    headers = {"Content-Type": "application/json"}
    data = {
        "message": message,
        "language": "en"
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"\nTesting query: {message}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_health():
    """Test the health check endpoint"""
    url = f"{BASE_URL}/health"
    response = requests.get(url)
    print("\nTesting health endpoint...")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def run_tests():
    """Run multiple test queries"""
    # Wait for server to start
    print("\nWaiting for server to start...")
    time.sleep(2)
    
    # Test health endpoint
    health_response = test_health()
    assert health_response["status"] == "healthy"
    
    # Test queries
    test_queries = [
        "Show me education projects",
        "Show me completed health projects in the Southern Region",
        "What are the highest budget transport projects?",
        "Show me water projects in progress",
        "Show me projects in the Central Region"
    ]
    
    results = []
    for query in test_queries:
        result = test_query(query)
        results.append(result)
        time.sleep(0.5)  # Small delay between requests
    
    # Print summary
    print("\nTest Summary:")
    for i, (query, result) in enumerate(zip(test_queries, results)):
        project_count = result['metadata']['row_count'] if result.get('metadata') else 0
        print(f"{i+1}. '{query}' -> Found {project_count} projects")
        
        # Verify response structure
        assert "answer" in result
        assert "suggested_questions" in result
        assert "metadata" in result
        assert "sources" in result
        
        # Verify metadata
        metadata = result["metadata"]
        assert "query_id" in metadata
        assert "execution_time" in metadata
        assert "row_count" in metadata
        assert "timestamp" in metadata
        assert "sources" in metadata
        
        # Verify sources
        assert isinstance(result["sources"], list)
        if result["sources"]:
            source = result["sources"][0]
            assert "table" in source
            assert "columns" in source
            assert "operation" in source
    
    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    run_tests() 