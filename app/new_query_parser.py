"""
Query Parser Module

This module provides SQL query generation for the Malawi infrastructure projects database
based on LLM classification results.
"""

import re
import logging
import os
import sys
from typing import Dict, Any, Tuple, List
from datetime import datetime
from app.llm_classification.new_classifier import QueryClassification

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

class QueryParser:
    """Parser for natural language queries to SQL"""
    
    def __init__(self):
        logger.info("Initializing QueryParser")
        
    async def parse_query(self, query: str, classification: QueryClassification) -> Dict[str, Any]:
        """
        Parse a natural language query into SQL based on classification
        
        Args:
            query: The query to parse
            classification: The classification result from LLM
            
        Returns:
            Dict containing query and metadata
        """
        logger.info(f"Parsing query: {query}")
        
        # Initialize response
        response = {
            "query": "",
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "original_query": query
            }
        }
        
        try:
            if classification.query_type == "specific":
                # Build specific project query
                response["query"] = self._build_specific_project_sql(
                    classification.parameters.project_identifier
                )
            elif classification.query_type == "general":
                # Build general query with filters
                response["query"] = self._build_general_query_sql(
                    classification.parameters.filters
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error parsing query: {e}")
            return {
                "query": "",
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "original_query": query,
                    "error": str(e)
                }
            }
    
    def _build_specific_project_sql(self, project_identifier: str) -> str:
        """Build SQL for specific project query"""
        if not project_identifier:
            return ""
            
        # Handle project codes
        if re.match(r'^MW-[A-Z]{2}-[A-Z0-9]{2}$', project_identifier, re.IGNORECASE):
            return f"""
                SELECT 
                    projectname as project_name,
                    projectcode as project_code,
                    projectsector as project_sector,
                    projectstatus as status,
                    stage,
                    region,
                    district,
                    traditionalauthority,
                    budget as total_budget,
                    totalexpenditureyear as total_expenditure,
                    fundingsource as funding_source,
                    startdate as start_date,
                    completionestidate as completion_date,
                    lastvisit as last_monitoring_visit,
                    completionpercentage as completion_progress,
                    contractorname as contractor,
                    signingdate as contract_signing_date,
                    projectdesc as description,
                    fiscalyear as fiscal_year
                FROM proj_dashboard
                WHERE ISLATEST = 1
                AND UPPER(PROJECTCODE) = '{project_identifier.upper()}'
                ORDER BY
                    CASE 
                        WHEN LOWER(PROJECTSTATUS) = 'ongoing' THEN 1
                        WHEN LOWER(PROJECTSTATUS) = 'completed' THEN 2
                        ELSE 3
                    END,
                    budget DESC
                LIMIT 1
            """
        
        # Handle project names
        project_name = project_identifier.replace("'", "''")
        return f"""
            SELECT 
                projectname as project_name,
                projectcode as project_code,
                projectsector as project_sector,
                projectstatus as status,
                stage,
                region,
                district,
                traditionalauthority,
                budget as total_budget,
                totalexpenditureyear as total_expenditure,
                fundingsource as funding_source,
                startdate as start_date,
                completionestidate as completion_date,
                lastvisit as last_monitoring_visit,
                completionpercentage as completion_progress,
                contractorname as contractor,
                signingdate as contract_signing_date,
                projectdesc as description,
                fiscalyear as fiscal_year
            FROM proj_dashboard
            WHERE ISLATEST = 1
            AND (
                LOWER(PROJECTNAME) LIKE LOWER('%{project_name}%')
                OR LOWER(PROJECTNAME) LIKE LOWER('%{project_name.replace(" ", "%")}%')
            )
            ORDER BY
                CASE 
                    WHEN LOWER(PROJECTNAME) = LOWER('{project_name}') THEN 1
                    WHEN LOWER(PROJECTNAME) LIKE LOWER('{project_name}%') THEN 2
                    WHEN LOWER(PROJECTNAME) LIKE LOWER('%{project_name}%') THEN 3
                    ELSE 4
                END,
                CASE 
                    WHEN LOWER(PROJECTSTATUS) = 'ongoing' THEN 1
                    WHEN LOWER(PROJECTSTATUS) = 'completed' THEN 2
                    ELSE 3
                END,
                budget DESC
            LIMIT 1
        """
    
    def _build_general_query_sql(self, filters: Dict[str, Any]) -> str:
        """Build SQL for general query with filters"""
        # Start with base query
        sql = """
            SELECT 
                projectname as project_name,
                fiscalyear as fiscal_year,
                district,
                budget as total_budget,
                projectstatus as status,
                projectsector as project_sector
            FROM 
                proj_dashboard
            WHERE 
                ISLATEST = 1
        """
        
        # Add filters
        conditions = []
        
        # District filter
        if filters.get("districts"):
            district_conditions = []
            for district in filters["districts"]:
                district = district.replace("'", "''")
                district_conditions.append(f"LOWER(district) = LOWER('{district}')")
            if district_conditions:
                conditions.append(f"({' OR '.join(district_conditions)})")
        
        # Sector filter
        if filters.get("sectors"):
            sector_conditions = []
            for sector in filters["sectors"]:
                sector = sector.replace("'", "''")
                sector_conditions.append(f"LOWER(projectsector) = LOWER('{sector}')")
            if sector_conditions:
                conditions.append(f"({' OR '.join(sector_conditions)})")
        
        # Status filter
        if filters.get("status"):
            status_conditions = []
            for status in filters["status"]:
                status = status.replace("'", "''")
                status_conditions.append(f"LOWER(projectstatus) = LOWER('{status}')")
            if status_conditions:
                conditions.append(f"({' OR '.join(status_conditions)})")
        
        # Budget range filter
        budget_range = filters.get("budget_range", {})
        if budget_range.get("min") is not None:
            conditions.append(f"budget >= {budget_range['min']}")
        if budget_range.get("max") is not None:
            conditions.append(f"budget <= {budget_range['max']}")
        
        # Time range filter
        time_range = filters.get("time_range", {})
        if time_range.get("start"):
            conditions.append(f"startdate >= '{time_range['start']}'")
        if time_range.get("end"):
            conditions.append(f"completionestidate <= '{time_range['end']}'")
        
        # Add all conditions
        for condition in conditions:
            sql += f"\nAND {condition}"
        
        # Add sorting and limits
        sql += """
            ORDER BY
                CASE 
                    WHEN LOWER(PROJECTSTATUS) = 'ongoing' THEN 1
                    WHEN LOWER(PROJECTSTATUS) = 'completed' THEN 2
                    ELSE 3
                END,
                budget DESC
            LIMIT 10
        """
        
        return sql 