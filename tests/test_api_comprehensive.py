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

class APITester:
    def __init__(self):
        self.test_cases = [
            # Budget Queries
            {
                "category": "Budget Queries",
                "tests": [
                    {
                        "title": "Total Infrastructure Budget",
                        "query": "What is the total budget for infrastructure projects?",
                        "expected_contains": ["total_budget", "infrastructure", "MWK"],
                        "sql_contains": ["SUM(budget)", "projectsector", "infrastructure"]
                    },
                    {
                        "title": "Average Project Budget",
                        "query": "What is the average budget for all projects?",
                        "expected_contains": ["AVG(budget)", "MWK"],
                        "sql_contains": ["AVG(budget)", "proj_dashboard"]
                    }
                ]
            },
            # Location Queries
            {
                "category": "Location Queries",
                "tests": [
                    {
                        "title": "Zomba Projects",
                        "query": "Show me all projects in Zomba district",
                        "expected_contains": ["Zomba", "projectname", "budget"],
                        "sql_contains": ["district", "zomba"]
                    },
                    {
                        "title": "Lilongwe Projects Count",
                        "query": "How many projects are there in Lilongwe?",
                        "expected_contains": ["COUNT", "Lilongwe"],
                        "sql_contains": ["COUNT", "district", "lilongwe"]
                    }
                ]
            },
            # Status Queries
            {
                "category": "Status Queries",
                "tests": [
                    {
                        "title": "Completed Projects",
                        "query": "List all completed projects",
                        "expected_contains": ["Completed", "projectname"],
                        "sql_contains": ["projectstatus", "completed"]
                    },
                    {
                        "title": "Active Projects Count",
                        "query": "How many active projects are there?",
                        "expected_contains": ["Active", "COUNT"],
                        "sql_contains": ["COUNT", "projectstatus", "active"]
                    }
                ]
            },
            # Sector Queries
            {
                "category": "Sector Queries",
                "tests": [
                    {
                        "title": "Education Projects",
                        "query": "Show all education sector projects",
                        "expected_contains": ["Education", "projectname"],
                        "sql_contains": ["projectsector", "education"]
                    },
                    {
                        "title": "Water Projects Budget",
                        "query": "What is the total budget for water projects?",
                        "expected_contains": ["Water", "total_budget"],
                        "sql_contains": ["SUM(budget)", "projectsector", "water"]
                    }
                ]
            },
            # Completion Percentage Queries
            {
                "category": "Completion Queries",
                "tests": [
                    {
                        "title": "High Completion Projects",
                        "query": "Show projects with completion percentage above 75%",
                        "expected_contains": ["completionpercentage", "75"],
                        "sql_contains": ["completionpercentage", ">", "75"]
                    },
                    {
                        "title": "Low Completion Projects",
                        "query": "List projects with less than 25% completion",
                        "expected_contains": ["completionpercentage", "25"],
                        "sql_contains": ["completionpercentage", "<", "25"]
                    }
                ]
            }
        ]
        self.results = []

    def format_response_data(self, response_data: Dict) -> str:
        """Format the response data for display"""
        try:
            results = response_data.get("response", {}).get("results", [])
            if not results:
                return "No results found"

            output = []
            for result in results:
                if "total_budget" in result:
                    # Handle total/average budget responses
                    amount = result["total_budget"].get("amount", 0)
                    formatted = result["total_budget"].get("formatted", format_currency(amount))
                    output.append(f"Total: {formatted}")
                else:
                    # Handle project listing responses
                    project_details = [
                        f"Project: {result.get('project_name', 'N/A')}",
                        f"District: {result.get('district', 'N/A')}",
                        f"Sector: {result.get('project_sector', 'N/A')}",
                        f"Status: {result.get('project_status', 'N/A')}",
                        f"Budget: {result.get('total_budget', {}).get('formatted', 'N/A')}",
                        f"Completion: {result.get('completion_percentage', 'N/A')}%"
                    ]
                    output.append("\n".join(project_details))

            return "\n\n".join(output)
        except Exception as e:
            return f"Error formatting response: {str(e)}"

    def run_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case with detailed output"""
        print_separator()
        logger.info(f"Testing: {test_case['title']}")
        print_separator()
        
        # Print natural language query
        print_section("Natural Language Query", test_case["query"])
        
        start_time = time.time()
        result = {
            "category": test_case.get("category", "Uncategorized"),
            "title": test_case["title"],
            "query": test_case["query"],
            "timestamp": datetime.now().isoformat(),
            "passed": False,
            "errors": []
        }

        try:
            # Make request to API
            response = requests.post(
                API_URL,
                json={"message": test_case["query"]},
                timeout=30
            )
            
            # Record response time
            result["response_time"] = time.time() - start_time
            result["status_code"] = response.status_code
            
            if response.status_code == 200:
                response_data = response.json()
                result["response"] = response_data
                
                # Extract and print SQL query
                sql_query = response_data.get("response", {}).get("metadata", {}).get("sql_query", "")
                if sql_query:
                    print_section("Generated SQL Query", format_sql(sql_query))
                
                # Print raw response data
                print_section("Raw Response Data")
                formatted_response = self.format_response_data(response_data)
                logger.info(formatted_response)
                
                # Validate expected content
                if "expected_contains" in test_case:
                    response_str = json.dumps(response_data).lower()
                    for expected in test_case["expected_contains"]:
                        if expected.lower() not in response_str:
                            result["errors"].append(f"Missing expected content: {expected}")
                
                # Validate SQL components
                if "sql_contains" in test_case:
                    sql_str = sql_query.lower()
                    for expected in test_case["sql_contains"]:
                        if expected.lower() not in sql_str:
                            result["errors"].append(f"Missing SQL component: {expected}")
                
                # Set passed status
                result["passed"] = len(result["errors"]) == 0
                
            else:
                result["errors"].append(f"Unexpected status code: {response.status_code}")
                if response.text:
                    result["error_detail"] = response.text
                    print_section("Error Response", response.text)
                    
        except requests.exceptions.Timeout:
            result["errors"].append("Request timed out")
            result["error_detail"] = "Request took too long to complete"
            result["response_time"] = 30.0  # Timeout duration
            print_section("Error", "Request timed out after 30 seconds")
        except Exception as e:
            result["errors"].append(f"Test error: {str(e)}")
            result["error_detail"] = str(e)
            result["response_time"] = time.time() - start_time
            print_section("Error", str(e))
        
        # Print test result
        status = "✓ PASSED" if result.get("passed", False) else "✗ FAILED"
        print_section("Test Result", f"{status} (Response Time: {result.get('response_time', 0):.2f}s)")
        if result.get("errors"):
            logger.info("Errors:")
            for error in result["errors"]:
                logger.info(f"  - {error}")
        
        return result

    def run_all_tests(self):
        """Run all test cases"""
        logger.info("Starting comprehensive API tests...")
        
        for category in self.test_cases:
            logger.info(f"\nTesting Category: {category['category']}")
            print_separator()
            
            for test in category["tests"]:
                test["category"] = category["category"]
                result = self.run_test(test)
                self.results.append(result)
                
        self.save_results()
        self.generate_report()
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        passed = sum(1 for r in self.results if r.get("passed", False))
        total = len(self.results)
        avg_time = sum(r.get("response_time", 0) for r in self.results) / total if total > 0 else 0
        
        print_separator()
        logger.info("Test Summary")
        print_separator()
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {total - passed}")
        logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
        logger.info(f"Average Response Time: {avg_time:.2f}s")

    def save_results(self):
        """Save test results to JSON file"""
        output = {
            "test_run_time": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "passed_tests": sum(1 for r in self.results if r.get("passed", False)),
            "failed_tests": sum(1 for r in self.results if not r.get("passed", False)),
            "results": self.results
        }
        
        with open(RESULTS_FILE, "w") as f:
            json.dump(output, f, indent=2)
        logger.info(f"\nTest results saved to {RESULTS_FILE}")

    def generate_report(self):
        """Generate HTML report of test results"""
        try:
            # Calculate statistics
            total_tests = len(self.results)
            passed_tests = sum(1 for r in self.results if r.get("passed", False))
            failed_tests = total_tests - passed_tests
            success_rate = (passed_tests/total_tests)*100 if total_tests > 0 else 0
            avg_time = sum(r.get("response_time", 0) for r in self.results) / total_tests if total_tests > 0 else 0

            # Create HTML content
            html = f"""
            <html>
            <head>
                <title>API Test Results</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .passed {{ color: green; }}
                    .failed {{ color: red; }}
                    .summary {{ background-color: #f0f0f0; padding: 10px; margin: 10px 0; }}
                    .test-case {{ border: 1px solid #ddd; padding: 10px; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <h1>API Test Results</h1>
                <div class="summary">
                    <h2>Summary</h2>
                    <p>Total Tests: {total_tests}</p>
                    <p>Passed: {passed_tests}</p>
                    <p>Failed: {failed_tests}</p>
                    <p>Success Rate: {success_rate:.1f}%</p>
                    <p>Average Response Time: {avg_time:.2f}s</p>
                </div>
            """

            # Add test results
            for result in self.results:
                status = "PASSED" if result.get("passed", False) else "FAILED"
                status_class = "passed" if result.get("passed", False) else "failed"
                
                html += f"""
                <div class="test-case">
                    <h3>{result.get("category", "Uncategorized")} - {result.get("title", "Untitled")}</h3>
                    <p class="{status_class}">Status: {status}</p>
                    <p>Response Time: {result.get("response_time", 0):.2f}s</p>
                    <p>Query: {result.get("query", "N/A")}</p>
                """
                
                if result.get("errors"):
                    html += "<p>Errors:</p><ul>"
                    for error in result["errors"]:
                        html += f"<li>{error}</li>"
                    html += "</ul>"
                
                html += "</div>"

            html += """
            </body>
            </html>
            """

            # Write report with UTF-8 encoding
            with open(HTML_REPORT_FILE, "w", encoding="utf-8") as f:
                f.write(html)
            logger.info(f"\nHTML report saved to {HTML_REPORT_FILE}")
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            logger.error(traceback.format_exc())

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
        tester = APITester()
        tester.run_all_tests()
        
    except Exception as e:
        logger.error(f"Test script failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 