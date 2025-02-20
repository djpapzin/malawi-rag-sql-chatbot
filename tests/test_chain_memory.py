import pytest
import pytest_asyncio
import asyncio
from langchain.memory import ConversationBufferMemory
from src.llm_chain import ProjectQueryChain

@pytest_asyncio.fixture
async def project_chain():
    """Initialize ProjectQueryChain for tests"""
    chain = ProjectQueryChain()
    return await chain.initialize()

@pytest.mark.asyncio
async def test_chain_interaction(project_chain):
    """Test interaction between different chain components"""
    # Test initial query
    result = await project_chain.invoke("What education projects are there in Lilongwe?")
    
    # Verify all chain components worked
    assert "sql_query" in result, "SQL query should be generated"
    assert "answer" in result, "Answer should be provided"
    assert "suggestions" in result, "Suggestions should be generated"
    
    # Verify query content
    assert "SELECT" in result["sql_query"].upper(), "SQL should be a SELECT statement"
    assert "EDUCATION" in result["sql_query"].upper(), "SQL should reference education"
    assert "LILONGWE" in result["sql_query"].upper(), "SQL should reference Lilongwe"

@pytest.mark.asyncio
async def test_memory_persistence(project_chain):
    """Test that memory persists across multiple queries"""
    # First query about education projects
    result1 = await project_chain.invoke("What education projects are there in Lilongwe?")
    
    # Follow-up query referencing previous context
    result2 = await project_chain.invoke("What is the total budget for these projects?")
    
    # Verify memory influenced the response
    assert "SELECT" in result2["sql_query"].upper(), "SQL should be a SELECT statement"
    assert "SUM" in result2["sql_query"].upper(), "SQL should include budget calculation"

@pytest.mark.asyncio
async def test_rag_components_memory(project_chain):
    """Test RAG components with memory integration"""
    # Initialize components
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    rag = project_chain.rag
    
    # Test conversation flow
    context1 = {
        "question": "Tell me about the CHILIPA CDSS project",
        "sql_results": "Sample results for CHILIPA CDSS",
        "chat_history": []
    }
    
    # First interaction
    answer1 = await rag.generate_answer(context1)
    assert isinstance(answer1, str), "Answer should be a string"
    assert len(answer1) > 0, "Answer should not be empty"
    
    # Follow-up interaction
    context2 = {
        "question": "What is its budget?",
        "sql_results": "Sample budget data",
        "chat_history": [{"input": "Tell me about the CHILIPA CDSS project", "output": answer1}]
    }
    
    answer2 = await rag.generate_answer(context2)
    assert isinstance(answer2, str), "Answer should be a string"
    assert len(answer2) > 0, "Answer should not be empty"

@pytest.mark.asyncio
async def test_suggestion_chain_memory(project_chain):
    """Test that suggestion chain uses conversation history"""
    # Initial query about a specific project
    result1 = await project_chain.invoke("Tell me about the CHILIPA CDSS project")
    suggestions1 = result1["suggestions"]
    
    # Follow-up query
    result2 = await project_chain.invoke("What is its budget?")
    suggestions2 = result2["suggestions"]
    
    # Verify suggestions evolve based on context
    assert isinstance(suggestions1, list), "Suggestions should be a list"
    assert isinstance(suggestions2, list), "Suggestions should be a list"
    assert len(suggestions1) > 0, "Should have initial suggestions"
    assert len(suggestions2) > 0, "Should have follow-up suggestions"
    assert suggestions1 != suggestions2, "Suggestions should evolve based on context"

if __name__ == "__main__":
    pytest.main([__file__]) 