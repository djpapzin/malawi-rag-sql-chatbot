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
                """Given a question about project data, write a SINGLE SQL query to answer it.
                
Table Schema (proj_dashboard):
- projectname: text
- district: text
- projectsector: text ('Infrastructure', 'Water', etc.)
- projectstatus: text
- budget: numeric (money)
- completionpercentage: numeric (0-100)
- startdate: date
- completiondata: date

Rules:
1. Return ONLY the SQL query, no explanations
2. Use lowercase column names
3. Use 'proj_dashboard' table
4. Use single quotes for strings
5. For sectors: WHERE LOWER(projectsector) = 'infrastructure'
6. For budgets: SUM(budget) as total_budget

Question: {question}

SQL Query: SELECT""")
            
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
        # Remove any markdown code block markers
        text = text.replace('```sql', '').replace('```', '')
        
        # Find the first SELECT statement
        matches = re.finditer(r'SELECT.*?;', text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            query = match.group(0)
            if query.strip():
                return query.strip()
                
        raise ValueError("No valid SQL query found in response")

    async def generate_sql_query(self, question: str) -> str:
        """Generate SQL query from natural language question"""
        try:
            # For budget queries, use direct SQL
            if 'total budget' in question.lower() and 'infrastructure' in question.lower():
                return "SELECT SUM(budget) as total_budget FROM proj_dashboard WHERE LOWER(projectsector) = 'infrastructure'"
            elif 'total budget' in question.lower():
                return "SELECT SUM(budget) as total_budget FROM proj_dashboard"
            
            # Generate SQL using LLM with timeout
            try:
                sql_chain = (
                    self.sql_prompt 
                    | self.llm 
                    | StrOutputParser()
                )
                
                response = await asyncio.wait_for(
                    sql_chain.ainvoke({"question": question}),
                    timeout=10.0  # 10 second timeout
                )
                
                logger.info(f"Raw LLM response: {response}")
                sql_query = self._extract_sql_query(response)
                logger.info(f"Extracted SQL query: {sql_query}")
                
                # Basic validation
                if not all(col in sql_query.upper() for col in ['FROM', 'PROJ_DASHBOARD']):
                    raise ValueError(f"Invalid query format: {sql_query}")
                
                return sql_query
                
            except asyncio.TimeoutError:
                logger.error("LLM request timed out, using fallback")
                raise
                
        except Exception as e:
            logger.error(f"Error generating SQL query: {str(e)}")
            # Improved fallback queries with better matching
            if 'infrastructure' in question.lower():
                if 'total budget' in question.lower():
                    return "SELECT SUM(budget) as total_budget FROM proj_dashboard WHERE LOWER(projectsector) = 'infrastructure'"
                else:
                    return "SELECT * FROM proj_dashboard WHERE LOWER(projectsector) = 'infrastructure'"
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
                raise ValueError(f"Failed to generate SQL query and no fallback available: {str(e)}")

    async def get_answer(self, question: str) -> Union[GeneralQueryResponse, SpecificQueryResponse]:
        """Get an answer for a natural language query"""
        try:
            logger.info("Generating SQL query...")
            
            # Generate SQL query
            sql_query = await self.generate_sql_query(question)
            logger.info(f"Generated SQL query: {sql_query}")
            
            # Clean up the SQL query
            sql_query = sql_query.strip().rstrip(';')
            if not sql_query.lower().strip().startswith('select'):
                logger.error(f"Invalid SQL query generated: {sql_query}")
                raise ValueError(f"Invalid SQL query generated: {sql_query}")
                
            # Execute query
            try:
                with self.db.get_connection() as conn:
                    logger.info("Executing SQL query...")
                    df = pd.read_sql_query(sql_query, conn)
                    logger.info(f"Query returned {len(df)} rows")
                    
                # Handle total budget queries
                if 'total_budget' in df.columns or 'sum(budget)' in df.columns.str.lower():
                    logger.info("Processing total budget query...")
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
                    logger.info("Processing general query...")
                    # For other queries, convert results to appropriate format
                    results = []
                    for _, row in df.iterrows():
                        try:
                            result = GeneralProjectInfo(
                                project_name=str(row.get('projectname', 'N/A')),
                                fiscal_year=str(row.get('startdate', 'N/A')),
                                location=Location(
                                    region="N/A",
                                    district=str(row.get('district', 'N/A'))
                                ),
                                total_budget=MonetaryAmount(
                                    amount=float(row.get('budget', 0) if pd.notnull(row.get('budget')) else 0),
                                    formatted=f"MWK {float(row.get('budget', 0) if pd.notnull(row.get('budget')) else 0):,.2f}"
                                ),
                                project_status=f"{float(row.get('completionpercentage', 0) if pd.notnull(row.get('completionpercentage')) else 0):.1f}% Complete",
                                project_sector=str(row.get('projectsector', 'N/A'))
                            )
                            results.append(result)
                        except Exception as e:
                            logger.error(f"Error processing row: {str(e)}")
                            continue
                    
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
