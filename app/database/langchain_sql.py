from typing import Dict, List, Any, Union, Optional, Tuple
from datetime import datetime
import logging
import time
import traceback
import re
from pydantic import BaseModel, Field, ValidationError
from together import Together
from ..models import DatabaseManager
import os

logger = logging.getLogger(__name__)

class SQLQueryError(Exception):
    """Custom exception for SQL query generation errors"""
    def __init__(self, message: str, query: str = "", stage: str = "", details: Dict[str, Any] = None):
        self.message = message
        self.query = query
        self.stage = stage
        self.details = details or {}
        super().__init__(self.message)

class QueryMetadata(BaseModel):
    """Metadata about a query execution"""
    total_results: int
    query_time: str
    sql_query: str

class Budget(BaseModel):
    """Budget information"""
    amount: float
    formatted: str

class ProjectLocation(BaseModel):
    """Project location information"""
    region: Optional[str] = None
    district: Optional[str] = None

class ProjectDetails(BaseModel):
    """Common project details"""
    project_name: str
    fiscal_year: Optional[str] = None
    location: Optional[ProjectLocation] = None
    total_budget: Optional[Budget] = None
    status: Optional[str] = None
    project_sector: Optional[str] = None

class GeneralQueryResponse(BaseModel):
    """Response format for general queries"""
    results: List[ProjectDetails]
    metadata: QueryMetadata

class ContractorInfo(BaseModel):
    """Contractor information"""
    name: Optional[str] = None
    contract_start_date: Optional[str] = None

class DetailedProjectInfo(ProjectDetails):
    """Detailed project information including contractor and expenditure"""
    contractor: Optional[ContractorInfo] = None
    expenditure_to_date: Optional[Budget] = None
    source_of_funding: Optional[str] = None
    project_code: Optional[str] = None
    last_monitoring_visit: Optional[str] = None

class SpecificQueryResponse(BaseModel):
    """Response format for specific project queries"""
    results: List[DetailedProjectInfo]
    metadata: QueryMetadata

class QueryResult(BaseModel):
    """Base model for query results validation"""
    project_name: Optional[str] = Field(None, description="Name of the project")
    district: Optional[str] = Field(None, description="District where project is located")
    project_sector: Optional[str] = Field(None, description="Sector of the project")
    project_status: Optional[str] = Field(None, description="Current status of the project")
    total_budget: Optional[float] = Field(None, description="Total budget allocated")
    completion_percentage: Optional[float] = Field(None, description="Percentage of completion")
    start_date: Optional[str] = Field(None, description="Project start date")
    completion_date: Optional[str] = Field(None, description="Project completion date")

class LangChainSQLIntegration:
    """Integration with LangChain for SQL query generation"""
    
    def __init__(self):
        """Initialize the integration"""
        try:
            # Get API key and model from environment variables
            api_key = os.getenv("TOGETHER_API_KEY", "f7119711abb83c4ec5e9b2339eb06c66c87d4958f4ce6cc348ed3ad0c6cb7101")
            model = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K")
            temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
            
            # Set Together API key
            os.environ["TOGETHER_API_KEY"] = api_key
            
            # Initialize LLM
            self.llm = Together()
            
            # Initialize database manager
            self.db_manager = DatabaseManager()
            
            # Set up logging
            self.logger = logging.getLogger(__name__)
            
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
            logger.info(f"Validating SQL query: {query}")
            
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
                    logger.error(f"Dangerous pattern detected: {pattern}")
                    return False, "Invalid SQL pattern detected"

            # Required components
            if 'FROM proj_dashboard' not in query.upper() and 'from proj_dashboard' not in query.lower():
                logger.error("Missing FROM proj_dashboard clause")
                return False, "Must include FROM proj_dashboard"

            if not query.strip().upper().startswith('SELECT'):
                logger.error("Query does not start with SELECT")
                return False, "Invalid SELECT statement"

            # Validate column names
            valid_columns = {
                'projectname', 'district', 'region', 'projectsector', 'projectstatus',
                'budget', 'completionpercentage', 'startdate', 'completiondata',
                'count(*)', 'sum(budget)', 'avg(budget)', 'min(budget)', 'max(budget)',
                'total_budget', 'project_count', 'average_budget', 'total_projects',
                'sector', '*', 'type', 'message', 'greeting_message'
            }
            
            # Extract column names from query
            columns_match = re.search(r'SELECT\s+(.*?)\s+FROM', query, re.IGNORECASE | re.DOTALL)
            if not columns_match:
                logger.error("Could not extract columns from SELECT clause")
                return False, "Invalid SELECT clause"

            columns = columns_match.group(1).lower()
            logger.info(f"Extracted columns: {columns}")
            
            # Allow COUNT(*), SUM(budget), and other aggregates
            if any(x in columns.lower() for x in ['count(*)', 'sum(', 'avg(', 'min(', 'max(']):
                logger.info("Query contains aggregate functions - skipping column validation")
                return True, ""

            # For non-aggregate queries, validate individual columns
            if '*' not in columns:
                # Split columns and clean them
                query_columns = set()
                for col in columns.split(','):
                    col = col.strip().lower()
                    # Handle aliased columns
                    if ' as ' in col:
                        col = col.split(' as ')[0].strip()
                    # Handle table qualified columns
                    if '.' in col:
                        col = col.split('.')[-1].strip()
                    query_columns.add(col)
                    logger.info(f"Processed column: {col}")
                
                logger.info(f"Query columns: {query_columns}")
                invalid_columns = query_columns - valid_columns
                if invalid_columns:
                    logger.error(f"Invalid columns found: {invalid_columns}")
                    return False, f"Invalid columns: {', '.join(invalid_columns)}"

            logger.info("SQL query validation successful")
            return True, ""
            
        except Exception as e:
            logger.error(f"Error validating SQL query: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(traceback.format_exc())
            return False, str(e)

    def validate_query_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean query result data"""
        try:
            # Convert budget and completion to proper types
            if 'budget' in result:
                result['budget'] = float(result['budget'] or 0)
            if 'completionpercentage' in result:
                result['completionpercentage'] = float(result['completionpercentage'] or 0)
                
            # Validate using Pydantic model
            validated = QueryResult(
                project_name=result.get('projectname'),
                district=result.get('district'),
                project_sector=result.get('projectsector'),
                project_status=result.get('projectstatus'),
                total_budget=result.get('budget'),
                completion_percentage=result.get('completionpercentage'),
                start_date=result.get('startdate'),
                completion_date=result.get('completiondata')
            )
            return validated.dict(exclude_none=True)
            
        except ValidationError as e:
            logger.error(f"Validation error for result: {result}")
            logger.error(f"Validation error details: {e.json()}")
            raise ValueError(f"Failed to validate query result: {str(e)}")
        except Exception as e:
            logger.error(f"Error validating result: {result}")
            logger.error(f"Error details: {str(e)}")
            raise ValueError(f"Failed to process query result: {str(e)}")

    def _generate_sql_query(self, user_query: str) -> str:
        """Generate SQL query from user query"""
        try:
            # Check for greetings
            greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]
            if user_query.lower().strip() in greetings:
                return """
                    SELECT 'greeting' as type, 
                           'Welcome! I can help you query information about infrastructure projects. Try asking about:
- Total budget for all projects
- Projects in a specific district
- Projects by sector (e.g., infrastructure, education)
- Completed or active projects
- Projects with specific budget ranges' as message
                    FROM proj_dashboard LIMIT 1
                """

            # Ensure the query is not empty
            if not user_query or not user_query.strip():
                raise SQLQueryError("Query cannot be empty", query=user_query, stage="validation")

            # Handle common queries directly
            query_lower = user_query.lower()

            # District projects query
            for district in ["zomba", "lilongwe", "blantyre", "mzuzu"]:
                if district in query_lower and "projects" in query_lower:
                    sql = f"""
                        SELECT 
                            projectname,
                            district,
                            projectsector,
                            projectstatus,
                            budget,
                            completionpercentage,
                            startdate,
                            completiondata
                        FROM proj_dashboard 
                        WHERE LOWER(district) = '{district}';
                    """
                    logger.info(f"Generated district query: {sql}")
                    return sql.strip()
                    
            # Sector projects query
            for sector in ["infrastructure", "education", "healthcare", "transport"]:
                if sector in query_lower and "projects" in query_lower:
                    sql = f"""
                        SELECT projectname, district, projectsector, projectstatus, 
                               budget, completionpercentage
                        FROM proj_dashboard 
                        WHERE LOWER(projectsector) = '{sector}'
                    """
                    logger.info(f"Generated sector query: {sql}")
                    return sql
                    
            # Status based query
            for status in ["active", "completed", "on hold", "planning"]:
                if status in query_lower:
                    sql = f"""
                        SELECT 
                            projectname, district, projectsector, projectstatus, 
                            budget, completionpercentage, startdate, completiondata
                        FROM proj_dashboard 
                        WHERE LOWER(projectstatus) = '{status}'
                    """
                    logger.info(f"Generated status query: {sql}")
                    return sql
                    
            # Budget range query
            if "budget" in query_lower and any(x in query_lower for x in ["over", "above", "more than"]):
                amount = None
                for word in query_lower.split():
                    try:
                        if word.isdigit():
                            amount = int(word)
                            break
                    except Exception as e:
                        logger.warning(f"Failed to parse amount from word '{word}': {str(e)}")
                        continue
                        
                if amount:
                    sql = f"""
                        SELECT 
                            projectname, district, projectsector, projectstatus, 
                            budget, completionpercentage, startdate, completiondata
                        FROM proj_dashboard 
                        WHERE budget > {amount}
                    """
                    logger.info(f"Generated budget range query: {sql}")
                    return sql.strip()
                else:
                    raise SQLQueryError("Could not extract amount from query", 
                                      query=user_query, 
                                      stage="amount_extraction")
                    
            # Completion percentage query
            if "complete" in query_lower and any(x in query_lower for x in ["over", "above", "more than"]):
                percentage = None
                for word in query_lower.split():
                    try:
                        if word.isdigit():
                            percentage = int(word)
                            break
                    except Exception as e:
                        logger.warning(f"Failed to parse percentage from word '{word}': {str(e)}")
                        continue
                        
                if percentage:
                    sql = f"""
                        SELECT 
                            projectname, district, projectsector, projectstatus, 
                            budget, completionpercentage, startdate, completiondata
                        FROM proj_dashboard 
                        WHERE completionpercentage > {percentage}
                    """
                    logger.info(f"Generated completion query: {sql}")
                    return sql.strip()
                else:
                    raise SQLQueryError("Could not extract percentage from query", 
                                      query=user_query, 
                                      stage="percentage_extraction")
                    
            # Project count query
            if "count" in query_lower and "projects" in query_lower and "district" in query_lower:
                sql = """
                    SELECT 
                        district, 
                        COUNT(*) as project_count 
                    FROM proj_dashboard 
                    GROUP BY district
                """
                logger.info(f"Generated count query: {sql}")
                return sql
                
            # Average budget query
            if "average" in query_lower and "budget" in query_lower and "sector" in query_lower:
                sql = """
                    SELECT 
                        projectsector as sector,
                        AVG(budget) as average_budget,
                        COUNT(*) as total_projects,
                        MIN(budget) as min_budget,
                        MAX(budget) as max_budget,
                        SUM(budget) as total_budget
                    FROM proj_dashboard 
                    GROUP BY projectsector
                """
                logger.info(f"Generated average budget query: {sql}")
                return sql
                
            # Date based query
            if "starting" in query_lower or "started" in query_lower:
                year = None
                for word in query_lower.split():
                    try:
                        if word.isdigit() and len(word) == 4:
                            year = int(word)
                            break
                    except Exception as e:
                        logger.warning(f"Failed to parse year from word '{word}': {str(e)}")
                        continue
                        
                if year:
                    sql = f"""
                        SELECT 
                            projectname, district, projectsector, projectstatus, 
                            budget, completionpercentage, startdate, completiondata
                        FROM proj_dashboard 
                        WHERE strftime('%Y', startdate) = '{year}'
                    """
                    logger.info(f"Generated date query: {sql}")
                    return sql.strip()
                else:
                    raise SQLQueryError("Could not extract year from query", 
                                      query=user_query, 
                                      stage="year_extraction")

            # If no pattern matches, generate a default query
            sql = """
                SELECT 
                    projectname, district, projectsector, projectstatus,
                    budget, completionpercentage, startdate, completiondata
                FROM proj_dashboard
            """
            logger.info(f"Generated default query: {sql}")
            return sql.strip()

        except Exception as e:
            logger.error(f"Error generating SQL query: {str(e)}")
            logger.error(f"Query: {user_query}")
            logger.error(traceback.format_exc())
            raise ValueError(f"Failed to generate SQL query: {str(e)}")

    def generate_sql_query(self, user_query: str) -> str:
        """Generate SQL query from natural language input"""
        try:
            # Log input query
            logger.info(f"Generating SQL query for: {user_query}")
            
            # Ensure the query is not empty
            if not user_query or not user_query.strip():
                raise SQLQueryError("Query cannot be empty", query=user_query, stage="validation")

            # Handle common queries directly
            query_lower = user_query.lower()
            
            # Total budget query
            if "total budget" in query_lower and "all projects" in query_lower:
                sql = "SELECT SUM(budget) as total_budget FROM proj_dashboard;"
                logger.info(f"Generated total budget query: {sql}")
                return sql
                
            # Specific project queries
            # Handle project code queries (e.g., MW-CR-DO)
            project_code_match = re.search(r'(?:project\s+)?([A-Za-z]{2}-[A-Za-z]{2}-[A-Za-z0-9]{2})', user_query, re.IGNORECASE)
            if project_code_match:
                project_code = project_code_match.group(1).upper()
                sql = f"""
                    SELECT 
                        projectname, district, projectsector, projectstatus, 
                        budget, completionpercentage, startdate, completiondata
                    FROM proj_dashboard 
                    WHERE UPPER(projectcode) = '{project_code}'
                """
                logger.info(f"Generated project code query: {sql}")
                return sql

            # Handle quoted project name queries
            project_name_match = re.search(r"'([^']+)'", user_query)
            if project_name_match:
                project_name = project_name_match.group(1).strip()
                sql = f"""
                    SELECT 
                        projectname, district, projectsector, projectstatus, 
                        budget, completionpercentage, startdate, completiondata
                    FROM proj_dashboard 
                    WHERE LOWER(projectname) = LOWER('{project_name}')
                """
                logger.info(f"Generated project name query: {sql}")
                return sql
                
            # District projects query
            for district in ["zomba", "lilongwe", "blantyre", "mzuzu"]:
                if district in query_lower and "projects" in query_lower:
                    sql = f"""
                        SELECT 
                            projectname as project_name,
                            district,
                            projectsector as project_sector,
                            projectstatus as project_status,
                            budget as total_budget,
                            completionpercentage as completion_percentage,
                            startdate as start_date,
                            completiondata as completion_date
                        FROM proj_dashboard 
                        WHERE LOWER(district) = '{district}';
                    """
                    logger.info(f"Generated district query: {sql}")
                    return sql.strip()
                    
            # Sector projects query
            for sector in ["infrastructure", "education", "healthcare", "transport"]:
                if sector in query_lower and "projects" in query_lower:
                    sql = f"""
                        SELECT 
                            projectname, district, projectsector, projectstatus, 
                            budget, completionpercentage, startdate, completiondata
                        FROM proj_dashboard 
                        WHERE LOWER(projectsector) = '{sector}'
                    """
                    logger.info(f"Generated sector query: {sql}")
                    return sql
                    
            # Status based query
            for status in ["active", "completed", "on hold", "planning"]:
                if status in query_lower and "status" in query_lower:
                    sql = f"""
                        SELECT 
                            projectname, district, projectsector, projectstatus, 
                            budget, completionpercentage, startdate, completiondata
                        FROM proj_dashboard 
                        WHERE LOWER(projectstatus) = '{status}'
                    """
                    logger.info(f"Generated status query: {sql}")
                    return sql
                    
            # Budget range query
            if "budget" in query_lower and any(x in query_lower for x in ["over", "above", "more than"]):
                amount = None
                for word in query_lower.split():
                    try:
                        if word.isdigit():
                            amount = int(word)
                            break
                        elif "million" in word:
                            num = float(word.replace("million", "").strip())
                            amount = int(num * 1000000)
                            break
                    except Exception as e:
                        logger.warning(f"Failed to parse amount from word '{word}': {str(e)}")
                        continue
                        
                if amount:
                    sql = f"""
                        SELECT 
                            projectname, district, projectsector, projectstatus, 
                            budget, completionpercentage, startdate, completiondata
                        FROM proj_dashboard 
                        WHERE budget > {amount}
                    """
                    logger.info(f"Generated budget range query: {sql}")
                    return sql
                else:
                    raise SQLQueryError("Could not extract amount from query", 
                                      query=user_query, 
                                      stage="amount_extraction")
                    
            # Completion percentage query
            if "complete" in query_lower and any(x in query_lower for x in ["over", "above", "more than"]):
                percentage = None
                for word in query_lower.split():
                    try:
                        if word.isdigit():
                            percentage = int(word)
                            break
                    except Exception as e:
                        logger.warning(f"Failed to parse percentage from word '{word}': {str(e)}")
                        continue
                        
                if percentage:
                    sql = f"""
                        SELECT 
                            projectname, district, projectsector, projectstatus, 
                            budget, completionpercentage, startdate, completiondata
                        FROM proj_dashboard 
                        WHERE completionpercentage > {percentage}
                    """
                    logger.info(f"Generated completion query: {sql}")
                    return sql
                else:
                    raise SQLQueryError("Could not extract percentage from query", 
                                      query=user_query, 
                                      stage="percentage_extraction")
                    
            # Project count query
            if "count" in query_lower and "projects" in query_lower and "district" in query_lower:
                sql = """
                    SELECT 
                        district, 
                        COUNT(*) as project_count 
                    FROM proj_dashboard 
                    GROUP BY district
                """
                logger.info(f"Generated count query: {sql}")
                return sql
                
            # Average budget query
            if "average" in query_lower and "budget" in query_lower and "sector" in query_lower:
                sql = """
                    SELECT 
                        projectsector as sector,
                        AVG(budget) as average_budget,
                        COUNT(*) as total_projects,
                        MIN(budget) as min_budget,
                        MAX(budget) as max_budget,
                        SUM(budget) as total_budget
                    FROM proj_dashboard 
                    GROUP BY projectsector
                """
                logger.info(f"Generated average budget query: {sql}")
                return sql
                
            # Date based query
            if "starting" in query_lower or "started" in query_lower:
                year = None
                for word in query_lower.split():
                    try:
                        if word.isdigit() and len(word) == 4:
                            year = int(word)
                            break
                    except Exception as e:
                        logger.warning(f"Failed to parse year from word '{word}': {str(e)}")
                        continue
                        
                if year:
                    sql = f"""
                        SELECT 
                            projectname, district, projectsector, projectstatus, 
                            budget, completionpercentage, startdate, completiondata
                        FROM proj_dashboard 
                        WHERE strftime('%Y', startdate) = '{year}'
                    """
                    logger.info(f"Generated date query: {sql}")
                    return sql
                else:
                    raise SQLQueryError("Could not extract year from query", 
                                      query=user_query, 
                                      stage="year_extraction")

            # Add context about the database schema for the LLM
            schema_context = """
            You are working with a project dashboard database that has a table called 'proj_dashboard'.
            The table contains the following columns:
            - projectname: Name of the project
            - district: District where the project is located
            - projectsector: Sector of the project (e.g., infrastructure)
            - projectstatus: Current status of the project (e.g., Active, Completed)
            - budget: Total budget allocated for the project
            - completionpercentage: Percentage of project completion
            - startdate: Project start date
            - completiondata: Project completion date

            Always include 'FROM proj_dashboard' in your queries.
            For numeric comparisons with budget, convert the values to float.
            For percentage comparisons, use float values (e.g., 75 for 75%).
            """

            # Combine schema context with user query
            full_prompt = f"{schema_context}\n\nGenerate a SQL query for: {user_query}"

            # Get SQL query from LLM
            sql_query = self.llm.invoke(full_prompt)

            # Extract just the SQL query if it's wrapped in markdown or other text
            sql_query = self._extract_sql_query(sql_query)

            # Validate the query has required components
            if "FROM proj_dashboard" not in sql_query.upper():
                sql_query = sql_query.replace("FROM", "FROM proj_dashboard")
                if "FROM proj_dashboard" not in sql_query.upper():
                    raise SQLQueryError("Must include FROM proj_dashboard", 
                                      query=sql_query, 
                                      stage="table_validation")

            # Clean up the query
            sql_query = sql_query.strip().rstrip(';')

            logger.info(f"Generated SQL query: {sql_query}")
            return sql_query

        except SQLQueryError as e:
            logger.error(f"SQL Query Error: {e.message}")
            logger.error(f"Query: {e.query}")
            logger.error(f"Stage: {e.stage}")
            logger.error(f"Details: {e.details}")
            raise ValueError(f"Failed to generate SQL query: {e.message}")
        except Exception as e:
            logger.error(f"Unexpected error generating SQL query: {str(e)}")
            logger.error(f"Query: {user_query}")
            logger.error(traceback.format_exc())
            raise ValueError(f"Failed to generate SQL query: {str(e)}")

    async def get_answer(self, user_query: str) -> Dict[str, Any]:
        """Get answer for user query"""
        try:
            # Check for greetings or general queries
            greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]
            if user_query.lower().strip() in greetings:
                response = self.llm.invoke(
                    "You are a helpful assistant for a Malawi infrastructure projects database. " +
                    "The user has greeted you. Respond warmly and suggest what kinds of questions they can ask about the projects."
                )
                return {
                    "query_type": "chat",
                    "results": [{"message": response}],
                    "metadata": {
                        "total_results": 1,
                        "query_time": "0.1s",
                        "sql_query": ""
                    }
                }
            
            try:
                # Try to generate SQL query
                sql_query = self._generate_sql_query(user_query)
                logger.info(f"Generated SQL query: {sql_query}")
                
                # Execute query
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(sql_query)
                    results = [dict(row) for row in cursor.fetchall()]
                    
                # Format response
                return {
                    "query_type": "sql",
                    "results": results,
                    "metadata": {
                        "total_results": len(results),
                        "query_time": "0.1s",
                        "sql_query": sql_query
                    }
                }
            except Exception as e:
                # If SQL fails, fall back to natural language response
                logger.info(f"SQL generation failed, falling back to LLM: {str(e)}")
                prompt = f"""You are a helpful assistant for a Malawi infrastructure projects database. 
                The user asked: "{user_query}"
                The database contains information about:
                - Project names, districts, and regions
                - Project sectors (e.g., infrastructure, education)
                - Project status and completion percentages
                - Project budgets and dates
                
                I couldn't generate a valid SQL query for this. Please provide a helpful response explaining what kind of information they can ask for instead."""
                
                response = self.llm.invoke(prompt)
                return {
                    "query_type": "chat",
                    "results": [{"message": response}],
                    "metadata": {
                        "total_results": 1,
                        "query_time": "0.1s",
                        "sql_query": ""
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting answer: {str(e)}")
            logger.error(traceback.format_exc())
            raise ValueError(f"Failed to get answer: {str(e)}")

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SQL query and return the results"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
                
                # Convert results to list of dicts
                columns = [description[0] for description in cursor.description]
                results = [dict(zip(columns, row)) for row in results]
            return results
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise

    def process_query(self, question: str) -> Dict[str, Any]:
        """Process a natural language query"""
        start_time = time.time()
        
        try:
            # Generate SQL query
            sql_query = self.generate_sql_query(question)
            logger.info(f"Generated SQL query: {sql_query}")
            
            # Execute query with timeout
            try:
                results = self.execute_query(sql_query)
            except Exception as e:
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

    def format_response(self, query_results: List[Dict[str, Any]], sql_query: str, query_time: float) -> Union[GeneralQueryResponse, SpecificQueryResponse]:
        """Format query results into a standardized response"""
        try:
            # Handle empty results
            if not query_results:
                return GeneralQueryResponse(
                    results=[],
                    metadata=QueryMetadata(
                        total_results=0,
                        query_time=f"{query_time:.2f}s",
                        sql_query=sql_query
                    )
                )

            # Handle aggregate queries (COUNT, SUM, AVG)
            if len(query_results) == 1 and any(key in query_results[0] for key in ['count', 'total_budget', 'average_budget']):
                result = query_results[0]
                
                # Format the result based on type
                if 'total_budget' in result:
                    return SpecificQueryResponse(
                        results=[{
                            'total_budget': {
                                'amount': float(result['total_budget'] or 0),
                                'formatted': f"MWK {float(result['total_budget'] or 0):,.2f}"
                            }
                        }],
                        metadata=QueryMetadata(
                            total_results=1,
                            query_time=f"{query_time:.2f}s",
                            sql_query=sql_query
                        )
                    )
                elif 'average_budget' in result:
                    return SpecificQueryResponse(
                        results=[{
                            'sector': result.get('sector', 'All Sectors'),
                            'average_budget': {
                                'amount': float(result['average_budget'] or 0),
                                'formatted': f"MWK {float(result['average_budget'] or 0):,.2f}"
                            },
                            'total_projects': int(result['total_projects']),
                            'min_budget': {
                                'amount': float(result['min_budget'] or 0),
                                'formatted': f"MWK {float(result['min_budget'] or 0):,.2f}"
                            },
                            'max_budget': {
                                'amount': float(result['max_budget'] or 0),
                                'formatted': f"MWK {float(result['max_budget'] or 0):,.2f}"
                            },
                            'total_budget': {
                                'amount': float(result['total_budget'] or 0),
                                'formatted': f"MWK {float(result['total_budget'] or 0):,.2f}"
                            }
                        }],
                        metadata=QueryMetadata(
                            total_results=1,
                            query_time=f"{query_time:.2f}s",
                            sql_query=sql_query
                        )
                    )
                elif 'project_count' in result:
                    return SpecificQueryResponse(
                        results=[{
                            'district': result['district'],
                            'project_count': int(result['project_count'])
                        }],
                        metadata=QueryMetadata(
                            total_results=1,
                            query_time=f"{query_time:.2f}s",
                            sql_query=sql_query
                        )
                    )

            # Handle project listings
            formatted_results = []
            for result in query_results:
                try:
                    # Validate and clean the result
                    validated_result = self.validate_query_result(result)
                    
                    formatted_result = {
                        'project_name': validated_result['project_name'],
                        'district': validated_result['district'],
                        'project_sector': validated_result['project_sector'],
                        'project_status': validated_result['project_status'],
                        'total_budget': {
                            'amount': validated_result['total_budget'],
                            'formatted': f"MWK {validated_result['total_budget']:,.2f}"
                        },
                        'completion_percentage': validated_result['completion_percentage']
                    }
                    
                    # Add dates if available
                    if validated_result.get('start_date'):
                        formatted_result.update({
                            'start_date': validated_result['start_date'],
                            'completion_date': validated_result.get('completion_date', 'Unknown')
                        })
                        
                    formatted_results.append(formatted_result)
                except Exception as e:
                    logger.error(f"Error formatting result: {result}")
                    logger.error(f"Error details: {str(e)}")
                    continue

            return GeneralQueryResponse(
                results=formatted_results,
                metadata=QueryMetadata(
                    total_results=len(formatted_results),
                    query_time=f"{query_time:.2f}s",
                    sql_query=sql_query
                )
            )

        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            logger.error(f"Query results: {query_results}")
            logger.error(f"SQL query: {sql_query}")
            logger.error(traceback.format_exc())
            raise ValueError(f"Failed to format response: {str(e)}")

        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            logger.error(f"Query results: {query_results}")
            logger.error(f"SQL query: {sql_query}")
            logger.error(traceback.format_exc())
            raise ValueError(f"Failed to format response: {str(e)}")
