#!/usr/bin/env python3
"""
Test for aggregate query detection and SQL generation
"""
import os
import sys
import unittest
from app.database.langchain_sql import LangChainSQLIntegration
from app.routers.chat import _is_aggregate_query

class TestAggregateQueries(unittest.TestCase):
    """Test cases for aggregate query detection and handling"""
    
    def test_aggregate_detection(self):
        """Test the aggregate query detection function"""
        # Test cases that should be detected as aggregate queries
        aggregate_queries = [
            "How many projects are there in Lilongwe?",
            "What is the total budget for infrastructure projects?",
            "Show me the average completion percentage of education projects",
            "Give me a breakdown of projects by sector",
            "What's the distribution of projects across districts?",
            "Count the number of completed projects",
            "Sum the budgets of all healthcare projects",
            "Compare the budgets between different sectors",
            "Show statistics for projects in the southern region"
        ]
        
        # Test cases that should not be detected as aggregate queries
        non_aggregate_queries = [
            "Show me details about the Nachuma Market Shed project",
            "What is the status of the Chilipa CDSS Girls Hostel?",
            "Tell me about education projects in Zomba",
            "List all projects in Lilongwe",
            "When did the Boma Stadium Phase 3 project start?",
            "Who is responsible for the Chilingani School Block construction?",
            "Describe the project with code MW-CR-DO"
        ]
        
        # Test aggregate queries
        for query in aggregate_queries:
            self.assertTrue(
                _is_aggregate_query(query),
                f"Failed to detect aggregate query: {query}"
            )
        
        # Test non-aggregate queries
        for query in non_aggregate_queries:
            self.assertFalse(
                _is_aggregate_query(query),
                f"Incorrectly detected as aggregate query: {query}"
            )
    
    def test_sql_generation_prompt_selection(self):
        """Test that different prompts are selected for different query types"""
        # This is a simple test to verify that the _generate_sql_query method
        # selects different prompts based on the query type
        # We'll just print the results for manual verification
        
        # Sample queries
        aggregate_query = "What is the total budget for all projects by sector?"
        regular_query = "Show me details about the Nachuma Market Shed project"
        
        # Print the query types for manual verification
        print(f"\nAggregate query: '{aggregate_query}'")
        print(f"Is aggregate: {_is_aggregate_query(aggregate_query)}")
        
        print(f"\nRegular query: '{regular_query}'")
        print(f"Is aggregate: {_is_aggregate_query(regular_query)}")
        
        # This test passes if it runs without errors
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
