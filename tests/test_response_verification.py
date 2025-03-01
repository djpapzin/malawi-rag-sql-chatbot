import pytest
import json
import re
import sqlite3
from typing import Dict, Any
import os
from dotenv import load_dotenv
from app.database.langchain_sql import LangChainSQLIntegration
from app.models import ChatRequest, DatabaseManager

# Load environment variables
load_dotenv()

class TestResponseVerification:
    @pytest.fixture(scope="class")
    def db_connection(self):
        """Create a database connection fixture"""
        try:
            # Use the same database path as the application
            db_manager = DatabaseManager()
            connection = sqlite3.connect(db_manager.db_path)
            connection.row_factory = sqlite3.Row  # Enable row factory for named columns
            yield connection
            connection.close()
        except Exception as e:
            pytest.fail(f"Failed to connect to database: {str(e)}")

    def execute_sql_query(self, connection, query: str) -> list:
        """Execute a SQL query and return results"""
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        except Exception as e:
            pytest.fail(f"Failed to execute query: {str(e)}")

    def extract_number_from_text(self, text: str, pattern: str) -> int:
        """Extract a number from text using regex pattern"""
        match = re.search(pattern, text)
        if match:
            try:
                # Handle numbers with commas (e.g., "1,234")
                number_str = match.group(1).replace(',', '')
                return int(number_str)
            except ValueError:
                return None
        return None

    def extract_sql_query(self, metadata: Dict[str, Any]) -> str:
        """Extract SQL query from metadata"""
        return metadata.get("sql_query", "").strip()

    def verify_project_count(self, llm_response: str, sql_results: list, metadata: Dict[str, Any]) -> bool:
        """Verify if the number of projects mentioned in LLM response matches SQL results"""
        # Extract number from LLM response (e.g., "There are 43 health projects...")
        llm_count = self.extract_number_from_text(llm_response, r"There are (\d+)")
        actual_count = len(sql_results)
        metadata_count = metadata.get("total_results", 0)
        
        if llm_count is None:
            pytest.fail(f"Could not extract project count from LLM response: {llm_response}")
        
        # Save count verification results
        verification_file = "test_results/count_verification.json"
        with open(verification_file, "w") as f:
            json.dump({
                "llm_count": llm_count,
                "actual_count": actual_count,
                "metadata_count": metadata_count,
                "discrepancy": {
                    "llm_vs_actual": llm_count - actual_count,
                    "llm_vs_metadata": llm_count - metadata_count,
                    "metadata_vs_actual": metadata_count - actual_count
                }
            }, f, indent=2)
        
        # Verify counts match
        assert metadata_count == actual_count, \
            f"Metadata count ({metadata_count}) doesn't match actual SQL results ({actual_count})"
        
        # Flag if LLM count is incorrect but don't fail the test
        if llm_count != actual_count:
            print(f"\nWARNING: LLM response count ({llm_count}) doesn't match actual count ({actual_count})")
            print(f"This indicates the LLM needs improvement in counting accuracy")
            return False
        return True

    def verify_total_results(self, metadata: Dict[str, Any], sql_results: list) -> bool:
        """Verify if total_results in metadata matches SQL results"""
        metadata_count = metadata.get("total_results")
        actual_count = len(sql_results)
        
        assert metadata_count == actual_count, \
            f"Metadata shows {metadata_count} results but SQL query returned {actual_count} results"

    def verify_budget_amounts(self, llm_response: str, sql_results: list) -> bool:
        """Verify budget amounts mentioned in LLM response"""
        # Extract all budget amounts from LLM response
        budget_pattern = r"MWK\s+([\d,]+(?:\.\d{2})?)"
        matches = re.finditer(budget_pattern, llm_response)
        
        budgets = {}
        for match in matches:
            try:
                amount = float(match.group(1).replace(',', ''))
                # Get surrounding context (up to 100 chars before and after)
                start = max(0, match.start() - 100)
                end = min(len(llm_response), match.end() + 100)
                context = llm_response[start:end]
                budgets[amount] = context
            except ValueError:
                continue
        
        # Save budget verification results
        verification_file = "test_results/budget_verification.json"
        with open(verification_file, "w") as f:
            json.dump({
                "llm_budgets": budgets,
                "sql_results": [{
                    "project_name": r.get("project_name"),
                    "budget": r.get("total_budget")
                } for r in sql_results]
            }, f, indent=2, default=str)
        
        # Verify each mentioned budget exists in SQL results
        for budget in budgets.keys():
            matching_projects = [r for r in sql_results 
                               if abs(float(r.get("total_budget", 0)) - budget) < 1]
            if not matching_projects:
                print(f"\nWARNING: Budget amount MWK {budget:,.2f} mentioned in LLM response not found in SQL results")
                print(f"Context: {budgets[budget]}")

    @pytest.mark.asyncio
    async def test_health_sector_query(self, db_connection):
        """Test verification for health sector projects query"""
        # Initialize LangChain SQL integration
        sql_chain = LangChainSQLIntegration()
        
        # Test query
        query = "Which projects are there in the health sector"
        
        # Get LLM response
        response = await sql_chain.process_query(query)
        
        # Extract components
        llm_response = response["results"][0]["message"]
        metadata = response["metadata"]
        sql_query = self.extract_sql_query(metadata)
        
        # Execute the actual SQL query
        sql_results = self.execute_sql_query(db_connection, sql_query)
        
        # Save SQL results for analysis
        results_file = "test_results/health_sector_query_results.json"
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        with open(results_file, "w") as f:
            json.dump(sql_results, f, indent=2, default=str)
        
        # Save LLM response for comparison
        llm_response_file = "test_results/health_sector_llm_response.json"
        with open(llm_response_file, "w") as f:
            json.dump({
                "llm_response": llm_response,
                "metadata": metadata
            }, f, indent=2, default=str)
        
        # Verify results
        self.verify_project_count(llm_response, sql_results, metadata)
        self.verify_total_results(metadata, sql_results)
        self.verify_budget_amounts(llm_response, sql_results)

    @pytest.mark.asyncio
    async def test_budget_verification(self, db_connection):
        """Test verification of budget calculations"""
        sql_chain = LangChainSQLIntegration()
        query = "What is the total budget for health sector projects?"
        
        # Get LLM response
        response = await sql_chain.process_query(query)
        
        # Extract components
        llm_response = response["results"][0]["message"]
        metadata = response["metadata"]
        sql_query = self.extract_sql_query(metadata)
        
        # Execute the actual SQL query
        sql_results = self.execute_sql_query(db_connection, sql_query)
        
        # Save SQL results
        results_file = "test_results/health_sector_budget_results.json"
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        with open(results_file, "w") as f:
            json.dump(sql_results, f, indent=2, default=str)
        
        # Save LLM response for comparison
        llm_response_file = "test_results/health_sector_budget_llm_response.json"
        with open(llm_response_file, "w") as f:
            json.dump({
                "llm_response": llm_response,
                "metadata": metadata
            }, f, indent=2, default=str)
        
        # Verify budgets
        self.verify_budget_amounts(llm_response, sql_results)
        
        # Extract total budget from LLM response
        budget_pattern = r"MWK\s+([\d,]+(?:\.\d{2})?)"
        llm_budget = self.extract_number_from_text(llm_response, budget_pattern)
        
        if llm_budget is not None:
            # Calculate actual total budget from SQL results
            actual_budget = sum(float(result.get("total_budget", 0)) for result in sql_results)
            
            # Verify budget matches with a small margin of error (1%)
            assert abs(llm_budget - actual_budget) / actual_budget < 0.01, \
                f"LLM mentioned budget {llm_budget:,} but actual total is {actual_budget:,}"
