"""
Test suite for LLM integration in RAG SQL Chatbot
"""

import os
import pytest
from dotenv import load_dotenv
from src.llm_chain import ProjectQueryChain
from langchain.memory import ConversationBufferMemory

# Load environment variables
load_dotenv()

@pytest.fixture
def chain():
    """Initialize chain for testing"""
    return ProjectQueryChain()

def test_llm_initialization(chain):
    """Test LLM initialization and basic functionality"""
    assert chain.together is not None
    assert chain.db is not None
    assert isinstance(chain.memory, ConversationBufferMemory)
    
    # Test API key configuration
    assert os.getenv("TOGETHER_API_KEY") is not None
    
    # Test model configuration
    model_name = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K"
    response = chain.together.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": "Test"}],
        max_tokens=10
    )
    assert response.choices is not None
    assert len(response.choices) > 0

def test_query_processing(chain):
    """Test query processing with the LLM"""
    test_query = "Show me education projects in the Southern Region"
    result = chain.invoke(test_query)
    
    # Verify response structure
    assert "sql_query" in result
    assert "answer" in result
    assert "error" not in result
    
    # Verify SQL query contains relevant terms
    sql_query = result["sql_query"].upper()
    assert "PROJECTSECTOR" in sql_query
    assert "REGION" in sql_query
    assert "SOUTHERN" in sql_query
    assert "EDUCATION" in sql_query

def test_query_enhancement(chain):
    """Test query enhancement capabilities"""
    original_query = "show projects"
    result = chain.invoke(original_query)
    
    # Verify SQL query is enhanced with standard columns
    sql_query = result["sql_query"].upper()
    assert "PROJECTNAME" in sql_query
    assert "PROJECTCODE" in sql_query
    assert "FISCALYEAR" in sql_query
    assert "REGION" in sql_query
    assert "DISTRICT" in sql_query
    assert "TOTALBUDGET" in sql_query

def test_suggestion_generation(chain):
    """Test generation of follow-up questions"""
    test_query = "Show me projects in Lilongwe"
    result = chain.invoke(test_query)
    
    # Verify memory contains the interaction
    memory_vars = chain.memory.load_memory_variables({})
    chat_history = memory_vars["chat_history"]
    assert len(chat_history) > 0
    
    # Verify the response contains project information
    assert "sql_query" in result
    assert "answer" in result
    assert "Lilongwe" in result["answer"]

def test_error_handling(chain):
    """Test error handling in the LLM service"""
    # Test with empty query
    result = chain.invoke("")
    assert "error" in result
    
    # Test with invalid district
    result = chain.invoke("Show projects in NonexistentDistrict")
    assert "sql_query" in result  # Should still generate a query
    assert "answer" in result  # Should provide a response
    assert "No results found" in result["answer"] or "error" in result
    
    # Test with malformed query
    result = chain.invoke("!!!invalid!!!")
    assert "error" in result

def test_full_conversation_flow(chain):
    """Test a complete conversation flow"""
    # Initial query
    query1 = "Show me education projects in Lilongwe"
    result1 = chain.invoke(query1)
    assert "sql_query" in result1
    assert "answer" in result1
    
    # Follow-up query
    query2 = "What is their total budget?"
    result2 = chain.invoke(query2)
    assert "sql_query" in result2
    assert "answer" in result2
    assert "TOTALBUDGET" in result2["sql_query"].upper()
    
    # Verify memory retention
    memory_vars = chain.memory.load_memory_variables({})
    chat_history = memory_vars["chat_history"]
    assert len(chat_history) >= 2  # Should contain both interactions
    assert any(query1 in str(msg) for msg in chat_history)
    assert any(query2 in str(msg) for msg in chat_history)

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 