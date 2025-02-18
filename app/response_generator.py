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
        self.currency_columns = ['TOTALBUDGET', 'TOTALEXPENDITURETODATE']
        self.date_columns = ['SIGNINGDATE', 'LASTVISIT', 'STARTDATE', 'COMPLETIONESTIDATE']
        
    def _format_currency(self, value: float) -> str:
        """Format currency values with commas and 2 decimal places"""
        try:
            if pd.isna(value):
                return "Not available"
            return f"MWK {value:,.2f}"
        except:
            return str(value)
            
    def _format_date(self, date_str: str) -> str:
        """Format date strings to a readable format"""
        try:
            if pd.isna(date_str):
                return "Not available"
            date_obj = datetime.strptime(str(date_str), '%Y-%m-%d')
            return date_obj.strftime('%B %d, %Y')
        except:
            return str(date_str)
            
    def _format_percentage(self, value: float) -> str:
        """Format percentage values"""
        try:
            if pd.isna(value):
                return "Not available"
            return f"{value:.1f}%"
        except:
            return str(value)
            
    def _format_project_list(self, df: pd.DataFrame) -> str:
        """Format a list of projects for display"""
        if df.empty:
            return "No projects found matching your criteria."
            
        formatted_projects = []
        for _, row in df.iterrows():
            project_str = []
            project_str.append(f"Project: {row['PROJECTNAME']}")
            
            if 'PROJECTSECTOR' in row:
                project_str.append(f"Sector: {row['PROJECTSECTOR']}")
                
            if 'REGION' in row and 'DISTRICT' in row:
                location = f"Location: {row['REGION']}, {row['DISTRICT']}"
                project_str.append(location)
                
            if 'PROJECTSTATUS' in row:
                project_str.append(f"Status: {row['PROJECTSTATUS']}")
                
            if 'TOTALBUDGET' in row:
                budget = self._format_currency(row['TOTALBUDGET'])
                project_str.append(f"Budget: {budget}")
                
            if 'COMPLETIONPERCENTAGE' in row:
                completion = self._format_percentage(row['COMPLETIONPERCENTAGE'])
                project_str.append(f"Completion: {completion}")
                
            formatted_projects.append("\n".join(project_str))
            
        return "\n\n".join(formatted_projects)
        
    def _format_single_project(self, df: pd.DataFrame) -> str:
        """Format detailed information for a single project"""
        if df.empty:
            return "Project not found."
            
        row = df.iloc[0]
        sections = []
        
        # Basic Information
        basic_info = [
            f"# {row['PROJECTNAME']}",
            f"Project Code: {row['PROJECTCODE']}",
            f"Sector: {row['PROJECTSECTOR']}",
            f"Status: {row['PROJECTSTATUS']}",
            f"Stage: {row['STAGE']}"
        ]
        sections.append("\n".join(basic_info))
        
        # Location Information
        location_info = [
            "## Location",
            f"Region: {row['REGION']}",
            f"District: {row['DISTRICT']}",
            f"Traditional Authority: {row['TRADITIONALAUTHORITY']}"
        ]
        sections.append("\n".join(location_info))
        
        # Financial Information
        financial_info = [
            "## Financial Details",
            f"Total Budget: {self._format_currency(row['TOTALBUDGET'])}",
            f"Total Expenditure to Date: {self._format_currency(row['TOTALEXPENDITURETODATE'])}",
            f"Funding Source: {row['FUNDINGSOURCE']}"
        ]
        sections.append("\n".join(financial_info))
        
        # Timeline Information
        timeline_info = [
            "## Timeline",
            f"Start Date: {self._format_date(row['STARTDATE'])}",
            f"Estimated Completion Date: {self._format_date(row['COMPLETIONESTIDATE'])}",
            f"Last Site Visit: {self._format_date(row['LASTVISIT'])}",
            f"Completion Percentage: {self._format_percentage(row['COMPLETIONPERCENTAGE'])}"
        ]
        sections.append("\n".join(timeline_info))
        
        # Contractor Information
        contractor_info = [
            "## Contractor Details",
            f"Contractor: {row['CONTRACTORNAME']}",
            f"Contract Signing Date: {self._format_date(row['SIGNINGDATE'])}"
        ]
        sections.append("\n".join(contractor_info))
        
        # Project Description
        if pd.notna(row['PROJECTDESC']):
            description = [
                "## Project Description",
                str(row['PROJECTDESC'])
            ]
            sections.append("\n".join(description))
            
        return "\n\n".join(sections)
        
    def generate_response(
        self,
        df: pd.DataFrame,
        sources: List[QuerySource],
        is_specific_project: bool = False
    ) -> Tuple[str, Dict[str, Any], QuerySource]:
        """Generate a formatted response with metadata"""
        try:
            # Generate formatted response based on query type
            if is_specific_project:
                response = self._format_single_project(df)
            else:
                response = self._format_project_list(df)
                
            # Prepare metadata
            metadata = {
                "query_time": "0:00:00.000000",  # Placeholder
                "total_results": len(df),
                "current_page": 1,  # Default
                "total_pages": 1,  # Default
                "has_more": False  # Default
            }
            
            # Prepare source information
            source = sources[0] if sources else QuerySource(
                sql="",
                table="",
                filters={}
            )
            
            return response, metadata, source
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return str(e), {}, QuerySource(sql="", table="", filters={})