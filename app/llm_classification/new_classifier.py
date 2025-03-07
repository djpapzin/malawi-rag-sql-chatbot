"""
LLM-based Query Classification Module

This module provides LLM-powered classification for natural language queries
to the Malawi infrastructure projects database.
"""

import json
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
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
    
    def __init__(self):
        """Initialize the classifier"""
        self.prompt_template = """
You are an assistant for a Malawi infrastructure project database.
Classify this user query into one of three types:

1. UNRELATED: General conversation, greetings, or questions about capabilities
2. GENERAL: Questions about projects that may include filters (district, sector, status, etc.)
3. SPECIFIC: Questions about a specific project or follow-up questions about a previously discussed project

For sector queries, be sure to identify the sector and add it to the filters.
Common sectors include: health, education, water, transport, agriculture

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
        # Initialize Together API
        self.together = Together()
        self.together.api_key = "YOUR_API_KEY"  # Replace with actual key
        
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
            # Call LLM
            response = await self._call_llm(prompt)
            
            # Parse response
            result = self._parse_llm_response(response)
            
            # Special handling for sector queries
            if "sector" in query.lower() or any(sector in query.lower() for sector in ["health", "education", "water", "transport", "agriculture"]):
                result["query_type"] = "general"
                result["confidence"] = 0.9
                # Extract sector from query
                for sector in ["health", "education", "water", "transport", "agriculture"]:
                    if sector in query.lower():
                        result["filters"]["sectors"] = [sector]
                        break
            
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
            # Default to general query on error
            return QueryClassification(
                query_type=QueryType.GENERAL,
                confidence=0.5,
                parameters=QueryParameters(
                    filters={},
                    context=context or {}
                )
            )
    
    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM service"""
        try:
            # Call the LLM
            response = await self.together.chat.completions.create(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Low temperature for more consistent classification
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            # Return default response for errors
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
            
            # Validate query type
            if result["query_type"] not in [t.value for t in QueryType]:
                raise ValueError(f"Invalid query type: {result['query_type']}")
            
            # Validate confidence
            if not isinstance(result["confidence"], (int, float)) or result["confidence"] < 0 or result["confidence"] > 1:
                raise ValueError(f"Invalid confidence value: {result['confidence']}")
            
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