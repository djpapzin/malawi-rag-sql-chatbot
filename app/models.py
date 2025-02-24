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
    fiscal_year: str
    location: Location
    total_budget: MonetaryAmount
    project_status: str
    project_sector: str

class DetailedProjectInfo(GeneralProjectInfo):
    """Model for detailed project information"""
    contractor: Contractor
    expenditure_to_date: MonetaryAmount
    source_of_funding: str
    project_code: str
    last_monitoring_visit: str

class GeneralQueryResponse(BaseModel):
    """Model for general query response"""
    query_type: str = "general"
    results: List[GeneralProjectInfo]
    metadata: QueryMetadata

class SpecificQueryResponse(BaseModel):
    """Model for specific query response"""
    query_type: str = "specific"
    results: List[DetailedProjectInfo]
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
    response: str

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