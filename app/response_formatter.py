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
        
        # Define fields for general queries - exactly 6 fields
        self.general_project_fields = [
            ("PROJECTNAME", "Name of project"),
            ("FISCALYEAR", "Fiscal year"),
            ("DISTRICT", "Location"),
            ("TOTALBUDGET", "Budget", "currency"),
            ("PROJECTSTATUS", "Status"),
            ("PROJECTSECTOR", "Project Sector")
        ]
        
        # Define fields for specific queries - exactly 12 fields
        self.specific_project_fields = [
            ("PROJECTNAME", "Name of project"),
            ("FISCALYEAR", "Fiscal year"),
            ("DISTRICT", "Location"),
            ("TOTALBUDGET", "Budget", "currency"),
            ("PROJECTSTATUS", "Status"),
            ("CONTRACTORNAME", "Contractor name"),
            ("SIGNINGDATE", "Contract start date", "date"),
            ("TOTALEXPENDITURETODATE", "Expenditure to date", "currency"),
            ("PROJECTSECTOR", "Sector"),
            ("FUNDINGSOURCE", "Source of funding"),
            ("PROJECTCODE", "Project code"),
            ("LASTVISIT", "Date of last Council monitoring visit", "date")
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
            # Convert the dictionary to a pandas Series for detailed formatting
            # First, create a version with lowercase keys for the formatter
            result_dict = {}
            field_mapping = {
                'PROJECTNAME': 'project_name',
                'PROJECTCODE': 'project_code',
                'PROJECTSECTOR': 'project_sector',
                'PROJECTSTATUS': 'status',
                'STAGE': 'stage',
                'REGION': 'region',
                'DISTRICT': 'district',
                'TRADITIONALAUTHORITY': 'traditionalauthority',
                'TOTALBUDGET': 'total_budget',
                'TOTALEXPENDITURETODATE': 'total_expenditure',
                'FUNDINGSOURCE': 'funding_source',
                'STARTDATE': 'start_date',
                'COMPLETIONESTIDATE': 'completion_date',
                'LASTVISIT': 'last_monitoring_visit',
                'COMPLETIONPERCENTAGE': 'completion_progress',
                'CONTRACTORNAME': 'contractor',
                'SIGNINGDATE': 'contract_signing_date',
                'PROJECTDESC': 'description',
                'FISCALYEAR': 'fiscal_year'
            }
            
            # Map all fields from uppercase DB fields to lowercase formatter fields
            for db_field, formatter_field in field_mapping.items():
                if db_field in results[0]:
                    result_dict[formatter_field] = results[0][db_field]
                    
            project_series = pd.Series(result_dict)
            return self.format_specific_project(project_series)
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
            
        # Format project list
        project_list = []
        for r in results:
            project = {}
            for field_info in self.general_project_fields:
                db_field = field_info[0]
                display_name = field_info[1]
                format_type = field_info[2] if len(field_info) > 2 else None
                
                value = r.get(db_field, self.NULL_VALUE)
                formatted_value = self.format_value(value, format_type)
                project[display_name] = formatted_value
            project_list.append(project)
            
        return {
            "type": "general",
            "message": summary,
            "results": project_list,
            "metadata": {
                "total_results": len(results),
                "filters_applied": parameters.get("filters", {})
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
            
            # Format each field in order
            formatted_data = {}
            for field_info in self.specific_project_fields:
                db_field = field_info[0]
                display_name = field_info[1]
                format_type = field_info[2] if len(field_info) > 2 else None
                
                value = project.get(db_field, self.NULL_VALUE)
                formatted_value = self.format_value(value, format_type)
                formatted_data[display_name] = formatted_value
            
            response["data"] = formatted_data
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