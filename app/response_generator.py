"""Response Generator Module

This module handles the generation of formatted responses from query results.
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
import logging
from .models import QuerySource

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Generates formatted responses from query results"""
    
    def __init__(self):
        """Initialize response generator"""
        self.currency_columns = ['TOTALBUDGET', 'TOTALEXPENDITUREYEAR']
        self.date_columns = ['SIGNINGDATE', 'LASTVISIT', 'STARTDATE', 'COMPLETIONESTIDATE']
        self.NULL_VALUE = "Not available"
        
        # Define standard field order for general queries (6 fields as per spec)
        self.general_field_order = [
            'PROJECTNAME',      # Name of project
            'FISCALYEAR',       # Fiscal year
            'DISTRICT',         # Location
            'TOTALBUDGET',      # Budget
            'PROJECTSTATUS',    # Status
            'PROJECTSECTOR'     # Project Sector
        ]
        
        # Define standard field order for specific queries (all fields)
        self.specific_field_order = [
            # Core Information
            'PROJECTNAME',              # Name of project
            'PROJECTCODE',             # Project code
            'PROJECTSECTOR',           # Sector
            'PROJECTSTATUS',           # Status
            'STAGE',                   # Project stage
            
            # Location Information
            'REGION',                  # Region
            'DISTRICT',                # Location
            'TRADITIONALAUTHORITY',    # Traditional Authority
            
            # Financial Information
            'TOTALBUDGET',             # Budget
            'TOTALEXPENDITUREYEAR',    # Expenditure to date
            'FUNDINGSOURCE',           # Source of funding
            
            # Timeline Information
            'STARTDATE',               # Contract start date
            'COMPLETIONESTIDATE',      # Estimated completion date
            'LASTVISIT',               # Date of last Council monitoring visit
            'COMPLETIONPERCENTAGE',    # Completion percentage
            
            # Contractor Information
            'CONTRACTORNAME',          # Contractor name
            'SIGNINGDATE',             # Contract signing date
            
            # Additional Information
            'PROJECTDESC',             # Project description
            'FISCALYEAR'               # Fiscal year
        ]
        
    def _format_value(self, value: Any) -> str:
        """Format any value with consistent null handling"""
        if pd.isna(value) or value is None or str(value).strip() == '':
            return self.NULL_VALUE
        return str(value)
        
    def _format_currency(self, value: float) -> str:
        """Format currency values with commas and 2 decimal places"""
        try:
            if pd.isna(value) or value is None or str(value).strip() == '':
                return self.NULL_VALUE
            return f"MWK {value:,.2f}"
        except:
            return self.NULL_VALUE
            
    def _format_date(self, date_str: str) -> str:
        """Format date strings to a readable format"""
        try:
            if pd.isna(date_str) or date_str is None or str(date_str).strip() == '':
                return self.NULL_VALUE
            date_obj = datetime.strptime(str(date_str), '%Y-%m-%d')
            return date_obj.strftime('%B %d, %Y')
        except:
            return self.NULL_VALUE
            
    def _format_percentage(self, value: float) -> str:
        """Format percentage values"""
        try:
            if pd.isna(value) or value is None or str(value).strip() == '':
                return self.NULL_VALUE
            return f"{value:.1f}%"
        except:
            return self.NULL_VALUE
            
    def _format_no_results(self, query_type: str, query_info: Dict[str, Any]) -> str:
        """Format response when no results are found"""
        if query_type == "specific":
            project_identifier = query_info.get("project_identifier", "")
            if project_identifier.startswith("MW-"):
                return f"No project found with code {project_identifier}. Please verify the project code and try again."
            else:
                return f"No project found matching '{project_identifier}'. Please verify the project name and try again."
        else:
            return "No projects found matching your criteria. Please try different search terms."
            
    def _format_specific_project(self, project: pd.Series, is_code_query: bool = False) -> str:
        """Format a specific project's details according to specification"""
        try:
            # Format all values first
            formatted_values = {}
            for field in self.specific_field_order:
                if field in project.index:
                    value = project[field]
                    formatted_values[field] = (
                        self._format_currency(value) if field in self.currency_columns
                        else self._format_date(value) if field in self.date_columns
                        else self._format_percentage(value) if field == 'COMPLETIONPERCENTAGE'
                        else self._format_value(value)
                    )
            
            # Build response with sections
            sections = {
                "Core Information": ['PROJECTNAME', 'PROJECTCODE', 'PROJECTSECTOR', 'PROJECTSTATUS', 'STAGE'],
                "Location": ['REGION', 'DISTRICT', 'TRADITIONALAUTHORITY'],
                "Financial Details": ['TOTALBUDGET', 'TOTALEXPENDITUREYEAR', 'FUNDINGSOURCE'],
                "Timeline": ['STARTDATE', 'COMPLETIONESTIDATE', 'LASTVISIT', 'COMPLETIONPERCENTAGE'],
                "Contractor Details": ['CONTRACTORNAME', 'SIGNINGDATE'],
                "Additional Information": ['PROJECTDESC', 'FISCALYEAR']
            }
            
            # User-friendly field names
            field_display_names = {
                'PROJECTNAME': 'Project Name',
                'PROJECTCODE': 'Project Code',
                'PROJECTSECTOR': 'Sector',
                'PROJECTSTATUS': 'Status',
                'STAGE': 'Current Stage',
                'REGION': 'Region',
                'DISTRICT': 'District',
                'TRADITIONALAUTHORITY': 'Traditional Authority',
                'TOTALBUDGET': 'Total Budget',
                'TOTALEXPENDITUREYEAR': 'Expenditure to Date',
                'FUNDINGSOURCE': 'Source of Funding',
                'STARTDATE': 'Start Date',
                'COMPLETIONESTIDATE': 'Estimated Completion Date',
                'LASTVISIT': 'Last Council Monitoring Visit',
                'COMPLETIONPERCENTAGE': 'Completion Progress',
                'CONTRACTORNAME': 'Contractor',
                'SIGNINGDATE': 'Contract Signing Date',
                'PROJECTDESC': 'Description',
                'FISCALYEAR': 'Fiscal Year'
            }
            
            # Build the response section by section
            response_parts = []
            
            # Add project name as header
            project_name = formatted_values.get('PROJECTNAME', 'Project Details')
            response_parts.append(f"# {project_name}")
            response_parts.append("")
            
            # Add each section
            for section_name, fields in sections.items():
                section_content = []
                for field in fields:
                    if field in formatted_values:
                        display_name = field_display_names.get(field, field)
                        value = formatted_values[field]
                        
                        # Special handling for project description
                        if field == 'PROJECTDESC':
                            if value != self.NULL_VALUE:
                                section_content.append(f"{value}")
                            continue
                            
                        section_content.append(f"- {display_name}: {value}")
                
                # Only add section if it has content
                if section_content:
                    response_parts.append(f"## {section_name}")
                    response_parts.extend(section_content)
                    response_parts.append("")  # Empty line after section
            
            return "\n".join(response_parts).strip()
            
        except Exception as e:
            logger.error(f"Error formatting specific project: {str(e)}")
            return "Error: Unable to format project details"
            
    def format_response(self, query_type: str, results: pd.DataFrame, query_info: Dict[str, Any]) -> str:
        """Format the response based on query type and results"""
        try:
            if results.empty:
                return self._format_no_results(query_type, query_info)
            
            if query_type == "specific":
                # For specific queries, always use the first result
                project = results.iloc[0]
                
                # Check if this was a project code query
                is_code_query = False
                if query_info.get("project_identifier", "").upper().startswith("MW-"):
                    is_code_query = True
                    
                # Format the response with all required fields
                response = self._format_specific_project(project, is_code_query)
                
                # Add metadata about the query
                if query_info.get("project_identifier"):
                    response += f"\n\nQuery matched project: {query_info['project_identifier']}"
                
                return response
            
            else:
                return self._format_project_list(results, query_info)
            
        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            return "Error: Unable to format response"
            
    def generate_response(
        self,
        df: pd.DataFrame,
        sources: List[QuerySource],
        is_specific_project: bool = False
    ) -> Tuple[str, Dict[str, Any], QuerySource]:
        """Generate a formatted response with metadata"""
        try:
            # Start timing
            start_time = datetime.now()
            
            # Check if this is a specific project query based on the columns
            is_specific = is_specific_project or (len(df) == 1 and 'CONTRACTORNAME' in df.columns)
            
            # Generate formatted response based on query type
            if is_specific and not df.empty:
                response = self.format_response("specific", df, {})
            else:
                response = self.format_response("list", df, {})
                
            # Calculate query time
            query_time = datetime.now() - start_time
            
            # Create metadata
            metadata = {
                "query_time": str(query_time),
                "total_results": len(df),
                "current_page": 1,
                "total_pages": 1,
                "has_more": False
            }
            
            # Use first source if available
            source = sources[0] if sources else QuerySource(
                sql="",
                table="proj_dashboard",
                filters={}
            )
            
            logger.info(f"Generated response with {len(df)} results in {query_time}")
            return response, metadata, source
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise 