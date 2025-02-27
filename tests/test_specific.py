import requests
import json

def test_specific():
    url = "http://localhost:5000/api/rag-sql-chatbot/chat"
    headers = {"Content-Type": "application/json"}
    query = {"message": "Show me details about Mangochi infrastructure projects"}
    
    response = requests.post(url, headers=headers, json=query)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\nResults:")
        for project in result["response"]["results"]:
            print(f"\nProject: {project['project_name']}")
            print(f"Location: {project['location']['district']}")
            print(f"Budget: {project['total_budget']['formatted']}")
            print(f"Status: {project['project_status']}")
            print(f"Sector: {project['project_sector']}")
        
        print(f"\nTotal Results: {result['response']['metadata']['total_results']}")
        print(f"Query Time: {result['response']['metadata']['query_time']}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_specific() 