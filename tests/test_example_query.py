import requests
import json

def test_example_query():
    """Test an example query to demonstrate the chatbot's functionality"""
    
    # Test query
    query = {
        "message": "Tell me about education projects in Rumphi",
        "language": "english",
        "session_id": "test_session"
    }
    
    # Send request
    response = requests.post(
        "http://localhost:8001/query",
        json=query
    )
    
    # Save response
    result = response.json()
    with open("example_query_response.json", "w") as f:
        json.dump(result, f, indent=2)
        
    print(f"Query: {query['message']}")
    print(f"Response saved to example_query_response.json")

if __name__ == "__main__":
    test_example_query() 