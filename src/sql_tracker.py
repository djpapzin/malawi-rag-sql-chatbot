"""
SQL Query Tracker for capturing metadata about SQL queries and their sources
"""

from typing import Dict, List, Optional, Any
import sqlparse
from dataclasses import dataclass
from datetime import datetime

@dataclass
class QuerySource:
    """Data class for storing query source information"""
    table_name: str
    columns: List[str]
    operation: str  # SELECT, JOIN, WHERE, etc.
    sample_data: Optional[Dict[str, Any]] = None
    
@dataclass
class QueryMetadata:
    """Data class for storing query execution metadata"""
    query_id: str
    timestamp: datetime
    execution_time: float
    row_count: int
    sources: List[QuerySource]
    original_query: str
    parsed_query: str
    error: Optional[str] = None

class SQLTracker:
    """Tracks SQL query execution and captures metadata"""
    
    def __init__(self):
        self.query_history: Dict[str, QueryMetadata] = {}
    
    def parse_query(self, query: str) -> List[QuerySource]:
        """
        Parse SQL query to extract table and column information
        
        Args:
            query (str): SQL query to parse
            
        Returns:
            List[QuerySource]: List of sources used in the query
        """
        sources = []
        parsed = sqlparse.parse(query)[0]
        
        # Extract tables and columns from parsed query
        tables = set()
        columns = {}
        
        for token in parsed.tokens:
            if token.is_group:
                if token.get_type() == 'FROM':
                    # Extract table names
                    for item in token.tokens:
                        if item.is_group:
                            tables.add(item.value)
                elif token.get_type() == 'SELECT':
                    # Extract column names
                    for item in token.tokens:
                        if isinstance(item, sqlparse.sql.Identifier):
                            col_name = item.get_name()
                            table_name = item.get_parent_name()
                            if table_name:
                                if table_name not in columns:
                                    columns[table_name] = []
                                columns[table_name].append(col_name)
        
        # Create QuerySource objects
        for table in tables:
            sources.append(QuerySource(
                table_name=table,
                columns=columns.get(table, []),
                operation="SELECT"  # Default operation
            ))
        
        return sources
    
    def track_query(self, query: str, execution_time: float, row_count: int, 
                   error: Optional[str] = None) -> str:
        """
        Track a SQL query execution and its metadata
        
        Args:
            query (str): Executed SQL query
            execution_time (float): Query execution time in seconds
            row_count (int): Number of rows returned/affected
            error (Optional[str]): Error message if query failed
            
        Returns:
            str: Query ID for reference
        """
        # Generate query ID
        query_id = f"q_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Parse query and extract sources
        sources = self.parse_query(query)
        
        # Create metadata
        metadata = QueryMetadata(
            query_id=query_id,
            timestamp=datetime.now(),
            execution_time=execution_time,
            row_count=row_count,
            sources=sources,
            original_query=query,
            parsed_query=str(sqlparse.parse(query)[0]),
            error=error
        )
        
        # Store metadata
        self.query_history[query_id] = metadata
        
        return query_id
    
    def get_query_sources(self, query_id: str) -> Optional[List[QuerySource]]:
        """
        Get sources for a tracked query
        
        Args:
            query_id (str): Query ID to look up
            
        Returns:
            Optional[List[QuerySource]]: List of sources or None if not found
        """
        if query_id in self.query_history:
            return self.query_history[query_id].sources
        return None
    
    def get_query_metadata(self, query_id: str) -> Optional[QueryMetadata]:
        """
        Get full metadata for a tracked query
        
        Args:
            query_id (str): Query ID to look up
            
        Returns:
            Optional[QueryMetadata]: Query metadata or None if not found
        """
        return self.query_history.get(query_id)
    
    def format_sources_response(self, query_id: str) -> Dict[str, Any]:
        """
        Format query sources into a response
        
        Args:
            query_id (str): Query ID to format sources for
            
        Returns:
            Dict[str, Any]: Formatted response with sources
        """
        metadata = self.get_query_metadata(query_id)
        if not metadata:
            return {
                "status": "error",
                "message": f"Query {query_id} not found"
            }
        
        sources_info = []
        for source in metadata.sources:
            source_info = {
                "table": source.table_name,
                "columns": source.columns,
                "operation": source.operation
            }
            if source.sample_data:
                source_info["sample_data"] = source.sample_data
            sources_info.append(source_info)
        
        return {
            "status": "success",
            "query_id": query_id,
            "execution_time": metadata.execution_time,
            "row_count": metadata.row_count,
            "sources": sources_info,
            "timestamp": metadata.timestamp.isoformat(),
            "parsed_query": metadata.parsed_query
        } 