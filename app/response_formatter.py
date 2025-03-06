"""Response Formatter Module

This module handles the formatting of responses for different query types.
"""

from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ResponseFormatter:
    """Formats responses for different query types"""
    
    def __init__(self):
        """Initialize response formatter"""
        self.NULL_VALUE = "Not available"
        
        # Define field groups for specific project queries
        self.specific_project_fields = {
            "Core Information": [
                ("project_name", "Project Name"),
                ("project_code", "Project Code"),
                ("project_sector", "Sector"),
                ("status", "Status"),
                ("stage", "Current Stage")
            ],
            "Location": [
                ("region", "Region"),
                ("district", "District"),
                ("traditionalauthority", "Traditional Authority")
            ],
            "Financial Details": [
                ("total_budget", "Total Budget", "currency"),
                ("total_expenditure", "Expenditure to Date", "currency"),
                ("funding_source", "Source of Funding")
            ],
            "Timeline": [
                ("start_date", "Start Date", "date"),
                ("completion_date", "Estimated Completion Date", "date"),
                ("last_monitoring_visit", "Last Council Monitoring Visit", "date"),
                ("completion_progress", "Completion Progress", "percentage")
            ],
            "Contractor Details": [
                ("contractor", "Contractor"),
                ("contract_signing_date", "Contract Signing Date", "date")
            ],
            "Additional Information": [
                ("description", "Description"),
                ("fiscal_year", "Fiscal Year")
            ]
        }
        
        # Define fields for general queries
        self.general_project_fields = [
            ("project_name", "Project Name"),
            ("fiscal_year", "Fiscal Year"),
            ("district", "Location"),
            ("total_budget", "Budget", "currency"),
            ("status", "Status"),
            ("project_sector", "Sector")
        ]
    
    def format_value(self, value: Any, format_type: str = None) -> str:
        """Format a value based on its type"""
        if pd.isna(value) or value is None or str(value).strip() == '':
            return self.NULL_VALUE
            
        if format_type == "currency":
            try:
                return f"MWK {float(value):,.2f}"
            except:
                return self.NULL_VALUE
        elif format_type == "date":
            try:
                date_obj = datetime.strptime(str(value), '%Y-%m-%d')
                return date_obj.strftime('%B %d, %Y')
            except:
                return self.NULL_VALUE
        elif format_type == "percentage":
            try:
                return f"{float(value):.1f}%"
            except:
                return self.NULL_VALUE
        else:
            return str(value)
    
    def format_specific_project(self, project: pd.Series) -> Dict[str, Any]:
        """Format a specific project query response"""
        try:
            response = {
                "type": "specific",
                "message": "Project Details",
                "data": {}
            }
            
            # Format each section
            for section_name, fields in self.specific_project_fields.items():
                section_data = {}
                for field in fields:
                    field_name = field[0]
                    display_name = field[1]
                    format_type = field[2] if len(field) > 2 else None
                    
                    if field_name in project.index:
                        value = self.format_value(project[field_name], format_type)
                        section_data[display_name] = value
                
                if section_data:
                    response["data"][section_name] = section_data
            
            return response
            
        except Exception as e:
            logger.error(f"Error formatting specific project: {str(e)}")
            return {
                "type": "error",
                "message": "Error formatting project details",
                "data": {}
            }
    
    def format_general_query(self, results: pd.DataFrame) -> Dict[str, Any]:
        """Format a general query response"""
        try:
            formatted_results = []
            for _, row in results.iterrows():
                project_data = {}
                for field, display_name, *format_type in self.general_project_fields:
                    if field in row.index:
                        value = self.format_value(row[field], format_type[0] if format_type else None)
                        project_data[display_name] = value
                formatted_results.append(project_data)
            
            return {
                "type": "list",
                "message": "Project List",
                "data": {
                    "fields": [field[1] for field in self.general_project_fields],
                    "values": formatted_results
                }
            }
            
        except Exception as e:
            logger.error(f"Error formatting general query: {str(e)}")
            return {
                "type": "error",
                "message": "Error formatting project list",
                "data": {}
            }
    
    def format_response(self, query_type: str, results: pd.DataFrame) -> Dict[str, Any]:
        """Format the response based on query type"""
        if results.empty:
            return {
                "type": "error",
                "message": "No projects found matching your criteria",
                "data": {}
            }
        
        if query_type == "specific":
            # For specific queries, always use the first result
            project = results.iloc[0]
            return self.format_specific_project(project)
        else:
            # For general queries, format as a list
            return self.format_general_query(results) 