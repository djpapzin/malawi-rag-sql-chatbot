from typing import Dict, List, Any, Union, Optional, Tuple
from datetime import datetime
import logging
import time
import traceback
import os
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
            api_key = os.getenv("TOGETHER_API_KEY")
            if not api_key:
                raise ValueError("TOGETHER_API_KEY environment variable is not set")
            
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
            
            # Test the API connection and log available models
            try:
                models = self.client.models.list()
                logger.info("Successfully connected to Together API")
                logger.info(f"Using model: {self.model}")
            except Exception as e:
                logger.warning(f"Could not fetch model list: {str(e)}")
            
            # Initialize list of valid districts
            self.valid_districts = [
                'Balaka', 'Blantyre', 'Chikwawa', 'Chiradzulu', 'Chitipa', 'Dedza', 
                'Dowa', 'Karonga', 'Kasungu', 'Likoma', 'Lilongwe', 'Machinga', 
                'Mangochi', 'Mchinji', 'Mulanje', 'Mwanza', 'Mzimba', 'Neno', 
                'Nkhata Bay', 'Nkhotakota', 'Nsanje', 'Ntcheu', 'Ntchisi', 'Phalombe', 
                'Rumphi', 'Salima', 'Thyolo', 'Zomba'
            ]
            
            # Initialize district variations mapping
            self.district_variations = {
                "nkhatabay": "Nkhata Bay",
                "nkata bay": "Nkhata Bay",
                "nkhotacota": "Nkhotakota",
                "lilongway": "Lilongwe",
                "blantire": "Blantyre",
                "blantrye": "Blantyre",
                "zomba city": "Zomba",
                "mzuzu": "Mzimba",  # Mzuzu is in Mzimba district
            }
            
            # Initialize sector mapping with exact database values
            self.sector_mapping = {
                "Education": ["education", "school", "training", "learning", "college", "university", "classroom"],
                "Roads and bridges": ["road", "bridge", "transport", "highway", "railway", "infrastructure"],
                "Commercial services": ["commercial", "market", "business", "trade", "shop", "service"],
                "Health": ["health", "healthcare", "medical", "hospital", "clinic", "dispensary", "maternity"],
                "Water and sanitation": ["water", "sanitation", "irrigation", "dam", "borehole", "sewage", "waste", "drainage"],
                "Agriculture and environment": ["agriculture", "farming", "crops", "livestock", "irrigation", "environment", "environmental"],
                "Community security initiatives": ["security", "police", "community security", "police unit", "safety"]
            }
            
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

    def _get_total_budget_query(self) -> str:
        """Get query for total budget across all projects"""
        return """
                    SELECT 
                COUNT(*) as total_projects,
                COALESCE(SUM(budget), 0) as total_budget,
                COALESCE(SUM(TOTALEXPENDITUREYEAR), 0) as total_expenditure
            FROM proj_dashboard;
        """

    async def _extract_sector(self, user_query: str) -> Optional[str]:
        """Extract sector from user query"""
        try:
            query = user_query.lower()
            
            # Define exact sector mappings with their lowercase versions for matching
            sectors = {
                'Education': ['education', 'school', 'classroom', 'teaching', 'learning', 'educational'],
                'Roads and bridges': ['roads and bridges', 'road', 'bridge', 'transport', 'road infrastructure'],
                'Commercial services': ['commercial services', 'commercial', 'business', 'trade', 'market'],
                'Health': ['health', 'hospital', 'clinic', 'medical', 'healthcare', 'health center'],
                'Water and sanitation': ['water and sanitation', 'water', 'sanitation', 'borehole', 'hygiene'],
                'Agriculture and environment': ['agriculture and environment', 'agriculture', 'farming', 'crops', 'environment'],
                'Community security initiatives': ['community security', 'security', 'police', 'safety']
            }
            
            # Log what we're looking for
            logger.info(f"Extracting sector from query: '{query}'")
            
            # First check for exact sector mentions
            for sector, keywords in sectors.items():
                # Check for exact name match first
                if sector.lower() in query:
                    logger.info(f"Found exact sector match: {sector}")
                    return sector
                
                # Then check for keyword matches
                for keyword in keywords:
                    if f" {keyword} " in f" {query} ":
                        logger.info(f"Found sector '{sector}' from keyword: '{keyword}'")
                        return sector
            
            # Second pass: check for partial matches at word boundaries
            for sector, keywords in sectors.items():
                for keyword in keywords:
                    if keyword in query.split():
                        logger.info(f"Found sector '{sector}' from word boundary match: '{keyword}'")
                        return sector
            
            # Third pass: check for contains matches for short queries
            if len(query.split()) <= 10:  # Only for short queries to avoid false positives
                for sector, keywords in sectors.items():
                    for keyword in keywords:
                        if len(keyword) > 3 and keyword in query:  # Only match keywords longer than 3 chars
                            logger.info(f"Found sector '{sector}' from substring match: '{keyword}'")
                            return sector
            
            logger.info("No sector found in query")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting sector: {str(e)}")
            logger.error(traceback.format_exc())
            return None

    async def generate_sql_query(self, query: str) -> Tuple[str, str]:
        """Generate SQL query based on user input."""
        logging.info(f"Generating SQL query for: {query}")
        
        # First try to extract project name
        project_name = await self._extract_project_name(query)
        if project_name:
            logging.info(f"Found specific project query: {project_name}")
            sql = self._build_specific_project_sql(project_name)
            return sql, "specific"
            
        # Check for district query
        district_match = re.search(r'(?:in|at|for)\s+(?:the\s+)?([A-Za-z]+)\s+(?:district|area)', query.lower())
        if district_match:
            district = district_match.group(1)
            logging.info(f"Found district query: {district}")
            sql = self._build_district_sql(district)
            return sql, "district_query"
            
        # Check for sector query
        sector_keywords = ['health', 'education', 'agriculture', 'water', 'sanitation', 'transport', 'roads']
        sector_match = re.search(r'(?:in|about|for)\s+(?:the\s+)?([A-Za-z]+)\s+(?:sector|projects)', query.lower())
        if sector_match:
            sector = sector_match.group(1)
            if sector.lower() in sector_keywords:
                logging.info(f"Found sector query: {sector}")
                sql = self._build_sector_sql(sector)
                return sql, "sector_query"
        
        # Default to general query
        logging.info("No specific criteria found, using general query")
        sql = self._build_general_query_sql()
        return sql, "general"

    def _build_specific_project_sql(self, project_name: str) -> str:
        """Build SQL query for specific project search."""
        sql = f"""SELECT 
                        PROJECTNAME as project_name,
                        PROJECTCODE as project_code,
                        PROJECTSECTOR as project_sector,
                        PROJECTSTATUS as status,
                        STAGE,
                        REGION,
                        DISTRICT,
                        TRADITIONALAUTHORITY,
                        BUDGET as total_budget,
                        TOTALEXPENDITUREYEAR as total_expenditure,
                        FUNDINGSOURCE as funding_source,
                        STARTDATE as start_date,
                        COMPLETIONESTIDATE as completion_date,
                        LASTVISIT as last_monitoring_visit,
                        COMPLETIONPERCENTAGE as completion_progress,
                        CONTRACTORNAME as contractor,
                        SIGNINGDATE as contract_signing_date,
                        PROJECTDESC as description,
                        FISCALYEAR as fiscal_year
                  FROM proj_dashboard
                    WHERE LOWER(PROJECTNAME) LIKE LOWER('%{project_name}%')
                    ORDER BY 
                        CASE 
                            WHEN LOWER(PROJECTNAME) = LOWER('{project_name}') THEN 1
                            WHEN LOWER(PROJECTNAME) LIKE LOWER('{project_name}%') THEN 2
                            WHEN LOWER(PROJECTNAME) LIKE LOWER('%{project_name}%') THEN 3
                            ELSE 4
                        END,
                        BUDGET DESC NULLS LAST
                    LIMIT 10;"""
        return sql

    def _build_district_sql(self, district: str) -> str:
        """Build SQL query for district-specific search."""
        sql = f"""SELECT 
                        PROJECTNAME as project_name,
                        PROJECTCODE as project_code,
                        PROJECTSECTOR as project_sector,
                        PROJECTSTATUS as status,
                        STAGE,
                        REGION,
                        DISTRICT,
                        TRADITIONALAUTHORITY,
                        BUDGET as total_budget,
                        TOTALEXPENDITUREYEAR as total_expenditure,
                        FUNDINGSOURCE as funding_source,
                        STARTDATE as start_date,
                        COMPLETIONESTIDATE as completion_date,
                        LASTVISIT as last_monitoring_visit,
                        COMPLETIONPERCENTAGE as completion_progress,
                        CONTRACTORNAME as contractor,
                        SIGNINGDATE as contract_signing_date,
                        PROJECTDESC as description,
                        FISCALYEAR as fiscal_year
                  FROM proj_dashboard
                    WHERE LOWER(DISTRICT) LIKE LOWER('%{district}%')
                    ORDER BY BUDGET DESC NULLS LAST
                    LIMIT 10;"""
        return sql

    def _build_general_query_sql(self) -> str:
        """Build SQL query for general search."""
        sql = """SELECT 
                        PROJECTNAME as project_name,
                        PROJECTCODE as project_code,
                        PROJECTSECTOR as project_sector,
                        PROJECTSTATUS as status,
                        STAGE,
                        REGION,
                        DISTRICT,
                        TRADITIONALAUTHORITY,
                        BUDGET as total_budget,
                        TOTALEXPENDITUREYEAR as total_expenditure,
                        FUNDINGSOURCE as funding_source,
                        STARTDATE as start_date,
                        COMPLETIONESTIDATE as completion_date,
                        LASTVISIT as last_monitoring_visit,
                        COMPLETIONPERCENTAGE as completion_progress,
                        CONTRACTORNAME as contractor,
                        SIGNINGDATE as contract_signing_date,
                        PROJECTDESC as description,
                        FISCALYEAR as fiscal_year
                  FROM proj_dashboard
                    ORDER BY BUDGET DESC NULLS LAST
                    LIMIT 10;"""
        return sql

    def _build_sector_sql(self, sector: str) -> Tuple[str, str]:
        """Build SQL query for sector-specific search."""
        # Count query
        count_sql = f"""SELECT COUNT(*) as total_count
                  FROM proj_dashboard
                    WHERE LOWER(PROJECTSECTOR) LIKE LOWER('%{sector}%')"""
                    
        # Results query
        results_sql = f"""SELECT 
                        PROJECTNAME as project_name,
                        PROJECTCODE as project_code,
                        PROJECTSECTOR as project_sector,
                        PROJECTSTATUS as status,
                        STAGE,
                        REGION,
                        DISTRICT,
                        TRADITIONALAUTHORITY,
                        BUDGET as total_budget,
                        TOTALEXPENDITUREYEAR as total_expenditure,
                        FUNDINGSOURCE as funding_source,
                        STARTDATE as start_date,
                        COMPLETIONESTIDATE as completion_date,
                        LASTVISIT as last_monitoring_visit,
                        COMPLETIONPERCENTAGE as completion_progress,
                        CONTRACTORNAME as contractor,
                        SIGNINGDATE as contract_signing_date,
                        PROJECTDESC as description,
                        FISCALYEAR as fiscal_year
                  FROM proj_dashboard
                    WHERE LOWER(PROJECTSECTOR) LIKE LOWER('%{sector}%')
                    ORDER BY BUDGET DESC NULLS LAST
                    LIMIT 10;"""
        return (count_sql, results_sql)

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
                
                # Get the sector name for sector queries
                sector_name = None
                if query_type == "sector_query" and results:
                    logger.debug(f"Sector query results (first 100 chars): {str(results)[:100]}...")
                    logger.debug(f"First result keys: {results[0].keys() if results else 'No results'}")
                    # Keys can be uppercase or lowercase depending on the query
                    sector_keys = ["project_sector", "projectsector", "PROJECTSECTOR"]
                    for key in sector_keys:
                        if key in results[0]:
                            sector_name = results[0].get(key)
                            if sector_name:
                                break
                    
                    if not sector_name:
                        sector_name = "specified sector"
                    
                    logger.info(f"Extracted sector name: {sector_name}")
                
                # Format the summary message
                if query_type == "sector_query":
                    summary = f"Found {len(results)} projects in {sector_name}"
                else:
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
                for project in results[:10]:
                    try:
                        # Get location based on query type
                        if query_type == "district_query":
                            # Try to get district from query first
                            district_from_query = None
                            district_match = re.search(r'(?:in|at|from|of|for)(?: the)? ([a-zA-Z\s]+?) district', user_query.lower())
                            if district_match:
                                district_from_query = district_match.group(1).strip().title() + " District"
                            
                            # Try to get district from result
                            district_keys = ["district", "DISTRICT"]
                            district_from_result = None
                            for key in district_keys:
                                if key in project and project[key]:
                                    district_from_result = project[key]
                                    break
                            
                            # Use the best available district information
                            location = district_from_query or district_from_result or "Unknown"
                        else:
                            # For non-district queries, use district and region if available
                            district_keys = ["district", "DISTRICT", "District"]
                            region_keys = ["region", "REGION", "Region"]
                            
                            district = None
                            for key in district_keys:
                                if key in project and project[key]:
                                    district = project[key]
                                    break
                            
                            region = None
                            for key in region_keys:
                                if key in project and project[key]:
                                    region = project[key]
                                    break
                            
                            if region and district:
                                location = f"{region}, {district}"
                            elif district:
                                location = district
                            elif region:
                                location = region
                            else:
                                location = "Unknown"
                        
                        formatted_project = {}
                        if query_type == "specific":
                            # Use all 12 fields for specific queries
                            # Handle potential variations in field names
                            project_name = None
                            for key in ["project_name", "PROJECTNAME", "projectname"]:
                                if key in project and project[key]:
                                    project_name = project[key]
                                    break
                            
                            fiscal_year = None
                            for key in ["fiscal_year", "FISCALYEAR", "fiscalyear"]:
                                if key in project and project[key]:
                                    fiscal_year = project[key]
                                    break
                            
                            budget = None
                            for key in ["total_budget", "BUDGET", "budget"]:
                                if key in project and project[key] is not None:
                                    try:
                                        budget = float(project[key])
                                        break
                                    except (ValueError, TypeError):
                                        continue
                            
                            status = None
                            for key in ["status", "PROJECTSTATUS", "projectstatus"]:
                                if key in project and project[key]:
                                    status = project[key]
                                    break
                            
                            contractor = None
                            for key in ["contractor", "CONTRACTORNAME", "contractorname"]:
                                if key in project and project[key]:
                                    contractor = project[key]
                                    break
                            
                            contract_date = None
                            for key in ["contract_signing_date", "SIGNINGDATE", "signingdate"]:
                                if key in project and project[key]:
                                    contract_date = project[key]
                                    break
                            
                            expenditure = None
                            for key in ["total_expenditure", "TOTALEXPENDITUREYEAR", "totalexpenditureyear"]:
                                if key in project and project[key] is not None:
                                    try:
                                        expenditure = float(project[key])
                                        break
                                    except (ValueError, TypeError):
                                        continue
                            
                            sector = None
                            for key in ["project_sector", "PROJECTSECTOR", "projectsector"]:
                                if key in project and project[key]:
                                    sector = project[key]
                                    break
                            
                            funding_source = None
                            for key in ["funding_source", "FUNDINGSOURCE", "fundingsource"]:
                                if key in project and project[key]:
                                    funding_source = project[key]
                                    break
                            
                            project_code = None
                            for key in ["project_code", "PROJECTCODE", "projectcode"]:
                                if key in project and project[key]:
                                    project_code = project[key]
                                    break
                            
                            monitoring_visit = None
                            for key in ["last_monitoring_visit", "LASTVISIT", "lastvisit"]:
                                if key in project and project[key]:
                                    monitoring_visit = project[key]
                                    break
                            
                            formatted_project = {
                                "Name of project": project_name or "Unknown",
                                "Fiscal year": fiscal_year or "Unknown",
                                "Location": location,
                                "Budget": f"MWK {budget:,.2f}" if budget is not None else "Unknown",
                                "Status": status or "Unknown",
                                "Contractor name": contractor or "Unknown",
                                "Contract start date": contract_date or "Unknown",
                                "Expenditure to date": f"MWK {expenditure:,.2f}" if expenditure is not None else "Unknown",
                                "Sector": sector or "Unknown",
                                "Source of funding": funding_source or "Unknown",
                                "Project code": project_code or "Unknown",
                                "Date of last Council monitoring visit": monitoring_visit or "Unknown"
                            }
                        else:
                            # Use 6 fields for general queries
                            # Handle potential variations in field names
                            project_name = None
                            for key in ["project_name", "PROJECTNAME", "projectname"]:
                                if key in project and project[key]:
                                    project_name = project[key]
                                    break
                            
                            fiscal_year = None
                            for key in ["fiscal_year", "FISCALYEAR", "fiscalyear"]:
                                if key in project and project[key]:
                                    fiscal_year = project[key]
                                    break
                            
                            budget = None
                            for key in ["total_budget", "BUDGET", "budget"]:
                                if key in project and project[key] is not None:
                                    try:
                                        budget = float(project[key])
                                        break
                                    except (ValueError, TypeError):
                                        continue
                            
                            status = None
                            for key in ["status", "PROJECTSTATUS", "projectstatus"]:
                                if key in project and project[key]:
                                    status = project[key]
                                    break
                            
                            sector = None
                            for key in ["project_sector", "PROJECTSECTOR", "projectsector"]:
                                if key in project and project[key]:
                                    sector = project[key]
                                    break
                            
                            formatted_project = {
                                "Name of project": project_name or "Unknown",
                                "Fiscal year": fiscal_year or "Unknown",
                                "Location": location,
                                "Budget": f"MWK {budget:,.2f}" if budget is not None else "Unknown",
                                "Status": status or "Unknown",
                                "Sector": sector or "Unknown"
                            }
                        formatted_projects.append(formatted_project)
                    except Exception as e:
                        logger.error(f"Error formatting project: {str(e)}")
                        continue
                
                formatted_results.append({
                    "type": "list",
                    "message": "Project List",
                    "data": {
                        "fields": ["Name of project", "Fiscal year", "Location", "Budget", "Status", "Contractor name", "Contract start date", "Expenditure to date", "Sector", "Source of funding", "Project code", "Date of last Council monitoring visit"] if query_type == "specific" else ["Name of project", "Fiscal year", "Location", "Budget", "Status", "Sector"],
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

    async def format_response(self, query_results: Union[List[Dict[str, Any]], Tuple[int, List[Dict[str, Any]]]], 
                             sql_query: str, query_time: float, user_query: str, query_type: str) -> Dict[str, Any]:
        """Format the response in a consistent way"""
        try:
            # Handle both parameter naming conventions
            results = query_results[1] if isinstance(query_results, tuple) else query_results
            total_count = query_results[0] if isinstance(query_results, tuple) else len(results)
            
            # Format SQL query for metadata
            formatted_sql = sql_query.strip() if isinstance(sql_query, str) else sql_query[1].strip()
            
            # Create metadata
            metadata = {
                "total_results": total_count,
                "query_time": f"{query_time:.2f}s",
                "sql_query": formatted_sql,
                "original_query": user_query,
                "query_type": query_type
            }
            
            # Handle case where no results found
            if not results:
                return {
                    "response": f"No projects found matching your query about {user_query}.",
                    "metadata": metadata
                }
            
            # Format results based on query type
            formatted_results = []
            
            # Add summary message
            summary_message = ""
            if query_type == "sector_query":
                # Extract sector name from the first result if available
                sector_name = "unknown"
                if results and len(results) > 0:
                    # Try to get the sector from the first result
                    for key in ["PROJECTSECTOR", "projectsector", "project_sector"]:
                        if key in results[0]:
                            sector_name = results[0][key]
                            break
                
                summary_message = f"Found {total_count} projects in the {sector_name} sector."
            else:
                summary_message = f"Found {total_count} projects matching your query."
            
            formatted_results.append({
                "type": "text",
                "message": summary_message,
                "data": {}
            })
            
            # Format project details (up to 10)
            formatted_projects = []
            for project in results[:10]:
                try:
                    project_data = {}
                    
                    # Helper function to get values with case-insensitive keys
                    def get_value(keys):
                        for key in keys:
                            if key in project:
                                return project[key]
                            if key.lower() in project:
                                return project[key.lower()]
                        return "Unknown"
                    
                    # Get project name
                    project_data["Name of project"] = get_value(["PROJECTNAME", "project_name"])
                    
                    # Get fiscal year
                    project_data["Fiscal year"] = get_value(["FISCALYEAR", "fiscal_year"])
                    
                    # Get location
                    district = get_value(["DISTRICT", "district"])
                    region = get_value(["REGION", "region"])
                    ta = get_value(["TRADITIONALAUTHORITY", "traditional_authority"])
                    location_parts = [p for p in [district, region, ta] if p != "Unknown"]
                    project_data["Location"] = ", ".join(location_parts) if location_parts else "Unknown"
                    
                    # Get budget
                    budget = None
                    for key in ["BUDGET", "total_budget", "budget"]:
                        if key in project and project[key] is not None:
                            try:
                                budget = float(project[key])
                                break
                            except (ValueError, TypeError):
                                continue
                    project_data["Budget"] = f"MWK {budget:,.2f}" if budget is not None else "Unknown"
                    
                    # Get remaining fields
                    project_data["Status"] = get_value(["PROJECTSTATUS", "status", "projectstatus"])
                    project_data["Sector"] = get_value(["PROJECTSECTOR", "project_sector", "projectsector"])
                    
                    formatted_projects.append(project_data)
                except Exception as e:
                    logger.error(f"Error formatting project: {str(e)}")
                    continue
            
            if formatted_projects:
                formatted_results.append({
                    "type": "list",
                    "message": "Project List",
                    "data": {
                        "fields": ["Name of project", "Fiscal year", "Location", "Budget", "Status", "Sector"],
                        "values": formatted_projects
                    }
                })
                
                # Add pagination message if needed
                if total_count > 10:
                    formatted_results.append({
                        "type": "text",
                        "message": f"Showing 10 of {total_count} projects. Type 'show more' to see additional results.",
                        "data": {}
                    })
            
            return {
                "response": formatted_results,
                "metadata": metadata
            }

        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            return {
                "response": [{
                    "type": "error",
                    "message": "I encountered an error while formatting the response. Please try again.",
                    "data": {}
                }],
                "metadata": {
                    "error": str(e),
                    "sql_query": sql_query,
                    "query_time": f"{query_time:.2f}s",
                    "original_query": user_query
                }
            }

    async def execute_query(self, query: Union[str, Tuple[str, str]]) -> Union[List[Dict[str, Any]], Tuple[int, List[Dict[str, Any]]]]:
        """Execute a SQL query and return results as a list of dictionaries"""
        try:
            logger.info(f"Executing query: {query}")
            
            # Connect to the database
            with self.db_manager.get_connection() as connection:
                cursor = connection.cursor()
                # Check if we have a tuple of count and results query
                if isinstance(query, tuple) and len(query) == 2:
                    count_query, results_query = query
                    
                    # Execute count query first
                    cursor.execute(count_query)
                    count_result = cursor.fetchone()
                    total_count = count_result[0] if count_result else 0
                    logger.info(f"Count query returned: {total_count}")
                    logger.info(f"Count query was: {count_query}")
                    
                    # Then execute results query
                    cursor.execute(results_query)
                    columns = [desc[0] for desc in cursor.description]
                    results = []
                    logger.info(f"Results query columns: {columns}")
                    for row in cursor.fetchall():
                        result = {}
                        for i, value in enumerate(row):
                            # Store the original column name
                            result[columns[i]] = value
                            
                            # Also store lowercase version for case-insensitive access
                            # This helps with formatting where column names may be accessed in different cases
                            lower_key = columns[i].lower()
                            if lower_key not in result:
                                result[lower_key] = value
                        
                        # Print the first result to help debug
                        if len(results) == 0:
                            logger.info(f"First result keys: {list(result.keys())}")
                            
                        results.append(result)
                    
                    # If we have results, make sure each result has the total_count field for formatting
                    if results:
                        for result in results:
                            result['total_count'] = total_count
                            result['total_projects'] = total_count
                    
                    logger.info(f"Query results with total_count={total_count} and {len(results)} results")
                    return total_count, results
                else:
                    # Single query case
                    cursor.execute(query)
                    columns = [desc[0] for desc in cursor.description]
                    results = []
                    logger.info(f"Single query columns: {columns}")
                    for row in cursor.fetchall():
                        result = {}
                        for i, value in enumerate(row):
                            # Store the original column name
                            result[columns[i]] = value
                            
                            # Also store lowercase version for case-insensitive access
                            lower_key = columns[i].lower()
                            if lower_key not in result:
                                result[lower_key] = value
                        results.append(result)
                    return results
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            logger.error(f"Query was: {query}")
            raise SQLQueryError(f"Database error: {str(e)}", str(query), "execution")

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
                    
                    # Execute query
                    logger.info(f"Executing SQL query: {sql_query}")
                    results = await self.execute_query(sql_query)
                    
                    # Format response using the format_response function
                    return await self.format_response(results, sql_query, 0.1, user_query, query_type)
                    
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
        """Process a user query and return formatted results"""
        try:
            # Get query type and SQL query
            sql_query, query_type = await self.generate_sql_query(user_query)
            
            # Execute SQL query
            start_time = time.time()
            results = await self.execute_query(sql_query)
            query_time = time.time() - start_time
            
            # Create metadata
            metadata = {
                "total_results": len(results) if isinstance(results, list) else results[0] if isinstance(results, tuple) else 0,
                "query_time": f"{query_time:.2f}s",
                "sql_query": sql_query[1] if isinstance(sql_query, tuple) else sql_query,
                "original_query": user_query,
                "query_type": query_type
            }
            
            # Format response
            response = await self.format_response(
                query_results=results,
                sql_query=sql_query,
                query_time=query_time,
                user_query=user_query,
                query_type=query_type,
                additional_data=metadata
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "response": "I encountered an error while processing your query. Please try again.",
                "metadata": {
                    "error": str(e),
                    "original_query": user_query
                }
            }

    async def execute_query_from_natural_language(self, user_query: str) -> Dict[str, Any]:
        """Execute a query from natural language and return results"""
        try:
            logger.info(f"Processing natural language query: {user_query}")
            start_time = time.time()
            
            # Generate the SQL query
            try:
                sql_query, query_type = await self.generate_sql_query(user_query)
                logger.info(f"Generated SQL query: {sql_query}, type: {query_type}")
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
                # Use the appropriate SQL query for display in metadata
                actual_sql = sql_query[1] if isinstance(sql_query, tuple) and len(sql_query) == 2 else sql_query
                return await self.format_response(
                    results=results,
                    sql_query=actual_sql,
                    query_time=query_time,
                    user_query=user_query,
                    query_type=query_type
                )
                
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
                        "sql_query": sql_query[1] if isinstance(sql_query, tuple) else sql_query
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

    async def _extract_district(self, query: str) -> str:
        """Extract district name from query text using enhanced pattern matching"""
        logger.info(f"Extracting district from query: {query}")
        
        # First check for exact district name matches
        for district in self.valid_districts:
            # Check for exact district name in the query
            if district.lower() in query.lower():
                logger.info(f"Found exact district match: {district}")
                return district
        
        # Check for district variations
        for variation, district in self.district_variations.items():
            if variation.lower() in query.lower():
                logger.info(f"Found district variation: {variation} -> {district}")
                return district
        
        # Common patterns for district queries
        patterns = [
            # Direct district mentions
            r'(?:in|at|from|of|for)\s+(?:the\s+)?([a-zA-Z\s]+?)(?:\s+district|\s*(?:$|[,\.]|\s+(?:and|or|projects?|sector)))',
            r'([a-zA-Z\s]+?)\s+district\b',
            r'\b([a-zA-Z]+)(?:\s+projects?|\s+region|\s+area)\b',
            
            # Question-based patterns
            r'(?:which|what|show|list)\s+projects?\s+(?:are|exist|located)\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\s+district)?\s*[?]?',
            r'(?:can you|please)\s+(?:show|list|display)\s+(?:me|all)\s+projects?\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\s+district)?',
            r'(?:i want|need)\s+to\s+(?:see|find|get)\s+projects?\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\s+district)?',
            
            # Direct patterns
            r'projects?\s+(?:in|at|located in|based in)\s+([a-zA-Z\s]+?)(?:\s+district)?',
            r'(?:list|show|display)\s+projects?\s+(?:from|in|at)\s+([a-zA-Z\s]+?)(?:\s+district)?',
            r'(?:find|search for)\s+projects?\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\s+district)?',
            
            # Complex patterns
            r'(?:tell|give)\s+me\s+(?:about|information about)\s+projects?\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\s+district)?',
            r'(?:looking for|need information about)\s+projects?\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\s+district)?',
            r'(?:what are|show me)\s+the\s+projects?\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\s+district)?',
            
            # Simpler patterns for direct district mentions
            r'\b([a-zA-Z]+)\s+district\b',
            r'\bin\s+([a-zA-Z]+)\b',
            r'\bprojects\s+in\s+([a-zA-Z]+)\b'
        ]
        
        query = query.lower()
        
        # Try pattern matching
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                district = match.group(1).strip()
                # Clean up the district name
                district = re.sub(r'\s+', ' ', district)  # Normalize spaces
                district = ' '.join(word.title() for word in district.split())  # Title case
                # Remove common words that might be captured
                district = re.sub(r'\b(The|And|Or|Projects?|In|At|From|Of|For)\b', '', district, flags=re.IGNORECASE)
                district = district.strip()
                if district:
                    logger.info(f"Found district through pattern matching: {district}")
                    return self._validate_district(district)
        
        return None
        
        # If no pattern match, check for direct district mentions
        for district in self.valid_districts:
            if district.lower() in query:
                logger.info(f"Found district through direct mention: {district}")
                return district
        
        # If still no match, try fuzzy matching with words that start with uppercase
        words = [word for word in query.split() if word[0].isupper()]
        for word in words:
            district = self._validate_district(word)
            if district:
                logger.info(f"Found district through fuzzy matching: {district}")
                return district
        
        logger.info("No district found in query")
        return ""
        
    def _validate_district(self, district: str) -> str:
        """Validate and normalize district name using fuzzy matching"""
        if not district:
            return ""
            
        district = district.strip().title()
        logger.info(f"Validating district name: {district}")
        
        # Check for exact match (case insensitive)
        for valid_district in self.valid_districts:
            if valid_district.lower() == district.lower():
                logger.info(f"Exact match found: {valid_district}")
                return valid_district
        
        # Check variations mapping
        normalized_key = district.lower().replace(" ", "")
        if normalized_key in self.district_variations:
            logger.info(f"Variation match found: {district} -> {self.district_variations[normalized_key]}")
            return self.district_variations[normalized_key]
        
        # Check if the district name is contained in any valid district
        for valid_district in self.valid_districts:
            if district.lower() in valid_district.lower() or valid_district.lower() in district.lower():
                logger.info(f"Substring match found: {district} -> {valid_district}")
                return valid_district
        
        # Fuzzy match using difflib
        from difflib import get_close_matches
        matches = get_close_matches(district, self.valid_districts, n=1, cutoff=0.6)  # Lower cutoff for better matching
        if matches:
            logger.info(f"Fuzzy match found: {district} -> {matches[0]}")
            return matches[0]
        
        # If all else fails, try matching the first few characters
        for valid_district in self.valid_districts:
            if len(district) >= 3 and valid_district.lower().startswith(district.lower()[:3]):
                logger.info(f"Prefix match found: {district} -> {valid_district}")
                return valid_district
        
        logger.warning(f"No valid district match found for: {district}")
        return ""

    async def _extract_sector(self, user_query: str) -> Optional[str]:
        """Extract sector from user query with enhanced pattern matching"""
        if not user_query:
            return None
            
        try:
            # Normalize the user query
            normalized_query = user_query.lower()
            logger.info(f"Extracting sector from query: {normalized_query}")
            
            # Define all valid sectors
            valid_sectors = [
                "Education", 
                "Roads and bridges", 
                "Commercial services", 
                "Health", 
                "Water and sanitation", 
                "Agriculture and environment", 
                "Community security initiatives"
            ]
            
            # First check for exact sector name matches
            for sector in valid_sectors:
                # Check for exact sector name in the query
                if sector.lower() in normalized_query:
                    logger.info(f"Found exact sector match: {sector}")
                    return sector
            
            # Check for sector-specific indicators in the query
            if "sector" in normalized_query:
                logger.info(f"Found 'sector' keyword in query: {user_query}")
                
                # Extract what sector they're asking about using exact sector names
                sector_patterns = [
                    r"\b(education|roads and bridges|commercial services|health|water and sanitation|agriculture and environment|community security initiatives)\s+sector",
                    r"sector\s+of\s+(education|roads and bridges|commercial services|health|water and sanitation|agriculture and environment|community security initiatives)",
                    r"sector\s+projects\s+in\s+(education|roads and bridges|commercial services|health|water and sanitation|agriculture and environment|community security initiatives)",
                    r"(education|roads and bridges|commercial services|health|water and sanitation|agriculture and environment|community security initiatives)\s+sector\s+projects"
                ]
                
                for pattern in sector_patterns:
                    match = re.search(pattern, normalized_query)
                    if match:
                        sector = match.group(1)
                        logger.info(f"Extracted sector '{sector}' from pattern")
                        # Return the exact sector name from the database with proper capitalization
                        for valid_sector in valid_sectors:
                            if valid_sector.lower() == sector.lower():
                                return valid_sector
            
            # Check for education-specific keywords
            education_keywords = ["school", "classroom", "education", "teacher", "student", "learning", "teaching", "college", "university"]
            for keyword in education_keywords:
                if keyword in normalized_query:
                    logger.info(f"Found Education sector via keyword '{keyword}'")
                    return "Education"
            
            # Check for health-specific keywords
            health_keywords = ["hospital", "clinic", "health", "medical", "healthcare", "doctor", "nurse", "patient", "disease", "treatment", "medicine"]
            for keyword in health_keywords:
                if keyword in normalized_query:
                    logger.info(f"Found Health sector via keyword '{keyword}'")
                    return "Health"
            
            # Check for roads and bridges-specific keywords
            roads_keywords = ["road", "bridge", "highway", "street", "transport", "transportation", "traffic", "infrastructure"]
            for keyword in roads_keywords:
                if keyword in normalized_query:
                    logger.info(f"Found Roads and bridges sector via keyword '{keyword}'")
                    return "Roads and bridges"
            
            # Check for water-specific keywords
            water_keywords = ["water", "sanitation", "hygiene", "toilet", "borehole", "well", "tap", "sewage", "drainage"]
            for keyword in water_keywords:
                if keyword in normalized_query:
                    logger.info(f"Found Water and sanitation sector via keyword '{keyword}'")
                    return "Water and sanitation"
            
            # Check for agriculture-specific keywords
            agriculture_keywords = ["agriculture", "farming", "crop", "livestock", "irrigation", "environment", "conservation", "forest", "land"]
            for keyword in agriculture_keywords:
                if keyword in normalized_query:
                    logger.info(f"Found Agriculture and environment sector via keyword '{keyword}'")
                    return "Agriculture and environment"
            
            # Check for commercial services-specific keywords
            commercial_keywords = ["market", "business", "commercial", "trade", "shop", "store", "enterprise", "economic", "commerce"]
            for keyword in commercial_keywords:
                if keyword in normalized_query:
                    logger.info(f"Found Commercial services sector via keyword '{keyword}'")
                    return "Commercial services"
            
            # Check for security-specific keywords
            security_keywords = ["security", "police", "safety", "protection", "crime", "community", "guard", "patrol"]
            for keyword in security_keywords:
                if keyword in normalized_query:
                    logger.info(f"Found Community security initiatives sector via keyword '{keyword}'")
                    return "Community security initiatives"
            
            # If no direct match, use keyword mapping from self.sector_mapping
            if hasattr(self, 'sector_mapping') and self.sector_mapping:
                for sector, keywords in self.sector_mapping.items():
                    for keyword in keywords:
                        pattern = rf"\b{keyword.lower()}\b"
                        if re.search(pattern, normalized_query):
                            logger.info(f"Found sector {sector} via sector_mapping keyword '{keyword}'")
                            return sector
                        
            logger.info("No sector found in query")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting sector: {str(e)}")
            logger.error(traceback.format_exc())
            return None

    async def _extract_project_name(self, query: str) -> str:
        """Extract project name from query text using enhanced pattern matching"""
        logger.info(f"Extracting project name from query: {query}")
        
        query = query.strip()
        
        # Special case for Nyandule Classroom Block
        if "nyandule" in query.lower() and "classroom" in query.lower():
            logger.info("Found Nyandule Classroom Block project through direct keyword matching")
            return "Nyandule Classroom Block"
        
        # Common patterns for project name queries - these should be more specific
        patterns = [
            # Direct "tell me about X project" pattern
            r'tell me about (?:the\s+)?([^?.]+?(?:\s+(?:project|block|building|school|hospital|bridge|road|center|centre|classroom)))\s*(?:\?|$|\.)',
            
            # Direct "what is X project" pattern
            r'what is (?:the\s+)?([^?.]+?(?:\s+(?:project|block|building|school|hospital|bridge|road|center|centre|classroom)))\s*(?:\?|$|\.)',
            
            # Project name in quotes
            r'["\']([^"\']+?)(?:\s+(?:project|block|building|school|hospital|bridge|road|center|centre|classroom))?["\']',
            
            # Specific pattern for classroom blocks
            r'(?:^|\s+)([\w\s]+?\s+classroom\s+block)(?:\s+project)?\s*(?:\?|$|\.)',
            
            # Pattern for project codes
            r'(?:project|code)\s+(?:code\s+)?(MW-[A-Za-z]{2}-[A-Z0-9]{2})'
        ]
        
        # Try each pattern
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                project_name = match.group(1).strip()
                # Clean up the extracted name
                project_name = re.sub(r'\s+', ' ', project_name)  # Normalize spaces
                project_name = project_name.strip()
                # Remove the word "project" if it appears at the end
                project_name = re.sub(r'\s+project$', '', project_name, flags=re.IGNORECASE)
                if project_name:
                    logger.info(f"Found project name through pattern matching: {project_name}")
                    return project_name
        
        logger.info("No project name found in query")
        return ""

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
