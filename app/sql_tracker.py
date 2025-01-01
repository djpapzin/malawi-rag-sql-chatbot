"""SQL Query Tracker

This module provides functionality to track SQL query execution and sources.
"""

import pandas as pd
import sqlite3
from typing import List, Tuple, Dict, Any
import logging
from .models import QuerySource
import re

logger = logging.getLogger(__name__)

class SQLTracker:
    """Tracks SQL query execution and sources"""
    
    def __init__(self, database: str = 'malawi_projects1.db'):
        self.database = database
        self.connection = None
        self.last_page = 1
        self.last_query = None
        logger.info(f"Initialized SQLTracker with database: {database}")
        
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
            logger.info("Disconnected from database")
        
    def _parse_query(self, query: str) -> List[QuerySource]:
        """Parse SQL query to extract table and column information"""
        sources = []
        try:
            # Basic SQL parsing - can be enhanced with a proper SQL parser
            query_lower = query.lower()
            
            # Extract table names
            if 'from' in query_lower:
                tables = query_lower.split('from')[1].split('where')[0].strip().split(',')
                tables = [t.strip() for t in tables]
                
                # Extract columns
                columns = []
                if 'select' in query_lower:
                    col_part = query_lower.split('from')[0].replace('select', '').strip()
                    if '*' in col_part:
                        # Get all columns from the tables
                        for table in tables:
                            cursor = self.connection.cursor()
                            cursor.execute(f"PRAGMA table_info({table})")
                            table_cols = [row[1] for row in cursor.fetchall()]
                            columns.extend(table_cols)
                    else:
                        columns = [c.strip() for c in col_part.split(',')]
                
                # Create source for each table
                for table in tables:
                    source = QuerySource(
                        sql=query,  # Use original query
                        table=table,
                        filters={}
                    )
                    sources.append(source)
        
        except Exception as e:
            logger.error(f"Error parsing query: {e}")
            # Return a generic source if parsing fails
            sources = [QuerySource(
                sql=query,  # Use original query
                table="unknown",
                filters={}
            )]
        
        return sources
    
    def execute_query(self, query: str) -> Tuple[pd.DataFrame, List[QuerySource]]:
        """Execute SQL query and return results with source information"""
        try:
            # Connect to database
            if not self.connection:
                self._connect()
            
            # Add LIMIT clause if not present
            final_query = query
            if 'LIMIT' not in query.upper():
                final_query = f"{query} LIMIT 100"  # Default limit
            
            logger.info(f"Original query: {query}")
            logger.info(f"Executing query: {final_query}")
            
            # Execute query with a timeout
            cursor = self.connection.cursor()
            cursor.execute(final_query)
            
            # Convert to DataFrame
            columns = [description[0] for description in cursor.description]
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=columns)
            
            logger.info(f"Query returned {len(df)} rows with columns: {columns}")
            
            # Create source with original query
            sources = [QuerySource(
                sql=query,  # Use original query without LIMIT
                table="projects",
                filters={}
            )]
            
            return df, sources
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            logger.error(f"Failed query: {query}")
            return pd.DataFrame(), []
            
        finally:
            cursor.close()
            self._disconnect()
            
    def execute_count_query(self, query: str) -> int:
        """Execute a COUNT query and return the total"""
        try:
            df, _ = self.execute_query(query)
            return df.iloc[0]['total'] if not df.empty else 0
        except Exception as e:
            logger.error(f"Error executing count query: {e}")
            raise
            
    def get_last_page(self) -> int:
        """Get the last page number that was queried"""
        return self.last_page
        
    def set_last_page(self, page: int):
        """Set the last page number that was queried"""
        self.last_page = page
        
    def execute_query_new(self, query: str) -> list:
        """Execute SQL query and return results"""
        try:
            if not self.connection:
                self._connect()
            cursor = self.connection.cursor()
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
            
    def execute_count_query_new(self, query: str) -> int:
        """Execute a COUNT query and return the total"""
        try:
            results = self.execute_query_new(query)
            return results[0].get('total', 0) if results else 0
        except Exception as e:
            logger.error(f"Error executing count query: {str(e)}")
            raise