"""Response Formatter Module

This module handles the formatting of responses for different query types.
"""

from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ResponseFormatter:
    """Formats query responses for output"""
    
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
        
        self.sector_names = {
            'health': 'Health',
            'education': 'Education',
            'water': 'Water and Sanitation',
            'transport': 'Transport',
            'agriculture': 'Agriculture'
        }
    
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
    
    def format_response(self, query_type: str, results: List[Dict], parameters: Dict) -> Dict:
        """Format the response based on query type and results"""
        if not results:
            return self._format_no_results(query_type, parameters)
            
        if query_type == "specific":
            return self._format_specific_response(results[0])
        else:
            return self._format_general_response(results, parameters)
            
    def _format_no_results(self, query_type: str, parameters: Dict) -> Dict:
        """Format response when no results are found"""
        sector = parameters.get("filters", {}).get("sectors", [None])[0]
        district = parameters.get("filters", {}).get("districts", [None])[0]
        
        if sector:
            sector_name = self.sector_names.get(sector, sector.title())
            message = f"I couldn't find any projects in the {sector_name} sector. Would you like to try a different sector?"
        elif district:
            message = f"I couldn't find any projects in {district}. Would you like to try a different district?"
        else:
            message = "I couldn't find any projects matching your criteria. Could you try rephrasing your query?"
            
        return {
            "type": query_type,
            "message": message,
            "results": [],
            "metadata": {
                "total_results": 0,
                "filters_applied": parameters.get("filters", {})
            }
        }
        
    def _format_general_response(self, results: List[Dict], parameters: Dict) -> Dict:
        """Format response for general queries"""
        sector = parameters.get("filters", {}).get("sectors", [None])[0]
        district = parameters.get("filters", {}).get("districts", [None])[0]
        
        # Build summary message
        if sector:
            sector_name = self.sector_names.get(sector, sector.title())
            summary = f"I found {len(results)} projects in the {sector_name} sector."
        elif district:
            summary = f"I found {len(results)} projects in {district}."
        else:
            summary = f"I found {len(results)} projects matching your criteria."
            
        # Add budget information if available
        total_budget = sum(r.get("TOTALBUDGET", 0) for r in results)
        if total_budget > 0:
            summary += f" The total budget for these projects is MWK {total_budget:,.2f}."
            
        # Format project list
        project_list = []
        for r in results:
            project = {
                "name": r.get("PROJECTNAME", "Unnamed Project"),
                "district": r.get("DISTRICT", "Unknown Location"),
                "status": r.get("PROJECTSTATUS", "Status Unknown"),
                "budget": r.get("TOTALBUDGET", 0),
                "sector": r.get("PROJECTSECTOR", "Sector Unknown"),
                "completion": r.get("COMPLETIONPERCENTAGE", 0)
            }
            project_list.append(project)
            
        return {
            "type": "general",
            "message": summary,
            "results": project_list,
            "metadata": {
                "total_results": len(results),
                "filters_applied": parameters.get("filters", {}),
                "total_budget": total_budget
            }
        }
        
    def _format_specific_response(self, result: Dict) -> Dict:
        """Format response for specific project queries"""
        project_name = result.get("PROJECTNAME", "this project")
        status = result.get("PROJECTSTATUS", "unknown status")
        budget = result.get("TOTALBUDGET", 0)
        completion = result.get("COMPLETIONPERCENTAGE", 0)
        district = result.get("DISTRICT", "unknown location")
        sector = result.get("PROJECTSECTOR", "unknown sector")
        
        message = f"{project_name} is a {sector} project in {district}. "
        message += f"The project is currently {status} with {completion}% completion. "
        if budget > 0:
            message += f"The total budget is MWK {budget:,.2f}."
            
        return {
            "type": "specific",
            "message": message,
            "result": result,
            "metadata": {
                "project_name": project_name,
                "status": status,
                "budget": budget,
                "completion": completion,
                "district": district,
                "sector": sector
            }
        }
    
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