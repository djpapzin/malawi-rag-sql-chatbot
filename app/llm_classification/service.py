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

DISTRICT_CLASSIFICATION_PROMPT = """
When analyzing queries about districts in Malawi:

1. Location Recognition:
   - Treat standalone capitalized words as potential district names
   - Consider both explicit ("Dowa district") and implicit ("in Dowa") references
   - Handle variations in district name formatting

2. Query Types:
   - Direct questions: "Which projects are in Dowa?"
   - Commands: "Show Dowa developments"
   - Status queries: "What's happening in Dowa?"
   - Activity focused: "Current works in Dowa"

3. Contextual Terms:
   - Projects, developments, works, initiatives, activities
   - Infrastructure, construction, rehabilitation
   - Current, ongoing, planned, completed

4. Response Format:
   - Always include district name in the response
   - List matching projects with their details
   - Sort by relevance or budget as appropriate

Example Variations:
- "Which projects are in Dowa?"
- "Show me Dowa developments"
- "List projects from Dowa district"
- "What's happening in Dowa?"
- "Dowa infrastructure initiatives"
"""

class QueryClassificationService:
    """
    Service to handle query classification and integration with existing codebase
    """
    
    def __init__(self):
        """Initialize the classification service"""
        self.classifier = HybridClassifier()
        self.base_prompt = "Base prompt for classification"
        logger.info("Initialized Query Classification Service")
    
    async def classify_query(self, query: str) -> QueryClassification:
        """
        Enhanced query classification with improved district detection.
        """
        # Add the district classification prompt to the context
        context = f"{self.base_prompt}\n{DISTRICT_CLASSIFICATION_PROMPT}\n\nQuery: {query}"
        
        # Get district using enhanced fuzzy matching
        district = extract_district(query)
        
        # Adjust classification based on district presence
        if district:
            parameters = QueryParameters(
                districts=[district],
                projects=[],
                sectors=[],
                budget_range={"min": None, "max": None},
                status=[],
                time_range={"start": None, "end": None}
            )
            return QueryClassification(
                query_type=QueryType.DISTRICT,
                parameters=parameters,
                confidence=0.9 if "district" in query.lower() else 0.8,
                original_query=query,
                processing_time=0.0
            )
        
        # Continue with other classification logic
        result = await self.classifier.classify_query(query)
        return result
    
    def generate_sql_from_classification(self, classification: QueryClassification) -> str:
        """Generate SQL query based on classification"""
        # Base SQL query with all fields for specific queries
        if classification.parameters.projects:
            sql = """
            SELECT 
                projectname as project_name,
                projectcode as project_code,
                projectsector as project_sector,
                projectstatus as status,
                stage,
                region,
                district as location,
                traditionalauthority,
                budget as total_budget,
                TOTALEXPENDITUREYEAR as total_expenditure,
                fundingsource as funding_source,
                startdate as start_date,
                completionestidate as completion_date,
                lastvisit as last_monitoring_visit,
                completionpercentage as completion_progress,
                contractorname as contractor,
                signingdate as contract_signing_date,
                projectdesc as description,
                fiscalyear as fiscal_year
            FROM 
                proj_dashboard
            """
        else:
            # Use basic fields for general queries
            sql = """
            SELECT 
                projectname as project_name,
                fiscalyear as fiscal_year,
                district as location,
                budget as total_budget,
                projectstatus as status,
                projectsector as project_sector
            FROM 
                proj_dashboard
            """
        
        # List to collect WHERE clauses
        where_clauses = []
        
        # Add district filter
        if classification.parameters.districts and not any(d.lower() == 'the' for d in classification.parameters.districts):
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
                status_conditions.append(f"LOWER(projectstatus) LIKE '%{status.lower()}%'")
            where_clauses.append(f"({' OR '.join(status_conditions)})")
        
        # Add time range filter
        if classification.parameters.time_range["start"] is not None:
            where_clauses.append(f"startdate >= '{classification.parameters.time_range['start']}'")
        if classification.parameters.time_range["end"] is not None:
            where_clauses.append(f"completionestidate <= '{classification.parameters.time_range['end']}'")
        
        # Combine WHERE clauses
        if where_clauses:
            sql += "\nWHERE " + " AND ".join(where_clauses)
        
        # Add ORDER BY clause
        if classification.parameters.projects:
            # For specific project queries, prioritize exact matches
            sql += """
            ORDER BY 
                CASE 
                    WHEN LOWER(projectname) = LOWER(?) THEN 1
                    WHEN LOWER(projectname) LIKE LOWER(?) THEN 2
                    ELSE 3
                END,
                budget DESC
            LIMIT 1
            """
        else:
            # For general queries, sort by budget and status
            sql += """
            ORDER BY 
                budget DESC,
                CASE 
                    WHEN LOWER(projectstatus) LIKE '%ongoing%' THEN 1
                    WHEN LOWER(projectstatus) LIKE '%completed%' THEN 2
                    ELSE 3
                END
            LIMIT 10
            """
        
        return sql
    
    def generate_explanation_from_classification(self, classification: QueryClassification, total_results: int = 0) -> str:
        """
        Generate a natural language explanation of the query classification
        
        Args:
            classification: The query classification result
            total_results: Total number of results found
            
        Returns:
            Explanation string
        """
        explanation = f"I understood your query as asking about "
        
        if classification.query_type == QueryType.DISTRICT:
            districts = [d for d in classification.parameters.districts if d.lower() != 'the']
            if districts:
                explanation += f"projects in the {', '.join(districts)} district."
            else:
                explanation += "projects in a specific district, but I couldn't determine which district."
        
        elif classification.query_type == QueryType.SECTOR:
            sectors = classification.parameters.sectors
            if len(sectors) == 1:
                sector = sectors[0]
                if sector.lower() == "health":
                    explanation += "projects in the health sector (including hospitals and medical facilities)."
                elif sector.lower() == "education":
                    explanation += "projects in the education sector (including schools and learning facilities)."
                elif sector.lower() == "water":
                    explanation += "projects in the water sector (including water and sanitation)."
                elif sector.lower() == "transport":
                    explanation += "projects in the transport sector (including roads and infrastructure)."
                elif sector.lower() == "agriculture":
                    explanation += "projects in the agriculture sector (including farming and crops)."
                else:
                    explanation += f"projects in the {sector} sector."
            else:
                explanation += f"projects in the following sectors: {', '.join(sectors)}."
        
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
            
            districts = [d for d in classification.parameters.districts if d.lower() != 'the']
            if districts:
                parts.append(f"in the {', '.join(districts)} district")
            
            if classification.parameters.sectors:
                sectors = classification.parameters.sectors
                if len(sectors) == 1:
                    sector = sectors[0]
                    if sector.lower() == "health":
                        parts.append("in the health sector (including hospitals and medical facilities)")
                    elif sector.lower() == "education":
                        parts.append("in the education sector (including schools and learning facilities)")
                    elif sector.lower() == "water":
                        parts.append("in the water sector (including water and sanitation)")
                    elif sector.lower() == "transport":
                        parts.append("in the transport sector (including roads and infrastructure)")
                    elif sector.lower() == "agriculture":
                        parts.append("in the agriculture sector (including farming and crops)")
                    else:
                        parts.append(f"in the {sector} sector")
                else:
                    parts.append(f"in the following sectors: {', '.join(sectors)}")
            
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

        # Add result count information in the requested format
        if total_results > 0:
            if total_results > 10:
                explanation = explanation.rstrip('.') + f". I have found {total_results} projects, showing the first 10."
            else:
                explanation = explanation.rstrip('.') + f". I have found {total_results} projects."
        elif total_results == 0:
            explanation = explanation.rstrip('.') + ". No projects found."
        
        return explanation

def extract_district(query: str) -> str:
    """Extract district name from query using regex patterns and fuzzy matching"""
    from .classifier import LLMClassifier
    
    classifier = LLMClassifier()
    return classifier.extract_district(query)
