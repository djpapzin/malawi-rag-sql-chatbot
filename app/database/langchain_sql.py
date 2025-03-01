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
import json
import sqlite3

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
            # Get model from environment variables
            model = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K")
            temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
            
            # Get API key from environment
            api_key = os.getenv("TOGETHER_API_KEY", "f7119711abb83c4ec5e9b2339eb06c66c87d4958f4ce6cc348ed3ad0c6cb7101")
            
            # Set the API key directly
            import together
            together.api_key = api_key
            
            # Initialize Together client
            self.client = Together()
            self.model = model
            self.temperature = temperature
            
            # Initialize database manager
            self.db_manager = DatabaseManager()
            
            # Test the API connection
            models = self.client.models.list()
            logger.info("Available Together models: %s", [m['name'] for m in models])
            logger.info("Using model: %s", self.model)
            logger.info("Successfully initialized Together API client")
            
        except Exception as e:
            logger.error(f"Error initializing LangChainSQLIntegration: {str(e)}")
            raise

    async def _extract_sql_from_text(self, text: str) -> str:
        """Extract SQL query from LLM response"""
        logger.info(f"Extracting SQL from text: {repr(text)}")
        
        # Try to extract SQL query using regex patterns
        patterns = [
            r"```sql\s*(.*?)\s*```",  # SQL code block
            r"```\s*(SELECT.*?;)\s*```",  # Generic code block with SELECT
            r"SELECT.*?;",  # Just the SQL query
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            logger.info(f"Pattern {pattern} matches: {matches}")
            if matches:
                sql_query = matches[0].strip()
                logger.info(f"Extracted SQL query: {repr(sql_query)}")
                return sql_query
        
        # If no pattern matches, check if the text itself is a SQL query
        if text.strip().upper().startswith("SELECT") and ";" in text:
            sql_query = text.strip()
            logger.info(f"Text itself is a SQL query: {repr(sql_query)}")
            return sql_query
            
        logger.error(f"Failed to extract SQL query from text: {repr(text)}")
        return ""

    async def _get_llm_response(self, prompt: str) -> str:
        """Get response from LLM using Together API"""
        try:
            import together
            logger.info(f"Sending prompt to LLM: {repr(prompt)}")
            
            # Use the Together API directly with the completion endpoint
            response = together.Complete.create(
                prompt=prompt,
                model=self.model,
                max_tokens=1024,
                temperature=self.temperature,
                top_k=50,
                top_p=0.7,
                repetition_penalty=1.1
            )
            
            # Extract the raw text from the response
            raw_text = response['output']['choices'][0]['text']
            logger.info(f"Raw LLM response: {repr(raw_text)}")
            
            # For intent detection, just return the raw text
            if "Respond with just one word: GREETING, GENERAL, SQL, or OTHER" in prompt:
                # Clean up and extract just the intent word
                intent = raw_text.strip().upper()
                # Return the first matching intent found
                for word in ["GREETING", "GENERAL", "SQL", "OTHER"]:
                    if word in intent:
                        return word
                # If no intent found in the response, try to detect from common patterns
                if re.search(r'\b(hi|hello|hey|greetings|howdy)\b', prompt.lower()):
                    return "GREETING"
                if re.search(r'\b(what|how|tell me about|explain|help|can you|able to)\b', prompt.lower()):
                    return "GENERAL"
                return "OTHER"  # Default to OTHER if no valid intent found
            
            # For greeting responses
            if "The user has greeted you" in prompt:
                return """Hello! I'm here to help you with information about Malawi infrastructure projects. You can ask me about:

- Project details in specific districts
- Project budgets and costs
- Completion status and timelines
- Project sectors and types

What would you like to know about?"""
                
            # For general questions about capabilities
            if "The user wants to know what kind of information they can query" in prompt:
                return """I can help you find information about infrastructure projects in Malawi. Here are some things you can ask about:

1. Project Information:
   - Projects in specific districts
   - Project sectors (Education, Infrastructure, etc.)
   - Project status and completion rates

2. Financial Information:
   - Project budgets
   - Get total budgets by district/sector
   - Compare project costs

3. Progress Tracking:
   - Find active/completed projects
   - Check project timelines
   - View completion rates

Just ask me what you'd like to know about these projects!"""
            
            # For SQL queries, try to extract just the explanation
            if "Provide a brief, natural language explanation of these results" in prompt:
                # Try to find a natural language explanation
                import re
                explanation_matches = re.search(r'explanation of (these|the) results[.:]?\s*(.*?)(?:$|"""|\n\n)', raw_text, re.DOTALL | re.IGNORECASE)
                if explanation_matches:
                    return explanation_matches.group(2).strip()
                return "Here are the results from the database based on your query."
            
            # For other queries
            if "This seems to be an unsupported type of query" in prompt:
                return """I can help you with information about Malawi infrastructure projects. You can ask me about:
                - Project information (names, locations, sectors)
                - Financial data (budgets, costs)
                - Status updates (completion %, timelines)
                - Statistics and analytics
                
                Please ask me a question related to these topics, and I'll do my best to assist you!"""
                
            # For SQL generation, return the raw text
            if "Generate a SQL query" in prompt:
                cleaned_text = raw_text.strip()
                logger.info(f"Cleaned SQL query: {repr(cleaned_text)}")
                return cleaned_text
            
            # Default case: clean up the response
            import re
            cleaned_text = re.sub(r'```.*?```', '', raw_text, flags=re.DOTALL)
            cleaned_text = re.sub(r'""".*?"""', '', cleaned_text, flags=re.DOTALL)
            
            # If we still have a substantial response, return it
            if len(cleaned_text.strip()) > 20:
                return cleaned_text.strip()
                
            # Last resort fallback
            return "I'm here to help with information about Malawi infrastructure projects. Please ask me about specific projects, budgets, locations, or other project details."
            
        except Exception as e:
            logger.error(f"Error getting LLM response: {str(e)}")
            raise Exception(f"Failed to get answer: {str(e)}")

    async def _validate_sql_query(self, sql_query: str) -> str:
        """Validate a SQL query"""
        try:
            # Basic validation
            if not sql_query or not isinstance(sql_query, str):
                raise ValueError("Invalid SQL query")
                
            # Check for malicious SQL
            malicious_patterns = [
                "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE",
                "GRANT", "REVOKE", "--", ";--", "/*", "*/", "@@", "@", "char",
                "nchar", "varchar", "nvarchar", "exec", "execute", "cursor",
                "declare", "xp_", "sp_", "msdb", "cmdshell", "writetext"
            ]
            for pattern in malicious_patterns:
                if pattern.lower() in sql_query.lower():
                    raise ValueError(f"SQL query contains forbidden pattern: {pattern}")
                    
            # Check for valid SELECT statement
            if not sql_query.strip().lower().startswith("select"):
                raise ValueError("SQL query must start with SELECT")
                
            # Ensure query ends with semicolon
            if not sql_query.strip().endswith(";"):
                sql_query = sql_query.strip() + ";"
                
            # Check for aggregate functions
            aggregate_functions = ["sum(", "count(", "avg(", "min(", "max("]
            has_aggregate = any(func in sql_query.lower() for func in aggregate_functions)
            
            if has_aggregate:
                # Check for COALESCE around numeric aggregates
                if "sum(" in sql_query.lower() and "coalesce(sum(" not in sql_query.lower():
                    sql_query = sql_query.replace("sum(", "COALESCE(SUM(")
                    sql_query = sql_query.replace(")", ", 0)")
                if "avg(" in sql_query.lower() and "coalesce(avg(" not in sql_query.lower():
                    sql_query = sql_query.replace("avg(", "COALESCE(AVG(")
                    sql_query = sql_query.replace(")", ", 0)")
                    
            return sql_query
            
        except Exception as e:
            logger.error(f"Error validating SQL query: {str(e)}")
            logger.error(f"Query: {sql_query}")
            raise SQLQueryError(str(e), sql_query)

    def _get_infrastructure_budget_query(self) -> str:
        """Get SQL query for infrastructure budget"""
        return """
        SELECT 
            COALESCE(SUM(budget), 0) as total_budget,
            COUNT(*) as project_count,
            'Infrastructure' as sector
        FROM proj_dashboard 
        WHERE LOWER(projectsector) LIKE '%infrastructure%';
        """.strip()

    def _get_basic_project_query(self, district: str = None, status: str = None) -> str:
        """Get SQL query for basic project information"""
        conditions = []
        if district:
            conditions.append(f"LOWER(district) = '{district.lower()}'")
        if status:
            conditions.append(f"LOWER(projectstatus) = '{status.lower()}'")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        return f"""
        SELECT 
            projectname as project_name,
            district,
            projectsector as project_sector,
            projectstatus as project_status,
            COALESCE(budget, 0) as total_budget,
            COALESCE(completionpercentage, 0) as completion_percentage
        FROM proj_dashboard 
        WHERE {where_clause}
        ORDER BY total_budget DESC;
        """.strip()

    async def generate_sql_query(self, user_query: str) -> str:
        """Generate a SQL query from a natural language query"""
        try:
            # Check for specific project queries
            project_name_patterns = [
                r"tell me about ['\"](.+?)['\"]",
                r"details? (?:for|about) ['\"](.+?)['\"]",
                r"information (?:for|about) ['\"](.+?)['\"]",
                r"show me ['\"](.+?)['\"]",
                r"what (?:is|are) ['\"](.+?)['\"]",
                # Additional patterns without quotes
                r"tell me about (?:the )?project (?:called |named )?(.+?)(?:\s|$|\.)",
                r"details? (?:for|about) (?:the )?project (?:called |named )?(.+?)(?:\s|$|\.)",
                r"information (?:for|about) (?:the )?project (?:called |named )?(.+?)(?:\s|$|\.)",
                r"show me (?:the )?project (?:called |named )?(.+?)(?:\s|$|\.)"
            ]
            
            for pattern in project_name_patterns:
                match = re.search(pattern, user_query.lower())
                if match:
                    project_name = match.group(1)
                    logger.info(f"Detected specific project query for: {project_name}")
                    return f"""
                    SELECT 
                        projectname as project_name,
                        district,
                        projectsector as project_sector,
                        projectstatus as project_status,
                        COALESCE(budget, 0) as total_budget,
                        COALESCE(completionpercentage, 0) as completion_percentage,
                        startdate,
                        completiondata as completion_date
                    FROM proj_dashboard 
                    WHERE LOWER(projectname) LIKE '%{project_name.lower().replace("'", "''")}%'
                    LIMIT 1;
                    """
            
            # Handle infrastructure budget query
            if "infrastructure" in user_query.lower() and any(word in user_query.lower() for word in ["budget", "cost", "amount", "total"]):
                return self._get_infrastructure_budget_query()
            
            # Handle basic project queries
            if "lilongwe" in user_query.lower():
                return self._get_basic_project_query(district="lilongwe")
            if "completed" in user_query.lower() or "status" in user_query.lower():
                return self._get_basic_project_query(status="completed")
            
            # Check if this is an aggregate query
            is_aggregate = self._is_aggregate_query(user_query)
            
            # Get table info
            table_info = self._get_table_info()
            
            # Prepare prompt based on query type
            if is_aggregate:
                prompt = f"""Generate a SQL query for this question about Malawi infrastructure projects:
{user_query}

Important rules:
1. ALWAYS use COALESCE for numeric aggregates:
   - COALESCE(SUM(budget), 0) as total_budget
   - COALESCE(AVG(budget), 0) as avg_budget
   - COUNT(*) for counting records
2. For sector filtering, use: LOWER(projectsector) LIKE '%keyword%'
3. For status filtering, use: LOWER(projectstatus) = 'status'
4. Return ONLY the SQL query, no explanations

Example query for total infrastructure budget:
SELECT COALESCE(SUM(budget), 0) as total_budget 
FROM proj_dashboard 
WHERE LOWER(projectsector) LIKE '%infrastructure%';"""
            else:
                prompt = f"""Generate a SQL query for this question about Malawi infrastructure projects:
{user_query}

Important rules:
1. ALWAYS use COALESCE for numeric fields:
   - COALESCE(budget, 0) as total_budget
   - COALESCE(completionpercentage, 0) as completion_percentage
2. For text matching, use LIKE with wildcards
3. Return ONLY the SQL query, no explanations

Example query for infrastructure projects:
SELECT 
    projectname as project_name,
    district,
    projectsector as project_sector,
    projectstatus as project_status,
    COALESCE(budget, 0) as total_budget,
    COALESCE(completionpercentage, 0) as completion_percentage
FROM proj_dashboard 
WHERE LOWER(projectsector) LIKE '%infrastructure%'
ORDER BY total_budget DESC;"""
            
            # Get SQL query from LLM
            sql_query = await self._get_llm_response(prompt)
            
            # Extract SQL if needed
            if not sql_query.lower().startswith('select'):
                sql_query = await self._extract_sql_from_text(sql_query)
            
            # Validate and transform query
            sql_query = await self._validate_sql_query(sql_query)
            
            return sql_query
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SQL query and return the results"""
        try:
            logger.info(f"Executing query: {query}")
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                
                # Get column names from cursor description
                columns = [description[0] for description in cursor.description]
                logger.debug(f"Query columns: {columns}")
                
                # Fetch results and convert to list of dictionaries
                rows = cursor.fetchall()
                logger.debug(f"Raw rows: {rows}")
                
                results = []
                for row in rows:
                    # Handle both sqlite3.Row and regular tuple results
                    if isinstance(row, sqlite3.Row):
                        results.append(dict(row))
                    else:
                        results.append(dict(zip(columns, row)))
                
                logger.info(f"Query returned {len(results)} results")
                if results:
                    logger.debug(f"First result: {results[0]}")
                return results
                
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(traceback.format_exc())
            raise

    async def get_answer(self, user_query: str) -> Dict[str, Any]:
        """Get answer for user query"""
        try:
            # First, detect query intent
            intent_prompt = """You are an expert at understanding user intent for a Malawi infrastructure projects database. The database contains ONLY the following information:
            - Project names and locations (districts)
            - Project sectors (Infrastructure, Education, etc.)
            - Project status (Active, Completed, etc.)
            - Project budgets and completion percentages
            - Project start and completion dates

            Given this user query, determine if it is:
            1. A GREETING (e.g., hello, hi, hey)
            2. A GENERAL QUESTION about what the system can do
            3. A SPECIFIC QUESTION about projects that needs SQL (ONLY if it asks about data we actually have)
            4. OTHER (if it asks about data we don't have, like ages, names of people, etc.)
            
            Respond with just one word: GREETING, GENERAL, SQL, or OTHER.
            
            User query: {query}"""
            
            # First try LLM-based intent detection
            intent = await self._get_llm_response(intent_prompt.format(query=user_query)).strip().upper()
            logger.info(f"LLM detected intent: {intent} for query: {user_query}")
            
            # If no clear intent, try pattern matching
            if intent not in ["GREETING", "GENERAL", "SQL", "OTHER"]:
                if re.search(r'\b(hi|hello|hey|greetings|howdy)\b', user_query.lower()):
                    intent = "GREETING"
                elif re.search(r'\b(what|how|tell me about|explain|help|can you|able to)\b', user_query.lower()):
                    intent = "GENERAL"
                else:
                    intent = "OTHER"
                logger.info(f"Pattern matching detected intent: {intent}")
            
            # Handle greetings
            if intent == "GREETING":
                greeting_prompt = """You are a helpful assistant for a Malawi infrastructure projects database. Respond warmly and suggest what kinds of questions they can ask about the projects. For example:
                - Ask about projects in specific districts
                - Query project budgets and costs
                - Find projects by sector (Infrastructure, Education, etc.)
                - Get statistics about project completion rates
                
                The user has greeted you. Respond warmly and provide these suggestions."""
                
                response = await self._get_llm_response(greeting_prompt)
                return {
                    "response": {
                        "query_type": "chat",
                        "results": [{"type": "greeting", "message": response}],
                        "metadata": {
                            "total_results": 1,
                            "query_time": "0.1s",
                            "sql_query": ""
                        }
                    }
                }
            
            # Handle general questions about system capabilities
            if intent == "GENERAL":
                capabilities_prompt = """You are a helpful assistant for a Malawi infrastructure projects database. The user wants to know what kind of information they can query. Explain the following capabilities:
                
                1. Project Information:
                   - Search by project name or district
                   - View project sectors and status
                   - Check completion percentages
                   
                2. Financial Data:
                   - Query project budgets
                   - Get total budgets by district/sector
                   - Compare project costs
                   
                3. Status and Progress:
                   - Find active/completed projects
                   - Check project timelines
                   - View completion rates
                   
                4. Analytics:
                   - Get project counts by district
                   - Calculate average budgets
                   - Find largest/smallest projects
                
                The user asked: {query}
                Provide a helpful response about these capabilities.""".format(query=user_query)
                
                response = await self._get_llm_response(capabilities_prompt)
                return {
                    "response": {
                        "query_type": "chat",
                        "results": [{"type": "help", "message": response}],
                        "metadata": {
                            "total_results": 1,
                            "query_time": "0.1s",
                            "sql_query": ""
                        }
                    }
                }
            
            # Handle SQL queries
            if intent == "SQL":
                try:
                    # Generate and execute SQL query
                    sql_query = await self.generate_sql_query(user_query)
                    logger.info(f"Generated SQL query: {sql_query}")
                    
                    with self.db_manager.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute(sql_query)
                        results = [dict(row) for row in cursor.fetchall()]
                        
                    # Get a natural language explanation of the results
                    explanation_prompt = f"""You are a helpful assistant for Malawi infrastructure projects. 
                    The user asked: "{user_query}"
                    The query returned {len(results)} results.
                    
                    First result: {str(results[0]) if results else 'No results'}
                    
                    Provide a brief, natural language explanation of these results."""
                    
                    explanation = await self._get_llm_response(explanation_prompt)
                    
                    return {
                        "response": {
                            "query_type": "sql",
                            "results": results,
                            "explanation": explanation,
                            "metadata": {
                                "total_results": len(results),
                                "query_time": "0.1s",
                                "sql_query": sql_query
                            }
                        }
                    }
                except Exception as e:
                    logger.error(f"SQL generation/execution failed: {str(e)}")
                    raise
            
            # Handle other types of queries
            response = await self._get_llm_response(
                f"""You are a helpful assistant for Malawi infrastructure projects database. 
                The user asked: "{user_query}"
                This seems to be an unsupported type of query. Explain what kinds of questions they can ask instead, focusing on:
                - Project information (names, locations, sectors)
                - Financial data (budgets, costs)
                - Status updates (completion %, timelines)
                - Statistics and analytics
                
                Provide a helpful response."""
            )
            
            return {
                "response": {
                    "query_type": "chat",
                    "results": [{"type": "other", "message": response}],
                    "metadata": {
                        "total_results": 1,
                        "query_time": "0.1s",
                        "sql_query": ""
                    }
                }
            }
                
        except Exception as e:
            logger.error(f"Error getting answer: {str(e)}")
            logger.error(traceback.format_exc())
            raise ValueError(f"Failed to get answer: {str(e)}")

    async def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process a natural language query"""
        try:
            # Check if it's a greeting
            if self._is_greeting_or_general(user_query):
                return {
                    "results": [{
                        "type": "text",
                        "message": get_greeting_response(),
                        "data": {}
                    }],
                    "metadata": {
                        "total_results": 1,
                        "query_time": "0.00s",
                        "sql_query": ""
                    }
                }

            # Start timing
            start_time = time.time()
            
            # Generate SQL query
            sql_query = await self.generate_sql_query(user_query)
            logger.info(f"Generated SQL query: {sql_query}")
            
            # Execute query
            results = self.execute_query(sql_query)
            logger.info(f"Query results: {results}")
            
            # Calculate query time
            query_time = time.time() - start_time
            
            # Format response
            return await self.format_response(results, sql_query, query_time, user_query)
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "results": [{
                    "type": "error",
                    "message": str(e),
                    "data": {}
                }],
                "metadata": {
                    "total_results": 0,
                    "query_time": "0.00s",
                    "sql_query": ""
                }
            }

    async def generate_natural_response(self, results: List[Dict[str, Any]], user_query: str, sql_query: str = None) -> str:
        """Generate a natural language response from query results."""
        try:
            logger.info(f"Generating natural response for user query: {user_query}")
            
            # Convert results to string format for the prompt
            results_str = json.dumps(results, indent=2)
            
            # Check if this is an aggregate query
            is_aggregate = self._is_aggregate_query(user_query)
            
            # Prepare prompt based on query type
            if is_aggregate:
                prompt = f"""Given these query results about Malawi infrastructure projects:
{results_str}

The user asked: "{user_query}"

Generate a natural language response that:
1. States the aggregated values clearly (total budget, average, count etc.)
2. Uses proper currency formatting (MWK with commas)
3. Provides context about what was calculated
4. Handles cases where values are 0 or not available
5. Is concise but informative

Example responses:
- "The total budget for infrastructure projects is MWK 1,234,567.00"
- "I found 15 completed projects with a total budget of MWK 987,654.00"

Response:"""
            else:
                prompt = f"""Given these query results about Malawi infrastructure projects:
{results_str}

The user asked: "{user_query}"

Generate a natural language response that:
1. Summarizes the key information
2. Uses proper formatting for currency (MWK with commas)
3. Is concise but informative
4. Maintains a helpful and professional tone

Example responses:
- "I found 5 projects in Lilongwe with a total budget of MWK 1,234,567.00"
- "There are 3 education projects, with budgets ranging from MWK 100,000.00 to MWK 500,000.00"

Response:"""
            
            # Generate response
            response = await self._get_llm_response(prompt)
            
            # Clean up response
            response = response.strip()
            
            # Remove code blocks and technical notes
            response = self._clean_llm_response(response)
            
            # Handle empty response
            if not response:
                if not results:
                    return "I found no matching projects in the database."
                else:
                    total_budget = sum(float(r.get('total_budget', 0)) for r in results)
                    return f"I found {len(results)} matching projects with a total budget of MWK {total_budget:,.2f}."
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating natural response: {str(e)}")
            logger.error(traceback.format_exc())
            if results and len(results) > 0:
                total_budget = sum(float(r.get('total_budget', 0)) for r in results)
                return f"I found {len(results)} matching projects with a total budget of MWK {total_budget:,.2f}."
            return "I found some matching projects in the database."
            
    async def format_response(self, query_results: List[Dict[str, Any]], sql_query: str, query_time: float, user_query: str) -> Dict[str, Any]:
        """Format query results into a standardized response with natural language."""
        try:
            if not query_results:
                return {
                    "results": [{
                        "type": "text",
                        "message": "No matching projects found. Please try different search terms.",
                        "data": {}
                    }],
                    "metadata": {
                        "total_results": 0,
                        "query_time": f"{query_time:.2f}s",
                        "sql_query": sql_query
                    }
                }
                
            natural_response = await self.generate_natural_response(query_results, user_query, sql_query)
            
            return {
                "results": [{
                    "type": "text",
                    "message": natural_response,
                    "data": query_results[0] if len(query_results) == 1 else {}
                }],
                "metadata": {
                    "total_results": len(query_results),
                    "query_time": f"{query_time:.2f}s",
                    "sql_query": sql_query
                }
            }
            
        except Exception as e:
            logger.error(f"Formatting error: {str(e)}")
            return {
                "results": [{
                    "type": "error",
                    "message": "Couldn't format response - please try again",
                    "data": {}
                }],
                "metadata": {
                    "total_results": 0,
                    "query_time": f"{query_time:.2f}s",
                    "sql_query": sql_query
                }
            }

    def _clean_llm_response(self, response: str) -> str:
        """Remove code blocks and technical notes from LLM response."""
        # Remove Python code blocks
        response = re.sub(r'```python.*?```', '', response, flags=re.DOTALL)
        # Remove any other code blocks
        response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
        # Remove notes about SQL queries
        response = re.sub(r'Note:.*?(?=\n\n|$)', '', response, flags=re.DOTALL)
        # Remove metadata about filtering
        response = re.sub(r'The response only includes projects where.*?(?=\n\n|$)', '', response, flags=re.DOTALL)
        # Clean up any double newlines resulting from removals
        response = re.sub(r'\n{3,}', '\n\n', response)
        # Remove any trailing/leading whitespace
        return response.strip()

    def _format_basic_response(self, query_results: List[Dict[str, Any]]) -> str:
        """Fallback method for basic response formatting."""
        try:
            if not query_results:
                return "I found no results matching your query. Could you try rephrasing your question?"
                
            if len(query_results) == 1:
                result = query_results[0]
                response_parts = []
                
                if 'project_name' in result:
                    response_parts.append(f"I found information about the project '{result['project_name']}'.")
                    
                if 'district' in result:
                    response_parts.append(f"It is located in {result['district']}.")
                    
                if 'project_sector' in result:
                    response_parts.append(f"This is a {result['project_sector']} sector project.")
                    
                if 'project_status' in result:
                    response_parts.append(f"The project status is {result['project_status']}.")
                    
                if 'total_budget' in result:
                    if isinstance(result['total_budget'], dict):
                        budget = result['total_budget'].get('formatted', str(result['total_budget'].get('amount', 'N/A')))
                    else:
                        budget = f"MWK {float(result['total_budget']):,.2f}"
                    response_parts.append(f"The total budget is {budget}.")
                    
                if 'completion_percentage' in result:
                    response_parts.append(f"It is {result['completion_percentage']}% complete.")
                    
                return " ".join(response_parts)
            else:
                # Summarize multiple results
                total_budget = 0
                districts = set()
                sectors = set()
                statuses = set()
                
                for result in query_results:
                    if 'district' in result:
                        districts.add(result['district'])
                    if 'project_sector' in result:
                        sectors.add(result['project_sector'])
                    if 'project_status' in result:
                        statuses.add(result['project_status'])
                    if 'total_budget' in result:
                        if isinstance(result['total_budget'], dict):
                            total_budget += float(result['total_budget'].get('amount', 0))
                        else:
                            total_budget += float(result['total_budget'])
                
                response_parts = [f"I found {len(query_results)} projects"]
                
                if districts:
                    if len(districts) == 1:
                        response_parts.append(f"in {list(districts)[0]}")
                    else:
                        response_parts.append(f"across {len(districts)} districts")
                
                if sectors:
                    if len(sectors) == 1:
                        response_parts.append(f"in the {list(sectors)[0]} sector")
                    else:
                        response_parts.append(f"across {len(sectors)} sectors")
                
                response_parts.append(".")
                
                if total_budget > 0:
                    response_parts.append(f" The total budget for these projects is MWK {total_budget:,.2f}.")
                
                if statuses:
                    status_counts = {}
                    for result in query_results:
                        if 'project_status' in result:
                            status = result['project_status']
                            status_counts[status] = status_counts.get(status, 0) + 1
                    
                    status_summary = []
                    for status, count in status_counts.items():
                        status_summary.append(f"{count} {status.lower()}")
                    
                    response_parts.append(f" Project status breakdown: {', '.join(status_summary)}.")
                
                response_parts.append(f" The first project is '{query_results[0].get('project_name', 'Unnamed Project')}'. Would you like more details about any specific project?")
                
                return "".join(response_parts)
                
        except Exception as e:
            logger.error(f"Error formatting basic response: {str(e)}")
            return "I found some information but encountered an error formatting it. Could you try asking in a different way?"

    def execute_query_from_natural_language(self, user_query: str) -> Dict[str, Any]:
        """Execute a query generated from natural language"""
        try:
            start_time = time.time()
            
            # Generate SQL query
            try:
                sql_query = self.generate_sql_query(user_query)
                logger.info(f"Generated SQL query: {sql_query}")
            except SQLQueryError as e:
                logger.error(f"SQL query generation error: {str(e)}")
                return {
                    "response": {
                        "query_type": "general",
                        "results": [],
                        "metadata": {
                            "total_results": 0,
                            "query_time": "0.1s",
                            "sql_query": "Error generating SQL query"
                        }
                    }
                }
            
            # Execute the query
            try:
                results = self.execute_query(sql_query)
                query_time = time.time() - start_time
                
                # Format budget values
                for result in results:
                    if 'total_budget' in result:
                        budget = float(result['total_budget'])
                        result['total_budget'] = {
                            'amount': budget,
                            'formatted': f"MWK {budget:,.2f}"
                        }
                
                return {
                    "response": {
                        "query_type": "general",
                        "results": results,
                        "metadata": {
                            "total_results": len(results),
                            "query_time": f"{query_time:.2f}s",
                            "sql_query": sql_query
                        }
                    }
                }
            except Exception as e:
                logger.error(f"Query execution error: {str(e)}")
                return {
                    "response": {
                        "query_type": "general",
                        "results": [],
                        "metadata": {
                            "total_results": 0,
                            "query_time": f"{time.time() - start_time:.2f}s",
                            "sql_query": sql_query,
                            "error": str(e)
                        }
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in execute_query_from_natural_language: {str(e)}")
            return {
                "response": {
                    "query_type": "error",
                    "results": [],
                    "metadata": {
                        "total_results": 0,
                        "query_time": "0.0s",
                        "error": str(e)
                    }
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
                    {"name": "projectname", "type": "text", "description": "Name of the infrastructure project"},
                    {"name": "district", "type": "text", "description": "District where the project is located"},
                    {"name": "projectsector", "type": "text", "description": "Sector of the project (e.g., infrastructure, education)"},
                    {"name": "projectstatus", "type": "text", "description": "Current status of the project (e.g., completed, in progress)"},
                    {"name": "budget", "type": "numeric", "description": "Total budget allocated in MWK"},
                    {"name": "completionpercentage", "type": "numeric", "description": "Percentage of project completion (0-100)"},
                    {"name": "startdate", "type": "numeric", "description": "Project start date in YYYYMMDD format"},
                    {"name": "completiondata", "type": "numeric", "description": "Expected completion date in YYYYMMDD format"}
                ]
            }
            return schema
        except Exception as e:
            logger.error(f"Error getting schema info: {str(e)}")
            raise

    def _get_table_info(self) -> Dict[str, Any]:
        """
        Get information about the database schema.
        
        Returns:
            Dict[str, Any]: Database schema information in a structured format
        """
        return self.get_table_info()

    def _is_aggregate_query(self, query: str) -> bool:
        """Check if the query requires aggregation"""
        aggregate_keywords = [
            'total', 'sum', 'average', 'avg', 'count', 'how many',
            'budget', 'most', 'least', 'highest', 'lowest'
        ]
        return any(keyword in query.lower() for keyword in aggregate_keywords)
        
    def _prepare_aggregate_prompt(self, user_query: str) -> str:
        """Prepare prompt for aggregate query"""
        return f"""Generate a SQL query for this question about Malawi infrastructure projects:
{user_query}

Important rules:
1. ALWAYS use COALESCE for numeric aggregates:
   - COALESCE(SUM(budget), 0) as total_budget
   - COALESCE(AVG(budget), 0) as avg_budget
   - COUNT(*) for counting records
2. For sector filtering, use: LOWER(projectsector) LIKE '%keyword%'
3. For status filtering, use: LOWER(projectstatus) = 'status'
4. Return ONLY the SQL query, no explanations

Example aggregate queries:
- Total budget: SELECT COALESCE(SUM(budget), 0) as total_budget FROM proj_dashboard;
- Sector budget: SELECT COALESCE(SUM(budget), 0) as total_budget FROM proj_dashboard WHERE LOWER(projectsector) LIKE '%infrastructure%';
- Project count: SELECT COUNT(*) as project_count FROM proj_dashboard;
"""

    def _prepare_non_aggregate_prompt(self, user_query: str) -> str:
        """Prepare prompt for non-aggregate query"""
        return f"""You are a SQL expert. Generate a SQL query to answer the following question:

Question: {user_query}

Use this database schema:
{self._get_table_info()}

Rules:
1. Use COALESCE for numeric fields:
   - COALESCE(budget, 0) as total_budget
   - COALESCE(completionpercentage, 0) as completion_percentage
2. For text matching, use LIKE with wildcards
3. Always alias columns with descriptive names
4. Only use SELECT statements

Example queries:
- Projects by district: SELECT projectname as project_name, COALESCE(budget, 0) as total_budget FROM proj_dashboard WHERE district = 'Lilongwe';
- Projects by sector: SELECT projectname as project_name, COALESCE(budget, 0) as total_budget FROM proj_dashboard WHERE LOWER(projectsector) LIKE '%education%';
"""

    def _transform_sql_query(self, sql_query: str) -> str:
        """Apply transformations to the SQL query"""
        # Replace district = 'X' with district = 'X'
        district_pattern = r"district\s*=\s*'([^']*)'"
        if re.search(district_pattern, sql_query):
            district_name = re.search(district_pattern, sql_query).group(1)
            sql_query = re.sub(
                district_pattern,
                f"district = '{district_name}'",
                sql_query
            )
            
        # Format date columns
        date_columns = ['startdate', 'completiondata']
        for col in date_columns:
            if col in sql_query and f"substr({col}" not in sql_query:
                # Replace the column with a formatted version
                sql_query = sql_query.replace(
                    f"{col}", 
                    f"substr({col},1,4) || '-' || substr({col},5,2) || '-' || substr({col},7,2)"
                )
                
        return sql_query

    def _is_greeting_or_general(self, query: str) -> bool:
        """Check if the query is a greeting or general conversation."""
        greetings = [
            'hello', 'hi', 'hey', 'good morning', 'good afternoon', 
            'good evening', 'howdy', 'greetings', 'hola'
        ]
        query = query.lower().strip()
        return any(query.startswith(greeting) for greeting in greetings)

def get_greeting_response() -> Dict:
    """Return a friendly greeting response."""
    return {
        "response": {
            "query_type": "chat",
            "results": [{
                "message": ("Hello! I'm Dwizani, your infrastructure projects assistant. "
                      "I can help you find information about infrastructure projects in Malawi. "
                      "You can ask me questions like:\n"
                      "- What projects are in Lilongwe?\n"
                      "- Query project budgets and costs\n"
                      "- Find projects by sector (Infrastructure, Education, etc.)\n"
                      "- Get statistics about project completion rates\n"
                      "How can I help you today?")
            }],
            "metadata": {
                "total_results": 1,
                "query_time": "0s",
                "sql_query": None
            }
        }
    }
