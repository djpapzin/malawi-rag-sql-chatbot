import pytest
import pytest_asyncio
import os
from src.llm_chain import ProjectQueryChain
from app.core.logger import logger
from app.core.config import settings

@pytest_asyncio.fixture
async def chain():
    """Initialize ProjectQueryChain for tests"""
    chain = ProjectQueryChain()
    return await chain.initialize()

@pytest.mark.asyncio
async def test_stats_tracking(chain):
    """Test that basic statistics are tracked"""
    # Initial stats should be zero or near-zero
    assert chain.usage_stats['total_queries'] == 0
    assert chain.usage_stats['error_count'] == 0
    
    # Process a query
    result = await chain.invoke("What education projects are there in Lilongwe?")
    
    # Verify stats were updated
    assert chain.usage_stats['total_queries'] == 1
    assert chain.usage_stats['total_api_calls'] > 0
    assert chain.usage_stats['avg_response_time'] > 0
    assert 'processing_time' in result

@pytest.mark.asyncio
async def test_error_tracking(chain):
    """Test that errors are properly tracked"""
    initial_errors = chain.usage_stats['error_count']
    
    # Try an invalid query
    with pytest.raises(Exception):
        await chain.invoke("")  # Empty query should raise error
    
    # Verify error count increased
    assert chain.usage_stats['error_count'] > initial_errors

@pytest.mark.asyncio
async def test_logging(chain):
    """Test that operations are properly logged"""
    # Get log file path from settings
    log_file = settings.LOG_FILE
    
    # Process a query that should generate logs
    await chain.invoke("Test logging with this query")
    
    # Verify log file exists and contains expected entries
    assert os.path.exists(log_file)
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert "Processing question: Test logging with this query" in log_content
        assert "SQL query generated" in log_content
        assert "Question processed in" in log_content 