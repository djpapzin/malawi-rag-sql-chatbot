import pytest
import os
import json
import asyncio
from app.database.langchain_sql import run_rag_sql
from app.database.db_functions import run_direct_query
import re

class TestDrilldown:
    @pytest.mark.asyncio
    async def test_sector_district_drilldown(self):
        """Test drill-down query for health projects in Lilongwe district."""
        query = "How many health projects are in Lilongwe district?"
        llm_response = await run_rag_sql(query)
        
        # Check the response format
        assert llm_response, "Response should not be empty"
        
        # Save the response for inspection
        os.makedirs("test_results", exist_ok=True)
        with open("test_results/drilldown_response.json", "w") as f:
            json.dump({"llm_response": llm_response}, f, indent=2)
        
        # Extract count from LLM response using regex
        count_match = re.search(r"There are (\d+) projects", llm_response)
        llm_count = int(count_match.group(1)) if count_match else None
        
        # Get actual count from SQL
        sql_query = """
        SELECT COUNT(*) as count
        FROM proj_dashboard 
        WHERE LOWER(projectsector) LIKE '%health%' 
        AND LOWER(district) = 'lilongwe'
        """
        
        results = await run_direct_query(sql_query)
        actual_count = results[0]["count"]
        
        # Save counts for comparison
        with open("test_results/drilldown_counts.json", "w") as f:
            json.dump({
                "llm_count": llm_count,
                "actual_count": actual_count,
                "discrepancy": actual_count - (llm_count or 0),
                "sql_query": sql_query
            }, f, indent=2)
        
        # Verify counts match
        assert llm_count == actual_count, f"Count mismatch: LLM={llm_count}, SQL={actual_count}"
        
        # Check for Lilongwe district in response
        assert "Lilongwe" in llm_response, "Response should mention Lilongwe district"
        
        # Check for Health sector in response
        assert "Health" in llm_response, "Response should mention the Health sector"

        print(f"✅ Drill-down test passed. Found {actual_count} health projects in Lilongwe district.")
        
    @pytest.mark.asyncio
    async def test_complex_drilldown(self):
        """Test complex drill-down query with multiple filters."""
        query = "How many completed health projects with budget over 50 million are in the Central Region?"
        llm_response = await run_rag_sql(query)
        
        # Save the response for inspection
        with open("test_results/complex_drilldown_response.json", "w") as f:
            json.dump({"llm_response": llm_response}, f, indent=2)
        
        # Extract count from LLM response using regex
        count_match = re.search(r"There are (\d+) projects", llm_response)
        llm_count = int(count_match.group(1)) if count_match else None
        
        # Get actual count from SQL
        sql_query = """
        SELECT COUNT(*) as count
        FROM proj_dashboard 
        WHERE LOWER(projectsector) LIKE '%health%' 
        AND LOWER(projectstatus) = 'completed'
        AND budget > 50000000
        AND (
            LOWER(district) IN ('lilongwe', 'kasungu', 'ntcheu', 'dedza', 'salima', 'mchinji', 'nkhotakota', 'ntchisi', 'dowa')
        )
        """
        
        results = await run_direct_query(sql_query)
        actual_count = results[0]["count"]
        
        # Save counts for comparison
        with open("test_results/complex_drilldown_counts.json", "w") as f:
            json.dump({
                "llm_count": llm_count,
                "actual_count": actual_count,
                "discrepancy": actual_count - (llm_count or 0),
                "sql_query": sql_query
            }, f, indent=2)
        
        # Verify counts match
        assert llm_count == actual_count, f"Count mismatch: LLM={llm_count}, SQL={actual_count}"
        
        print(f"✅ Complex drill-down test passed. Found {actual_count} completed health projects with budget over 50M in Central Region.")
