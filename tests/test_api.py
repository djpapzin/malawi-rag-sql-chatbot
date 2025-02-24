import requests
import json
from requests.exceptions import Timeout, RequestException
import time

def test_api():
    url = "http://localhost:5000/query"
    headers = {"Content-Type": "application/json"}
    timeout = 30  # 30 seconds timeout
    
    def make_request(query_data, max_retries=3):
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=query_data, timeout=timeout)
                return response
            except Timeout:
                print(f"Request timed out (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait 2 seconds before retrying
                else:
                    raise
            except RequestException as e:
                print(f"Request failed: {str(e)}")
                raise
    
    with open('test_results.txt', 'w') as f:
        # Test general query
        general_query = {"message": "Show me all infrastructure projects"}
        f.write(f"\nTesting general query: {general_query['message']}\n")
        try:
            response = make_request(general_query)
            f.write(f"Status Code: {response.status_code}\n")
            if response.status_code == 200:
                result = response.json()
                f.write("\nResults:\n")
                for project in result["response"]["results"]:
                    f.write(f"\nProject: {project['project_name']}\n")
                    f.write(f"Location: {project['location']['region']}, {project['location']['district']}\n")
                    f.write(f"Budget: {project['total_budget']['formatted']}\n")
                    f.write(f"Status: {project['project_status']}\n")
                    f.write(f"Sector: {project['project_sector']}\n")
                
                f.write(f"\nTotal Results: {result['response']['metadata']['total_results']}\n")
                f.write(f"Query Time: {result['response']['metadata']['query_time']}\n")
            else:
                f.write(f"Error response: {response.text}\n")
        except Exception as e:
            f.write(f"Error processing general query: {str(e)}\n")
        
        # Wait a bit before the next request
        time.sleep(2)
        
        # Test specific query
        specific_query = {"message": "Show me details about Mangochi infrastructure projects"}
        print(f"\nTesting specific query: {specific_query['message']}")
        try:
            response = make_request(specific_query)
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
            else:
                print(f"Error response: {response.text}")
        except Exception as e:
            print(f"Error processing specific query: {str(e)}")
        
        print("Test results have been written to test_results.txt")

if __name__ == "__main__":
    test_api() 