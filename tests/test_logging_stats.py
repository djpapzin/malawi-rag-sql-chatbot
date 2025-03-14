import pytest
import pytest_asyncio
from src.llm_chain import ProjectQueryChain
from app.core.logger import logger

@pytest_asyncio.fixture
async def project_chain():
    """Initialize ProjectQueryChain for tests"""
    chain = ProjectQueryChain()
    return await chain.initialize()

@pytest.mark.asyncio
async def test_usage_statistics_tracking(project_chain):
    """Test that usage statistics are properly tracked"""
    # Initial stats should be zero
    assert project_chain.usage_stats['total_queries'] == 0
    assert project_chain.usage_stats['error_count'] == 0
    
    # Process a valid query
    result = await project_chain.invoke("What education projects are there in Lilongwe?")
    
    # Check stats were updated
    assert project_chain.usage_stats['total_queries'] == 1
    assert project_chain.usage_stats['total_api_calls'] > 0
    assert project_chain.usage_stats['avg_response_time'] > 0
    assert 'processing_time' in result
