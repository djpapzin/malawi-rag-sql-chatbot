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
    """Simplified query types for classification"""
    UNRELATED = "unrelated"  # General conversation, greetings, etc.
    GENERAL = "general"      # Questions about multiple projects
    SPECIFIC = "specific"    # Questions about a specific project

class QueryParameters(BaseModel):
    """Parameters extracted from the query"""
    project_identifier: Optional[str] = None  # For specific queries
    filters: Dict[str, Any] = Field(default_factory=dict)  # For general queries
    context: Dict[str, Any] = Field(default_factory=dict)  # For follow-up questions

class QueryClassification(BaseModel):
    """Result of query classification"""
    query_type: QueryType
    confidence: float
    parameters: QueryParameters = Field(default_factory=QueryParameters)

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
        self.prompt_template = """
You are an assistant for a Malawi infrastructure project database.
Classify this user query into one of three types:

1. UNRELATED: General conversation, greetings, or questions about capabilities
2. GENERAL: Questions about projects that may include filters (district, sector, status, etc.)
3. SPECIFIC: Questions about a specific project or follow-up questions about a previously discussed project

Return a JSON object with:
{
    "query_type": "unrelated|general|specific",
    "confidence": 0.0 to 1.0,
    "project_identifier": null or project name/code if specific,
    "filters": {
        "districts": [],
        "sectors": [],
        "status": [],
        "budget_range": {"min": null, "max": null},
        "time_range": {"start": null, "end": null}
    }
}

Query: {query}

Previous context: {context}
"""
    
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
    
    async def classify_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> QueryClassification:
        """
        Classify a query using LLM
        
        Args:
            query: The query to classify
            context: Optional conversation context
            
        Returns:
            QueryClassification object
        """
        # Format context for prompt
        context_str = "None" if not context else str(context)
        
        # Create prompt
        prompt = self.prompt_template.format(
            query=query,
            context=context_str
        )
        
        try:
            # Call LLM (placeholder - implement actual LLM call)
            response = await self._call_llm(prompt)
            
            # Parse response
            result = self._parse_llm_response(response)
            
            # Create classification
            classification = QueryClassification(
                query_type=QueryType(result["query_type"]),
                confidence=result["confidence"],
                parameters=QueryParameters(
                    project_identifier=result.get("project_identifier"),
                    filters=result.get("filters", {}),
                    context=context or {}
                )
            )
            
            return classification
            
        except Exception as e:
            logger.error(f"Error classifying query: {e}")
            # Return default classification for errors
            return QueryClassification(
                query_type=QueryType.GENERAL,
                confidence=0.0,
                parameters=QueryParameters()
            )
    
    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM service (placeholder)"""
        # TODO: Implement actual LLM call
        return """
        {
            "query_type": "general",
            "confidence": 0.8,
            "project_identifier": null,
            "filters": {
                "districts": [],
                "sectors": [],
                "status": [],
                "budget_range": {"min": null, "max": null},
                "time_range": {"start": null, "end": null}
            }
        }
        """
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured data"""
        try:
            # Extract JSON from response
            json_str = response.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            
            # Parse JSON
            result = json.loads(json_str)
            
            # Validate required fields
            required_fields = ["query_type", "confidence", "filters"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            # Return default result for errors
            return {
                "query_type": "general",
                "confidence": 0.0,
                "project_identifier": None,
                "filters": {}
            }
