from typing import Dict, Any, List, Union
from langchain_community.utilities import SQLDatabase
from langchain_together import Together
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
import os
from sqlalchemy import text
import re
import logging
import traceback
from ..response_formatter import (
    format_general_response,
    format_specific_response,
    is_specific_query,
    GeneralQueryResponse,
    SpecificQueryResponse
)

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LangChainSQLIntegration:
    def __init__(self):
        """Initialize the LangChain SQL Integration"""
        try:
            # Load environment variables
            load_dotenv()
            
            # Initialize logger
            logging.basicConfig(level=logging.INFO)
            
            # Setup database connection
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'malawi_projects1.db')
            logger.info(f"Looking for database at: {db_path}")
            
            if not os.path.exists(db_path):
                logger.error(f"Database file not found at {db_path}")
                raise ValueError(f"Database file not found at {db_path}")
                
            logger.info(f"Found database at {db_path}")
            
            # Create database instance with direct SQLite connection
            try:
                logger.info("Attempting to create SQLDatabase instance...")
                self.db = SQLDatabase.from_uri(
                    f"sqlite:///{db_path}",
                    include_tables=['proj_dashboard'],
                    sample_rows_in_table_info=2,
                    view_support=True
                )
                logger.info("Successfully created SQLDatabase instance")
            except Exception as e:
                logger.error(f"Failed to create SQLDatabase instance: {str(e)}")
                logger.error(f"Full trace: {traceback.format_exc()}")
                raise
            
            # Test database connection
            try:
                logger.info("Testing database connection...")
                test_query = "SELECT COUNT(*) FROM proj_dashboard;"
                result = self.db.run(test_query)
                logger.info(f"Database connection test successful. Row count: {result}")
            except Exception as e:
                logger.error(f"Database connection test failed: {str(e)}")
                logger.error(f"Full trace: {traceback.format_exc()}")
                raise ValueError(f"Failed to connect to database: {str(e)}")
            
            # Initialize LLM
            self.llm = Together(
                model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K",
                api_key=os.getenv("TOGETHER_API_KEY"),
                temperature=0.1,  # Lower temperature for more deterministic output
                max_tokens=128  # Limit tokens to prevent long explanations
            )
            
            # Initialize the SQL toolkit
            self.toolkit = SQLDatabaseToolkit(
                db=self.db,
                llm=self.llm
            )
            
            # Get the tools
            self.tools = self.toolkit.get_tools()
            
            # Create prompts
            self.sql_prompt = ChatPromptTemplate.from_messages([
                ("system", """Generate SQL queries for Malawi infrastructure projects database.

IMPORTANT RULES:
1. Use ONLY lowercase column names
2. Always query from the 'proj_dashboard' table
3. Use single quotes for string values
4. Include semicolon at the end of queries
5. Keep queries simple and direct

SCHEMA:
TABLE: proj_dashboard
- projectname (TEXT)
- district (TEXT)
- projectsector (TEXT)
- projectstatus (TEXT)
- budget (NUMERIC)
- completionpercentage (NUMERIC)
- startdate (NUMERIC)
- completiondata (NUMERIC)

EXAMPLES:
Q: How many projects in Lilongwe?
SELECT COUNT(*) FROM proj_dashboard WHERE district = 'lilongwe';

Q: Total budget for all projects?
SELECT SUM(budget) FROM proj_dashboard;

Q: Projects in Infrastructure sector?
SELECT * FROM proj_dashboard WHERE LOWER(projectsector) = 'infrastructure';

Q: Projects over 50% complete?
SELECT * FROM proj_dashboard WHERE completionpercentage > 50;

Q: Average budget by district?
SELECT district, AVG(budget) FROM proj_dashboard GROUP BY district;
"""),
                ("human", "{question}")
            ])
            
            self.answer_prompt = ChatPromptTemplate.from_messages([
                ("system", "Given the SQL query and its results, provide a natural language answer.\n\nSQL Query: {query}\nQuery Results: {results}\nQuestion: {question}"),
                ("human", "Please provide a clear and concise answer.")
            ])

        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
        
    def extract_sql_query(self, text: str) -> str:
        """Extract and clean SQL query from text"""
        # Remove markdown code blocks
        text = re.sub(r'```(?:sql)?(.*?)```', r'\1', text, flags=re.DOTALL)
        
        # Find SQL query
        match = re.search(r'select\s+.*?;', text.lower(), re.DOTALL | re.IGNORECASE)
        if not match:
            raise ValueError("No SQL query found in text")
            
        query = match.group(0).strip()
        
        # Clean up the query
        query = ' '.join(query.split())  # Normalize whitespace
        query = query.rstrip(';') + ';'  # Ensure single semicolon at end
        
        return query

    def generate_sql_query(self, question: str) -> str:
        """Generate SQL query from natural language question"""
        try:
            chain = (
                self.sql_prompt 
                | self.llm 
                | StrOutputParser()
            )
            
            # Generate SQL query
            text = chain.invoke({"question": question})
            logger.info(f"LLM response: {text}")
            
            # Extract SQL query
            query = self.extract_sql_query(text)
            if not query:
                raise ValueError("Failed to extract SQL query from LLM response")
                
            logger.info(f"Extracted query: {query}")
            return query
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {str(e)}\nFull trace: {traceback.format_exc()}")
            raise ValueError(f"Failed to generate SQL query: {str(e)}")

    def get_answer(self, question: str) -> Union[GeneralQueryResponse, SpecificQueryResponse]:
        """
        Get a complete answer to a question about the database.
        
        Args:
            question (str): Natural language question about the database
            
        Returns:
            Union[GeneralQueryResponse, SpecificQueryResponse]: Formatted response based on query type
        """
        try:
            # Generate SQL query
            query = self.generate_sql_query(question)
            logger.info(f"Generated SQL query: {query}")
            
            # Validate query
            self.validate_sql_query(query)
            logger.info("Query validation passed")
            
            # Execute query with error handling
            logger.info(f"Executing query: {query}")
            try:
                result = self.db.run(query)
                logger.info(f"Query result: {result}")
            except Exception as exec_error:
                logger.error(f"Query execution failed: {str(exec_error)}\nQuery: {query}")
                raise ValueError(f"Query execution failed: {str(exec_error)}")
            
            # Convert result to list of dictionaries
            if isinstance(result, str):
                # Handle single value results
                if result.strip('()').replace('.0', '').isdigit():
                    value = float(result.strip('()'))
                    result = [{'value': value}]
                else:
                    result = [{'result': result}]
            elif isinstance(result, tuple):
                # Handle tuple results
                result = [{'value': item} for item in result]
            
            # Format response based on query type
            if is_specific_query(question):
                if result and len(result) > 0:
                    return format_specific_response(result[0])
                else:
                    raise ValueError("No results found for specific query")
            else:
                return format_general_response(result)
            
        except Exception as e:
            logger.error(f"Error getting answer: {str(e)}\nFull trace: {traceback.format_exc()}")
            raise ValueError(f"Failed to get answer: {str(e)}")

    def get_table_info(self) -> Dict[str, Any]:
        """
        Get information about the database schema.
        
        Returns:
            Dict[str, Any]: Database schema information in a structured format
        """
        try:
            schema = {
                "table_name": "proj_dashboard",
                "columns": [
                    {"name": "projectname", "type": "TEXT", "description": "projectname"},
                    {"name": "district", "type": "TEXT", "description": "district"},
                    {"name": "projectsector", "type": "TEXT", "description": "projectsector"},
                    {"name": "projectstatus", "type": "TEXT", "description": "projectstatus"},
                    {"name": "budget", "type": "NUM", "description": "budget"},
                    {"name": "completionpercentage", "type": "NUM", "description": "completionpercentage"},
                    {"name": "startdate", "type": "NUM", "description": "startdate"},
                    {"name": "completiondata", "type": "NUM", "description": "completiondata"}
                ]
            }
            return schema
        except Exception as e:
            logger.error(f"Error getting schema info: {str(e)}")
            raise

    def validate_sql_query(self, query: str) -> bool:
        """
        Validate the SQL query for proper structure and syntax.
        Args:
            query (str): SQL query to validate
        Returns:
            bool: True if valid, raises ValueError if invalid
        """
        query = query.lower()  # Convert to lowercase for validation
        
        validation_checks = {
            'invalid_select': not re.search(r'select\s+.+?\s+from', query),
            'missing_from': 'from proj_dashboard' not in query,
            'unbalanced_quotes': query.count("'") % 2 != 0,
            'missing_group_by': (
                any(f in query for f in ['avg(', 'sum(']) and
                re.search(r',', query.split('from')[0]) and
                not re.search(r'count\(\*\)', query) and
                'group by' not in query
            ),
            'invalid_syntax': bool(re.search(r'\b(and|or)\s+(?:another|one|lets|try)\b', query))
        }
        
        failed = next((k for k, v in validation_checks.items() if v), None)
        if failed:
            raise ValueError({
                'invalid_select': 'Invalid SELECT statement',
                'missing_from': 'Must include FROM proj_dashboard',
                'unbalanced_quotes': 'Unbalanced single quotes',
                'missing_group_by': 'Aggregate functions require GROUP BY when selecting multiple columns',
                'invalid_syntax': 'Invalid SQL syntax'
            }[failed])
        
        return True
