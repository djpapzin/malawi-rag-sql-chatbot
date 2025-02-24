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
                max_tokens=128  # Limit tokens to prevent long explanations
            )
            
            # Set up the SQL generation prompt
            self.sql_prompt = PromptTemplate.from_template(
                """Given the following question about a database, write a SQL query that would answer the question.
                The database has a table called 'proj_dashboard' with the following columns in UPPERCASE:
                
                - PROJECTNAME: Project name
                - FISCALYEAR: Fiscal year
                - REGION: Region
                - DISTRICT: District
                - TOTALBUDGET: Total budget
                - PROJECTSTATUS: Project status
                - PROJECTSECTOR: Project sector
                - CONTRACTORNAME: Contractor name
                - CONTRACTSTARTDATE: Contract start date
                - EXPENDITURETODATE: Expenditure to date
                - SOURCEOFFUNDING: Source of funding
                - PROJECTCODE: Project code
                - LASTMONITORINGVISIT: Last monitoring visit
                
                EXAMPLES:
                Q: Show me all infrastructure projects
                A: SELECT * FROM proj_dashboard WHERE UPPER(PROJECTSECTOR) = 'INFRASTRUCTURE';
                
                Q: Give me details about the Mangochi Road project
                A: SELECT * FROM proj_dashboard WHERE PROJECTNAME LIKE '%Mangochi Road%';
                
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

    def generate_sql_query(self, question: str) -> str:
        """Generate SQL query from natural language question"""
        try:
            # Generate SQL using LLM
            chain = (
                self.sql_prompt 
                | self.llm 
                | StrOutputParser()
            )
            
            text = chain.invoke({"question": question})
            
            # Extract SQL query from response
            sql_lines = [line for line in text.split('\n') if line.strip().upper().startswith('SELECT')]
            if not sql_lines:
                raise ValueError(f"No SQL query found in response: {text}")
                
            query = sql_lines[0].strip().rstrip(';')
            logger.info(f"Extracted query: {query}")
            
            return query
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {str(e)}")
            raise ValueError(f"Failed to generate SQL query: {str(e)}")

    def get_answer(self, question: str) -> Union[GeneralQueryResponse, SpecificQueryResponse]:
        """Get answer for a question using SQL"""
        try:
            # Generate SQL query
            logger.info("Generating SQL query...")
            query = self.generate_sql_query(question)
            logger.info(f"Generated query: {query}")
            
            # Execute query and get results
            logger.info("Executing query...")
            with self.db.get_connection() as conn:
                df = pd.read_sql_query(query, conn)
            logger.info(f"Query returned {len(df)} rows")
            logger.info(f"DataFrame columns: {df.columns.tolist()}")
            
            # Determine if this is a general or specific query
            is_specific = any(word in question.lower() for word in ["details", "specific", "about"])
            logger.info(f"Query type: {'specific' if is_specific else 'general'}")
            
            # Format results according to query type
            if is_specific:
                logger.info("Processing specific query results...")
                results = []
                for _, row in df.iterrows():
                    try:
                        result = DetailedProjectInfo(
                            project_name=str(row['PROJECTNAME']),
                            fiscal_year=str(row['FISCALYEAR']),
                            location=Location(
                                region=str(row['REGION']),
                                district=str(row['DISTRICT'])
                            ),
                            total_budget=MonetaryAmount(
                                amount=float(row['TOTALBUDGET'] if pd.notnull(row['TOTALBUDGET']) else 0),
                                formatted=f"MWK {float(row['TOTALBUDGET'] if pd.notnull(row['TOTALBUDGET']) else 0):,.2f}"
                            ),
                            project_status=str(row['PROJECTSTATUS']),
                            project_sector=str(row['PROJECTSECTOR']),
                            contractor=Contractor(
                                name=str(row['CONTRACTORNAME'] if pd.notnull(row['CONTRACTORNAME']) else 'N/A'),
                                contract_start_date=str(row['CONTRACTSTARTDATE'] if pd.notnull(row['CONTRACTSTARTDATE']) else 'N/A')
                            ),
                            expenditure_to_date=MonetaryAmount(
                                amount=float(row['EXPENDITURETODATE'] if pd.notnull(row['EXPENDITURETODATE']) else 0),
                                formatted=f"MWK {float(row['EXPENDITURETODATE'] if pd.notnull(row['EXPENDITURETODATE']) else 0):,.2f}"
                            ),
                            source_of_funding=str(row['SOURCEOFFUNDING'] if pd.notnull(row['SOURCEOFFUNDING']) else 'N/A'),
                            project_code=str(row['PROJECTCODE'] if pd.notnull(row['PROJECTCODE']) else 'N/A'),
                            last_monitoring_visit=str(row['LASTMONITORINGVISIT'] if pd.notnull(row['LASTMONITORINGVISIT']) else 'N/A')
                        )
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Error processing row: {row}")
                        logger.error(f"Error details: {str(e)}")
                        continue
                
                return SpecificQueryResponse(
                    results=results,
                    metadata=QueryMetadata(
                        total_results=len(results),
                        query_time=datetime.now().isoformat(),
                        sql_query=query
                    )
                )
            else:
                logger.info("Processing general query results...")
                results = []
                for _, row in df.iterrows():
                    try:
                        result = GeneralProjectInfo(
                            project_name=str(row['PROJECTNAME']),
                            fiscal_year=str(row['FISCALYEAR']),
                            location=Location(
                                region=str(row['REGION']),
                                district=str(row['DISTRICT'])
                            ),
                            total_budget=MonetaryAmount(
                                amount=float(row['TOTALBUDGET'] if pd.notnull(row['TOTALBUDGET']) else 0),
                                formatted=f"MWK {float(row['TOTALBUDGET'] if pd.notnull(row['TOTALBUDGET']) else 0):,.2f}"
                            ),
                            project_status=str(row['PROJECTSTATUS']),
                            project_sector=str(row['PROJECTSECTOR'])
                        )
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Error processing row: {row}")
                        logger.error(f"Error details: {str(e)}")
                        continue
                
                return GeneralQueryResponse(
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
