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
        logger.info("Initialized Hybrid Classifier")
        
        # Compile regex patterns for efficiency
        self._compile_patterns()
    
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
            re.compile(r'(?:what are|show me) the projects (?:in|at) (\w+)(?: district)?', re.IGNORECASE)
        ]
        
        # Sector patterns
        self.sector_patterns = [
            re.compile(r'(?:health sector|healthcare|health projects)', re.IGNORECASE),
            re.compile(r'(?:education|school|learning) (?:sector|projects|initiatives)', re.IGNORECASE),
            re.compile(r'(?:water|sanitation) (?:sector|projects|initiatives)', re.IGNORECASE),
            re.compile(r'(?:transport|road|infrastructure) (?:sector|projects|initiatives)', re.IGNORECASE),
            re.compile(r'(?:agriculture|farming|crop) (?:sector|projects|initiatives)', re.IGNORECASE)
        ]
        
        # Budget patterns
        self.budget_patterns = [
            re.compile(r'budget (?:of|for|is) (?:more than|over|above) (?:MWK|K)?(\d[\d,.]*)', re.IGNORECASE),
            re.compile(r'budget (?:of|for|is) (?:less than|under|below) (?:MWK|K)?(\d[\d,.]*)', re.IGNORECASE),
            re.compile(r'budget (?:between|from) (?:MWK|K)?(\d[\d,.]*) (?:and|to) (?:MWK|K)?(\d[\d,.]*)', re.IGNORECASE),
            re.compile(r'(?:projects|initiatives) (?:costing|worth|valued at) (?:more than|over|above) (?:MWK|K)?(\d[\d,.]*)', re.IGNORECASE),
            re.compile(r'(?:projects|initiatives) (?:costing|worth|valued at) (?:less than|under|below) (?:MWK|K)?(\d[\d,.]*)', re.IGNORECASE)
        ]
        
        # Status patterns
        self.status_patterns = [
            re.compile(r'(?:completed|finished|done) projects', re.IGNORECASE),
            re.compile(r'(?:ongoing|current|in progress|active) projects', re.IGNORECASE),
            re.compile(r'(?:planned|future|upcoming|proposed) projects', re.IGNORECASE),
            re.compile(r'projects (?:that are|which are) (?:completed|ongoing|planned|in progress)', re.IGNORECASE)
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
        
        # Check for health sector
        if re.search(r'(?:health sector|healthcare|health projects)', query.lower()):
            sectors.append("health")
        
        # Check for education sector
        if re.search(r'(?:education|school|learning) (?:sector|projects|initiatives)', query.lower()):
            sectors.append("education")
        
        # Check for water sector
        if re.search(r'(?:water|sanitation) (?:sector|projects|initiatives)', query.lower()):
            sectors.append("water")
        
        # Check for transport sector
        if re.search(r'(?:transport|road|infrastructure) (?:sector|projects|initiatives)', query.lower()):
            sectors.append("transport")
        
        # Check for agriculture sector
        if re.search(r'(?:agriculture|farming|crop) (?:sector|projects|initiatives)', query.lower()):
            sectors.append("agriculture")
        
        # Return with confidence based on number of sectors found
        if sectors:
            return sectors, 0.8
        
        return [], 0.0
    
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
        
        # Check for completed projects
        if re.search(r'(?:completed|finished|done) projects', query.lower()) or \
           re.search(r'projects (?:that are|which are) (?:completed|finished|done)', query.lower()):
            statuses.append("completed")
        
        # Check for ongoing projects
        if re.search(r'(?:ongoing|current|in progress|active) projects', query.lower()) or \
           re.search(r'projects (?:that are|which are) (?:ongoing|in progress|active)', query.lower()):
            statuses.append("ongoing")
        
        # Check for planned projects
        if re.search(r'(?:planned|future|upcoming|proposed) projects', query.lower()) or \
           re.search(r'projects (?:that are|which are) (?:planned|proposed)', query.lower()):
            statuses.append("planned")
        
        # Return with confidence based on number of statuses found
        if statuses:
            return statuses, 0.8
        
        return [], 0.0
    
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
        Classify query using regex patterns
        
        Returns:
            QueryClassification with highest confidence match
        """
        start_time = time.time()
        
        # Initialize parameters
        parameters = QueryParameters()
        confidence = 0.0
        query_type = QueryType.UNKNOWN
        
        # Try district classification first (most specific)
        districts, district_confidence = self._regex_classify_district(query)
        if districts and district_confidence > 0.7:  # Lower threshold for district queries
            parameters.districts = districts
            confidence = district_confidence
            query_type = QueryType.DISTRICT
            return QueryClassification(
                query_type=query_type,
                parameters=parameters,
                confidence=confidence,
                original_query=query,
                processing_time=time.time() - start_time
            )
        
        # Try project classification next
        projects, proj_conf = self._regex_classify_project(query)
        if projects and proj_conf > 0.8:
            parameters.projects = projects
            confidence = proj_conf
            query_type = QueryType.PROJECT
            return QueryClassification(
                query_type=query_type,
                parameters=parameters,
                confidence=confidence,
                original_query=query,
                processing_time=time.time() - start_time
            )
        
        # Continue with other classifications
        sectors, sector_confidence = self._regex_classify_sector(query)
        budget_range, budget_confidence = self._regex_classify_budget(query)
        statuses, status_confidence = self._regex_classify_status(query)
        time_range, time_confidence = self._regex_classify_time(query)
        
        # Update parameters with regex results
        parameters.districts = districts
        parameters.sectors = sectors
        parameters.budget_range = budget_range
        parameters.status = statuses
        parameters.time_range = time_range
        
        # Determine query type and confidence
        confidences = {
            QueryType.DISTRICT: district_confidence if districts else 0.0,
            QueryType.SECTOR: sector_confidence if sectors else 0.0,
            QueryType.BUDGET: budget_confidence if (budget_range["min"] is not None or budget_range["max"] is not None) else 0.0,
            QueryType.STATUS: status_confidence if statuses else 0.0,
            QueryType.TIME: time_confidence if (time_range["start"] is not None or time_range["end"] is not None) else 0.0
        }
        
        # Count non-empty parameter types
        non_empty_param_types = sum(1 for conf in confidences.values() if conf > 0.0)
        
        # Determine query type
        if non_empty_param_types > 1:
            query_type = QueryType.COMBINED
            confidence = sum(confidences.values()) / non_empty_param_types
        elif non_empty_param_types == 1:
            # Get the query type with the highest confidence
            query_type = max(confidences.items(), key=lambda x: x[1])[0]
            confidence = confidences[query_type]
        else:
            # If no specific type is found, check if it's a general query
            if any(word in query.lower() for word in ['projects', 'list', 'show', 'find', 'what', 'which']):
                query_type = QueryType.GENERAL
                confidence = 0.6
            else:
                query_type = QueryType.UNKNOWN
                confidence = 0.0
        
        # Create classification result
        classification = QueryClassification(
            query_type=query_type,
            parameters=parameters,
            confidence=confidence,
            original_query=query,
            processing_time=time.time() - start_time
        )
        
        return classification
    
    def _merge_classifications(self, regex_class: QueryClassification, llm_class: QueryClassification) -> QueryClassification:
        """
        Merge regex and LLM classifications intelligently
        
        Args:
            regex_class: Classification from regex patterns
            llm_class: Classification from LLM
            
        Returns:
            Merged QueryClassification
        """
        # If regex has high confidence and LLM has low confidence, prefer regex
        if regex_class.confidence > 0.8 and llm_class.confidence < 0.6:
            return regex_class
            
        # If LLM has high confidence and regex has low confidence, prefer LLM
        if llm_class.confidence > 0.8 and regex_class.confidence < 0.6:
            return llm_class
            
        # For medium confidence cases, merge the parameters
        merged_params = QueryParameters()
        
        # Merge districts
        merged_params.districts = list(set(regex_class.parameters.districts + llm_class.parameters.districts))
        
        # Merge projects
        merged_params.projects = list(set(regex_class.parameters.projects + llm_class.parameters.projects))
        
        # Merge sectors
        merged_params.sectors = list(set(regex_class.parameters.sectors + llm_class.parameters.sectors))
        
        # Merge budget ranges - take the more specific one
        if regex_class.parameters.budget_range["min"] is not None or regex_class.parameters.budget_range["max"] is not None:
            merged_params.budget_range = regex_class.parameters.budget_range
        else:
            merged_params.budget_range = llm_class.parameters.budget_range
            
        # Merge statuses
        merged_params.status = list(set(regex_class.parameters.status + llm_class.parameters.status))
        
        # Merge time ranges - take the more specific one
        if regex_class.parameters.time_range["start"] is not None or regex_class.parameters.time_range["end"] is not None:
            merged_params.time_range = regex_class.parameters.time_range
        else:
            merged_params.time_range = llm_class.parameters.time_range
            
        # Determine merged query type
        if regex_class.query_type == llm_class.query_type:
            query_type = regex_class.query_type
        elif regex_class.query_type == QueryType.COMBINED or llm_class.query_type == QueryType.COMBINED:
            query_type = QueryType.COMBINED
        else:
            # Count non-empty parameters for each type
            regex_params = sum(1 for p in regex_class.parameters.dict().values() if p)
            llm_params = sum(1 for p in llm_class.parameters.dict().values() if p)
            query_type = regex_class.query_type if regex_params > llm_params else llm_class.query_type
            
        # Calculate merged confidence
        merged_confidence = (regex_class.confidence + llm_class.confidence) / 2
        
        # Create merged classification
        return QueryClassification(
            query_type=query_type,
            parameters=merged_params,
            confidence=merged_confidence,
            original_query=regex_class.original_query,
            processing_time=regex_class.processing_time + llm_class.processing_time
        )
    
    async def classify_query(self, query: str, use_llm: bool = True) -> QueryClassification:
        """
        Classify a natural language query using the hybrid approach
        
        Args:
            query: The natural language query to classify
            use_llm: Whether to use LLM for classification (if False, only use regex)
            
        Returns:
            QueryClassification object with query type and parameters
        """
        # First, try regex classification (fast)
        regex_classification = self._regex_classify(query)
        
        # If regex classification has high confidence or LLM is disabled, return it
        if regex_classification.confidence > 0.8 or not use_llm:
            return regex_classification
        
        # Otherwise, also try LLM classification
        llm_classification = await self.llm_classifier.classify_query(query)
        
        # Merge the classifications
        return self._merge_classifications(regex_classification, llm_classification)
