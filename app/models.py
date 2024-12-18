from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel, Field
import logging
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

class QuerySource(BaseModel):
    """Model for query source information"""
    table_name: str
    columns: List[str]
    operation: str
    sample_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class ChatQuery(BaseModel):
    """Model for chat query request"""
    message: str
    language: Optional[str] = None
    chat_history: Optional[List[str]] = None

class QueryMetadata(BaseModel):
    """Model for query execution metadata"""
    query_id: str
    execution_time: float
    row_count: int
    sources: List[QuerySource]
    timestamp: datetime

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    """Model for chat response with sources"""
    answer: str
    suggested_questions: List[str]
    metadata: Optional[QueryMetadata] = None
    sources: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True

class QueryParser:
    def __init__(self):
        self.initialized = True
    
    def parse_query_intent(self, query: str, language: str = 'en') -> Tuple[str, Dict[str, Any]]:
        """
        Parse query and return SQL query and filters
        
        Args:
            query: The user's query
            language: The query language (default: 'en')
            
        Returns:
            Tuple containing:
            - SQL query string
            - Dictionary of filters
        """
        try:
            filters = {}
            query = query.lower()
            
            # Base SQL query
            sql = "SELECT * FROM projects"
            where_clauses = []
            
            # Check for education projects
            if 'education' in query:
                filters['sector'] = 'Education'
                where_clauses.append("sector = 'Education'")
            
            # Check for health projects
            elif 'health' in query:
                filters['sector'] = 'Health'
                where_clauses.append("sector = 'Health'")
                
            # Check for water projects
            elif 'water' in query or 'sanitation' in query:
                filters['sector'] = 'Water and Sanitation'
                where_clauses.append("sector = 'Water and Sanitation'")
                
            # Check for transport projects
            elif 'transport' in query or 'road' in query or 'bridge' in query:
                filters['sector'] = 'Transport'
                where_clauses.append("sector = 'Transport'")
            
            # Check for security projects
            elif 'security' in query or 'police' in query:
                filters['sector'] = 'Community security initiatives'
                where_clauses.append("sector = 'Community security initiatives'")
            
            # Add status filters
            if 'completed' in query or 'finished' in query or 'done' in query:
                filters['completed'] = True
                where_clauses.append("completion_percentage = 100")
            elif 'progress' in query or 'ongoing' in query:
                filters['in_progress'] = True
                where_clauses.append("completion_percentage > 0 AND completion_percentage < 100")
            elif 'not started' in query or 'pending' in query:
                filters['not_started'] = True
                where_clauses.append("completion_percentage = 0")
            
            # Add region filters
            if 'northern' in query or 'north' in query:
                filters['region'] = 'Northern Region'
                where_clauses.append("region = 'Northern Region'")
            elif 'central' in query or 'centre' in query:
                filters['region'] = 'Central Region'
                where_clauses.append("region = 'Central Region'")
            elif 'southern' in query or 'south' in query:
                filters['region'] = 'Southern Region'
                where_clauses.append("region = 'Southern Region'")
            
            # Combine WHERE clauses
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # Add ORDER BY
            if 'budget' in query:
                if 'highest' in query:
                    sql += " ORDER BY budget DESC"
                elif 'lowest' in query:
                    sql += " ORDER BY budget ASC"
            elif 'recent' in query:
                sql += " ORDER BY start_date DESC"
            elif 'completion' in query:
                sql += " ORDER BY completion_percentage DESC"
                
            return sql, filters
            
        except Exception as e:
            logger.error(f"Error parsing query: {e}")
            return "SELECT * FROM projects", {}
    
    def generate_suggestions(self, df: pd.DataFrame, filters: Dict[str, Any]) -> List[str]:
        """Generate suggested follow-up questions based on the current results"""
        suggestions = []
        
        try:
            # If no sector filter, suggest exploring specific sectors
            if not filters.get('sector'):
                sectors = df['sector'].unique() if 'sector' in df.columns else []
                if len(sectors) > 0:
                    sector = sectors[0]
                    suggestions.append(f"Show me {sector.lower()} projects")
            
            # If no region filter, suggest exploring specific regions
            if not filters.get('region'):
                regions = df['region'].unique() if 'region' in df.columns else []
                if len(regions) > 0:
                    region = regions[0]
                    suggestions.append(f"What projects are in {region}?")
            
            # If no status filter, suggest exploring by status
            if not any(key in filters for key in ['completed', 'in_progress', 'not_started']):
                suggestions.append("Show me completed projects")
                suggestions.append("What projects are in progress?")
            
            # Add general suggestions
            suggestions.extend([
                "What are the highest budget projects?",
                "Show me projects with the highest completion rate",
                "What are the most recent projects?"
            ])
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return ["Show me all projects", "What are the latest projects?"]