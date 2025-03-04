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
                results.append({
                    "query": query,
                    "success": "error" not in response,
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
        working_queries = [r["query"] for r in results if r["success"]]
        failing_queries = [r["query"] for r in results if not r["success"]]
        
        return {
            "total_queries": len(results),
            "working_queries": len(working_queries),
            "failing_queries": len(failing_queries),
            "working_patterns": working_queries,
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
    print(f"Working queries: {analysis['working_queries']}")
    print(f"Failing queries: {analysis['failing_queries']}")
    
    print("\n=== Working Query Patterns ===")
    for query in analysis["working_patterns"]:
        print(f"✓ {query}")
    
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