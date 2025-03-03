"""
LLM-based Query Classification Module

This module provides LLM-powered classification for natural language queries
to the Malawi infrastructure projects database.
"""

import json
import logging
import os
import re
from typing import Dict, Any, List, Optional, Tuple, Union
import asyncio
from pydantic import BaseModel, Field
from enum import Enum
import time
from fuzzywuzzy import fuzz

# Import Together API client
from together import Together

logger = logging.getLogger(__name__)

class QueryType(str, Enum):
    """Enum for query types"""
    DISTRICT = "district"
    PROJECT = "project"
    SECTOR = "sector"
    BUDGET = "budget"
    STATUS = "status"
    TIME = "time"
    COMBINED = "combined"
    UNKNOWN = "unknown"

class QueryParameters(BaseModel):
    """Parameters extracted from a query"""
    districts: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    sectors: List[str] = Field(default_factory=list)
    budget_range: Dict[str, Optional[float]] = Field(default_factory=lambda: {"min": None, "max": None})
    status: List[str] = Field(default_factory=list)
    time_range: Dict[str, Optional[str]] = Field(default_factory=lambda: {"start": None, "end": None})

class QueryClassification(BaseModel):
    """Classification result for a query"""
    query_type: QueryType
    parameters: QueryParameters
    confidence: float = 0.0
    original_query: str
    llm_response: Optional[str] = None
    processing_time: float = 0.0

class LLMClassifier:
    """LLM-based query classifier"""
    
    MALAWI_DISTRICTS = [
        "Balaka", "Blantyre", "Chikwawa", "Chiradzulu", "Chitipa", "Dedza", 
        "Dowa", "Karonga", "Kasungu", "Likoma", "Lilongwe", "Machinga", 
        "Mangochi", "Mchinji", "Mulanje", "Mwanza", "Mzimba", "Neno", 
        "Nkhata Bay", "Nkhotakota", "Nsanje", "Ntcheu", "Ntchisi", "Phalombe", 
        "Rumphi", "Salima", "Thyolo", "Zomba"
    ]
    
    DISTRICT_PATTERNS = [
        # Base patterns for explicit district mentions
        r"\b(projects?|works|developments?|initiatives?)\b.*\b(in|around|for|of)\s+([\w\s]+?)(\s+district)?\b",
        
        # Patterns for questions and commands
        r"\b((list|show|find|what|tell|give).*\b(in|from|about)\s+([A-Z][\w\s]+))(\s+district)?\b",
        
        # Patterns for district-first mentions
        r"\b([A-Z][\w\s]+?)\s+(projects?|developments?|infrastructure|activities|works|initiatives)\b",
        
        # Patterns for ongoing/current activities
        r"\b(ongoing|current|existing)\s+.*\b(in|around|at)\s+([\w\s]+)\b",
        
        # Patterns for general queries about locations
        r"\b(what'?s\s+happening|what\s+is\s+happening|status)\s+.*\b(in|around|at)\s+([\w\s]+)\b"
    ]
    
    def __init__(self):
        """Initialize the classifier"""
        # Get model from environment variables
        self.model = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
        
        # Get API key from environment
        api_key = os.getenv("TOGETHER_API_KEY", "f7119711abb83c4ec5e9b2339eb06c66c87d4958f4ce6cc348ed3ad0c6cb7101")
        
        # Set the API key directly
        import together
        together.api_key = api_key
        
        # Initialize Together client
        self.client = Together()
        
        logger.info(f"Initialized LLM Classifier with model: {self.model}")
    
    def match_district(self, input_name, min_ratio=75):
        """
        Find matching district names using fuzzy string matching.
        Args:
            input_name (str): Input district name to match
            min_ratio (int): Minimum similarity ratio (0-100) to consider a match
        Returns:
            list: List of matching district names
        """
        matches = []
        for district in self.MALAWI_DISTRICTS:
            if fuzz.ratio(input_name.lower(), district.lower()) > min_ratio:
                matches.append(district)
        return matches
    
    def extract_district(self, text):
        """
        Enhanced district extraction with fuzzy matching support.
        Args:
            text (str): Input text to extract district from
        Returns:
            str: Matched district name or None
        """
        # Try exact pattern matching first
        for pattern in self.DISTRICT_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Extract the district name from the appropriate group
                district_name = match.group(3) if len(match.groups()) >= 3 else match.group(1)
                district_name = district_name.strip()
                
                # Try fuzzy matching with the extracted name
                matches = self.match_district(district_name)
                if matches:
                    return matches[0]  # Return the best match
                    
        # If no pattern match, try direct fuzzy matching with words
        words = text.split()
        for word in words:
            if word[0].isupper():  # Only try matching capitalized words
                matches = self.match_district(word)
                if matches:
                    return matches[0]
        
        return None
    
    def _validate_district(self, district: str) -> str:
        """Validate and normalize district name"""
        district = district.strip().title()
        
        # Exact match
        if district in self.MALAWI_DISTRICTS:
            return district
        
        # Fuzzy match (simple implementation)
        for known_district in self.MALAWI_DISTRICTS:
            if district in known_district or known_district in district:
                return known_district
            
            # Calculate similarity (very basic)
            similarity = sum(1 for a, b in zip(district.lower(), known_district.lower()) if a == b)
            if similarity > len(known_district) * 0.7:  # 70% similarity threshold
                return known_district
        
        # No match found, return as is
        return district
    
    def _validate_sector(self, sector: str) -> str:
        """Validate and normalize sector name"""
        sector = sector.strip().lower()
        
        # Mapping of common terms to standard sectors
        sector_mapping = {
            "school": "education",
            "classroom": "education",
            "hospital": "health",
            "clinic": "health",
            "medical": "health",
            "healthcare": "health",
            "road": "transport",
            "bridge": "transport",
            "highway": "transport",
            "water supply": "water",
            "borehole": "water",
            "well": "water",
            "irrigation": "agriculture",
            "farming": "agriculture",
            "crop": "agriculture"
        }
        
        # Check mapping first
        for key, value in sector_mapping.items():
            if key in sector:
                return value
        
        # Exact match
        if sector in ["education", "health", "water", "sanitation", "transport", 
            "agriculture", "energy", "infrastructure", "environment", 
            "governance", "social protection", "tourism", "trade", "industry"]:
            return sector
        
        # Fuzzy match
        for known_sector in ["education", "health", "water", "sanitation", "transport", 
            "agriculture", "energy", "infrastructure", "environment", 
            "governance", "social protection", "tourism", "trade", "industry"]:
            if sector in known_sector or known_sector in sector:
                return known_sector
        
        # No match found, return as is
        return sector
    
    def _validate_status(self, status: str) -> str:
        """Validate and normalize status"""
        status = status.strip().lower()
        
        # Mapping of common terms to standard statuses
        status_mapping = {
            "in progress": "ongoing",
            "in-progress": "ongoing",
            "inprogress": "ongoing",
            "active": "ongoing",
            "current": "ongoing",
            "done": "completed",
            "finished": "completed",
            "complete": "completed",
            "ended": "completed",
            "pending": "planned",
            "proposed": "planned",
            "future": "planned",
            "upcoming": "planned",
            "late": "delayed",
            "behind schedule": "delayed",
            "postponed": "delayed",
            "stopped": "suspended",
            "halted": "suspended",
            "terminated": "cancelled"
        }
        
        # Check mapping first
        if status in status_mapping:
            return status_mapping[status]
        
        # Exact match
        if status in ["planned", "approved", "in progress", "ongoing", "completed", 
            "delayed", "cancelled", "suspended"]:
            return status
        
        # Fuzzy match
        for known_status in ["planned", "approved", "in progress", "ongoing", "completed", 
            "delayed", "cancelled", "suspended"]:
            if status in known_status or known_status in status:
                return known_status
        
        # No match found, return as is
        return status
    
    def _validate_parameters(self, parameters: QueryParameters) -> QueryParameters:
        """Validate and normalize extracted parameters"""
        # Validate districts
        if parameters.districts:
            parameters.districts = [self._validate_district(d) for d in parameters.districts]
        
        # Validate sectors
        if parameters.sectors:
            parameters.sectors = [self._validate_sector(s) for s in parameters.sectors]
        
        # Validate statuses
        if parameters.status:
            parameters.status = [self._validate_status(s) for s in parameters.status]
        
        # Validate budget range
        if parameters.budget_range:
            # Ensure min <= max if both are provided
            if parameters.budget_range["min"] is not None and parameters.budget_range["max"] is not None:
                if parameters.budget_range["min"] > parameters.budget_range["max"]:
                    parameters.budget_range["min"], parameters.budget_range["max"] = parameters.budget_range["max"], parameters.budget_range["min"]
        
        # Validate time range
        if parameters.time_range:
            # Ensure start <= end if both are provided
            if parameters.time_range["start"] and parameters.time_range["end"]:
                if parameters.time_range["start"] > parameters.time_range["end"]:
                    parameters.time_range["start"], parameters.time_range["end"] = parameters.time_range["end"], parameters.time_range["start"]
        
        return parameters
    
    def _determine_query_type(self, parameters: QueryParameters) -> QueryType:
        """Determine the query type based on parameters"""
        # Count non-empty parameter types
        param_counts = {
            QueryType.DISTRICT: len(parameters.districts),
            QueryType.PROJECT: len(parameters.projects),
            QueryType.SECTOR: len(parameters.sectors),
            QueryType.STATUS: len(parameters.status),
            QueryType.BUDGET: 1 if (parameters.budget_range["min"] is not None or parameters.budget_range["max"] is not None) else 0,
            QueryType.TIME: 1 if (parameters.time_range["start"] is not None or parameters.time_range["end"] is not None) else 0
        }
        
        # Count how many parameter types are present
        non_empty_param_types = sum(1 for count in param_counts.values() if count > 0)
        
        # If multiple parameter types, it's a combined query
        if non_empty_param_types > 1:
            return QueryType.COMBINED
        
        # If only one parameter type, return that type
        for query_type, count in param_counts.items():
            if count > 0:
                return query_type
        
        # If no parameters, return unknown
        return QueryType.UNKNOWN
    
    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM API to get a response"""
        try:
            import together
            logger.info(f"Sending prompt to LLM: {repr(prompt[:100])}...")
            
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
            logger.info(f"Raw LLM response: {repr(raw_text[:100])}...")
            
            return raw_text
            
        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            raise
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response text"""
        # Try to find JSON in the response
        json_pattern = r'```json\s*(.*?)\s*```'
        json_matches = re.findall(json_pattern, text, re.DOTALL)
        
        if json_matches:
            try:
                return json.loads(json_matches[0])
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON from match: {json_matches[0]}")
        
        # Try to find any JSON-like structure
        try:
            # Look for opening and closing braces
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                json_str = text[start_idx:end_idx+1]
                return json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from text: {text}")
        
        # Return empty dict if no JSON found
        return {}
    
    async def classify_query(self, query: str) -> QueryClassification:
        """
        Classify a natural language query using LLM
        
        Args:
            query: The natural language query to classify
            
        Returns:
            QueryClassification object with query type and parameters
        """
        start_time = time.time()
        
        # Create the prompt for the LLM
        prompt = f"""
        You are an assistant for a Malawi infrastructure project database.
        Classify this user query: "{query}"
        
        Return a JSON object with the following structure:
        {{
            "query_type": "district|project|sector|budget|status|time|combined",
            "parameters": {{
                "districts": ["district_name1", "district_name2"],
                "projects": ["project_name1", "project_name2"],
                "sectors": ["sector_name1", "sector_name2"],
                "budget_range": {{"min": null, "max": null}},
                "status": ["completed", "in_progress", "planned"],
                "time_range": {{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}}
            }}
        }}
        
        Only include parameters that are relevant to the query.
        For project names, extract the full project name as mentioned in the query.
        For districts, extract the district names mentioned.
        For sectors, identify the sectors like education, health, water, transport, etc.
        For budget queries, extract any minimum or maximum values mentioned.
        For status queries, identify if the user is asking about completed, ongoing, or planned projects.
        For time queries, extract any date ranges or years mentioned.
        
        Format your response as valid JSON inside ```json ``` code blocks.
        """
        
        # Call the LLM
        llm_response = await self._call_llm(prompt)
        
        # Extract JSON from the response
        classification_data = self._extract_json_from_text(llm_response)
        
        # Default classification
        classification = QueryClassification(
            query_type=QueryType.UNKNOWN,
            parameters=QueryParameters(),
            original_query=query,
            llm_response=llm_response,
            confidence=0.5
        )
        
        # Update with LLM classification if available
        if classification_data:
            try:
                # Extract query type
                if "query_type" in classification_data:
                    query_type = classification_data["query_type"].lower()
                    if query_type in [e.value for e in QueryType]:
                        classification.query_type = QueryType(query_type)
                
                # Extract parameters
                if "parameters" in classification_data:
                    params = classification_data["parameters"]
                    
                    # Extract districts
                    if "districts" in params and isinstance(params["districts"], list):
                        classification.parameters.districts = params["districts"]
                    
                    # Extract projects
                    if "projects" in params and isinstance(params["projects"], list):
                        classification.parameters.projects = params["projects"]
                    
                    # Extract sectors
                    if "sectors" in params and isinstance(params["sectors"], list):
                        classification.parameters.sectors = params["sectors"]
                    
                    # Extract budget range
                    if "budget_range" in params and isinstance(params["budget_range"], dict):
                        classification.parameters.budget_range = params["budget_range"]
                    
                    # Extract status
                    if "status" in params and isinstance(params["status"], list):
                        classification.parameters.status = params["status"]
                    
                    # Extract time range
                    if "time_range" in params and isinstance(params["time_range"], dict):
                        classification.parameters.time_range = params["time_range"]
                
                # Validate parameters
                classification.parameters = self._validate_parameters(classification.parameters)
                
                # Determine query type if not provided
                if classification.query_type == QueryType.UNKNOWN:
                    classification.query_type = self._determine_query_type(classification.parameters)
                
                # Set confidence based on parameter extraction
                param_count = (
                    len(classification.parameters.districts) +
                    len(classification.parameters.projects) +
                    len(classification.parameters.sectors) +
                    len(classification.parameters.status) +
                    (1 if classification.parameters.budget_range["min"] is not None or 
                         classification.parameters.budget_range["max"] is not None else 0) +
                    (1 if classification.parameters.time_range["start"] is not None or 
                         classification.parameters.time_range["end"] is not None else 0)
                )
                
                if param_count > 0:
                    classification.confidence = min(0.9, 0.5 + param_count * 0.1)
                
            except Exception as e:
                logger.error(f"Error processing LLM classification: {str(e)}")
        
        # Calculate processing time
        classification.processing_time = time.time() - start_time
        
        return classification
