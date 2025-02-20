"""
LangSmith Configuration Module

This module contains configuration and setup for LangSmith tracing and debugging.
"""

import os
from langsmith import Client
from langchain.callbacks.tracers import LangChainTracer, ConsoleCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langsmith.run_helpers import traceable
from dotenv import load_dotenv
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class LangSmithConfig:
    """Configuration class for LangSmith settings"""
    
    def __init__(self):
        # LangSmith API settings
        self.api_url = os.getenv("LANGSMITH_ENDPOINT_URL", "https://api.smith.langchain.com")
        self.api_key = os.getenv("LANGSMITH_API_KEY")
        self.project_name = os.getenv("LANGSMITH_PROJECT", "rag-sql-chatbot")
        
        # Tracing configuration
        self.tracing_enabled = os.getenv("ENABLE_TRACING", "true").lower() == "true"
        self.debug_enabled = os.getenv("ENABLE_DEBUG", "false").lower() == "true"
        
        # Initialize client and tracer
        self.client = None
        self.tracer = None
        self.callback_manager = None
        
        if self.tracing_enabled:
            self.setup_tracing()
    
    def setup_tracing(self):
        """Initialize LangSmith client and tracer"""
        try:
            if not self.api_key:
                logger.warning("LANGSMITH_API_KEY not set. Tracing will be disabled.")
                self.tracing_enabled = False
                return
                
            # Initialize LangSmith client
            self.client = Client(
                api_url=self.api_url,
                api_key=self.api_key
            )
            
            # Initialize tracer with project name
            self.tracer = LangChainTracer(
                project_name=self.project_name
            )
            
            # Add console handler for debugging
            handlers = [self.tracer]
            if self.debug_enabled:
                handlers.append(ConsoleCallbackHandler())
            
            # Set up callback manager
            self.callback_manager = CallbackManager(handlers)
            
            logger.info(f"LangSmith tracing initialized for project: {self.project_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangSmith tracing: {str(e)}")
            self.tracing_enabled = False
    
    def get_callback_manager(self):
        """Get the callback manager for tracing"""
        return self.callback_manager if self.tracing_enabled else None
    
    def trace_chain(self, chain_type: str):
        """Decorator for tracing chains"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                if not self.tracing_enabled:
                    return await func(*args, **kwargs)
                
                # Add tracing metadata
                metadata = {
                    "chain_type": chain_type,
                    "timestamp": str(datetime.now())
                }
                
                # Execute with tracing
                callbacks = self.get_callback_manager()
                if callbacks:
                    kwargs["callbacks"] = callbacks
                
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    if callbacks:
                        # Log error to LangSmith
                        for handler in callbacks.handlers:
                            if hasattr(handler, "on_chain_error"):
                                handler.on_chain_error(error=e, metadata=metadata)
                    raise
                    
            return wrapper
        return decorator

langsmith_config = LangSmithConfig() 