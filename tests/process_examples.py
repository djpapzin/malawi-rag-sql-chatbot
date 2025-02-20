import requests
import logging
import json
import sys
import os
import csv
from datetime import datetime
import traceback
from typing import Dict, Any, List
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class QueryAnalyzer:
    def __init__(self):
        self.results = []
        self.db_path = self._find_database()
        self.output_dir = "results"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
    def _find_database(self) -> str:
        """Find the database file by searching common locations"""
        possible_paths = [
            "malawi_projects1.db",
            "../malawi_projects1.db",
            "data/malawi_projects1.db",
            "../data/malawi_projects1.db"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found database at: {path}")
                return path
                
        logger.warning("Database not found, some functionality will be limited")
        return None
        
    def save_results(self):
        """Save results to CSV file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"query_analysis_{timestamp}.csv")
        
        headers = [
            "Query #",
            "Category",
            "Input Query",
            "SQL Query",
            "API Results",
            "DB Matches",
            "Total Projects",
            "Match %",
            "Response Time",
            "Error"
        ]
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                
                for i, result in enumerate(self.results, 1):
                    row = {
                        "Query #": i,
                        "Category": result.get('category', ''),
                        "Input Query": result['input_query'],
                        "SQL Query": result['sql_query'],
                        "API Results": result['api_records'],
                        "DB Matches": result['total_matches'],
                        "Total Projects": result['total_projects'],
                        "Match %": f"{result['match_percentage']:.1f}%",
                        "Response Time": f"{result['response_time']:.2f}s",
                        "Error": result['error'] or ''
                    }
                    writer.writerow(row)
                    
            logger.info(f"Results saved to: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            return None
            
    def get_total_records(self, sql: str) -> int:
        """Get total records that would match this SQL query without LIMIT"""
        if not self.db_path:
            return 0
            
        try:
            # Remove LIMIT clause if present
            sql = sql.split('LIMIT')[0].strip()
            # Add COUNT
            count_sql = f"SELECT COUNT(*) FROM ({sql}) as subq"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(count_sql)
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error counting records: {str(e)}")
            return 0
            
    def get_total_projects(self) -> int:
        """Get total number of projects in database"""
        if not self.db_path:
            return 0
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM proj_dashboard WHERE ISLATEST = 1")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error counting total projects: {str(e)}")
            return 0
            
    def analyze_query(self, query: str, category: str = '') -> Dict[str, Any]:
        """Analyze a single query and return results"""
        logger.info(f"\nAnalyzing query: {query}")
        
        try:
            # Make API request
            start_time = datetime.now()
            response = requests.post(
                "http://localhost:8000/query",
                json={"query": query}
            )
            query_time = datetime.now() - start_time
            
            if response.status_code != 200:
                result = {
                    "input_query": query,
                    "category": category,
                    "sql_query": "ERROR",
                    "response_time": query_time.total_seconds(),
                    "api_records": 0,
                    "total_matches": 0,
                    "total_projects": 0,
                    "match_percentage": 0,
                    "error": f"API Error: {response.status_code}"
                }
                self.results.append(result)
                return result
                
            data = response.json()
            
            # Extract SQL query
            sql_query = ""
            if "source" in data and isinstance(data["source"], list):
                for source in data["source"]:
                    if "sql" in source:
                        sql_query = source["sql"]
                        break
            elif "source" in data and isinstance(data["source"], dict) and "sql" in data["source"]:
                sql_query = data["source"]["sql"]
                
            # Get record counts
            total_matches = 0
            total_projects = 0
            api_records = 0
            
            try:
                if sql_query:
                    total_matches = self.get_total_records(sql_query)
                total_projects = self.get_total_projects()
                api_records = data.get("metadata", {}).get("total_results", 0)
            except Exception as e:
                logger.warning(f"Error getting record counts: {str(e)}")
            
            result = {
                "input_query": query,
                "category": category,
                "sql_query": sql_query or "No SQL Generated",
                "response_time": query_time.total_seconds(),
                "api_records": api_records,
                "total_matches": total_matches,
                "total_projects": total_projects,
                "match_percentage": round((total_matches / total_projects * 100), 2) if total_projects > 0 else 0,
                "error": None
            }
            
            self.results.append(result)
            return result
        except Exception as e:
            logger.error(f"Error analyzing query: {str(e)}")
            result = {
                "input_query": query,
                "category": category,
                "sql_query": "ERROR",
                "response_time": 0,
                "api_records": 0,
                "total_matches": 0,
                "total_projects": 0,
                "match_percentage": 0,
                "error": str(e)
            }
            self.results.append(result)
            return result
            
    def print_results_table(self):
        """Print results in a formatted table"""
        if not self.results:
            logger.info("No results to display")
            return
            
        # Print header
        print("\nQuery Analysis Results")
        print("="*150)
        
        # Column headers
        headers = [
            "Query #",
            "Category",
            "Input Query",
            "SQL Query",
            "API Results",
            "DB Matches",
            "Total Projects",
            "Match %",
            "Response Time",
            "Error"
        ]
        
        # Calculate column widths
        widths = [8, 20, 40, 50, 12, 12, 15, 8, 15, 30]
        
        # Print headers
        header_format = "".join(f"{{:<{w}}}" for w in widths)
        print(header_format.format(*headers))
        print("-" * sum(widths))
        
        # Print rows
        row_format = "".join(f"{{:<{w}}}" for w in widths)
        for i, result in enumerate(self.results, 1):
            # Truncate long strings
            input_query = result['input_query'][:37] + "..." if len(result['input_query']) > 40 else result['input_query']
            sql_query = result['sql_query'][:47] + "..." if len(result['sql_query']) > 50 else result['sql_query']
            category = result['category'][:17] + "..." if len(result['category']) > 20 else result['category']
            
            row = [
                str(i),
                category,
                input_query,
                sql_query,
                str(result['api_records']),
                str(result['total_matches']),
                str(result['total_projects']),
                f"{result['match_percentage']:.1f}%",
                f"{result['response_time']:.2f}s",
                str(result['error'])[:27] + "..." if result['error'] and len(str(result['error'])) > 30 else str(result['error'])
            ]
            print(row_format.format(*row))
            
        # Print summary
        print("\nSummary Statistics")
        print("-"*50)
        print(f"Total Queries Run: {len(self.results)}")
        avg_time = sum(r['response_time'] for r in self.results) / len(self.results)
        print(f"Average Response Time: {avg_time:.2f}s")
        errors = sum(1 for r in self.results if r['error'])
        print(f"Queries with Errors: {errors}")
        
def run_comprehensive_tests():
    """Run a comprehensive set of test queries"""
    analyzer = QueryAnalyzer()
    
    # Project Code Test Cases
    project_code_tests = [
        "Show me project MW-CR-DO",
        "What is the status of project MW-CR-DO?",
        "Tell me about projects in MW-CR",
        "Show all CR-DO projects",
        "List projects with code CR",
    ]
    
    # General Query Test Cases with Result Limiting
    general_query_tests = [
        "Show all education projects in Zomba",
        "List the top health projects",
        "What are the biggest projects in Central Region?",
        "Show me ongoing road construction projects",
        "List completed school projects",
    ]
    
    # Specific Project Tests
    specific_project_tests = [
        "Tell me about 'Nachuma Market Shed phase 3'",
        "What is the status of 'Chilingani School Block Construction'?",
        "Show details for 'Boma Stadium Phase 3'",
        "Give me information about project MW-CR-DO",
    ]
    
    # Run all tests
    all_tests = {
        "Project Code Queries": project_code_tests,
        "General Queries": general_query_tests,
        "Specific Project Queries": specific_project_tests
    }
    
    for category, tests in all_tests.items():
        logger.info(f"\nRunning {category}...")
        for test in tests:
            try:
                analyzer.analyze_query(test, category)
            except Exception as e:
                logger.error(f"Error processing query '{test}': {str(e)}")
                traceback.print_exc()
    
    # Print final results table
    analyzer.print_results_table()
    
    # Save results
    results_file = analyzer.save_results()
    if results_file:
        print(f"\nResults have been saved to: {results_file}")

if __name__ == "__main__":
    try:
        run_comprehensive_tests()
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)
