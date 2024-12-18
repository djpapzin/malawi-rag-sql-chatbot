import requests
import json

def test_query(message: str):
    """Test a specific query"""
    url = "http://localhost:8003/query"
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

def run_tests():
    """Run multiple test queries"""
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
    
    # Print summary
    print("\nTest Summary:")
    for i, (query, result) in enumerate(zip(test_queries, results)):
        project_count = result['metadata']['row_count'] if result.get('metadata') else 0
        print(f"{i+1}. '{query}' -> Found {project_count} projects")

if __name__ == "__main__":
    run_tests() 