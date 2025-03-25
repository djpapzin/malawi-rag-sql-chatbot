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
            ("TOTALEXPENDITUREYEAR", "Expenditure to date", "currency"),
            ("PROJECTSECTOR", "Sector"),
            ("FUNDINGSOURCE", "Source of funding"),
            ("PROJECTCODE", "Project code"),
            ("LASTVISIT", "Date of last Council monitoring visit", "date")
        ]
        
        # Updated sector names to match query parser
        self.sector_names = {
            'health': 'Health',
            'healthcare': 'Health',
            'medical': 'Health',
            'hospital': 'Health',
            'clinic': 'Health',
            'education': 'Education',
            'school': 'Education',
            'university': 'Education',
            'classroom': 'Education',
            'infrastructure': 'Infrastructure',
            'road': 'Infrastructure',
            'bridge': 'Infrastructure',
            'transport': 'Infrastructure',
            'water': 'Water and sanitation',
            'sanitation': 'Water and sanitation',
            'irrigation': 'Water and sanitation',
            'rural development': 'Rural Development',
            'rural': 'Rural Development',
            'village': 'Rural Development',
            'rural roads': 'Rural Development',
            'rural infrastructure': 'Rural Development',
            'urban development': 'Urban Development',
            'urban': 'Urban Development',
            'city': 'Urban Development',
            'environment': 'Environment',
            'climate': 'Environment',
            'forestry': 'Environment',
            'governance': 'Governance',
            'administration': 'Governance',
            'agriculture': 'Agriculture',
            'farming': 'Agriculture',
            'energy': 'Energy',
            'power': 'Energy',
            'electricity': 'Energy'
        }
    
    def format_value(self, value: Any, format_type: str = None) -> str:
        """Format a value based on its type"""
        if pd.isna(value) or value is None or str(value).strip() == '':
            return self.NULL_VALUE
            
        if format_type == "currency":
            try:
                # Handle string values with commas and currency symbols
                if isinstance(value, str):
                    # Remove currency symbols and commas
                    value = value.replace('MWK', '').replace('MK', '').replace(',', '').strip()
                    value = float(value)
                elif isinstance(value, (int, float)):
                    value = float(value)
                else:
                    return str(value)
                
                # Format as currency with MWK symbol
                if value == 0:
                    return "MWK 0.00"
                return f"MWK {value:,.2f}"
            except Exception as e:
                logger.error(f"Error formatting currency value '{value}': {str(e)}")
                return str(value)
                
        elif format_type == "date":
            try:
                if isinstance(value, str):
                    # Try different date formats
                    date_formats = [
                        '%Y-%m-%d',
                        '%d/%m/%Y',
                        '%m/%d/%Y',
                        '%Y/%m/%d',
                        '%d-%m-%Y',
                        '%m-%d-%Y'
                    ]
                    
                    for fmt in date_formats:
                        try:
                            date_obj = datetime.strptime(value, fmt)
                            return date_obj.strftime('%B %d, %Y')
                        except:
                            continue
                            
                    # If no format matches, return original
                    return value
                elif isinstance(value, datetime):
                    return value.strftime('%B %d, %Y')
                else:
                    return str(value)
            except Exception as e:
                logger.error(f"Error formatting date value '{value}': {str(e)}")
                return str(value)
                
        elif format_type == "percentage":
            try:
                if isinstance(value, str):
                    value = value.replace('%', '').strip()
                return f"{float(value):.1f}%"
            except Exception as e:
                logger.error(f"Error formatting percentage value '{value}': {str(e)}")
                return str(value)
        else:
            return str(value)
    
    def format_response(self, results: List[Dict], query_type: str, metadata: Dict = None) -> Dict:
        """Format query results into a natural language response"""
        try:
            if not results:
                if query_type == "specific":
                    return {
                        "response": "I couldn't find any project matching that name. Please try a different project name or check the spelling.",
                        "metadata": metadata or {}
                    }
                elif query_type == "sector_query":
                    return {
                        "response": "I couldn't find any projects in that sector. Please try a different sector.",
                        "metadata": metadata or {}
                    }
                else:
                    return {
                        "response": "No results found for your query.",
                        "metadata": metadata or {}
                    }

            if query_type == "sector_query":
                # Get unique sectors and count projects
                sectors = {}
                for result in results:
                    sector = result.get('PROJECTSECTOR', 'Unknown')
                    if sector not in sectors:
                        sectors[sector] = []
                    sectors[sector].append(result)

                response_parts = []
                for sector, projects in sectors.items():
                    response_parts.append(f"Found {len(projects)} project(s) in {sector}:")
                    for project in projects[:5]:  # Limit to 5 projects per sector
                        project_details = []
                        if project.get('PROJECTNAME'):
                            project_details.append(f"Name: {project['PROJECTNAME']}")
                        if project.get('PROJECTSTATUS'):
                            project_details.append(f"Status: {project['PROJECTSTATUS']}")
                        if project.get('TOTALPROJECTCOST'):
                            formatted_cost = self.format_value(project['TOTALPROJECTCOST'], 'currency')
                            project_details.append(f"Budget: {formatted_cost}")
                        if project.get('STARTDATE'):
                            formatted_date = self.format_value(project['STARTDATE'], 'date')
                            project_details.append(f"Start Date: {formatted_date}")
                        response_parts.append("- " + ", ".join(project_details))
                    if len(projects) > 5:
                        response_parts.append(f"... and {len(projects) - 5} more project(s)")

                response = "\n".join(response_parts)

            elif query_type == "specific":
                result = results[0]
                project_details = []
                if result.get('PROJECTNAME'):
                    project_details.append(f"Project Name: {result['PROJECTNAME']}")
                if result.get('PROJECTCODE'):
                    project_details.append(f"Project Code: {result['PROJECTCODE']}")
                if result.get('PROJECTSECTOR'):
                    project_details.append(f"Sector: {result['PROJECTSECTOR']}")
                if result.get('PROJECTSTATUS'):
                    project_details.append(f"Status: {result['PROJECTSTATUS']}")
                if result.get('TOTALPROJECTCOST'):
                    formatted_cost = self.format_value(result['TOTALPROJECTCOST'], 'currency')
                    project_details.append(f"Total Budget: {formatted_cost}")
                if result.get('STARTDATE'):
                    formatted_date = self.format_value(result['STARTDATE'], 'date')
                    project_details.append(f"Start Date: {formatted_date}")
                if result.get('ENDDATE'):
                    formatted_date = self.format_value(result['ENDDATE'], 'date')
                    project_details.append(f"End Date: {formatted_date}")
                if result.get('IMPLEMENTINGAGENCY'):
                    project_details.append(f"Implementing Agency: {result['IMPLEMENTINGAGENCY']}")
                if result.get('DESCRIPTION'):
                    project_details.append(f"Description: {result['DESCRIPTION']}")
                
                response = "\n".join(project_details)
            else:
                response = "I found some results but I'm not sure how to format them. Please try rephrasing your question."

            return {
                "response": response,
                "metadata": metadata or {}
            }

        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            return {
                "response": "I encountered an error while formatting the response. Please try again.",
                "metadata": metadata or {}
            }
            
    def _format_no_results(self, query_type: str, parameters: Dict) -> Dict:
        """Format response when no results are found"""
        sector = parameters.get("filters", {}).get("sectors", [None])[0]
        district = parameters.get("filters", {}).get("districts", [None])[0]
        
        if sector:
            sector_name = self.sector_names.get(sector.lower(), sector.title())
            message = f"I couldn't find any projects in the {sector_name} sector. Would you like to try a different sector?"
        elif district:
            message = f"I couldn't find any projects in {district}. Would you like to try a different district?"
        else:
            message = "I couldn't find any projects matching your criteria. Could you try rephrasing your query?"
            
        return {
            "results": [
                {
                    "type": "text",
                    "message": message,
                    "data": {}
                }
            ],
            "metadata": {
                "total_results": 0,
                "query_type": query_type,
                "filters_applied": parameters.get("filters", {})
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