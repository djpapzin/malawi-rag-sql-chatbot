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
            logger.info(f"Processing question: '{question}'")
            
            # Generate SQL query
            sql_query = await self.generate_sql_query(question)
            logger.info(f"Generated SQL query: {sql_query}")
            
            # Execute query and measure time
            start_time = datetime.now()
            raw_results = await self.db.execute_query(sql_query)
            query_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Query result: {raw_results}")
            
            # Convert raw results to list of dicts
            if raw_results:
                if 'total_budget' in sql_query.lower():
                    # Handle total budget queries
                    results = [{'total_budget': raw_results[0][0]}]
                else:
                    # Get column names from cursor description
                    with self.db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute(sql_query)
                        columns = [desc[0] for desc in cursor.description]
                    
                    # Convert to list of dicts
                    results = []
                    for row in raw_results:
                        result_dict = {}
                        for i, value in enumerate(row):
                            result_dict[columns[i]] = value
                        results.append(result_dict)
            else:
                results = []
            
            # Format the results
            return self.format_query_results(results, query_time, sql_query)
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}\n{traceback.format_exc()}")
            raise ValueError(f"Error processing query: {str(e)}")

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

    def format_query_results(self, results: List[Dict[str, Any]], query_time: float, sql_query: str) -> Union[GeneralQueryResponse, SpecificQueryResponse]:
        """Format query results into appropriate response model"""
        try:
            # Check if this is a total budget query
            if len(results) == 1 and 'total_budget' in results[0]:
                total_budget = results[0]['total_budget'] or 0
                formatted_results = [{
                    'project_name': 'Total Budget Summary',
                    'total_budget': {
                        'amount': float(total_budget),
                        'formatted': f'MWK {total_budget:,.2f}'
                    }
                }]
                
                metadata = QueryMetadata(
                    total_results=1,
                    query_time=f"{query_time:.2f}s",
                    sql_query=sql_query
                )
                
                return GeneralQueryResponse(
                    results=formatted_results,
                    metadata=metadata
                )

            # For regular project queries
            formatted_results = []
            for row in results:
                budget = row.get('budget', 0) or 0
                completion = row.get('completionpercentage', 0) or 0
                
                budget_amount = MonetaryAmount(
                    amount=float(budget),
                    formatted=f'MWK {float(budget):,.2f}'
                )
                
                # Basic project info
                project_info = {
                    'project_name': row.get('projectname', 'Unknown'),
                    'district': row.get('district', 'Unknown'),
                    'project_sector': row.get('projectsector', 'Unknown'),
                    'project_status': row.get('projectstatus', 'Unknown'),
                    'total_budget': budget_amount.dict(),
                    'completion_percentage': float(completion)
                }
                
                # Add detailed info if available
                if 'startdate' in row:
                    project_info.update({
                        'start_date': str(row.get('startdate', 'Unknown')),
                        'completion_date': str(row.get('completiondata', 'Unknown'))
                    })
                
                formatted_results.append(project_info)
            
            metadata = QueryMetadata(
                total_results=len(results),
                query_time=f"{query_time:.2f}s",
                sql_query=sql_query
            )
            
            # Determine if this is a detailed query based on the fields present
            is_detailed = any('startdate' in row for row in results)
            
            if is_detailed:
                return SpecificQueryResponse(
                    results=formatted_results,
                    metadata=metadata
                )
            else:
                return GeneralQueryResponse(
                    results=formatted_results,
                    metadata=metadata
                )
                
        except Exception as e:
            logger.error(f"Error formatting query results: {str(e)}")
            logger.error(f"Results that caused error: {results}")
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
