import os
import pytest
import pytest_asyncio
from unittest.mock import patch
from src.llm_chain import ProjectQueryChain
from app.core.langsmith_config import langsmith_config
from langsmith.client import Client
from langchain_core.tracers.context import tracing_v2_enabled

@pytest.fixture
def langsmith_client():
    """Create a LangSmith client for testing"""
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        pytest.skip("LANGSMITH_API_KEY not set")
    return Client(api_key=api_key)

@pytest_asyncio.fixture
async def chain():
    """Create a ProjectQueryChain instance for testing"""
    chain = ProjectQueryChain()
    await chain.initialize()
    return chain

@pytest.mark.asyncio
async def test_langsmith_configuration():
    """Test that LangSmith configuration is properly initialized"""
    assert os.getenv("LANGSMITH_API_KEY") is not None
    assert os.getenv("LANGSMITH_PROJECT") == "rag-sql-chatbot"
    assert os.getenv("ENABLE_TRACING") == "true"
    assert os.getenv("ENABLE_DEBUG") == "true"

@pytest.mark.asyncio
async def test_chain_tracing(chain, langsmith_client):
    """Test that chain operations are properly traced"""
    # Test a simple query
    question = "What is the total budget for all projects?"
    try:
        result = await chain.invoke(question)
        assert result is not None
        assert "answer" in result
        assert "sql_query" in result
        
        # Verify trace exists in LangSmith
        runs = langsmith_client.list_runs(
            project_name="rag-sql-chatbot",
            execution_order=1,
            error=False
        )
        assert len(list(runs)) > 0
        
    except Exception as e:
        pytest.fail(f"Chain invocation failed: {str(e)}")

@pytest.mark.asyncio
async def test_error_tracing(chain, langsmith_client):
    """Test that errors are properly traced"""
    # Test with an empty query to trigger an error
    with pytest.raises(ValueError):
        await chain.invoke("")
    
    # Verify error trace exists in LangSmith
    runs = langsmith_client.list_runs(
        project_name="rag-sql-chatbot",
        error=True
    )
    assert len(list(runs)) > 0

@pytest.mark.asyncio
async def test_chain_performance_monitoring(chain, langsmith_client):
    """Test that performance metrics are captured"""
    # Test a complex query that should take some time
    question = "What are the top 5 projects by budget, including their locations and start dates?"
    result = await chain.invoke(question)
    
    # Verify performance metrics in result
    assert "processing_time" in result
    assert result["processing_time"] > 0
    
    # Verify metrics in LangSmith
    runs = langsmith_client.list_runs(
        project_name="rag-sql-chatbot",
        execution_order=1
    )
    run = next(runs)
    assert run.end_time > run.start_time
    assert run.latency > 0

def test_api_connection():
    # Set tracing environment variables
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "rag-sql-chatbot"
    
    # Use context manager for explicit tracing control
    with tracing_v2_enabled():
        chain = ProjectQueryChain(api_key="your_api_key")
        result = chain.ainvoke("Test prompt")
        assert result is not None

