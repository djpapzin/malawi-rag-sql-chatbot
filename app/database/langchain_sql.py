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
                """You are an expert SQL query generator. Generate a SQL query to answer questions about project data.

Table: proj_dashboard
Columns:
- projectname (text): Name of the project
- district (text): District where project is located
- projectsector (text): Sector (Infrastructure, Water, Education, Healthcare, Energy)
- projectstatus (text): Status (Active, Planning, Completed, On Hold)
- budget (numeric): Project budget in MWK
- completionpercentage (numeric): Percentage of completion
- startdate (numeric): Project start date (YYYYMMDD)
- completiondata (numeric): Expected completion date (YYYYMMDD)

IMPORTANT RULES:
1. ALWAYS include 'FROM proj_dashboard'
2. For counting queries, use 'COUNT(*) as count'
3. For budget sums, use 'SUM(budget) as total_budget'
4. For filtering text fields, ALWAYS use LOWER() on both sides
5. Return these columns for listing queries:
   projectname, district, projectsector, projectstatus, budget, completionpercentage

Example Queries:
1. "What is the total budget for water projects?"
   SELECT SUM(budget) as total_budget 
   FROM proj_dashboard 
   WHERE LOWER(projectsector) = 'water';

2. "How many projects are in Lilongwe?"
   SELECT COUNT(*) as count 
   FROM proj_dashboard 
   WHERE LOWER(district) = 'lilongwe';

3. "Show all completed projects"
   SELECT projectname, district, projectsector, projectstatus, budget, completionpercentage
   FROM proj_dashboard 
   WHERE LOWER(projectstatus) = 'completed';

4. "List projects with completion above 75%"
   SELECT projectname, district, projectsector, projectstatus, budget, completionpercentage
   FROM proj_dashboard 
   WHERE completionpercentage > 75;

Question: {question}

Return ONLY the SQL query, no explanations.""")

            # Set up the answer generation prompt
            self.answer_prompt = PromptTemplate.from_template(
                """Given the SQL query results, format a clear response.

Question: {question}
SQL Query: {query}
Results: {results}

Formatting Rules:
1. Format monetary amounts as "MWK X,XXX.XX"
2. Format percentages as "X.X%"
3. For project listings, include:
   - Project Name: [name]
   - Location: [district]
   - Sector: [sector]
   - Status: [status]
   - Budget: [formatted_budget]
   - Completion: [formatted_percentage]
4. For counts, respond with "Total Count: X projects"
5. For sums, respond with "Total Budget: MWK X,XXX.XX"

Response:""")
            
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

    def validate_sql_query(self, query: str) -> tuple[bool, str]:
        """Validate SQL query before execution"""
        try:
            # Basic SQL injection prevention
            dangerous_patterns = [
                r';\s*DROP',
                r';\s*DELETE',
                r';\s*UPDATE',
                r';\s*INSERT',
                r'UNION\s+ALL',
                r'UNION\s+SELECT'
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return False, "Invalid SQL pattern detected"

            # Required components
            if 'FROM proj_dashboard' not in query.upper():
                return False, "Must include FROM proj_dashboard"

            if not query.strip().upper().startswith('SELECT'):
                return False, "Invalid SELECT statement"

            # Validate column names
            valid_columns = {
                'projectname', 'district', 'projectsector', 'projectstatus',
                'budget', 'completionpercentage', 'startdate', 'completiondata'
            }
            
            # Extract column names from query
            columns_match = re.search(r'SELECT\s+(.*?)\s+FROM', query, re.IGNORECASE)
            if not columns_match:
                return False, "Invalid SELECT clause"

            columns = columns_match.group(1).lower()
            
            # Allow COUNT(*), SUM(budget), and other aggregates
            if any(x in columns.lower() for x in ['count(*)', 'sum(', 'avg(', 'min(', 'max(']):
                return True, ""

            # For non-aggregate queries, validate individual columns
            if '*' not in columns:
                query_columns = {c.strip().split('.')[-1] for c in columns.split(',') 
                               if not any(agg in c.lower() for agg in ['as', 'count', 'sum', 'avg', 'min', 'max'])}
                invalid_columns = query_columns - valid_columns
                if invalid_columns:
                    return False, f"Invalid columns: {', '.join(invalid_columns)}"

            return True, ""
            
        except Exception as e:
            logger.error(f"Error validating SQL query: {str(e)}")
            return False, str(e)

    async def generate_sql_query(self, question: str) -> str:
        """Generate SQL query from natural language question"""
        try:
            # Handle common cases directly
            question_lower = question.lower()
            
            if 'budget' in question_lower and 'infrastructure' in question_lower:
                return "SELECT SUM(budget) as total_budget FROM proj_dashboard WHERE LOWER(projectsector) = 'infrastructure'"
            
            if 'projects' in question_lower and any(district in question_lower for district in ['zomba', 'lilongwe']):
                district = 'zomba' if 'zomba' in question_lower else 'lilongwe'
                return f"""SELECT projectname, district, projectsector, projectstatus, budget, completionpercentage 
                         FROM proj_dashboard WHERE LOWER(district) = '{district}'"""
            
            if 'completed' in question_lower and 'projects' in question_lower:
                return """SELECT projectname, district, projectsector, projectstatus, budget, completionpercentage
                         FROM proj_dashboard WHERE LOWER(projectstatus) = 'completed'"""
            
            # Use LLM for other cases
            sql_chain = self.sql_prompt | self.llm | StrOutputParser()
            
            response = await sql_chain.ainvoke({"question": question})
            sql_query = self._extract_sql_query(response)
            
            if not sql_query.upper().startswith('SELECT'):
                raise ValueError("Invalid SELECT statement")
            if 'FROM proj_dashboard' not in sql_query.upper():
                raise ValueError("Must include FROM proj_dashboard")
            
            return sql_query
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {str(e)}")
            raise ValueError(f"Failed to generate SQL query: {str(e)}")

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

    def format_response(self, query_results: List[Dict[str, Any]], sql_query: str, query_time: float) -> Dict[str, Any]:
        """Format query results into a standardized response"""
        try:
            def format_currency(value: float) -> str:
                if value is None or not isinstance(value, (int, float)):
                    return "MWK 0.00"
                return f"MWK {float(value):,.2f}"

            def format_percentage(value: float) -> str:
                if value is None or not isinstance(value, (int, float)):
                    return "0.0%"
                return f"{float(value):.1f}%"

            # Handle empty results
            if not query_results:
                return {
                    "status": "success",
                    "data": [],
                    "metadata": {
                        "query_time": f"{query_time:.2f}s",
                        "sql_query": sql_query
                    }
                }

            # Handle aggregate queries (COUNT, SUM, etc.)
            if len(query_results) == 1 and any(key in query_results[0] for key in ['count', 'total_budget']):
                result = query_results[0]
                if 'count' in result:
                    value = {"count": result['count']}
                else:
                    value = {"total_budget": format_currency(result['total_budget'])}
                
                return {
                    "status": "success",
                    "data": value,
                    "metadata": {
                        "query_time": f"{query_time:.2f}s",
                        "sql_query": sql_query
                    }
                }

            # Handle project listings
            formatted_results = []
            for row in query_results:
                formatted_row = {
                    "project_name": row.get('projectname', ''),
                    "location": row.get('district', ''),
                    "sector": row.get('projectsector', ''),
                    "status": row.get('projectstatus', ''),
                    "budget": format_currency(row.get('budget')),
                    "completion": format_percentage(row.get('completionpercentage'))
                }
                formatted_results.append(formatted_row)

            return {
                "status": "success",
                "data": formatted_results,
                "metadata": {
                    "query_time": f"{query_time:.2f}s",
                    "row_count": len(formatted_results),
                    "sql_query": sql_query
                }
            }

        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "metadata": {
                    "query_time": f"{query_time:.2f}s",
                    "sql_query": sql_query
                }
            }

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

    async def process_query(self, question: str) -> Dict[str, Any]:
        """Process a natural language query"""
        start_time = time.time()
        
        try:
            # Generate SQL query
            sql_query = await self.generate_sql_query(question)
            logger.info(f"Generated SQL query: {sql_query}")
            
            # Execute query with timeout
            try:
                async with asyncio.timeout(10.0):  # 10 second timeout
                    results = await self.db.execute_query(sql_query)
            except asyncio.TimeoutError:
                raise TimeoutError("Query execution timed out")
            
            # Format response
            query_time = time.time() - start_time
            return self.format_response(results, sql_query, query_time)
            
        except Exception as e:
            query_time = time.time() - start_time
            logger.error(f"Error processing query: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "metadata": {
                    "query_time": query_time,
                    "question": question
                }
            }
