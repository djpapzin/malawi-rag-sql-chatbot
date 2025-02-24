from typing import Dict, List, Any, Optional, Tuple, Union
from pydantic import BaseModel, Field
import logging
from datetime import datetime
import pandas as pd
import sqlite3
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class Location(BaseModel):
    """Model for location information"""
    region: str
    district: str

class MonetaryAmount(BaseModel):
    """Model for monetary amounts"""
    amount: float
    formatted: str

class Contractor(BaseModel):
    """Model for contractor information"""
    name: str
    contract_start_date: str

class QueryMetadata(BaseModel):
    """Model for query execution metadata"""
    total_results: int
    query_time: str
    sql_query: str

class GeneralProjectInfo(BaseModel):
    """Model for general project information"""
    project_name: str
    district: str
    project_sector: str
    project_status: str
    budget: MonetaryAmount
    completion_percentage: float

class DetailedProjectInfo(BaseModel):
    """Model for detailed project information"""
    project_name: str
    district: str
    project_sector: str
    project_status: str
    budget: MonetaryAmount
    completion_percentage: float
    start_date: str
    completion_date: str

class GeneralQueryResponse(BaseModel):
    """Model for general query response"""
    query_type: str = "general"
    results: List[Dict[str, Any]]  # Using Dict for more flexible formatting
    metadata: QueryMetadata

class SpecificQueryResponse(BaseModel):
    """Model for specific query response"""
    query_type: str = "specific"
    results: List[Dict[str, Any]]  # Using Dict for more flexible formatting
    metadata: QueryMetadata

class QuerySource(BaseModel):
    """Model for query source information"""
    type: str = "sql"
    sql: str
    database: str = "malawi_projects1.db"

    class Config:
        from_attributes = True

class ChatQuery(BaseModel):
    """Chat query model"""
    message: str
    source_lang: str = "english"
    page: Optional[int] = 1
    page_size: Optional[int] = 30
    continue_previous: Optional[bool] = False

class ChatResponse(BaseModel):
    """Model for chat response"""
    response: Union[GeneralQueryResponse, SpecificQueryResponse]

    class Config:
        from_attributes = True

class DatabaseManager:
    def __init__(self, db_path: str = 'malawi_projects1.db'):
        self.db_path = db_path
        
    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
                
    async def execute_query(self, query: str) -> List[Tuple]:
        """Execute a SQL query and return the results"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
                logger.info(f"Query executed successfully, returned {len(results)} rows")
                return results
        except sqlite3.Error as e:
            logger.error(f"Error executing query: {e}")
            raise ValueError(f"Error executing SQL query: {str(e)}")