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
            # Default query to select all projects with correct column names
            base_query = """
                SELECT p.id, p.project_name, p.description, p.region, p.district, 
                       p.status, p.start_date, p.budget, p.completion_percentage, p.sector
                FROM projects p
                WHERE 1=1
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
                    base_query += f" AND (p.region LIKE '%{location}%' OR p.district LIKE '%{location}%')"
                    logger.info(f"Added location filter: {location}")
            
            # Extract status filters
            statuses = ['completed', 'in progress', 'planned']
            for status in statuses:
                if status in query_lower:
                    filters['status'] = status
                    base_query += f" AND LOWER(p.status) = '{status.lower()}'"
                    logger.info(f"Added status filter: {status}")
            
            # Extract sector filters
            if 'sector' in query_lower:
                sectors = re.findall(r'sector\s+(\w+(?:\s+\w+)*)', query_lower, re.IGNORECASE)
                if sectors:
                    sector = sectors[0]
                    if sector.lower() != 'projects':  # Skip if sector is just "projects"
                        filters['sector'] = sector
                        base_query += f" AND LOWER(p.sector) LIKE LOWER('%{sector}%')"
                        logger.info(f"Added sector filter: {sector}")
            elif any(sector in query_lower for sector in ['health', 'education', 'security', 'water']):
                # Extract sector from keywords
                for sector in ['health', 'education', 'security', 'water']:
                    if sector in query_lower:
                        filters['sector'] = sector
                        base_query += f" AND LOWER(p.sector) LIKE LOWER('%{sector}%')"
                        logger.info(f"Added sector filter from keyword: {sector}")
                        break
            
            # Extract date filters
            if 'recent' in query_lower:
                filters['recent'] = True
                base_query += " ORDER BY p.start_date DESC"
                logger.info("Added recent filter")
            elif 'oldest' in query_lower:
                filters['oldest'] = True
                base_query += " ORDER BY p.start_date ASC"
                logger.info("Added oldest filter")
            else:
                base_query += " ORDER BY p.start_date DESC"  # Default to most recent
            
            logger.info(f"Final SQL query: {base_query}")
            return base_query, filters
            
        except Exception as e:
            logger.error(f"Error parsing query: {str(e)}")
            return "SELECT * FROM projects ORDER BY start_date DESC", {} 