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
        # Remove comments
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        # Remove newlines and extra spaces
        sql = ' '.join(sql.split())
        return sql.strip().lower()
    
    def compare_sql(self, expected: str, actual: str) -> bool:
        """Compare expected and actual SQL queries"""
        expected_clean = self.clean_sql(expected)
        actual_clean = self.clean_sql(actual)
        
        # For empty queries (like greetings)
        if not expected_clean and not actual_clean:
            return True
            
        return expected_clean == actual_clean
    
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
            sql_matches = self.compare_sql(query_data["expected_sql"], generated_sql)
            
            return {
                "id": query_data["id"],
                "query": query_data["query_text"],
                "expected_type": query_data["expected_type"],
                "actual_type": result.get("query_type", "unknown"),
                "expected_sql": query_data["expected_sql"],
                "generated_sql": generated_sql,
                "sql_matches": sql_matches,
                "response": result,
                "success": response.status_code == 200 and sql_matches,
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
                "sql_matches": False,
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
            "sql_matches": r["sql_matches"],
            "success": r["success"],
            "error": r["error"]
        } for r in results])
        
        # Save summary CSV
        summary_df.to_csv(f"{self.results_dir}/summary_{timestamp}.csv", index=False)
        
        # Log summary
        logger.info(f"\nTest Summary:")
        logger.info(f"Total Tests: {len(results)}")
        logger.info(f"Successful Tests: {sum(1 for r in results if r['success'])}")
        logger.info(f"Failed Tests: {sum(1 for r in results if not r['success'])}")
        logger.info(f"\nResults saved to:")
        logger.info(f"- Detailed: {self.results_dir}/detailed_results_{timestamp}.json")
        logger.info(f"- Summary: {self.results_dir}/summary_{timestamp}.csv")

if __name__ == "__main__":
    # Create runner
    runner = TestQueryRunner()
    
    # Run tests
    runner.run_all_tests() 