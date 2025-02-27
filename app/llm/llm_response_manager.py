"""
LLMResponseManager - Centralized handling of LLM interactions for the Dziwani chatbot.

This module handles all interactions with the LLM model, including prompt generation,
response validation, and caching for improved performance.
"""

import json
import logging
import time
import hashlib
from typing import Dict, List, Optional, Union, Any

from together import Together
import os
from functools import lru_cache

logger = logging.getLogger(__name__)

class LLMResponseManager:
    """
    Central manager for all LLM interactions in the Dziwani chatbot system.
    
    This class handles:
    - Dynamic prompt generation
    - LLM API calls with appropriate parameters
    - Response validation and error handling
    - Caching for improved performance
    - Token usage tracking
    """
    
    def __init__(
        self,
        model_name: str = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K",
        temperature: float = 0.1,
        max_tokens: int = 1024,
        api_key: Optional[str] = None,
        cache_size: int = 100
    ):
        """
        Initialize the LLM Response Manager.
        
        Args:
            model_name: Name of the LLM model to use
            temperature: Temperature parameter for generation
            max_tokens: Maximum tokens to generate in responses
            api_key: Together API key (defaults to environment variable)
            cache_size: Size of the LRU cache for responses
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize Together client
        self.api_key = api_key or os.environ.get("TOGETHER_API_KEY")
        if not self.api_key:
            raise ValueError("Together API key must be provided or set as TOGETHER_API_KEY env variable")
        
        self.together_client = Together(api_key=self.api_key)
        
        # Track token usage
        self.token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
        
        # Stats tracking
        self.stats = {
            "calls": 0,
            "cache_hits": 0,
            "failures": 0,
            "avg_response_time": 0
        }
        
        # Initialize prompt library
        self._init_prompt_library()
    
    def _init_prompt_library(self):
        """Initialize the library of prompt templates."""
        self.prompt_templates = {
            "base_system": """You are Dziwani, an AI assistant specialized in providing information about infrastructure projects in Malawi.
You have access to a database of project details including locations, budgets, timelines, and implementation status.
Always provide accurate, helpful information based on the available data.""",
            
            "intent_analysis": """Analyze this user query: "{query}"
Determine the primary intent, entities mentioned, and implied information needs.
Return a JSON object with the following structure:
{
  "intent": "GREETING | GENERAL | SPECIFIC | OTHER",
  "entities": {
    "locations": [],
    "project_types": [],
    "time_periods": [],
    "constraints": []
  },
  "information_needs": []
}""",
            
            "sql_generation": """Given this database schema:
{schema}

And this user query:
"{query}"

With the following intent analysis:
{intent_data}

Generate an SQL query that will retrieve the appropriate information from the database.
Return only the SQL query without explanation.""",
            
            "response_generation": """Given the user query:
"{query}"

And these database results:
{results_json}

Generate a natural, helpful response that:
1. Directly answers the user's question
2. Organizes the information in a logical structure
3. Uses appropriate formatting for currencies, dates, and percentages
4. Provides context where helpful

Your response should be in plain text format suitable for display to the user."""
        }
    
    @lru_cache(maxsize=100)
    def _get_cached_response(self, prompt_hash: str):
        """Get a cached response by prompt hash."""
        # This is a placeholder for a more sophisticated caching mechanism
        # In a real implementation, this would likely use Redis or a similar cache
        return None
    
    def _store_cached_response(self, prompt_hash: str, response: str):
        """Store a response in the cache."""
        # This is a placeholder for a more sophisticated caching mechanism
        pass
    
    def _create_prompt_hash(self, system_prompt: str, user_prompt: str) -> str:
        """Create a hash of the prompt for caching purposes."""
        combined = f"{system_prompt}||{user_prompt}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get_response(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        use_cache: bool = True
    ) -> str:
        """
        Get a response from the LLM.
        
        Args:
            user_prompt: The user's prompt
            system_prompt: Optional system prompt (defaults to base_system)
            use_cache: Whether to use the response cache
            
        Returns:
            The LLM's response text
        """
        system_prompt = system_prompt or self.prompt_templates["base_system"]
        
        # Track stats
        self.stats["calls"] += 1
        start_time = time.time()
        
        # Check cache
        if use_cache:
            prompt_hash = self._create_prompt_hash(system_prompt, user_prompt)
            cached_response = self._get_cached_response(prompt_hash)
            if cached_response:
                self.stats["cache_hits"] += 1
                logger.info(f"Cache hit for prompt hash {prompt_hash[:8]}")
                return cached_response
        
        try:
            # Call LLM API
            response = self.together_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract response text
            response_text = response.choices[0].message.content
            
            # Update token usage
            self.token_usage["prompt_tokens"] += response.usage.prompt_tokens
            self.token_usage["completion_tokens"] += response.usage.completion_tokens
            self.token_usage["total_tokens"] += response.usage.total_tokens
            
            # Cache response if caching is enabled
            if use_cache:
                self._store_cached_response(prompt_hash, response_text)
            
            # Update response time stats
            elapsed = time.time() - start_time
            self.stats["avg_response_time"] = (
                (self.stats["avg_response_time"] * (self.stats["calls"] - 1) + elapsed) / 
                self.stats["calls"]
            )
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error getting LLM response: {str(e)}")
            self.stats["failures"] += 1
            raise
    
    def analyze_intent(self, query: str) -> Dict[str, Any]:
        """
        Analyze the intent of a user query.
        
        Args:
            query: The user's query
            
        Returns:
            A dictionary containing intent analysis
        """
        prompt = self.prompt_templates["intent_analysis"].format(query=query)
        response = self.get_response(prompt, use_cache=True)
        
        try:
            # Parse the JSON response
            intent_data = json.loads(response)
            return intent_data
        except json.JSONDecodeError:
            logger.error(f"Failed to parse intent analysis response as JSON: {response}")
            # Fallback to basic intent detection
            return {
                "intent": self._detect_basic_intent(query),
                "entities": {"locations": [], "project_types": [], "time_periods": [], "constraints": []},
                "information_needs": []
            }
    
    def _detect_basic_intent(self, query: str) -> str:
        """
        Fallback method for basic intent detection.
        
        Args:
            query: The user's query
            
        Returns:
            The detected intent type
        """
        query_lower = query.lower()
        
        # Simple keyword matching as fallback
        if any(greeting in query_lower for greeting in ["hello", "hi", "hey", "greetings"]):
            return "GREETING"
        
        if any(general in query_lower for general in ["what can you do", "help", "capabilities"]):
            return "GENERAL"
        
        # Default to SPECIFIC for anything else
        return "SPECIFIC"
    
    def generate_sql(self, query: str, schema: str, intent_data: Dict) -> str:
        """
        Generate an SQL query based on the user's query and intent analysis.
        
        Args:
            query: The user's query
            schema: The database schema representation
            intent_data: The intent analysis data
            
        Returns:
            The generated SQL query
        """
        prompt = self.prompt_templates["sql_generation"].format(
            schema=schema,
            query=query,
            intent_data=json.dumps(intent_data)
        )
        
        return self.get_response(prompt, use_cache=True)
    
    def generate_response(self, query: str, results: List[Dict]) -> str:
        """
        Generate a natural language response based on query results.
        
        Args:
            query: The user's query
            results: The query results as a list of dictionaries
            
        Returns:
            A formatted natural language response
        """
        results_json = json.dumps(results)
        
        prompt = self.prompt_templates["sql_generation"].format(
            query=query,
            results_json=results_json
        )
        
        return self.get_response(prompt, use_cache=False)  # Don't cache responses as they're data-dependent
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics for the LLM.
        
        Returns:
            A dictionary containing usage statistics
        """
        return {
            "token_usage": self.token_usage,
            "calls": self.stats["calls"],
            "cache_hits": self.stats["cache_hits"],
            "cache_hit_rate": self.stats["cache_hits"] / max(1, self.stats["calls"]),
            "failures": self.stats["failures"],
            "avg_response_time": self.stats["avg_response_time"]
        }
    
    def add_prompt_template(self, name: str, template: str):
        """
        Add a new prompt template to the library.
        
        Args:
            name: The name of the template
            template: The template text
        """
        self.prompt_templates[name] = template
    
    def get_prompt_template(self, name: str) -> Optional[str]:
        """
        Get a prompt template by name.
        
        Args:
            name: The name of the template
            
        Returns:
            The template text, or None if not found
        """
        return self.prompt_templates.get(name)
