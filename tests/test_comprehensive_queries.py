import requests
import json
from typing import Dict, Any, List
import sqlite3
import pandas as pd
from tabulate import tabulate
import logging
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QueryTester:
    """Comprehensive query testing framework"""
    
    def __init__(self, api_url: str = "http://localhost:8001"):
        self.api_url = api_url
        self.db_conn = sqlite3.connect('malawi_projects1.db')
        self.results = []
        
    def _verify_record_exists(self, query_type: str, value: str) -> int:
        """Verify if record exists in database and return expected count"""
        try:
            if query_type == "project_code":
                sql = f"""
                    SELECT COUNT(*) as count 
                    FROM proj_dashboard 
                    WHERE ISLATEST = 1 
                    AND UPPER(PROJECTCODE) = '{value.upper()}'
                """
            elif query_type == "project_name":
                sql = f"""
                    SELECT COUNT(*) as count 
                    FROM proj_dashboard 
                    WHERE ISLATEST = 1 
                    AND LOWER(PROJECTNAME) = LOWER('{value}')
                """
            else:
                return None
                
            df = pd.read_sql_query(sql, self.db_conn)
            return df.iloc[0]['count'] if not df.empty else 0
        except Exception as e:
            logger.error(f"Error verifying record: {str(e)}")
            return None
            
    def _execute_api_query(self, query: str) -> Dict[str, Any]:
        """Execute query through API"""
        try:
            response = requests.post(
                f"{self.api_url}/query",
                json={"message": query, "language": "english"}
            )
            return response.json()
        except Exception as e:
            logger.error(f"API query failed: {str(e)}")
            return None
            
    def _execute_db_query(self, sql: str) -> pd.DataFrame:
        """Execute query directly on database"""
        try:
            return pd.read_sql_query(sql, self.db_conn)
        except Exception as e:
            logger.error(f"Database query failed: {str(e)}")
            return pd.DataFrame()
            
    def test_query(self, query: str, description: str, expected_count: int = None) -> Dict[str, Any]:
        """Test a specific query and record results"""
        logger.info(f"\nTesting: {description}")
        logger.info(f"Query: {query}")
        
        # Verify record existence for specific project queries
        if "MW-" in query:  # Project code query
            code = re.search(r'MW-[A-Z]{2}-[A-Z0-9]{2}', query)
            if code:
                expected_count = self._verify_record_exists("project_code", code.group())
        elif "'" in query:  # Project name query
            name = re.search(r"'([^']+)'", query)
            if name:
                project_name = name.group(1).strip()
                expected_count = self._verify_record_exists("project_name", project_name)
        
        # Execute API query
        api_result = self._execute_api_query(query)
        
        # Extract SQL from API response
        sql = api_result.get('source', {}).get('sql', '') if api_result else ''
        logger.info(f"\nGenerated SQL: {sql}")
        
        # Execute database query if SQL is available
        db_results = self._execute_db_query(sql) if sql else pd.DataFrame()
        
        # Compare results
        api_count = len(api_result.get('response', '').split('\n\n')) if api_result else 0
        db_count = len(db_results)
        
        result = {
            'description': description,
            'query': query,
            'sql': sql,
            'api_count': api_count,
            'db_count': db_count,
            'expected_count': expected_count,
            'counts_match': api_count == db_count,
            'matches_expected': expected_count is None or api_count == expected_count,
            'api_response': api_result,
            'db_results': db_results
        }
        
        self.results.append(result)
        
        # Log results
        logger.info("\nResults:")
        logger.info(f"API Results: {api_count}")
        logger.info(f"DB Results: {db_count}")
        logger.info(f"Expected: {expected_count if expected_count is not None else 'Not specified'}")
        logger.info(f"Counts Match: {'PASS' if result['counts_match'] else 'FAIL'}")
        logger.info(f"Matches Expected: {'PASS' if result['matches_expected'] else 'FAIL'}")
        
        return result
        
    def generate_report(self) -> str:
        """Generate markdown report of all test results"""
        markdown = "# Specific Project Query Test Results\n\n"
        
        # Add summary statistics
        total_tests = len(self.results)
        passed_count = sum(1 for r in self.results if r['counts_match'] and r['matches_expected'])
        failed_count = total_tests - passed_count
        
        markdown += "## Summary\n"
        markdown += f"* **Total Tests:** {total_tests}\n"
        markdown += f"* **Passed:** {passed_count} ({(passed_count/total_tests)*100:.1f}%)\n"
        markdown += f"* **Failed:** {failed_count} ({(failed_count/total_tests)*100:.1f}%)\n\n"
        
        # Add test categories summary
        categories = {}
        for result in self.results:
            category = result['description'].split(' - ')[0]
            if category not in categories:
                categories[category] = {'total': 0, 'passed': 0}
            categories[category]['total'] += 1
            if result['counts_match'] and result['matches_expected']:
                categories[category]['passed'] += 1
        
        markdown += "## Test Categories\n"
        for category, stats in categories.items():
            success_rate = (stats['passed'] / stats['total']) * 100
            markdown += f"* **{category}:** {stats['passed']}/{stats['total']} ({success_rate:.1f}%)\n"
        
        # Add results table with improved formatting
        markdown += "\n## Test Results\n\n"
        markdown += "| Category | Test Description | Query | Expected | API Results | DB Results | Status |\n"
        markdown += "|----------|-----------------|--------|-----------|-------------|------------|--------|\n"
        
        for result in self.results:
            category, description = result['description'].split(' - ', 1)
            expected = str(result['expected_count']) if result['expected_count'] is not None else "N/A"
            status = "PASS" if result['counts_match'] and result['matches_expected'] else "FAIL"
            markdown += f"| {category} | {description} | `{result['query']}` | {expected} | {result['api_count']} | {result['db_count']} | {status} |\n"
        
        # Add detailed results with SQL queries and response analysis
        markdown += "\n## Detailed Results\n\n"
        for result in self.results:
            category, description = result['description'].split(' - ', 1)
            markdown += f"### {category}: {description}\n"
            markdown += f"**Query:** `{result['query']}`\n\n"
            
            if result['sql']:
                markdown += "**Generated SQL:**\n```sql\n"
                markdown += result['sql'] + "\n```\n\n"
            
            markdown += "**Results:**\n"
            markdown += f"* Expected Count: {result['expected_count'] if result['expected_count'] is not None else 'N/A'}\n"
            markdown += f"* API Results: {result['api_count']}\n"
            markdown += f"* DB Results: {result['db_count']}\n"
            markdown += f"* Status: {status}\n\n"
            
            if result['api_response'] and 'response' in result['api_response']:
                markdown += "**API Response:**\n```\n"
                markdown += result['api_response']['response'] + "\n```\n\n"
            
            if not result['counts_match'] or not result['matches_expected']:
                markdown += "**Discrepancy Details:**\n"
                if not result['counts_match']:
                    markdown += f"* Count mismatch: API returned {result['api_count']} results vs DB's {result['db_count']} results\n"
                if not result['matches_expected']:
                    markdown += f"* Expected {result['expected_count']} results but got {result['api_count']}\n"
                markdown += "\n"
        
        return markdown

def test_specific_queries():
    """Run comprehensive tests on specific project queries"""
    tester = QueryTester()
    
    logger.info("\nTesting Specific Project Queries...")
    
    # 1. Exact Match Tests
    logger.info("\n1. Testing Exact Matches...")
    
    # Quoted project names with exact match
    tester.test_query(
        "Tell me about 'CHILIPA CDSS GIRLS HOSTEL'",
        "Exact Match - Full Quoted Name",
        expected_count=1
    )
    
    tester.test_query(
        "Show details for 'CHILIPA CDSS GIRLS HOSTEL project'",
        "Exact Match - With Project Keyword",
        expected_count=1
    )
    
    # Project code exact matches
    tester.test_query(
        "Show details for project MW-CR-DO",
        "Exact Match - Full Project Code",
        expected_count=1
    )
    
    tester.test_query(
        "Project code MW-CR-DO status",
        "Exact Match - Code with Status",
        expected_count=1
    )
    
    # 2. Case Sensitivity Tests
    logger.info("\n2. Testing Case Sensitivity...")
    
    tester.test_query(
        "Tell me about 'chilipa cdss girls hostel'",
        "Case Sensitivity - All Lowercase",
        expected_count=1
    )
    
    tester.test_query(
        "Show details for project mw-cr-do",
        "Case Sensitivity - Lowercase Code",
        expected_count=1
    )
    
    tester.test_query(
        "What is the status of CHILIPA cdss GIRLS hostel",
        "Case Sensitivity - Mixed Case",
        expected_count=1
    )
    
    # 3. Partial Match Tests
    logger.info("\n3. Testing Partial Matches...")
    
    tester.test_query(
        "Tell me about 'CHILIPA CDSS'",
        "Partial Match - Beginning",
        expected_count=1
    )
    
    tester.test_query(
        "Show status of 'GIRLS HOSTEL'",
        "Partial Match - End",
        expected_count=1
    )
    
    tester.test_query(
        "Project MW-CR",
        "Partial Match - Project Code",
        expected_count=1
    )
    
    # 4. Query Format Variations
    logger.info("\n4. Testing Query Format Variations...")
    
    tester.test_query(
        "What is the progress of 'CHILIPA CDSS GIRLS HOSTEL'",
        "Format - Progress Query",
        expected_count=1
    )
    
    tester.test_query(
        "Show me the budget for 'CHILIPA CDSS GIRLS HOSTEL'",
        "Format - Budget Query",
        expected_count=1
    )
    
    tester.test_query(
        "Who is the contractor for 'CHILIPA CDSS GIRLS HOSTEL'",
        "Format - Contractor Query",
        expected_count=1
    )
    
    tester.test_query(
        "When will 'CHILIPA CDSS GIRLS HOSTEL' be completed",
        "Format - Completion Date Query",
        expected_count=1
    )
    
    # 5. Edge Cases
    logger.info("\n5. Testing Edge Cases...")
    
    tester.test_query(
        "Tell me about 'Non Existent Project'",
        "Edge Case - Non-existent Project",
        expected_count=0
    )
    
    tester.test_query(
        "Show details for project XX-YY-ZZ",
        "Edge Case - Invalid Project Code",
        expected_count=0
    )
    
    tester.test_query(
        "Tell me about 'CHILIPA CDSS GIRLS HOSTEL' and 'Another Project'",
        "Edge Case - Multiple Projects",
        expected_count=1  # Should only return first project
    )
    
    tester.test_query(
        "Tell me about ''",
        "Edge Case - Empty Project Name",
        expected_count=0
    )
    
    tester.test_query(
        "Tell me about 'A'",
        "Edge Case - Single Character",
        expected_count=0
    )
    
    # Generate and save report
    report = tester.generate_report()
    with open('results/specific_project_query_test_results.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info("\nTest results saved to results/specific_project_query_test_results.md")

if __name__ == "__main__":
    test_specific_queries() 