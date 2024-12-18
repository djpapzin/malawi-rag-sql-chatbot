import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
from .models import QueryMetadata, QuerySource

class ResponseGenerator:
    """Generates formatted responses from SQL query results"""
    
    def __init__(self):
        self.default_limit = 3  # Number of projects to show in initial response
    
    def format_project_details(self, project: Dict[str, Any]) -> str:
        """Format individual project details"""
        return f"""
Project: {project.get('project_name', 'N/A')}
Location: {project.get('region', 'N/A')}, {project.get('district', 'N/A')}
Sector: {project.get('sector', 'N/A')}
Status: {project.get('status', 'N/A')}
Budget: ${project.get('budget', 0):,.2f}
Completion: {project.get('completion_percentage', 0)}%
"""
    
    def generate_response(self, df: pd.DataFrame, query_metadata: QueryMetadata,
                         filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a formatted response with source information
        
        Args:
            df: DataFrame with query results
            query_metadata: Metadata about the query execution
            filters: Applied filters (optional)
            
        Returns:
            Dict with formatted response and metadata
        """
        try:
            if df.empty:
                return {
                    "answer": "No projects found matching your criteria.",
                    "metadata": query_metadata,
                    "sources": []
                }
            
            # Calculate summary statistics
            total_projects = len(df)
            total_budget = df['budget'].sum() if 'budget' in df.columns else 0
            avg_completion = df['completion_percentage'].mean() if 'completion_percentage' in df.columns else 0
            
            # Format header based on filters
            header = self._generate_header(filters, total_projects, total_budget, avg_completion)
            
            # Format project details
            projects_shown = min(self.default_limit, total_projects)
            details = []
            for _, project in df.head(projects_shown).iterrows():
                details.append(self.format_project_details(project))
            
            # Add pagination info if needed
            remaining = total_projects - projects_shown
            pagination_info = f"\n\nShowing {projects_shown} of {total_projects} projects. "
            if remaining > 0:
                pagination_info += f"There are {remaining} more projects. Type 'show more' to see additional results."
            
            # Combine all parts
            answer = f"{header}\n\n{''.join(details)}{pagination_info}"
            
            # Format source information
            sources = self._format_sources(query_metadata.sources, df)
            
            return {
                "answer": answer,
                "metadata": {
                    "query_id": query_metadata.query_id,
                    "execution_time": query_metadata.execution_time,
                    "row_count": query_metadata.row_count,
                    "timestamp": query_metadata.timestamp.isoformat()
                },
                "sources": sources
            }

        except Exception as e:
            return {
                "answer": f"Error generating response: {str(e)}",
                "metadata": query_metadata,
                "sources": []
            }
    
    def _generate_header(self, filters: Dict[str, Any], total: int, 
                        budget: float, completion: float) -> str:
        """Generate response header based on filters"""
        parts = [f"Found {total} project(s)"]
        
        if filters:
            conditions = []
            if filters.get('sector'):
                conditions.append(f"sector: {filters['sector']}")
            if filters.get('region'):
                conditions.append(f"region: {filters['region']}")
            if filters.get('status'):
                conditions.append(f"status: {filters['status']}")
            if conditions:
                parts.append(f"matching {', '.join(conditions)}")
        
        parts.append(f"\nTotal Budget: ${budget:,.2f}")
        parts.append(f"Average Completion: {completion:.1f}%")
        
        return " ".join(parts)
    
    def _format_sources(self, sources: List[QuerySource], df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Format source information with sample data"""
        formatted_sources = []
        
        for source in sources:
            # Get sample data for the table
            if source.table_name in df:
                sample = df[source.table_name].head(1).to_dict('records')[0] if not df.empty else {}
            else:
                sample = {}
            
            formatted_sources.append({
                "table": source.table_name,
                "columns": source.columns,
                "operation": source.operation,
                "sample_data": sample
            })
        
        return formatted_sources