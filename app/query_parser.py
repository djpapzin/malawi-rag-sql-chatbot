import re
import logging
import os
import sys
from typing import Dict, Any, Tuple, List
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

class QueryParser:
    """Parser for natural language queries to SQL"""
    
    def __init__(self):
        logger.info("Initializing QueryParser")
        self.specific_query_patterns = [
            # Direct project name queries
            r'(?:details?|tell me|what|show)\s+(?:about|for|on|is|the status of)\s+(?:the\s+)?["\'](.+?)["\'](?:\s+(?:project|construction|building))?(?:\s*\?)?$',
            r'show\s+(?:me\s+)?(?:the\s+)?details?\s+(?:about|for|of)\s+(?:the\s+)?["\'](.+?)["\'](?:\s+(?:project|construction))?(?:\s*\?)?$',
            r'(?:what is|how is)\s+(?:the\s+)?["\'](.+?)["\'](?:\s+(?:project|construction|building))?\s+(?:doing|going|progressing)(?:\s*\?)?$',
            r'what\s+is\s+the\s+status\s+of\s+["\'](.+?)["\'](?:\s+(?:project|construction))?(?:\s*\?)?$',
            r'give\s+me\s+details\s+(?:about|for|on)\s+["\'](.+?)["\'](?:\s+(?:project|construction))?(?:\s*\?)?$',
            r'project\s+overview\s+for\s+["\'](.+?)["\'](?:\s*\?)?$',
            r'expenditure\s+(?:for|of)\s+["\'](.+?)["\'](?:\s*\?)?$',
            r'contractor\s+(?:for|of)\s+["\'](.+?)["\'](?:\s*\?)?$',
            
            # Project code queries
            r'(?:project|code)\s+(?:code\s+)?(MW-[A-Z]{2}-[A-Z0-9]{2})',
            r'tell\s+me\s+about\s+project\s+([A-Za-z0-9-]+)',
            
            # Unquoted project name queries
            r'(?:details?|tell me|what|show)\s+(?:about|for|on|is|the status of)\s+(?:the\s+)?([^"\']+?)(?:\s+(?:project|construction|building))?(?:\s*\?)?$',
            r'show\s+(?:me\s+)?(?:the\s+)?details?\s+(?:about|for|of)\s+(?:the\s+)?([^"\']+?)(?:\s+(?:project|construction))?(?:\s*\?)?$'
        ]
        
    def _extract_project_name(self, text: str) -> Tuple[str, bool]:
        """Extract project name from text, handling both quoted and unquoted names"""
        # First try to find quoted project names (both single and double quotes)
        quoted_patterns = [
            r"'([^']+)'",  # Single quotes
            r'"([^"]+)"'   # Double quotes
        ]
        
        for pattern in quoted_patterns:
            match = re.search(pattern, text)
            if match:
                project_name = match.group(1).strip()
                # Remove any trailing periods or other punctuation
                project_name = re.sub(r'[.,;!?]+$', '', project_name)
                # Remove project/construction keywords if they appear at the end
                project_name = re.sub(r'\s+(?:project|construction)$', '', project_name, flags=re.IGNORECASE)
                return project_name, True
            
        # Then try to find unquoted project names after specific phrases
        phrases = [
            r"about\s+(.+?)(?:\s+(?:project|construction|building|status|budget|details?|progress|contractor|completion)|$)",
            r"show\s+(?:me\s+)?(?:the\s+)?(?:details?\s+(?:about|for|of)\s+)?(.+?)(?:\s+(?:project|construction|building|status|budget|details?|progress|contractor|completion)|$)",
            r"what\s+is\s+(?:the\s+)?(?:status|budget|progress)\s+(?:of|for)\s+(.+?)(?:\s+(?:project|construction|building|status|budget|details?|progress|contractor|completion)|$)",
            r"about\s+(.+?)(?:\s+(?:in|at|for|status|budget|details?)|$)",
            r"show\s+(?:me\s+)?(?:the\s+)?(?:details?\s+(?:about|for|of)\s+)?(.+?)(?:\s+(?:in|at|for|status|budget|details?)|$)",
            r"what\s+is\s+(?:the\s+)?(?:status|budget)\s+(?:of|for)\s+(.+?)(?:\s+(?:in|at|for|status|budget|details?)|$)",
            r"tell\s+me\s+about\s+(.+?)(?:\s+(?:in|at|for|status|budget|details?)|$)"
        ]
        
        for phrase in phrases:
            match = re.search(phrase, text, re.IGNORECASE)
            if match:
                project_name = match.group(1).strip()
                # Remove any trailing periods or other punctuation
                project_name = re.sub(r'[.,;!?]+$', '', project_name)
                # Remove project/construction keywords if they appear at the end
                project_name = re.sub(r'\s+(?:project|construction)$', '', project_name, flags=re.IGNORECASE)
                return project_name, False
                
        return "", False

    def _extract_project_code(self, query: str) -> str:
        """Extract project code from query text
        
        Args:
            query (str): The query text to extract code from
            
        Returns:
            str: Extracted project code or empty string if not found
        """
        # Common patterns for project codes, ordered by specificity
        patterns = [
            # Full project code with MW prefix - return with MW prefix
            (r"(?:project|code)?\s*(?:code\s+)?(?:MW|mw)-([A-Za-z]{2}-[A-Za-z0-9]{2})\b", True),
            
            # Full project code without MW prefix - return as is
            (r"(?:project|code)?\s*(?:code\s+)?([A-Za-z]{2}-[A-Za-z0-9]{2})\b", False),
            
            # Regional code with MW prefix - return with MW prefix
            (r"(?:project|code)?\s*(?:code\s+)?(?:MW|mw)-([A-Za-z]{2})\b", True),
            
            # Just the region code - return as is
            (r"\b([A-Za-z]{2})\b(?:\s+(?:region|projects?|code)|\s+(?:region|projects?|code)\s+|\s*$)", False)
        ]
        
        query = query.upper()  # Convert to upper case for consistent matching
        
        for pattern, has_mw_prefix in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                code = match.group(1).upper()
                # Special handling for region codes
                if re.match(r'^[A-Z]{2}$', code):
                    if "REGION" in query or "PROJECTS" in query or "CODE" in query:
                        return code
                # Normal handling for other codes
                if has_mw_prefix:
                    return f"MW-{code}"
                return code
        
        return ""

    def _build_project_code_query(self, project_code: str) -> str:
        """Build SQL query fragment for project code filtering"""
        if not project_code:
            return ""
            
        project_code = project_code.upper()
        
        # Handle different code formats
        if project_code.startswith('MW-'):
            # Code already has MW prefix
            if re.match(r'^MW-[A-Z]{2}-[A-Z0-9]{2}$', project_code):
                # Full project code
                return f"AND PROJECTCODE = '{project_code}'"
            elif re.match(r'^MW-[A-Z]{2}$', project_code):
                # Regional code
                return f"AND PROJECTCODE LIKE '{project_code}-%'"
        else:
            # Code needs MW prefix
            if re.match(r'^[A-Z]{2}-[A-Z0-9]{2}$', project_code):
                # Full code without MW prefix
                return f"AND PROJECTCODE LIKE 'MW-{project_code}'"
            elif re.match(r'^[A-Z]{2}$', project_code):
                # Just region code
                return f"AND PROJECTCODE LIKE 'MW-{project_code}-%'"
        
        return ""

    def _build_project_name_query(self, project_name: str, is_quoted: bool) -> str:
        """Build SQL query for project name search"""
        if not project_name:
            return ""
        
        # Escape single quotes
        project_name = project_name.replace("'", "''")
        
        # Remove 'project' keyword if it appears at the end
        project_name = re.sub(r'\s+(?:project|construction|building)$', '', project_name, flags=re.IGNORECASE)
        
        # Build conditions with priority
        conditions = []
        
        # 1. Exact match (highest priority)
        conditions.append(f"LOWER(PROJECTNAME) = LOWER('{project_name}')")
        
        # 2. Exact match with project/construction suffix
        conditions.append(f"LOWER(PROJECTNAME) = LOWER('{project_name} project')")
        conditions.append(f"LOWER(PROJECTNAME) = LOWER('{project_name} construction')")
        
        # 3. Starts with match
        conditions.append(f"LOWER(PROJECTNAME) LIKE LOWER('{project_name}%')")
        
        # 4. Contains match with word boundaries
        conditions.append(f"LOWER(PROJECTNAME) LIKE LOWER('% {project_name} %')")
        
        # 5. For unquoted names, also try word matching
        if not is_quoted:
            words = [w for w in project_name.split() if len(w) >= 2 and w.lower() not in {'the', 'and', 'or', 'in', 'at', 'of', 'to', 'for', 'with', 'by'}]
            if words:
                word_conditions = []
                for word in words:
                    word_conditions.append(f"LOWER(PROJECTNAME) LIKE LOWER('% {word} %')")
                conditions.append(f"({' AND '.join(word_conditions)})")
                    
        where_clause = f"""AND (
            {' OR '.join(conditions)}
        )"""
        
        order_clause = f"""ORDER BY
            CASE 
                WHEN LOWER(PROJECTNAME) = LOWER('{project_name}') THEN 1
                WHEN LOWER(PROJECTNAME) = LOWER('{project_name} project') THEN 2
                WHEN LOWER(PROJECTNAME) = LOWER('{project_name} construction') THEN 3
                WHEN LOWER(PROJECTNAME) LIKE LOWER('{project_name}%') THEN 4
                WHEN LOWER(PROJECTNAME) LIKE LOWER('% {project_name} %') THEN 5
                ELSE 6
            END,
            CASE 
                WHEN LOWER(PROJECTSTATUS) = 'ongoing' THEN 1
                WHEN LOWER(PROJECTSTATUS) = 'completed' THEN 2
                ELSE 3
            END"""
        
        return f"{where_clause}\n{order_clause}"

    def _add_result_limits(self, base_query: str, query_type: str = "general") -> str:
        """Add LIMIT and ORDER BY clauses to improve result relevance
        
        Args:
            base_query (str): Base SQL query
            query_type (str): Type of query ("specific" or "general")
            
        Returns:
            str: Enhanced query with sorting and limits
        """
        # Define sort order based on project status
        status_order = """
            CASE 
                WHEN LOWER(PROJECTSTATUS) = 'ongoing' THEN 1
                WHEN LOWER(PROJECTSTATUS) = 'completed' THEN 2
                WHEN LOWER(PROJECTSTATUS) = 'approved' THEN 3
                ELSE 4
            END
        """
        
        # Define relevance sorting based on query type
        if query_type == "specific":
            # For specific queries, prioritize exact matches
            return f"""
            {base_query}
            ORDER BY 
                {status_order},
                TOTALBUDGET DESC
                LIMIT 1
            """
        else:
            # For general queries, limit to most relevant results
            return f"""
            {base_query}
            ORDER BY 
                {status_order},
                TOTALBUDGET DESC,
                COMPLETIONPERCENTAGE DESC
            LIMIT 10
            """
    
    def is_specific_project_query(self, query: str) -> Tuple[bool, str]:
        """Check if this is a query for a specific project"""
        # First check for project codes
        code_patterns = [
            r"(?:project|code)\s+(?:code\s+)?(?:MW-)?([A-Za-z]{2}-[A-Z0-9]{2})",
            r"(?:project|code)\s+([A-Za-z]{2}-[A-Z0-9]{2})",
            r"(?:MW|mw)-([A-Za-z]{2}-[A-Z0-9]{2})",
            r"(?:project|code)\s+([A-Za-z]{2})"
        ]
        
        for pattern in code_patterns:
            code_match = re.search(pattern, query, re.IGNORECASE)
            if code_match:
                code = code_match.group(1).upper()
                # Add MW- prefix if missing and matches format
                if not code.startswith('MW-'):
                    if re.match(r'^[A-Z]{2}-[A-Z0-9]{2}$', code):
                        code = f"MW-{code}"
                    elif re.match(r'^[A-Z]{2}$', code):
                        code = f"MW-{code}"
                return True, code
                
        # Then check for quoted project names
        project_name, is_quoted = self._extract_project_name(query)
        if project_name:
            return True, project_name
                
        return False, ""

    def _build_specific_project_sql(self, project_name: str = "", project_code: str = "") -> str:
        """Build SQL for specific project query"""
        conditions = []
        
        if project_name:
            # Escape single quotes
            project_name = project_name.replace("'", "''")
            
            # Try exact match first
            conditions.append(f"LOWER(PROJECTNAME) = LOWER('{project_name}')")
            
            # Then try partial matches
            conditions.append(f"LOWER(PROJECTNAME) LIKE LOWER('{project_name}%')")
            conditions.append(f"LOWER(PROJECTNAME) LIKE LOWER('%{project_name}%')")
            
            # Then try word matching for multi-word queries
            words = project_name.split()
            if len(words) > 1:
                word_conditions = []
                for word in words:
                    if len(word) >= 2 and word.lower() not in {'the', 'and', 'or', 'in', 'at', 'of', 'to', 'for', 'with', 'by'}:
                        word_conditions.append(f"LOWER(PROJECTNAME) LIKE LOWER('% {word} %')")
                if word_conditions:
                    conditions.append(f"({' AND '.join(word_conditions)})")
                    
        if project_code:
            code_conditions = []
            # Exact match
            code_conditions.append(f"PROJECTCODE = '{project_code}'")
            # Case-insensitive match
            code_conditions.append(f"LOWER(PROJECTCODE) = LOWER('{project_code}')")
            # Partial match
            code_conditions.append(f"LOWER(PROJECTCODE) LIKE LOWER('%{project_code}%')")
            conditions.append(f"({' OR '.join(code_conditions)})")
            
        where_clause = f"({' OR '.join(conditions)})" if conditions else "1=1"
        
        sql = f"""
            SELECT 
                PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR,
                CONTRACTORNAME, SIGNINGDATE, TOTALEXPENDITURETODATE,
                FUNDINGSOURCE, PROJECTCODE, LASTVISIT,
                COMPLETIONPERCENTAGE, PROJECTDESC, TRADITIONALAUTHORITY,
                STAGE, STARTDATE, COMPLETIONESTIDATE
                FROM proj_dashboard
                WHERE ISLATEST = 1
            AND {where_clause}
            ORDER BY
                CASE 
                    WHEN LOWER(PROJECTNAME) = LOWER('{project_name}') THEN 1
                    WHEN LOWER(PROJECTNAME) LIKE LOWER('{project_name}%') THEN 2
                    WHEN LOWER(PROJECTNAME) LIKE LOWER('%{project_name}%') THEN 3
                    ELSE 4
                END,
                CASE 
                    WHEN LOWER(PROJECTSTATUS) = 'ongoing' THEN 1
                    WHEN LOWER(PROJECTSTATUS) = 'completed' THEN 2
                    ELSE 3
                END
            LIMIT 1
        """
        return sql

    def _extract_sector(self, query: str) -> str:
        """Extract sector from query text"""
        # Common patterns for sectors
        patterns = [
            r"\b(?:in\s+the\s+)?(school|education|health|hospital|clinic|road|transport|water|sanitation|agriculture|farming)\s+(?:sector|projects?|facilities?|infrastructure)?\b",
            r"(?:sector|projects?|facilities?|infrastructure)\s+(?:in|for|about)\s+(school|education|health|hospital|clinic|road|transport|water|sanitation|agriculture|farming)\b"
        ]
        
        query = query.lower()
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                sector = match.group(1)
                return sector
                
        return ""

    def _extract_status(self, query: str) -> str:
        """Extract status from query text"""
        # Common patterns for statuses
        patterns = [
            r"\b(?:that\s+(?:are|is)\s+)?(ongoing|in progress|complete|completed|done|finished|approved|planned|pending)\b",
            r"\b(ongoing|in progress|complete|completed|done|finished|approved|planned|pending)\s+(?:projects?|status)\b"
        ]
        
        query = query.lower()
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                status = match.group(1)
                return status
                
        return ""

    def _build_sector_query(self, sector: str) -> str:
        """Build SQL query fragment for sector filtering"""
        if not sector:
            return ""
            
        sector = sector.strip().lower()
        
        # Map common terms to actual sectors
        sector_mapping = {
            "school": "education",
            "education": "education",
            "health": "health",
            "hospital": "health",
            "clinic": "health",
            "road": "transport",
            "transport": "transport",
            "water": "water",
            "sanitation": "water",
            "agriculture": "agriculture",
            "farming": "agriculture"
        }
        
        if sector in sector_mapping:
            mapped_sector = sector_mapping[sector]
            return f"AND LOWER(PROJECTSECTOR) = '{mapped_sector}'"
            
        return f"AND LOWER(PROJECTSECTOR) LIKE '%{sector}%'"

    def _build_status_query(self, status: str) -> str:
        """Build SQL query fragment for status filtering"""
        if not status:
            return ""
            
        status = status.strip().lower()
        
        # Map common terms to actual statuses
        status_mapping = {
            "ongoing": "in progress",
            "in progress": "in progress",
            "complete": "completed",
            "completed": "completed",
            "done": "completed",
            "finished": "completed",
            "approved": "approved",
            "planned": "planned",
            "pending": "planned"
        }
        
        if status in status_mapping:
            mapped_status = status_mapping[status]
            return f"AND LOWER(PROJECTSTATUS) = '{mapped_status}'"
            
        return f"AND LOWER(PROJECTSTATUS) LIKE '%{status}%'"

    def _build_completion_query(self, is_complete: bool) -> str:
        """Build SQL query for completed/incomplete projects"""
        status = 'yes' if is_complete else 'no'
        return f"""
        SELECT 
            projectname as project_name,
            district,
            projectsector as project_sector,
            projectstatus as project_status,
            COALESCE(budget, 0) as total_budget,
            COALESCE(completionpercentage, 0) as completion_percentage
        FROM proj_dashboard 
        WHERE LOWER(isprojectcomplete) = '{status}'
        ORDER BY total_budget DESC;
        """

    def _extract_location(self, query: str) -> str:
        """Extract location from query text"""
        # Common patterns for locations
        patterns = [
            r"\b(in|at|near|from)\s+([A-Za-z\s]+)",
            r"\b([A-Za-z\s]+)\s+(?:region|district|province|area)"
        ]
        
        query = query.lower()
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                location = match.group(2) if match.group(2) else match.group(1)
                return location.strip()
                
        return ""

    def _build_location_query(self, location: str) -> str:
        """Build SQL query fragment for location filtering"""
        if not location:
            return ""
            
        location = location.strip().lower()
        
        return f"AND (LOWER(REGION) LIKE '%{location}%' OR LOWER(DISTRICT) LIKE '%{location}%')"

    def _format_response(self, row: Dict[str, Any]) -> str:
        """Format a database row into a human-readable response"""
        response_parts = []
        
        # Project name and code
        response_parts.append(f"Project: {row.get('PROJECTNAME', 'Not available')}")
        if row.get('PROJECTCODE'):
            response_parts.append(f"Project Code: {row['PROJECTCODE']}")
            
        # Location
        district = row.get('DISTRICT', 'Not available')
        region = row.get('REGION', 'Not available')
        response_parts.append(f"Region: {region}")
        response_parts.append(f"District: {district}")
        
        # Status and sector
        if row.get('PROJECTSECTOR'):
            response_parts.append(f"Sector: {row['PROJECTSECTOR']}")
        if row.get('PROJECTSTATUS'):
            response_parts.append(f"Status: {row['PROJECTSTATUS']}")
            
        # Financial information
        if any(row.get(k) for k in ['TOTALBUDGET', 'TOTALEXPENDITURETODATE', 'FUNDINGSOURCE']):
            response_parts.append("\nFinancial Information:")
            if row.get('TOTALBUDGET'):
                response_parts.append(f"Total Budget: MWK {row['TOTALBUDGET']:,.2f}")
            if row.get('TOTALEXPENDITURETODATE'):
                response_parts.append(f"Expenditure to Date: MWK {row['TOTALEXPENDITURETODATE']:,.2f}")
            if row.get('FUNDINGSOURCE'):
                response_parts.append(f"Funding Source: {row['FUNDINGSOURCE']}")
                
        return "\n".join(response_parts)

    def parse_query(self, query: str) -> Dict[str, Any]:
        """Parse a natural language query into SQL"""
        logger.info(f"Parsing query: {query}")
        
        # Initialize response
        response = {
            "type": "general",
            "query": "",
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "original_query": query
            }
        }
        
        # First check if this is a specific project query
        project_code = self._extract_project_code(query)
        if project_code and not query.lower().startswith("show all"):
            response["type"] = "specific"
            response["metadata"]["project_code"] = project_code
            
            # Build base query for specific project
            base_query = """
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
            
            # Add project code condition
            base_query += f"\n{self._build_project_code_query(project_code)}"
            
            # Add limit
            base_query += "\nLIMIT 1"
            response["query"] = base_query
            return response
            
        # Check for project name
        project_name, is_quoted = self._extract_project_name(query)
        if project_name and not query.lower().startswith("show all"):
            response["type"] = "specific"
            response["metadata"]["project_name"] = project_name
            
            # Build base query for specific project
            base_query = """
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
            
            # Add project name condition
            base_query += f"\n{self._build_project_name_query(project_name, is_quoted)}"
            
            # Add limit
            base_query += "\nLIMIT 1"
            response["query"] = base_query
            return response
        
        # Handle general queries
        base_query = """
            SELECT 
                PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
            FROM proj_dashboard
            WHERE ISLATEST = 1
        """
        
        # Add filters for general queries
        filters = []
        
        # Location filter
        location = self._extract_location(query)
        if location:
            filters.append(self._build_location_query(location))
            response["metadata"]["location"] = location
            
        # Status filter
        status = self._extract_status(query)
        if status:
            filters.append(self._build_status_query(status))
            response["metadata"]["status"] = status
            
        # Sector filter
        sector = self._extract_sector(query)
        if sector:
            filters.append(self._build_sector_query(sector))
            response["metadata"]["sector"] = sector
            
        # Add all filters
        for filter_query in filters:
            if filter_query:
                base_query += f"\n{filter_query}"
                
        # Add sorting and limits
        response["query"] = self._add_result_limits(base_query, response["type"])
        return response