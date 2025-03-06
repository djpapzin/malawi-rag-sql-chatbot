import re
import logging
import os
import sys
from typing import Dict, Any, Tuple, List
from datetime import datetime
from app.llm_classification.hybrid_classifier import HybridClassifier
from app.services.llm_service import LLMService

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

class QueryParser:
    """Parser for natural language queries to SQL"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.logger = logging.getLogger(__name__)
        self.classifier = HybridClassifier()
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
        
    async def parse_query(self, query: str, classification: Dict = None) -> Dict[str, Any]:
        """Parse a natural language query into SQL"""
        self.logger.info(f"Parsing query: {query}")
        
        # Initialize response
        response = {
            "type": "general",
            "query": "",
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "original_query": query
            }
        }

        # Get query classification from LLM if not provided
        if not classification:
            classification = await self.llm_service.classify_query(query)

        # Extract key information based on classification
        if classification["query_type"] == "specific":
            # Handle specific project query
            project_info = await self._extract_project_info(query, classification)
            if project_info:
                response["query"] = self._build_specific_project_sql(project_info)
                response["type"] = "specific"
                response["metadata"].update(project_info)
        else:
            # Handle general query
            filters = await self._extract_filters(query, classification)
            response["query"] = self._build_general_query_sql(filters)
            response["metadata"]["filters"] = filters

        return response

    async def _extract_project_info(self, query: str, classification: Dict) -> Dict:
        """Extract project information using LLM and basic patterns"""
        # First try LLM extraction
        project_info = classification.get("context", {}).get("project_info", {})
        
        if not project_info:
            # Fallback to basic pattern matching
            for pattern in [
                r"(?:about|details?|info(?:rmation)?|tell me about|show me|what is)(?: the)? (.+?)(?:\s*\?|\s*$)",
                r"(.+?)(?:\s+project|\s+construction)(?:\s*\?|\s*$)",
            ]:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    project_name = match.group(1).strip()
                    project_info = {"name": project_name}
                    break

        return project_info

    async def _extract_filters(self, query: str, classification: Dict) -> Dict:
        """Extract filter information using LLM and patterns"""
        # Start with LLM-extracted filters
        filters = classification.get("context", {}).get("extracted_filters", {})
        
        # Enhance with pattern matching if needed
        if not filters.get("district"):
            filters["district"] = self._extract_district(query)
        if not filters.get("sector"):
            filters["sector"] = self._extract_sector(query)
        if not filters.get("status"):
            filters["status"] = self._extract_status(query)

        return filters

    def _build_specific_project_sql(self, project_info: Dict) -> str:
        """Build SQL for specific project query"""
        conditions = []
        
        if project_name := project_info.get("name"):
            # Use fuzzy matching for project names
            project_name = project_name.replace("'", "''")
            conditions.append(f"similarity(LOWER(project_name), LOWER('{project_name}')) > 0.6")
        
        if project_code := project_info.get("code"):
            conditions.append(f"project_code = '{project_code}'")
            
        if not conditions:
            return ""
            
        return f"""
            SELECT *
            FROM projects
            WHERE {' OR '.join(conditions)}
            ORDER BY 
                CASE 
                    WHEN LOWER(project_name) = LOWER('{project_info.get("name", "")}') THEN 1
                    ELSE 2
                END,
                similarity(LOWER(project_name), LOWER('{project_info.get("name", "")}')) DESC
            LIMIT 5
        """

    def _build_general_query_sql(self, filters: Dict) -> str:
        """Build SQL for general project query"""
        conditions = []
        
        if district := filters.get("district"):
            conditions.append(self._build_district_condition(district))
        if sector := filters.get("sector"):
            conditions.append(self._build_sector_condition(sector))
        if status := filters.get("status"):
            conditions.append(self._build_status_condition(status))
            
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        return f"""SELECT *
            FROM projects
            WHERE {where_clause}
            ORDER BY completion_percentage DESC, project_name
            LIMIT 10"""
    
    def _build_district_condition(self, district: str) -> str:
        """Build district filter condition with fuzzy matching"""
        district = district.replace("'", "''")
        return f"""(
            LOWER(district) = LOWER('{district}') OR 
            LOWER(district) LIKE LOWER('%{district}%') OR
            similarity(LOWER(district), LOWER('{district}')) > 0.4
        )"""

    def _build_sector_condition(self, sector: str) -> str:
        """Build sector filter condition with fuzzy matching"""
        sector = sector.replace("'", "''")
        return f"""(
            LOWER(sector) = LOWER('{sector}') OR
            LOWER(sector) LIKE LOWER('%{sector}%') OR
            similarity(LOWER(sector), LOWER('{sector}')) > 0.4
        )"""

    def _build_status_condition(self, status: str) -> str:
        """Build status filter condition"""
        status_map = {
            "ongoing": "In Progress",
            "in progress": "In Progress",
            "active": "In Progress",
            "running": "In Progress",
            "complete": "Completed",
            "completed": "Completed",
            "finished": "Completed",
            "done": "Completed",
            "planned": "Planned",
            "upcoming": "Planned",
            "proposed": "Planned",
            "pending": "Pending",
            "delayed": "Pending",
            "on hold": "Pending"
        }
        mapped_status = status_map.get(status.lower(), status)
        return f"LOWER(status) = LOWER('{mapped_status}')"

    def _extract_sector(self, query: str) -> str:
        """Extract sector from query text"""
        # Common patterns for sectors
        patterns = [
            # Direct sector mentions
            r"\b(?:in\s+the\s+)?(school|education|health|hospital|clinic|road|transport|water|sanitation|agriculture|farming)\s+(?:sector|projects?|facilities?|infrastructure)?\b",
            r"(?:sector|projects?|facilities?|infrastructure)\s+(?:in|for|about)\s+(school|education|health|hospital|clinic|road|transport|water|sanitation|agriculture|farming)\b",
            
            # Question-based patterns
            r"(?:what|which|show|list)\s+(?:are\s+the\s+)?(school|education|health|hospital|clinic|road|transport|water|sanitation|agriculture|farming)\s+(?:sector\s+)?projects?\b",
            r"(?:tell\s+me\s+about|show\s+me|list)\s+(?:the\s+)?(school|education|health|hospital|clinic|road|transport|water|sanitation|agriculture|farming)\s+(?:sector\s+)?projects?\b",
            
            # Natural language patterns
            r"(?:i\s+want|need)\s+to\s+(?:see|find|get)\s+(?:information\s+about\s+)?(school|education|health|hospital|clinic|road|transport|water|sanitation|agriculture|farming)\s+(?:sector\s+)?projects?\b",
            r"(?:looking\s+for|interested\s+in)\s+(?:information\s+about\s+)?(school|education|health|hospital|clinic|road|transport|water|sanitation|agriculture|farming)\s+(?:sector\s+)?projects?\b"
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
            # Direct status mentions
            r"\b(?:that\s+(?:are|is)\s+)?(ongoing|in progress|complete|completed|done|finished|approved|planned|pending)\b",
            r"\b(ongoing|in progress|complete|completed|done|finished|approved|planned|pending)\s+(?:projects?|status)\b",
            
            # Question-based patterns
            r"(?:what|which|show|list)\s+(?:are\s+the\s+)?(ongoing|in progress|complete|completed|done|finished|approved|planned|pending)\s+projects?\b",
            r"(?:tell\s+me\s+about|show\s+me|list)\s+(?:the\s+)?(ongoing|in progress|complete|completed|done|finished|approved|planned|pending)\s+projects?\b",
            
            # Natural language patterns
            r"(?:i\s+want|need)\s+to\s+(?:see|find|get)\s+(?:information\s+about\s+)?(ongoing|in progress|complete|completed|done|finished|approved|planned|pending)\s+projects?\b",
            r"(?:looking\s+for|interested\s+in)\s+(?:information\s+about\s+)?(ongoing|in progress|complete|completed|done|finished|approved|planned|pending)\s+projects?\b"
        ]
        
        query = query.lower()
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                status = match.group(1)
                return status
                
        return ""

    def _extract_district(self, query: str) -> str:
        """Extract district name from query text
        
        Args:
            query (str): The query text to extract district from
            
        Returns:
            str: Extracted district name or empty string if not found
        """
        # Common patterns for district queries
        patterns = [
            # Direct district queries
            r'(?:in|at|from|of) (?:the )?([a-zA-Z\s]+?) district',
            r'(?:projects|list).* (?:in|located in|based in|for) ([a-zA-Z\s]+?)(?: district)?',
            r'([a-zA-Z\s]+?) (?:district|region).* projects',
            r'show (?:me|all) projects.* ([a-zA-Z\s]+?)',
            r'(?:what|which|any) projects (?:are|exist|located) (?:in|at) ([a-zA-Z\s]+?)',
            
            # Question-based patterns
            r'(?:which|what) projects (?:are|exist|located) (?:in|at) ([a-zA-Z\s]+?)(?: district)?\s*[?]?',
            r'(?:can you|please) (?:show|list|display) (?:me|all) projects (?:in|at) ([a-zA-Z\s]+?)(?: district)?',
            r'(?:i want|need) to (?:see|find|get) projects (?:in|at) ([a-zA-Z\s]+?)(?: district)?',
            
            # Direct patterns
            r'projects (?:in|at|located in|based in) ([a-zA-Z\s]+?)(?: district)?',
            r'(?:list|show|display) projects (?:from|in|at) ([a-zA-Z\s]+?)(?: district)?',
            r'(?:find|search for) projects (?:in|at) ([a-zA-Z\s]+?)(?: district)?',
            
            # Complex patterns
            r'(?:tell|give) me (?:about|information about) projects (?:in|at) ([a-zA-Z\s]+?)(?: district)?',
            r'(?:looking for|need information about) projects (?:in|at) ([a-zA-Z\s]+?)(?: district)?',
            r'(?:what are|show me) the projects (?:in|at) ([a-zA-Z\s]+?)(?: district)?',
            
            # Additional variations
            r'(?:what|which) (?:infrastructure|development) projects (?:are|exist) (?:in|at) ([a-zA-Z\s]+?)(?: district)?',
            r'(?:tell me|show me) (?:about|all) (?:the )?projects (?:that are|which are) (?:in|at) ([a-zA-Z\s]+?)(?: district)?',
            r'(?:i am|i\'m) (?:looking for|interested in) projects (?:in|at) ([a-zA-Z\s]+?)(?: district)?',
            r'(?:can you|please) (?:tell me|show me) (?:about|all) projects (?:in|at) ([a-zA-Z\s]+?)(?: district)?',
            r'(?:what|which) (?:kinds of|types of) projects (?:are|exist) (?:in|at) ([a-zA-Z\s]+?)(?: district)?',
            r'(?:give me|show me) a (?:list of|summary of) projects (?:in|at) ([a-zA-Z\s]+?)(?: district)?',
            r'(?:what|which) projects (?:can you|do you) (?:find|show) (?:in|at) ([a-zA-Z\s]+?)(?: district)?',
            r'(?:i need|i want) to (?:know about|see) projects (?:in|at) ([a-zA-Z\s]+?)(?: district)?',
            r'(?:are there|do you have) (?:any )?projects (?:in|at) ([a-zA-Z\s]+?)(?: district)?',
            r'(?:please|can you) (?:list|show) (?:all )?projects (?:from|in|at) ([a-zA-Z\s]+?)(?: district)?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                district = match.group(1).strip()
                # Clean up the district name
                district = re.sub(r'\s+', ' ', district)  # Normalize spaces
                district = ' '.join(word.title() for word in district.split())  # Title case
                return district
        
        return ""

    def _build_district_query(self, district: str) -> str:
        """Build SQL query fragment for district filtering"""
        # Escape single quotes
        district = district.replace("'", "''")
        
        # Split district name into words
        words = district.split()
        
        if len(words) == 1:
            # For single-word districts, use exact match
            return f"LOWER(district) = LOWER('{district}')"
        else:
            # For multi-word districts, use regex pattern with word boundaries
            pattern = r'\b' + r'\b.*\b'.join(words) + r'\b'
            return f"LOWER(district) ~ LOWER('{pattern}')"