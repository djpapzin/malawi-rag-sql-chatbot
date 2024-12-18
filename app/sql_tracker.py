"""SQL Query Tracker

This module provides functionality to track SQL query execution and sources.
"""

import pandas as pd
import sqlite3
from typing import List, Tuple, Dict, Any
import logging
from .models import QuerySource

logger = logging.getLogger(__name__)

class SQLTracker:
    """Tracks SQL query execution and sources"""
    
    def __init__(self, database: str = 'malawi_projects1.db'):
        self.database = database
        self.connection = None
    
    def _connect(self):
        """Create database connection"""
        try:
            self.connection = sqlite3.connect(self.database)
            logger.info(f"Connected to database: {self.database}")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def _disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def _parse_query(self, query: str) -> List[QuerySource]:
        """Parse SQL query to extract table and column information"""
        sources = []
        try:
            # Basic SQL parsing - can be enhanced with a proper SQL parser
            query = query.lower()
            
            # Extract table names
            if 'from' in query:
                tables = query.split('from')[1].split('where')[0].strip().split(',')
                tables = [t.strip() for t in tables]
                
                # Extract columns
                columns = []
                if 'select' in query:
                    col_part = query.split('from')[0].replace('select', '').strip()
                    if '*' in col_part:
                        # Get all columns from the tables
                        for table in tables:
                            cursor = self.connection.cursor()
                            cursor.execute(f"PRAGMA table_info({table})")
                            table_cols = [row[1] for row in cursor.fetchall()]
                            columns.extend(table_cols)
                    else:
                        columns = [c.strip() for c in col_part.split(',')]
                
                # Determine operation type
                operation = 'SELECT'
                if 'update' in query:
                    operation = 'UPDATE'
                elif 'insert' in query:
                    operation = 'INSERT'
                elif 'delete' in query:
                    operation = 'DELETE'
                
                # Create source for each table
                for table in tables:
                    source = QuerySource(
                        table_name=table,
                        columns=columns,
                        operation=operation,
                        sample_data=None
                    )
                    sources.append(source)
        
        except Exception as e:
            logger.error(f"Error parsing query: {e}")
            # Return a generic source if parsing fails
            sources = [QuerySource(
                table_name="unknown",
                columns=["*"],
                operation="SELECT",
                sample_data=None
            )]
        
        return sources
    
    def execute_query(self, query: str) -> Tuple[pd.DataFrame, List[QuerySource]]:
        """Execute SQL query and track sources"""
        try:
            # Connect to database
            self._connect()
            
            # Parse query for sources
            sources = self._parse_query(query)
            
            # Execute query
            df = pd.read_sql_query(query, self.connection)
            
            # Add sample data to sources
            for source in sources:
                if not df.empty and source.table_name in df.columns:
                    source.sample_data = df[source.table_name].head(1).to_dict()
            
            return df, sources
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return pd.DataFrame(), []
            
        finally:
            self._disconnect() 