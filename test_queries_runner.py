import pandas as pd
import requests
import json
from datetime import datetime
import logging
from typing import Dict, Any, List
import os
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestQueryRunner:
    def __init__(self, api_url: str = "http://154.0.164.254:5000/api/rag-sql-chatbot/chat"):
        self.api_url = api_url
        self.results_dir = "test_results"
        os.makedirs(self.results_dir, exist_ok=True)
        
    def clean_sql(self, sql: str) -> str:
        """Clean SQL query for comparison by removing whitespace and newlines"""
        if not sql:
            return ""
            
        # Handle COUNT/RESULTS format
        if sql.startswith("COUNT:"):
            parts = sql.split("RESULTS:")
            count_sql = self.normalize_sql(parts[0].replace("COUNT:", "").strip())
            results_sql = self.normalize_sql(parts[1].strip()) if len(parts) > 1 else ""
            return f"COUNT: {count_sql} RESULTS: {results_sql}"
            
        # Handle single query format
        return self.normalize_sql(sql)
    
    def normalize_sql(self, sql: str) -> str:
        """Normalize a SQL query by removing formatting variations"""
        # Remove comments
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        
        # Convert to lowercase
        sql = sql.lower()
        
        # Normalize whitespace
        sql = ' '.join(sql.split())
        
        # Normalize column names
        replacements = {
            'projectname': 'project_name',
            'projectcode': 'project_code',
            'projectsector': 'sector',
            'projectstatus': 'status',
            'traditionalauthority': 'traditional_authority',
            'budget': 'budget_amount',
            'totalexpenditureyear': 'total_expenditure',
            'fundingsource': 'funding_source',
            'startdate': 'start_date',
            'completionestidate': 'completion_date',
            'lastvisit': 'last_monitoring_visit',
            'completionpercentage': 'completion_rate',
            'contractorname': 'contractor_name',
            'signingdate': 'signing_date',
            'projectdesc': 'description',
            'fiscalyear': 'fiscal_year'
        }
        
        for old, new in replacements.items():
            sql = sql.replace(old, new)
            
        # Normalize SIMILAR TO vs LIKE
        sql = sql.replace('similar to', 'like')
        
        # Remove ORDER BY clauses as they're not critical for functionality
        sql = re.sub(r'order by.*?(?=limit|$)', '', sql)
        
        # Remove NULLS LAST/FIRST as they're implementation details
        sql = sql.replace('nulls last', '').replace('nulls first', '')
        
        return sql.strip()
    
    def compare_sql(self, expected: str, actual: str) -> Dict[str, Any]:
        """Compare expected and actual SQL queries and return comparison details"""
        expected_clean = self.clean_sql(expected)
        actual_clean = self.clean_sql(actual)
        
        # For empty queries (like greetings)
        if not expected_clean and not actual_clean:
            return {
                "matches": True,
                "expected": expected_clean,
                "actual": actual_clean,
                "differences": None
            }
            
        # For queries with COUNT/RESULTS format
        if expected_clean.startswith("COUNT:"):
            expected_parts = expected_clean.split("RESULTS:")
            actual_parts = actual_clean.split("RESULTS:")
            
            count_matches = self.compare_query_parts(
                expected_parts[0].replace("COUNT:", "").strip(),
                actual_parts[0].replace("COUNT:", "").strip() if len(actual_parts) > 0 else actual_clean
            )
            
            results_matches = True
            if len(expected_parts) > 1 and len(actual_parts) > 1:
                results_matches = self.compare_query_parts(
                    expected_parts[1].strip(),
                    actual_parts[1].strip()
                )
            
            return {
                "matches": count_matches["matches"] and results_matches,
                "expected": expected_clean,
                "actual": actual_clean,
                "differences": {
                    "count": count_matches["differences"],
                    "results": results_matches if isinstance(results_matches, bool) else results_matches["differences"]
                }
            }
            
        # For single queries
        return {
            "matches": expected_clean == actual_clean,
            "expected": expected_clean,
            "actual": actual_clean,
            "differences": None if expected_clean == actual_clean else {
                "expected": expected_clean,
                "actual": actual_clean
            }
        }
    
    def compare_query_parts(self, expected: str, actual: str) -> Dict[str, Any]:
        """Compare individual parts of SQL queries"""
        expected = self.normalize_sql(expected)
        actual = self.normalize_sql(actual)
        
        return {
            "matches": expected == actual,
            "differences": None if expected == actual else {
                "expected": expected,
                "actual": actual
            }
        }
    
    def run_test(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test query"""
        try:
            # Prepare request
            payload = {
                "message": query_data["query_text"]
            }
            
            # Send request
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Extract generated SQL from response
            generated_sql = result.get("metadata", {}).get("sql_query", "")
            
            # Compare with expected SQL
            sql_comparison = self.compare_sql(query_data["expected_sql"], generated_sql)
            
            return {
                "id": query_data["id"],
                "query": query_data["query_text"],
                "expected_type": query_data["expected_type"],
                "actual_type": result.get("query_type", "unknown"),
                "expected_sql": query_data["expected_sql"],
                "generated_sql": generated_sql,
                "sql_comparison": sql_comparison,
                "response": result,
                "success": response.status_code == 200 and sql_comparison["matches"],
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error running test {query_data['id']}: {str(e)}")
            return {
                "id": query_data["id"],
                "query": query_data["query_text"],
                "expected_type": query_data["expected_type"],
                "actual_type": "error",
                "expected_sql": query_data["expected_sql"],
                "generated_sql": None,
                "sql_comparison": {
                    "matches": False,
                    "expected": query_data["expected_sql"],
                    "actual": None,
                    "differences": str(e)
                },
                "response": None,
                "success": False,
                "error": str(e)
            }
    
    def run_all_tests(self) -> None:
        """Run all test queries and save results"""
        # Read test queries
        df = pd.read_csv("test_queries.csv")
        
        # Store results
        results = []
        
        # Run each test
        for _, row in df.iterrows():
            logger.info(f"Running test {row['id']}: {row['query_text']}")
            result = self.run_test(row)
            results.append(result)
            
        # Create timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        detailed_results = {
            "timestamp": timestamp,
            "total_tests": len(results),
            "successful_tests": sum(1 for r in results if r["success"]),
            "failed_tests": sum(1 for r in results if not r["success"]),
            "results": results
        }
        
        with open(f"{self.results_dir}/detailed_results_{timestamp}.json", "w") as f:
            json.dump(detailed_results, f, indent=2)
            
        # Create summary DataFrame
        summary_df = pd.DataFrame([{
            "id": r["id"],
            "query": r["query"],
            "expected_type": r["expected_type"],
            "actual_type": r["actual_type"],
            "sql_matches": r["sql_comparison"]["matches"],
            "success": r["success"],
            "error": r["error"]
        } for r in results])
        
        # Save summary CSV
        summary_df.to_csv(f"{self.results_dir}/summary_{timestamp}.csv", index=False)
        
        # Create detailed SQL comparison report
        sql_report = []
        for r in results:
            if not r["success"] and r["sql_comparison"]["differences"]:
                sql_report.append(f"""
Test {r['id']}: {r['query']}
Expected SQL:
{r['sql_comparison']['expected']}

Actual SQL:
{r['sql_comparison']['actual']}

Differences:
{json.dumps(r['sql_comparison']['differences'], indent=2)}
-------------------
""")
                
        with open(f"{self.results_dir}/sql_differences_{timestamp}.txt", "w") as f:
            f.write("\n".join(sql_report))
        
        # Log summary
        logger.info(f"\nTest Summary:")
        logger.info(f"Total Tests: {len(results)}")
        logger.info(f"Successful Tests: {sum(1 for r in results if r['success'])}")
        logger.info(f"Failed Tests: {sum(1 for r in results if not r['success'])}")
        logger.info(f"\nResults saved to:")
        logger.info(f"- Detailed: {self.results_dir}/detailed_results_{timestamp}.json")
        logger.info(f"- Summary: {self.results_dir}/summary_{timestamp}.csv")
        logger.info(f"- SQL Differences: {self.results_dir}/sql_differences_{timestamp}.txt")

if __name__ == "__main__":
    # Create runner
    runner = TestQueryRunner()
    
    # Run tests
    runner.run_all_tests() 