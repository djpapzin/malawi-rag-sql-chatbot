import requests
import json
import logging
from datetime import datetime
import time
from typing import Dict, Any, List
import os
from tabulate import tabulate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
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
    keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN']
    for keyword in keywords:
        sql = sql.replace(keyword, f'\n{keyword}')
    return sql

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

    def run_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case"""
        logger.info(f"\nTesting: {test_case['title']}")
        logger.info("=" * 80)
        
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
                
                # Extract SQL query
                sql_query = response_data.get("response", {}).get("metadata", {}).get("sql_query", "")
                result["sql_query"] = sql_query
                
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
                    
        except requests.exceptions.Timeout:
            result["errors"].append("Request timed out")
            result["error_detail"] = "Request took too long to complete"
        except Exception as e:
            result["errors"].append(f"Test error: {str(e)}")
            result["error_detail"] = str(e)
        
        return result

    def run_all_tests(self):
        """Run all test cases"""
        logger.info("Starting comprehensive API tests...")
        
        for category in self.test_cases:
            logger.info(f"\nTesting Category: {category['category']}")
            logger.info("=" * 80)
            
            for test in category["tests"]:
                test["category"] = category["category"]
                result = self.run_test(test)
                self.results.append(result)
                
                # Log result
                status = "✓ PASSED" if result["passed"] else "✗ FAILED"
                logger.info(f"{status} - {test['title']}")
                if not result["passed"]:
                    for error in result["errors"]:
                        logger.info(f"  Error: {error}")
                logger.info(f"  Response Time: {result['response_time']:.2f}s")
                
        self.save_results()
        self.generate_report()

    def save_results(self):
        """Save test results to JSON file"""
        output = {
            "test_run_time": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "passed_tests": sum(1 for r in self.results if r["passed"]),
            "failed_tests": sum(1 for r in self.results if not r["passed"]),
            "results": self.results
        }
        
        with open(RESULTS_FILE, "w") as f:
            json.dump(output, f, indent=2)
        logger.info(f"\nTest results saved to {RESULTS_FILE}")

    def generate_report(self):
        """Generate HTML report"""
        # Calculate statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["passed"])
        failed_tests = total_tests - passed_tests
        avg_response_time = sum(r["response_time"] for r in self.results) / total_tests

        # Create HTML report
        html = f"""
        <html>
        <head>
            <title>API Test Results</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f5f5f5; padding: 20px; margin-bottom: 20px; }}
                .passed {{ color: green; }}
                .failed {{ color: red; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f5f5f5; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .error-detail {{ color: red; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <h1>API Test Results</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p>Test Run Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Total Tests: {total_tests}</p>
                <p class="passed">Passed Tests: {passed_tests}</p>
                <p class="failed">Failed Tests: {failed_tests}</p>
                <p>Average Response Time: {avg_response_time:.2f}s</p>
            </div>
        """

        # Add results table
        html += """
            <h2>Detailed Results</h2>
            <table>
                <tr>
                    <th>Category</th>
                    <th>Test</th>
                    <th>Query</th>
                    <th>Status</th>
                    <th>Response Time</th>
                    <th>Errors</th>
                </tr>
        """

        for result in self.results:
            status = "✓ PASSED" if result["passed"] else "✗ FAILED"
            status_class = "passed" if result["passed"] else "failed"
            errors = "<br>".join(result["errors"]) if result["errors"] else ""
            
            html += f"""
                <tr>
                    <td>{result['category']}</td>
                    <td>{result['title']}</td>
                    <td>{result['query']}</td>
                    <td class="{status_class}">{status}</td>
                    <td>{result['response_time']:.2f}s</td>
                    <td class="error-detail">{errors}</td>
                </tr>
            """

        html += """
            </table>
        </body>
        </html>
        """

        with open(HTML_REPORT_FILE, "w") as f:
            f.write(html)
        logger.info(f"HTML report generated: {HTML_REPORT_FILE}")

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
        
        # Print summary
        passed = sum(1 for r in tester.results if r["passed"])
        total = len(tester.results)
        logger.info(f"\nTest Summary:")
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {total - passed}")
        logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
        
    except Exception as e:
        logger.error(f"Test script failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 