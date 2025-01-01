from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel, Field
import logging
from datetime import datetime
import pandas as pd
import sqlite3
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class QuerySource(BaseModel):
    """Model for query source information"""
    sql: str
    table: str
    filters: Dict[str, Any]

    class Config:
        from_attributes = True

class ChatQuery(BaseModel):
    """Chat query model"""
    message: str
    source_lang: str = "english"
    page: Optional[int] = 1
    page_size: Optional[int] = 30
    continue_previous: Optional[bool] = False

class QueryMetadata(BaseModel):
    """Model for query execution metadata"""
    query_time: str
    total_results: int
    current_page: int
    total_pages: int
    has_more: bool

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    """Model for chat response with sources"""
    response: str
    message: str
    metadata: QueryMetadata
    source: Optional[QuerySource] = None

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