import re
import logging
from typing import Dict, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class QueryParser:
    """Parser for natural language queries to SQL"""
    
    def __init__(self):
        logger.info("Initializing QueryParser")
        pass
        
    def parse_query(self, query: str) -> str:
        """Parse a natural language query into SQL"""
        logger.info(f"Parsing query: {query}")
        sql_query, _ = self.parse_query_intent(query)
        logger.info(f"Generated SQL: {sql_query}")
        return sql_query
    
    def parse_query_intent(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Parse user query to determine intent and extract filters"""
        try:
            logger.info(f"Parsing query intent: {query}")
            
            # Check if this is a specific project query
            is_specific = any(phrase in query.lower() for phrase in [
                'tell me more about', 'show details for', 'details of',
                'more information about', 'specific details'
            ])
            
            # Select fields based on query type
            if is_specific:
                # Specific project query - include all detailed fields
                fields = """
                    PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                    TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR,
                    CONTRACTORNAME, SIGNINGDATE, TOTALEXPENDITURETODATE,
                    FUNDINGSOURCE, PROJECTCODE, LASTVISIT
                """
            else:
                # General project query - basic fields only
                fields = """
                    PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                    TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                """
            
            # Base query with selected fields
            base_query = f"""
                SELECT {fields}
                FROM proj_dashboard
                WHERE ISLATEST = 1
            """
            
            filters = {}
            query_lower = query.lower()
            
            # Extract project name for specific queries
            if is_specific:
                project_names = re.findall(r'(?:about|for|of)\s+([^?.,]+?)(?:\s+project)?\s*(?:\?|$|\.)', query_lower)
                if project_names:
                    project_name = project_names[0].strip()
                    filters['project_name'] = project_name
                    base_query += f" AND LOWER(PROJECTNAME) LIKE LOWER('%{project_name}%')"
                    logger.info(f"Added project name filter: {project_name}")
            
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
            sectors = ['education', 'health', 'water', 'sanitation', 'roads', 'transport']
            for sector in sectors:
                if sector in query_lower:
                    filters['sector'] = sector
                    base_query += f" AND LOWER(PROJECTSECTOR) LIKE LOWER('%{sector}%')"
                    logger.info(f"Added sector filter: {sector}")
            
            # Add order by
            base_query += " ORDER BY PROJECTNAME ASC"
            
            logger.info(f"Final SQL query: {base_query}")
            return base_query, filters
            
        except Exception as e:
            logger.error(f"Error parsing query intent: {str(e)}")
            # Return a safe default query that matches the schema
            return """
                SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
                ORDER BY PROJECTNAME ASC
            """, {}