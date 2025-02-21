"""
LangChain Configuration Module

This module contains all LangChain-specific configurations and settings.
"""

from typing import Dict, Any
from langchain_community.callbacks.manager import get_openai_callback
from langchain_community.cache import InMemoryCache
from langchain.globals import set_llm_cache, set_debug
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import logging
from pydantic import BaseModel, Field
from langchain_core.memory import BaseMemory
from langchain.memory import ConversationBufferMemory
from langchain_community.utilities import SQLDatabase
from langchain_together import Together
from app.core.logger import logger

# Load environment variables
load_dotenv()

class LangChainConfig(BaseModel):
    """Configuration for LangChain components"""
    llm_kwargs: Dict[str, Any] = Field(default_factory=lambda: {
        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K",
        "temperature": 0.1,
        "max_tokens": 512,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1
    })
    memory_kwargs: Dict[str, Any] = Field(default_factory=lambda: {
        "return_messages": True,
        "input_key": "input",
        "output_key": "output",
        "memory_key": "chat_history"
    })
    db_kwargs: Dict[str, Any] = Field(default_factory=lambda: {
        "sample_rows_in_table_info": 3
    })
    debug_mode: bool = Field(default=False)
    use_cache: bool = Field(default=True)

    model_config = {"arbitrary_types_allowed": True}

    def get_llm_kwargs(self) -> Dict[str, Any]:
        """Get LLM configuration"""
        return self.llm_kwargs

    def get_memory_kwargs(self) -> Dict[str, Any]:
        """Get memory configuration"""
        return self.memory_kwargs

    def get_db_kwargs(self) -> Dict[str, Any]:
        """Get database configuration"""
        return self.db_kwargs

    def setup_langchain(self):
        """Setup LangChain configuration"""
        try:
            # Enable debug mode if needed
            if self.debug_mode:
                logger.setLevel("DEBUG")
                logger.debug("Debug mode enabled")

            # Enable caching if needed
            if self.use_cache:
                logger.info("Caching enabled")

        except Exception as e:
            logger.error(f"Error setting up LangChain configuration: {str(e)}")
            raise

def initialize_config() -> LangChainConfig:
    """Initialize and return a LangChainConfig instance"""
    config = LangChainConfig()
    config.setup_langchain()
    return config 