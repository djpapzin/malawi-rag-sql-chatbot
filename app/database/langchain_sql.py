from typing import Dict, Any, Union, List
from langchain_community.utilities import SQLDatabase
from langchain_together import Together
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
import os
from sqlalchemy import text
import re
import logging
import traceback
import pandas as pd
from datetime import datetime
from ..models import (
    GeneralQueryResponse, 
    SpecificQueryResponse, 
    GeneralProjectInfo,
    DetailedProjectInfo,
    Location,
    MonetaryAmount,
    Contractor,
    QueryMetadata,
    DatabaseManager
)
import asyncio
import time

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY')
if not TOGETHER_API_KEY:
    raise ValueError("TOGETHER_API_KEY environment variable not set")

class LangChainSQLIntegration:
    def __init__(self):
        """Initialize the SQL integration with LangChain"""
        try:
            # Initialize database connection
            self.db = DatabaseManager()
            
            # Initialize database connection for LangChain
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'projects.db')
            self.sql_database = SQLDatabase.from_uri(f"sqlite:///{db_path}")
            
            # Initialize LLM
            self.llm = Together(
                model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K",
                api_key=TOGETHER_API_KEY,
                temperature=0.1,  # Lower temperature for more deterministic output
                max_tokens=512  # Increased token limit
            )
            
            # Set up the SQL generation prompt
            self.sql_prompt = PromptTemplate.from_template(
                """Generate a SQL query to answer this question about project data.

Table: proj_dashboard
Columns:
- projectname (text)
- district (text)
- projectsector (text)
- projectstatus (text)
- budget (numeric)
- completionpercentage (numeric)
- startdate (numeric)
- completiondata (numeric)

For general queries, return:
- projectname
- district
- projectsector
- projectstatus
- budget
- completionpercentage

For specific queries, return all columns.

Example Queries:
1. Total budget for all projects:
   SELECT SUM(budget) as total_budget FROM proj_dashboard;

2. Total budget for infrastructure projects:
   SELECT SUM(budget) as total_budget FROM proj_dashboard WHERE LOWER(projectsector) = 'infrastructure';

3. List all infrastructure projects (general query):
   SELECT projectname, district, projectsector, projectstatus, budget, completionpercentage
   FROM proj_dashboard 
   WHERE LOWER(projectsector) = 'infrastructure';

4. Show project details (specific query):
   SELECT * FROM proj_dashboard WHERE projectname = 'Project Name';

5. Show projects in a district:
   SELECT projectname, district, projectsector, projectstatus, budget, completionpercentage
   FROM proj_dashboard
   WHERE LOWER(district) = 'zomba';

Question: {question}
""")

            # Set up the answer generation prompt
            self.answer_prompt = PromptTemplate.from_template(
                """Given the following SQL query and its results, provide a clear and concise answer to the question.
                Format any monetary amounts as "MWK X,XXX.XX".
                
                Question: {question}
                SQL Query: {query}
                Query Results: {results}
                
                Answer:"""
            )
            
            logger.info("Initialized LangChainSQLIntegration")

        except Exception as e:
            logger.error(f"Error initializing LangChainSQLIntegration: {str(e)}")
            raise
        
    def _extract_sql_query(self, text: str) -> str:
        """Extract the SQL query from the LLM response"""
        logger.info(f"Extracting SQL query from text: {repr(text)}")
        
        # Remove any markdown code block markers
        text = text.replace('```sql', '').replace('```', '')
        
        # Find SELECT statement
        matches = []
        
        # Try different patterns from most to least strict
        patterns = [
            r'SELECT\s+.*?(?:;|$)',  # Match until semicolon or end of string
            r'SELECT\s+[^#\n]*',      # Match until comment or newline
            r'SELECT\s+[^.]*'         # Match until period
        ]
        
        for pattern in patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE | re.DOTALL))
            if matches:
                break
                
        for match in matches:
            query = match.group(0).strip()
            
            # Basic validation
            if not query:
                continue
                
            # Remove any trailing explanation text
            if 'SELECT' in query.upper()[5:]:
                # Multiple SELECT statements found, take only the first one
                query = query[:query.upper()[5:].find('SELECT') + 5]
        
        # Clean up the query
            query = query.strip()
            if not query.endswith(';'):
                query += ';'
        
            # Validate query structure
            if all(word.upper() in query.upper() for word in ['SELECT', 'FROM', 'PROJ_DASHBOARD']):
                logger.info(f"Found valid SQL query: {repr(query)}")
        return query

        logger.error(f"No valid SQL query found in text: {repr(text)}")
        raise ValueError("No valid SQL query found in response")

    async def generate_sql_query(self, question: str) -> str:
        """Generate SQL query from natural language question"""
        try:
            # Handle common cases directly
            if 'infrastructure' in question.lower() and 'total budget' in question.lower():
                return "SELECT SUM(budget) as total_budget FROM proj_dashboard WHERE LOWER(projectsector) = 'infrastructure'"
            elif 'total budget' in question.lower():
                return "SELECT SUM(budget) as total_budget FROM proj_dashboard"
            
            # Generate SQL using LLM
            sql_chain = (
                self.sql_prompt 
                | self.llm 
                | StrOutputParser()
            )
            
            try:
                response = await asyncio.wait_for(
                    sql_chain.ainvoke({"question": question}),
                    timeout=30.0  # 30 second timeout
                )
                logger.info(f"Raw LLM response: {response}")
                sql_query = self._extract_sql_query(response)
                
                # Additional validation for common issues
                sql_query = sql_query.replace('`', '"')  # Replace backticks with double quotes
                sql_query = sql_query.replace('are all columns (*)', '*')  # Fix common LLM mistake
                sql_query = sql_query.replace('all columns', '*')  # Fix common LLM mistake
                
                logger.info(f"Validated SQL query: {repr(sql_query)}")
                return sql_query
                
            except asyncio.TimeoutError:
                logger.error("SQL generation timed out")
                raise TimeoutError("SQL generation took too long. Please try again.")
            except Exception as e:
                logger.error(f"Error generating SQL query: {str(e)}")
                raise ValueError(f"Failed to generate SQL query: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error in generate_sql_query: {str(e)}")
            # Fallback queries
            if 'infrastructure' in question.lower():
                if 'total budget' in question.lower():
                    return "SELECT SUM(budget) as total_budget FROM proj_dashboard WHERE LOWER(projectsector) = 'infrastructure'"
                else:
                    return """
                        SELECT projectname, district, projectsector, projectstatus, budget, completionpercentage 
                        FROM proj_dashboard 
                        WHERE LOWER(projectsector) = 'infrastructure'
                    """
            elif 'total budget' in question.lower():
                return "SELECT SUM(budget) as total_budget FROM proj_dashboard"
            elif any(word in question.lower() for word in ['details', 'about', 'specific']):
                # Extract the project name from the question
                search_terms = []
                if 'about' in question.lower():
                    search_terms = question.lower().split('about')[-1].strip().split()
                elif 'for' in question.lower():
                    search_terms = question.lower().split('for')[-1].strip().split()
                elif 'on' in question.lower():
                    search_terms = question.lower().split('on')[-1].strip().split()
                
                # Remove common words and create search pattern
                stop_words = {'the', 'a', 'an', 'in', 'at', 'of', 'to', 'for', 'by', 'with', 'project', 'details', 'rehabilitation'}
                search_terms = [term for term in search_terms if term not in stop_words]
                
                # Create individual LIKE conditions for each search term
                conditions = []
                for term in search_terms:
                    conditions.append(f"LOWER(projectname) LIKE '%{term}%'")
                
                # Combine conditions with OR for more flexible matching
                where_clause = ' OR '.join(conditions)
                
                # Add projectsector condition if infrastructure is mentioned
                if 'infrastructure' in question.lower():
                    where_clause = f"({where_clause}) AND LOWER(projectsector) = 'infrastructure'"
                
                return f"SELECT * FROM proj_dashboard WHERE {where_clause}"
            else:
                # Default to general query format for district or other filters
                base_fields = "projectname, district, projectsector, projectstatus, budget, completionpercentage"
                where_clause = ""
                
                # Check for district filter
                if 'district' in question.lower():
                    district = None
                    for word in question.lower().split():
                        if word in ['zomba', 'lilongwe', 'blantyre', 'mzuzu']:  # Add more districts as needed
                            district = word
                            break
                    if district:
                        where_clause = f"WHERE LOWER(district) = '{district}'"
                
                return f"SELECT {base_fields} FROM proj_dashboard {where_clause}"

    async def get_answer(self, question: str) -> Union[GeneralQueryResponse, SpecificQueryResponse]:
        """Get an answer for a natural language query"""
        try:
            # Generate SQL query
            sql_query = await self.generate_sql_query(question)
            
            # Validate the query
            self.validate_sql_query(sql_query)
            
            # Execute query and measure time
            start_time = time.time()
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql_query)
                results = cursor.fetchall()
                
                # Convert results to list of dicts
                columns = [description[0] for description in cursor.description]
                results = [dict(zip(columns, row)) for row in results]
            
            query_time = time.time() - start_time
            
            # Format response
            return self.format_response(results, sql_query, query_time)
            
        except Exception as e:
            logger.error(f"Error getting answer: {str(e)}\n{traceback.format_exc()}")
            raise

    def format_response(self, query_results: List[Dict[str, Any]], sql_query: str, query_time: float) -> Union[GeneralQueryResponse, SpecificQueryResponse]:
        """Format the query results into a standardized response"""
        try:
            # Format monetary amounts
            for result in query_results:
                if 'budget' in result:
                    result['total_budget'] = {
                        'amount': float(result['budget']),
                        'formatted': f"MWK {float(result['budget']):,.2f}"
                    }
                if 'completionpercentage' in result:
                    result['completion_percentage'] = float(result['completionpercentage'])
                if 'projectname' in result:
                    result['project_name'] = result['projectname']
                if 'projectsector' in result:
                    result['project_sector'] = result['projectsector']
                if 'projectstatus' in result:
                    result['project_status'] = result['projectstatus']

            # Create metadata
            metadata = QueryMetadata(
                total_results=len(query_results),
                query_time=f"{query_time:.2f}s",
                sql_query=sql_query
            )

            # Determine if this is a general or specific query
            is_specific = any(key in sql_query.lower() for key in ['count', 'sum', 'avg', 'min', 'max'])

            if is_specific:
                return SpecificQueryResponse(
                    results=query_results,
                    metadata=metadata
                )
            else:
                return GeneralQueryResponse(
                    results=query_results,
                    metadata=metadata
                )
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            logger.error(traceback.format_exc())
            raise

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
                    {"name": "projectname", "type": "text", "description": "projectname"},
                    {"name": "district", "type": "text", "description": "district"},
                    {"name": "projectsector", "type": "text", "description": "projectsector"},
                    {"name": "projectstatus", "type": "text", "description": "projectstatus"},
                    {"name": "budget", "type": "numeric", "description": "budget"},
                    {"name": "completionpercentage", "type": "numeric", "description": "completionpercentage"},
                    {"name": "startdate", "type": "numeric", "description": "startdate"},
                    {"name": "completiondata", "type": "numeric", "description": "completiondata"}
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

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process a natural language query and return formatted results"""
        try:
            # Generate SQL query
            sql_query = await self.generate_sql_query(query)
            if not sql_query:
                raise ValueError("Failed to generate SQL query")

            # Execute query
            results, query_time = self.db.execute_query(sql_query)
            
            # Format response
            response = self.format_response(results, sql_query, query_time)
            
            return {"response": response}
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}\n{traceback.format_exc()}")
            raise ValueError(f"Error processing query: {str(e)}")
