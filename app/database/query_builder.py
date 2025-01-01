# database/query_builder.py 
from typing import Dict, List, Any, Tuple, Optional
import sqlite3
import pandas as pd
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = 'malawi_projects1.db'):
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def build_base_query(self, conditions: List[str]) -> str:
        return f"""
            SELECT 
                PROJECTNAME,
                PROJECTSTATUS,
                PROJECTSECTOR,
                PROJECTTYPE,
                REGION,
                DISTRICT,
                BUDGET,
                COMPLETIONPERCENTAGE,
                PROJECTDESC
            FROM proj_dashboard
            WHERE {' AND '.join(conditions)}
        """

    def build_status_conditions(self, filters: Dict[str, Any], conditions: List[str]) -> None:
        if filters.get('completed'):
            conditions.append("""
                (
                    CAST(COALESCE(COMPLETIONPERCENTAGE, 0) AS FLOAT) >= 100
                    OR LOWER(PROJECTSTATUS) LIKE '%complete%'
                    OR LOWER(PROJECTSTATUS) LIKE '%finished%'
                    OR LOWER(PROJECTSTATUS) LIKE '%done%'
                )
            """)
        elif filters.get('not_started'):
            conditions.append("""
                (
                    CAST(COALESCE(COMPLETIONPERCENTAGE, 0) AS FLOAT) <= 0.1 
                    OR COMPLETIONPERCENTAGE IS NULL 
                    OR LOWER(PROJECTSTATUS) LIKE '%not started%'
                    OR LOWER(PROJECTSTATUS) LIKE '%pending%'
                    OR PROJECTSTATUS IS NULL
                )
            """)
        elif filters.get('in_progress'):
            conditions.append("""
                (
                    CAST(COALESCE(COMPLETIONPERCENTAGE, 0) AS FLOAT) BETWEEN 0.1 AND 99.9
                    AND LOWER(COALESCE(PROJECTSTATUS, '')) NOT LIKE '%complete%'
                )
            """)

    def build_budget_conditions(self, filters: Dict[str, Any], conditions: List[str], params: List[Any]) -> None:
        if filters.get('has_budget') or filters.get('sort_by') in ['budget_desc', 'budget_asc']:
            conditions.append("COALESCE(BUDGET, 0) > 0")
        
        if filters.get('min_budget'):
            conditions.append("COALESCE(BUDGET, 0) >= ?")
            params.append(float(filters['min_budget']))
        if filters.get('max_budget'):
            conditions.append("COALESCE(BUDGET, 0) <= ?")
            params.append(float(filters['max_budget']))

    def get_project_data(self, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        try:
            conditions = ["ISLATEST = 1"]
            params = []

            if filters:
                if filters.get('sector'):
                    conditions.append("PROJECTSECTOR = ?")
                    params.append(filters['sector'])

                if filters.get('region'):
                    conditions.append("REGION = ?")
                    params.append(filters['region'])

                self.build_status_conditions(filters, conditions)
                self.build_budget_conditions(filters, conditions, params)

            query = self.build_base_query(conditions)
            
            logger.info(f"Executing query: {query}")
            logger.info(f"Query parameters: {params}")

            with self.get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=params)
                logger.info(f"Query returned {len(df)} results")
                return df

        except Exception as e:
            logger.error(f"Error retrieving project data: {e}", exc_info=True)
            return pd.DataFrame()

    def format_results(self, results: List[Dict[str, Any]], total_count: int = 0) -> str:
        """Format query results into a readable response"""
        if not results:
            return "No projects found matching your criteria."
        
        response = []
        
        # Format each project
        for i, project in enumerate(results[:3]):  # Show first 3 projects
            response.append(f"\nProject: {project.get('project_name', 'Unnamed Project')}")
            response.append(f"Location: {project.get('region', 'Unknown Region')}, {project.get('district', 'Unknown District')}")
            
        # Add summary of remaining results
        if total_count > 3:
            remaining = total_count - 3
            response.append(f"\n\nShowing 3 of {total_count} projects. There are {remaining} more projects. Type 'show more' to see additional results.")
        
        return "\n".join(response)