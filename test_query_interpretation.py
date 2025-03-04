import asyncio
import json
from datetime import datetime
from app.query_parser import QueryParser

async def check_response_content(response: dict, expected_params: list) -> tuple[bool, list]:
    """Check if the response contains the expected parameters"""
    missing_params = []
    
    # Check if response has the required fields
    if not response.get("query") or not response.get("type"):
        return False, ["Invalid response format"]
    
    # Get the SQL query
    sql_query = response["query"].lower()
    
    # Check for each expected parameter
    for param in expected_params:
        param_lower = param.lower()
        if param_lower not in sql_query:
            missing_params.append(param)
    
    return len(missing_params) == 0, missing_params

async def main():
    parser = QueryParser()
    test_cases = [
        {
            "query": "Which projects are in Dowa?",
            "expected_params": ["dowa"],
            "description": "Basic district query"
        },
        {
            "query": "Show me all projects in Dowa district",
            "expected_params": ["dowa"],
            "description": "Alternative district format"
        },
        {
            "query": "I want to see projects in Dowa",
            "expected_params": ["dowa"],
            "description": "Natural district query"
        },
        {
            "query": "What projects exist in Dowa?",
            "expected_params": ["dowa"],
            "description": "Question-based district query"
        },
        {
            "query": "Show me health sector projects",
            "expected_params": ["health"],
            "description": "Health sector query"
        },
        {
            "query": "What education projects are there?",
            "expected_params": ["education"],
            "description": "Education sector query"
        },
        {
            "query": "List all water projects",
            "expected_params": ["water"],
            "description": "Water sector query"
        },
        {
            "query": "Show me health projects in Dowa",
            "expected_params": ["health", "dowa"],
            "description": "District and sector combined"
        },
        {
            "query": "List completed education projects",
            "expected_params": ["completed", "education"],
            "description": "Status and sector combined"
        },
        {
            "query": "What are the ongoing projects in Dowa?",
            "expected_params": ["ongoing", "dowa"],
            "description": "Status and district combined"
        }
    ]
    
    results = []
    for test_case in test_cases:
        try:
            # Parse the query
            parsed_query = await parser.parse_query(test_case["query"])
            
            # Check if the query was parsed correctly
            success, missing_params = await check_response_content(parsed_query, test_case["expected_params"])
            
            result = {
                "query": test_case["query"],
                "description": test_case["description"],
                "success": success,
                "missing_params": missing_params,
                "parsed_query": parsed_query
            }
            results.append(result)
            
            # Log the result
            print(f"\nTest: {test_case['description']}")
            print(f"Query: {test_case['query']}")
            print(f"Success: {'✓' if success else '✗'}")
            if missing_params:
                print(f"Missing parameters: {', '.join(missing_params)}")
            print(f"SQL Query: {parsed_query.get('query', '')}")
            print("-" * 50)
            
        except Exception as e:
            print(f"Error processing query '{test_case['query']}': {str(e)}")
            results.append({
                "query": test_case["query"],
                "description": test_case["description"],
                "success": False,
                "error": str(e)
            })
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"query_interpretation_results_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    total_tests = len(test_cases)
    passed_tests = sum(1 for r in results if r.get("success", False))
    failed_tests = total_tests - passed_tests
    
    print(f"\nTest Summary:")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"\nDetailed results saved to: {filename}")

if __name__ == "__main__":
    asyncio.run(main()) 