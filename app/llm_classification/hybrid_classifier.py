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
        # District patterns
        self.district_patterns = [
            re.compile(r'(?:projects|list).* (?:in|located in|based in|for) (\w+)(?: district)?', re.IGNORECASE),
            re.compile(r'(\w+) (?:district|region).* projects', re.IGNORECASE),
            re.compile(r'show (?:me|all) projects.* (\w+)', re.IGNORECASE),
            re.compile(r'(?:what|which|any) projects (?:are|exist|located) (?:in|at) (\w+)', re.IGNORECASE)
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
    
    def _regex_classify_district(self, query: str) -> Tuple[List[str], float]:
        """
        Classify district queries using regex
        
        Returns:
            Tuple of (list of districts, confidence)
        """
        for pattern in self.district_patterns:
            match = pattern.search(query)
            if match:
                district = match.group(1).strip().title()
                return [district], 0.8
        
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
        Classify a query using regex patterns
        
        Args:
            query: The natural language query to classify
            
        Returns:
            QueryClassification object with query type and parameters
        """
        start_time = time.time()
        
        # Initialize parameters
        parameters = QueryParameters()
        
        # Try to classify with each regex classifier
        districts, district_confidence = self._regex_classify_district(query)
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
    
    def _merge_classifications(self, regex_classification: QueryClassification, llm_classification: QueryClassification) -> QueryClassification:
        """
        Merge regex and LLM classification results
        
        Strategy:
        - Take the classification with higher confidence
        - For parameters, combine from both sources with preference to higher confidence source
        
        Args:
            regex_classification: Classification from regex
            llm_classification: Classification from LLM
            
        Returns:
            Merged QueryClassification
        """
        # Start with the classification that has higher confidence
        if regex_classification.confidence >= llm_classification.confidence:
            base_classification = regex_classification
            secondary_classification = llm_classification
        else:
            base_classification = llm_classification
            secondary_classification = regex_classification
        
        # Create a new merged classification
        merged = QueryClassification(
            query_type=base_classification.query_type,
            parameters=QueryParameters(),
            confidence=max(regex_classification.confidence, llm_classification.confidence),
            original_query=base_classification.original_query,
            llm_response=llm_classification.llm_response,
            processing_time=regex_classification.processing_time + llm_classification.processing_time
        )
        
        # Merge parameters with preference to base classification
        
        # Districts
        merged.parameters.districts = base_classification.parameters.districts.copy()
        for district in secondary_classification.parameters.districts:
            if district not in merged.parameters.districts:
                merged.parameters.districts.append(district)
        
        # Projects
        merged.parameters.projects = base_classification.parameters.projects.copy()
        for project in secondary_classification.parameters.projects:
            if project not in merged.parameters.projects:
                merged.parameters.projects.append(project)
        
        # Sectors
        merged.parameters.sectors = base_classification.parameters.sectors.copy()
        for sector in secondary_classification.parameters.sectors:
            if sector not in merged.parameters.sectors:
                merged.parameters.sectors.append(sector)
        
        # Budget range
        merged.parameters.budget_range = base_classification.parameters.budget_range.copy()
        if merged.parameters.budget_range["min"] is None and secondary_classification.parameters.budget_range["min"] is not None:
            merged.parameters.budget_range["min"] = secondary_classification.parameters.budget_range["min"]
        if merged.parameters.budget_range["max"] is None and secondary_classification.parameters.budget_range["max"] is not None:
            merged.parameters.budget_range["max"] = secondary_classification.parameters.budget_range["max"]
        
        # Status
        merged.parameters.status = base_classification.parameters.status.copy()
        for status in secondary_classification.parameters.status:
            if status not in merged.parameters.status:
                merged.parameters.status.append(status)
        
        # Time range
        merged.parameters.time_range = base_classification.parameters.time_range.copy()
        if merged.parameters.time_range["start"] is None and secondary_classification.parameters.time_range["start"] is not None:
            merged.parameters.time_range["start"] = secondary_classification.parameters.time_range["start"]
        if merged.parameters.time_range["end"] is None and secondary_classification.parameters.time_range["end"] is not None:
            merged.parameters.time_range["end"] = secondary_classification.parameters.time_range["end"]
        
        # Recalculate query type based on merged parameters
        param_counts = {
            QueryType.DISTRICT: len(merged.parameters.districts),
            QueryType.PROJECT: len(merged.parameters.projects),
            QueryType.SECTOR: len(merged.parameters.sectors),
            QueryType.STATUS: len(merged.parameters.status),
            QueryType.BUDGET: 1 if (merged.parameters.budget_range["min"] is not None or merged.parameters.budget_range["max"] is not None) else 0,
            QueryType.TIME: 1 if (merged.parameters.time_range["start"] is not None or merged.parameters.time_range["end"] is not None) else 0
        }
        
        # Count how many parameter types are present
        non_empty_param_types = sum(1 for count in param_counts.values() if count > 0)
        
        # If multiple parameter types, it's a combined query
        if non_empty_param_types > 1:
            merged.query_type = QueryType.COMBINED
        # If only one parameter type, return that type
        elif non_empty_param_types == 1:
            for query_type, count in param_counts.items():
                if count > 0:
                    merged.query_type = query_type
                    break
        # If no parameters, return unknown
        else:
            merged.query_type = QueryType.UNKNOWN
        
        return merged
    
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
