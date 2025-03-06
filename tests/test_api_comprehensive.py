#!/usr/bin/env python3
import requests
import json
import time
import datetime
import os
import logging
import argparse
from tabulate import tabulate
from typing import Dict, Any, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration with defaults
DEFAULT_API_URL = "http://154.0.164.254:5000/api/chat"  # Updated URL
DEFAULT_HEADERS = {"Content-Type": "application/json"}
RESULTS_DIR = "test_results"

class APITester:
    """Comprehensive API testing utility for the Malawi RAG SQL Chatbot"""
    
    def __init__(self, api_url: str = DEFAULT_API_URL, headers: Dict = None):
        self.api_url = api_url
        self.headers = headers or DEFAULT_HEADERS
        self.results = []
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure results directory exists
        if not os.path.exists(RESULTS_DIR):
            os.makedirs(RESULTS_DIR)
            
    def format_sql(self, sql: str) -> str:
        """Format SQL query for better readability"""
        if not sql:
            return "No SQL generated"
            
        # Basic SQL formatting
        sql = sql.replace("SELECT", "\nSELECT")
        sql = sql.replace("FROM", "\nFROM")
        sql = sql.replace("WHERE", "\nWHERE")
        sql = sql.replace("GROUP BY", "\nGROUP BY")
        sql = sql.replace("ORDER BY", "\nORDER BY")
        sql = sql.replace("HAVING", "\nHAVING")
        sql = sql.replace("LIMIT", "\nLIMIT")
        sql = sql.replace("JOIN", "\nJOIN")
        return sql
        
    def execute_query(self, name: str, message: str, verbose: bool = True) -> Dict[str, Any]:
        """Execute a query and return the response"""
        if verbose:
            logger.info(f"\n{'=' * 80}")
            logger.info(f"Testing: {name}")
            logger.info(f"Query: {message}")
            logger.info(f"{'-' * 80}")
        
        start_time = time.time()
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"message": message},
                timeout=30
            )
            elapsed = time.time() - start_time
            
            status_code = response.status_code
            if verbose:
                logger.info(f"Status Code: {status_code} (in {elapsed:.2f}s)")
            
            result = {
                "query_name": name,
                "query": message,
                "status_code": status_code,
                "response_time": elapsed,
                "timestamp": datetime.datetime.now().isoformat(),
                "raw_response": None,
                "error": None
            }
            
            if status_code == 200:
                try:
                    # Parse the JSON response
                    data = response.json()
                    result["raw_response"] = data
                    
                    # Extract and add specific elements
                    if "results" in data:
                        # New response format
                        result["text_response"] = data["results"][0]["message"] if data["results"] else ""
                        if "metadata" in data:
                            result["sql_query"] = data["metadata"].get("sql_query", "")
                            result["query_time"] = data["metadata"].get("query_time", "")
                            result["total_results"] = data["metadata"].get("total_results", 0)
                    
                    # Handle old format too                    
                    elif "response" in data and "results" in data["response"]:
                        if len(data["response"]["results"]) > 0:
                            result["text_response"] = data["response"]["results"][0].get("message", "")
                        if "metadata" in data["response"]:
                            result["sql_query"] = data["response"]["metadata"].get("sql_query", "")
                            result["query_time"] = data["response"]["metadata"].get("query_time", "")
                            result["total_results"] = data["response"]["metadata"].get("total_results", 0)
                    
                    if verbose:
                        # Display text response
                        logger.info(f"\nResponse: {result.get('text_response', 'No text response')}")
                        
                        # Display SQL query if available
                        sql = result.get("sql_query", "")
                        if sql:
                            logger.info(f"\nSQL Query: {self.format_sql(sql)}")
                            
                        # Display stats if available
                        if "query_time" in result and "total_results" in result:
                            logger.info(f"\nStats: {result.get('total_results', 0)} results in {result.get('query_time', '')}")
                                
                except json.JSONDecodeError as e:
                    result["error"] = f"JSON Decode Error: {str(e)}"
                    result["raw_response"] = response.text
                    if verbose:
                        logger.error(f"Response (not JSON): {response.text}")
            else:
                result["error"] = f"HTTP Error: {status_code}"
                result["raw_response"] = response.text
                if verbose:
                    logger.error(f"Error Response: {response.text}")
                
        except requests.RequestException as e:
            elapsed = time.time() - start_time
            result = {
                "query_name": name,
                "query": message,
                "status_code": None,
                "response_time": elapsed,
                "timestamp": datetime.datetime.now().isoformat(),
                "error": f"Request Error: {str(e)}"
            }
            if verbose:
                logger.error(f"Error: {str(e)}")
                
        if verbose:
            logger.info(f"{'=' * 80}")
            
        self.results.append(result)
        return result
        
    def export_results(self, format_type: str = "all") -> None:
        """
        Export test results to file(s)
        format_type: 'json', 'markdown', 'html', or 'all'
        """
        # Generate filenames with timestamp
        base_filename = f"api_test_results_{self.timestamp}"
        
        if format_type in ["json", "all"]:
            # Export as JSON
            json_file = os.path.join(RESULTS_DIR, f"{base_filename}.json")
            with open(json_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"Results saved to JSON: {json_file}")
                
        if format_type in ["markdown", "all"]:
            # Export as Markdown
            md_file = os.path.join(RESULTS_DIR, f"{base_filename}.md")
            with open(md_file, 'w') as f:
                f.write(f"# API Test Results\n\n")
                f.write(f"_Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n\n")
                f.write(f"**API URL:** {self.api_url}\n\n")
                
                # Summary table
                f.write("## Summary\n\n")
                summary_table = [
                    ["Query", "Status", "Time (s)", "Results"]
                ]
                
                for result in self.results:
                    status = "✅ Pass" if result["status_code"] == 200 and not result.get("error") else "❌ Fail"
                    time_s = f"{result['response_time']:.2f}s"
                    results_count = result.get("total_results", "N/A")
                    summary_table.append([
                        result["query_name"],
                        status,
                        time_s,
                        results_count
                    ])
                
                f.write(tabulate(summary_table, headers="firstrow", tablefmt="pipe"))
                f.write("\n\n")
                
                # Detailed results
                f.write("## Detailed Results\n\n")
                for i, result in enumerate(self.results):
                    f.write(f"### {i+1}. {result['query_name']}\n\n")
                    f.write(f"**Query:** {result['query']}\n\n")
                    f.write(f"**Status:** {result['status_code']} ({result['response_time']:.2f}s)\n\n")
                    
                    if result.get("error"):
                        f.write(f"**Error:** {result['error']}\n\n")
                    
                    if result.get("text_response"):
                        f.write(f"**Response:**\n\n```\n{result['text_response']}\n```\n\n")
                    
                    if result.get("sql_query"):
                        f.write(f"**SQL Query:**\n\n```sql\n{self.format_sql(result['sql_query'])}\n```\n\n")
                    
                    if result.get("query_time") and result.get("total_results") is not None:
                        f.write(f"**Stats:** {result['total_results']} results in {result['query_time']}\n\n")
                    
                    f.write("---\n\n")
            
            logger.info(f"Results saved to Markdown: {md_file}")
                
        if format_type in ["html", "all"]:
            # Export as HTML
            html_file = os.path.join(RESULTS_DIR, f"{base_filename}.html")
            with open(html_file, 'w') as f:
                f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Test Results</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1, h2, h3 { color: #444; }
        .test-item { background: #f9f9f9; border-radius: 5px; padding: 15px; margin-bottom: 20px; }
        .test-item.pass { border-left: 5px solid #4CAF50; }
        .test-item.fail { border-left: 5px solid #F44336; }
        .sql { background: #002b36; color: #93a1a1; padding: 15px; border-radius: 5px; overflow-x: auto; }
        .response { background: #f5f5f5; padding: 15px; border-radius: 5px; white-space: pre-wrap; }
        .stats { display: flex; gap: 20px; margin-top: 15px; }
        .stat-item { background: #e9e9e9; padding: 10px; border-radius: 5px; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { text-align: left; padding: 12px; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .summary-status.pass { color: #4CAF50; }
        .summary-status.fail { color: #F44336; }
    </style>
</head>
<body>
    <h1>API Test Results</h1>
    <p><em>Generated: """)
                f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                f.write("""</em></p>
    <p><strong>API URL:</strong> """)
                f.write(self.api_url)
                f.write("""</p>
                
    <h2>Summary</h2>
    <table>
        <tr>
            <th>Query</th>
            <th>Status</th>
            <th>Time (s)</th>
            <th>Results</th>
        </tr>""")
                
                for result in self.results:
                    status_text = "✅ Pass" if result["status_code"] == 200 and not result.get("error") else "❌ Fail"
                    status_class = "pass" if result["status_code"] == 200 and not result.get("error") else "fail"
                    
                    f.write(f"""
        <tr>
            <td>{result["query_name"]}</td>
            <td class="summary-status {status_class}">{status_text}</td>
            <td>{result["response_time"]:.2f}s</td>
            <td>{result.get("total_results", "N/A")}</td>
        </tr>""")
                
                f.write("""
    </table>
    
    <h2>Detailed Results</h2>""")
                
                for i, result in enumerate(self.results):
                    status_class = "pass" if result["status_code"] == 200 and not result.get("error") else "fail"
                    
                    f.write(f"""
    <div class="test-item {status_class}">
        <h3>{i+1}. {result["query_name"]}</h3>
        <p><strong>Query:</strong> {result["query"]}</p>
        <p><strong>Status:</strong> {result["status_code"]} ({result["response_time"]:.2f}s)</p>""")
                    
                    if result.get("error"):
                        f.write(f"""
        <p><strong>Error:</strong> {result["error"]}</p>""")
                    
                    if result.get("text_response"):
                        f.write(f"""
        <div>
            <h4>Response:</h4>
            <div class="response">{result["text_response"]}</div>
        </div>""")
                    
                    if result.get("sql_query"):
                        f.write(f"""
        <div>
            <h4>SQL Query:</h4>
            <pre class="sql">{self.format_sql(result["sql_query"])}</pre>
        </div>""")
                    
                    if result.get("query_time") and result.get("total_results") is not None:
                        f.write(f"""
        <div class="stats">
            <div class="stat-item">
                <strong>Results:</strong> {result["total_results"]}
            </div>
            <div class="stat-item">
                <strong>Query Time:</strong> {result["query_time"]}
            </div>
        </div>""")
                    
                    f.write("""
    </div>""")
                
                f.write("""
</body>
</html>""")
                
            logger.info(f"Results saved to HTML: {html_file}")
        
        return

def run_comprehensive_tests(api_url=DEFAULT_API_URL, verbose=True):
    """Run a comprehensive set of tests against the API"""
    tester = APITester(api_url=api_url)
    logger.info(f"Starting comprehensive API tests against {api_url}")
    
    # Test queries (categorized)
    
    # 1. Health check and basic functionality
    tester.execute_query("Health Check", "Hello, can you help me?", verbose)
    
    # 2. Basic sector queries
    tester.execute_query("Health Sector Query", "Show me all health sector projects", verbose)
    tester.execute_query("Education Sector Query", "Show me all education sector projects", verbose)
    tester.execute_query("Roads Sector Query", "Show me all road construction projects", verbose)
    
    # 3. Location queries
    tester.execute_query("District Query - Lilongwe", "What projects are in Lilongwe district?", verbose)
    tester.execute_query("District Query - Zomba", "Show me all projects in Zomba district", verbose)
    tester.execute_query("Region Query", "List all projects in Southern Region", verbose)
    
    # 4. Status queries
    tester.execute_query("Completed Projects", "Show me all completed projects", verbose)
    tester.execute_query("Ongoing Projects", "List all ongoing projects", verbose)
    
    # 5. Budget queries
    tester.execute_query("Budget Analysis", "What projects have the highest budget?", verbose)
    tester.execute_query("Total Budget Query", "What is the total budget for all projects?", verbose)
    
    # 6. Combined filters
    tester.execute_query("Combined Sector + District", "Show me education projects in Zomba", verbose)
    tester.execute_query("Combined Sector + Status", "List all completed health projects", verbose)
    
    # 7. Specific project queries
    tester.execute_query("Specific Project Query", "Tell me about the Construction of Maternity Wing project", verbose)
    
    # Export results to all formats
    tester.export_results("all")
    logger.info(f"Completed comprehensive API tests")
    
    return tester.results

def main():
    """Main execution function with command line arguments"""
    parser = argparse.ArgumentParser(description='Comprehensive API Testing for Malawi RAG SQL Chatbot')
    
    parser.add_argument('--url', type=str, default=DEFAULT_API_URL,
                        help=f'API URL (default: {DEFAULT_API_URL})')
    
    parser.add_argument('--query', type=str,
                        help='Run a single query instead of the comprehensive test suite')
    
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress verbose output')
    
    args = parser.parse_args()
    
    if args.query:
        # Run a single query
        tester = APITester(api_url=args.url)
        tester.execute_query("Custom Query", args.query, verbose=not args.quiet)
        tester.export_results("all")
    else:
        # Run comprehensive tests
        run_comprehensive_tests(api_url=args.url, verbose=not args.quiet)

if __name__ == "__main__":
    main()
