from typing import Dict, List, Any, Optional, Tuple, Union
from pydantic import BaseModel, Field
import logging
from datetime import datetime
import pandas as pd
import sqlite3
from contextlib import contextmanager
import os

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
    database: str = "pmisProjects.db"

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    session_id: Optional[str] = None

class ResultData(BaseModel):
    """Model for result data"""
    type: str
    message: str
    data: Dict[str, Any]

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    results: List[ResultData]
    query_time_ms: float
    sql_query: str

class DatabaseManager:
    def __init__(self, db_path: str = None):
        # Default to the database specified in environment variable or fall back to a default
        if db_path is None:
            db_path = os.getenv('DATABASE_URL', '')
            if db_path.startswith('sqlite:///'):
                db_path = db_path[len('sqlite:///'):]
                
            # If no database URL is set, default to malawi_projects1.db in the project root
            if not db_path:
                db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'malawi_projects1.db')
        
        # Convert to absolute path if relative
        if not os.path.isabs(db_path):
            db_path = os.path.abspath(db_path)
            
        self.db_path = db_path
        logger.info(f"Using database at: {self.db_path}")

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            if not os.path.exists(self.db_path):
                raise FileNotFoundError(f"Database file not found: {self.db_path}")
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable row factory for named columns
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def execute_query(self, query: str) -> Tuple[List[Dict[str, Any]], float]:
        start_time = datetime.now()
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            query_time = (datetime.now() - start_time).total_seconds()
            return results, query_time
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            logger.error(f"Failed query: {query}")
            raise
        finally:
            if conn:
                conn.close()