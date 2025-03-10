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
                "original_query": query,
                "confidence": 0.0,
                "intent": {},
                "entities": []
            }
        }

        # Get query classification from LLM
        if not classification:
            classification = await self.llm_service.classify_query(query)
        
        # Update metadata with LLM insights
        response["metadata"].update({
            "confidence": classification.get("confidence", 0.0),
            "intent": classification.get("context", {}).get("intent", {}),
            "entities": classification.get("context", {}).get("entities", [])
        })

        # Extract key information based on classification
        if classification["query_type"] == "specific":
            # Handle specific project query
            project_info = await self._extract_project_info(query, classification)
            if project_info:
                response["query"] = self._build_specific_project_sql(project_info)
                response["type"] = "specific"
                response["metadata"].update(project_info)
        else:
            # Handle general query using both LLM and pattern matching
            llm_filters = classification.get("context", {}).get("extracted_filters", {})
            pattern_filters = await self._extract_filters(query, classification)
            
            # Merge filters, preferring LLM results when confidence is high
            filters = {}
            for key in set(llm_filters.keys()) | set(pattern_filters.keys()):
                llm_value = llm_filters.get(key)
                pattern_value = pattern_filters.get(key)
                
                # Use LLM value if confidence is high, otherwise use pattern matching
                entity_confidence = next(
                    (e["confidence"] for e in response["metadata"]["entities"] 
                     if e["type"] == key and e["value"] == llm_value),
                    0.0
                )
                
                filters[key] = llm_value if entity_confidence > 0.7 else pattern_value

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
            # Use fuzzy matching for project names with lower threshold
            project_name = project_name.replace("'", "''")
            conditions.append(f"similarity(LOWER(PROJECTNAME), LOWER('{project_name}')) > 0.4")
        
        if project_code := project_info.get("code"):
            conditions.append(f"PROJECTCODE = '{project_code}'")
            
        if not conditions:
            return ""
            
            return f"""
            SELECT *
            FROM proj_dashboard
            WHERE {' OR '.join(conditions)}
            ORDER BY 
                CASE 
                    WHEN LOWER(PROJECTNAME) = LOWER('{project_info.get("name", "")}') THEN 1
                    ELSE 2
                END,
                similarity(LOWER(PROJECTNAME), LOWER('{project_info.get("name", "")}')) DESC
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
            FROM proj_dashboard
            WHERE {where_clause}
            ORDER BY COMPLETIONPERCENTAGE DESC, PROJECTNAME
            LIMIT 10"""
    
    def _build_district_condition(self, district: str) -> str:
        """Build district filter condition with fuzzy matching"""
        district = district.replace("'", "''")
        return f"""(
            LOWER(DISTRICT) = LOWER('{district}') OR 
            LOWER(DISTRICT) LIKE LOWER('%{district}%') OR
            similarity(LOWER(DISTRICT), LOWER('{district}')) > 0.4
        )"""

    def _build_sector_condition(self, sector: str) -> str:
        """Build sector filter condition with fuzzy matching"""
        sector = sector.replace("'", "''")
        
        # Sector-specific patterns
        sector_patterns = {
            'health': '%(health|medical|hospital|clinic)%',
            'education': '%(education|school|classroom|college|university)%',
            'water': '%(water|sanitation|sewage|borehole)%',
            'transport': '%(transport|road|bridge|highway)%',
            'agriculture': '%(agriculture|farming|irrigation)%'
        }
        
        pattern = sector_patterns.get(sector, f'%{sector}%')
        
        return f"""(
            LOWER(PROJECTSECTOR) SIMILAR TO '{pattern}' OR
            similarity(LOWER(PROJECTSECTOR), LOWER('{sector}')) > 0.4
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
        return f"LOWER(PROJECTSTATUS) = LOWER('{mapped_status}')"

    def _extract_sector(self, query: str) -> str:
        """Extract sector from query text"""
        # Common patterns for sectors
        patterns = [
            # Direct sector mentions
            r"\b(?:in\s+the\s+)?(health|medical|hospital|clinic|education|school|classroom|water|sanitation|transport|road|bridge|agriculture|farming)\s+(?:sector|projects?|facilities?|infrastructure)?\b",
            r"(?:sector|projects?|facilities?|infrastructure)\s+(?:in|for|about)\s+(health|medical|hospital|clinic|education|school|classroom|water|sanitation|transport|road|bridge|agriculture|farming)\b",
            
            # Question-based patterns
            r"(?:what|which|show|list)\s+(?:are\s+the\s+)?(health|medical|hospital|clinic|education|school|classroom|water|sanitation|transport|road|bridge|agriculture|farming)\s+(?:sector\s+)?projects?\b",
            r"(?:tell\s+me\s+about|show\s+me|list)\s+(?:the\s+)?(health|medical|hospital|clinic|education|school|classroom|water|sanitation|transport|road|bridge|agriculture|farming)\s+(?:sector\s+)?projects?\b",
            
            # Natural language patterns
            r"(?:i\s+want|need)\s+to\s+(?:see|find|get)\s+(?:information\s+about\s+)?(health|medical|hospital|clinic|education|school|classroom|water|sanitation|transport|road|bridge|agriculture|farming)\s+(?:sector\s+)?projects?\b",
            r"(?:looking\s+for|interested\s+in)\s+(?:information\s+about\s+)?(health|medical|hospital|clinic|education|school|classroom|water|sanitation|transport|road|bridge|agriculture|farming)\s+(?:sector\s+)?projects?\b",
            
            # Simple patterns
            r"\b(health|medical|hospital|clinic|education|school|classroom|water|sanitation|transport|road|bridge|agriculture|farming)\b"
        ]
        
        # Sector mapping for variations
        sector_mapping = {
            'medical': 'health',
            'hospital': 'health',
            'clinic': 'health',
            'school': 'education',
            'classroom': 'education',
            'road': 'transport',
            'bridge': 'transport',
            'farming': 'agriculture'
        }
        
        query = query.lower()
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                sector = match.group(1)
                # Map sector variations to standard sectors
                return sector_mapping.get(sector, sector)
                
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
        """Extract district name from query text"""
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
            
            # Additional variations
            r'(?:what|which)\s+(?:infrastructure|development)\s+projects?\s+(?:are|exist)\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\s+district)?',
            r'(?:tell me|show me)\s+(?:about|all)\s+(?:the\s+)?projects?\s+(?:that are|which are)\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\s+district)?',
            r'(?:i am|i\'m)\s+(?:looking for|interested in)\s+projects?\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\s+district)?',
            r'(?:can you|please)\s+(?:tell me|show me)\s+(?:about|all)\s+projects?\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\s+district)?',
            r'(?:what|which)\s+(?:kinds of|types of)\s+projects?\s+(?:are|exist)\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\s+district)?',
            r'(?:give me|show me)\s+a\s+(?:list of|summary of)\s+projects?\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\s+district)?',
            r'(?:what|which)\s+projects?\s+(?:can you|do you)\s+(?:find|show)\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\s+district)?',
            r'(?:i need|i want)\s+to\s+(?:know about|see)\s+projects?\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\s+district)?',
            r'(?:are there|do you have)\s+(?:any\s+)?projects?\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\s+district)?',
            r'(?:please|can you)\s+(?:list|show)\s+(?:all\s+)?projects?\s+(?:from|in|at)\s+([a-zA-Z\s]+?)(?:\s+district)?'
        ]
        
        query = query.lower()
        
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
                    return district
        
        return ""