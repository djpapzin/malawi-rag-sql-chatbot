"""Database Service Module

This module handles database operations and query execution.
"""

import sqlite3
import pandas as pd
import logging
from typing import Dict, Any, List
from ..core.config import settings

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self):
        """Initialize database service"""
        self.db_path = settings.DATABASE_URL.replace('sqlite:///', '')
        
    async def execute_query(self, query: str) -> List[Dict]:
        """Execute a SQL query and return results as a list of dictionaries"""
        try:
            # Create connection
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            # Create cursor
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute(query)
            
            # Fetch results
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            results = [dict(row) for row in rows]
            
            # Close cursor and connection
            cursor.close()
            conn.close()
            
            return results
            
        except sqlite3.Error as e:
            logger.error(f"Database error executing query: {str(e)}")
            logger.error(f"Query was: {query}")
            raise
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            logger.error(f"Query was: {query}")
            raise 