import pytest
import json
import re
from typing import Dict, Any
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from app.database.langchain_sql import LangChainSQLIntegration
from app.models import ChatRequest

# Load environment variables
load_dotenv()

class TestResponseVerification:
    @pytest.fixture(scope="class")
    def db_connection(self):
        """Create a database connection fixture"""
        try:
            connection = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME")
            )
            yield connection
            connection.close()
        except Error as e:
            pytest.fail(f"Failed to connect to database: {str(e)}")

    def execute_sql_query(self, connection, query: str) -> list:
        """Execute a SQL query and return results"""
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            pytest.fail(f"Failed to execute query: {str(e)}")

    def extract_number_from_text(self, text: str, pattern: str) -> int:
        """Extract a number from text using regex pattern"""
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
        return None

    def extract_sql_query(self, metadata: Dict[str, Any]) -> str:
        """Extract SQL query from metadata"""
        return metadata.get("sql_query", "").strip()

    def verify_project_count(self, llm_response: str, sql_results: list) -> bool:
        """Verify if the number of projects mentioned in LLM response matches SQL results"""
        # Extract number from LLM response (e.g., "There are 43 health projects...")
        llm_count = self.extract_number_from_text(llm_response, r"There are (\d+)")
        actual_count = len(sql_results)
        
        if llm_count is None:
            pytest.fail(f"Could not extract project count from LLM response: {llm_response}")
        
        assert llm_count == actual_count, \
            f"LLM mentioned {llm_count} projects but SQL query returned {actual_count} projects"

    def verify_total_results(self, metadata: Dict[str, Any], sql_results: list) -> bool:
        """Verify if total_results in metadata matches SQL results"""
        metadata_count = metadata.get("total_results")
        actual_count = len(sql_results)
        
        assert metadata_count == actual_count, \
            f"Metadata shows {metadata_count} results but SQL query returned {actual_count} results"

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
            json.dump(sql_results, f, indent=2)
        
        # Verify results
        self.verify_project_count(llm_response, sql_results)
        self.verify_total_results(metadata, sql_results)

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
            json.dump(sql_results, f, indent=2)
        
        # Extract budget from LLM response
        budget_pattern = r"MWK\s+([\d,]+(?:\.\d{2})?)"
        llm_budget = self.extract_number_from_text(llm_response, budget_pattern)
        
        if llm_budget is not None:
            # Calculate actual total budget from SQL results
            actual_budget = sum(float(result["total_budget"]) for result in sql_results)
            
            # Verify budget matches
            assert abs(llm_budget - actual_budget) < 1, \
                f"LLM mentioned budget {llm_budget} but actual total is {actual_budget}"
