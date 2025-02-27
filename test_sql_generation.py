#!/usr/bin/env python3
import os
import logging
from dotenv import load_dotenv
from app.database.langchain_sql import LangChainSQLIntegration

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test queries
TEST_QUERIES = [
    "Show me all projects in Lilongwe",
    "What is the total budget for infrastructure projects?",
    "Which projects have the highest completion percentage?",
    "List all districts",
    "How many projects are there in each sector?"
]

def main():
    # Initialize SQL integration
    sql_integration = LangChainSQLIntegration()
    
    # Test each query
    for query in TEST_QUERIES:
        print(f"\n\n{'='*50}")
        print(f"Testing query: {query}")
        print(f"{'-'*50}")
        
        try:
            # Get table info
            table_info = sql_integration.get_table_info()
            print(f"Table info: {table_info}")
            
            # Generate SQL query
            sql_query = sql_integration._generate_sql_query(query)
            print(f"Generated SQL query: {sql_query}")
            
            # Validate SQL query
            is_valid, error = sql_integration.validate_sql_query(sql_query)
            print(f"Valid: {is_valid}, Error: {error}")
            
            if is_valid:
                # Transform SQL query
                transformed_query = sql_integration.generate_sql_query(query)
                print(f"Transformed SQL query: {transformed_query}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
if __name__ == "__main__":
    main()
