import requests
import json

def test_api():
    url = "http://localhost:8000/api/rag-sql-chatbot/query"
    headers = {"Content-Type": "application/json"}
    data = {"message": "What is the total budget for infrastructure projects?"}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_api() 