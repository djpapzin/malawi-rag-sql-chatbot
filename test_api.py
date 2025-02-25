import requests
import json
import time
from datetime import datetime

def test_query(query):
    url = "http://localhost:5000/query"
    headers = {"Content-Type": "application/json"}
    data = {"message": query}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        try:
            if hasattr(e.response, 'json'):
                error_details = e.response.json()
                if isinstance(error_details, dict) and 'detail' in error_details:
                    error_msg = error_details['detail']
                else:
                    error_msg = json.dumps(error_details, indent=2)
        except:
            pass
        return {"error": error_msg}

def save_test_results(results):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# API Test Results\n\n")
        f.write(f"Test run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for result in results:
            f.write(f"## Query: {result['query']}\n\n")
            
            if "error" in result['response']:
                f.write("### ❌ ERROR:\n")
                f.write(f"```\n{result['response']['error']}\n```\n\n")
            else:
                f.write("### ✅ SUCCESS:\n")
                response_data = result['response']
                
                if not isinstance(response_data, dict):
                    f.write(f"**Raw Response:**\n```\n{json.dumps(response_data, indent=2)}\n```\n\n")
                    continue
                    
                query_type = response_data.get('query_type', 'unknown')
                f.write(f"**Response Type:** {query_type}\n\n")
                
                if 'results' in response_data:
                    if query_type == 'chat':
                        message = response_data['results'][0].get('message', '')
                        f.write(f"**Message:**\n{message}\n\n")
                    else:
                        f.write("**Results:**\n")
                        f.write("```json\n")
                        f.write(json.dumps(response_data['results'], indent=2))
                        f.write("\n```\n\n")
                
                if "metadata" in response_data:
                    metadata = response_data["metadata"]
                    if isinstance(metadata, dict):
                        if "sql_query" in metadata:
                            f.write("**SQL Query:**\n")
                            f.write("```sql\n")
                            f.write(metadata["sql_query"])
                            f.write("\n```\n\n")
                        if "total_results" in metadata:
                            f.write(f"**Total Results:** {metadata['total_results']}\n\n")
                        if "query_time" in metadata:
                            f.write(f"**Query Time:** {metadata['query_time']}\n\n")
            
            f.write("---\n\n")
        
        f.write("\n## Summary\n\n")
        total = len(results)
        successful = sum(1 for r in results if "error" not in r['response'])
        f.write(f"- Total Tests: {total}\n")
        f.write(f"- Successful: {successful}\n")
        f.write(f"- Failed: {total - successful}\n")
    
    return filename

def run_tests():
    print("Starting API test...")
    results = []
    
    # Test cases
    queries = [
        # Greeting
        "hi",
        
        # District queries
        "Show me all projects in Zomba district",
        "What projects are there in Lilongwe?",
        
        # Budget queries
        "What is the total budget for all projects?",
        "What is the total budget for infrastructure projects?",
        
        # Status queries
        "Show me all completed projects",
        "List active projects",
        
        # Sector queries
        "Show me education projects",
        "List all infrastructure projects",
        
        # Invalid queries
        "What is the weather like?",
        "Tell me a joke",
        
        # Complex queries
        "Show me completed projects in the Southern Region",
        "What is the average budget for education projects?"
    ]
    
    for query in queries:
        print(f"\nTesting: {query}")
        response = test_query(query)
        results.append({
            "query": query,
            "response": response
        })
        time.sleep(1)  # Wait between tests to avoid overwhelming the server
    
    # Save results to markdown file
    filename = save_test_results(results)
    print(f"\nTest results saved to: {filename}")

if __name__ == "__main__":
    run_tests()