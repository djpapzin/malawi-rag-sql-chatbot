import pytest
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8001"

# def test_status_endpoint():
#     """Test the status endpoint"""
#     response = requests.get(f"{BASE_URL}/api/rag-sql-chatbot/status")
#     assert response.status_code == 200
#     data = response.json()
#     assert "status" in data
#     assert data["status"] in ["ok", "error"]
#     assert "database" in data
#     assert "model" in data
#     assert "query_parser" in data

# def test_query_endpoint_english():
#     """Test the query endpoint with English input"""
#     print("\n" + "="*50)
#     print("Testing Query Endpoint (English)")
#     print("="*50)
#     
#     payload = {
#         "message": "Show me all projects in Lilongwe",
#         "language": "en"
#     }
#     print(f"\nSending request with payload:\n{json.dumps(payload, indent=2)}")
#     
#     response = requests.post(f"{BASE_URL}/api/rag-sql-chatbot/query", json=payload)
#     print(f"\nResponse status code: {response.status_code}")
#     
#     data = response.json()
#     print(f"\nResponse data:\n{json.dumps(data, indent=2)}")
#     
#     assert response.status_code == 200
#     assert "answer" in data
#     assert "suggested_questions" in data
#     assert isinstance(data["suggested_questions"], list)

def test_query_endpoint_no_language():
    """Test the query endpoint without specifying language (should default to 'en')"""
    print("\n" + "="*50)
    print("Testing Query Endpoint (Default Language)")
    print("="*50)
    
    payload = {
        "message": "Show me all projects in Lilongwe"
    }
    print(f"\nSending request with payload:\n{json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/rag-sql-chatbot/query", json=payload)
    print(f"\nResponse status code: {response.status_code}")
    
    data = response.json()
    print(f"\nResponse data:\n{json.dumps(data, indent=2)}")
    
    assert response.status_code == 200
    assert "answer" in data
    assert "suggested_questions" in data
    assert isinstance(data["suggested_questions"], list)

# def test_query_endpoint_invalid_request():
#     """Test the query endpoint with invalid request"""
#     payload = {
#         "message": ""  # Empty message should be invalid
#     }
#     response = requests.post(f"{BASE_URL}/api/rag-sql-chatbot/query", json=payload)
#     assert response.status_code in [400, 422]  # FastAPI validation error

# def test_parser_endpoint():
#     """Test the parser test endpoint"""
#     test_query = "Show projects in Lilongwe"
#     response = requests.get(f"{BASE_URL}/test/parser/{test_query}")
#     assert response.status_code == 200
#     data = response.json()
#     assert "status" in data
#     assert "original_query" in data
#     assert "parsed_filters" in data
#     assert data["original_query"] == test_query

# def test_db_endpoint():
#     """Test the database test endpoint"""
#     response = requests.get(f"{BASE_URL}/test/db")
#     assert response.status_code == 200
#     data = response.json()
#     assert "status" in data
#     assert "project_count" in data
#     assert isinstance(data["project_count"], int)

# def test_error_handling():
#     """Test error handling with invalid JSON"""
#     response = requests.post(
#         f"{BASE_URL}/api/rag-sql-chatbot/query", 
#         data="invalid json",
#         headers={"Content-Type": "application/json"}
#     )
#     assert response.status_code == 422  # FastAPI returns 422 for validation errors
#     data = response.json()
#     assert "detail" in data

# def test_more_results_endpoint():
#     """Test the pagination endpoint"""
#     # First make a query to get some results
#     initial_query = {
#         "message": "Show me all projects in Lilongwe",
#         "language": "en"
#     }
#     response = requests.post(f"{BASE_URL}/api/rag-sql-chatbot/query", json=initial_query)
#     assert response.status_code == 200
#     initial_response = response.json()
#     assert "answer" in initial_response
#     
#     # Now request more results
#     more_query = {
#         "message": "Show me more projects",
#         "chat_history": [
#             {"role": "user", "content": initial_query["message"]},
#             {"role": "assistant", "content": initial_response["answer"]}
#         ],
#         "language": "en"
#     }
#     more_response = requests.post(f"{BASE_URL}/api/rag-sql-chatbot/more", json=more_query)
#     
#     # Print response for debugging
#     print("\nMore endpoint response:")
#     print(f"Status code: {more_response.status_code}")
#     try:
#         print(f"Response body: {more_response.json()}")
#     except:
#         print(f"Raw response: {more_response.text}")
#     
#     # For now, we'll accept 500 as the endpoint might not be implemented yet
#     assert more_response.status_code in [200, 404, 500]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
