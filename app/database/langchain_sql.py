from typing import Dict, Any, Union
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
            
            # Initialize LLM
            self.llm = Together(
                model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K",
                api_key=TOGETHER_API_KEY,
                temperature=0.1,  # Lower temperature for more deterministic output
                max_tokens=512,  # Increased token limit
                request_timeout=30  # Add 30 second timeout
            )
            
            # Set up the SQL generation prompt
            self.sql_prompt = PromptTemplate.from_template(
                """Given the following question about a database, write a SQL query that would answer the question.
                The database has a table called 'proj_dashboard' with the following columns in lowercase:
                
                - projectname: Project name
                - district: District
                - projectsector: Project sector (values include: 'Infrastructure', 'Water', etc.)
                - budget: Total budget
                - completionpercentage: Completion percentage
                - startdate: Start date
                - completiondata: Completion data

IMPORTANT RULES:
                1. Use ONLY the exact column names shown above (in lowercase)
2. Always query from the 'proj_dashboard' table
3. Use single quotes for string values
                4. For sector queries, use projectsector column

EXAMPLES:
                Q: Show me all infrastructure projects
                A: SELECT * FROM proj_dashboard WHERE LOWER(projectsector) = 'infrastructure';
                
                Q: Give me details about the Mangochi Road project
                A: SELECT * FROM proj_dashboard WHERE LOWER(projectname) LIKE '%mangochi road%';
                
                Question: {question}
                
                SQL Query:"""
            )
            
            # Set up the answer generation prompt
            self.answer_prompt = PromptTemplate.from_template(
                """Given the following SQL query and its results, provide a clear and concise answer to the question.
                
                Question: {question}
                SQL Query: {query}
                Query Results: {results}
                
                Answer:"""
            )
            
            logger.info("Initialized LangChainSQLIntegration")

        except Exception as e:
            logger.error(f"Error initializing LangChainSQLIntegration: {str(e)}")
            raise

    async def generate_sql_query(self, question: str) -> str:
        """Generate SQL query from natural language question"""
        try:
            # Generate SQL using LLM
            sql_chain = (
                self.sql_prompt 
                | self.llm 
                | StrOutputParser()
            )
            
            text = await sql_chain.ainvoke({"question": question})
            logger.info(f"LLM response: {text}")
            
            # Extract SQL query from response
            sql_lines = [line for line in text.split('\n') if line.strip().upper().startswith('SELECT')]
            if not sql_lines:
                raise ValueError(f"No SQL query found in response: {text}")
                
            query = sql_lines[0].strip().rstrip(';')
            logger.info(f"Extracted query: {query}")
            
            # Basic validation
            if not all(col in query.upper() for col in ['FROM', 'PROJ_DASHBOARD']):
                raise ValueError(f"Invalid query format: {query}")
            
            return query
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {str(e)}")
            # Improved fallback queries with better matching
            if 'infrastructure' in question.lower():
                return "SELECT * FROM proj_dashboard WHERE LOWER(projectsector) = 'infrastructure'"
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
                raise ValueError(f"Failed to generate SQL query and no fallback available: {str(e)}")

    async def get_answer(self, question: str) -> Union[GeneralQueryResponse, SpecificQueryResponse]:
        """Get answer for a question using SQL"""
        try:
            # Generate SQL query
            logger.info("Generating SQL query...")
            query = await self.generate_sql_query(question)
            logger.info(f"Generated query: {query}")
            
            # Execute query and get results
            logger.info("Executing query...")
            with self.db.get_connection() as conn:
                df = pd.read_sql_query(query, conn)
            logger.info(f"Query returned {len(df)} rows")
            
            # Determine if this is a general or specific query
            is_specific = any(word in question.lower() for word in ["details", "specific", "about"])
            logger.info(f"Query type: {'specific' if is_specific else 'general'}")
            
            # Format results according to query type
            if is_specific:
                results = []
                for _, row in df.iterrows():
                    result = DetailedProjectInfo(
                        project_name=str(row['projectname']),
                        fiscal_year=str(row['startdate']),  # Using startdate as fiscal year
                        location=Location(
                            region="N/A",  # Region not in schema
                            district=str(row['district'])
                        ),
                        total_budget=MonetaryAmount(
                            amount=float(row['budget'] if pd.notnull(row['budget']) else 0),
                            formatted=f"MWK {float(row['budget'] if pd.notnull(row['budget']) else 0):,.2f}"
                        ),
                        project_status=f"{float(row['completionpercentage'] if pd.notnull(row['completionpercentage']) else 0):.1f}% Complete",
                        project_sector=str(row['projectsector']),
                        contractor=Contractor(
                            name="N/A",  # Not in schema
                            contract_start_date=str(row['startdate'])
                        ),
                        expenditure_to_date=MonetaryAmount(
                            amount=0,  # Not in schema
                            formatted="MWK 0.00"
                        ),
                        source_of_funding="N/A",  # Not in schema
                        project_code="N/A",  # Not in schema
                        last_monitoring_visit="N/A"  # Not in schema
                    )
                    results.append(result)
                
                return SpecificQueryResponse(
                    query_type="specific",
                    results=results,
                    metadata=QueryMetadata(
                        total_results=len(results),
                        query_time=datetime.now().isoformat(),
                        sql_query=query
                    )
                )
            else:
                results = []
                for _, row in df.iterrows():
                    result = GeneralProjectInfo(
                        project_name=str(row['projectname']),
                        fiscal_year=str(row['startdate']),  # Using startdate as fiscal year
                        location=Location(
                            region="N/A",  # Region not in schema
                            district=str(row['district'])
                        ),
                        total_budget=MonetaryAmount(
                            amount=float(row['budget'] if pd.notnull(row['budget']) else 0),
                            formatted=f"MWK {float(row['budget'] if pd.notnull(row['budget']) else 0):,.2f}"
                        ),
                        project_status=f"{float(row['completionpercentage'] if pd.notnull(row['completionpercentage']) else 0):.1f}% Complete",
                        project_sector=str(row['projectsector'])
                    )
                    results.append(result)
                
                return GeneralQueryResponse(
                    query_type="general",
                    results=results,
                    metadata=QueryMetadata(
                        total_results=len(results),
                        query_time=datetime.now().isoformat(),
                        sql_query=query
                    )
                )
            
        except Exception as e:
            logger.error(f"Error getting answer: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise ValueError(f"Failed to get answer: {str(e)}")

    async def process_query(self, question: str) -> str:
        """Process a natural language query and return a response"""
        try:
            logger.info("Generating SQL query...")
            
            # Generate SQL query
            sql_chain = self.sql_prompt | self.llm | StrOutputParser()
            sql_query = await sql_chain.ainvoke({"question": question})
            
            logger.info(f"Generated SQL query: {sql_query}")
            
            # Execute query
            with self.db.get_connection() as conn:
                df = pd.read_sql_query(sql_query, conn)
            
            # Convert results to string format
            results = df.to_string() if not df.empty else "No results found"
            
            # Generate natural language answer
            answer_chain = self.answer_prompt | self.llm | StrOutputParser()
            answer = await answer_chain.ainvoke({
                "question": question,
                "query": sql_query,
                "results": results
            })
            
            return answer
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}\n{traceback.format_exc()}")
            raise ValueError(f"Error processing query: {str(e)}")

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
