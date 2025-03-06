"""Database Service Module

This module handles database operations and query execution.
"""

import sqlite3
import pandas as pd
import logging
from typing import Dict, Any
from ..core.config import settings

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self):
        """Initialize database service"""
        self.db_path = settings.DATABASE_URL.replace('sqlite:///', '')
        
    async def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query and return results as a DataFrame"""
        try:
            # Create connection
            conn = sqlite3.connect(self.db_path)
            
            # Execute query and get results
            results = pd.read_sql_query(query, conn)
            
            # Close connection
            conn.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise 