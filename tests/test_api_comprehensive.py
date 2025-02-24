import requests
import json
import logging
from datetime import datetime
import time
from typing import Dict, Any, List
import os
from tabulate import tabulate
import traceback

# Configure logging with a cleaner format
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Simplified format for cleaner output
)
logger = logging.getLogger(__name__)

# Configuration
API_URL = "http://localhost:5000/query"
RESULTS_FILE = "api_test_results.json"
HTML_REPORT_FILE = "api_test_report.html"

def format_currency(amount: float) -> str:
    """Format amount as MWK currency"""
    return f"MWK {amount:,.2f}"

def format_sql(sql: str) -> str:
    """Format SQL query for better readability"""
    sql = sql.strip()
    keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING', 'JOIN']
    for keyword in keywords:
        sql = sql.replace(keyword, f'\n{keyword}')
    return sql.strip()

def print_separator(char="=", length=80):
    """Print a separator line"""
    logger.info(char * length)

def print_section(title, content=""):
    """Print a section with title and optional content"""
    print_separator("-", 40)
    logger.info(f"{title}:")
    if content:
        logger.info(content)
    logger.info("")

def run_test(query: Dict[str, Any]) -> Dict[str, Any]:
    """Run a single test and return the results"""
    start_time = time.time()
    
    try:
        # Send request to API
        response = requests.post(API_URL, json={"message": query["natural_language_query"]}, timeout=30)
        response_time = time.time() - start_time
        
        # Process response
        result = {
            "title": query["title"],
            "category": query["category"],
            "description": query["description"],
            "natural_language_query": query["natural_language_query"],
            "expected_content": query.get("expected_content", []),
            "expected_sql_components": query.get("expected_sql_components", []),
            "response_time": response_time,
            "status_code": response.status_code,
            "errors": []
        }
        
        # Extract SQL and response data
        if response.status_code == 200:
            response_data = response.json()
            result["sql_query"] = response_data.get("metadata", {}).get("sql_query", "Not available")
            result["response_data"] = response_data
            
            # Validate expected content
            response_str = json.dumps(response_data).lower()
            for content in query.get("expected_content", []):
                if content.lower() not in response_str:
                    result["errors"].append(f"Missing expected content: {content}")
            
            # Validate SQL components
            sql_str = result["sql_query"].lower()
            for component in query.get("expected_sql_components", []):
                if component.lower() not in sql_str:
                    result["errors"].append(f"Missing SQL component: {component}")
        else:
            result["sql_query"] = "Not available"
            result["response_data"] = response.json() if response.status_code != 500 else {"error": str(response.text)}
            result["errors"].append(f"Unexpected status code: {response.status_code}")
        
        return result
        
    except requests.exceptions.Timeout:
        return {
            **query,
            "sql_query": "Not available",
            "response_time": 30.0,
            "status_code": 408,
            "errors": ["Request timed out"]
        }
    except Exception as e:
        return {
            **query,
            "sql_query": "Not available",
            "response_time": time.time() - start_time,
            "status_code": 500,
            "errors": [f"Test error: {str(e)}"]
        }

def generate_html_report(results: List[Dict[str, Any]], filename: str):
    """Generate an HTML report from test results"""
    html = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .test { margin: 20px 0; padding: 10px; border: 1px solid #ddd; }
            .passed { border-left: 5px solid #4CAF50; }
            .failed { border-left: 5px solid #f44336; }
            .error { color: #f44336; }
            .success { color: #4CAF50; }
            pre { background: #f5f5f5; padding: 10px; overflow-x: auto; }
        </style>
    </head>
    <body>
    <h1>API Test Results</h1>
    """
    
    # Add summary
    total = len(results)
    passed = sum(1 for r in results if not r["errors"])
    success_rate = (passed / total) * 100 if total > 0 else 0
    avg_time = sum(r["response_time"] for r in results) / total if total > 0 else 0
    
    html += f"""
    <div class="summary">
        <h2>Summary</h2>
        <p>Total Tests: {total}<br>
        Passed: {passed}<br>
        Failed: {total - passed}<br>
        Success Rate: {success_rate:.1f}%<br>
        Average Response Time: {avg_time:.2f}s</p>
    </div>
    """
    
    # Add test results
    for result in results:
        status = "passed" if not result["errors"] else "failed"
        html += f"""
        <div class="test {status}">
            <h3>{result["title"]}</h3>
            <p><strong>Category:</strong> {result["category"]}</p>
            <p><strong>Description:</strong> {result["description"]}</p>
            <p><strong>Query:</strong> {result["natural_language_query"]}</p>
            <p><strong>SQL:</strong></p>
            <pre>{result["sql_query"]}</pre>
            <p><strong>Response Time:</strong> {result["response_time"]:.2f}s</p>
            <p><strong>Status Code:</strong> {result["status_code"]}</p>
        """
        
        if result["errors"]:
            html += "<p><strong>Errors:</strong></p><ul>"
            for error in result["errors"]:
                html += f"<li class='error'>{error}</li>"
            html += "</ul>"
        
        html += "</div>"
    
    html += "</body></html>"
    
    with open(filename, "w") as f:
        f.write(html)

def test_api_comprehensive():
    """Run comprehensive API tests"""
    test_cases = [
        # Budget Queries
        {
            "category": "Budget Queries",
            "title": "Total Infrastructure Budget",
            "description": "Get total budget for infrastructure projects",
            "natural_language_query": "What is the total budget for infrastructure projects?",
            "expected_content": ["MWK"],
            "expected_sql_components": ["SUM(budget)", "infrastructure"]
        },
        {
            "category": "Budget Queries",
            "title": "Average Project Budget",
            "description": "Calculate average budget across all projects",
            "natural_language_query": "What is the average budget for all projects?",
            "expected_content": ["MWK"],
            "expected_sql_components": ["AVG(budget)"]
        },
        
        # Location Queries
        {
            "category": "Location Queries",
            "title": "Zomba Projects",
            "description": "List all projects in Zomba district",
            "natural_language_query": "Show me all projects in Zomba district",
            "expected_content": ["Zomba", "MWK"],
            "expected_sql_components": ["district", "zomba"]
        },
        {
            "category": "Location Queries",
            "title": "Lilongwe Projects Count",
            "description": "Count projects in Lilongwe",
            "natural_language_query": "How many projects are there in Lilongwe?",
            "expected_content": ["count"],
            "expected_sql_components": ["COUNT(*)", "lilongwe"]
        },
        
        # Status Queries
        {
            "category": "Status Queries",
            "title": "Completed Projects",
            "description": "List all completed projects",
            "natural_language_query": "List all completed projects",
            "expected_content": ["completed"],
            "expected_sql_components": ["projectstatus", "completed"]
        },
        {
            "category": "Status Queries",
            "title": "Active Projects Count",
            "description": "Count number of active projects",
            "natural_language_query": "How many active projects are there?",
            "expected_content": ["count"],
            "expected_sql_components": ["COUNT(*)", "active"]
        },
        
        # Sector Queries
        {
            "category": "Sector Queries",
            "title": "Education Projects",
            "description": "List all education sector projects",
            "natural_language_query": "Show all education sector projects",
            "expected_content": ["education"],
            "expected_sql_components": ["projectsector", "education"]
        },
        {
            "category": "Sector Queries",
            "title": "Water Projects Budget",
            "description": "Calculate total budget for water sector",
            "natural_language_query": "What is the total budget for water projects?",
            "expected_content": ["Water", "MWK"],
            "expected_sql_components": ["projectsector", "water"]
        },
        
        # Completion Queries
        {
            "category": "Completion Queries",
            "title": "High Completion Projects",
            "description": "List projects with high completion percentage",
            "natural_language_query": "Show projects with completion percentage above 75%",
            "expected_content": ["%"],
            "expected_sql_components": ["completionpercentage", "75"]
        },
        {
            "category": "Completion Queries",
            "title": "Low Completion Projects",
            "description": "List projects with low completion percentage",
            "natural_language_query": "List projects with less than 25% completion",
            "expected_content": ["%"],
            "expected_sql_components": ["completionpercentage", "25"]
        }
    ]
    
    # Run all tests
    results = []
    for test_case in test_cases:
        # Print test header
        logger.info(f"\n{'='*80}")
        logger.info(f"Testing Category: {test_case['category']}")
        logger.info(f"{'='*80}")
        logger.info(f"Testing: {test_case['title']}")
        logger.info(f"{'='*80}")
        
        # Run test
        result = run_test(test_case)
        
        # Log results
        logger.info("Natural Language Query:")
        logger.info("-" * 50)
        logger.info(test_case["natural_language_query"])
        logger.info("\n")
        
        if result["sql_query"] != "Not available":
            logger.info("Generated SQL Query:")
            logger.info("-" * 50)
            logger.info(result["sql_query"])
            logger.info("\n")
        
        if result.get("response_data"):
            logger.info("Raw Response Data:")
            logger.info("-" * 50)
            logger.info(json.dumps(result["response_data"], indent=2))
            logger.info("\n")
        elif result.get("errors"):
            logger.info("Error Response:")
            logger.info("-" * 50)
            logger.info(json.dumps({"detail": result["errors"][0]}, indent=2))
            logger.info("\n")
        
        # Log test result
        logger.info("Test Result:")
        status = "✓ PASSED" if not result["errors"] else "✗ FAILED"
        logger.info(f"{status} (Response Time: {result['response_time']:.2f}s)\n")
        
        if result["errors"]:
            logger.info("Errors:")
            for error in result["errors"]:
                logger.info(f"  - {error}")
            logger.info("\n")
        
        results.append(result)
    
    # Save results
    with open(RESULTS_FILE, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results
        }, f, indent=2)
    
    # Generate HTML report
    generate_html_report(results, HTML_REPORT_FILE)
    
    # Print summary
    total = len(results)
    passed = sum(1 for r in results if not r["errors"])
    success_rate = (passed / total) * 100 if total > 0 else 0
    avg_time = sum(r["response_time"] for r in results) / total if total > 0 else 0
    
    logger.info(f"\n{'='*80}")
    logger.info("Test Summary")
    logger.info(f"{'='*80}")
    logger.info(f"Total Tests: {total}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {total - passed}")
    logger.info(f"Success Rate: {success_rate:.1f}%")
    logger.info(f"Average Response Time: {avg_time:.2f}s")
    
    logger.info(f"\nTest results saved to {RESULTS_FILE}")
    logger.info(f"\nHTML report saved to {HTML_REPORT_FILE}")

def main():
    try:
        # First check if API is running
        try:
            health_check = requests.get("http://localhost:5000/health")
            if health_check.status_code != 200:
                logger.error("API health check failed. Please ensure the API is running.")
                return
        except requests.exceptions.ConnectionError:
            logger.error("Could not connect to API. Please ensure the API is running on http://localhost:5000")
            return

        # Run tests
        test_api_comprehensive()
        
    except Exception as e:
        logger.error(f"Test script failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 