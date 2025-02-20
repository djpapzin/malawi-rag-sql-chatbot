"""Test suite for LangChain configuration"""

import pytest
from src.config import LangChainConfig, initialize_config
from langchain.prompts import PromptTemplate
from langchain_community.cache import InMemoryCache
import os
import logging
import shutil
import time

@pytest.fixture(scope="session", autouse=True)
def setup_and_cleanup():
    """Setup before tests and cleanup after"""
    # Setup
    os.makedirs("logs", exist_ok=True)
    
    yield
    
    # Cleanup
    # Close all handlers to release file locks
    logger = logging.getLogger("langchain")
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    
    # Small delay to ensure file is released
    time.sleep(0.1)
    
    # Remove logs directory
    if os.path.exists("logs"):
        try:
            shutil.rmtree("logs")
        except PermissionError:
            print("Warning: Could not remove logs directory due to file lock")

@pytest.fixture
def config():
    """Initialize configuration for testing"""
    return initialize_config()

def test_config_initialization():
    """Test basic configuration initialization"""
    config = LangChainConfig()
    
    # Verify LLM configuration
    assert config.llm_config["model"] == "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K"
    assert isinstance(config.llm_config["temperature"], float)
    assert isinstance(config.llm_config["max_tokens"], int)
    
    # Verify memory configuration
    assert config.memory_config["memory_key"] == "chat_history"
    assert config.memory_config["return_messages"] is True
    assert "max_token_limit" in config.memory_config
    
    # Verify database configuration
    assert "proj_dashboard" in config.db_config["include_tables"]
    assert isinstance(config.db_config["sample_rows_in_table_info"], int)
    
    # Verify prompt template
    assert isinstance(config.sql_prompt_template, PromptTemplate)
    assert "columns" in config.sql_prompt_template.input_variables
    assert "question" in config.sql_prompt_template.input_variables

def test_cache_configuration(config):
    """Test cache setup"""
    # Verify cache is enabled
    assert config.cache_config["enabled"] is True
    assert config.cache_config["type"] == "in_memory"
    assert isinstance(config.cache_config["ttl"], int)

def test_logging_configuration(config):
    """Test logging setup"""
    # Verify logging configuration
    assert config.logging_config["verbose"] is True
    assert config.logging_config["log_level"] == "INFO"
    assert "langchain.log" in config.logging_config["log_file"]
    
    # Check if logs directory exists
    assert os.path.exists("logs")
    
    # Check if log file is created
    config.setup_langchain()
    assert os.path.exists(config.logging_config["log_file"])
    
    # Verify logging functionality
    logger = logging.getLogger("langchain")
    assert logger.level == getattr(logging, config.logging_config["log_level"])

def test_getter_methods(config):
    """Test configuration getter methods"""
    # Test LLM configuration
    llm_kwargs = config.get_llm_kwargs()
    assert isinstance(llm_kwargs, dict)
    assert "model" in llm_kwargs
    assert "temperature" in llm_kwargs
    
    # Test memory configuration
    memory_kwargs = config.get_memory_kwargs()
    assert isinstance(memory_kwargs, dict)
    assert "memory_key" in memory_kwargs
    assert "return_messages" in memory_kwargs
    
    # Test database configuration
    db_kwargs = config.get_db_kwargs()
    assert isinstance(db_kwargs, dict)
    assert "include_tables" in db_kwargs
    
    # Test SQL prompt
    sql_prompt = config.get_sql_prompt()
    assert isinstance(sql_prompt, PromptTemplate)

def test_langchain_setup(config):
    """Test LangChain setup process"""
    # Setup LangChain
    config.setup_langchain()
    
    # Verify cache setup
    from langchain.globals import get_llm_cache
    assert isinstance(get_llm_cache(), InMemoryCache)
    
    # Verify logging setup
    logger = logging.getLogger("langchain")
    assert logger.handlers  # Check if handlers are configured
    
    # Test logging functionality
    test_message = "Test log message"
    logger.info(test_message)
    
    # Verify message was logged
    with open(config.logging_config["log_file"], 'r') as f:
        log_content = f.read()
        assert test_message in log_content

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 