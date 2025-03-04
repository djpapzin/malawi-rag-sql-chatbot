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
        
        # Define standard field order for general queries (6 fields as per spec)
        self.general_field_order = [
            'PROJECTNAME',      # Name of project
            'FISCALYEAR',       # Fiscal year
            'DISTRICT',         # Location
            'TOTALBUDGET',      # Budget
            'PROJECTSTATUS',    # Status
            'PROJECTSECTOR'     # Project Sector
        ]
        
        # Define standard field order for specific queries (12 fields as per spec)
        self.specific_field_order = [
            'PROJECTNAME',              # Name of project
            'FISCALYEAR',              # Fiscal year
            'DISTRICT',                # Location
            'TOTALBUDGET',             # Budget
            'PROJECTSTATUS',           # Status
            'CONTRACTORNAME',          # Contractor name
            'STARTDATE',               # Contract start date
            'TOTALEXPENDITURETODATE',  # Expenditure to date
            'PROJECTSECTOR',           # Sector
            'FUNDINGSOURCE',           # Source of funding
            'PROJECTCODE',             # Project code
            'LASTVISIT'                # Date of last Council monitoring visit
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
        
    def format_budget(self, value: float) -> str:
        """Format budget value with MWK currency and proper formatting"""
        if isinstance(value, (int, float)):
            return f"MWK {value:,.2f}"
        return str(value)

    def format_project_results(self, results: List[Dict]) -> str:
        """Format project results into a readable response"""
        if not results:
            return "I couldn't find any matching projects."
        
        total_budget = sum(float(r.get('total_budget', 0)) for r in results)
        response = [
            f"I found {len(results)} projects with a total budget of {self.format_budget(total_budget)}. "
            "The projects include:"
        ]
        
        for project in results[:5]:  # Show first 5 projects
            budget = self.format_budget(float(project.get('total_budget', 0)))
            status = project.get('project_status', 'Unknown status')
            response.append(f"* {project['project_name']} - {status} ({budget})")
        
        if len(results) > 5:
            response.append(f"...and {len(results) - 5} more projects")
        
        return " ".join(response)

    def _format_project_list(self, df: pd.DataFrame, query_info: Dict[str, Any] = None) -> str:
        """Format a list of projects according to general query specification"""
        try:
            start_time = datetime.now()
            
            if df.empty:
                return "No projects found matching your criteria."
            
            # Format each project with only the required fields for general queries
            formatted_projects = []
            for idx, project in df.iterrows():
                project_details = []
                for field in self.general_field_order:
                    if field in project.index:
                        value = project[field]
                        formatted_value = (
                            self._format_currency(value) if field in self.currency_columns
                            else self._format_date(value) if field in self.date_columns
                            else self._format_value(value)
                        )
                        # Use more user-friendly field names
                        display_name = {
                            'PROJECTNAME': 'Name',
                            'FISCALYEAR': 'Fiscal Year',
                            'DISTRICT': 'Location',
                            'TOTALBUDGET': 'Budget',
                            'PROJECTSTATUS': 'Status',
                            'PROJECTSECTOR': 'Sector'
                        }.get(field, field)
                        project_details.append(f"- {display_name}: {formatted_value}")
                
                formatted_projects.append("\n".join(project_details))
            
            # Join all projects with clear separation
            response = "\n\n".join([
                f"Project {i+1}:\n{details}"
                for i, details in enumerate(formatted_projects)
            ])
            
            # Add metadata
            total_results = len(df)
            if query_info and query_info.get('total_count', total_results) > total_results:
                response = f"Found {query_info['total_count']} projects, showing first {total_results}:\n\n{response}"
            else:
                response = f"Found {total_results} projects:\n\n{response}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error formatting project list: {str(e)}")
            return "Error: Unable to format project list"
        
    def _format_specific_project(self, project: pd.Series, is_code_query: bool = False) -> str:
        """Format a specific project's details according to specification"""
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
                        else self._format_value(value)
                    )
            
            # Build response with user-friendly field names
            field_display_names = {
                'PROJECTNAME': 'Name of project',
                'FISCALYEAR': 'Fiscal year',
                'DISTRICT': 'Location',
                'TOTALBUDGET': 'Budget',
                'PROJECTSTATUS': 'Status',
                'CONTRACTORNAME': 'Contractor name',
                'STARTDATE': 'Contract start date',
                'TOTALEXPENDITURETODATE': 'Expenditure to date',
                'PROJECTSECTOR': 'Sector',
                'FUNDINGSOURCE': 'Source of funding',
                'PROJECTCODE': 'Project code',
                'LASTVISIT': 'Date of last Council monitoring visit'
            }
            
            details = []
            for field in self.specific_field_order:
                display_name = field_display_names.get(field, field)
                value = formatted_values.get(field, self.NULL_VALUE)
                details.append(f"- {display_name}: {value}")
            
            response = f"Project Details:\n\n" + "\n".join(details)
            
            return response
            
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