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
import pandas as pd
# Import the new LLM classification module
from ..llm_classification.service import QueryClassificationService
from ..llm_classification.classifier import QueryType

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
            
            # Initialize the query classification service
            self.query_classifier = QueryClassificationService()
            
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
                logger.error(f"Invalid SQL query: {sql_query}")
                return ""
                
            # Check for malicious SQL
            malicious_patterns = [
                "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE",
                "GRANT", "REVOKE", "--", ";--", "/*", "*/", "@@", "@", "char",
                "nchar", "varchar", "nvarchar", "exec", "execute", "cursor",
                "declare", "xp_", "sp_", "msdb", "cmdshell", "writetext"
            ]
            for pattern in malicious_patterns:
                if pattern.lower() in sql_query.lower():
                    logger.error(f"SQL query contains forbidden pattern: {pattern}")
                    return ""
                    
            # Check for valid SELECT statement
            if not sql_query.strip().lower().startswith("select"):
                logger.error("SQL query must start with SELECT")
                return ""
                
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
            return ""

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

    async def generate_sql_query(self, user_query: str) -> Tuple[str, str]:
        """Generate a SQL query from a natural language query"""
        try:
            # Check if this is a sector query
            sector_patterns = [
                r'(?:which|what|show|list|tell me about)(?: the)? projects?(?: are)? (?:in|from|about) (?:the )?([\w\s]+?) sector',
                r'(?:which|what|show|list|tell me about)(?: the)? ([\w\s]+?) sector projects',
                r'projects in (?:the )?([\w\s]+?) sector'
            ]
            
            for pattern in sector_patterns:
                match = re.search(pattern, user_query.lower(), re.IGNORECASE)
                if match:
                    sector_name = match.group(1).strip()
                    sql_query = f"""
                    SELECT 
                        projectname as project_name,
                        projectcode as project_code,
                        projectsector as project_sector,
                        projectstatus as status,
                        stage,
                        region,
                        district,
                        traditionalauthority,
                        budget as total_budget,
                        TOTALEXPENDITUREYEAR as total_expenditure,
                        fundingsource as funding_source,
                        startdate as start_date,
                        completionestidate as completion_date,
                        lastvisit as last_monitoring_visit,
                        completionpercentage as completion_progress,
                        contractorname as contractor,
                        signingdate as contract_signing_date,
                        projectdesc as description,
                        fiscalyear as fiscal_year
                    FROM 
                        proj_dashboard
                    WHERE 
                        LOWER(projectsector) LIKE '%{sector_name.lower()}%'
                    ORDER BY
                        budget DESC NULLS LAST
                    LIMIT 10;
                    """
                    return sql_query.strip(), "sector_query"

            # Check if this is a greeting or general conversation
            if self._is_greeting_or_general(user_query):
                return "", "greeting"
                
            # Check for health sector query
            if re.search(r'(?:health sector|healthcare|health projects)', user_query.lower()):
                sql_query = """
                SELECT 
                    projectname as project_name,
                    projectcode as project_code,
                    projectsector as project_sector,
                    projectstatus as status,
                    stage,
                    region,
                    district,
                    traditionalauthority,
                    budget as total_budget,
                    TOTALEXPENDITUREYEAR as total_expenditure,
                    fundingsource as funding_source,
                    startdate as start_date,
                    completionestidate as completion_date,
                    lastvisit as last_monitoring_visit,
                    completionpercentage as completion_progress,
                    contractorname as contractor,
                    signingdate as contract_signing_date,
                    projectdesc as description,
                    fiscalyear as fiscal_year
                FROM 
                    proj_dashboard 
                WHERE 
                    LOWER(projectsector) LIKE '%health%'
                ORDER BY 
                    budget DESC NULLS LAST
                LIMIT 10;
                """
                return sql_query.strip(), "sector_query"
            
            # Check if this is a district query
            district_match = re.search(r'(?:in|at|from|of)(?: the)? ([a-zA-Z\s]+?) district', user_query.lower())
            if district_match:
                district_name = district_match.group(1).strip()
                sql_query = f"""
                SELECT 
                    projectname as project_name,
                    fiscalyear as fiscal_year,
                    district,
                    budget as total_budget,
                    projectstatus as status,
                    projectsector as project_sector
                FROM 
                    proj_dashboard
                WHERE 
                    LOWER(district) LIKE '%{district_name.lower()}%'
                ORDER BY 
                    budget DESC
                LIMIT 10
                """
                
                # Execute query
                results = await self.execute_query(sql_query)
                query_time = time.time() - start_time
                
                if not results:
                    return {
                        "results": [{
                            "type": "text",
                            "message": f"I couldn't find any projects in {district_name.title()} district.",
                            "data": {}
                        }],
                        "metadata": {
                            "total_results": 0,
                            "query_time": f"{query_time:.2f}s",
                            "sql_query": sql_query
                        }
                    }
                
                # Format the response
                return await self.format_response(results, sql_query, query_time, user_query, "district_query", {"district_name": district_name})
            
            # Check if this is a specific project query
            project_patterns = [
                r'(?:tell|show|give) (?:me|us) (?:about|details of|information about) (?:the )?([\w\s-]+?)(?:\s+project)?\s*(?:$|[?.])',
                r'(?:what|how) (?:is|about) (?:the )?([\w\s-]+?)(?:\s+project)?\s*(?:$|[?.])',
                r'(?:details|information|status) (?:for|of) (?:the )?([\w\s-]+?)(?:\s+project)?\s*(?:$|[?.])'
            ]
            
            for pattern in project_patterns:
                match = re.search(pattern, user_query, re.IGNORECASE)
                if match:
                    project_name = match.group(1).strip()
                    sql_query = f"""
                    SELECT 
                        projectname as project_name,
                        projectcode as project_code,
                        projectsector as project_sector,
                        projectstatus as status,
                        stage,
                        region,
                        district,
                        traditionalauthority,
                        budget as total_budget,
                        TOTALEXPENDITUREYEAR as total_expenditure,
                        fundingsource as funding_source,
                        startdate as start_date,
                        completionestidate as completion_date,
                        lastvisit as last_monitoring_visit,
                        completionpercentage as completion_progress,
                        contractorname as contractor,
                        signingdate as contract_signing_date,
                        projectdesc as description,
                        fiscalyear as fiscal_year
                    FROM 
                        proj_dashboard
                    WHERE 
                        LOWER(projectname) LIKE '%{project_name.lower()}%'
                    ORDER BY
                        CASE 
                            WHEN LOWER(projectname) = '{project_name.lower()}' THEN 1
                            ELSE 2
                        END,
                        budget DESC
                    LIMIT 1
                    """
                    return sql_query, "specific_project"
            
            # Continue with other query types
            # Generate SQL query for other queries using LLM
            try:
                # Get LLM response for SQL generation
                prompt = self._prepare_non_aggregate_prompt(user_query)
                llm_response = await self._get_llm_response(prompt)
                sql_query = await self._extract_sql_from_text(llm_response)
                
                # Validate and transform the SQL query
                sql_query = await self._validate_sql_query(sql_query)
                sql_query = self._transform_sql_query(sql_query)
                
                # Execute query
                results = await self.execute_query(sql_query)
                query_time = time.time() - start_time
                
                # Format the response
                return await self.format_response(results, sql_query, query_time, user_query)
                
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}")
                return {
                    "results": [{
                        "type": "error",
                        "message": f"Error processing query: {str(e)}",
                        "data": {}
                    }],
                    "metadata": {
                        "total_results": 0,
                        "query_time": f"{time.time() - start_time:.2f}s",
                        "sql_query": ""
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in execute_query_from_natural_language: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "results": [{
                    "type": "error",
                    "message": f"An unexpected error occurred: {str(e)}",
                    "data": {}
                }],
                "metadata": {
                    "total_results": 0,
                    "query_time": "0.0s",
                    "error": str(e)
                }
            }

    async def generate_natural_response(self, results: List[Dict[str, Any]], user_query: str, sql_query: str = None, query_type: str = None) -> Dict[str, Any]:
        """Generate a natural language response from query results."""
        try:
            # Check if this is a count query
            is_count_query = any(key.lower().endswith('count') for result in results for key in result.keys())
            has_count = any('count' in key.lower() for result in results for key in result.keys())
            
            if is_count_query or has_count or 'which' in user_query.lower():
                # For count queries, format response directly without LLM
                count = None
                if has_count:
                    count = next(val for result in results for key, val in result.items() if 'count' in key.lower())
                else:
                    count = len(results)
                
                # Calculate total budget if available
                total_budget = 0
                budget_field = next((key for result in results for key in result.keys() if 'budget' in key.lower()), None)
                if budget_field:
                    total_budget = sum(float(result[budget_field]) for result in results if result.get(budget_field))
                
                # Format the response
                response = f"Found {count} projects"
                if total_budget > 0:
                    response += f" with a total budget of MWK {total_budget:,.2f}"
                
                # Add summary for 'which' queries
                if 'which' in user_query.lower():
                    if results:
                        # Get unique non-empty sectors and districts
                        sectors = {r.get('project_sector', r.get('PROJECTSECTOR', '')) for r in results if r.get('project_sector') or r.get('PROJECTSECTOR')}
                        districts = {r.get('district', r.get('DISTRICT', '')) for r in results if r.get('district') or r.get('DISTRICT')}
                        
                        if sectors:
                            if len(sectors) == 1:
                                response += f". All projects are in the {next(iter(sectors))} sector"
                            else:
                                sector_list = sorted(sectors)
                                response += f". Projects are in the following sectors: {', '.join(sector_list)}"
                        
                        if districts:
                            if len(districts) <= 5:
                                response += f". Located in: {', '.join(sorted(districts))}"
                            else:
                                top_districts = sorted(districts)[:5]
                                response += f". Projects are spread across {len(districts)} districts, including: {', '.join(top_districts)}"
                
                response += "."
                
                return {
                    "results": [{
                        "type": "text",
                        "message": response,
                        "data": {}
                    }],
                    "metadata": {
                        "total_results": count,
                        "query_time": "0.00s"
                    }
                }
            
            # For other queries, format results in a standardized way
            formatted_results = []
            total_budget = 0
            
            # Add summary message
            if results:
                budget_field = next((key for result in results[0].keys() if 'budget' in key.lower()), None)
                if budget_field:
                    total_budget = sum(float(result[budget_field]) for result in results if result.get(budget_field))
                
                summary = f"Found {len(results)} projects"
                if total_budget > 0:
                    summary += f" with a total budget of MWK {total_budget:,.2f}"
                summary += "."
                
                formatted_results.append({
                    "type": "text",
                    "message": summary,
                    "data": {}
                })
            
            # Format project details
            if len(results) > 0:
                formatted_projects = []
                for project in results[:10]:  # Show first 10 projects
                    # Get district name for district queries
                    location = project.get("district", "Unknown")
                    if query_type == "district_query":
                        district_match = re.search(r'(?:in|at|from|of)(?: the)? ([a-zA-Z\s]+?) district', user_query.lower())
                        if district_match:
                            location = district_match.group(1).strip().title()
                    
                    formatted_project = {
                        "Name of project": project.get("project_name", "Unknown"),
                        "Fiscal year": project.get("fiscal_year", "Unknown"),
                        "Location": location,
                        "Budget": f"MWK {float(project.get('total_budget', 0)):,.2f}" if project.get('total_budget') else "Unknown",
                        "Status": project.get("status", "Unknown"),
                        "Project Sector": project.get("project_sector", "Unknown")
                    }
                    formatted_projects.append(formatted_project)
                
                formatted_results.append({
                    "type": "list",
                    "message": "Project Details",
                    "data": {
                        "fields": ["Name of project", "Fiscal year", "Location", "Budget", "Status", "Project Sector"],
                        "values": formatted_projects
                    }
                })
                
                # Add pagination message if needed
                if len(results) > 10:
                    formatted_results.append({
                        "type": "text",
                        "message": f"Showing 10 of {len(results)} projects. Type 'show more' to see additional results.",
                        "data": {}
                    })
            
            return {
                "results": formatted_results,
                "metadata": {
                    "total_results": len(results),
                    "query_time": "0.00s",
                    "sql_query": sql_query
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating natural response: {str(e)}")
            return {
                "results": [{
                    "type": "error",
                    "message": "Error generating response",
                    "data": {}
                }],
                "metadata": {
                    "total_results": 0,
                    "query_time": "0.00s"
                }
            }

    async def format_response(self, query_results: List[Dict[str, Any]], sql_query: str, query_time: float, user_query: str, query_type: str = None, additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
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
            
            formatted_results = []
            
            # Add summary message with total count
            if query_results:
                total_count = len(query_results)
                shown_count = min(10, total_count)
                
                if query_type == "sector_query":
                    # Extract sector name from the first result
                    sector_name = query_results[0].get("project_sector", "specified sector")
                    summary = f"Found {total_count} projects in {sector_name}"
                else:
                    summary = f"Found {total_count} projects"
                
                if total_count > shown_count:
                    summary += f", showing first {shown_count}"
                summary += "."
                
                # Add budget information if available
                budget_field = next((key for key in query_results[0].keys() if 'budget' in key.lower()), None)
                if budget_field:
                    total_budget = sum(float(result[budget_field]) for result in query_results if result.get(budget_field) is not None)
                    if total_budget > 0:
                        summary += f" Total budget: MWK {total_budget:,.2f}"
                
                formatted_results.append({
                    "type": "text",
                    "message": summary,
                    "data": {}
                })

            # Format project list
            if len(query_results) > 0:
                formatted_projects = []
                for project in query_results[:10]:
                    try:
                        formatted_project = {
                            "Name": project.get("project_name", "Unknown"),
                            "Code": project.get("project_code", "Unknown"),
                            "Sector": project.get("project_sector", "Unknown"),
                            "Status": project.get("status", "Unknown"),
                            "Location": f"{project.get('region', '')}, {project.get('district', '')}".strip(", "),
                            "Budget": f"MWK {float(project.get('total_budget', 0)):,.2f}" if project.get('total_budget') is not None else "Unknown",
                            "Progress": f"{project.get('completion_progress', 0)}%" if project.get('completion_progress') is not None else "Unknown"
                        }
                        formatted_projects.append(formatted_project)
                    except Exception as e:
                        logger.error(f"Error formatting project: {str(e)}")
                        continue
                
                if formatted_projects:
                    formatted_results.append({
                        "type": "list",
                        "message": "Project Details",
                        "data": {
                            "fields": ["Name", "Code", "Sector", "Status", "Location", "Budget", "Progress"],
                            "values": formatted_projects
                        }
                    })
                    
                    # Add pagination message if needed
                    if len(query_results) > 10:
                        formatted_results.append({
                            "type": "text",
                            "message": "Type 'show more' to see additional results.",
                            "data": {}
                        })
            
            return {
                "results": formatted_results,
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

    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results as a list of dictionaries"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    result = {}
                    for i, value in enumerate(row):
                        result[columns[i]] = value
                    results.append(result)
                return results
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            logger.error(f"Query was: {query}")
            raise SQLQueryError(f"Database error: {str(e)}", query, "execution")

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
                greeting_response = await get_greeting_response()
                return greeting_response
                
            # Handle general questions about system capabilities
            if intent == "GENERAL":
                capabilities_prompt = """You are a helpful assistant for a Malawi infrastructure projects database. The user wants to know what kind of information they can query. Explain the following capabilities:
                
                1. Project Information:
                   - Search by project name or district
                   - View project sectors and status
                   - Check completion percentages
                   
                2. Financial Information:
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
                    sql_query, query_type = await self.generate_sql_query(user_query)
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
                            "query_type": query_type,
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
        """Process a natural language query and return formatted results"""
        try:
            start_time = time.time()
            
            # Generate SQL query
            sql_query, query_type = await self.generate_sql_query(user_query)
            
            if not sql_query:
                if query_type == "greeting":
                    return {
                        "results": [{
                            "type": "text",
                            "message": "Hello! I can help you find information about infrastructure projects in Malawi. You can ask about specific projects, sectors, or districts.",
                            "data": {}
                        }],
                        "metadata": {
                            "total_results": 0,
                            "query_time": f"{time.time() - start_time:.2f}s"
                        }
                    }
                return {
                    "results": [{
                        "type": "error",
                        "message": "I couldn't understand your query. Please try rephrasing it.",
                        "data": {}
                    }],
                    "metadata": {
                        "total_results": 0,
                        "query_time": f"{time.time() - start_time:.2f}s"
                    }
                }
            
            # Execute query
            results = await self.execute_query(sql_query)
            query_time = time.time() - start_time
            
            # Format the response
            return await self.format_response(results, sql_query, query_time, user_query, query_type)
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "results": [{
                    "type": "error",
                    "message": f"An error occurred while processing your query: {str(e)}",
                    "data": {}
                }],
                "metadata": {
                    "total_results": 0,
                    "query_time": "0.00s"
                }
            }

    async def execute_query_from_natural_language(self, user_query: str) -> Dict[str, Any]:
        """Execute a query from natural language and return results"""
        try:
            logger.info(f"Processing natural language query: {user_query}")
            start_time = time.time()
            
            # Generate SQL query
            try:
                sql_query, query_type = await self.generate_sql_query(user_query)
                logger.info(f"Generated SQL query: {sql_query}")
            except SQLQueryError as e:
                logger.error(f"SQL query generation error: {str(e)}")
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
            
            # If we didn't get a valid SQL query, return an error
            if not sql_query:
                return {
                    "results": [{
                        "type": "text",
                        "message": "I'm not sure how to answer that. Could you rephrase your question?",
                        "data": {}
                    }],
                    "metadata": {
                        "total_results": 0,
                        "query_time": f"{time.time() - start_time:.2f}s",
                        "sql_query": ""
                    }
                }
            
            # Execute query
            try:
                results = await self.execute_query(sql_query)
                query_time = time.time() - start_time
                
                # Format response using the format_response function
                return await self.format_response(results, sql_query, query_time, user_query, query_type)
                
            except Exception as e:
                logger.error(f"Query execution error: {str(e)}")
                return {
                    "results": [{
                        "type": "error",
                        "message": f"Error executing query: {str(e)}",
                        "data": {}
                    }],
                    "metadata": {
                        "total_results": 0,
                        "query_time": f"{time.time() - start_time:.2f}s",
                        "sql_query": sql_query
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in execute_query_from_natural_language: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "results": [{
                    "type": "error",
                    "message": f"An unexpected error occurred: {str(e)}",
                    "data": {}
                }],
                "metadata": {
                    "total_results": 0,
                    "query_time": "0.0s",
                    "error": str(e)
                }
            }

    def _format_basic_response(self, query_results: List[Dict[str, Any]]) -> str:
        """Fallback method for basic response formatting."""
        try:
            if not query_results:
                return "I found no results matching your query. Could you try different search terms?"
                
            if len(query_results) == 1:
                result = query_results[0]
                response_parts = []
                
                if 'project_name' in result:
                    response_parts.append(f"Project: {result['project_name']}")
                    
                if 'district' in result:
                    response_parts.append(f"Location: {result['district']}")
                    
                if 'project_sector' in result:
                    response_parts.append(f"Sector: {result['project_sector']}")
                    
                if 'project_status' in result:
                    response_parts.append(f"Status: {result['project_status']}")
                    
                if 'total_budget' in result:
                    if isinstance(result['total_budget'], dict):
                        budget = result['total_budget'].get('formatted', str(result['total_budget'].get('amount', 'N/A')))
                    else:
                        budget = f"MWK {float(result['total_budget']):,.2f}"
                    response_parts.append(f"Budget: {budget}")
                    
                if 'completion_percentage' in result:
                    response_parts.append(f"Completion: {result['completion_percentage']}%")
                    
                return "\n".join(response_parts)
                
            # Multiple results
            total_budget = sum(float(r.get('total_budget', 0)) for r in query_results)
            budget_str = f"MWK {total_budget:,.2f}"
            
            response_parts = [f"Found {len(query_results)} projects with a total budget of {budget_str}."]
            
            # Group projects by sector if available
            sectors = {}
            for result in query_results:
                if 'project_sector' in result:
                    sector = result['project_sector']
                    sectors[sector] = sectors.get(sector, 0) + 1
            
            if sectors:
                sector_summary = []
                for sector, count in sectors.items():
                    sector_summary.append(f"{count} in {sector.lower()}")
                response_parts.append(f"Projects by sector: {', '.join(sector_summary)}.")
            
            # Add first 5 projects as examples
            response_parts.append("\nProjects include:")
            for result in query_results[:5]:  # Show first 5 projects
                project_info = []
                project_info.append(result.get('project_name', 'Unnamed Project'))
                
                if 'project_status' in result:
                    project_info.append(f"({result['project_status']})")
                    
                if 'total_budget' in result:
                    if isinstance(result['total_budget'], dict):
                        budget = result['total_budget'].get('formatted', str(result['total_budget'].get('amount', 'N/A')))
                    else:
                        budget = f"MWK {float(result['total_budget']):,.2f}"
                    project_info.append(f"- {budget}")
                    
                response_parts.append(f"* {' '.join(project_info)}")
            
            if len(query_results) > 5:
                response_parts.append(f"\n...and {len(query_results) - 5} more projects.")
            
            return "\n".join(response_parts)
                
        except Exception as e:
            logger.error(f"Error formatting basic response: {str(e)}")
            return "I found some information but encountered an error formatting it. Could you try asking in a different way?"

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
        # Handle None or empty query
        if not sql_query:
            return ""
            
        try:
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
                        col,
                        f"strftime('%Y-%m-%d', {col})"
                    )
                    
            return sql_query
        except Exception as e:
            logger.error(f"Error transforming SQL query: {str(e)}")
            logger.error(f"Query: {sql_query}")
            return ""
            
    def _is_greeting_or_general(self, query: str) -> bool:
        """Check if the query is a greeting or general conversation."""
        greetings = [
            'hello', 'hi', 'hey', 'good morning', 'good afternoon', 
            'good evening', 'howdy', 'greetings', 'hola'
        ]
        query = query.lower().strip()
        return any(query.startswith(greeting) for greeting in greetings)

    def _clean_llm_response(self, response: str) -> str:
        """Clean the LLM response to remove code blocks, markdown, and other unwanted content."""
        # Remove code blocks (both ``` and ``)
        response = re.sub(r'```[\s\S]*?```', '', response)
        response = re.sub(r'``[\s\S]*?``', '', response)
        
        # Remove function definitions
        response = re.sub(r'def\s+\w+\s*\([^)]*\)\s*:', '', response)
        
        # Remove print statements
        response = re.sub(r'print\s*\([^)]*\)', '', response)
        
        # Remove Python syntax elements
        response = re.sub(r'if\s+.*?:', '', response)
        response = re.sub(r'else\s*:', '', response)
        response = re.sub(r'elif\s+.*?:', '', response)
        response = re.sub(r'return\s+.*', '', response)
        
        # Remove f-string syntax
        response = re.sub(r'f".*?"', '', response)
        response = re.sub(r"f'.*?'", '', response)
        
        # Remove variable assignments
        response = re.sub(r'\w+\s*=\s*.*', '', response)
        
        # Remove markdown formatting
        response = re.sub(r'##+\s+.*', '', response)
        
        # Clean up extra whitespace and newlines
        response = re.sub(r'\n{3,}', '\n\n', response)
        response = re.sub(r'\s{2,}', ' ', response)
        
        # Final cleanup
        response = response.strip()
        
        # If response is empty after cleaning, provide a fallback
        if not response:
            response = "I found some matching projects in the database."
            
        return response

    def _format_specific_project(self, project: pd.Series, is_code_query: bool = False) -> str:
        """Format a specific project's details"""
        try:
            # Format all values first
            formatted_values = {}
            for field in self.specific_field_order:
                if field in project.index:
                    value = project[field]
                    formatted_values[field] = (
                        self._format_currency(value) if field in self.currency_columns
                        else self._format_date(value) if field in self.date_columns
                        else self._format_percentage(value) if field == 'COMPLETIONPERCENTAGE'
                        else self._format_value(value)
                    )
            
            # Build response sections
            sections = []
            
            # Basic Information
            basic_info = []
            if is_code_query:
                basic_info.extend([
                    f"Project Code: {formatted_values.get('PROJECTCODE', self.NULL_VALUE)}",
                    f"Project Name: {formatted_values.get('PROJECTNAME', self.NULL_VALUE)}"
                ])
            else:
                basic_info.extend([
                    f"Project Name: {formatted_values.get('PROJECTNAME', self.NULL_VALUE)}",
                    f"Project Code: {formatted_values.get('PROJECTCODE', self.NULL_VALUE)}"
                ])
            basic_info.extend([
                f"Sector: {formatted_values.get('PROJECTSECTOR', self.NULL_VALUE)}",
                f"Region: {formatted_values.get('REGION', self.NULL_VALUE)}",
                f"District: {formatted_values.get('DISTRICT', self.NULL_VALUE)}",
                f"Status: {formatted_values.get('PROJECTSTATUS', self.NULL_VALUE)}"
            ])
            sections.append("\n".join(basic_info))
            
            # Implementation Details
            if any(field in formatted_values for field in ['CONTRACTORNAME', 'STARTDATE', 'COMPLETIONESTIDATE', 'COMPLETIONPERCENTAGE']):
                impl_details = ["\nImplementation Details:"]
                for field in ['CONTRACTORNAME', 'STARTDATE', 'COMPLETIONESTIDATE', 'COMPLETIONPERCENTAGE', 'STAGE']:
                    if field in formatted_values:
                        impl_details.append(f"{field.title()}: {formatted_values[field]}")
                sections.append("\n".join(impl_details))
            
            # Financial Information
            if any(field in formatted_values for field in ['TOTALBUDGET', 'TOTALEXPENDITUREYEAR', 'FUNDINGSOURCE']):
                financial_info = ["\nFinancial Information:"]
                for field in ['TOTALBUDGET', 'TOTALEXPENDITUREYEAR', 'FUNDINGSOURCE']:
                    if field in formatted_values:
                        financial_info.append(f"{field.title()}: {formatted_values[field]}")
                sections.append("\n".join(financial_info))
            
            # Additional Information
            if formatted_values.get('PROJECTDESC', self.NULL_VALUE) != self.NULL_VALUE:
                sections.append("\nProject Description:")
                sections.append(formatted_values['PROJECTDESC'])
            
            return "\n\n".join(sections)
            
        except Exception as e:
            logger.error(f"Error formatting specific project: {str(e)}")
            return "Error: Unable to format project details"

    async def process_paginated_query(self, user_query: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Process a query with pagination parameters"""
        start_time = time.time()
        
        try:
            # Generate the SQL query
            sql_query = await self._generate_sql_query(user_query)
            
            # Modify the query to include pagination
            if not sql_query.lower().strip().endswith(";"):
                sql_query += ";"
                
            # Remove existing LIMIT clause if present
            sql_query = re.sub(r"\s+LIMIT\s+\d+\s*;", ";", sql_query)
            
            # Add new LIMIT and OFFSET clauses
            sql_query = sql_query[:-1]  # Remove trailing semicolon
            sql_query += f" LIMIT {limit} OFFSET {offset};"
            
            # Execute the query
            logger.info(f"Executing paginated SQL query: {sql_query}")
            results = await self._execute_query(sql_query)
            
            # Generate count query to get total results
            count_query = self._generate_count_query(sql_query)
            count_results = await self._execute_query(count_query)
            total_results = count_results[0].get("count", len(results))
            
            # Format the response
            response = await self._format_paginated_results(
                results, user_query, sql_query, total_results, limit, offset
            )
            
            return response
        except Exception as e:
            logger.error(f"Error processing paginated query: {str(e)}")
            return {
                "results": [{
                    "type": "error",
                    "message": f"Error processing paginated query: {str(e)}",
                    "data": {}
                }],
                "metadata": {
                    "total_results": 0,
                    "query_time": f"{time.time() - self.start_time:.2f}s",
                    "sql_query": ""
                }
            }

    def _generate_count_query(self, sql_query: str) -> str:
        """Generate a count query from a SELECT query"""
        # Parse the original query
        from_pos = sql_query.lower().find("from")
        where_pos = sql_query.lower().find("where")
        
        if from_pos == -1:
            return "SELECT COUNT(*) as count FROM proj_dashboard;"
        
        # Extract FROM clause and beyond
        if where_pos != -1:
            from_clause = sql_query[from_pos:where_pos]
            where_clause = sql_query[where_pos:]
            
            # Remove ORDER BY, LIMIT and OFFSET clauses
            order_pos = where_clause.lower().find("order by")
            limit_pos = where_clause.lower().find("limit")
            
            if order_pos != -1:
                where_clause = where_clause[:order_pos]
            elif limit_pos != -1:
                where_clause = where_clause[:limit_pos]
            
            return f"SELECT COUNT(*) as count {from_clause} {where_clause};"
        
        # No WHERE clause
        remaining = sql_query[from_pos:]
        order_pos = remaining.lower().find("order by")
        limit_pos = remaining.lower().find("limit")
        
        if order_pos != -1:
            remaining = remaining[:order_pos]
        elif limit_pos != -1:
            remaining = remaining[:limit_pos]
        
        return f"SELECT COUNT(*) as count {remaining};"

    async def _format_paginated_results(
        self,
        results: List[Dict[str, Any]],
        user_query: str,
        sql_query: str,
        total_results: int,
        limit: int,
        offset: int
    ) -> Dict[str, Any]:
        """Format paginated results with metadata"""
        current_page = (offset // limit) + 1
        total_pages = (total_results + limit - 1) // limit
        start_index = offset + 1
        end_index = min(offset + limit, total_results)
        
        formatted_results = []
        
        # Add header message
        if offset == 0:
            message = f"Found {total_results} results. Showing {start_index}-{end_index}:"
        else:
            message = f"Showing results {start_index}-{end_index} of {total_results}:"
            
        formatted_results.append({
            "type": "text",
            "message": message,
            "data": {}
        })
        
        # Format the results as a table
        if results:
            # Get headers from the first result
            headers = list(results[0].keys())
            
            formatted_results.append({
                "type": "table",
                "message": "Project Details",
                "data": {
                    "headers": headers,
                    "rows": results
                }
            })
        
        return {
            "results": formatted_results,
            "metadata": {
                "total_results": total_results,
                "current_page": current_page,
                "total_pages": total_pages,
                "page_size": limit,
                "query_time": f"{time.time() - self.start_time:.2f}s",
                "sql_query": sql_query
            },
            "pagination": {
                "has_more": current_page < total_pages,
                "has_previous": current_page > 1,
                "current_page": current_page,
                "total_pages": total_pages,
                "next_page_command": "show more" if current_page < total_pages else None,
                "prev_page_command": "previous page" if current_page > 1 else None
            }
        }

async def get_greeting_response() -> Dict:
    """Return a friendly greeting response."""
    return {
        "response": {
            "query_type": "chat",
            "results": [{
                "message": ("Hello! I'm Dziwani, your infrastructure projects assistant. "
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
