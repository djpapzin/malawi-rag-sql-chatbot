import pytest
import asyncio
import time
from src.llm_chain import ProjectQueryChain
import concurrent.futures
from typing import List, Dict
import statistics
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def chain():
    """Initialize chain for testing"""
    return ProjectQueryChain()

def measure_execution_time(func):
    """Decorator to measure function execution time"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        return result, execution_time
    return wrapper

@measure_execution_time
def execute_query(chain: ProjectQueryChain, query: str) -> Dict:
    """Execute a single query and return result"""
    return chain.invoke(query)

async def execute_concurrent_queries(queries: List[str], max_workers: int = 3) -> List[Dict]:
    """Execute multiple queries concurrently"""
    results = []
    chain = ProjectQueryChain()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create futures for all queries
        futures = [
            executor.submit(execute_query, chain, query)
            for query in queries
        ]
        
        # Wait for all futures to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                result, execution_time = future.result()
                results.append({
                    "result": result,
                    "execution_time": execution_time
                })
            except Exception as e:
                logger.error(f"Error executing query: {str(e)}")
                results.append({
                    "error": str(e),
                    "execution_time": 0
                })
    
    return results

def test_chain_execution_times(chain):
    """Test and measure chain execution times"""
    test_queries = [
        "Show me all projects in Lilongwe District",
        "What is the total budget for education projects?",
        "Show details about CHILIPA CDSS GIRLS HOSTEL"
    ]
    
    execution_times = []
    for query in test_queries:
        result, execution_time = execute_query(chain, query)
        execution_times.append(execution_time)
        
        # Log performance metrics
        logger.info(f"Query: {query}")
        logger.info(f"Execution time: {execution_time:.2f} seconds")
        
        # Basic assertions
        assert execution_time > 0  # Should take some time
        assert execution_time < 30  # Should not take too long
    
    # Calculate statistics
    avg_time = statistics.mean(execution_times)
    max_time = max(execution_times)
    min_time = min(execution_times)
    
    logger.info(f"Average execution time: {avg_time:.2f} seconds")
    logger.info(f"Maximum execution time: {max_time:.2f} seconds")
    logger.info(f"Minimum execution time: {min_time:.2f} seconds")

@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test handling of concurrent requests"""
    test_queries = [
        "Show projects in Lilongwe",
        "Show projects in Zomba",
        "Show projects in Blantyre",
        "Show education projects",
        "Show transport projects"
    ]
    
    # Test with different concurrency levels
    for max_workers in [2, 3, 5]:
        logger.info(f"\nTesting with {max_workers} concurrent workers")
        start_time = time.time()
        
        results = await execute_concurrent_queries(test_queries, max_workers)
        
        total_time = time.time() - start_time
        successful = sum(1 for r in results if "error" not in r)
        
        logger.info(f"Total execution time: {total_time:.2f} seconds")
        logger.info(f"Successful queries: {successful}/{len(results)}")
        
        # Verify results
        assert len(results) == len(test_queries)
        assert successful > 0  # At least some queries should succeed

def test_token_usage(chain):
    """Test and monitor token usage"""
    test_query = "Show me details about education projects in Lilongwe District"
    
    # Get initial token count
    initial_response = chain.together.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K",
        messages=[{"role": "user", "content": "Test"}],
        max_tokens=10
    )
    
    # Execute main query
    result = chain.invoke(test_query)
    
    # Get final token count
    final_response = chain.together.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K",
        messages=[{"role": "user", "content": "Test"}],
        max_tokens=10
    )
    
    # Log token usage
    logger.info(f"Query: {test_query}")
    if hasattr(final_response, 'usage'):
        logger.info(f"Prompt tokens: {final_response.usage.prompt_tokens}")
        logger.info(f"Completion tokens: {final_response.usage.completion_tokens}")
        logger.info(f"Total tokens: {final_response.usage.total_tokens}")
    
    # Verify response structure
    assert "sql_query" in result
    assert "answer" in result
    assert "error" not in result

def test_memory_usage(chain):
    """Test memory usage during chain execution"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
    
    # Execute a series of queries
    test_queries = ["Show projects in Lilongwe"] * 5
    
    memory_usage = []
    for query in test_queries:
        result = chain.invoke(query)
        current_memory = process.memory_info().rss / 1024 / 1024
        memory_usage.append(current_memory)
        
        logger.info(f"Memory usage: {current_memory:.2f} MB")
    
    final_memory = process.memory_info().rss / 1024 / 1024
    memory_increase = final_memory - initial_memory
    
    logger.info(f"Initial memory: {initial_memory:.2f} MB")
    logger.info(f"Final memory: {final_memory:.2f} MB")
    logger.info(f"Memory increase: {memory_increase:.2f} MB")
    
    # Memory shouldn't grow unbounded
    assert memory_increase < 1000  # Less than 1GB increase

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 