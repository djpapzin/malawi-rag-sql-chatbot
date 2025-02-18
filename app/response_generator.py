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
        
    def _format_specific_project(self, project: pd.Series) -> str:
        """Format a specific project's details"""
        try:
            # Format all the values first
            formatted_values = {}
            for col in project.index:
                value = project[col]
                if col in self.currency_columns:
                    formatted_values[col] = self._format_currency(value)
                elif col in self.date_columns:
                    formatted_values[col] = self._format_date(value)
                else:
                    formatted_values[col] = str(value) if not pd.isna(value) else "Not available"

            # Build the response sections
            sections = []
            
            # Project Name and Basic Info
            sections.append(f"Project: {formatted_values.get('PROJECTNAME', 'Unknown Project')}")
            sections.append(f"Sector: {formatted_values.get('PROJECTSECTOR', 'Not specified')}")
            sections.append(f"Location: {formatted_values.get('REGION', 'Not specified')}, {formatted_values.get('DISTRICT', 'Not specified')}")
            sections.append(f"Status: {formatted_values.get('PROJECTSTATUS', 'Not specified')}")
            sections.append(f"Budget: {formatted_values.get('TOTALBUDGET', 'Not available')}")
            
            # Only add additional sections if this is a detailed query
            if 'CONTRACTORNAME' in formatted_values:
                # Implementation Details
                if formatted_values.get('CONTRACTORNAME', 'Not available') != 'Not available':
                    sections.append("\nImplementation Details:")
                    sections.append(f"Contractor: {formatted_values.get('CONTRACTORNAME', 'Not specified')}")
                    sections.append(f"Start Date: {formatted_values.get('STARTDATE', 'Not specified')}")
                    sections.append(f"Expected Completion: {formatted_values.get('COMPLETIONESTIDATE', 'Not specified')}")
                    sections.append(f"Completion Percentage: {formatted_values.get('COMPLETIONPERCENTAGE', 'Not available')}")
                
                # Financial Information
                if formatted_values.get('TOTALEXPENDITURETODATE', 'Not available') != 'Not available':
                    sections.append("\nFinancial Information:")
                    sections.append(f"Total Budget: {formatted_values.get('TOTALBUDGET', 'Not available')}")
                    sections.append(f"Expenditure to Date: {formatted_values.get('TOTALEXPENDITURETODATE', 'Not available')}")
                    sections.append(f"Funding Source: {formatted_values.get('FUNDINGSOURCE', 'Not specified')}")
                
                # Project Description
                if formatted_values.get('PROJECTDESC', 'Not available') != 'Not available':
                    sections.append("\nProject Description:")
                    sections.append(formatted_values.get('PROJECTDESC', 'Not available'))

            return "\n".join(sections)
            
        except Exception as e:
            logger.error(f"Error formatting specific project: {str(e)}")
            return "Error: Unable to format project details"
        
    def generate_response(
        self,
        df: pd.DataFrame,
        sources: List[QuerySource],
        is_specific_project: bool = False
    ) -> Tuple[str, Dict[str, Any], QuerySource]:
        """Generate a formatted response with metadata"""
        try:
            # Check if this is a specific project query based on the columns
            is_specific = is_specific_project or (len(df) == 1 and 'CONTRACTORNAME' in df.columns)
            
            # Generate formatted response based on query type
            if is_specific and not df.empty:
                response = self._format_specific_project(df.iloc[0])
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