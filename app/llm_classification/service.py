"""
Query Classification Service

This module provides services to integrate the hybrid classifier
with the existing codebase.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union

from .hybrid_classifier import HybridClassifier, QueryClassification, QueryType, QueryParameters

logger = logging.getLogger(__name__)

class QueryClassificationService:
    """
    Service to handle query classification and integration with existing codebase
    """
    
    def __init__(self):
        """Initialize the classification service"""
        self.classifier = HybridClassifier()
        logger.info("Initialized Query Classification Service")
    
    async def classify_query(self, query: str) -> QueryClassification:
        """
        Classify a query using the hybrid classifier
        
        Args:
            query: The natural language query to classify
            
        Returns:
            QueryClassification object with query type and parameters
        """
        return await self.classifier.classify_query(query)
    
    def generate_sql_from_classification(self, classification: QueryClassification) -> str:
        """
        Generate SQL query based on classification result
        
        Args:
            classification: The query classification result
            
        Returns:
            SQL query string
        """
        # Base SQL query
        sql = """
        SELECT * FROM proj_dashboard
        """
        
        # List to collect WHERE clauses
        where_clauses = []
        
        # Add district filter
        if classification.parameters.districts:
            district_conditions = []
            for district in classification.parameters.districts:
                district_conditions.append(f"LOWER(district) LIKE '%{district.lower()}%'")
            where_clauses.append(f"({' OR '.join(district_conditions)})")
        
        # Add sector filter
        if classification.parameters.sectors:
            sector_conditions = []
            for sector in classification.parameters.sectors:
                # Special handling for health sector
                if sector.lower() == "health":
                    sector_conditions.append("(LOWER(projectsector) LIKE '%health%' OR LOWER(projectsector) LIKE '%medical%' OR LOWER(projectsector) LIKE '%hospital%')")
                # Special handling for education sector
                elif sector.lower() == "education":
                    sector_conditions.append("(LOWER(projectsector) LIKE '%education%' OR LOWER(projectsector) LIKE '%school%' OR LOWER(projectsector) LIKE '%learning%')")
                # Special handling for water sector
                elif sector.lower() == "water":
                    sector_conditions.append("(LOWER(projectsector) LIKE '%water%' OR LOWER(projectsector) LIKE '%sanitation%')")
                # Special handling for transport sector
                elif sector.lower() == "transport":
                    sector_conditions.append("(LOWER(projectsector) LIKE '%transport%' OR LOWER(projectsector) LIKE '%road%' OR LOWER(projectsector) LIKE '%infrastructure%')")
                # Special handling for agriculture sector
                elif sector.lower() == "agriculture":
                    sector_conditions.append("(LOWER(projectsector) LIKE '%agriculture%' OR LOWER(projectsector) LIKE '%farming%' OR LOWER(projectsector) LIKE '%crop%')")
                else:
                    sector_conditions.append(f"LOWER(projectsector) LIKE '%{sector.lower()}%'")
            where_clauses.append(f"({' OR '.join(sector_conditions)})")
        
        # Add project filter
        if classification.parameters.projects:
            project_conditions = []
            for project in classification.parameters.projects:
                project_conditions.append(f"LOWER(projectname) LIKE '%{project.lower()}%'")
            where_clauses.append(f"({' OR '.join(project_conditions)})")
        
        # Add budget filter
        if classification.parameters.budget_range["min"] is not None:
            where_clauses.append(f"CAST(REPLACE(REPLACE(budget, ',', ''), 'MWK', '') AS FLOAT) >= {classification.parameters.budget_range['min']}")
        if classification.parameters.budget_range["max"] is not None:
            where_clauses.append(f"CAST(REPLACE(REPLACE(budget, ',', ''), 'MWK', '') AS FLOAT) <= {classification.parameters.budget_range['max']}")
        
        # Add status filter
        if classification.parameters.status:
            status_conditions = []
            for status in classification.parameters.status:
                if status.lower() == "completed":
                    status_conditions.append("LOWER(status) LIKE '%completed%' OR LOWER(status) LIKE '%finished%'")
                elif status.lower() == "ongoing":
                    status_conditions.append("LOWER(status) LIKE '%ongoing%' OR LOWER(status) LIKE '%progress%' OR LOWER(status) LIKE '%active%'")
                elif status.lower() == "planned":
                    status_conditions.append("LOWER(status) LIKE '%planned%' OR LOWER(status) LIKE '%proposed%' OR LOWER(status) LIKE '%future%'")
                else:
                    status_conditions.append(f"LOWER(status) LIKE '%{status.lower()}%'")
            where_clauses.append(f"({' OR '.join(status_conditions)})")
        
        # Add time filter
        if classification.parameters.time_range["start"] is not None:
            where_clauses.append(f"startdate >= '{classification.parameters.time_range['start']}'")
        if classification.parameters.time_range["end"] is not None:
            where_clauses.append(f"enddate <= '{classification.parameters.time_range['end']}'")
        
        # Combine WHERE clauses
        if where_clauses:
            sql += f" WHERE {' AND '.join(where_clauses)}"
        
        # Add ORDER BY clause
        sql += " ORDER BY projectname"
        
        return sql
    
    def generate_explanation_from_classification(self, classification: QueryClassification) -> str:
        """
        Generate a natural language explanation of the query classification
        
        Args:
            classification: The query classification result
            
        Returns:
            Explanation string
        """
        explanation = f"I understood your query as asking about "
        
        if classification.query_type == QueryType.DISTRICT:
            districts = ", ".join(classification.parameters.districts)
            explanation += f"projects in the {districts} district."
        
        elif classification.query_type == QueryType.SECTOR:
            sectors = ", ".join(classification.parameters.sectors)
            explanation += f"projects in the {sectors} sector."
        
        elif classification.query_type == QueryType.PROJECT:
            projects = ", ".join(classification.parameters.projects)
            explanation += f"the specific project: {projects}."
        
        elif classification.query_type == QueryType.BUDGET:
            if classification.parameters.budget_range["min"] is not None and classification.parameters.budget_range["max"] is not None:
                explanation += f"projects with budget between MWK {classification.parameters.budget_range['min']} and MWK {classification.parameters.budget_range['max']}."
            elif classification.parameters.budget_range["min"] is not None:
                explanation += f"projects with budget greater than MWK {classification.parameters.budget_range['min']}."
            elif classification.parameters.budget_range["max"] is not None:
                explanation += f"projects with budget less than MWK {classification.parameters.budget_range['max']}."
        
        elif classification.query_type == QueryType.STATUS:
            statuses = ", ".join(classification.parameters.status)
            explanation += f"projects with status: {statuses}."
        
        elif classification.query_type == QueryType.TIME:
            if classification.parameters.time_range["start"] is not None and classification.parameters.time_range["end"] is not None:
                explanation += f"projects between {classification.parameters.time_range['start']} and {classification.parameters.time_range['end']}."
            elif classification.parameters.time_range["start"] is not None:
                explanation += f"projects after {classification.parameters.time_range['start']}."
            elif classification.parameters.time_range["end"] is not None:
                explanation += f"projects before {classification.parameters.time_range['end']}."
        
        elif classification.query_type == QueryType.COMBINED:
            parts = []
            
            if classification.parameters.districts:
                districts = ", ".join(classification.parameters.districts)
                parts.append(f"in the {districts} district")
            
            if classification.parameters.sectors:
                sectors = ", ".join(classification.parameters.sectors)
                parts.append(f"in the {sectors} sector")
            
            if classification.parameters.projects:
                projects = ", ".join(classification.parameters.projects)
                parts.append(f"related to '{projects}'")
            
            if classification.parameters.budget_range["min"] is not None and classification.parameters.budget_range["max"] is not None:
                parts.append(f"with budget between MWK {classification.parameters.budget_range['min']} and MWK {classification.parameters.budget_range['max']}")
            elif classification.parameters.budget_range["min"] is not None:
                parts.append(f"with budget greater than MWK {classification.parameters.budget_range['min']}")
            elif classification.parameters.budget_range["max"] is not None:
                parts.append(f"with budget less than MWK {classification.parameters.budget_range['max']}")
            
            if classification.parameters.status:
                statuses = ", ".join(classification.parameters.status)
                parts.append(f"with status: {statuses}")
            
            if classification.parameters.time_range["start"] is not None and classification.parameters.time_range["end"] is not None:
                parts.append(f"between {classification.parameters.time_range['start']} and {classification.parameters.time_range['end']}")
            elif classification.parameters.time_range["start"] is not None:
                parts.append(f"after {classification.parameters.time_range['start']}")
            elif classification.parameters.time_range["end"] is not None:
                parts.append(f"before {classification.parameters.time_range['end']}")
            
            explanation += f"projects {' and '.join(parts)}."
        
        else:  # UNKNOWN
            explanation = "I'm not sure what you're asking about. Could you please rephrase your question?"
        
        return explanation
