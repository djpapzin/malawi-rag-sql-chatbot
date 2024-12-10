from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class ChatQuery(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    language: Optional[str] = Field(default="en", description="Language code for the response")
    chat_history: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Chat history for context")

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    answer: str
    suggested_questions: List[str] = Field(default_factory=list)
    error: Optional[str] = None

    class Config:
        from_attributes = True

class QueryParser:
    def __init__(self):
        self.initialized = True
    
    def parse_query_intent(self, query: str, language: str = 'en') -> Dict[str, Any]:
        """Parse query and return filters"""
        try:
            filters = {}
            query = query.lower()
            
            # Check for education projects
            if 'education' in query:
                filters['sector'] = 'Education'
            
            # Check for health projects
            elif 'health' in query:
                filters['sector'] = 'Health'
                
            # Check for water projects
            elif 'water' in query or 'sanitation' in query:
                filters['sector'] = 'Water and Sanitation'
                
            # Check for transport projects
            elif 'transport' in query or 'road' in query or 'bridge' in query:
                filters['sector'] = 'Transport'
            
            # Check for security projects
            elif 'security' in query or 'police' in query:
                filters['sector'] = 'Community security initiatives'
            
            # Add status filters
            if 'completed' in query or 'finished' in query or 'done' in query:
                filters['completed'] = True
            elif 'progress' in query or 'ongoing' in query:
                filters['in_progress'] = True
            elif 'not started' in query or 'pending' in query:
                filters['not_started'] = True
            
            # Add region filters
            if 'northern' in query or 'north' in query:
                filters['region'] = 'Northern Region'
            elif 'central' in query or 'centre' in query:
                filters['region'] = 'Central Region'
            elif 'southern' in query or 'south' in query:
                filters['region'] = 'Southern Region'
                
            return filters
            
        except Exception as e:
            logger.error(f"Error parsing query: {e}")
            return {}