import requests
import json
from typing import List, Dict
import time

class QueryVariationTester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.endpoint = f"{base_url}/api/rag-sql-chatbot/chat"
        
    def test_query(self, query: str) -> Dict:
        """Test a single query and return the response"""
        payload = {"message": query}
        response = requests.post(self.endpoint, json=payload)
        return response.json()
    
    def verify_response(self, response: Dict, query: str, district: str) -> Dict:
        """Verify the response contains the expected data"""
        verification = {
            "has_error": "error" in response,
            "has_results": False,
            "has_correct_district": False,
            "has_project_list": False,
            "has_metadata": False,
            "total_results": 0
        }
        
        if not verification["has_error"]:
            # Check for results
            if "results" in response and len(response["results"]) > 0:
                verification["has_results"] = True
                
                # Check for project list
                for result in response["results"]:
                    if result.get("type") == "list" and "data" in result:
                        verification["has_project_list"] = True
                        # Check if district is correct in the results
                        if "values" in result["data"]:
                            for project in result["data"]["values"]:
                                if project.get("Location", "").lower() == district.lower():
                                    verification["has_correct_district"] = True
                                    break
            
            # Check for metadata
            if "metadata" in response:
                verification["has_metadata"] = True
                verification["total_results"] = response["metadata"].get("total_results", 0)
        
        return verification
    
    def test_district_variations(self, district: str = "Dowa") -> List[Dict]:
        """Test various ways of asking for projects in a district"""
        variations = [
            f"Which projects are in {district}?",
            f"Show me all projects in {district} district",
            f"List projects from {district}",
            f"What projects exist in {district}?",
            f"Projects located in {district}",
            f"Give me projects in {district}",
            f"Show projects in {district}",
            f"Find projects in {district}",
            f"Display projects from {district}",
            f"What are the projects in {district}?",
            f"Can you show me projects in {district}?",
            f"I want to see projects in {district}",
            f"Looking for projects in {district}",
            f"Need information about projects in {district}",
            f"Tell me about projects in {district}"
        ]
        
        results = []
        for query in variations:
            print(f"\nTesting query: {query}")
            try:
                response = self.test_query(query)
                verification = self.verify_response(response, query, district)
                results.append({
                    "query": query,
                    "success": not verification["has_error"],
                    "verification": verification,
                    "response": response
                })
                # Add a small delay to avoid overwhelming the server
                time.sleep(0.5)
            except Exception as e:
                results.append({
                    "query": query,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def analyze_results(self, results: List[Dict]) -> Dict:
        """Analyze the test results"""
        working_queries = []
        partially_working_queries = []
        failing_queries = []
        
        for result in results:
            if not result["success"]:
                failing_queries.append(result["query"])
            else:
                verification = result["verification"]
                if all([
                    verification["has_results"],
                    verification["has_project_list"],
                    verification["has_correct_district"],
                    verification["has_metadata"],
                    verification["total_results"] > 0
                ]):
                    working_queries.append(result["query"])
                else:
                    partially_working_queries.append({
                        "query": result["query"],
                        "missing": [
                            k for k, v in verification.items() 
                            if k != "has_error" and not v
                        ]
                    })
        
        return {
            "total_queries": len(results),
            "working_queries": len(working_queries),
            "partially_working_queries": len(partially_working_queries),
            "failing_queries": len(failing_queries),
            "working_patterns": working_queries,
            "partially_working_patterns": partially_working_queries,
            "failing_patterns": failing_queries
        }

def main():
    tester = QueryVariationTester()
    
    # Test district queries
    print("Testing district query variations...")
    district_results = tester.test_district_variations()
    
    # Analyze results
    analysis = tester.analyze_results(district_results)
    
    # Print summary
    print("\n=== Test Results Summary ===")
    print(f"Total queries tested: {analysis['total_queries']}")
    print(f"Fully working queries: {analysis['working_queries']}")
    print(f"Partially working queries: {analysis['partially_working_queries']}")
    print(f"Failing queries: {analysis['failing_queries']}")
    
    print("\n=== Working Query Patterns ===")
    for query in analysis["working_patterns"]:
        print(f"✓ {query}")
    
    print("\n=== Partially Working Query Patterns ===")
    for item in analysis["partially_working_patterns"]:
        print(f"⚠ {item['query']}")
        print(f"  Missing: {', '.join(item['missing'])}")
    
    print("\n=== Failing Query Patterns ===")
    for query in analysis["failing_patterns"]:
        print(f"✗ {query}")
    
    # Save detailed results to file
    with open("query_variation_results.json", "w") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": district_results,
            "analysis": analysis
        }, f, indent=2)

if __name__ == "__main__":
    main() 