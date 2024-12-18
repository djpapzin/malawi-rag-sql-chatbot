"""
SQL Handler for database operations and query tracking
"""

import os
import logging
import time
from typing import Dict, Any, List, Optional
import sqlite3
from .sql_tracker import SQLTracker

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLHandler:
    """Handler for SQL operations with query tracking"""
    
    def __init__(self, db_path: str):
        """
        Initialize SQL Handler
        
        Args:
            db_path (str): Path to SQLite database
        """
        if not os.path.exists(db_path):
            raise ValueError(f"Database not found: {db_path}")
            
        self.db_path = db_path
        self.tracker = SQLTracker()
        
    def execute_query(self, query: str) -> Dict[str, Any]:
        """
        Execute SQL query and track metadata
        
        Args:
            query (str): SQL query to execute
            
        Returns:
            Dict[str, Any]: Query results with metadata
        """
        start_time = time.time()
        error = None
        results = []
        row_count = 0
        
        try:
            # Execute query
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                
                # Get column names
                columns = [description[0] for description in cursor.description] if cursor.description else []
                
                # Fetch results
                rows = cursor.fetchall()
                row_count = len(rows)
                
                # Format results as list of dicts
                for row in rows:
                    results.append(dict(zip(columns, row)))
                
        except Exception as e:
            error = str(e)
            logger.error(f"Query execution error: {error}")
            
        finally:
            execution_time = time.time() - start_time
            
            # Track query execution
            query_id = self.tracker.track_query(
                query=query,
                execution_time=execution_time,
                row_count=row_count,
                error=error
            )
            
            # Get source information
            sources_info = self.tracker.format_sources_response(query_id)
            
            return {
                "status": "success" if not error else "error",
                "results": results if not error else [],
                "error": error,
                "metadata": {
                    "query_id": query_id,
                    "execution_time": execution_time,
                    "row_count": row_count,
                    "sources": sources_info.get("sources", [])
                }
            }
    
    def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a table
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            Optional[Dict[str, Any]]: Table information or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                if not columns:
                    return None
                
                # Get sample data
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                sample = cursor.fetchone()
                
                return {
                    "table_name": table_name,
                    "columns": [
                        {
                            "name": col[1],
                            "type": col[2],
                            "nullable": not col[3],
                            "primary_key": bool(col[5])
                        }
                        for col in columns
                    ],
                    "sample_data": dict(zip([col[1] for col in columns], sample)) if sample else None
                }
                
        except Exception as e:
            logger.error(f"Error getting table info: {str(e)}")
            return None
    
    def get_database_schema(self) -> List[Dict[str, Any]]:
        """
        Get schema information for all tables
        
        Returns:
            List[Dict[str, Any]]: List of table information
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get list of tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                return [
                    info for info in (
                        self.get_table_info(table[0]) for table in tables
                    )
                    if info is not None
                ]
                
        except Exception as e:
            logger.error(f"Error getting database schema: {str(e)}")
            return []
    
    def get_query_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent query history
        
        Args:
            limit (int): Maximum number of queries to return
            
        Returns:
            List[Dict[str, Any]]: List of recent queries with metadata
        """
        history = []
        for query_id in list(self.tracker.query_history.keys())[-limit:]:
            metadata = self.tracker.get_query_metadata(query_id)
            if metadata:
                history.append({
                    "query_id": metadata.query_id,
                    "timestamp": metadata.timestamp.isoformat(),
                    "execution_time": metadata.execution_time,
                    "row_count": metadata.row_count,
                    "query": metadata.original_query,
                    "error": metadata.error
                })
        return history 