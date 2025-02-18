import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from .models import QueryMetadata, QuerySource
import logging

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Generates formatted responses from SQL query results"""
    
    def __init__(self, sql_tracker):
        self.sql_tracker = sql_tracker
        self.last_query = None
        logger.info("Initialized ResponseGenerator")
        
    def format_project(self, row: pd.Series) -> str:
        """Format a single project row into a readable string according to general query format"""
        try:
            # Format budget with commas and 2 decimal places
            budget = f"MWK {row['TOTALBUDGET']:,.2f}" if pd.notnull(row['TOTALBUDGET']) else "N/A"
            
            # Format the project information according to the specification
            return f"""Project Name: {row['PROJECTNAME']}
Fiscal Year: {row['FISCALYEAR']}
Location: {row['REGION']}, {row['DISTRICT']}
Budget: {budget}
Status: {row['PROJECTSTATUS']}
Sector: {row['PROJECTSECTOR']}"""

        except Exception as e:
            logger.error(f"Error formatting project: {str(e)}")
            return str(row)

    def format_summary_statistics(self, df: pd.DataFrame) -> str:
        """Generate summary statistics for the query results"""
        try:
            # Total projects per region
            region_stats = df.groupby('REGION').size()
            
            # Projects by sector
            sector_stats = df.groupby('PROJECTSECTOR').size()
            
            # Budget allocation by sector
            budget_by_sector = df.groupby('PROJECTSECTOR')['TOTALBUDGET'].sum()
            
            # Status distribution
            status_stats = df.groupby('PROJECTSTATUS').size()
            
            summary = "\n\nSummary Statistics:\n"
            summary += "\nProjects by Region:\n"
            for region, count in region_stats.items():
                summary += f"- {region}: {count} projects\n"
            
            summary += "\nProjects by Sector:\n"
            for sector, count in sector_stats.items():
                summary += f"- {sector}: {count} projects\n"
            
            summary += "\nBudget Allocation by Sector:\n"
            for sector, budget in budget_by_sector.items():
                summary += f"- {sector}: MWK {budget:,.2f}\n"
            
            summary += "\nProject Status Distribution:\n"
            for status, count in status_stats.items():
                summary += f"- {status}: {count} projects\n"
            
            return summary

        except Exception as e:
            logger.error(f"Error generating summary statistics: {str(e)}")
            return ""

    def generate_response(self, query: str, page: int = 1, page_size: int = 30, is_show_more: bool = False) -> Tuple[str, Dict]:
        """Generate a response based on the SQL query results"""
        try:
            logger.info(f"Executing query: {query}")
            # Execute the query
            df, sources = self.sql_tracker.execute_query(query)
            
            # Get the executed SQL and filters from sources
            executed_sql = sources[0].sql if sources else query
            filters = sources[0].filters if sources else {}
            
            if df.empty:
                logger.info("Query returned no results")
                return "No results found.", {
                    "message": "No results found.",
                    "total_results": 0,
                    "current_page": page,
                    "total_pages": 0,
                    "has_more": False,
                    "query_time": "0.0s",
                    "sql": executed_sql,  # Use executed SQL
                    "filters": filters  # Include filters
                }
            
            # Calculate pagination
            total_results = len(df)
            total_pages = (total_results + page_size - 1) // page_size
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, total_results)
            
            logger.info(f"Query returned {total_results} results")
            
            # Format results
            results = []
            for _, row in df.iloc[start_idx:end_idx].iterrows():
                results.append(self.format_project(row))
                
            # Generate response text
            response = "\n---\n".join(results)
            
            if is_show_more:
                message = f"Here are more results (page {page} of {total_pages}):"
            else:
                message = f"Found {total_results} projects. Showing page {page} of {total_pages}:"
            
            if page < total_pages:
                message += "\n\nType 'show more' to see additional results."
            
            metadata = {
                "message": message,
                "total_results": total_results,
                "current_page": page,
                "total_pages": total_pages,
                "has_more": page < total_pages,
                "query_time": "0.1s",  # Placeholder value
                "sql": executed_sql,  # Use executed SQL
                "filters": filters  # Include filters
            }
            
            return response, metadata
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return str(e), {
                "message": str(e),
                "total_results": 0,
                "current_page": page,
                "total_pages": 0,
                "has_more": False,
                "query_time": "0.0s",
                "sql": query,  # Use original query
                "filters": {}  # Empty filters
            }