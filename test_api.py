import requests
import json

def test_api():
    url = "http://localhost:8000/api/rag-sql-chatbot/query"
    headers = {"Content-Type": "application/json"}
    
    # Test general query
    general_query = {"message": "Show me all infrastructure projects"}
    print("\nTesting general query:", general_query["message"])
    try:
        response = requests.post(url, headers=headers, json=general_query)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("\nResults:")
            for project in result["response"]["results"]:
                print(f"\nProject: {project['project_name']}")
                print(f"Location: {project['location']['region']}, {project['location']['district']}")
                print(f"Budget: {project['total_budget']['formatted']}")
                print(f"Status: {project['project_status']}")
                print(f"Sector: {project['project_sector']}")
            
            print(f"\nTotal Results: {result['response']['metadata']['total_results']}")
            print(f"Query Time: {result['response']['metadata']['query_time']}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test specific query
    specific_query = {"message": "Give me details about the Mangochi Road Rehabilitation project"}
    print("\nTesting specific query:", specific_query["message"])
    try:
        response = requests.post(url, headers=headers, json=specific_query)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("\nResults:")
            for project in result["response"]["results"]:
                print(f"\nProject Details:")
                print(f"Name: {project['project_name']}")
                print(f"Location: {project['location']['region']}, {project['location']['district']}")
                print(f"Budget: {project['total_budget']['formatted']}")
                print(f"Status: {project['project_status']}")
                print(f"Contractor: {project['contractor']['name']}")
                print(f"Contract Start: {project['contractor']['contract_start_date']}")
                print(f"Expenditure: {project['expenditure_to_date']['formatted']}")
                print(f"Sector: {project['project_sector']}")
                print(f"Funding Source: {project['source_of_funding']}")
                print(f"Project Code: {project['project_code']}")
                print(f"Last Monitoring: {project['last_monitoring_visit']}")
            
            print(f"\nTotal Results: {result['response']['metadata']['total_results']}")
            print(f"Query Time: {result['response']['metadata']['query_time']}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_api() 