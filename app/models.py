from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel, Field
import logging
from datetime import datetime
import pandas as pd
import sqlite3
from contextlib import contextmanager
from decimal import Decimal

logger = logging.getLogger(__name__)

# Base Models
class Location(BaseModel):
    """Model for location information"""
    region: str
    district: str

class MonetaryValue(BaseModel):
    """Model for monetary values with formatting"""
    amount: Decimal
    formatted: str

class ContractorInfo(BaseModel):
    """Model for contractor information"""
    name: str
    contract_start_date: str

class ProjectBase(BaseModel):
    """Base model for project information"""
    project_name: str
    fiscal_year: str
    location: Location
    budget: MonetaryValue
    status: str
    sector: str

class ProjectGeneral(ProjectBase):
    """Model for general project information"""
    pass

class ProjectSpecific(ProjectBase):
    """Model for specific project information"""
    contractor: ContractorInfo
    expenditure_to_date: MonetaryValue
    funding_source: str
    project_code: str
    last_monitoring_visit: str

class Summary(BaseModel):
    """Model for query summary information"""
    total_projects: int
    total_budget: MonetaryValue

class ResponseMetadata(BaseModel):
    """Model for response metadata"""
    query_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    query_id: str

# Response Models
class GeneralQueryResponse(BaseModel):
    """Model for general query responses"""
    query_type: str = "general"
    results: List[ProjectGeneral]
    summary: Summary
    metadata: ResponseMetadata

class SpecificQueryResponse(BaseModel):
    """Model for specific query responses"""
    query_type: str = "specific"
    result: ProjectSpecific
    metadata: ResponseMetadata

# Legacy Models (for backward compatibility)
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

class QueryMetadata(BaseModel):
    """Model for query execution metadata"""
    timestamp: str
    query_id: str
    processing_time: float

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    """Model for chat response with sources"""
    response: str
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

# Utility functions for formatting
def format_currency(amount: Decimal) -> str:
    """Format currency in MWK format"""
    return f"MWK {amount:,.2f}"

def format_date(date_str: str) -> str:
    """Format date in consistent format"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        return date_str