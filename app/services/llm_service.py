import logging
import re
from typing import Dict, Any

class LLMService:
    """Service for LLM-based query classification and processing"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)

    async def classify_query(self, query: str) -> Dict[str, Any]:
        """Classify a query and extract relevant information using LLM
        
        The LLM analyzes the query to:
        1. Determine query type (specific/general)
        2. Extract entities and context
        3. Understand user intent
        4. Handle variations in phrasing
        """
        # Normalize query
        query = query.strip()
        
        # Initialize response
        classification = {
            "query_type": "general",
            "context": {
                "project_info": {},
                "extracted_filters": {},
                "intent": {},
                "entities": []
            },
            "confidence": 0.0
        }

        try:
            # Prepare prompt for LLM
            prompt = f"""Analyze this query about infrastructure projects: "{query}"

Instructions:
1. Determine if this is asking about a specific project or a general query
2. Extract key information like:
   - District names
   - Project sectors (education, health, etc.)
   - Project status (ongoing, completed, etc.)
3. Identify the main intent (e.g., location search, sector filter, status check)
4. Note any entities mentioned (places, organizations, etc.)

Format the response as JSON with these fields:
{{
    "query_type": "specific" or "general",
    "confidence": 0.0 to 1.0,
    "intent": {{
        "primary": "main intent",
        "secondary": ["other intents"]
    }},
    "entities": [
        {{"type": "district/sector/status", "value": "extracted value", "confidence": 0.0 to 1.0}}
    ],
    "filters": {{
        "district": "extracted district",
        "sector": "extracted sector",
        "status": "extracted status"
    }}
}}"""

            # TODO: Call actual LLM here
            # For now, fall back to regex-based extraction
            classification["context"]["extracted_filters"] = await self._extract_filters(query)
            
            # Determine if specific query based on patterns
            specific_indicators = [
                "tell me about",
                "show me details",
                "what is",
                "details of",
                "information about"
            ]
            
            if any(query.lower().startswith(indicator) for indicator in specific_indicators):
                classification["query_type"] = "specific"
                project_info = await self._extract_project_info(query)
                if project_info:
                    classification["context"]["project_info"] = project_info
                    classification["confidence"] = 0.8
            else:
                # For general queries, set confidence based on filter extraction
                filters = classification["context"]["extracted_filters"]
                if filters:
                    classification["confidence"] = 0.7 if len(filters) > 1 else 0.6
                    classification["context"]["intent"] = {
                        "primary": "filter_search",
                        "secondary": [f"{k}_filter" for k in filters.keys()]
                    }
                    classification["context"]["entities"] = [
                        {"type": k, "value": v, "confidence": 0.8}
                        for k, v in filters.items()
                    ]

        except Exception as e:
            self.logger.error(f"Error in LLM classification: {str(e)}")
            # Fall back to basic classification
            classification["confidence"] = 0.5
            
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
            r"\b(?:in|at|from|of|for)\s+(?:the\s+)?([A-Za-z\s]+?)(?:\s+district|\s*(?:$|[,\.]|\s+(?:and|or|projects?|sector)))",
            r"([A-Za-z\s]+?)\s+district\b",
            r"\b([A-Za-z]+)(?:\s+projects?|\s+region|\s+area)\b"
        ]
        
        query = query.lower()
        for pattern in district_patterns:
            if match := re.search(pattern, query, re.IGNORECASE):
                district = match.group(1).strip()
                # Clean up district name
                district = re.sub(r'\s+', ' ', district)  # Normalize spaces
                district = district.title()  # Title case
                # Remove common words that might be captured
                district = re.sub(r'\b(The|And|Or|Projects?|In|At|From|Of|For)\b', '', district, flags=re.IGNORECASE)
                district = district.strip()
                if district:
                    filters["district"] = district
                    break
                
        # Extract sector
        sector_mapping = {
            "health": ["health", "healthcare", "medical", "hospital", "clinic", "dispensary"],
            "education": ["education", "school", "training", "learning", "college", "university"],
            "water": ["water", "irrigation", "dam", "borehole", "sanitation"],
            "agriculture": ["agriculture", "farming", "crops", "livestock", "irrigation"],
            "infrastructure": ["infrastructure", "building", "construction", "facility"],
            "transport": ["transport", "road", "bridge", "highway", "railway"],
            "energy": ["energy", "power", "electricity", "solar", "grid"],
            "housing": ["housing", "residential", "homes", "settlement"],
            "sanitation": ["sanitation", "sewage", "waste", "drainage"],
        }
        
        for sector, keywords in sector_mapping.items():
            if any(keyword in query for keyword in keywords):
                filters["sector"] = sector
                break
                
        # Extract status
        status_patterns = [
            (r"\b(?:ongoing|in progress|current|active|running)\b", "ongoing"),
            (r"\b(?:complete|completed|finished|done)\b", "completed"),
            (r"\b(?:planned|upcoming|future|proposed)\b", "planned"),
            (r"\b(?:pending|waiting|delayed|on hold)\b", "pending"),
        ]
        
        for pattern, status in status_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                filters["status"] = status
                break
                
        return filters 