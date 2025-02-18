import re
import logging
from typing import Dict, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class QueryParser:
    """Parser for natural language queries to SQL"""
    
    def __init__(self):
        logger.info("Initializing QueryParser")
        self.specific_query_patterns = [
            r'details?\s+(?:about|for|on)\s+["\'](.+?)["\']',  # "details about 'Project Name'"
            r'tell\s+me\s+about\s+["\'](.+?)["\']',          # "tell me about 'Project Name'"
            r'show\s+information\s+for\s+["\'](.+?)["\']',    # "show information for 'Project Name'"
            r'(?:project|code)\s+(?:code\s+)?(MW-[A-Z]{2}-[A-Z0-9]{2})',  # "project code MW-CR-DO" or "project MW-CR-DO"
            r'tell\s+me\s+about\s+project\s+([A-Za-z0-9-]+)',  # "tell me about project MW-CR-DO"
            r'show\s+details?\s+for\s+["\'](.+?)["\']'       # "show details for 'Project Name'"
        ]
        
    def parse_query(self, query: str) -> str:
        """Parse a natural language query into SQL"""
        logger.info(f"Parsing query: {query}")
        sql_query, _ = self.parse_query_intent(query)
        logger.info(f"Generated SQL: {sql_query}")
        return sql_query
    
    def is_specific_project_query(self, query: str) -> Tuple[bool, str]:
        """
        Check if the query is asking for specific project details.
        Returns (is_specific, project_identifier)
        """
        if not query:
            return False, ""
            
        query_lower = query.lower()
        
        # Check for project code pattern (e.g., MW-CR-DO)
        project_code_match = re.search(r'(?:^|\s)(MW-[A-Z]{2}-[A-Z0-9]{2})(?:\s|$)', query.upper())
        if project_code_match:
            logger.info(f"Found project code: {project_code_match.group(1)}")
            return True, project_code_match.group(1)
            
        # Check for project name patterns
        for pattern in self.specific_query_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                project_identifier = match.group(1)
                logger.info(f"Found project name/identifier: {project_identifier}")
                return True, project_identifier
                
        return False, ""

    def parse_query_intent(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Parse user query to determine intent and extract filters"""
        try:
            logger.info(f"Parsing query intent: {query}")
            
            # Check if this is a specific project query
            is_specific, project_identifier = self.is_specific_project_query(query)
            
            if is_specific:
                logger.info(f"Detected specific project query for: {project_identifier}")
                # If it looks like a project code
                if re.match(r'MW-[A-Z]{2}-[A-Z0-9]{2}', project_identifier.upper()):
                    return self._build_specific_project_sql(project_code=project_identifier), {
                        "query_type": "specific",
                        "filters": {"project_code": project_identifier}
                    }
                else:
                    return self._build_specific_project_sql(project_name=project_identifier), {
                        "query_type": "specific",
                        "filters": {"project_name": project_identifier}
                    }
            
            # Default query with correct table and column names
            base_query = """
                SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
            """
            
            filters = {}
            query_lower = query.lower()
            
            # Extract location filters
            locations = re.findall(r'in\s+(\w+(?:\s+\w+)*)', query_lower, re.IGNORECASE)
            if locations:
                location = locations[0]
                if location.lower() != 'progress':  # Skip if location is "progress"
                    filters['location'] = location
                    # Try to match either region or district
                    base_query += f" AND (LOWER(REGION) LIKE LOWER('%{location}%') OR LOWER(DISTRICT) LIKE LOWER('%{location}%'))"
                    logger.info(f"Added location filter: {location}")
            
            # Extract status filters
            statuses = ['completed', 'in progress', 'planned']
            for status in statuses:
                if status in query_lower:
                    filters['status'] = status
                    base_query += f" AND LOWER(PROJECTSTATUS) LIKE LOWER('%{status}%')"
                    logger.info(f"Added status filter: {status}")
            
            # Extract sector filters
            sectors = ['education', 'health', 'water', 'transport', 'agriculture']
            for sector in sectors:
                if sector in query_lower:
                    filters['sector'] = sector
                    base_query += f" AND LOWER(PROJECTSECTOR) LIKE LOWER('%{sector}%')"
                    logger.info(f"Added sector filter: {sector}")
            
            # Add order by
            base_query += " ORDER BY PROJECTNAME ASC"
            
            return base_query, {"query_type": "general", "filters": filters}
            
        except Exception as e:
            logger.error(f"Error parsing query intent: {str(e)}")
            raise

    def _build_specific_project_sql(self, project_code: str = None, project_name: str = None) -> str:
        """Build SQL query for specific project details"""
        sql = """
            SELECT 
                PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR,
                CONTRACTORNAME, SIGNINGDATE, TOTALEXPENDITURETODATE,
                FUNDINGSOURCE, PROJECTCODE, LASTVISIT,
                COMPLETIONPERCENTAGE, PROJECTDESC, TRADITIONALAUTHORITY,
                STAGE, STARTDATE, COMPLETIONESTIDATE
            FROM proj_dashboard
            WHERE ISLATEST = 1
        """
        
        if project_code:
            sql += f" AND UPPER(PROJECTCODE) = '{project_code.upper()}'"
        elif project_name:
            sql += f" AND LOWER(PROJECTNAME) LIKE LOWER('%{project_name}%')"
            
        sql += " LIMIT 1"
        
        return sql