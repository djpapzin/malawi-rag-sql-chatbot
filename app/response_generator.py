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
        self.NULL_VALUE = "Not available"
        
        # Define standard field order
        self.general_field_order = [
            'PROJECTNAME',
            'PROJECTCODE',
            'PROJECTSECTOR',
            'REGION',
            'DISTRICT',
            'PROJECTSTATUS',
            'TOTALBUDGET',
            'COMPLETIONPERCENTAGE'
        ]
        
        self.specific_field_order = [
            # Basic Information
            'PROJECTNAME',
            'PROJECTCODE',
            'PROJECTSECTOR',
            'REGION',
            'DISTRICT',
            'PROJECTSTATUS',
            # Implementation Details
            'CONTRACTORNAME',
            'STARTDATE',
            'COMPLETIONESTIDATE',
            'COMPLETIONPERCENTAGE',
            'STAGE',
            # Financial Information
            'TOTALBUDGET',
            'TOTALEXPENDITURETODATE',
            'FUNDINGSOURCE',
            # Additional Information
            'PROJECTDESC',
            'TRADITIONALAUTHORITY',
            'LASTVISIT'
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
            
    def _format_metadata(self, query_time: datetime, total_results: int, filters_applied: List[str] = None) -> str:
        """Format metadata section of response"""
        metadata = [
            "\nMetadata:",
            f"Results Found: {total_results}",
            f"Query Time: {query_time.total_seconds():.3f} seconds"
        ]
        
        if filters_applied:
            metadata.append("Filters Applied:")
            for filter_info in filters_applied:
                metadata.append(f"- {filter_info}")
                
        return "\n".join(metadata)
        
    def _format_project_list(self, df: pd.DataFrame, query_info: Dict[str, Any] = None) -> str:
        """Format a list of projects for display"""
        if df.empty:
            return "No projects found matching your criteria."
            
        # Start timing for metadata
        start_time = datetime.now()
        
        # Format summary
        summary = []
        total_projects = len(df)
        total_budget = df['TOTALBUDGET'].sum() if 'TOTALBUDGET' in df.columns else None
        avg_completion = df['COMPLETIONPERCENTAGE'].mean() if 'COMPLETIONPERCENTAGE' in df.columns else None
        
        summary.append(f"Found {total_projects} project{'s' if total_projects != 1 else ''}")
        if total_budget is not None and not pd.isna(total_budget):
            summary.append(f"Total Budget: {self._format_currency(total_budget)}")
        if avg_completion is not None and not pd.isna(avg_completion):
            summary.append(f"Average Completion: {self._format_percentage(avg_completion)}")
            
        # Format individual projects
        formatted_projects = []
        for _, row in df.iterrows():
            project_details = []
            
            # Add fields in standard order
            for field in self.general_field_order:
                if field in row.index:
                    value = row[field]
                    formatted_value = (
                        self._format_currency(value) if field in self.currency_columns
                        else self._format_date(value) if field in self.date_columns
                        else self._format_percentage(value) if field == 'COMPLETIONPERCENTAGE'
                        else self._format_value(value)
                    )
                    project_details.append(f"{field.title()}: {formatted_value}")
                    
            formatted_projects.append("\n".join(project_details))
            
        # Get filters applied
        filters_applied = []
        if query_info:
            if 'sector' in query_info:
                filters_applied.append(f"Sector: {query_info['sector']}")
            if 'region' in query_info:
                filters_applied.append(f"Region: {query_info['region']}")
            if 'status' in query_info:
                filters_applied.append(f"Status: {query_info['status']}")
                
        # Combine all sections
        response_parts = [
            "\n".join(summary),
            "\nProjects:",
            "\n\n".join(formatted_projects),
            self._format_metadata(datetime.now() - start_time, total_projects, filters_applied)
        ]
        
        return "\n\n".join(response_parts)
        
    def _format_specific_project(self, project: pd.Series, is_code_query: bool = False) -> str:
        """Format a specific project's details"""
        try:
            start_time = datetime.now()
            
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
            
            # Build response sections
            sections = []
            
            # Basic Information
            basic_info = []
            if is_code_query:
                basic_info.extend([
                    f"Project Code: {formatted_values.get('PROJECTCODE', self.NULL_VALUE)}",
                    f"Project Name: {formatted_values.get('PROJECTNAME', self.NULL_VALUE)}"
                ])
            else:
                basic_info.extend([
                    f"Project Name: {formatted_values.get('PROJECTNAME', self.NULL_VALUE)}",
                    f"Project Code: {formatted_values.get('PROJECTCODE', self.NULL_VALUE)}"
                ])
            basic_info.extend([
                f"Sector: {formatted_values.get('PROJECTSECTOR', self.NULL_VALUE)}",
                f"Region: {formatted_values.get('REGION', self.NULL_VALUE)}",
                f"District: {formatted_values.get('DISTRICT', self.NULL_VALUE)}",
                f"Status: {formatted_values.get('PROJECTSTATUS', self.NULL_VALUE)}"
            ])
            sections.append("\n".join(basic_info))
            
            # Implementation Details
            if any(field in formatted_values for field in ['CONTRACTORNAME', 'STARTDATE', 'COMPLETIONESTIDATE', 'COMPLETIONPERCENTAGE']):
                impl_details = ["\nImplementation Details:"]
                for field in ['CONTRACTORNAME', 'STARTDATE', 'COMPLETIONESTIDATE', 'COMPLETIONPERCENTAGE', 'STAGE']:
                    if field in formatted_values:
                        impl_details.append(f"{field.title()}: {formatted_values[field]}")
                sections.append("\n".join(impl_details))
            
            # Financial Information
            if any(field in formatted_values for field in ['TOTALBUDGET', 'TOTALEXPENDITURETODATE', 'FUNDINGSOURCE']):
                financial_info = ["\nFinancial Information:"]
                for field in ['TOTALBUDGET', 'TOTALEXPENDITURETODATE', 'FUNDINGSOURCE']:
                    if field in formatted_values:
                        financial_info.append(f"{field.title()}: {formatted_values[field]}")
                sections.append("\n".join(financial_info))
            
            # Additional Information
            if formatted_values.get('PROJECTDESC', self.NULL_VALUE) != self.NULL_VALUE:
                sections.append("\nProject Description:")
                sections.append(formatted_values['PROJECTDESC'])
            
            # Add metadata
            sections.append(self._format_metadata(
                datetime.now() - start_time,
                1,
                [f"Query Type: {'Project Code' if is_code_query else 'Project Name'} Search"]
            ))
            
            return "\n\n".join(sections)
            
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
                if query_info.get("project_name", "").upper().startswith("MW-"):
                    is_code_query = True
                    
                return self._format_specific_project(project, is_code_query)
            
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