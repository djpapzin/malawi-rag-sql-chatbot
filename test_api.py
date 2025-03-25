import requests
import json
from typing import Dict, Any
import time

def test_query(query: str) -> Dict[str, Any]:
    """Send a query to the API and return the response"""
    url = "https://dziwani.kwantu.support/api/rag-sql-chatbot/chat"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "message": query,
        "session_id": f"test_session_{int(time.time())}"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

def run_tests():
    """Run a series of test queries"""
    
    # Test sector queries
    sector_queries = [
        "Show me all healthcare projects",
        "What are the education projects",
        "List infrastructure projects",
        "Show water and sanitation projects",
        "What rural development projects are there"
    ]
    
    print("\nTesting sector queries:")
    print("=" * 50)
    for query in sector_queries:
        print(f"\nQuery: {query}")
        response = test_query(query)
        if response:
            print(f"Results found: {len(response.get('results', []))}")
            print("First result:")
            if response.get('results'):
                print(json.dumps(response['results'][0], indent=2))
        print("-" * 50)
    
    # Test specific project queries
    project_queries = [
        "Tell me about the Health Center Construction Project",
        "Show details of Water Supply Programme",
        "What is the status of the Rural Roads Development Project",
        "Give me information about the Education Infrastructure Program",
        "Tell me about the Community Development Scheme"
    ]
    
    print("\nTesting specific project queries:")
    print("=" * 50)
    for query in project_queries:
        print(f"\nQuery: {query}")
        response = test_query(query)
        if response:
            print(f"Results found: {len(response.get('results', []))}")
            print("First result:")
            if response.get('results'):
                print(json.dumps(response['results'][0], indent=2))
        print("-" * 50)

if __name__ == "__main__":
    run_tests() 