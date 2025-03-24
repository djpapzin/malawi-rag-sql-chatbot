"""
Hybrid Query Classification Module

This module combines regex-based and LLM-based classification approaches
for optimal query understanding.
"""

import logging
import re
import time
from typing import Dict, Any, List, Optional, Tuple, Union
import asyncio

from .classifier import LLMClassifier, QueryClassification, QueryType, QueryParameters
from ..services.llm_service import LLMService

logger = logging.getLogger(__name__)

class HybridClassifier:
    """
    Hybrid classifier that combines regex and LLM approaches
    
    Strategy:
    1. Try regex patterns first for fast classification of common queries
    2. If regex fails or has low confidence, use LLM for more complex queries
    3. Combine results if both methods provide partial matches
    """
    
    def __init__(self):
        """Initialize the hybrid classifier"""
        self.llm_classifier = LLMClassifier()
        self.llm_service = LLMService()
        self.logger = logging.getLogger(__name__)
        
        # Compile regex patterns for efficiency
        self._compile_patterns()
        
        # Patterns for unrelated queries
        self.unrelated_patterns = [
            # Single words that aren't project-related
            r'^[a-zA-Z]{1,4}$',  # Single short words
            
            # Common unrelated words/phrases
            r'^(?:cat|dog|food|weather|time|date|hello|hi|hey|thanks|thank you|bye|goodbye)$',
            
            # Questions not about projects
            r'^(?:what|who|where|when|why|how)\s+(?:is|are|do|does|did)\s+(?!.*project).*$',
            
            # Statements not about projects
            r'^(?!.*(?:project|construction|building|infrastructure))(?:[a-zA-Z\s]{1,20})$'
        ]
    
    def _compile_patterns(self):
        """Compile regex patterns for different query types"""
        # Project patterns (add these first)
        self.project_patterns = [
            re.compile(r'(?:tell|show|give) (?:me|us) (?:about|details of|information about) (?:the )?([\w\s-]+?)(?:\s+project)?\s*(?:$|[?.])', re.IGNORECASE),
            re.compile(r'(?:what|how) (?:is|about) (?:the )?([\w\s-]+?)(?:\s+project)?\s*(?:$|[?.])', re.IGNORECASE),
            re.compile(r'(?:details|information|status) (?:for|of) (?:the )?([\w\s-]+?)(?:\s+project)?\s*(?:$|[?.])', re.IGNORECASE),
            re.compile(r'(?:project|code) (?:code )?(MW-[A-Za-z]{2}-[A-Z0-9]{2})', re.IGNORECASE)
        ]
        
        # District patterns
        self.district_patterns = [
            # Basic patterns
            re.compile(r'(?:projects|list).* (?:in|located in|based in|for) (\w+)(?: district)?', re.IGNORECASE),
            re.compile(r'(\w+) (?:district|region).* projects', re.IGNORECASE),
            re.compile(r'show (?:me|all) projects.* (\w+)', re.IGNORECASE),
            re.compile(r'(?:what|which|any) projects (?:are|exist|located) (?:in|at) (\w+)', re.IGNORECASE),
            
            # Question-based patterns
            re.compile(r'(?:which|what) projects (?:are|exist|located) (?:in|at) (\w+)(?: district)?\s*[?]?', re.IGNORECASE),
            re.compile(r'(?:can you|please) (?:show|list|display) (?:me|all) projects (?:in|at) (\w+)(?: district)?', re.IGNORECASE),
            re.compile(r'(?:i want|need) to (?:see|find|get) projects (?:in|at) (\w+)(?: district)?', re.IGNORECASE),
            
            # Direct patterns
            re.compile(r'projects (?:in|at|located in|based in) (\w+)(?: district)?', re.IGNORECASE),
            re.compile(r'(?:list|show|display) projects (?:from|in|at) (\w+)(?: district)?', re.IGNORECASE),
            re.compile(r'(?:find|search for) projects (?:in|at) (\w+)(?: district)?', re.IGNORECASE),
            
            # Complex patterns
            re.compile(r'(?:tell|give) me (?:about|information about) projects (?:in|at) (\w+)(?: district)?', re.IGNORECASE),
            re.compile(r'(?:looking for|need information about) projects (?:in|at) (\w+)(?: district)?', re.IGNORECASE),
            re.compile(r'(?:what are|show me) the projects (?:in|at) (\w+)(?: district)?', re.IGNORECASE),
            
            # Combined patterns
            re.compile(r'(?:show|list|find) (?:me|all) (?:health|education|water|transport|agriculture) projects (?:in|at) (\w+)(?: district)?', re.IGNORECASE),
            re.compile(r'(?:health|education|water|transport|agriculture) projects (?:in|at) (\w+)(?: district)?', re.IGNORECASE),
            re.compile(r'(?:completed|ongoing|approved) (?:health|education|water|transport|agriculture) projects (?:in|at) (\w+)(?: district)?', re.IGNORECASE)
        ]
        
        # Sector patterns
        self.sector_patterns = [
            # Health sector
            re.compile(r'(?:health|healthcare|hospital|clinic|medical) (?:sector|projects|initiatives)?', re.IGNORECASE),
            re.compile(r'(?:show|list|find) (?:me|all) (?:health|healthcare|hospital|clinic|medical) (?:projects)?', re.IGNORECASE),
            re.compile(r'(?:health|healthcare|hospital|clinic|medical) projects (?:in|at) (\w+)(?: district)?', re.IGNORECASE),
            
            # Education sector
            re.compile(r'(?:education|school|university|college|learning) (?:sector|projects|initiatives)?', re.IGNORECASE),
            re.compile(r'(?:show|list|find) (?:me|all) (?:education|school|university|college|learning) (?:projects)?', re.IGNORECASE),
            re.compile(r'(?:education|school|university|college|learning) projects (?:in|at) (\w+)(?: district)?', re.IGNORECASE),
            
            # Water sector
            re.compile(r'(?:water|sanitation|irrigation|drainage) (?:sector|projects|initiatives)?', re.IGNORECASE),
            re.compile(r'(?:show|list|find) (?:me|all) (?:water|sanitation|irrigation|drainage) (?:projects)?', re.IGNORECASE),
            re.compile(r'(?:water|sanitation|irrigation|drainage) projects (?:in|at) (\w+)(?: district)?', re.IGNORECASE),
            
            # Transport sector
            re.compile(r'(?:transport|road|highway|bridge|infrastructure) (?:sector|projects|initiatives)?', re.IGNORECASE),
            re.compile(r'(?:show|list|find) (?:me|all) (?:transport|road|highway|bridge|infrastructure) (?:projects)?', re.IGNORECASE),
            re.compile(r'(?:transport|road|highway|bridge|infrastructure) projects (?:in|at) (\w+)(?: district)?', re.IGNORECASE),
            
            # Agriculture sector
            re.compile(r'(?:agriculture|farming|crop|livestock|food) (?:sector|projects|initiatives)?', re.IGNORECASE),
            re.compile(r'(?:show|list|find) (?:me|all) (?:agriculture|farming|crop|livestock|food) (?:projects)?', re.IGNORECASE),
            re.compile(r'(?:agriculture|farming|crop|livestock|food) projects (?:in|at) (\w+)(?: district)?', re.IGNORECASE),
            
            # Combined patterns
            re.compile(r'(?:show|list|find) (?:me|all) (?:health|education|water|transport|agriculture) projects (?:in|at) (\w+)(?: district)?', re.IGNORECASE),
            re.compile(r'(?:health|education|water|transport|agriculture) projects (?:in|at) (\w+)(?: district)?', re.IGNORECASE),
            re.compile(r'(?:completed|ongoing|approved) (?:health|education|water|transport|agriculture) projects (?:in|at) (\w+)(?: district)?', re.IGNORECASE)
        ]
        
        # Status patterns
        self.status_patterns = [
            # Completed status
            re.compile(r'(?:completed|finished|done|finalized) (?:projects|initiatives)?', re.IGNORECASE),
            re.compile(r'projects (?:that are|which are) (?:completed|finished|done|finalized)', re.IGNORECASE),
            re.compile(r'(?:completed|finished|done|finalized) (?:health|education|water|transport|agriculture) projects', re.IGNORECASE),
            
            # Ongoing status
            re.compile(r'(?:ongoing|current|in progress|active|running) (?:projects|initiatives)?', re.IGNORECASE),
            re.compile(r'projects (?:that are|which are) (?:ongoing|current|in progress|active|running)', re.IGNORECASE),
            re.compile(r'(?:ongoing|current|in progress|active|running) (?:health|education|water|transport|agriculture) projects', re.IGNORECASE),
            
            # Planned status
            re.compile(r'(?:planned|future|upcoming|proposed|approved) (?:projects|initiatives)?', re.IGNORECASE),
            re.compile(r'projects (?:that are|which are) (?:planned|future|upcoming|proposed|approved)', re.IGNORECASE),
            re.compile(r'(?:planned|future|upcoming|proposed|approved) (?:health|education|water|transport|agriculture) projects', re.IGNORECASE)
        ]
        
        # Budget patterns
        self.budget_patterns = [
            re.compile(r'budget (?:of|for|is) (?:more than|over|above) (?:MWK|K)?(\d[\d,.]*)', re.IGNORECASE),
            re.compile(r'budget (?:of|for|is) (?:less than|under|below) (?:MWK|K)?(\d[\d,.]*)', re.IGNORECASE),
            re.compile(r'budget (?:between|from) (?:MWK|K)?(\d[\d,.]*) (?:and|to) (?:MWK|K)?(\d[\d,.]*)', re.IGNORECASE),
            re.compile(r'(?:projects|initiatives) (?:costing|worth|valued at) (?:more than|over|above) (?:MWK|K)?(\d[\d,.]*)', re.IGNORECASE),
            re.compile(r'(?:projects|initiatives) (?:costing|worth|valued at) (?:less than|under|below) (?:MWK|K)?(\d[\d,.]*)', re.IGNORECASE)
        ]
        
        # Time patterns
        self.time_patterns = [
            re.compile(r'projects (?:in|from|during) (?:the year )?(\d{4})', re.IGNORECASE),
            re.compile(r'projects (?:between|from) (?:the years? )?(\d{4})(?:-| to | and )(\d{4})', re.IGNORECASE),
            re.compile(r'projects (?:after|since) (?:the year )?(\d{4})', re.IGNORECASE),
            re.compile(r'projects (?:before|until|up to) (?:the year )?(\d{4})', re.IGNORECASE)
        ]
    
    def _regex_classify_project(self, query: str) -> Tuple[List[str], float]:
        """
        Classify project queries using regex
        
        Returns:
            Tuple of (list of projects, confidence)
        """
        for pattern in self.project_patterns:
            match = pattern.search(query)
            if match:
                project = match.group(1).strip()
                # If it's a project code, ensure proper format
                if re.match(r'(?:MW-)?[A-Za-z]{2}-[A-Z0-9]{2}', project, re.IGNORECASE):
                    if not project.upper().startswith('MW-'):
                        project = f"MW-{project.upper()}"
                    return [project], 0.9
                return [project], 0.8
        
        return [], 0.0
    
    def _regex_classify_district(self, query: str) -> Tuple[List[str], float]:
        """
        Classify district queries using regex
        
        Returns:
            Tuple of (list of districts, confidence)
        """
        best_match = None
        best_confidence = 0.0
        
        for pattern in self.district_patterns:
            match = pattern.search(query)
            if match:
                # Extract the district name and clean it
                district = match.group(1).strip()
                
                # Handle multi-word districts
                if ' ' in district:
                    # If it's a multi-word district, we need to capture all words
                    district = ' '.join(word.title() for word in district.split())
                else:
                    district = district.title()
                
                # Calculate confidence based on pattern match quality
                confidence = 0.8  # Base confidence
                
                # Increase confidence for more specific patterns
                if 'district' in query.lower():
                    confidence += 0.1
                if 'show me all' in query.lower():
                    confidence += 0.1
                if 'projects' in query.lower():
                    confidence += 0.05
                
                # Increase confidence for combined queries
                if any(term in query.lower() for term in ["health", "education", "water", "transport", "agriculture"]):
                    confidence += 0.1
                if any(term in query.lower() for term in ["sector", "projects"]):
                    confidence += 0.05
                
                # Update best match if this one has higher confidence
                if confidence > best_confidence:
                    best_match = district
                    best_confidence = confidence
        
        if best_match:
            return [best_match], min(best_confidence, 1.0)  # Cap confidence at 1.0
        
        return [], 0.0
    
    def _regex_classify_sector(self, query: str) -> Tuple[List[str], float]:
        """
        Classify sector queries using regex
        
        Returns:
            Tuple of (list of sectors, confidence)
        """
        sectors = []
        confidence = 0.0
        
        # Check each sector pattern
        for pattern in self.sector_patterns:
            match = pattern.search(query)
            if match:
                # Extract the sector from the matched text
                matched_text = match.group(0).lower()
                
                # Map matched text to sector
                if any(term in matched_text for term in ["health", "healthcare", "hospital", "clinic", "medical"]):
                    sectors.append("health")
                    confidence = max(confidence, 0.8)
                elif any(term in matched_text for term in ["education", "school", "university", "college", "learning"]):
                    sectors.append("education")
                    confidence = max(confidence, 0.8)
                elif any(term in matched_text for term in ["water", "sanitation", "irrigation", "drainage"]):
                    sectors.append("water")
                    confidence = max(confidence, 0.8)
                elif any(term in matched_text for term in ["transport", "road", "highway", "bridge", "infrastructure"]):
                    sectors.append("transport")
                    confidence = max(confidence, 0.8)
                elif any(term in matched_text for term in ["agriculture", "farming", "crop", "livestock", "food"]):
                    sectors.append("agriculture")
                    confidence = max(confidence, 0.8)
                
                # Increase confidence for combined queries
                if "in" in matched_text or "at" in matched_text:
                    confidence = min(confidence + 0.1, 1.0)
                if "district" in matched_text:
                    confidence = min(confidence + 0.1, 1.0)
        
        # Remove duplicates while preserving order
        sectors = list(dict.fromkeys(sectors))
        
        return sectors, confidence
    
    def _regex_classify_budget(self, query: str) -> Tuple[Dict[str, Optional[float]], float]:
        """
        Classify budget queries using regex
        
        Returns:
            Tuple of (budget range dict, confidence)
        """
        budget_range = {"min": None, "max": None}
        
        # Check for "more than" pattern
        match = re.search(r'(?:more than|over|above) (?:MWK|K)?(\d[\d,.]*)', query.lower())
        if match:
            try:
                value = float(match.group(1).replace(',', ''))
                budget_range["min"] = value
                return budget_range, 0.8
            except ValueError:
                pass
        
        # Check for "less than" pattern
        match = re.search(r'(?:less than|under|below) (?:MWK|K)?(\d[\d,.]*)', query.lower())
        if match:
            try:
                value = float(match.group(1).replace(',', ''))
                budget_range["max"] = value
                return budget_range, 0.8
            except ValueError:
                pass
        
        # Check for "between" pattern
        match = re.search(r'(?:between|from) (?:MWK|K)?(\d[\d,.]*) (?:and|to) (?:MWK|K)?(\d[\d,.]*)', query.lower())
        if match:
            try:
                min_value = float(match.group(1).replace(',', ''))
                max_value = float(match.group(2).replace(',', ''))
                budget_range["min"] = min_value
                budget_range["max"] = max_value
                return budget_range, 0.9
            except ValueError:
                pass
        
        return budget_range, 0.0
    
    def _regex_classify_status(self, query: str) -> Tuple[List[str], float]:
        """
        Classify status queries using regex
        
        Returns:
            Tuple of (list of statuses, confidence)
        """
        statuses = []
        confidence = 0.0
        
        # Check each status pattern
        for pattern in self.status_patterns:
            match = pattern.search(query)
            if match:
                # Extract the status from the matched text
                matched_text = match.group(0).lower()
                
                # Map matched text to status
                if any(term in matched_text for term in ["completed", "finished", "done", "finalized"]):
                    statuses.append("completed")
                    confidence = max(confidence, 0.8)
                elif any(term in matched_text for term in ["ongoing", "current", "in progress", "active", "running"]):
                    statuses.append("ongoing")
                    confidence = max(confidence, 0.8)
                elif any(term in matched_text for term in ["planned", "future", "upcoming", "proposed", "approved"]):
                    statuses.append("approved")
                    confidence = max(confidence, 0.8)
        
        # Remove duplicates while preserving order
        statuses = list(dict.fromkeys(statuses))
        
        return statuses, confidence
    
    def _regex_classify_time(self, query: str) -> Tuple[Dict[str, Optional[str]], float]:
        """
        Classify time queries using regex
        
        Returns:
            Tuple of (time range dict, confidence)
        """
        time_range = {"start": None, "end": None}
        
        # Check for specific year
        match = re.search(r'(?:in|from|during) (?:the year )?(\d{4})', query.lower())
        if match:
            year = match.group(1)
            time_range["start"] = f"{year}-01-01"
            time_range["end"] = f"{year}-12-31"
            return time_range, 0.8
        
        # Check for year range
        match = re.search(r'(?:between|from) (?:the years? )?(\d{4})(?:-| to | and )(\d{4})', query.lower())
        if match:
            start_year = match.group(1)
            end_year = match.group(2)
            time_range["start"] = f"{start_year}-01-01"
            time_range["end"] = f"{end_year}-12-31"
            return time_range, 0.9
        
        # Check for "after" year
        match = re.search(r'(?:after|since) (?:the year )?(\d{4})', query.lower())
        if match:
            year = match.group(1)
            time_range["start"] = f"{year}-01-01"
            return time_range, 0.8
        
        # Check for "before" year
        match = re.search(r'(?:before|until|up to) (?:the year )?(\d{4})', query.lower())
        if match:
            year = match.group(1)
            time_range["end"] = f"{year}-12-31"
            return time_range, 0.8
        
        return time_range, 0.0
    
    def _regex_classify(self, query: str) -> QueryClassification:
        """
        Classify a query using regex patterns
        
        Args:
            query: The query to classify
            
        Returns:
            QueryClassification object
        """
        # Initialize classification
        classification = QueryClassification(
            query_type=QueryType.GENERAL,
            confidence=0.0,
            parameters=QueryParameters()
        )
        
        # Try project classification first
        projects, project_confidence = self._regex_classify_project(query)
        if projects:
            classification.parameters.projects = projects
            classification.query_type = QueryType.PROJECT
            classification.confidence = project_confidence
            return classification
        
        # Try district classification
        districts, district_confidence = self._regex_classify_district(query)
        if districts:
            classification.parameters.districts = districts
            classification.query_type = QueryType.DISTRICT
            classification.confidence = district_confidence
        
        # Try sector classification
        sectors, sector_confidence = self._regex_classify_sector(query)
        if sectors:
            classification.parameters.sectors = sectors
            # If we already have districts, this is a combined query
            if classification.parameters.districts:
                classification.query_type = QueryType.COMBINED
                classification.confidence = max(district_confidence, sector_confidence)
            else:
                classification.query_type = QueryType.SECTOR
                classification.confidence = sector_confidence
        
        # Try status classification
        status, status_confidence = self._regex_classify_status(query)
        if status:
            classification.parameters.status = status
            # If we already have districts or sectors, this is a combined query
            if classification.parameters.districts or classification.parameters.sectors:
                classification.query_type = QueryType.COMBINED
                classification.confidence = max(
                    classification.confidence,
                    status_confidence
                )
            else:
                classification.query_type = QueryType.STATUS
                classification.confidence = status_confidence
        
        # Try budget classification
        budget, budget_confidence = self._regex_classify_budget(query)
        if budget["min"] is not None or budget["max"] is not None:
            classification.parameters.budget_range = budget
            # If we already have other parameters, this is a combined query
            if classification.parameters.districts or classification.parameters.sectors or classification.parameters.status:
                classification.query_type = QueryType.COMBINED
                classification.confidence = max(
                    classification.confidence,
                    budget_confidence
                )
            else:
                classification.query_type = QueryType.BUDGET
                classification.confidence = budget_confidence
        
        # Try time classification
        time_range, time_confidence = self._regex_classify_time(query)
        if time_range["start"] is not None or time_range["end"] is not None:
            classification.parameters.time_range = time_range
            # If we already have other parameters, this is a combined query
            if (classification.parameters.districts or 
                classification.parameters.sectors or 
                classification.parameters.status or 
                classification.parameters.budget_range["min"] is not None or 
                classification.parameters.budget_range["max"] is not None):
                classification.query_type = QueryType.COMBINED
                classification.confidence = max(
                    classification.confidence,
                    time_confidence
                )
            else:
                classification.query_type = QueryType.TIME
                classification.confidence = time_confidence
        
        # Update confidence based on number of parameters
        param_count = (
            len(classification.parameters.districts) +
            len(classification.parameters.sectors) +
            len(classification.parameters.status) +
            (1 if classification.parameters.budget_range["min"] is not None or 
                 classification.parameters.budget_range["max"] is not None else 0) +
            (1 if classification.parameters.time_range["start"] is not None or 
                 classification.parameters.time_range["end"] is not None else 0)
        )
        
        if param_count > 0:
            classification.confidence = min(classification.confidence + (param_count * 0.1), 1.0)
        
        return classification
    
    async def classify_query(self, query: str, use_llm: bool = True) -> QueryClassification:
        """
        Classify a query using both regex and LLM approaches
        
        Args:
            query: The query to classify
            use_llm: Whether to use LLM classification
            
        Returns:
            QueryClassification object
        """
        # First check if it's an unrelated query
        for pattern in self.unrelated_patterns:
            if re.match(pattern, query):
                self.logger.info(f"Query '{query}' matched unrelated pattern: {pattern}")
                return QueryClassification(
                    query_type=QueryType.UNRELATED,
                    confidence=0.95,
                    parameters=QueryParameters()
                )
        
        # First try regex classification
        regex_class = self._regex_classify(query)
        
        # If regex classification is complete and confident, return it
        if regex_class.query_type != QueryType.GENERAL and regex_class.confidence >= 0.8:
            return regex_class
        
        # If LLM is disabled or regex is confident enough, return regex result
        if not use_llm or regex_class.confidence >= 0.6:
            return regex_class
        
        # Get LLM classification
        llm_class = await self.llm_classifier.classify_query(query)
        
        # Merge the results
        return self._merge_classifications(regex_class, llm_class)
    
    def _merge_classifications(self, regex_class: QueryClassification, llm_class: QueryClassification) -> QueryClassification:
        """
        Merge regex and LLM classifications
        
        Args:
            regex_class: Regex classification result
            llm_class: LLM classification result
            
        Returns:
            Merged QueryClassification object
        """
        # Initialize merged result
        merged = QueryClassification(
            query_type=QueryType.GENERAL,
            confidence=0.0,
            parameters=QueryParameters()
        )
        
        # Determine query type
        if regex_class.query_type != QueryType.GENERAL and llm_class.query_type != QueryType.GENERAL:
            merged.query_type = QueryType.COMBINED
            merged.confidence = max(regex_class.confidence, llm_class.confidence)
        else:
            merged.query_type = regex_class.query_type if regex_class.query_type != QueryType.GENERAL else llm_class.query_type
            merged.confidence = max(regex_class.confidence, llm_class.confidence)
        
        # Merge parameters
        merged.parameters.districts = list(set(regex_class.parameters.districts + llm_class.parameters.districts))
        merged.parameters.sectors = list(set(regex_class.parameters.sectors + llm_class.parameters.sectors))
        merged.parameters.status = list(set(regex_class.parameters.status + llm_class.parameters.status))
        merged.parameters.budget = regex_class.parameters.budget if regex_class.parameters.budget else llm_class.parameters.budget
        merged.parameters.time = regex_class.parameters.time if regex_class.parameters.time else llm_class.parameters.time
        
        # Update confidence based on number of parameters
        param_count = len(merged.parameters.districts) + len(merged.parameters.sectors) + len(merged.parameters.status)
        if param_count > 0:
            merged.confidence = min(merged.confidence + (param_count * 0.1), 1.0)
        
        return merged
