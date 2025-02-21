"""
SQL Chain Module

This module provides a dedicated chain for handling SQL queries using LangChain.
It integrates with our configuration system and provides a clean interface for database operations.
"""

from typing import Dict, Any, Optional, List, Tuple
from langchain_community.utilities import SQLDatabase
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from together import Together
from src.config import initialize_config
from src.sql_validator import SQLValidator, ValidationLevel, ValidationResult
import logging
import re
from datetime import datetime
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class SQLChain:
    """A dedicated chain for handling SQL queries"""
    
    def __init__(self):
        """Initialize the SQL Chain with configuration"""
        self.config = initialize_config()
        
        # Initialize LLM
        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key:
            raise ValueError("TOGETHER_API_KEY environment variable not set")
            
        llm_kwargs = self.config.get_llm_kwargs()
        self.client = Together(api_key=api_key)
        self.model = llm_kwargs["model"]
        self.temperature = llm_kwargs["temperature"]
        self.max_tokens = llm_kwargs["max_tokens"]
        
        # Initialize database
        db_kwargs = self.config.get_db_kwargs()
        self.db = SQLDatabase.from_uri(
            "sqlite:///malawi_projects1.db",
            **db_kwargs
        )
        
        # Initialize SQL validator
        self.validator = SQLValidator(self.db, ValidationLevel.STRICT)
        
        # Get standard columns for queries
        self.standard_columns = [
            "projectname", "projectcode", "district", "projectsector", "projectstatus",
            "budget", "completionpercentage", "startdate", "completiondata"
        ]
        
        # Additional columns for specific queries
        self.specific_columns = []  # No additional columns in the actual schema
    
    async def _validate_and_clean_query(self, query: str) -> Tuple[bool, str, List[str]]:
        """Validate and clean an SQL query"""
        validation_result = self.validator.validate_query(query)
        
        if not validation_result.is_valid:
            error_msg = "SQL validation failed:\n" + "\n".join(validation_result.errors)
            logger.error(error_msg)
            if validation_result.warnings:
                logger.warning("Warnings:\n" + "\n".join(validation_result.warnings))
            return False, error_msg, []
        
        if validation_result.warnings:
            logger.warning("SQL validation warnings:\n" + "\n".join(validation_result.warnings))
        
        return True, validation_result.query or query, validation_result.warnings
    
    async def generate_sql(self, question: str) -> str:
        """Generate a SQL query from a natural language question"""
        try:
            # Basic validation
            if not question.strip():
                raise ValueError("Empty question provided")
            
            # Generate initial SQL query
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a SQL expert that converts questions about infrastructure projects into SQL queries."},
                    {"role": "user", "content": question}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            initial_query = response.choices[0].message.content.strip()
            
            # Validate and clean the query
            is_valid, cleaned_query, warnings = await self._validate_and_clean_query(initial_query)
            
            if not is_valid:
                raise ValueError(f"Invalid SQL query generated: {cleaned_query}")
            
            return cleaned_query
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {str(e)}")
            raise
    
    async def process_results(self, question: str, query: str, results: Any) -> str:
        """Process and format the query results"""
        try:
            formatted_results = self._format_results(results)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing SQL query results about infrastructure projects."},
                    {"role": "user", "content": f"Question: {question}\nSQL Query: {query}\nResults: {formatted_results}\n\nProvide a clear and concise answer."}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error processing results: {str(e)}")
            raise
    
    def _format_results(self, results: Any) -> str:
        """Format the SQL results for presentation"""
        if results is None:
            return "No results found"
            
        if isinstance(results, str):
            return results
            
        if isinstance(results, list):
            if not results:
                return "No results found"
            if len(results) == 1 and isinstance(results[0], tuple) and len(results[0]) == 1:
                return str(results[0][0])
            return str(results)
            
        return str(results)
    
    async def run(self, question: str) -> Dict[str, Any]:
        """
        Run the complete SQL chain
        
        Args:
            question (str): Natural language question about the database
            
        Returns:
            Dict[str, Any]: Dictionary containing the query, results, and formatted answer
        """
        try:
            if not question.strip():
                raise ValueError("Empty question provided")
            
            # Generate and validate SQL query
            query = await self.generate_sql(question)
            logger.info(f"Generated SQL query: {query}")
            
            # Execute query
            start_time = datetime.now()
            results = self.db.run(query)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Query executed in {execution_time:.2f} seconds")
            
            # Process results
            answer = await self.process_results(question, query, results)
            logger.info("Results processed successfully")
            
            return {
                "query": query,
                "results": results,
                "answer": answer,
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Error in SQL chain: {str(e)}")
            return {
                "error": str(e),
                "query": None,
                "results": None,
                "answer": f"An error occurred: {str(e)}",
                "execution_time": 0.0
            } 