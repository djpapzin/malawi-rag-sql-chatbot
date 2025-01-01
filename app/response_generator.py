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
        """Format a single project row into a readable string"""
        try:
            # Format budget with commas and 2 decimal places
            budget = f"MWK {row['budget']:,.2f}" if pd.notnull(row['budget']) else "N/A"
            
            # Format completion percentage
            completion = f"{row['completion_percentage']:.1f}%" if pd.notnull(row['completion_percentage']) else "N/A"
            
            # Format date
            start_date = pd.to_datetime(row['start_date']).strftime('%Y-%m-%d') if pd.notnull(row['start_date']) else "N/A"
            
            return f"""Project: {row['project_name']}
Location: {row['region']}, {row['district']}
Status: {row['status']} ({completion} complete)
Sector: {row['sector']}
Budget: {budget}
Start Date: {start_date}
Description: {row['description']}
"""
        except Exception as e:
            logger.error(f"Error formatting project: {str(e)}")
            return str(row)
        
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