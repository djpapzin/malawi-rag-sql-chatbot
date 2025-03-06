import logging
import re
from typing import Dict, Any

class LLMService:
    """Service for LLM-based query classification and processing"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)

    async def classify_query(self, query: str) -> Dict[str, Any]:
        """Classify a query and extract relevant information
        
        Returns a dict with:
        - query_type: "specific" or "general"
        - context: Dict containing extracted information
            - project_info: Dict for specific queries
            - extracted_filters: Dict for general queries
        """
        # Normalize query
        query = query.strip().lower()
        
        # Initialize response
        classification = {
            "query_type": "general",
            "context": {
                "project_info": {},
                "extracted_filters": {}
            }
        }
        
        # Check for specific project indicators
        specific_indicators = [
            "tell me about",
            "show me details",
            "what is",
            "details of",
            "information about"
        ]
        
        if any(query.startswith(indicator) for indicator in specific_indicators):
            classification["query_type"] = "specific"
            # Extract project info
            project_info = await self._extract_project_info(query)
            if project_info:
                classification["context"]["project_info"] = project_info
        else:
            # Extract filters for general queries
            filters = await self._extract_filters(query)
            classification["context"]["extracted_filters"] = filters
            
        return classification
        
    async def _extract_project_info(self, query: str) -> Dict[str, Any]:
        """Extract project information from query"""
        project_info = {}
        
        # Extract project code if present
        code_match = re.search(r"(?:project|code)?\s*(?:code\s+)?(?:MW-)?([A-Za-z]{2}-[A-Z0-9]{2})", query)
        if code_match:
            code = code_match.group(1).upper()
            if not code.startswith('MW-'):
                code = f"MW-{code}"
            project_info["code"] = code
            
        # Extract project name
        name_patterns = [
            r"(?:about|details?|info|tell me about|show me|what is)(?: the)? (.+?)(?:\s*\?|\s*$)",
            r"(.+?)(?:\s+project|\s+construction)(?:\s*\?|\s*$)",
        ]
        
        for pattern in name_patterns:
            if match := re.search(pattern, query):
                name = match.group(1).strip()
                # Clean up name
                name = re.sub(r'\s+(?:project|construction)$', '', name)
                name = re.sub(r'^(?:the|a|an)\s+', '', name)
                project_info["name"] = name
                break
                
        return project_info
        
    async def _extract_filters(self, query: str) -> Dict[str, Any]:
        """Extract filter information from query"""
        filters = {}
        
        # Extract district
        district_patterns = [
            r"in\s+([A-Za-z\s]+?)(?:\s+district|\s*$)",
            r"(?:from|at|near)\s+([A-Za-z\s]+?)(?:\s+district|\s*$)",
        ]
        for pattern in district_patterns:
            if match := re.search(pattern, query):
                filters["district"] = match.group(1).strip()
                break
                
        # Extract sector
        sector_mapping = {
            "health": ["health", "healthcare", "medical", "hospital"],
            "education": ["education", "school", "training", "learning"],
            "water": ["water", "irrigation", "dam"],
            "agriculture": ["agriculture", "farming", "crops"],
            "infrastructure": ["infrastructure", "building", "construction"],
            "transport": ["transport", "road", "bridge"],
            "energy": ["energy", "power", "electricity"],
            "housing": ["housing", "residential", "homes"],
            "sanitation": ["sanitation", "sewage", "waste"],
        }
        
        for sector, keywords in sector_mapping.items():
            if any(keyword in query for keyword in keywords):
                filters["sector"] = sector
                break
                
        # Extract status
        status_patterns = [
            (r"\b(?:ongoing|in progress|current)\b", "ongoing"),
            (r"\b(?:complete|completed|finished)\b", "completed"),
            (r"\b(?:planned|upcoming|future)\b", "planned"),
            (r"\b(?:pending|waiting|delayed)\b", "pending"),
        ]
        
        for pattern, status in status_patterns:
            if re.search(pattern, query):
                filters["status"] = status
                break
                
        return filters 