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
import asyncio

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
                max_tokens=512  # Increased token limit
            )
            
            # Set up the SQL generation prompt
            self.sql_prompt = PromptTemplate.from_template(
                """Generate a SQL query to answer this question about project data.

Table: proj_dashboard
Columns:
- projectname (text)
- district (text)
- fiscalyear (text)
- region (text)
- projectsector (text)
- status (text)
- budget (numeric)
- contractor_name (text)
- contract_start_date (text)
- expenditure_to_date (numeric)
- funding_source (text)
- project_code (text)
- last_monitoring_visit (text)

For general queries, return:
- projectname
- fiscalyear
- district
- budget
- status
- projectsector

For specific queries, return all columns.

Example Queries:
1. Total budget for all projects:
   SELECT SUM(budget) as total_budget FROM proj_dashboard;

2. Total budget for infrastructure projects:
   SELECT SUM(budget) as total_budget FROM proj_dashboard WHERE LOWER(projectsector) = 'infrastructure';

3. List all infrastructure projects (general query):
   SELECT projectname, fiscalyear, district, budget, status, projectsector 
   FROM proj_dashboard 
   WHERE LOWER(projectsector) = 'infrastructure';

4. Show project details (specific query):
   SELECT * FROM proj_dashboard WHERE projectname = 'Project Name';

Question: {question}

Return ONLY the SQL query, starting with SELECT:
SELECT""")
            
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
                    timeout=10.0  # 10 second timeout
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
                        SELECT projectname, fiscalyear, district, budget, status, projectsector 
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
                base_fields = "projectname, fiscalyear, district, budget, status, projectsector"
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
            logger.info(f"Processing question: {repr(question)}")
            
            # Generate SQL query
            sql_query = await self.generate_sql_query(question)
            logger.info(f"Generated SQL query: {sql_query}")
            
            # Execute query
            try:
                result = await self.db.execute_query(sql_query)
                logger.info(f"Query result: {result}")
                
                # Determine query type and format response
                if 'total budget' in question.lower():
                    # Format as general query response
                    total_budget = result[0][0] if result and result[0] else 0
                    return GeneralQueryResponse(
                        query_type="general",
                        results=[{
                            "project_name": "Budget Summary",
                            "fiscal_year": str(datetime.now().year),
                            "location": {
                                "region": "All",
                                "district": "All"
                            },
                            "budget": {
                                "amount": float(total_budget),
                                "formatted": f"MWK {total_budget:,.2f}"
                            },
                            "status": "N/A",
                            "project_sector": "All" if 'infrastructure' not in question.lower() else "Infrastructure"
                        }],
                        metadata=QueryMetadata(
                            total_results=1,
                            query_time=datetime.now().isoformat(),
                            sql_query=sql_query
                        )
                    )
                else:
                    # Format as specific query response for project details
                    projects = []
                    for row in result:
                        if len(row) >= 8:  # Check if we have all required fields
                            project = {
                                "project_name": row[0] if row[0] else "N/A",
                                "fiscal_year": row[2] if row[2] else "N/A",
                                "location": {
                                    "region": row[3] if len(row) > 3 and row[3] else "N/A",
                                    "district": row[1] if row[1] else "N/A"
                                },
                                "budget": {
                                    "amount": float(row[4]) if row[4] else 0,
                                    "formatted": f"MWK {float(row[4]):,.2f}" if row[4] else "N/A"
                                },
                                "status": f"{row[5]}% Complete" if row[5] else "N/A",
                                "project_sector": row[6] if row[6] else "N/A",
                                "contractor_name": row[7] if len(row) > 7 and row[7] else "N/A"
                            }
                            
                            # Add additional fields for specific queries
                            if len(row) > 8:
                                project.update({
                                    "contract_start_date": row[8] if row[8] else "N/A",
                                    "expenditure_to_date": {
                                        "amount": float(row[9]) if row[9] else 0,
                                        "formatted": f"MWK {float(row[9]):,.2f}" if row[9] else "N/A"
                                    },
                                    "sector": row[6] if row[6] else "N/A",
                                    "source_of_funding": row[10] if len(row) > 10 and row[10] else "N/A",
                                    "project_code": row[11] if len(row) > 11 and row[11] else "N/A",
                                    "last_monitoring_visit": row[12] if len(row) > 12 and row[12] else "N/A"
                                })
                            
                            projects.append(project)
                    
                    response_type = "specific" if len(row) > 8 else "general"
                    response_class = SpecificQueryResponse if response_type == "specific" else GeneralQueryResponse
                    
                    return response_class(
                        query_type=response_type,
                        results=projects,
                        metadata=QueryMetadata(
                            total_results=len(projects),
                            query_time=datetime.now().isoformat(),
                            sql_query=sql_query
                        )
                    )
                    
            except Exception as e:
                logger.error(f"Error executing SQL query: {str(e)}")
                raise ValueError(f"Error executing SQL query: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in get_answer: {str(e)}")
            raise ValueError(str(e))

    async def process_query(self, question: str) -> str:
        """Process a natural language query and return a response"""
        try:
            logger.info("Generating SQL query...")
            
            # Generate SQL query with timeout
            sql_chain = self.sql_prompt | self.llm | StrOutputParser()
            response = await sql_chain.ainvoke({"question": question})
            logger.info(f"Raw LLM response: {response}")
            sql_query = self._extract_sql_query(response)
            logger.info(f"Extracted SQL query: {sql_query}")
            
            # Clean up the SQL query
            sql_query = sql_query.strip().rstrip(';')
            if not sql_query.lower().strip().startswith('select'):
                logger.error(f"Invalid SQL query generated: {sql_query}")
                raise ValueError(f"Invalid SQL query generated: {sql_query}")
                
            # Execute query
            try:
                with self.db.get_connection() as conn:
                    df = pd.read_sql_query(sql_query, conn)
                    
                # Handle total budget queries
                if 'total_budget' in df.columns or 'sum(budget)' in df.columns.str.lower():
                    total = float(df.iloc[0][0] or 0)  # Get first value from first row
                    results = []
                    results.append(GeneralProjectInfo(
                        project_name="Total Budget Summary",
                        fiscal_year=str(datetime.now().year),
                        location=Location(
                            region="All",
                            district="All"
                        ),
                        total_budget=MonetaryAmount(
                            amount=total,
                            formatted=f"MWK {total:,.2f}"
                        ),
                        project_status="N/A",
                        project_sector="All"
                    ))
                    
                    return GeneralQueryResponse(
                        query_type="general",
                        results=results,
                        metadata=QueryMetadata(
                            total_results=1,
                            query_time=datetime.now().isoformat(),
                            sql_query=sql_query
                        )
                    )
                else:
                    # For other queries, convert results to appropriate format
                    results = []
                    for _, row in df.iterrows():
                        result = GeneralProjectInfo(
                            project_name=str(row['projectname']),
                            fiscal_year=str(row['startdate']),
                            location=Location(
                                region="N/A",
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
                            sql_query=sql_query
                        )
                    )
                    
            except Exception as e:
                logger.error(f"SQL execution error: {str(e)}")
                raise ValueError(f"Error executing SQL query: {str(e)}")
            
        except asyncio.TimeoutError:
            logger.error("LLM request timed out")
            raise TimeoutError("Request took too long to process. Please try again with a simpler query.")
        except ValueError as e:
            logger.error(f"Value error: {str(e)}")
            raise
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
